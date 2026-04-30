"""Stage 2: docker swarm init on data, join from proc, create cpip_network.

Network name and gateway match the upstream calgary stack
(docker-compose.stack.yml expects ``cpip_network`` to exist as an
external attachable overlay network before deploy).

References:

- ``docker swarm init --data-path-port`` flag (we set 9789 to override
  the default 4789): "Port number used to send data; if no value is set
  or is set to 0, the default port (4789) is used." —
  https://docs.docker.com/reference/cli/docker/swarm/init/
- ``host.data.<key>`` access. pyinfra 3.x's ``HostData`` exposes data
  via ``__getattr__`` only and does **not** implement ``__getitem__``;
  ``host.data["bidsflux_swarm_advertise_addr"]`` raises
  ``TypeError: 'HostData' object is not subscriptable`` at runtime.
  See the class definition (``__getattr__``, ``__setattr__``, ``.get()``
  but no ``__getitem__``) at
  https://github.com/pyinfra-dev/pyinfra/blob/812a1499dfb2979848bf4603fe02017c6bf149e7/src/pyinfra/api/host.py#L48-L96

Shell-script discipline
-----------------------

Each shell command sets ``set -eu -o pipefail`` and avoids the two
silent-failure idioms we got bitten by in TODO Phase 0:

1. ``cmd1 || cmd2`` — masks ``cmd2`` failures because the whole expr
   returns ``cmd2``'s exit code, but pyinfra reports the operation as
   `Success` if the spawned shell ran at all. Replaced by explicit
   ``if … then … fi`` blocks with explicit ``exit 1`` on the failure
   path.
2. ``TOKEN=$(cmd)`` — a bash assignment always returns 0 even when the
   command-substitution command failed, so a downstream ``[ -n "$TOKEN" ]``
   check is required to surface the failure. ``set -o pipefail`` does
   not help with this; only an explicit non-empty check does.

Plus a post-condition check after ``docker swarm init`` that we are
actually a manager (``Swarm.ControlAvailable == true``) — otherwise the
stack-deploy step in the next stage fails opaquely with "This node is
not a swarm manager".
"""

from pathlib import Path

from pyinfra import host
from pyinfra.operations import files, server


SWARM_DATA_PORT = 9789
OVERLAY_NET = "cpip_network"
OVERLAY_GATEWAY = "192.11.0.2"
OVERLAY_SUBNET = "192.11.0.0/16"

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
LOCAL_JOIN_FILE = CACHE_DIR / "swarm-join.sh"


def init_manager() -> None:
    # Attribute access only — host.data has __getattr__ but no __getitem__.
    # see https://github.com/pyinfra-dev/pyinfra/blob/812a1499dfb2979848bf4603fe02017c6bf149e7/src/pyinfra/api/host.py#L66-L77
    advertise = host.data.bidsflux_swarm_advertise_addr

    server.shell(
        name="swarm init (idempotent, verified manager)",
        commands=[
            # Single bash invocation so $STATE / $MGR persist.
            "set -eu -o pipefail; "
            # Pre-flight: the advertise IP must actually be bound on a NIC,
            # else `docker swarm init` "succeeds" but doesn't manage anything
            # we'd recognise. This is the libvirt boot-timing trap.
            f"if ! ip -4 addr show | grep -q 'inet {advertise}/'; then "
            f"  echo 'ERROR: advertise-addr {advertise} not on any local interface' >&2; "
            "   ip -4 addr show >&2; "
            "   exit 1; "
            "fi; "
            "STATE=$(docker info --format '{{.Swarm.LocalNodeState}}'); "
            "echo \"swarm state before init: $STATE\"; "
            "if [ \"$STATE\" != active ]; then "
            f"  docker swarm init --data-path-port {SWARM_DATA_PORT} --advertise-addr {advertise}; "
            "fi; "
            # Post-condition: not just active, but a *manager*.
            "MGR=$(docker info --format '{{.Swarm.ControlAvailable}}'); "
            "echo \"ControlAvailable after init: $MGR\"; "
            "if [ \"$MGR\" != true ]; then "
            "  echo 'ERROR: node is active in swarm but not a manager' >&2; "
            "  docker info --format '{{json .Swarm}}' >&2; "
            "  exit 1; "
            "fi",
        ],
        _sudo=True,
    )

    files.directory(
        name="bidsflux state dir",
        path="/etc/bidsflux",
        mode="0755",
        _sudo=True,
    )
    server.shell(
        name="dump worker join command (WORKER_IP placeholder)",
        commands=[
            "set -eu -o pipefail; "
            # `TOKEN=$(...)` returns 0 even on failure, so check non-empty.
            "TOKEN=$(docker swarm join-token worker -q); "
            "test -n \"$TOKEN\"; "
            f"printf 'docker swarm join --token %s "
            f"--advertise-addr WORKER_IP {advertise}:2377\\n' \"$TOKEN\" "
            "> /etc/bidsflux/swarm-join.sh; "
            "chmod 0644 /etc/bidsflux/swarm-join.sh",
        ],
        _sudo=True,
    )

    server.shell(
        name=f"overlay network {OVERLAY_NET}",
        commands=[
            "set -eu; "
            f"if ! docker network inspect {OVERLAY_NET} >/dev/null 2>&1; then "
            f"  docker network create --driver=overlay --attachable "
            f"--subnet={OVERLAY_SUBNET} --gateway={OVERLAY_GATEWAY} {OVERLAY_NET}; "
            "fi",
        ],
        _sudo=True,
    )


def join_worker() -> None:
    if not LOCAL_JOIN_FILE.exists():
        raise SystemExit(
            f"Missing {LOCAL_JOIN_FILE}; run `make swarm-fetch-join` "
            "after the manager has been initialised."
        )

    # Attribute access — see the init_manager() comment above.
    advertise = host.data.bidsflux_swarm_advertise_addr

    files.put(
        name="upload join script",
        src=str(LOCAL_JOIN_FILE),
        dest="/etc/bidsflux/swarm-join.sh",
        mode="0644",
        _sudo=True,
    )

    server.shell(
        name="join swarm if not already (verified worker)",
        commands=[
            "set -eu -o pipefail; "
            f"if ! ip -4 addr show | grep -q 'inet {advertise}/'; then "
            f"  echo 'ERROR: advertise-addr {advertise} not on any local interface' >&2; "
            "   ip -4 addr show >&2; "
            "   exit 1; "
            "fi; "
            "STATE=$(docker info --format '{{.Swarm.LocalNodeState}}'); "
            "if [ \"$STATE\" = active ]; then "
            "  echo 'already in swarm'; exit 0; "
            "fi; "
            f"sed 's|WORKER_IP|{advertise}|' /etc/bidsflux/swarm-join.sh | sh -; "
            # Post-condition: we should now be active.
            "STATE=$(docker info --format '{{.Swarm.LocalNodeState}}'); "
            "if [ \"$STATE\" != active ]; then "
            "  echo 'ERROR: swarm join apparently succeeded but node not active' >&2; "
            "  docker info --format '{{json .Swarm}}' >&2; "
            "  exit 1; "
            "fi",
        ],
        _sudo=True,
    )
