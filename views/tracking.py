import fastapi
from fastapi_chameleon import template
from starlette.requests import Request

from viewmodels.tracking.submit_result_viewmodel import SubmitResultViewModel
from viewmodels.tracking.leaderboard_viewmodel import LeaderboardViewModel

router = fastapi.APIRouter()


@router.get('/leaderboard')
@template()
def leaderboard(request: Request):
    vm = LeaderboardViewModel(request)
    return vm.to_dict()


@router.get('/submit_result')
@template()
def submit_result(request: Request):
    vm = SubmitResultViewModel(request)
    return vm.to_dict()
