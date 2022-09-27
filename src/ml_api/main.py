"""
FootyTracker ML microservice example
"""
import math
from random import choice

from fastapi import FastAPI

from schemas import RowForML, DataForML

app = FastAPI()


def predict_goal_diff_rule(result_to_predict: RowForML) -> int:
    """Predict the goal diff off the game using only the row of features for the actual game.

    If Jesus (user id 1) is on offence, his team will always win by 5
    Otherwise we predict a random goal diff between -3 and 3, but never 0.
    """

    if result_to_predict.team1_attacker_user_id == 1:
        return 5
    elif result_to_predict.team2_attacker_user_id == 1:
        return -5
    else:
        return choice([-3, -2, -1, 1, 2, 3])


def magic_footy_sigmoid(x):
    """"Magic footy sigmoid that outputs value between -10 and 10"""
    if x >= 0:
        z = math.exp(-x)
        return 20 * (1 / (1 + z)) - 10
    else:
        z = math.exp(x)
        return 20 * (z / (1 + z)) - 10


def predict_goal_diff_based_on_ratings(result_to_predict: RowForML) -> int:
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
    return round(magic_footy_sigmoid((team1_rating - team2_rating) / magic_factor))


@app.post("/rule_based_predict")
def predict(body: DataForML) -> int:
    result_to_predict = [r for r in body.data if r.result_to_predict][0]
    return predict_goal_diff_rule(result_to_predict)


@app.post("/rating_based_predict")
def predict(body: DataForML) -> int:
    result_to_predict = [r for r in body.data if r.result_to_predict][0]
    return predict_goal_diff_based_on_ratings(result_to_predict)
