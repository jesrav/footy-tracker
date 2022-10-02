# API for FootyTracker

# Get started

Install the python dependencies in your prefered virtual Python env
```bash
pip install -r requirements.txt
```

Copy the template for environment variable.
```bash
cp .env_example .env
```

Start the other required services (API and ML API)
```bash
docker-compose up
```
This will start 2 containers that runs
- a Postgres DB that the API uses
- an ML microservice used by the API (exposed at http://0.0.0.0:8002)

To stop the services, stop the containers. To kill the containers (You will lose the data), run
```bash
docker-compose down
```

Now start the api
```bash
    uvicorn main:app --reload
```