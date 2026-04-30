# vagrant-demo TODO

Tracked gaps and known divergences from upstream / this repo's docs.

## docs ↔ upstream divergence (this repo's `source/`)

`source/INSTALLATION.rst` was written against the abandoned
`ni-dataops/stack@stack_refactor` branch (last commit 2024-04-12). Names
that appear in INSTALLATION.rst but **do not exist** on any active branch:

| docs name                       | actual on `calgary` branch              |
|---------------------------------|-----------------------------------------|
| `BIDSflux_stack.yml`            | `docker-compose.stack.yml`              |
| `BIDS-flux.yml`                 | (same — `docker-compose.stack.yml`)     |
| `BIDS-flux-net`                 | `cpip_network`                          |
| `bids-flux/local-stack`         | `ni-dataops/stack`                      |
| `bids-flux/containers`          | `ni-dataops/containers`                 |
| `bids-flux/ci-pipelines`        | `ni-dataops/ci-pipelines`               |
| (not mentioned)                 | `ni-dataops/bids-containers`            |
| `init_ni-dataops.py`            | `deploy/post_gitlab_install.py`         |
| `dind_runner_configuration.json`| `deploy/runner_configuration-dind.json` |
| `mercure-setup.sh`              | (only on `mercure` branch)              |
| `docker-compose-mercure.yml`    | (only on `mercure` branch)              |
| `--dport 9789`                  | `--data-path-port 9789`                 |
| `GITLAB_HOME=/srv/gitlab`       | `/data/gitlab` (per `create_directory.sh`) |
| `MERCURE_BASE=/opt/mercure`     | `/data/mercure`                         |
| `MINIO_HOME=/mnt/minio-disks`   | `/data/minio`                           |

INSTALLATION.rst should be rewritten against `calgary` (or whichever active
branch is canonical) as a follow-up. Until then this `vagrant-demo/`
documents what actually works.

## hostname coupling

`docker-compose.stack.yml` on `calgary` hardcodes UCalgary swarm placement
constraints (`node.hostname == itappcpipdp01.uc.ucalgary.ca`,
`itappcpippp01.uc.ucalgary.ca`). The Vagrantfile sets these as VM hostnames
verbatim so the upstream compose deploys without modification.

To deploy on hosts with different names (typhon, washoe replacement, …) one
of: (a) override the placement constraints with a docker-compose override
file, (b) sed-rewrite the hostnames in a copy of the compose, or (c) switch
to the `montreal-update2dev` branch (uses `imagerie-server-{1,2}`).

- [ ] Add a docker-compose override file to demonstrate (a).

## stub secrets

`deploy/generate_secrets.sh` mints only 3 docker secrets
(`gitlab_root_password`, `minio_access_key`, `minio_secret_key`). The 8
file-secrets the compose mounts (`gitlab_local`, `gitlab_remote`,
`bundle.crt`, `cert.key`, `dicom_token`, `s3_id`, `s3_key`, `passphrase`,
`mc.conf`, `minio_pass`) are user-supplied. `tasks/stack.py` seeds these with
random/self-signed stubs so first deploy succeeds; rotate to real values
during post-install or for production.

- [ ] Replace stubs with values minted by `deploy/post_gitlab_install.py`
      once that script runs end-to-end against our self-hosted gitlab.

## GitLab root PAT (currently manual)

Stage 4 prints an instructional message if `GITLAB_TOKEN` is missing.

- [ ] Mint via `gitlab-rails runner` inside the gitlab container:
      ```bash
      docker exec -i $(docker ps -q -f name=cpip_gitlab) gitlab-rails runner \
        'u = User.find_by_username("root"); \
         t = u.personal_access_tokens.create!(scopes: %w[api admin_mode read_user read_repository write_repository read_registry write_registry read_package write_package], name: "bootstrap", expires_at: 365.days.from_now); \
         t.set_token(SecureRandom.hex(20)); t.save!; puts t.token'
      ```
      Wire into `tasks/post_install.py` so the demo is fully hands-off.
- [ ] Validate scope set against gitlab-ee 17.7 token API.

## GitLab Runner registration

`deploy/runner_registration.py` (calgary) prompts interactively for the
`dicom_bot` token via `docker login`. We need to:

- [ ] Patch the script (or maintain a fork) to accept a non-interactive flag.
- [ ] Migrate to GitLab 16+ runner-token auth (no more registration tokens).

## Mercure (not on calgary)

The `mercure` branch of `ni-dataops/stack` carries the Mercure flow. To
exercise it:

- [ ] Add a `BRANCH=mercure` switch to `make init` so submodules pin to
      `mercure` instead of `calgary` for testing the DICOM-via-Mercure path.
- [ ] Seed `data_endpoint/configuration/default_mercure.json` rules at
      deploy time to skip the GUI clicks documented in INSTALLATION.rst.

## DICOM scanner / sample data

For end-to-end testing:

- [ ] Add a `make replay-sample` target that pushes a small DICOM set via
      `storescu` (from `dcmtk`) at `localhost:2100` to exercise the
      storescp ingest path.

## Reference: vendored upstream layout

Submodules under `vagrant-demo/sourcedata/` (initialized via `make init`):

- `stack` — compose files, deploy scripts, runner config templates (calgary).
- `containers` — Dockerfiles for dicom_indexer, BIDS pipelines (calgary).
- `ci-pipelines` — GitLab CI templates run by the runners (calgary).
- `bids-containers` — BIDS-flux specific image variants (main).

`branch =` is set in `.gitmodules` so `git submodule update --remote` will
follow upstream HEAD on those branches; bump deliberately and re-run
`make destroy && make up && make deploy` to re-validate.
