from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.sql import text

from models.ml_training_data import MLTrainingData


ML_TRAINING_DATA_QUERY = """
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
    order by rs.id
"""


async def get_ml_training_data(session: AsyncSession) -> MLTrainingData:
    results = await session.execute(text(ML_TRAINING_DATA_QUERY))
    results = results.all()

    return MLTrainingData(
        result_id=[r[0] for r in results],
        team1_id=[r[1] for r in results],
        team2_id =[r[2] for r in results],
        goals_team1=[r[3] for r in results],
        goals_team2=[r[4] for r in results],
        team1_defender_user_id=[r[5] for r in results],
        team1_attacker_user_id=[r[6] for r in results],
        team2_defender_user_id=[r[7] for r in results],
        team2_attacker_user_id=[r[8] for r in results],
        team1_defender_overall_rating_before_game=[r[9] for r in results],
        team1_defender_defensive_rating_before_game=[r[10] for r in results],
        team1_defender_offensive_rating_before_game=[r[11] for r in results],
        team1_attacker_overall_rating_before_game=[r[12] for r in results],
        team1_attacker_defensive_rating_before_game=[r[13] for r in results],
        team1_attacker_offensive_rating_before_game=[r[14] for r in results],
        team2_defender_overall_rating_before_game=[r[15] for r in results],
        team2_defender_defensive_rating_before_game=[r[16] for r in results],
        team2_defender_offensive_rating_before_game=[r[17] for r in results],
        team2_attacker_overall_rating_before_game=[r[18] for r in results],
        team2_attacker_defensive_rating_before_game=[r[19] for r in results],
        team2_attacker_offensive_rating_before_game=[r[20] for r in results],
    )

