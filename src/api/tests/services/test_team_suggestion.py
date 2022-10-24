import pytest

from api.models.ml import DataForML, RowForML
from api.models.rating import UserRating
from api.models.team import UsersForTeamsSuggestion
from api.services.team_suggestion import get_all_user_permutations, prepare_data_for_user_combination_prediction


def test_get_all_user_permutations():
    users = UsersForTeamsSuggestion(
        user_id_1=1,
        user_id_2=2,
        user_id_3=3,
        user_id_4=4,
    )
    all_user_combinations =  get_all_user_permutations(users)
    assert len(all_user_combinations) == 24, "There should be 24 possible combinations"

    # Test that all combinations are unique
    unique_user_combinations = []
    for user_combination in all_user_combinations:
        if user_combination not in unique_user_combinations:
            unique_user_combinations.append(user_combination)
    assert len(unique_user_combinations) == 24, "There should be 24 unique combinations"


@pytest.mark.asyncio
async def test_prepare_data_for_user_combination_prediction(historical_ml_data):
    # Prepare test data
    user_combination = UsersForTeamsSuggestion(
        user_id_1=1,
        user_id_2=2,
        user_id_3=3,
        user_id_4=4,
    )
    latest_ratings = [
        UserRating(
            user_id=1,
            rating_defence=1400,
            rating_offence=1500,
            overall_rating=1450,
            latest_result_at_update_id=2,
        ),
        UserRating(
            user_id=2,
            rating_defence=1500,
            rating_offence=1400,
            overall_rating=1450,
            latest_result_at_update_id=2,
        ),
        UserRating(
            user_id=3,
            rating_defence=1600,
            rating_offence=1500,
            overall_rating=1550,
            latest_result_at_update_id=2,
        ),
        UserRating(
            user_id=4,
            rating_defence=1500,
            rating_offence=1600,
            overall_rating=1550,
            latest_result_at_update_id=2,
        ),
    ]

    data_prepared_for_prediction = await prepare_data_for_user_combination_prediction(
        user_combination, latest_ratings, historical_ml_data
    )

    historical_ml_data_non_internal = DataForML(data=[RowForML(**r.dict()) for r in historical_ml_data.data])
    assert data_prepared_for_prediction.data[:-1] == historical_ml_data_non_internal.data, \
        "All rows except the last should match the historical data passed."

    new_row_for_prediction = data_prepared_for_prediction.data[-1]
    assert new_row_for_prediction.result_to_predict, "The new row should be for prediction"
    assert new_row_for_prediction.result_id is None, "The new row should not have a result_id"
    assert new_row_for_prediction.team1_defender_user_id == 1, "The new row should have the correct user ids"
    assert new_row_for_prediction.team1_attacker_user_id == 2, "The new row should have the correct user ids"
    assert new_row_for_prediction.team2_defender_user_id == 3, "The new row should have the correct user ids"
    assert new_row_for_prediction.team2_attacker_user_id == 4, "The new row should have the correct user ids"
    assert new_row_for_prediction.team1_defender_defensive_rating_before_game == 1400, "The new row should have the correct ratings"
    assert new_row_for_prediction.team1_defender_offensive_rating_before_game == 1500, "The new row should have the correct ratings"
    assert new_row_for_prediction.team1_defender_overall_rating_before_game == 1450, "The new row should have the correct ratings"
    assert new_row_for_prediction.team1_attacker_defensive_rating_before_game == 1500, "The new row should have the correct ratings"
    assert new_row_for_prediction.team1_attacker_offensive_rating_before_game == 1400, "The new row should have the correct ratings"
    assert new_row_for_prediction.team1_attacker_overall_rating_before_game == 1450, "The new row should have the correct ratings"
    assert new_row_for_prediction.team2_defender_defensive_rating_before_game == 1600, "The new row should have the correct ratings"
    assert new_row_for_prediction.team2_defender_offensive_rating_before_game == 1500, "The new row should have the correct ratings"
    assert new_row_for_prediction.team2_defender_overall_rating_before_game == 1550, "The new row should have the correct ratings"
    assert new_row_for_prediction.team2_attacker_defensive_rating_before_game == 1500, "The new row should have the correct ratings"
    assert new_row_for_prediction.team2_attacker_offensive_rating_before_game == 1600, "The new row should have the correct ratings"
    assert new_row_for_prediction.team2_attacker_overall_rating_before_game == 1550, "The new row should have the correct ratings"
