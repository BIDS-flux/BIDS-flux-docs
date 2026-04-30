.PHONY: help init up halt destroy deploy \
        deploy-step1-prereqs deploy-step2-swarm-init swarm-fetch-join \
        deploy-step3-swarm-join deploy-step4-stack \
        smoke status clean-secrets clean-cache

VAGRANT ?= vagrant
PYINFRA ?= pyinfra
INVENTORY ?= inventories/vagrant.py
CACHE_DIR := .cache

DATA_HOST := itappcpipdp01.uc.ucalgary.ca
PROC_HOST := itappcpippp01.uc.ucalgary.ca

help:
	@echo "Targets:"
	@echo "  init                     -- git submodule update --init for sourcedata/*"
	@echo "  up                       -- vagrant up data + proc"
	@echo "  deploy                   -- chain steps 1..4 (full deploy)"
	@echo "  deploy-step1-prereqs     -- phase 1: prereqs on both hosts"
	@echo "  deploy-step2-swarm-init  -- phase 2: swarm init on data"
	@echo "  swarm-fetch-join         -- copy join command from data to .cache/"
	@echo "  deploy-step3-swarm-join  -- phase 3: join swarm on proc"
	@echo "  deploy-step4-stack       -- phase 4: stack deploy + post on data"
	@echo "  smoke                    -- curl health checks against forwarded ports"
	@echo "  status                   -- vagrant status + docker service ls on data"
	@echo "  halt                     -- stop both VMs"
	@echo "  destroy                  -- destroy both VMs (irreversible)"
	@echo "  clean-secrets            -- clear .secrets-generated marker on data"
	@echo "  clean-cache              -- remove local .cache/ (join token etc.)"

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

deploy: deploy-step1-prereqs deploy-step2-swarm-init swarm-fetch-join \
        deploy-step3-swarm-join deploy-step4-stack

deploy-step1-prereqs:
	$(PYINFRA) --sudo $(INVENTORY) deploy_prereqs.py

deploy-step2-swarm-init:
	$(PYINFRA) --sudo --limit $(DATA_HOST) $(INVENTORY) deploy_swarm_init.py

swarm-fetch-join:
	mkdir -p $(CACHE_DIR)
	$(VAGRANT) ssh data -c "sudo cat /etc/bidsflux/swarm-join.sh" > $(CACHE_DIR)/swarm-join.sh
	chmod 0644 $(CACHE_DIR)/swarm-join.sh
	@echo "fetched $$(wc -l < $(CACHE_DIR)/swarm-join.sh) line join command"

deploy-step3-swarm-join:
	$(PYINFRA) --sudo --limit $(PROC_HOST) $(INVENTORY) deploy_swarm_join.py

deploy-step4-stack:
	$(PYINFRA) --sudo --limit $(DATA_HOST) $(INVENTORY) deploy_stack.py

smoke:
	@echo ">>> GitLab health"
	-curl -sk --max-time 10 https://127.0.0.1:8443/-/health || true
	@echo
	@echo ">>> MinIO health"
	-curl -s  --max-time 10 http://127.0.0.1:9000/minio/health/ready || true
	@echo
	@echo ">>> docker service ls"
	-$(VAGRANT) ssh data -c "sudo docker service ls"

status:
	$(VAGRANT) status
	@echo
	-$(VAGRANT) ssh data -c "sudo docker service ls"

clean-secrets:
	$(VAGRANT) ssh data -c "sudo rm -f /opt/bidsflux/stack/.secrets-generated"

clean-cache:
	rm -rf $(CACHE_DIR)
