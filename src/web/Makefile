include .env
export

build:
	docker build -t footy-tracker_web .

tag_and_push:
	az acr login --name footycr
	docker tag footy-tracker_web:latest footycr.azurecr.io/footy-tracker_web:latest
	docker push footycr.azurecr.io/footy-tracker_web:latest

run:
	python main.py
