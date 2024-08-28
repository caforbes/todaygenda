default: typecheck format lint pytest
testall: typecheck format lint build testrollback coverage
typecheck:
	@mypy src --strict
	@mypy api cli db
format:
	@black api cli db src test *.py
	@docformatter -r . --black
lint:
	@flake8
	@echo "Good lint!"
pytest: cleartestdb
	@pytest
coverage: cleartestdb
	@coverage run -m pytest -q
	@coverage report -m --skip-empty
	@coverage html
build:
	@pipenv clean
	@pipenv requirements > requirements.txt
	@echo "Checked requirements.txt!"
cleartestdb:
	@dbmate -e TEST_DATABASE_URL drop
	@dbmate -e TEST_DATABASE_URL up
testrollback:
	@dbmate -e TEST_DATABASE_URL rollback
	@dbmate -e TEST_DATABASE_URL migrate
	@echo "Migration was successfully rolled back and re-migrated!"
backupdb:
	pg_dump ${DATABASE_URL} > export.sql