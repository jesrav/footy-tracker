include .env
export

run_dev_db:
	docker run \
	-p 5432:5432 \
	-e POSTGRES_PASSWORD=postgres \
	-e POSTGRES_USER=postgres \
	-e POSTGRES_DB=footy \
	-d \
	postgres:13.4

build:
	docker build -t footy-tracker_api .

tag_and_push:
	az acr login --name footycr
	docker tag footy-tracker_api:latest footycr.azurecr.io/footy-tracker_api:latest
	docker push footycr.azurecr.io/footy-tracker_api:latest

run:
	uvicorn main:app --reload

run_docker:
	docker run -p 80:80 --env-file=.env footy-tracker_api