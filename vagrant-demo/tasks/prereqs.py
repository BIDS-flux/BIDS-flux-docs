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

    # The calgary docker-compose.stack.yml volumes are rooted at /data — see
    # vagrant-demo/sourcedata/stack/deploy/create_directory.sh. We pre-create
    # the parent here; create_directory.sh fills in the leaves with the right
    # ownership during the stack stage.
    files.directory(
        name="mkdir /data",
        path="/data",
        mode="0755",
        _sudo=True,
    )
