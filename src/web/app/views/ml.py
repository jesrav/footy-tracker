import fastapi
from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from app.viewmodels.ml.add_ml_model_viewmodel import AddMLViewModel
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


@router.get('/ml/add_model')
@template()
async def add_ml_model(request: Request):
    vm = AddMLViewModel(request)
    await vm.authorize()
    if vm.redirect_response:
        return vm.redirect_response
    return await vm.to_dict()


@router.post('/ml/add_model')
@template()
async def add_ml_model(request: Request):
    vm = AddMLViewModel(request)
    await vm.post_form()
    if vm.error:
        return await vm.to_dict()
    response = fastapi.responses.RedirectResponse(url='/ml', status_code=status.HTTP_302_FOUND)
    return response
