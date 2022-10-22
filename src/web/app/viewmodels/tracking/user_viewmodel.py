from typing import Optional, List

from starlette.requests import Request

from app.models.rankings import UserRanking
from app.models.ratings import UserRating
from app.models.user import UserRead
from app.models.result import ResultSubmissionRead, ResultForUserDisplay
from app.models.user_stats import UserStats
from app.services import user_service, tracking_service
from app.viewmodels.shared.viewmodel import ViewModelBase


class HistoricalUserRatings:

    TREND_DELTA: float = 5.0  # Delta that must be present before we classify something as a trend

    def __init__(self, user_ratings: List[UserRating], trend_window_size: int):
        self.ratings = sorted(user_ratings, key= lambda x: x.created_dt)
        self.trend_window_size = min(trend_window_size, len(self.ratings) - 1)

        self.user_ranking_overall_trending_up = (
                self.ratings[-1].overall_rating > self.ratings[-(self.trend_window_size + 1)].overall_rating + self.TREND_DELTA
        )
        self.user_ranking_overall_trending_down = (
                self.ratings[-1].overall_rating + self.TREND_DELTA < self.ratings[-(self.trend_window_size + 1)].overall_rating
        )
        self.user_ranking_overall_trending_up = (
                self.ratings[-1].overall_rating > self.ratings[-(self.trend_window_size + 1)].overall_rating + self.TREND_DELTA
        )
        self.user_ranking_defence_trending_down = (
                self.ratings[-1].rating_defence + self.TREND_DELTA < self.ratings[-(self.trend_window_size + 1)].rating_defence
        )
        self.user_ranking_defence_trending_up = (
                self.ratings[-1].rating_defence > self.ratings[-(self.trend_window_size + 1)].rating_defence + self.TREND_DELTA
        )
        self.user_ranking_offence_trending_down = (
                self.ratings[-1].rating_offence + self.TREND_DELTA < self.ratings[-(self.trend_window_size + 1)].rating_offence
        )
        self.user_ranking_offence_trending_up = (
                self.ratings[-1].rating_offence > self.ratings[-(self.trend_window_size + 1)].rating_offence + self.TREND_DELTA
        )


class UserViewModel(ViewModelBase):
    def __init__(self, user_in_view_id, request: Request):
        super().__init__(request)
        self.user: Optional[UserRead] = None
        self.user_in_view_id: int = int(user_in_view_id)
        self.historical_user_ratings: Optional[HistoricalUserRatings] = None
        self.latest_results = List[ResultSubmissionRead]
        self.latest_user_rating: Optional[UserRating] = None
        self.user_ranking: Optional[UserRanking] = None
        self.user_stats: Optional[UserStats] = None

    async def load(self):
        self.user = await user_service.get_user_by_id(user_id=self.user_in_view_id)

        _latest_results_api_format = await tracking_service.get_approved_results(user_id=self.user_in_view_id)
        self.latest_results = [
            ResultForUserDisplay.from_result_submission(
                user_id=int(self.user_in_view_id),
                result=r,
            ) for r in _latest_results_api_format
        ]

        user_in_viev_ratings = await tracking_service.get_user_ratings(user_id=self.user_in_view_id)
        self.historical_user_ratings = HistoricalUserRatings(
            user_ratings=user_in_viev_ratings,
            trend_window_size=5
        )
        self.latest_user_rating = await tracking_service.get_latest_user_rating(user_id=self.user_in_view_id)
        user_rankings = await tracking_service.get_user_rankings()
        self.user_ranking = [user_ranking for user_ranking in user_rankings if user_ranking.user_id == self.user_in_view_id][0]
        user_stats_list = await tracking_service.get_user_stats()
        self.user_stats = [user_stats for user_stats in user_stats_list if user_stats.user_id == self.user_in_view_id]
        if not self.user_stats:
            self.user_stats = None
        else:
            self.user_stats = self.user_stats[0]
