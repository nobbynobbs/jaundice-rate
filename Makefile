.PHONY: tests

install:
	poetry install --no-dev

install-dev:
	poetry install

tests:
	poetry run pytest tests -v


lint:
	poetry run flake8 --exclude .venv

mypy:
	poetry run mypy -p filter