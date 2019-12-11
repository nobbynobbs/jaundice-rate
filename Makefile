.PHONY: tests

install:
	poetry install --no-dev

install-dev:
	poetry install

tests:
	poetry run pytest tests -v
