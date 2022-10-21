import pytest

from api.models.ml import DataForMLInternal, RowForMLInternal


@pytest.fixture(scope="session")
def historical_ml_data():
    return DataForMLInternal(
        data=[
            RowForMLInternal(
                result_to_predict=False,
                result_id=1,
                result_dt="2022-01-01 12:00",
                result_approved=True,
                goals_team1=2,
                goals_team2=10,
                team1_defender_user_id=1,
                team1_attacker_user_id=2,
                team2_defender_user_id=3,
                team2_attacker_user_id=4,
                team1_defender_defensive_rating_before_game=1500,
                team1_defender_offensive_rating_before_game=1500,
                team1_defender_overall_rating_before_game=1500,
                team1_attacker_defensive_rating_before_game=1500,
                team1_attacker_offensive_rating_before_game=1500,
                team1_attacker_overall_rating_before_game=1500,
                team2_defender_defensive_rating_before_game=1500,
                team2_defender_offensive_rating_before_game=1500,
                team2_defender_overall_rating_before_game=1500,
                team2_attacker_defensive_rating_before_game=1500,
                team2_attacker_offensive_rating_before_game=1500,
                team2_attacker_overall_rating_before_game=1500,
                goal_diff=-8,
                teams_switched=True,
            ),
            RowForMLInternal(
                result_to_predict=False,
                result_id=2,
                result_dt="2022-01-01 13:00",
                result_approved=True,
                goals_team1=2,
                goals_team2=8,
                team1_defender_user_id=1,
                team1_attacker_user_id=2,
                team2_defender_user_id=3,
                team2_attacker_user_id=4,
                team1_defender_defensive_rating_before_game=1400,
                team1_defender_offensive_rating_before_game=1500,
                team1_defender_overall_rating_before_game=1450,
                team1_attacker_defensive_rating_before_game=1500,
                team1_attacker_offensive_rating_before_game=1400,
                team1_attacker_overall_rating_before_game=1450,
                team2_defender_defensive_rating_before_game=1600,
                team2_defender_offensive_rating_before_game=1500,
                team2_defender_overall_rating_before_game=1550,
                team2_attacker_defensive_rating_before_game=1500,
                team2_attacker_offensive_rating_before_game=1600,
                team2_attacker_overall_rating_before_game=1550,
                goal_diff=-8,
                teams_switched=True,
            )
        ]
    )
