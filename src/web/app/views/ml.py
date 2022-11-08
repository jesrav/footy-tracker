import fastapi
from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from app.viewmodels.ml.add_ml_model_viewmodel import AddMLViewModel
from app.viewmodels.ml.ml_model_viewmodel import MLModelViewModel
from app.viewmodels.ml.user_ml_overview_viewmodel import UserMLOverviewViewModel

router = fastapi.APIRouter()


@router.get('/ml')
@template()
async def user_ml_overview(request: Request):
    vm = UserMLOverviewViewModel(request)
    await vm.authorize()
    if vm.redirect_response:
        return vm.redirect_response
    await vm.load()
    return await vm.to_dict()


@router.get('/ml/model/{ml_model_id}')
@template()
async def ml_model(ml_model_id: int, request: Request):
    vm = MLModelViewModel(ml_model_id=ml_model_id, request=request)
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
    return vm.redirect_response or await vm.to_dict()


@router.post('/ml/add_model')
@template()
async def add_ml_model(request: Request):
    vm = AddMLViewModel(request)
    await vm.post_form()
    if vm.error:
        return await vm.to_dict()
    return fastapi.responses.RedirectResponse(
        url='/ml', status_code=status.HTTP_302_FOUND
    )
