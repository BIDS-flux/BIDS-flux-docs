# BIDS-flux local Vagrant demo

Two-VM, single-laptop reproduction of the `ni-dataops` deployment that the
BIDS-flux project actually runs in production. Tracks the upstream
`calgary` branch verbatim — `source/INSTALLATION.rst` in this repo
describes a different, abandoned branch (`stack_refactor`); see
[`TODO.md`](TODO.md) for the docs ↔ upstream divergence table.

| VM     | Role                                | Hostname                       | Private IP      | Forwarded host ports                                        |
|--------|-------------------------------------|--------------------------------|-----------------|-------------------------------------------------------------|
| `data` | GitLab, Runner DinD, MinIO, dicom   | `itappcpipdp01.uc.ucalgary.ca` | `192.168.56.10` | 8443→443, 8080→80, 2223→222, 5050→5050, 9000→9000, 9090→9090 |
| `proc` | GitLab Runner                       | `itappcpippp01.uc.ucalgary.ca` | `192.168.56.11` | none (talks to data over private net)                       |

The hostnames look funny on purpose: the upstream `docker-compose.stack.yml` pins swarm placement to those exact UCalgary names, so we use them verbatim and avoid modifying upstream files. To change, see the "hostname coupling" note in TODO.md.

## Prerequisites on the host

- Vagrant ≥ 2.2 with the `vagrant-libvirt` plugin
- libvirt + qemu/kvm (typhon and washoe replacement both have ≥ 32 GB RAM, sufficient for 12 + 8 GB allocations)
- Python ≥ 3.10 with `pyinfra` available (`pipx install pyinfra` or a venv)
- ssh client
- *(optional, for nice URLs)* add to the host `/etc/hosts`:

      127.0.0.1  itappcpipdp01.uc.ucalgary.ca

## Quick start

```bash
cd vagrant-demo
make init                # git submodule update --init for the four upstream repos
make up                  # boot both VMs
make deploy              # phases 1..4 (4 is partly manual: GitLab root PAT)
make smoke               # curl health endpoints on the host
```

`make deploy` chains:

    0. ssh-config              (Make target: writes .cache/ssh_config from
                                `vagrant ssh-config data proc` — pyinfra
                                reads this so we don't have to guess where
                                Vagrant put the SSH key)
    1. deploy-step1-prereqs    (pyinfra against both VMs: docker, datalad, openssl)
    2. deploy-step2-swarm-init (pyinfra --limit data: swarm init + cpip_network)
    3. swarm-fetch-join        (Make target: vagrant ssh into data, dump
                                /etc/bidsflux/swarm-join.sh into .cache/)
    4. deploy-step3-swarm-join (pyinfra --limit proc: upload .cache/ file
                                + docker swarm join)
    5. deploy-step4-stack      (pyinfra --limit data: stage upstream stack,
                                stub secrets, generate_secrets, stack deploy,
                                wait for gitlab healthy, run post-install if
                                GITLAB_TOKEN is set)

Each step is idempotent and can be re-run on its own. To regenerate the
SSH config after a `vagrant reload` or destroy/up cycle: `rm $(make -p
2>/dev/null | awk '/^SSH_CONFIG /{print $$3}')` then `make ssh-config`.

## Manual gate (after first deploy)

The first `make deploy` ends with a printed reminder to mint a root PAT in the GitLab UI (see [`TODO.md`](TODO.md) for the rails-runner automation plan):

```bash
export GITLAB_TOKEN=glpat-...
make deploy-step4-stack    # re-runs idempotently; this time post-install completes
```

## Resource overrides

Defaults assume a comfortable laptop. To shrink:

```bash
BIDSFLUX_DATA_MEM=8192 BIDSFLUX_DATA_CPUS=4 \
BIDSFLUX_PROC_MEM=4096 BIDSFLUX_PROC_CPUS=2 \
make up
```

To target a different libvirt-compatible Ubuntu box:

```bash
BIDSFLUX_BOX="generic/ubuntu2404" make up
```

## Targeting non-Vagrant infra (typhon, washoe replacement)

The pyinfra deploy is host-agnostic. Copy `inventories/vagrant.py` to e.g. `inventories/typhon.py`, replace the `ssh_*` keys, keep the `bidsflux_role` / `bidsflux_swarm_*` data fields, and:

```bash
INVENTORY=inventories/typhon.py make deploy
```

The hostname-coupling caveat above still applies: either set the target
machine's hostname to match upstream's swarm constraints, or apply the
override approach tracked in TODO.md.

## Layout

```
vagrant-demo/
├── Vagrantfile           # libvirt, two Ubuntu 22.04 VMs (calgary-pinned hostnames)
├── Makefile              # init / up / deploy-stepN / smoke / destroy
├── inventories/          # one file per target (vagrant default)
├── deploy_prereqs.py     # phase-1 entrypoint (both hosts)
├── deploy_swarm_init.py  # phase-2 entrypoint (data only)
├── deploy_swarm_join.py  # phase-3 entrypoint (proc only)
├── deploy_stack.py       # phase-4 entrypoint (data only)
├── tasks/                # shared helpers: prereqs, swarm, stack, post_install
├── sourcedata/           # submodules pinned to ni-dataops/* @ calgary:
│   ├── stack             # docker-compose.stack.yml + deploy/* scripts
│   ├── containers        # dicom_indexer, BIDS pipeline images
│   ├── ci-pipelines      # gitlab CI templates
│   └── bids-containers   # BIDS-flux image variants (main branch)
├── .cache/               # local-only; holds the swarm join command (gitignored)
├── TODO.md               # automation gaps + docs/upstream divergence
└── README.md             # you are here
```

## Troubleshooting

- `docker service ls` shows `0/1` — see `sudo docker stack ps cpip --no-trunc`. Common cause: a `secrets/<name>` file the compose mounts is missing or empty. `tasks/stack.py` seeds stubs for the user-supplied ones; if you've cleaned them, re-run `make deploy-step4-stack`.
- Worker won't join — check `192.168.56.0/24` reachability between VMs and that swarm ports are open (2377/tcp, 7946/tcp+udp, 9789/udp on the private libvirt network).
- Re-run idempotency — markers `.secrets-generated` and the seeded `secrets/*` files live under `/opt/bidsflux/stack/`. `make clean-secrets` removes the secrets-generated marker.
- The `gitlab` service is the slow one (4 GB RAM, several minutes to settle on first boot). The wait loop in `tasks/stack.py` polls for ten minutes (60 × 10s) before giving up.
