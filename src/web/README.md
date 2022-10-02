# FootyTracker frontend

# Get started
Right now the development setup uses an Azure blob storage account for storing profile images, 
so you will need to first set that up to see and store user images. (You can run the web app without)

Install the python dependencies in your preferred virtual Python env
```bash
pip install -r requirements.txt
```

Copy and fill out the template for environment variable. 
The variables need to match the Azure storge account and blob container you created.
```bash
cp .env_example .env
```

Start the other required services (API and ML API)
```bash
docker-compose up
```
This will start 3 containers that runs
- the backend API (exposed at http://0.0.0.0:8001)
- a Postgres DB that the API uses
- an ML microservice used by the API (exposed at http://0.0.0.0:8002)

To stop the app, stop the containers. To kill the containers (You will lose the data), run
```bash
docker-compose down
```
