from datetime import datetime
from typing import Union, List

from pydantic import BaseModel


class RowForML(BaseModel):
    result_to_predict: bool
    result_id: Union[int, None]
    result_dt: Union[datetime, None]
    team1_id: int
    team2_id: int
    goals_team1: Union[int, None]
    goals_team2: Union[int, None]
    team1_defender_user_id: int
    team1_attacker_user_id: int
    team2_defender_user_id: int
    team2_attacker_user_id: int
    team1_defender_overall_rating_before_game: float
    team1_defender_defensive_rating_before_game: float
    team1_defender_offensive_rating_before_game: float
    team1_attacker_overall_rating_before_game: float
    team1_attacker_defensive_rating_before_game: float
    team1_attacker_offensive_rating_before_game: float
    team2_defender_overall_rating_before_game: float
    team2_defender_defensive_rating_before_game: float
    team2_defender_offensive_rating_before_game: float
    team2_attacker_overall_rating_before_game: float
    team2_attacker_defensive_rating_before_game: float
    team2_attacker_offensive_rating_before_game: float
    goal_diff: Union[int, None]


class DataForML(BaseModel):
    data: List[RowForML]
