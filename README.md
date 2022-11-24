# FootyTracker
A table soccer tracking web app. Find a deployed version here

- web app: [https://www.footy-tracker.live](https://www.footy-tracker.live) 
- Min api: [https://api.footy-tracker.live](https://api.footy-tracker.live/docs).
- ML prediction microservice: [https://ml.footy-tracker.live](https://ml.footy-tracker.live/docs).

# Get started
Right now the development setup uses an Azure blob storage account for storing profile images, 
so you will need to set that up to see and store user images.

Copy and fill out the template for environment variable.
```bash
cp .env_example .env
```

To run the app locally in Docker
```bash
docker-compose up
```
This will start 4 containers that runs
- the backend API (exposed at http://0.0.0.0:8001)
- a Postgres DB that the API uses
- an ML microservice used by the API (exposed at http://0.0.0.0:8002)
- the web server for the frontend (exposed at http://0.0.0.0:8000)

To stop the app, stop the containers. To kill the containers (You will lose the data), run
```bash
docker-compose down
```

# Development
To develop and debug the individual components (web / api / ml_api), open subprojects individually.
