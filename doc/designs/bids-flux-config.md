# Centralised configuration for BIDS-flux deployments

Status: design / research — *no implementation yet*. Tracked from
`vagrant-demo/TODO.md` ("centralise the deployment configuration").

## Goal

Today the deploy recipe carries site-specific values in at least four
files, each consumed by a different runtime:

| file                              | runtime | values today                                         |
|-----------------------------------|---------|------------------------------------------------------|
| `vagrant-demo/Vagrantfile`        | Ruby    | VM hostnames, IPs, resource sizing, port forwards    |
| `vagrant-demo/inventories/vagrant.py` | Python (pyinfra) | hostnames, IPs, swarm advertise/manager addresses |
| `vagrant-demo/tasks/swarm.py`     | Python  | overlay subnet/gateway, swarm data-path port, network name |
| `vagrant-demo/tasks/stack.py`     | Python  | stack name (`cpip`), stack VM path, certificate CN   |
| `vagrant-demo/Makefile`           | GNU make | DATA_NAME, PROC_NAME, ssh-config path               |

Any change to a domain name, IP block, or stack name today has to be
edited in lockstep across these. The goal is one source of truth that
every runtime consults.

## Recommendation

**Hybrid `.env` file + environment-variable overrides**, all keys
prefixed `BIDS_FLUX_*`.

- Defaults in `vagrant-demo/.env` (gitignored), shipped as `.env.example`.
- Override per-invocation: `BIDS_FLUX_TLD=foo make deploy`.
- Make `include`s `.env` and `export`s its keys to children.
- Vagrantfile parses `.env` with a 5-line Ruby snippet.
- pyinfra inventory + tasks read `os.environ` (Make already exports them).
- (Future) `docker-compose.stack.yml` substitution reads the same `.env`
  via Compose's native support.

The user's instinct ("alternative — define env vars like `BIDS_FLEX_TLD`
and make those consult it, mandating it to be defined") collapses to this:
mandatory env-vars *with* `.env` providing sensible defaults.

> Naming nit: the project is `bids-flux` everywhere else in this repo, so
> standardise on `BIDS_FLUX_*` (assumed; the user's text said `BIDS_FLEX`,
> probably a typo). Worth confirming before locking in a prefix.

## Why over the alternatives

| approach                | Vagrantfile (Ruby)        | pyinfra (Python)            | Makefile (GNU make) | new dep      | overrideable        | Docker Compose native? |
|-------------------------|---------------------------|-----------------------------|---------------------|--------------|---------------------|-----------------------|
| YAML file               | stdlib                    | needs `pyyaml`              | needs `yq`          | yes          | edit-only           | no                    |
| TOML file               | needs `toml-rb` gem       | stdlib (Py ≥ 3.11)          | needs `toml-cli`    | yes          | edit-only           | no                    |
| JSON file               | stdlib                    | stdlib                      | needs `jq`          | maybe        | edit-only           | no                    |
| Pure env vars (no file) | `ENV[]`                   | `os.environ`                | `$(VAR)`            | none         | trivially           | yes (var sub)         |
| **`.env` + env override** | 5-line reader           | `os.environ` / `python-dotenv` | `include` + `export` | none      | trivially           | yes (Compose reads `.env`) |

`.env` wins three ways: zero new dependencies, all five consumers parse
key=value identically, and Compose v2 reads `.env` from the project
directory natively — the upstream `stack_refactor` branch literally
shipped one.

## Suggested keys (illustrative, not final)

```sh
# vagrant-demo/.env.example

# --- domain / hostnames ------------------------------------------------
BIDS_FLUX_TLD=bids-flux.example.com           # rfc2606 reserved (.localnet OK too)
BIDS_FLUX_DATA_HOST=data.${BIDS_FLUX_TLD}
BIDS_FLUX_PROC_HOST=proc.${BIDS_FLUX_TLD}

# --- networking --------------------------------------------------------
BIDS_FLUX_PRIVATE_NET_CIDR=192.168.56.0/24    # libvirt private net
BIDS_FLUX_DATA_IP=192.168.56.10
BIDS_FLUX_PROC_IP=192.168.56.11
BIDS_FLUX_OVERLAY_NAME=cpip_network           # must match upstream
BIDS_FLUX_OVERLAY_SUBNET=192.11.0.0/16
BIDS_FLUX_OVERLAY_GATEWAY=192.11.0.2
BIDS_FLUX_SWARM_DATA_PORT=9789

# --- stack identity ----------------------------------------------------
BIDS_FLUX_STACK_NAME=cpip                     # `docker stack deploy <name>`
BIDS_FLUX_STACK_BRANCH=calgary                # submodule branch
BIDS_FLUX_STACK_VM_PATH=/opt/bidsflux/stack

# --- vagrant resourcing (already env-overridable today) ---------------
BIDSFLUX_DATA_CPUS=6
BIDSFLUX_DATA_MEM=12288
BIDSFLUX_PROC_CPUS=4
BIDSFLUX_PROC_MEM=8192
```

## Implementation sketch (consumer-by-consumer)

### Makefile

```make
ifneq (,$(wildcard .env))
include .env
export
endif
```

Three lines. Variables in `.env` become Make variables AND are exported
into every recipe's environment, so child Ruby/Python/shell processes
see them.

### Vagrantfile

```ruby
# Load .env if present; existing ENV wins (so `BIDS_FLUX_TLD=foo vagrant up` works).
File.foreach('.env') do |line|
  next if line.strip.empty? || line.start_with?('#')
  k, v = line.strip.split('=', 2)
  ENV[k] ||= v if k && v
end if File.exist?('.env')

DATA_HOST = ENV.fetch('BIDS_FLUX_DATA_HOST')
PROC_HOST = ENV.fetch('BIDS_FLUX_PROC_HOST')
# ... existing constants read ENV directly
```

`fetch` raises if the key is unset → loud failure beats silent default.

### pyinfra inventory + tasks

```python
import os

DATA_HOST = os.environ['BIDS_FLUX_DATA_HOST']  # KeyError = loud failure
DATA_IP   = os.environ['BIDS_FLUX_DATA_IP']
# ... etc
```

Or a tiny `tasks/_config.py` that does this once and exports a dict so
typos surface as `AttributeError` instead of silent `None`.

### Docker Compose

Compose v2 reads `.env` from the project dir (where the YAML lives) on
its own. If our `.env` lives at `vagrant-demo/.env` but compose runs
inside `/opt/bidsflux/stack/`, we either:

1. `cp .env /opt/bidsflux/stack/.env` during stage 3 (simple), or
2. symlink / bind-mount, or
3. point Compose at our file via `--env-file`.

Option 1 is simplest for the demo.

## Open research questions

These would be the first items for the implementation session:

1. **Compose's existing `.env` behaviour.** Does the upstream `calgary`
   branch already ship a `.env` we'd be overwriting? (As of survey:
   no `.env` on calgary; `stack_refactor` had one, but that branch is
   dead.) Confirm + decide whether ours coexists or replaces.

2. **Naming consistency.** Existing Vagrantfile uses `BIDSFLUX_*` (no
   underscore). Migrate those to `BIDS_FLUX_*` for one consistent prefix,
   or grandfather them and add the new prefix alongside? Recommend
   migrating with a one-cycle deprecation note.

3. **Validation strategy.** Should `tasks/_config.py` enforce required
   keys at import time with friendly error messages, or trust each
   consumer to fail loudly when a key is missing? Lean toward an
   explicit validation step — a single `make config-check` target that
   reports every missing key at once beats a deploy that fails halfway
   through stage 3.

4. **Parser dep boundaries.** Three-line Ruby reader is dep-free but
   limited (no `${VAR}` interpolation, no quoted multi-line). The Python
   side could use `python-dotenv` for fancier parsing — but that's a new
   dep. Recommend the dep-free reader on both sides, and ban
   interpolation/quoting in `.env` to keep them in sync.

5. **Hostname rename is paired with a docker-compose override.**
   Centralising config doesn't fix the upstream-pinned
   `node.hostname == itappcpipdp01.uc.ucalgary.ca` constraints. The
   `.env` rollout has to land alongside the override (TODO entry
   "switch demo VM hostnames away from `*.uc.ucalgary.ca`"), or stack
   deploy will silently park services at 0/1 after a hostname change.

6. **Per-site inventories.** When we eventually have multiple
   inventories (vagrant, typhon, washoe-replacement), do they each
   carry their own `.env`, or do they all sit under one site-agnostic
   `.env` with `BIDS_FLUX_SITE_*` prefixes? Probably one `.env` per
   inventory, kept beside it.

7. **Secrets vs config.** Keep secrets out of `.env`. Docker Swarm
   secrets handle the gitlab/MinIO/cert files; `.env` should stay
   versionable (via `.env.example`) and free of credentials.

## Decision deferred

No code changes from this design pass — that's the next session's job
once we resolve at least Q1, Q2, and Q5 above.
