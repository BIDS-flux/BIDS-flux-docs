"""Stage 4: gated GitLab API automation against upstream calgary scripts.

Real upstream entrypoints on calgary (vs. the names in the stale docs):

    deploy/post_gitlab_install.py        (was: init_ni-dataops.py)
    deploy/runner_registration.py        (same name; signature differs)
    deploy/runner_configuration.json
    deploy/runner_configuration-dind.json (note: dash, not underscore)

These need a root personal access token. We gate on GITLAB_TOKEN env var;
without it we print an instructional message and stop. See TODO.md for
the rails-runner approach to mint the PAT non-interactively.
"""

import os

from pyinfra.operations import server

from .stack import STACK_VM_PATH


def run_on_manager() -> None:
    gitlab_token = os.environ.get("GITLAB_TOKEN", "").strip()

    if not gitlab_token:
        server.shell(
            name="GitLab API config (skipped — GITLAB_TOKEN not set)",
            commands=[
                "echo '>>> GITLAB_TOKEN not set; skipping post_gitlab_install + runner_registration.'",
                "echo '>>> 1) open https://127.0.0.1:8443 and log in as root with the password'",
                "echo '>>>    printed in /opt/bidsflux/stack/.secrets-output on the data VM'",
                "echo '>>> 2) create a PAT (api, admin_mode, read/write_repository, read/write_registry, read/write_package, read_user)'",
                "echo '>>> 3) GITLAB_TOKEN=<tok> make deploy-step4-stack'",
                "echo '>>> See vagrant-demo/TODO.md for the rails-runner automation plan.'",
            ],
        )
        return

    server.shell(
        name="python venv for deploy scripts",
        commands=[
            f"cd {STACK_VM_PATH} && "
            "test -d .venv || python3 -m venv --system-site-packages .venv; "
            ". .venv/bin/activate && "
            "pip install --quiet python-gitlab requests datalad",
        ],
        _sudo=True,
    )

    server.shell(
        name="register gitlab runners",
        commands=[
            f"cd {STACK_VM_PATH} && . .venv/bin/activate && "
            f"GITLAB_TOKEN={gitlab_token} "
            "python deploy/runner_registration.py "
            "$HOME/.docker/config.json deploy/runner_configuration.json "
            "cpip_gitlab-runner.x && "
            f"GITLAB_TOKEN={gitlab_token} "
            "python deploy/runner_registration.py "
            "$HOME/.docker/config.json deploy/runner_configuration-dind.json "
            "cpip_gitlab-runner-dind.x",
        ],
        _sudo=True,
    )

    server.shell(
        name="post_gitlab_install (creates bots, mirrors repos)",
        commands=[
            f"cd {STACK_VM_PATH} && . .venv/bin/activate && "
            f"GITLAB_TOKEN={gitlab_token} "
            "python deploy/post_gitlab_install.py",
        ],
        _sudo=True,
    )
