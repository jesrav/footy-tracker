import fastapi
from fastapi_chameleon import template

router = fastapi.APIRouter()


@router.get('/')
@template()
def index():
    return {}


@router.get('/bulma')
@template()
def bulma():
    return {}


@router.get('/about')
@template()
def about():
    return {}


@router.get('/get_started')
@template()
def get_started():
    return {}

