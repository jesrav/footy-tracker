build:
	docker build -t footy-tracker-ml .

tag_and_push:
	az acr login --name footycr
	docker tag footy-tracker_api:latest footycr.azurecr.io/footy-tracker-ml:latest
	docker push footycr.azurecr.io/footy-tracker-ml :latest

run:
	uvicorn main:app --port 8002 --reload
