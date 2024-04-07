DOCKER_COMPOSE_EXECUTABLE=$$(which docker-compose >/dev/null 2>&1 && echo 'docker-compose' || echo 'docker compose')
PROD_COMPOSE_ARGS=-f docker-compose.yml -f docker-compose.prod.yml
DEV_COMPOSE_ARGS=-f docker-compose.yml -f docker-compose.dev.yml

help: ## This help
	@grep -F "##" $(MAKEFILE_LIST) | grep -vF '@grep -F "##" $$(MAKEFILE_LIST)' | sed -r 's/(:).*##/\1/' | sort

list: ## List all targets
	@make -qp | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}'

build: ## Build prod-like container
	docker build --tag=kyokley/bs_int .

up: ## Bring up containers and daemonize
	${DOCKER_COMPOSE_EXECUTABLE} ${DEV_COMPOSE_ARGS} up -d
	${DOCKER_COMPOSE_EXECUTABLE} ${DEV_COMPOSE_ARGS} logs -f bs_int

down:
	${DOCKER_COMPOSE_EXECUTABLE} ${DEV_COMPOSE_ARGS} down --remove-orphans

clear-db:
	${DOCKER_COMPOSE_EXECUTABLE} ${DEV_COMPOSE_ARGS} down -v

fresh: clear-db migrate up

shell:
	${DOCKER_COMPOSE_EXECUTABLE} ${DEV_COMPOSE_ARGS} run bs_int /bin/bash

migrate:
	${DOCKER_COMPOSE_EXECUTABLE} up -d
	${DOCKER_COMPOSE_EXECUTABLE} exec bs_int python manage.py migrate
	${DOCKER_COMPOSE_EXECUTABLE} exec bs_int python manage.py initdata

attach:
	docker attach $$(docker ps -qf name=bs_int-bs_int)

prod-up: migrate
	${DOCKER_COMPOSE_EXECUTABLE} ${PROD_COMPOSE_ARGS} up -d
	${DOCKER_COMPOSE_EXECUTABLE} ${PROD_COMPOSE_ARGS} logs -f

prod-restart: down prod-up

pytest:
	${DOCKER_COMPOSE_EXECUTABLE} ${DEV_COMPOSE_ARGS} run --rm bs_int pytest

tests: pytest
