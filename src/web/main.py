import fastapi
import fastapi_chameleon
from starlette.staticfiles import StaticFiles

from views import home, account, tracking
from config import settings

app = fastapi.FastAPI()


def configure_templates(dev_mode: bool):
    fastapi_chameleon.global_init('templates', auto_reload=dev_mode)


def configure_routes():
    app.mount('/static', StaticFiles(directory='static'), name='static')
    app.include_router(home.router)
    app.include_router(account.router)
    app.include_router(tracking.router)


configure_templates(dev_mode=settings.DEV_MODE)
configure_routes()
