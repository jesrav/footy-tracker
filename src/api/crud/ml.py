from typing import Optional, List, Union

from sqlalchemy import select
import numpy as np
from numpy import random
import pandas as pd
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from models.ml import MLModel, MLModelCreate, UserMLModel, Prediction, DataForMLInternal, DataForML
from services.ml import get_ml_prediction


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
            rs.team1_id,
            rs.team2_id,
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
            "team1_id",
            "team2_id",
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


async def create_ml_model(
    session: AsyncSession,
        ml_model_create: MLModelCreate,
        commit_changes: bool = True
) -> MLModel:
    ml_model = MLModel(
        model_name=ml_model_create.model_name,
        model_url=ml_model_create.model_url,
    )
    session.add(ml_model)
    if commit_changes:
        await session.commit()
        await session.refresh(ml_model)
    else:
        # Update the user object with autoincrement id from db without committing
        await session.flush()
        await session.refresh(ml_model)
    return ml_model


async def create_user_ml_model(
    session: AsyncSession,
        user_id: int,
        ml_model_id: int,
        commit_changes: bool = True
) -> UserMLModel:
    user_ml_model = UserMLModel(
        user_id=user_id,
        ml_model_id=ml_model_id,
    )
    session.add(user_ml_model)
    if commit_changes:
        await session.commit()
        await session.refresh(user_ml_model)
    else:
        # Update the user object with autoincrement id from db without committing
        await session.flush()
        await session.refresh(user_ml_model)
    return user_ml_model


async def get_ml_models(session: AsyncSession) -> List[MLModel]:
    statement = select(MLModel)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_ml_model(session: AsyncSession, model_id: int) -> Optional[MLModel]:
    statement = select(MLModel).filter(MLModel.id == model_id)
    result = await session.execute(statement)
    return result.scalars().first()


async def get_ml_model_by_name(session: AsyncSession, name: str) -> Optional[MLModel]:
    statement = select(MLModel).filter(MLModel.model_name == name)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_ml_model_by_url(session: AsyncSession, url: str) -> Optional[MLModel]:
    statement = select(MLModel).filter(MLModel.model_url == url)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def add_prediction(
        session: AsyncSession, model_id: int, result_id: int, predicted_goal_diff: int
) -> Prediction:
    prediction = Prediction(
        ml_model_id=model_id,
        result_id=result_id,
        predicted_goal_diff=predicted_goal_diff,
    )
    session.add(prediction)
    await session.commit()
    await session.refresh(prediction)
    return prediction


async def single_prediction_task(
    result_id: int,
    ml_model: MLModel,
    ml_data: DataForMLInternal,
    session: AsyncSession,
):
    """Make prediction and register prediction using an ML model API"""

    # Get data for prediction, without columns we don't want to send to the ML endpoint
    data_for_prediction = DataForML.parse_obj(ml_data)
    prediction = await get_ml_prediction(url=ml_model.model_url, data_for_prediction=data_for_prediction)

    if not prediction:
        return None

    # Get the row that the prediction is to be used on
    row_to_predict = [r for r in ml_data.data if r.result_to_predict][0]
    # If the teams have been switched (not shown to the algorithm), we correct the prediction
    if row_to_predict.teams_switched:
        prediction = -prediction

    # Add prediction to db
    prediction = await add_prediction(
        session=session, model_id=ml_model.id, result_id=result_id, predicted_goal_diff=prediction
    )
    return prediction
