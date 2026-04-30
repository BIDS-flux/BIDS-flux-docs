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
            f"cd {STACK_VM_PATH} && bash deploy/create_directory.sh",
        ],
        _sudo=True,
    )

    # Stub the 8 secrets that upstream expects as ./secrets/* but doesn't
    # create. Random base64 for tokens; empty for cert/key (which makes
    # the gitlab service degrade to plain HTTP — fine for the demo).
    server.shell(
        name="seed secrets/ stubs",
        commands=[
            f"cd {STACK_VM_PATH} && mkdir -p secrets && cd secrets && "
            "for f in gitlab_local gitlab_remote dicom_token s3_id s3_key passphrase mc.conf; do "
            "  test -s \"$f\" || openssl rand -base64 24 > \"$f\"; "
            "done; "
            # cert/key are referenced by the gitlab service via secret mounts;
            # generate a self-signed pair so the secret targets exist.
            "test -s bundle.crt || openssl req -x509 -nodes -days 365 -newkey rsa:2048 "
            "-keyout cert.key -out bundle.crt "
            "-subj '/CN=itappcpipdp01.uc.ucalgary.ca' "
            "-addext 'subjectAltName=DNS:itappcpipdp01.uc.ucalgary.ca,DNS:localhost,IP:127.0.0.1'; "
            "test -s minio_pass || openssl rand -base64 24 > minio_pass; "
            "chmod 0600 *",
        ],
        _sudo=True,
    )

    server.shell(
        name="generate_secrets (idempotent)",
        commands=[
            f"cd {STACK_VM_PATH} && "
            "test -f .secrets-generated || "
            "(bash deploy/generate_secrets.sh 2>&1 | tee .secrets-output && "
            "touch .secrets-generated)",
        ],
        _sudo=True,
    )

    server.shell(
        name=f"docker stack deploy {STACK_NAME}",
        commands=[
            f"cd {STACK_VM_PATH} && "
            f"docker stack deploy -c docker-compose.stack.yml {STACK_NAME}",
        ],
        _sudo=True,
    )

    server.shell(
        name="wait for gitlab service 1/1",
        commands=[
            f"for i in $(seq 1 60); do "
            f"  state=$(docker service ls --filter name={STACK_NAME}_gitlab "
            "    --format '{{.Replicas}}' 2>/dev/null); "
            "  echo \"[$i/60] gitlab replicas=$state\"; "
            "  [ \"$state\" = \"1/1\" ] && exit 0; "
            "  sleep 10; "
            "done; exit 1",
        ],
        _sudo=True,
    )
