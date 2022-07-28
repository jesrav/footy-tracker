import fastapi
from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from models.result import ResultSubmissionCreate
from models.team import TeamCreate
from services import tracking_service
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
async def submit_result(request: Request):
    vm = SubmitResultViewModel(request)
    await vm.load()
    return vm.to_dict()


@router.post('/submit_result')
@template()
async def submit_result(request: Request):
    vm = SubmitResultViewModel(request)

    await vm.load_form()

    if vm.error:
        return vm.to_dict()

    match = ResultSubmissionCreate(
        submitter_id=vm.user_id,
        team1=TeamCreate(
            defender_user_id=vm.team1_defender,
            attacker_user_id=vm.team1_attacker,
        ),
        team2=TeamCreate(
            defender_user_id=vm.team2_defender,
            attacker_user_id=vm.team2_attacker,
        ),
        goals_team1=vm.goals_team1,
        goals_team2=vm.goals_team2,
    )

    # Create match registration
    _ = await tracking_service.register_result(match)

    response = fastapi.responses.RedirectResponse(url='/account', status_code=status.HTTP_302_FOUND)
    return response
