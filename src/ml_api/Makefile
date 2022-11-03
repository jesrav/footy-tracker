build:
	docker build -t footy-tracker-ml .

tag_and_push:
	az acr login --name footycr
	docker tag footy-tracker-ml:latest footycr.azurecr.io/footy-tracker-ml:latest
	docker push footycr.azurecr.io/footy-tracker-ml:latest

run:
	uvicorn api.main:app --port 8002 --reload

run_docker:
	docker run -p 80:80 footy-tracker-ml

make train:
	python api/footy_ml/train.py
