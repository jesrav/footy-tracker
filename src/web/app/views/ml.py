import fastapi
from fastapi_chameleon import template
from starlette.requests import Request

from app.viewmodels.ml.ml_viewmodel import MLViewModel

router = fastapi.APIRouter()


@router.get('/ml')
@template()
async def ml(request: Request):
    vm = MLViewModel(request)
    await vm.authorize()
    if vm.redirect_response:
        return vm.redirect_response
    await vm.load()
    return await vm.to_dict()
