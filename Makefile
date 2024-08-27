default: typecheck lint build pytest
typecheck:
	mypy src --strict
	mypy api cli
lint:
	flake8
pytest:
	@pytest
coverage:
	@coverage run -m pytest -q
	@coverage report -m --skip-empty
	@coverage html
build:
	pipenv requirements > requirements.txt