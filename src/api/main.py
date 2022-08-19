from fastapi import FastAPI

from database import create_db_and_tables
from routes import user, result, rating, ranking, user_stats

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def configure_routing():
    app.include_router(user.router)
    app.include_router(result.router)
    app.include_router(rating.router)
    app.include_router(ranking.router)
    app.include_router(user_stats.router)


configure_routing()