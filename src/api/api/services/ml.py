import json
from typing import Union, List

from numpy import random
import httpx
import numpy as np
from httpx import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
import pandas as pd
from starlette.background import BackgroundTasks

from api.crud.ml import get_ml_models, add_prediction, add_ml_metrics, get_predictions
from api.models.ml import (
    DataForML, DataForMLInternal, RowForMLInternal, MLModel, Prediction, PredictionRead, MLMetric
)
from api.core.config import settings
from api.models.result import ResultSubmission


async def get_ml_prediction(url: str, data_for_prediction: DataForML) -> Union[float, None]:
    """Get prediction for goal difference (team1 goals - team2 goals) from ML microservice

    The prediction is supposed to be made for the row `RowForML` with attribute result_to_predict = True.

    If we do not get a successful response with a status code 200, where the json content is an integer,
    we return None
    """
    timeout = httpx.Timeout(10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp: Response = await client.post(
            url=url,
            json=json.loads(data_for_prediction.json()),
        )
    if resp.status_code != 200:
        return None
    json_resp = resp.json()
    if isinstance(json_resp, float):
        return json_resp


async def single_prediction_task(
    result_id: int,
    ml_model: MLModel,
    ml_data: DataForMLInternal,
    session: AsyncSession,
) -> Union[Prediction, None]:
    """Make prediction for a specific result id using an ML model API and write prediction to db.

    If the API call is unsuccessful we return None and no prediction is written to the db.


    Parameters
    ----------
    result_id: int
        Result id for the match we are making a prediction for
    ml_model: MLModel
        ML model (API) we are using to make the prediction
    ml_data: DataForMLInternal
        Data for making prediction. Contains information that is not sent to the ML API
    session: AsyncSession

    Returns
    -------
    int
        Predicted goal difference (team1 goals - team2 goals)
    """
    # Get data for prediction, without columns we don't want to send to the ML endpoint
    data_for_prediction = DataForML.parse_obj(ml_data)

    # Get a prediction from ML model API
    prediction = await get_ml_prediction(url=ml_model.model_url, data_for_prediction=data_for_prediction)

    if prediction is None:
        return None

    # Get the row/result that the prediction was made on
    row_to_predict = [r for r in ml_data.data if r.result_to_predict][0]

    # If the teams have been switched (not shown to the API), we correct the prediction
    if row_to_predict.teams_switched:
        prediction = -prediction

    # Add prediction to db
    prediction = await add_prediction(
        session=session, model_id=ml_model.id, result_id=result_id, predicted_goal_diff=prediction
    )
    return prediction


async def add_prediction_background_tasks(
        result: ResultSubmission, ml_prediction_background_tasks: BackgroundTasks, session: AsyncSession
):
    """Add predictions tasks for a specific result to a collection of background tasks `ml_prediction_background_tasks`

    A prediction task is added for each model registered in the db.
    """
    ml_models = await get_ml_models(session=session)
    ml_data = await get_ml_data(
        session=session, n_rows=settings.N_HISTORICAL_ROWS_FOR_PREDICTION, result_id_to_predict=result.id
    )
    for ml_model in ml_models:
        ml_prediction_background_tasks.add_task(
            single_prediction_task,
            result_id=result.id,
            ml_model=ml_model,
            ml_data=ml_data,
            session=session,
        )


async def update_ml_metrics_from_predictions(session: AsyncSession):
    """Add model metrics for any new approved results"""
    predictions = await get_predictions(session=session)
    ml_metrics = calculate_ml_metrics(
        predictions,
        short_rolling_window_size=settings.METRICS_SHORT_WINDOW_SIZE,
        long_rolling_window_size=settings.METRICS_LONG_WINDOW_SIZE
    )
    await add_ml_metrics(ml_metrics, session=session)


def mean_absolute_error(y_pred: float, y_actual: int) -> float:
    return abs(y_pred - y_actual)


def calculate_ml_metrics(
    predictions: List[PredictionRead],
    short_rolling_window_size: int = 10,
    long_rolling_window_size: int = 100,
) -> List[MLMetric]:
    """Calculate metrics for each model."""
    # Only use results that have a goal dif (They have been approved)
    predictions = [pred for pred in predictions if pred.result_goal_diff is not None]

    # Get data into a dataframe
    predictions_df = pd.DataFrame([pred.dict() for pred in predictions])

    # Add the absolute error of each prediction
    predictions_df['ae'] = predictions_df.apply(
        lambda x: mean_absolute_error(x['predicted_goal_diff'], x['result_goal_diff']), axis=1
    )

    # Add the rolling mean absolute error for each model for a short and long window
    predictions_df = predictions_df.sort_values(by=['ml_model_id', 'created_dt'])
    predictions_df["rolling_short_window_mae"] = (
        predictions_df.groupby('ml_model_id')["ae"]
        .rolling(window=short_rolling_window_size, min_periods=1)
        .mean().values
    )
    predictions_df = predictions_df.sort_values(by=['ml_model_id', 'created_dt'])
    predictions_df["rolling_long_window_mae"] = (
        predictions_df.groupby('ml_model_id')["ae"]
        .rolling(window=long_rolling_window_size, min_periods=1)
        .mean().values
    )

    # Rename columns to match MLMetric pydantic model
    predictions_df = predictions_df.rename(columns={'created_dt': 'prediction_dt', "id": "prediction_id"})

    # Make dictionary representation of data jsonifiable
    ml_metrics_data = predictions_df.to_dict('records')
    for rec in ml_metrics_data:
        rec['prediction_dt'] = rec['prediction_dt'].to_pydatetime()

    return [MLMetric(**row) for row in ml_metrics_data]


async def get_ml_data(
        session: AsyncSession,
        n_rows: Union[int, None] = None,
        result_id_to_predict: Union[int, None] = None,
) -> DataForMLInternal:
    """Get data for ML training or prediction.

    If `result_id_to_predict` is passed, no results after this result id will be included and the result with that id,
    will have the columns "result_id", "goals_team1", "goals_team2" and "goal_diff" removed and have column
    result_to_predict set to True.

    We randomize the team order to avoid the information leakage present in knowing that team1 registered on a result
    is almost always the winner.
    """
    query = await get_ml_data_query(n_rows)
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
    df = df.replace({np.nan: None})
    return DataForMLInternal(data=[RowForMLInternal(**r) for r in df.to_dict(orient="records")])


async def randomize_team_order(df: pd.DataFrame) -> pd.DataFrame:
    """Randomly swap team 1 and team 2 in dataframe with ml data.

    A boolean column teams_switched to indicate if team 1 and team 2 have been switched.
    """
    df = df.copy()
    teams_switched = random.rand(len(df)) > 0.5
    df["teams_switched"] = teams_switched
    team1_cols = [col for col in df.columns if "team1" in col]
    team2_cols = [col for col in df.columns if "team2" in col]
    df.loc[teams_switched, team1_cols + team2_cols] = df.loc[teams_switched, team2_cols + team1_cols].values
    return df


async def add_ml_target(df: pd.DataFrame) -> pd.DataFrame:
    """Add target to dataframe with ML data"""
    df["goal_diff"] = df.goals_team1 - df.goals_team2
    return df


async def get_ml_data_query(n_rows: Union[int, None]) -> str:
    """Get SQL query for historical data to be use in ML training and prediction"""
    limit_statement = f"limit {n_rows}" if n_rows else ""
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
   on r.latest_result_at_update_id = sub.max_result_id and r.user_id = sub.user_id
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
