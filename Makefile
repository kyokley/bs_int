help: ## This help
	@grep -F "##" $(MAKEFILE_LIST) | grep -vF '@grep -F "##" $$(MAKEFILE_LIST)' | sed -r 's/(:).*##/\1/' | sort

list: ## List all targets
	@make -qp | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}'

build: ## Build prod-like container
	docker build --tag=kyokley/bs_int .

up: ## Bring up containers and daemonize
	docker compose up -d

shell:
	docker compose run bs_int /bin/bash
