from typing import Union

from numpy import random
import pandas as pd
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text


def randomize_team_order(df: pd.DataFrame) -> pd.DataFrame:
    swap_teams = random.rand(len(df)) > 0.5
    team1_cols = [col for col in df.columns if "team1" in col]
    team2_cols = [col for col in df.columns if "team2" in col]
    df.loc[swap_teams, team1_cols + team2_cols] = df.loc[swap_teams, team2_cols + team1_cols].values
    return df


def add_ml_target(df: pd.DataFrame) -> pd.DataFrame:
    df["goal_diff"] = df.goals_team1 - df.goals_team2
    return df


def ml_data_query(n_rows: int) -> str:
    if n_rows:
        limit_statement = f"limit {n_rows}"
    else:
        limit_statement = ""
    return f"""
        with ratings_before_result as (
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
         )
         
        select 
            rs.id as result_id,
            rs.created_dt as result_dt,
            rs.team1_id,
            rs.team2_id,
            rs.goals_team1,
            rs.goals_team2,
            t1.defender_user_id as team1_defender_user_id,
            t1.attacker_user_id as team1_attacker_user_id,
            t2.defender_user_id as team2_defender_user_id,
            t2.attacker_user_id as team2_attacker_user_id,
            
            rbr1d.overall_rating_before_game as team1_defender_overall_rating_before_game,
            rbr1d.defensive_rating_before_game as team1_defender_defensive_rating_before_game,
            rbr1d.offensive_rating_before_game as team1_defender_offensive_rating_before_game,
            
            rbr1a.overall_rating_before_game as team1_attacker_overall_rating_before_game,
            rbr1a.defensive_rating_before_game as team1_attacker_defensive_rating_before_game,
            rbr1a.offensive_rating_before_game as team1_attacker_offensive_rating_before_game,
            
            rbr2d.overall_rating_before_game as team2_defender_overall_rating_before_game,
            rbr2d.defensive_rating_before_game as team2_defender_defensive_rating_before_game,
            rbr2d.offensive_rating_before_game as team2_defender_offensive_rating_before_game,
            
            rbr2a.overall_rating_before_game as team2_attacker_overall_rating_before_game,
            rbr2a.defensive_rating_before_game as team2_attacker_defensive_rating_before_game,
            rbr2a.offensive_rating_before_game as team2_attacker_offensive_rating_before_game
            
        from resultsubmission rs
        inner join team t1 on rs.team1_id = t1.id
        inner join team t2 on rs.team2_id = t2.id
        inner join ratings_before_result rbr1d on rbr1d.user_id = t1.defender_user_id and rs.id = rbr1d.result_id
        inner join ratings_before_result rbr1a on rbr1a.user_id = t1.attacker_user_id and rs.id = rbr1a.result_id
        inner join ratings_before_result rbr2d on rbr2d.user_id = t2.defender_user_id and rs.id = rbr2d.result_id
        inner join ratings_before_result rbr2a on rbr2a.user_id = t2.attacker_user_id and rs.id = rbr2a.result_id
        where approved = true
        order by rs.id desc
        {limit_statement}
    """


async def get_ml_data(session: AsyncSession, n_rows: Union[int, None] = None) -> pd.DataFrame:
    results = await session.execute(text(ml_data_query(n_rows)))
    results = results.all()
    df = pd.DataFrame(
        columns=[
            "result_id",
            "result_dt",
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
    df = randomize_team_order(df)
    return add_ml_target(df)
