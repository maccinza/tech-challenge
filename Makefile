include .env.app
include .env.db
export
export DB_CONTAINER := pagamentos
export PG_DATA_PATH := /var/lib/postgresql/data
export WAIT_FOR_DB := 15

precommit: precommit_install
	. .venv/bin/activate; \
	pre-commit run -a

lint: precommit

.venv/:
	python3 -m venv .venv

precommit_install: .venv/
	. .venv/bin/activate; \
	pre-commit install

install_requirements: .venv/
	. .venv/bin/activate; \
	pip install --upgrade pip && \
	pip install -r requirements.txt

apply_migrations:
	. .venv/bin/activate; \
	DB_HOST=localhost && export DB_HOST && \
	python manage.py migrate

stop_database_docker:
	docker rm -f $(DB_CONTAINER) || true

start_database_docker: stop_database_docker
	docker pull postgres; \
	docker run --rm --name pagamentos -v ~/postgres_data:$(PG_DATA_PATH) -p $(DB_PORT):$(DB_PORT) -e PGDATA=$(PG_DATA_PATH)/pgdata -e POSTGRES_PASSWORD=$(POSTGRES_PASSWORD) -e POSTGRES_DB=$(POSTGRES_DB) -e POSTGRES_USER=$(POSTGRES_USER) -d postgres; \
	echo "Waiting 15 sec for the database to be ready..."; \
	sleep $(WAIT_FOR_DB)

import_companies: apply_migrations
	DB_HOST=localhost && export DB_HOST; \
	. .venv/bin/activate; \
	python manage.py import_companies --filepath data/companies.json

import_companies_dockerized:
	docker-compose run backend python manage.py import_companies --filepath data/companies.json

test:
	$(MAKE) start_database_docker && \
	$(MAKE) apply_migrations && \
	DB_HOST=localhost && export DB_HOST; \
	. .venv/bin/activate; \
	python manage.py test -v 2

test_dockerized:
	docker-compose run backend python manage.py test -v 2

start_app_local:
	$(MAKE) install_requirements && \
	$(MAKE) start_database_docker && \
	$(MAKE) import_companies && \
	DB_HOST=localhost && export DB_HOST; \
	. .venv/bin/activate; \
	python manage.py runserver

stop_app_local: stop_database_docker
	kill `ps aux | grep manage.py | awk '{print $$2}'`

run_dockerized_app:
	docker-compose up --build
