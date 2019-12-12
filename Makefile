.PHONY: tests

run:
	docker-compose -f deployment/docker-compose.yaml up -d --build

stop:
	docker-compose -f deployment/docker-compose.yaml down

install:
	poetry install --no-dev

install-dev:
	poetry install

tests:
	poetry run pytest tests -v

tests-cov:
	poetry run pytest -v --cov=filter tests

tests-cov-report:
	poetry run pytest -v --cov=filter --cov-report=html tests

lint:
	poetry run flake8 --exclude .venv

mypy:
	poetry run mypy -p filter
