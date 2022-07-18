import fastapi
from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from src.web.services import tracking_service
from src.web.viewmodels.tracking.submit_result_viewmodel import SubmitResultViewModel
from src.web.viewmodels.tracking.leaderboard_viewmodel import LeaderboardViewModel

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


@router.post('/submit_result')
@template()
async def submit_result(request: Request):
    vm = SubmitResultViewModel(request)

    await vm.load()

    if vm.error:
        return vm.to_dict()

    # Create match registration
    match = tracking_service.register_match(
        team1_defender=vm.team1_defender,
        team1_attacker=vm.team1_attacker,
        team2_defender=vm.team2_defender,
        team2_attacker=vm.team2_attacker,
        goals_team1=vm.goals_team1,
        goals_team2=vm.goals_team2,
    )

    # redirect (should be to some overview)
    response = fastapi.responses.RedirectResponse(url='/account', status_code=status.HTTP_302_FOUND)
    return response
