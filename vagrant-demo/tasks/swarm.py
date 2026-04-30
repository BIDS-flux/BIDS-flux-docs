"""Stage 2: docker swarm init on data, join from proc, create cpip_network.

Network name and gateway match the upstream calgary stack
(docker-compose.stack.yml expects ``cpip_network`` to exist as an
external attachable overlay network before deploy).
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
    advertise = host.data["bidsflux_swarm_advertise_addr"]

    server.shell(
        name="swarm init (idempotent)",
        commands=[
            "docker info --format '{{.Swarm.LocalNodeState}}' | grep -q active "
            f"|| docker swarm init --data-path-port {SWARM_DATA_PORT} "
            f"--advertise-addr {advertise}",
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
            "TOKEN=$(docker swarm join-token worker -q); "
            f"printf 'docker swarm join --token %s "
            f"--advertise-addr WORKER_IP {advertise}:2377\\n' \"$TOKEN\" "
            "> /etc/bidsflux/swarm-join.sh",
            "chmod 0644 /etc/bidsflux/swarm-join.sh",
        ],
        _sudo=True,
    )

    server.shell(
        name=f"overlay network {OVERLAY_NET}",
        commands=[
            f"docker network inspect {OVERLAY_NET} >/dev/null 2>&1 "
            "|| docker network create --driver=overlay --attachable "
            f"--subnet={OVERLAY_SUBNET} --gateway={OVERLAY_GATEWAY} {OVERLAY_NET}",
        ],
        _sudo=True,
    )


def join_worker() -> None:
    if not LOCAL_JOIN_FILE.exists():
        raise SystemExit(
            f"Missing {LOCAL_JOIN_FILE}; run `make swarm-fetch-join` "
            "after the manager has been initialised."
        )

    advertise = host.data["bidsflux_swarm_advertise_addr"]

    files.put(
        name="upload join script",
        src=str(LOCAL_JOIN_FILE),
        dest="/etc/bidsflux/swarm-join.sh",
        mode="0644",
        _sudo=True,
    )

    server.shell(
        name="join swarm if not already",
        commands=[
            "docker info --format '{{.Swarm.LocalNodeState}}' | grep -q active && exit 0; "
            f"sed 's|WORKER_IP|{advertise}|' /etc/bidsflux/swarm-join.sh | sh -",
        ],
        _sudo=True,
    )
