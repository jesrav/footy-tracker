import httpx
from httpx import Response

from app.models.team import UsersForTeamsSuggestion, TeamsSuggestion
from app.models.validation_error import ValidationError
from app.config import settings


async def get_teams_suggestion(
        users: UsersForTeamsSuggestion ,bearer_token: str
) -> TeamsSuggestion:
    timeout = httpx.Timeout(20)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp: Response = await client.post(
            url=settings.BASE_WEB_API_URL + "/ml/suggest_teams/",
            json=users.dict(),
            headers={"Authorization": f"Bearer {bearer_token}"},
        )
        if resp.status_code != 200:
            raise ValidationError(resp.text, status_code=resp.status_code)
    return TeamsSuggestion(**resp.json())
