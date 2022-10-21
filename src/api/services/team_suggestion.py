import asyncio
import itertools
from datetime import datetime
from functools import partial
from random import choice
from typing import List, Optional

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.deps import get_session
from crud.rating import get_latest_ratings
from models.ml import DataForMLInternal, RowForML, DataForML
from models.rating import UserRating

from models.team import UsersForTeamsSuggestion, TeamsSuggestion, TeamCreate
from services.ml import get_ml_prediction, get_ml_data


def get_all_user_permutations(users: UsersForTeamsSuggestion) -> List[UsersForTeamsSuggestion]:
    """Get all possible permutations of users for a team suggestion."""
    user_ids = [users.user_id_1, users.user_id_2, users.user_id_3, users.user_id_4]
    possible_user_combinations = list(itertools.permutations(user_ids))
    return [UsersForTeamsSuggestion(
        user_id_1=user_ids[0],
        user_id_2=user_ids[1],
        user_id_3=user_ids[2],
        user_id_4=user_ids[3],
    ) for user_ids in possible_user_combinations]


async def prepare_data_for_user_combination_prediction(
    user_combination: UsersForTeamsSuggestion,
    latest_ratings: List[UserRating],
    historical_ml_data: DataForMLInternal
) -> DataForML:
    """Prepare data for prediction for a user combination."""

    # Get the latest ratings for players
    user_ratings = {
        r.user_id: {
            "rating_defence": r.rating_defence, "rating_offence": r.rating_offence,
            "rating_overall": r.overall_rating
        }
        for r in latest_ratings if r.user_id in [
            user_combination.user_id_1,
            user_combination.user_id_2,
            user_combination.user_id_3,
            user_combination.user_id_4
        ]
    }

    combination_data_for_pred = RowForML(
        result_to_predict=True,
        result_dt=datetime.now(),
        team1_defender_user_id=user_combination.user_id_1,
        team1_attacker_user_id=user_combination.user_id_2,
        team2_defender_user_id=user_combination.user_id_3,
        team2_attacker_user_id=user_combination.user_id_4,
        team1_defender_overall_rating_before_game=user_ratings[user_combination.user_id_1]["rating_overall"],
        team1_defender_defensive_rating_before_game=user_ratings[user_combination.user_id_1]["rating_defence"],
        team1_defender_offensive_rating_before_game=user_ratings[user_combination.user_id_1]["rating_offence"],
        team1_attacker_overall_rating_before_game=user_ratings[user_combination.user_id_2]["rating_overall"],
        team1_attacker_defensive_rating_before_game=user_ratings[user_combination.user_id_2]["rating_defence"],
        team1_attacker_offensive_rating_before_game=user_ratings[user_combination.user_id_2]["rating_offence"],
        team2_defender_overall_rating_before_game=user_ratings[user_combination.user_id_3]["rating_overall"],
        team2_defender_defensive_rating_before_game=user_ratings[user_combination.user_id_3]["rating_defence"],
        team2_defender_offensive_rating_before_game=user_ratings[user_combination.user_id_3]["rating_offence"],
        team2_attacker_overall_rating_before_game=user_ratings[user_combination.user_id_4]["rating_overall"],
        team2_attacker_defensive_rating_before_game=user_ratings[user_combination.user_id_4]["rating_defence"],
        team2_attacker_offensive_rating_before_game=user_ratings[user_combination.user_id_4]["rating_offence"],
    )

    return DataForML(
        data=[RowForML(**row.dict()) for row in historical_ml_data.data] + [combination_data_for_pred]
    )


async def get_prediction_for_user_user_team_suggestion(
    user_combination: UsersForTeamsSuggestion,
    latest_ratings: List[UserRating],
    historical_ml_data: DataForMLInternal
) -> Optional[float]:
    data_for_prediction = await prepare_data_for_user_combination_prediction(
        user_combination=user_combination,
        latest_ratings=latest_ratings,
        historical_ml_data=historical_ml_data
    )
    return await get_ml_prediction(url=settings.ML_MODEL_URL, data_for_prediction=data_for_prediction)


async def suggest_most_fair_teams(
        users: UsersForTeamsSuggestion, session: AsyncSession = Depends(get_session)
) -> TeamsSuggestion:
    """Get most fair teams by minimizing the predicted goal difference

    We call a prediction API to get the goal difference for all team combinations.
    If multiple combinations have the minimum expected goal diff, we return a random one of these combinations.
    """
    # Get data for prediction for all previous results
    ml_data = await get_ml_data(
        session=session, n_rows=settings.N_HISTORICAL_ROWS_FOR_PREDICTION
    )

    # Create all combinations of users
    possible_user_combinations = get_all_user_permutations(users)

    latest_ratings = await get_latest_ratings(session=session)

    # For each user combination, we predict the goal difference, with an async call to the prediction API
    results = await asyncio.gather(
        *map(
            partial(get_prediction_for_user_user_team_suggestion, historical_ml_data=ml_data, latest_ratings=latest_ratings),
            possible_user_combinations,
        )
    )

    # Get user combinations with the lowest predicted goal difference
    min_goal_diffs = min([abs(r) for r in results])
    user_combinations_with_min_expected_goal_diff = [
        uc for i, uc in enumerate(possible_user_combinations) if results[i] == min_goal_diffs
    ]

    # Return a random user combination among the ones with the lowest expected goal difference
    suggested_user_comb = choice(user_combinations_with_min_expected_goal_diff)
    return TeamsSuggestion(
        team1=TeamCreate(
            defender_user_id=suggested_user_comb.user_id_1,
            attacker_user_id=suggested_user_comb.user_id_2,
        ),
        team2=TeamCreate(
            defender_user_id=suggested_user_comb.user_id_3,
            attacker_user_id=suggested_user_comb.user_id_4,
        ),
    )
