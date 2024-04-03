help: ## This help
	@grep -F "##" $(MAKEFILE_LIST) | grep -vF '@grep -F "##" $$(MAKEFILE_LIST)' | sed -r 's/(:).*##/\1/' | sort

list: ## List all targets
	@make -qp | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}'

build: ## Build prod-like container
	docker build --tag=kyokley/bs_int .

up: ## Bring up containers and daemonize
	docker compose up -d
	docker compose logs -f bs_int

down:
	docker compose down

clear-db:
	docker compose down -v

fresh: clear-db migrate up

shell:
	docker compose run bs_int /bin/bash

migrate:
	docker compose up -d
	docker compose exec bs_int python manage.py migrate
	docker compose exec bs_int python manage.py initdata

attach:
	docker attach $$(docker ps -qf name=bs_int-bs_int)
