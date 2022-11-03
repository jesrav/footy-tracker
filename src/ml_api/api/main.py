"""
FootyTracker ML microservice to predict goal difference of match.

We use a bayesian model where each user has an attack and defensive strength.

The goal difference is modelled as a normal distribution where the mean (expected goal difference)
has a contribution from each player's attack or defensive strength.

This way we can directly interpret the strength of each player on offense or defense as their expected
contribution to the goal difference.
"""
import pickle
from typing import Dict, List

from fastapi import FastAPI, HTTPException

from api.schemas import DataForML, RowForML, FootyStrength, UserStrength

with open("api/model_training_artifacts/model.pickle", "rb") as f:
    model = pickle.load(f)

app = FastAPI()


def predict_using_user_strengths(row: RowForML, model: Dict[int, FootyStrength]) -> float:
    """Predict goal difference for a single row of data"""
    team1_strength = model[row.team1_attacker_user_id].defensive_strength + model[row.team2_defender_user_id].attack_strength
    team2_strength = model[row.team2_attacker_user_id].defensive_strength - model[row.team1_defender_user_id].attack_strength
    return team1_strength - team2_strength


@app.post("/predict")
async def predict(body: DataForML) -> float:
    try:
        row_to_predict = [row for row in body.data if row.result_to_predict][0]
    except IndexError:
        raise HTTPException(
            status_code=404,
            detail="No row to predict. At least one row must have the result_to_predict flag set to true."
        )
    try:
        prediction = predict_using_user_strengths(row_to_predict, model)
    except KeyError:
        raise HTTPException(status_code=404, detail="one of the users of the result to predict does not exist.")
    return prediction


@app.post("/predict")
async def predict(body: DataForML) -> float:
    row_to_predict = [row for row in body.data if row.result_to_predict][0]
    return predict_using_user_strengths(row_to_predict, model)


@app.get("/get_user_strengths", response_model=List[UserStrength])
async def get_user_strengths() -> List[UserStrength]:
    return [
        UserStrength(user_id=user_id, **strength.dict())
        for user_id, strength in model.items()
    ]
