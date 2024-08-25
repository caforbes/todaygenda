lint:
	mypy src --strict
	mypy api cli
	flake8
tests:
	@pytest
coverage:
	@coverage run -m pytest -q
	@coverage report -m --skip-empty
	@coverage html