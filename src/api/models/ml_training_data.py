from typing import List

from sqlmodel import SQLModel


class MLTrainingData(SQLModel):
    result_id: List[int]
    team1_id: List[int]
    team2_id: List[int]
    goals_team1: List[int]
    goals_team2: List[int]
    team1_defender_user_id: List[int]
    team1_attacker_user_id: List[int]
    team2_defender_user_id: List[int]
    team2_attacker_user_id: List[int]
    team1_defender_overall_rating_before_game: List[float]
    team1_defender_defensive_rating_before_game: List[float]
    team1_defender_offensive_rating_before_game: List[int]
    team1_attacker_overall_rating_before_game: List[float]
    team1_attacker_defensive_rating_before_game: List[float]
    team1_attacker_offensive_rating_before_game: List[float]
    team2_defender_overall_rating_before_game: List[float]
    team2_defender_defensive_rating_before_game: List[float]
    team2_defender_offensive_rating_before_game: List[float]
    team2_attacker_overall_rating_before_game: List[float]
    team2_attacker_defensive_rating_before_game: List[float]
    team2_attacker_offensive_rating_before_game: List[float]