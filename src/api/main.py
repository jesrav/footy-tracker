from fastapi import FastAPI
from sqlmodel import SQLModel

from database import engine, create_db_and_tables
from routes import user, result, rating

SQLModel.metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def configure_routing():
    app.include_router(user.router)
    app.include_router(result.router)
    app.include_router(rating.router)


configure_routing()