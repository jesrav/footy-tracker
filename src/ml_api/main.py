"""
FootyTracker ML microservice to predict goal difference of match.
"""
import pickle
from typing import Dict

from fastapi import FastAPI

from schemas import DataForML, RowForML, UserStrength

with open("model_training_artifacts/model.pickle", "rb") as f:
    model = pickle.load(f)

app = FastAPI()


def predict_using_user_strengths(row: RowForML, model: Dict[int, UserStrength]) -> float:
    """Predict goal difference for a single row of data"""
    team1_strength = model[row.team1_attacker_user_id].defensive_strength + model[row.team2_defender_user_id].attack_strength
    team2_strength = model[row.team2_attacker_user_id].defensive_strength - model[row.team1_defender_user_id].attack_strength
    return team1_strength - team2_strength


@app.post("/rating_based_predict")
async def predict(body: DataForML) -> float:
    row_to_predict = [row for row in body.data if row.result_to_predict][0]
    return predict_using_user_strengths(row_to_predict, model)
