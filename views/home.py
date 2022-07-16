import fastapi
from fastapi_chameleon import template
from starlette.requests import Request

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


@router.get('/leaderboard')
@template()
def leaderboard(request: Request):
    vm = ViewModelBase(request)
    return vm.to_dict()


@router.get('/submit_result')
@template()
def submit_result(request: Request):
    vm = ViewModelBase(request)
    return vm.to_dict()
