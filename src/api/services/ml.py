import itertools
import json
from datetime import datetime
from typing import Union

from numpy import random
import httpx
import numpy as np
from fastapi import Depends
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
import pandas as pd

from core.deps import get_session
from crud.rating import get_latest_ratings
from models.ml import DataForML, DataForMLInternal, RowForMLInternal, RowForML
from core.config import settings
from models.team import UsersForTeamsSuggestion, TeamsSuggestion, TeamCreate


async def randomize_team_order(df: pd.DataFrame) -> pd.DataFrame:
    """Randomly swap team 1 and team 2 in dataframe with ml data.

    A boolean column teams_switched to indicate if team 1 and team 2 have been switched.
    """
    teams_switched = random.rand(len(df)) > 0.5
    df["teams_switched"] = teams_switched
    team1_cols = [col for col in df.columns if "team1" in col]
    team2_cols = [col for col in df.columns if "team2" in col]
    df.loc[teams_switched, team1_cols + team2_cols] = df.loc[teams_switched, team2_cols + team1_cols].values
    return df


async def add_ml_target(df: pd.DataFrame) -> pd.DataFrame:
    df["goal_diff"] = df.goals_team1 - df.goals_team2
    return df


async def ml_data_query(n_rows: Union[int, None]) -> str:
    if n_rows:
        limit_statement = f"limit {n_rows}"
    else:
        limit_statement = ""
    return f"""
        with userrating_before_game_was_appoved as (
    select * from 
    (
      select 
      user_id, 
      latest_result_at_update_id as result_id, 
      lag(overall_rating, 1) over (order by user_id, created_dt) overall_rating_before_game,
      lag(rating_defence, 1) over (order by user_id, created_dt) defensive_rating_before_game,
      lag(rating_offence, 1) over (order by user_id, created_dt) offensive_rating_before_game
      from userrating
    ) sub
    where result_id is not null
),
latest_user_rating as (
  select distinct
  r.user_id, 
  overall_rating as overall_rating_latest_game,
  rating_defence as rating_defence_latest_game, 
  rating_offence as rating_offence_latest_game
  from userrating r
  inner join (
   select 
      user_id, 
      max(latest_result_at_update_id) as max_result_id 
      from userrating
  	  where latest_result_at_update_id is not null
   group by user_id
   ) sub
   on r.latest_result_at_update_id = sub.max_result_id
)    


        select 
            rs.id as result_id,
            rs.created_dt as result_dt,
            rs.approved as result_approved,
            rs.goals_team1,
            rs.goals_team2,
            t1.defender_user_id as team1_defender_user_id,
            t1.attacker_user_id as team1_attacker_user_id,
            t2.defender_user_id as team2_defender_user_id,
            t2.attacker_user_id as team2_attacker_user_id,

            COALESCE(rbr1d.overall_rating_before_game, COALESCE(lur1d.overall_rating_latest_game, 1500.00)) as team1_defender_overall_rating_before_game,
            COALESCE(rbr1d.defensive_rating_before_game, COALESCE(lur1d.rating_defence_latest_game, 1500.00)) as team1_defender_defensive_rating_before_game,
            COALESCE(rbr1d.offensive_rating_before_game, COALESCE(lur1d.rating_offence_latest_game, 1500.00)) as team1_defender_offensive_rating_before_game,

            COALESCE(rbr1a.overall_rating_before_game, COALESCE(lur1a.overall_rating_latest_game, 1500.00)) as team1_attacker_overall_rating_before_game,
            COALESCE(rbr1a.defensive_rating_before_game, COALESCE(lur1a.rating_defence_latest_game, 1500.00)) as team1_attacker_defensive_rating_before_game,
            COALESCE(rbr1a.offensive_rating_before_game, COALESCE(lur1a.rating_offence_latest_game, 1500.00)) as team1_attacker_offensive_rating_before_game,

	        COALESCE(rbr2d.overall_rating_before_game, COALESCE(lur2d.overall_rating_latest_game, 1500.00)) as team2_defender_overall_rating_before_game,
            COALESCE(rbr2d.defensive_rating_before_game, COALESCE(lur2d.rating_defence_latest_game, 1500.00)) as team2_defender_defensive_rating_before_game,
            COALESCE(rbr2d.offensive_rating_before_game, COALESCE(lur2d.rating_offence_latest_game, 1500.00)) as team2_defender_offensive_rating_before_game,

	        COALESCE(rbr2a.overall_rating_before_game, COALESCE(lur2a.overall_rating_latest_game, 1500.00)) as team2_attacker_overall_rating_before_game,
            COALESCE(rbr2a.defensive_rating_before_game, COALESCE(lur2a.rating_defence_latest_game, 1500.00)) as team2_attacker_defensive_rating_before_game,
            COALESCE(rbr2a.offensive_rating_before_game, COALESCE(lur2a.rating_offence_latest_game, 1500.00)) as team2_attacker_offensive_rating_before_game

        from resultsubmission rs
        inner join team t1 on rs.team1_id = t1.id
        inner join team t2 on rs.team2_id = t2.id
        left join userrating_before_game_was_appoved rbr1d on rbr1d.user_id = t1.defender_user_id and rs.id = rbr1d.result_id
        left join userrating_before_game_was_appoved rbr1a on rbr1a.user_id = t1.attacker_user_id and rs.id = rbr1a.result_id
        left join userrating_before_game_was_appoved rbr2d on rbr2d.user_id = t2.defender_user_id and rs.id = rbr2d.result_id
        left join userrating_before_game_was_appoved rbr2a on rbr2a.user_id = t2.attacker_user_id and rs.id = rbr2a.result_id
        left join latest_user_rating lur1d on lur1d.user_id = t1.defender_user_id
        left join latest_user_rating lur1a on lur1a.user_id = t1.attacker_user_id
        left join latest_user_rating lur2d on lur2d.user_id = t2.defender_user_id
        left join latest_user_rating lur2a on lur2a.user_id = t2.attacker_user_id
        order by rs.id desc
        {limit_statement}
    """


async def get_ml_data(
        session: AsyncSession,
        n_rows: Union[int, None] = None,
        result_id_to_predict: Union[int, None] = None,
) -> pd.DataFrame:
    """Get data for ML training or prediction.

    If result_id_to_predict is passed, no results after this result id will be included and the result with that id,
    will have the outcome columns removed and have a column
    """
    query = await ml_data_query(n_rows)
    results = await session.execute(text(query))
    results = results.all()
    df = pd.DataFrame(
        columns=[
            "result_id",
            "result_dt",
            "result_approved",
            "goals_team1",
            "goals_team2",
            "team1_defender_user_id",
            "team1_attacker_user_id",
            "team2_defender_user_id",
            "team2_attacker_user_id",
            "team1_defender_overall_rating_before_game",
            "team1_defender_defensive_rating_before_game",
            "team1_defender_offensive_rating_before_game",
            "team1_attacker_overall_rating_before_game",
            "team1_attacker_defensive_rating_before_game",
            "team1_attacker_offensive_rating_before_game",
            "team2_defender_overall_rating_before_game",
            "team2_defender_defensive_rating_before_game",
            "team2_defender_offensive_rating_before_game",
            "team2_attacker_overall_rating_before_game",
            "team2_attacker_defensive_rating_before_game",
            "team2_attacker_offensive_rating_before_game",
        ],
        data=results,
    )
    df = await randomize_team_order(df)
    df = await add_ml_target(df)

    df["result_to_predict"] = False
    if result_id_to_predict:
        df = df[df.result_id <= result_id_to_predict]
        latest_result = df.result_id.max()
        df.loc[df.result_id == latest_result, "result_to_predict"] = True
        df.loc[
            df.result_id == latest_result,
            ["result_id", "goals_team1", "goals_team2", "goal_diff"]
        ] = [None, None, None, None]
    return df.replace({np.nan: None})


async def get_ml_prediction(url: str, data_for_prediction: DataForML) -> Union[int, None]:
    """Get prediction from ml microservice

    If we do not get a response with a status code 200, where the json content is an integer,
    we return None
    """
    async with httpx.AsyncClient() as client:
        resp: Response = await client.post(
            url=url,
            json=json.loads(data_for_prediction.json()),
        )

    if resp.status_code == 200:
        json_resp = resp.json()
        if isinstance(json_resp, int):
            return json_resp
    else:
        return None


async def suggest_most_fair_teams(
        users: UsersForTeamsSuggestion, session: AsyncSession = Depends(get_session)
) -> TeamsSuggestion:
    """Get most fair teams by minimizing the predicted goal difference

    We call a prediction API to get the goal difference for all team combinations
    """
    # Get data for prediction for previous results
    ml_data = await get_ml_data(
        session=session, n_rows=settings.N_HISTORICAL_ROWS_FOR_PREDICTION
    )

    # Get the latest ratings for players
    user_ids = [users.user_id_1, users.user_id_2, users.user_id_3, users.user_id_4]
    latest_ratings = await get_latest_ratings(session=session)
    user_ratings = {
        r.user_id: {
            "rating_defence": r.rating_defence, "rating_offence": r.rating_offence, "rating_overall": r.overall_rating
        }
        for r in latest_ratings if r.user_id in user_ids
    }

    # Create all combinations of users
    possible_user_combinations = list(itertools.permutations(user_ids))

    user_comb_predictions: dict= {}
    for user_comb in possible_user_combinations:
        combination_date_for_pred = RowForML(
            result_to_predict=True,
            result_dt= datetime.now(),
            team1_defender_user_id=user_comb[0],
            team1_attacker_user_id=user_comb[1],
            team2_defender_user_id=user_comb[2],
            team2_attacker_user_id=user_comb[3],
            team1_defender_overall_rating_before_game=user_ratings[user_comb[0]]["rating_overall"],
            team1_defender_defensive_rating_before_game=user_ratings[user_comb[0]]["rating_defence"],
            team1_defender_offensive_rating_before_game=user_ratings[user_comb[0]]["rating_offence"],
            team1_attacker_overall_rating_before_game=user_ratings[user_comb[1]]["rating_overall"],
            team1_attacker_defensive_rating_before_game=user_ratings[user_comb[1]]["rating_defence"],
            team1_attacker_offensive_rating_before_game=user_ratings[user_comb[1]]["rating_offence"],
            team2_defender_overall_rating_before_game=user_ratings[user_comb[2]]["rating_overall"],
            team2_defender_defensive_rating_before_game=user_ratings[user_comb[2]]["rating_defence"],
            team2_defender_offensive_rating_before_game=user_ratings[user_comb[2]]["rating_offence"],
            team2_attacker_overall_rating_before_game=user_ratings[user_comb[3]]["rating_overall"],
            team2_attacker_defensive_rating_before_game=user_ratings[user_comb[3]]["rating_defence"],
            team2_attacker_offensive_rating_before_game=user_ratings[user_comb[3]]["rating_offence"],
        )

        data_for_prediction = DataForML(
            data=[RowForML(**r) for r in ml_data.to_dict(orient="records")] + [combination_date_for_pred]
        )
        user_comb_predictions[user_comb] = await get_ml_prediction(
            url=settings.ML_MODEL_API_BASE_URL, data_for_prediction=data_for_prediction
        )

    # Get user combinations with the lowest predicted goal difference
    min_goal_diffs = min(user_comb_predictions.values())
    user_combinations_with_mon_expected_goal_dff = [k for k, v in user_comb_predictions.items() if v == min_goal_diffs]

    # Return first user combination with min expected goal diff
    return TeamsSuggestion(
        team1=TeamCreate(
            defender_user_id=user_combinations_with_mon_expected_goal_dff[0][0],
            attacker_user_id=user_combinations_with_mon_expected_goal_dff[0][1],
        ),
        team2=TeamCreate(
            defender_user_id=user_combinations_with_mon_expected_goal_dff[0][2],
            attacker_user_id=user_combinations_with_mon_expected_goal_dff[0][3],
        ),
    )
