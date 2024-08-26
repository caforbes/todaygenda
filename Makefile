default: typecheck lint build tests
typecheck:
	mypy src --strict
	mypy api cli
lint:
	flake8
tests:
	@pytest
coverage:
	@coverage run -m pytest -q
	@coverage report -m --skip-empty
	@coverage html
build:
	pipenv requirements > requirements.txt