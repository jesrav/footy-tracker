build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

tag_and_push_hub:
	docker tag footy-tracker_api:latest jesrav/footy-tracker-api:latest
	docker tag footy-tracker_web:latest jesrav/footy-tracker_web:latest
	docker tag footy-tracker_ml_api:latest jesrav/footy-tracker_ml_api:latest
	docker push jesrav/footy-tracker-api:latest
	docker push jesrav/footy-tracker_web:latest
	docker push jesrav/footy-tracker_ml_api:latest
