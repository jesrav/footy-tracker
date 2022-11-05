import fastapi
import fastapi_chameleon
from starlette.staticfiles import StaticFiles

from app.views import home, account, tracking, ml
from app.config import settings

app = fastapi.FastAPI()


def configure_templates(dev_mode: bool):
    fastapi_chameleon.global_init('app/templates', auto_reload=dev_mode)


def configure_routes():
    app.mount('/static', StaticFiles(directory='app/static'), name='static')
    app.include_router(home.router)
    app.include_router(account.router)
    app.include_router(tracking.router)
    app.include_router(ml.router)


configure_templates(dev_mode=settings.DEV_MODE)
configure_routes()
