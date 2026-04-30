.PHONY: help init up halt destroy deploy ssh-config \
        deploy-step1-prereqs deploy-step2-swarm-init swarm-fetch-join \
        deploy-step3-swarm-join deploy-step4-stack \
        smoke status clean-secrets clean-cache

VAGRANT ?= vagrant
PYINFRA ?= pyinfra
INVENTORY ?= inventories/vagrant.py
CACHE_DIR := .cache
SSH_CONFIG := $(CACHE_DIR)/ssh_config

# Pass-through flags for every pyinfra invocation. Default empty
# (interactive — pyinfra prints a "Detected changes / Press enter to
# execute" gate). Set PYINFRA_YES=-y to auto-confirm:
#
#     PYINFRA_YES=-y make deploy
#     PYINFRA_YES=-y make deploy-step4-stack
#
# Or `-q` to also quieten pyinfra's per-op detection table:
#     PYINFRA_FLAGS="-y -q" make deploy
PYINFRA_YES   ?=
PYINFRA_FLAGS ?= $(PYINFRA_YES)

# Inventory-side host aliases — must match `Host data` / `Host proc` in
# vagrant ssh-config output, and the `config.vm.define` names in the
# Vagrantfile. Distinct from the swarm placement constraint hostnames
# baked into upstream calgary's docker-compose.stack.yml (those are the
# VM /etc/hostname values, set in the Vagrantfile).
DATA_NAME := data
PROC_NAME := proc

help:
	@echo "Targets:"
	@echo "  init                     -- git submodule update --init for sourcedata/*"
	@echo "  up                       -- vagrant up data + proc"
	@echo "  ssh-config               -- regenerate $(SSH_CONFIG) from \`vagrant ssh-config\`"
	@echo "  deploy                   -- chain steps 1..4 (full deploy)"
	@echo "  deploy-step1-prereqs     -- phase 1: prereqs on both hosts"
	@echo "  deploy-step2-swarm-init  -- phase 2: swarm init on data"
	@echo "  swarm-fetch-join         -- copy worker swarm token from data to $(CACHE_DIR)/swarm-token"
	@echo "  deploy-step3-swarm-join  -- phase 3: join swarm on proc"
	@echo "  deploy-step4-stack       -- phase 4: stack deploy + post on data"
	@echo "  smoke                    -- curl health checks against forwarded ports"
	@echo "  status                   -- vagrant status + docker service ls on data"
	@echo "  halt                     -- stop both VMs"
	@echo "  destroy                  -- destroy both VMs (irreversible)"
	@echo "  clean-secrets            -- clear .secrets-generated marker on data"
	@echo "  clean-cache              -- remove local $(CACHE_DIR)/ (ssh_config, swarm token, …)"
	@echo
	@echo "Useful overrides:"
	@echo "  PYINFRA_YES=-y           -- skip pyinfra's 'Press enter to execute' prompt"
	@echo "  PYINFRA_FLAGS='-y -q'    -- combined flags (yes + quieten the changes table)"
	@echo "  Example:  PYINFRA_YES=-y make deploy"

init:
	git -C .. submodule update --init --recursive \
	    vagrant-demo/sourcedata/stack \
	    vagrant-demo/sourcedata/containers \
	    vagrant-demo/sourcedata/ci-pipelines \
	    vagrant-demo/sourcedata/bids-containers

up:
	$(VAGRANT) up data proc

halt:
	$(VAGRANT) halt

destroy:
	$(VAGRANT) destroy -f

# Discover SSH coordinates straight from Vagrant. This dodges the whole
# `~/.vagrant.d/insecure_private_key` (legacy, RSA-only) vs the modern
# `~/.vagrant.d/insecure_private_keys/vagrant.key.{rsa,ed25519}` layout
# vs `.vagrant/machines/<vm>/...` vs per-VM-key-with-insert_key=true
# mess across Vagrant versions.
# see https://github.com/hashicorp/vagrant/blob/b40f6e5fdae1113518e9c92f96dfcd364b646ff9/keys/README.md
# (note: prior to vagrant 2.3.8 only the RSA key was honoured)
# and https://developer.hashicorp.com/vagrant/docs/vagrantfile/ssh_settings#config-ssh-insert_key
$(SSH_CONFIG):
	mkdir -p $(CACHE_DIR)
	$(VAGRANT) ssh-config $(DATA_NAME) $(PROC_NAME) > $@.tmp
	mv $@.tmp $@
	@echo "wrote $@"

ssh-config: $(SSH_CONFIG)

deploy: deploy-step1-prereqs deploy-step2-swarm-init swarm-fetch-join \
        deploy-step3-swarm-join deploy-step4-stack

deploy-step1-prereqs: $(SSH_CONFIG)
	$(PYINFRA) $(PYINFRA_FLAGS) --sudo $(INVENTORY) deploy_prereqs.py

deploy-step2-swarm-init: $(SSH_CONFIG)
	$(PYINFRA) $(PYINFRA_FLAGS) --sudo --limit $(DATA_NAME) $(INVENTORY) deploy_swarm_init.py

swarm-fetch-join:
	mkdir -p $(CACHE_DIR)
	# Strip CR — `vagrant ssh -c` may allocate a pty that translates LF→CRLF,
	# leaving a stray \r on the token line. `docker swarm join --token
	# SWMTKN-…\r` then fails with "invalid join token".
	$(VAGRANT) ssh $(DATA_NAME) -c "sudo cat /etc/bidsflux/swarm-token" | tr -d '\r' > $(CACHE_DIR)/swarm-token
	chmod 0644 $(CACHE_DIR)/swarm-token
	@case "$$(cat $(CACHE_DIR)/swarm-token)" in \
	    SWMTKN-*) echo "fetched swarm token (SWMTKN-…)";; \
	    *) echo "ERROR: fetched content is not a swarm token" >&2; exit 1;; \
	 esac

deploy-step3-swarm-join: $(SSH_CONFIG)
	$(PYINFRA) $(PYINFRA_FLAGS) --sudo --limit $(PROC_NAME) $(INVENTORY) deploy_swarm_join.py

deploy-step4-stack: $(SSH_CONFIG)
	$(PYINFRA) $(PYINFRA_FLAGS) --sudo --limit $(DATA_NAME) $(INVENTORY) deploy_stack.py

smoke:
	@echo ">>> GitLab health"
	-curl -sk --max-time 10 https://127.0.0.1:8443/-/health || true
	@echo
	@echo ">>> MinIO health"
	-curl -s  --max-time 10 http://127.0.0.1:9000/minio/health/ready || true
	@echo
	@echo ">>> docker service ls"
	-$(VAGRANT) ssh $(DATA_NAME) -c "sudo docker service ls"

status:
	$(VAGRANT) status
	@echo
	-$(VAGRANT) ssh $(DATA_NAME) -c "sudo docker service ls"

clean-secrets:
	$(VAGRANT) ssh $(DATA_NAME) -c "sudo rm -f /opt/bidsflux/stack/.secrets-generated"

clean-cache:
	rm -rf $(CACHE_DIR)
