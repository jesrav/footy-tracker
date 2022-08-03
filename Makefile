tag_and_push:
	az acr login --name footycr
	docker tag footy-tracker_web:latest footycr.azurecr.io/footy-tracker_web:latest	
	docker tag footy-tracker_api:latest footycr.azurecr.io/footy-tracker_api:latest	
	docker push footycr.azurecr.io/footy-tracker_api:latest
	docker push footycr.azurecr.io/footy-tracker_web:latest