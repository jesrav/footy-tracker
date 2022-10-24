import fastapi
from fastapi_chameleon import template
from starlette.requests import Request

from app.viewmodels.shared.viewmodel import ViewModelBase
from app.viewmodels.home.index_viewmodel import IndexViewModel

router = fastapi.APIRouter()


@router.get('/')
@template()
async def index(request: Request):
    vm = IndexViewModel(request)
    await vm.authorize()
    if vm.redirect_response:
        return vm.redirect_response
    await vm.load()
    return await vm.to_dict()


@router.get('/about')
@template()
async def about(request: Request):
    vm = ViewModelBase(request)
    return await vm.to_dict()
