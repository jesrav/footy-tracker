include .env
export


run_dev_db:
	docker run \
	-p 5455:5455 \
	-e POSTGRES_PASSWORD=postgres \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_DB=footy \
	-d \
	postgres:13.4


run:
	uvicorn main:app --reload


seed_dev_db:
	python seed.py


