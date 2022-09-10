from dataclasses import dataclass
from typing import Optional, List, Dict

from starlette.requests import Request

from models.rankings import UserRanking
from models.ratings import UserRating
from models.user import UserRead
from services import user_service, tracking_service
from viewmodels.shared.viewmodel import ViewModelBase


@dataclass
class UserLeaderboardOverview:
    user_id: int
    user: UserRead
    rating_defence: float
    rating_offence: float
    overall_rating: float
    defensive_ranking: int
    offensive_ranking: int
    overall_ranking: int


class LeaderboardViewModel(ViewModelBase):
    def __init__(self, request: Request):
        super().__init__(request)
        self.user_infos_overall: List[UserLeaderboardOverview] = []
        self.user_infos_defence: List[UserLeaderboardOverview] = []
        self.user_infos_offence: List[UserLeaderboardOverview] = []

    async def load(self):
        latest_user_ratings = await tracking_service.get_latest_user_ratings()
        latest_user_ratings_dict = {r.user.id: r for r in latest_user_ratings}
        user_rankings = await tracking_service.get_user_rankings()
        user_rankings_dict = {r.user_id: r for r in user_rankings}
        for user_id, user_rating in latest_user_ratings_dict.items():
            self.user_infos_overall.append(UserLeaderboardOverview(
                user_id=user_id,
                user=user_rating.user,
                rating_defence=user_rating.rating_defence,
                rating_offence=user_rating.rating_offence,
                overall_rating=user_rating.overall_rating,
                defensive_ranking=user_rankings_dict[user_id].defensive_ranking,
                offensive_ranking=user_rankings_dict[user_id].offensive_ranking,
                overall_ranking=user_rankings_dict[user_id].overall_ranking,
            ))
        self.user_infos_overall = sorted(self.user_infos_overall, key=lambda x: x.overall_ranking)
        self.user_infos_defence = sorted(self.user_infos_overall, key=lambda x: x.defensive_ranking)
        self.user_infos_offence = sorted(self.user_infos_overall, key=lambda x: x.offensive_ranking)
