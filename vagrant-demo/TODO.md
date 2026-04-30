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
| `--dport 9789`                  | `--data-path-port 9789`[^swarm-flag]    |
| `GITLAB_HOME=/srv/gitlab`       | `/data/gitlab` (per `create_directory.sh`) |
| `MERCURE_BASE=/opt/mercure`     | `/data/mercure`                         |
| `MINIO_HOME=/mnt/minio-disks`   | `/data/minio`                           |

INSTALLATION.rst should be rewritten against `calgary` (or whichever active
branch is canonical) as a follow-up. Until then this `vagrant-demo/`
documents what actually works.

[^swarm-flag]: The actual `docker swarm init` flag is `--data-path-port`,
not `--dport`. The reference doc reads: "Port number used to send data;
if no value is set or is set to 0, the default port (4789) is used."
See <https://docs.docker.com/reference/cli/docker/swarm/init/>.

## hostname coupling

`docker-compose.stack.yml` on `calgary` hardcodes UCalgary swarm placement
constraints[^placement-constraints] (`node.hostname == itappcpipdp01.uc.ucalgary.ca`,
`itappcpippp01.uc.ucalgary.ca`). The Vagrantfile sets these as VM hostnames
verbatim so the upstream compose deploys without modification.

[^placement-constraints]: At submodule SHA `1bfcd55…` (calgary), all six service blocks declare a single-element `deploy.placement.constraints` list pinning to one of the two FQDNs: `gitlab` ([L28-L30](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L28-L30)), `gitlab-runner` ([L55-L57](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L55-L57)), `gitlab-runner-dind` ([L77-L79](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L77-L79)), `data_endpoint` ([L114-L116](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L114-L116)), `dicom_indexer` ([L144-L146](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L144-L146)), `minio` ([L204-L206](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L204-L206)).

To deploy on hosts with different names (typhon, washoe replacement, …) one
of: (a) override the placement constraints with a docker-compose override
file, (b) sed-rewrite the hostnames in a copy of the compose, or (c) switch
to the `montreal-update2dev` branch (uses `imagerie-server-{1,2}`).

- [ ] Add a docker-compose override file to demonstrate (a).

## switch demo VM hostnames away from `*.uc.ucalgary.ca`

The current Vagrantfile pins the VM hostnames to `itappcpip{dp,pp}01.uc.ucalgary.ca` because that's what upstream's swarm placement expects. That's misleading for *any* deployment that isn't UCalgary's — and the demo is the most prominent "isn't UCalgary's" case.

Pick neutral names — candidates:

- `data.bids-flux.localnet` / `proc.bids-flux.localnet`
- `data.bids-flux.example.com` / `proc.bids-flux.example.com` (RFC 2606 reserved domain — best for docs)
- `bids-flux-data` / `bids-flux-proc` (short, no domain)

Implementing this needs the docker-compose override from the previous
TODO — the placement constraints have to be rewritten in lockstep, or
the upstream compose patched in a fork. Don't ship the rename without
that override or stack deploy will silently park services at 0/1.

## centralise the deployment configuration

Right now site-specific values are scattered across at least four files:

- `Vagrantfile` — VM hostnames, IPs, resource sizing
- `inventories/vagrant.py` — IPs again, swarm advertise/manager addresses
- `tasks/swarm.py` — overlay subnet/gateway, swarm data-path port
- `tasks/stack.py` — stack name (`cpip`), `STACK_VM_PATH`, certificate CN

Each has to move in lockstep when adapting the demo to a real site. The
TODO is to consolidate into a single source of truth — likely a
top-level `config.env` (or `config.toml`) that `Vagrantfile` parses with
Ruby, the inventory parses with Python, and the Makefile sources for
shell-side use.

Constraints to research first:

- Does pyinfra v3 support reading a per-deploy config file cleanly, or
  do we ship our own loader in `tasks/_config.py` and import it from
  inventory + tasks?
- Does Vagrantfile's Ruby parse the same format the Python side wants?
  An `.env`-style file is the easiest common denominator; TOML needs a
  Ruby parser.
- Should overrides be per-site (one config file per inventory) or a
  single site-agnostic file with env-var overrides?

Until this lands, treat the four files above as a single conceptual
unit when changing site-specific values.

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
