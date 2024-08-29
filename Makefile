default: typecheck format lint pytest
testall: typecheck format lint build coverage
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
testmigrate:
	@dbmate -e TEST_DATABASE_URL migrate
	@dbmate -e TEST_DATABASE_URL rollback
	@echo "Migration was successfully rolled back and re-migrated!"
	@echo "Make sure to APPLY the migration next."
testmigrate-local: backupdb
	@dbmate migrate
	@dbmate rollback
	@echo "Migration was successfully rolled back and re-migrated!"
	@echo "Make sure to APPLY the migration next."
backupdb:
	pg_dump ${DATABASE_URL} > backup.sql