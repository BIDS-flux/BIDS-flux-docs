# vagrant-demo TODO

Sequenced plan for finalising the demo, plus post-deploy backlog and
reference material. Phases are ordered so each unblocks the next; do not
skip ahead without reading the dependency notes.

## Phase 0 — get `make deploy` actually green on the host

**Status:** in progress. `make deploy` currently fails at step 2
(`overlay network cpip_network`) with "This node is not a swarm
manager" even though the previous three operations report `Success`.

Root cause: shell-level error masking in `tasks/swarm.py`.

- `swarm init (idempotent)` uses `docker info … | grep -q active || docker swarm init …`. If the right side fails after the left side returns 1, the whole expression returns the right side's exit code — but pyinfra still reports `Success` if the *operation* (single shell invocation) ran at all? Actually no, non-zero exit propagates. The mystery is why it doesn't here. Likely candidate: the init *does* run with exit 0, but doesn't actually leave the node as a manager (silent partial failure, e.g., advertise-addr binding race against libvirt's bring-up of the bidsflux private network).
- `dump worker join command` does `TOKEN=$(docker swarm join-token worker -q); printf … > /etc/bidsflux/swarm-join.sh`. Bash assignment `TOKEN=$(…)` *always* returns 0 even when the subcommand fails — so this step's `Success` is meaningless. The empty/garbage token gets written silently.
- Only `overlay network cpip_network` calls a daemon API that surfaces the swarm-not-up reality.

Fix plan (this commit):

- [ ] Drop the `||` masking. Run `docker info | grep -q active` as a
      separate exit-code check, then run `docker swarm init …` if
      needed, capturing stderr and failing loudly.
- [ ] Add a post-condition: `docker info --format '{{.Swarm.ControlAvailable}}' | grep -q true` after init. If we're not a manager after the step, the operation must error.
- [ ] Same `TOKEN=…` problem in `dump worker join command`. Use `set -o pipefail; TOKEN=$(docker swarm join-token worker -q) && printf …` so a join-token failure aborts.
- [ ] Audit `tasks/stack.py` for the same anti-patterns (`||`, `$(…)` assignments, unchecked subshells).

### Known residual Rejected services after this round

These won't reach 1/1 in phase 0 — they need separate follow-ups:

- **`cpip_gitlab-runner.1` (proc)** — needs `gitlab-runner-calgary:latest` image on proc; we currently only build it on data. Follow-up: either sync `deploy/Dockerfile-runner` + a bundle.crt to proc and `docker build` there, or `docker save` from data + `docker load` on proc via pyinfra `files.get`/`files.put`.
- **`cpip_dicom_endpoint.1`** — needs `ITAPPCPIPDP01.uc.ucalgary.ca:5050/ni-dataops/containers/dicom_indexer:latest` from the GitLab container registry. The image gets built and pushed by the **CI pipelines in `containers/`** repo, which can only run after GitLab is up + bots are registered. Defer to post_install (see "GitLab Runner registration" backlog item).

`cpip_gitlab-runner-dind`, `cpip_scratch`, `cpip_minio`, and `cpip_gitlab` itself should all reach 1/1 — those are what `wait for gitlab service 1/1` gates on.

After phase 0 is green, before moving on:

- [ ] Run `make smoke` — expect HTTP responses from GitLab and MinIO.
- [ ] `vagrant ssh data -c "sudo docker service ls"` — every service `1/1`.
- [ ] Mint the root PAT manually (see Backlog → GitLab root PAT) and
      re-run `GITLAB_TOKEN=… make deploy-step4-stack`.
- [ ] Confirm `post_gitlab_install.py` completes against our gitlab-ee.

If any of these fail, phase 0 isn't done — iterate before touching
phase 1.

## Phase 1 — centralise the deployment configuration

**Depends on:** phase 0 (need a known-working baseline before refactoring).

Today site-specific values are scattered across at least five files:

- `Vagrantfile` — VM hostnames, IPs, resource sizing, port forwards
- `inventories/vagrant.py` — IPs again, swarm advertise/manager addresses
- `tasks/swarm.py` — overlay subnet/gateway, swarm data-path port, network name
- `tasks/stack.py` — stack name (`cpip`), `STACK_VM_PATH`, certificate CN
- `Makefile` — DATA_NAME, PROC_NAME, ssh-config path

Any change to a domain name, IP block, or stack name has to land in
lockstep across these. Goal: one source of truth.

**Approach:** `.env` file + env-var override, `BIDS_FLUX_*` prefix.
Full rationale + comparison tables + per-consumer implementation
sketches in [`doc/designs/bids-flux-config.md`](../doc/designs/bids-flux-config.md).

Open questions to resolve before implementation:

- [ ] Q1 — does the upstream `calgary` branch ship a `.env` we'd be
      overwriting? (Survey suggests no, but confirm.)
- [ ] Q2 — naming: existing Vagrantfile uses `BIDSFLUX_*` (no
      underscore). Migrate to `BIDS_FLUX_*` for consistency or
      grandfather? Recommend migrating with a one-cycle deprecation.
- [ ] Q3 — validation strategy: `tasks/_config.py` import-time required-key check vs. trust-and-fail-loudly?
- [ ] Q4 — parser dep boundary: dep-free 5-line readers in Ruby/Python vs. `python-dotenv`? Recommend dep-free, ban `${VAR}` interpolation in `.env` to keep readers in sync.
- [ ] Q5 — coupled with phase 2 (hostname rename). Centralisation alone doesn't fix the upstream-pinned `node.hostname == itappcpipdp01…` constraints.
- [ ] Q6 — per-site inventories: does each carry its own `.env`, or one site-agnostic with env-var overrides? Recommend one `.env` per inventory, kept beside it.
- [ ] Q7 — secrets vs. config: keep secrets *out* of `.env` (they're handled by Docker Swarm secrets and the seeded files in `secrets/`).

Implementation tasks (after Q1/Q2/Q5 resolved):

- [ ] Ship `vagrant-demo/.env.example`; gitignore `.env`.
- [ ] `Makefile`: `ifneq (,$(wildcard .env)) include .env / export / endif`.
- [ ] `Vagrantfile`: 5-line `.env` reader (existing-`ENV` wins for overrides).
- [ ] `tasks/_config.py`: required-keys load + helpful error messages.
- [ ] Migrate `Vagrantfile`, `inventories/vagrant.py`, `tasks/swarm.py`, `tasks/stack.py`, `Makefile` to read from `os.environ` / `ENV`.
- [ ] Update `doc/designs/bids-flux-config.md` to mark questions resolved.

## Phase 2 — hostname rename + docker-compose override

**Depends on:** phase 1 (consumes `BIDS_FLUX_TLD` and friends).

The current `Vagrantfile` pins VM hostnames to `itappcpip{dp,pp}01.uc.ucalgary.ca` because that's what upstream's `docker-compose.stack.yml` expects in its swarm placement constraints[^placement-constraints]. That's misleading for *any* deployment that isn't UCalgary's — and the demo is the most prominent "isn't UCalgary's" case.

[^placement-constraints]: At submodule SHA `1bfcd55…` (calgary), all six service blocks declare a single-element `deploy.placement.constraints` list pinning to one of the two FQDNs: `gitlab` ([L28-L30](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L28-L30)), `gitlab-runner` ([L55-L57](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L55-L57)), `gitlab-runner-dind` ([L77-L79](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L77-L79)), `data_endpoint` ([L114-L116](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L114-L116)), `dicom_indexer` ([L144-L146](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L144-L146)), `minio` ([L204-L206](https://gitlab.unf-montreal.ca/ni-dataops/stack/-/blob/1bfcd551520ae7e771fcd459428cde47a44eb192/docker-compose.stack.yml#L204-L206)).

**Strategy:** rename + write a docker-compose override that rewrites
the placement constraints to match. The rename and the override land
together — shipping just the rename will silently park services at
0/1.

Candidate names (pick during phase 1):

- `data.bids-flux.example.com` / `proc.bids-flux.example.com` (RFC 2606 reserved domain — best for docs and avoidance of accidental real-DNS lookups)
- `data.bids-flux.localnet` / `proc.bids-flux.localnet`
- `bids-flux-data` / `bids-flux-proc` (short, no domain)

Tasks:

- [ ] Add `vagrant-demo/files/compose-override.yml` rewriting every
      `deploy.placement.constraints` block to the new hostnames.
- [ ] Update `tasks/stack.py` to deploy with `-c docker-compose.stack.yml -c compose-override.yml`.
- [ ] Add a `BRANCH=montreal-update2dev` short-circuit (uses `imagerie-server-{1,2}`) in case we ever need that flow.
- [ ] Verify swarm placement actually resolves under the new names (`docker stack ps cpip --no-trunc` shows non-zero replicas for every service).

## Phase 3 — SSH access for Claude (assistant)

**Depends on:** phase 0 (need a working VM to install a key on).
**Independent of phase 2 / phase 4.**

So Claude can iterate on `make deploy` without the user copy-pasting
logs. Project-scoped key, never the user's private vagrant key.

Tasks:

- [ ] `make claude-bootstrap`: generates `vagrant-demo/.cache/claude_key{,.pub}` (ed25519, no passphrase) if not present.
- [ ] One-shot installer (Make target or one-liner) that does
      `vagrant ssh data -c "echo '$(cat .cache/claude_key.pub)' >> ~/.ssh/authorized_keys"` and same for `proc`.
- [ ] OR: a Vagrantfile shell provisioner that appends the pubkey on `vagrant up` / `reload`, so the key survives VM rebuild.
- [ ] Patch `inventories/vagrant.py` to use `IdentityFile=$(realpath .cache/claude_key)` when running under Claude (env-var-gated to keep user-side runs unchanged).
- [ ] README: 5-line "what you do, what I do" for granting and revoking the access.

## Phase 4 — port forwards into Claude's podman env

**Depends on:** phase 3 (needs the project key in place).
**Independent of phase 2.**

Claude runs in a podman sandbox without direct reach into libvirt's
192.168.121.0/24 management subnet or the bidsflux 192.168.56.0/24
private subnet. Need a tunnel.

Tasks:

- [ ] `make claude-tunnels`: runs `ssh -L 22210:192.168.121.<data-ip>:22 -L 22211:192.168.121.<proc-ip>:22 -L 8443:127.0.0.1:8443 …` against the right entry point in the user's env.
- [ ] Document the host-side port forwards needed for HTTPS/MinIO/Mercure (8443/9000/9090/8000) so Claude can `curl` them inside the sandbox.
- [ ] README: minimum-trust description of what the tunnel exposes (only the four service ports + two SSH ports), how to revoke.

## Backlog (post-deploy improvements)

These are not on the critical path — they make the demo nicer/more
complete after phase 0–4 are done.

### stub secrets

`deploy/generate_secrets.sh` mints only 3 docker secrets
(`gitlab_root_password`, `minio_access_key`, `minio_secret_key`). The
8 file-secrets the compose mounts (`gitlab_local`, `gitlab_remote`,
`bundle.crt`, `cert.key`, `dicom_token`, `s3_id`, `s3_key`,
`passphrase`, `mc.conf`, `minio_pass`) are user-supplied.
`tasks/stack.py` seeds these with random/self-signed stubs so first
deploy succeeds; rotate to real values during post-install.

- [ ] Replace stubs with values minted by `deploy/post_gitlab_install.py`
      once that script runs end-to-end against our self-hosted gitlab.

### GitLab root PAT (currently manual)

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

### Extract multi-line shell to `files/scripts/` + shellcheck CI

Today most of `tasks/{prereqs,swarm,stack,post_install}.py` is
multi-statement shell embedded in Python f-strings. Quoting hell
(`\\1` for sed backrefs, `\"` everywhere), no syntax highlighting,
not testable in isolation. pyinfra ships a first-class operation for
this: [`server.script`](https://docs.pyinfra.com/en/3.x/operations/server.html#server-script)
uploads a local file and executes it remotely; the variant
`server.script_template` Jinja-renders first.

Recommended layout once phase 0 is closed:

```
vagrant-demo/files/scripts/
├── README.md              # "shipped via server.script"
├── swarm_init.sh          # set -eu; pre-flight; docker swarm init; verify
├── swarm_join.sh          # token + advertise as $1 $2
├── seed_secrets.sh        # 11 file-stubs + cert
└── build_local_images.sh  # docker build runner + scratch
```

Add `# shellcheck shell=bash` to each script; new `make shellcheck`
target running `shellcheck files/scripts/*.sh`; gate in CI.

- [ ] Pick the dividing line — keep `server.shell` for one-liners
      (e.g. `mkdir`, single `docker swarm leave`), use
      `server.script` for everything `set -eu`-prefaced.
- [ ] Decide args-via-`$1$2` vs. `_env={...}` vs.
      `server.script_template` per script (3+ params probably wants
      template; few-args wants positional).
- [ ] Acknowledge `server.script` is non-idempotent per pyinfra
      (no built-in change detection) — the scripts already encode
      `if [ ! -X ]; then …; fi` guards so re-runs are still cheap.

### GitLab Runner registration

`deploy/runner_registration.py` (calgary) prompts interactively for the
`dicom_bot` token via `docker login`.

- [ ] Patch the script (or maintain a fork) to accept a non-interactive flag.
- [ ] Migrate to GitLab 16+ runner-token auth (no more registration tokens).

### Mercure (not on calgary)

The `mercure` branch of `ni-dataops/stack` carries the Mercure flow.

- [ ] Add a `BRANCH=mercure` switch to `make init` so submodules pin to
      `mercure` instead of `calgary` for testing the DICOM-via-Mercure path.
- [ ] Seed `data_endpoint/configuration/default_mercure.json` rules at
      deploy time to skip the GUI clicks documented in INSTALLATION.rst.

### DICOM scanner / sample data

For end-to-end testing:

- [ ] Add a `make replay-sample` target that pushes a small DICOM set via
      `storescu` (from `dcmtk`) at `localhost:2100` to exercise the
      storescp ingest path.

### Diagnosis follow-up: was c773508's "FQDN doesn't match `--limit`" claim correct?

The commit message for `c773508` blamed pyinfra's `--limit` for not
matching dotted FQDN host names. Investigation by the citation
sub-agent (commit `eb597e4`) reading `pyinfra_cli/cli.py
_apply_inventory_limit` at v3.7 (`L691-L708`) shows `--limit` uses
`fnmatch(host.name, limiter)` after a `get_group` fallback — exact
string match should have worked. The actual fix in `c773508` was
swapping the SSH discovery path to `vagrant ssh-config`; the
simultaneous FQDN→short rename was incidental, not causal.

- [ ] Re-test with the *old* inventory (FQDN host names) plus the *new* SSH discovery (ssh_config_file) to disambiguate. If `--limit <fqdn>` works there, correct the commit message attribution somewhere visible (release notes, future commit message reference).

## Reference: cleansing existing setup before a fresh run

Run on the host before re-attempting `make deploy` from scratch (e.g.,
after a hostname rename in phase 2):

```bash
cd ~/proj/misc/BIDS-flux-docs/vagrant-demo

# 1. Tear down VMs
make destroy

# 2. Confirm libvirt sees no leftover domains for this project
virsh list --all | grep -E 'vagrant-demo_(data|proc)' || echo "(none)"

# 3. The libvirt private network "bidsflux" persists across destroy
virsh net-destroy bidsflux 2>/dev/null || true
virsh net-undefine bidsflux 2>/dev/null || true

# 4. Optional: free the ~500 MB box image
vagrant box remove generic/ubuntu2204 --provider libvirt --all --force 2>/dev/null || true

# 5. Project-local state
rm -rf .cache/                                    # ssh_config, swarm-join command
rm -f log.txt log-deploy.txt out.txt              # old run logs
rm -rf sourcedata/stack/secrets/                  # stub secrets seeded inside the VM
rm -f sourcedata/stack/.secrets-generated sourcedata/stack/.secrets-output

# 6. Forget VM SSH host keys (their IPs likely change on re-up)
ssh-keygen -R 192.168.121.211 2>/dev/null || true
ssh-keygen -R 192.168.121.199 2>/dev/null || true

# 7. Submodules can stay (just local clones). Sanity:
git submodule status
git status   # should show only untracked logs / .cache after the rm
```

After this, `make init` is a no-op and `make up && make deploy` start fresh.

## Reference: how to explore a running deployment

When phase 0 finishes and `make deploy` ends green, these are the
handles to inspect what's actually up:

```bash
# Service-level: every service should be 1/1
vagrant ssh data -c "sudo docker service ls"

# Per-service tasks (which node it's pinned to, current state)
vagrant ssh data -c "sudo docker stack ps cpip --no-trunc"

# Per-service logs (replace cpip_gitlab with whatever you're chasing)
vagrant ssh data -c "sudo docker service logs cpip_gitlab --tail 200"
vagrant ssh data -c "sudo docker service logs cpip_minio  --tail 200"

# Swarm state from the manager's perspective
vagrant ssh data -c "sudo docker node ls"
vagrant ssh data -c "sudo docker info --format '{{.Swarm.LocalNodeState}} ControlAvailable={{.Swarm.ControlAvailable}}'"

# Overlay network membership
vagrant ssh data -c "sudo docker network inspect cpip_network --format '{{range .Containers}}{{.Name}} {{end}}'"

# Secrets present in the swarm (names only, not values)
vagrant ssh data -c "sudo docker secret ls"
```

From the host:

```bash
# GitLab UI (root password is in /opt/bidsflux/stack/.secrets-output on the VM)
xdg-open https://127.0.0.1:8443/

# MinIO console
xdg-open http://127.0.0.1:9090/

# Health-check round-trip — `make smoke` does this
make smoke
```

Useful upstream docs:

- `docker stack` reference: <https://docs.docker.com/reference/cli/docker/stack/>
- swarm troubleshooting: <https://docs.docker.com/engine/swarm/admin_guide/>
- pyinfra cli flags (verbose / debug / facts): <https://docs.pyinfra.com/en/3.x/cli.html>

If something is silently zero-replicas, the usual suspects are:

1. **Placement constraint mismatch** — `docker node ls` to confirm the
   node hostnames; compare against the placement strings in
   `docker-compose.stack.yml`.
2. **Missing volume directory** — `/data/{gitlab,minio,...}` on the
   target node (created by `deploy/create_directory.sh`).
3. **Missing/empty secret file** — `secrets/<name>` referenced by
   compose; check size with `vagrant ssh data -c "sudo wc -c /opt/bidsflux/stack/secrets/*"`.

## Reference: docs ↔ upstream divergence (this repo's `source/`)

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

INSTALLATION.rst should be rewritten against `calgary` (or whichever
active branch is canonical) as a follow-up. Until then this
`vagrant-demo/` documents what actually works.

[^swarm-flag]: The actual `docker swarm init` flag is `--data-path-port`, not `--dport`. The reference doc reads: "Port number used to send data; if no value is set or is set to 0, the default port (4789) is used." See <https://docs.docker.com/reference/cli/docker/swarm/init/>.

## Reference: vendored upstream layout

Submodules under `vagrant-demo/sourcedata/` (initialized via `make init`):

- `stack` — compose files, deploy scripts, runner config templates (calgary).
- `containers` — Dockerfiles for dicom_indexer, BIDS pipelines (calgary).
- `ci-pipelines` — GitLab CI templates run by the runners (calgary).
- `bids-containers` — BIDS-flux specific image variants (main).

`branch =` is set in `.gitmodules` so `git submodule update --remote` will
follow upstream HEAD on those branches; bump deliberately and re-run
`make destroy && make up && make deploy` to re-validate.
