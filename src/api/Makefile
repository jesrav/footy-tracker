include .env
export

up_services:
	docker-compose up

stop_services:
	docker-compose stop

run:
	uvicorn api.main:app --reload

make run_tests:
	pytest tests
