PYTHON ?= python3.12

.PHONY: install install-api install-web dev test lint format seed

install: install-api install-web

install-api:
	cd apps/api && $(PYTHON) -m pip install -e .[dev]

install-web:
	npm install

dev:
	npm run dev

test:
	npm run api:test

lint:
	npm run api:lint
	npm run web:lint

format:
	npm run api:format

seed:
	cd apps/api && $(PYTHON) -m app.db.seed

