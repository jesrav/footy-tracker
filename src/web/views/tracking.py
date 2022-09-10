import fastapi
from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from models.result import ResultSubmissionCreate
from models.team import TeamCreate
from services import tracking_service
from viewmodels.tracking.approve_results_viewmodel import ApproveResultsViewModel
from viewmodels.tracking.submit_result_viewmodel import SubmitResultViewModel
from viewmodels.tracking.leaderboard_viewmodel import LeaderboardViewModel
from viewmodels.tracking.user_viewmodel import UserViewModel

router = fastapi.APIRouter()


@router.get('/user/{user_in_view_id}/')
@template()
async def user(user_in_view_id, request: Request):
    vm = UserViewModel(user_in_view_id, request, )
    await vm.load()
    return vm.to_dict()


@router.get('/leaderboard/')
@template()
async def leaderboard(request: Request):
    vm = LeaderboardViewModel(request)
    await vm.load()
    return vm.to_dict()


@router.get('/submit_result')
@template()
async def submit_result(request: Request):
    vm = SubmitResultViewModel(request)
    if not vm.is_logged_in:
        return fastapi.responses.RedirectResponse('/account/login', status_code=status.HTTP_302_FOUND)
    await vm.load()
    return vm.to_dict()


@router.post('/submit_result')
@template()
async def submit_result(request: Request):
    vm = SubmitResultViewModel(request)

    await vm.post_form()

    if vm.error:
        return vm.to_dict()

    return fastapi.responses.RedirectResponse(url='/results_for_approval', status_code=status.HTTP_302_FOUND)


@router.get('/results_for_approval')
@template()
async def get_results_for_approval(request: Request):
    vm = ApproveResultsViewModel(request)
    if not vm.is_logged_in:
        return fastapi.responses.RedirectResponse('/account/login', status_code=status.HTTP_302_FOUND)
    await vm.load()
    return vm.to_dict()


@router.post('/results_for_approval')
@template()
async def approve_result(request: Request):
    vm = ApproveResultsViewModel(request)

    await vm.load_form()

    if vm.error:
        return vm.to_dict()

    _ = await tracking_service.validate_result(
        result_id=vm.result_id,
        approved=vm.approved,
        bearer_token=vm.bearer_token
    )
    return fastapi.responses.RedirectResponse('/results_for_approval', status_code=status.HTTP_302_FOUND)
