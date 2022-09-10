import fastapi
from fastapi_chameleon import template
from starlette.requests import Request

from viewmodels.shared.viewmodel import ViewModelBase

router = fastapi.APIRouter()


@router.get('/')
@template()
async def index(request: Request):
    vm = ViewModelBase(request)
    return await vm.to_dict()


@router.get('/about')
@template()
async def about(request: Request):
    vm = ViewModelBase(request)
    return await vm.to_dict()
