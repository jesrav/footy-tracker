import fastapi
from fastapi_chameleon import template
from starlette.requests import Request
from starlette.responses import FileResponse

from viewmodels.shared.viewmodel import ViewModelBase

router = fastapi.APIRouter()


@router.get('/')
@template()
def index(request: Request):
    vm = ViewModelBase(request)
    return vm.to_dict()


@router.get('/about')
@template()
def about(request: Request):
    vm = ViewModelBase(request)
    return vm.to_dict()
