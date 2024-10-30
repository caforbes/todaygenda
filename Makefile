default: typecheck format lint
prerelease: default build coverage
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
	@dbmate --no-dump-schema -e TEST_DATABASE_URL up
testmigrate: testmigrate-initial pytest
testmigrate-initial:
	@dbmate --no-dump-schema -e TEST_DATABASE_URL migrate
	@dbmate --no-dump-schema -e TEST_DATABASE_URL rollback
	@echo "Test migration was successfully applied and rolled back."
	@dbmate --no-dump-schema -e TEST_DATABASE_URL up
	@echo "Test migration was applied."
testmigrate-rollback:
	@dbmate --no-dump-schema -e TEST_DATABASE_URL rollback
migrate-initial: backupdb
	@dbmate --no-dump-schema migrate
	@dbmate --no-dump-schema rollback
	@echo "Migration was successfully applied and rolled back."
	@echo "Note: Migration was not permanently applied."
migrate: migrate-initial
	@dbmate migrate
	@echo "Migration applied."
backupdb:
	pg_dump ${DATABASE_URL} > backup.sql
backupdb-prod:
	heroku pg:backups:capture
	@sleep 10
	heroku pg:backups:download
	@mv latest.dump "backup-"$(date "+%Y%m%d-%H%M%S")".dump"
	@echo "Backup saved with timestamp"
release: backupdb-prod
	git push heroku main
	heroku run bin/dbmate --no-dump-schema up