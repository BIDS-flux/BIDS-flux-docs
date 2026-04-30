"""Stage 1: install Docker, DataLad, git-annex, python venv tooling, OpenSSL.

Mirrors the pre-requisites section of source/INSTALLATION.rst. Idempotent.
"""

from pyinfra.operations import apt, files, server


def run() -> None:
    apt.update(name="apt update", cache_time=3600, _sudo=True)

    apt.packages(
        name="base packages",
        packages=[
            "ca-certificates",
            "curl",
            "gnupg",
            "lsb-release",
            "python3",
            "python3-venv",
            "python3-pip",
            "git",
            "jq",
            "make",
            "rsync",
            "openssl",
        ],
        _sudo=True,
    )

    files.directory(
        name="docker keyring dir",
        path="/etc/apt/keyrings",
        mode="0755",
        _sudo=True,
    )
    server.shell(
        name="docker gpg key",
        commands=[
            "test -s /etc/apt/keyrings/docker.gpg "
            "|| (curl -fsSL https://download.docker.com/linux/ubuntu/gpg "
            "| gpg --dearmor -o /etc/apt/keyrings/docker.gpg "
            "&& chmod a+r /etc/apt/keyrings/docker.gpg)",
        ],
        _sudo=True,
    )
    server.shell(
        name="docker apt repo",
        commands=[
            "CODENAME=$(. /etc/os-release && echo \"$VERSION_CODENAME\"); "
            "echo \"deb [arch=$(dpkg --print-architecture) "
            "signed-by=/etc/apt/keyrings/docker.gpg] "
            "https://download.docker.com/linux/ubuntu $CODENAME stable\" "
            "> /etc/apt/sources.list.d/docker.list",
            "apt-get update -qq",
        ],
        _sudo=True,
    )
    apt.packages(
        name="docker engine",
        packages=[
            "docker-ce",
            "docker-ce-cli",
            "containerd.io",
            "docker-buildx-plugin",
            "docker-compose-plugin",
        ],
        _sudo=True,
    )
    server.shell(
        name="enable docker",
        commands=["systemctl enable --now docker"],
        _sudo=True,
    )
    server.user(
        name="add vagrant to docker group",
        user="vagrant",
        groups=["docker"],
        _sudo=True,
    )

    apt.packages(
        name="datalad + git-annex",
        packages=["datalad", "git-annex"],
        _sudo=True,
    )

    # /data/* paths the upstream compose binds. We mkdir these on **both**
    # VMs because:
    #   - gitlab-runner is pinned to proc and binds /data/runner/{conf,certs,cache};
    #     running deploy/create_directory.sh only on data left those missing.
    #   - upstream's create_directory.sh makes /data/minio/backups but compose
    #     binds /data/minio/data — tiny upstream gap; we cover both.
    # `chmod go+w` matches what create_directory.sh does so non-root containers
    # (gitlab-runner, mercure) can write.
    server.shell(
        name="mkdir /data/* (compose bind sources)",
        commands=[
            "set -eu; "
            "mkdir -p "
            "  /data/gitlab/data /data/gitlab/logs /data/gitlab/backups "
            "  /data/gitlab/config/trusted-certs "
            "  /data/minio/data /data/minio/backups "
            "  /data/runner/conf /data/runner/certs /data/runner/cache "
            "  /data/dicom_endpoint/dicom_data/tmp "
            "  /data/mercure/db /data/mercure/data /data/mercure/config; "
            "chmod -R go+w "
            "  /data/gitlab/data /data/gitlab/logs /data/gitlab/backups "
            "  /data/gitlab/config/trusted-certs "
            "  /data/minio/backups "
            "  /data/runner /data/dicom_endpoint/dicom_data/tmp "
            "  /data/mercure",
        ],
        _sudo=True,
    )
