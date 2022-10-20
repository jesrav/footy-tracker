"""
FootyTracker ML microservice to predict goal difference of match.

Right now it's just a sigmoid transformation of the difference in team ratings.
"""
import math

from fastapi import FastAPI

from schemas import RowForML, DataForML

app = FastAPI()


async def magic_footy_sigmoid(x):
    """"Magic footy sigmoid that outputs value between -10 and 10"""
    if x >= 0:
        z = math.exp(-x)
        return 20 * (1 / (1 + z)) - 10
    else:
        z = math.exp(x)
        return 20 * (z / (1 + z)) - 10


async def predict_goal_diff_based_on_ratings(result_to_predict: RowForML) -> float:
    """"
    Naive rule to predict the result based on the teams combined rating
    """
    magic_factor = 100

    team1_rating = (
        result_to_predict.team1_attacker_offensive_rating_before_game
        + result_to_predict.team1_defender_defensive_rating_before_game
    ) / 2
    team2_rating = (
        result_to_predict.team2_attacker_offensive_rating_before_game
        + result_to_predict.team2_defender_defensive_rating_before_game
    ) / 2
    return await magic_footy_sigmoid((team1_rating - team2_rating) / magic_factor)


@app.post("/rating_based_predict")
async def predict(body: DataForML) -> float:
    result_to_predict = [r for r in body.data if r.result_to_predict][0]
    return await predict_goal_diff_based_on_ratings(result_to_predict)


@app.post("/rating_based_predict_inv")
async def predict(body: DataForML) -> float:
    result_to_predict = [r for r in body.data if r.result_to_predict][0]
    pred = await predict_goal_diff_based_on_ratings(result_to_predict)
    return -pred
