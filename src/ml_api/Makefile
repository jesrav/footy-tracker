build:
	docker build -t footy-tracker_api .

tag_and_push:
	az acr login --name footycr
	docker tag footy-tracker_api:latest footycr.azurecr.io/footy-tracker_api:latest
	docker push footycr.azurecr.io/footy-tracker_api:latest

run:
	uvicorn main:app --port 8002 --reload
