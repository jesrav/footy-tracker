# FootyTracker
A table soccer tracking web app.

A work in progress.

# Get started
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
