"""Stage 3: stage upstream stack on data, generate secrets, deploy.

Real upstream filenames (calgary branch of ni-dataops/stack):

    deploy/create_directory.sh        creates /data/{gitlab,minio,...}
    deploy/generate_secrets.sh        mints 3 docker secrets
    docker-compose.stack.yml          monolithic compose, network = cpip_network
    config/cal_config.rb              referenced as a docker config
    secrets/                          gitignored; we seed stub files here

The 8 user-supplied secrets (cert/key, gitlab tokens, dicom token, s3 id/key,
ssh passphrase, mc.conf) are stubbed with random/empty content for the demo —
they let stack deploy succeed enough to bring GitLab + MinIO up. Real values
get rotated in via post_install.run_on_manager().

Shell-script discipline: every multi-statement command starts with
``set -eu`` (not ``-o pipefail``: pyinfra runs commands under
``/bin/sh`` which is dash on Ubuntu and does not support pipefail).
Partial failures abort the operation instead of being papered over
by ``cmd1 || cmd2`` short-circuits or ``VAR=$(cmd)`` assignments
that always return 0. See `tasks/swarm.py` for the full rationale
(TODO Phase 0).
"""

from pathlib import Path

from pyinfra.operations import files, server


STACK_HOST_PATH = Path(__file__).resolve().parent.parent / "sourcedata" / "stack"
STACK_VM_PATH = "/opt/bidsflux/stack"
STACK_NAME = "cpip"


def deploy_on_manager() -> None:
    files.directory(
        name="bidsflux opt dir",
        path="/opt/bidsflux",
        mode="0755",
        _sudo=True,
    )

    files.sync(
        name="sync upstream stack to manager",
        src=str(STACK_HOST_PATH),
        dest=STACK_VM_PATH,
        delete=False,
        exclude=[".git"],
        _sudo=True,
    )

    server.shell(
        name="create_directory.sh (/data/...)",
        commands=[
            "set -eu; "
            f"cd {STACK_VM_PATH}; "
            "bash deploy/create_directory.sh",
        ],
        _sudo=True,
    )

    # Stub the 8 secrets that upstream expects as ./secrets/* but doesn't
    # create. Random base64 for tokens; self-signed cert/key for the gitlab
    # service's TLS.
    server.shell(
        name="seed secrets/ stubs",
        commands=[
            "set -eu; "
            f"cd {STACK_VM_PATH}; "
            "mkdir -p secrets; "
            "cd secrets; "
            "for f in gitlab_local gitlab_remote dicom_token s3_id s3_key passphrase mc.conf minio_pass; do "
            "  if [ ! -s \"$f\" ]; then openssl rand -base64 24 > \"$f\"; fi; "
            "done; "
            # cert/key referenced by the gitlab service via secret mounts.
            "if [ ! -s bundle.crt ]; then "
            "  openssl req -x509 -nodes -days 365 -newkey rsa:2048 "
            "    -keyout cert.key -out bundle.crt "
            "    -subj '/CN=itappcpipdp01.uc.ucalgary.ca' "
            "    -addext 'subjectAltName=DNS:itappcpipdp01.uc.ucalgary.ca,DNS:localhost,IP:127.0.0.1'; "
            "fi; "
            "chmod 0600 ./*",
        ],
        _sudo=True,
    )

    server.shell(
        name="generate_secrets (idempotent)",
        commands=[
            "set -eu; "
            f"cd {STACK_VM_PATH}; "
            "if [ ! -f .secrets-generated ]; then "
            # Avoid `… | tee` (pyinfra runs under /bin/sh — no pipefail);
            # write to file, then surface to stdout via cat.
            "  bash deploy/generate_secrets.sh > .secrets-output 2>&1; "
            "  cat .secrets-output; "
            "  touch .secrets-generated; "
            "fi",
        ],
        _sudo=True,
    )

    server.shell(
        name=f"docker stack deploy {STACK_NAME}",
        commands=[
            "set -eu; "
            f"cd {STACK_VM_PATH}; "
            f"docker stack deploy -c docker-compose.stack.yml {STACK_NAME}",
        ],
        _sudo=True,
    )

    # Wait for gitlab to settle. This is a polling loop so a transient
    # daemon hiccup doesn't blow up the operation; we cap at 60 × 10s = 10 min.
    server.shell(
        name="wait for gitlab service 1/1",
        commands=[
            "set -u; "
            "for i in $(seq 1 60); do "
            f"  state=$(docker service ls --filter name={STACK_NAME}_gitlab "
            "    --format '{{.Replicas}}' 2>/dev/null || true); "
            "  echo \"[$i/60] gitlab replicas=$state\"; "
            "  if [ \"$state\" = \"1/1\" ]; then exit 0; fi; "
            "  sleep 10; "
            "done; "
            "echo 'ERROR: gitlab did not reach 1/1 within 10 minutes' >&2; "
            f"docker stack ps {STACK_NAME} --no-trunc >&2 || true; "
            "exit 1",
        ],
        _sudo=True,
    )
