from fastapi import FastAPI

from api.database import create_db_and_tables
from api.routes import user, result, rating, ranking, user_stats, auth, ml

app = FastAPI(title="FootyTracker API")


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


def configure_routing():
    app.include_router(auth.router)
    app.include_router(user.router)
    app.include_router(result.router)
    app.include_router(rating.router)
    app.include_router(ranking.router)
    app.include_router(user_stats.router)
    app.include_router(ml.router)


configure_routing()
