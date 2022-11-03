build:
	docker build -t jesrav/footy-tracker_ml_api .

run:
	uvicorn api.main:app --port 8002 --reload

run_docker:
	docker run -p 80:80 footy-tracker-ml

make train:
	python api/footy_ml/train.py
