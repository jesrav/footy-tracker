import pandas as pd
import requests

FOOTY_API_URL = "https://api.footy-tracker.live/ml/training_data/json"


def get_footy_training_data() -> pd.DataFrame:
    """Get training data for footy model"""
    response = requests.get(FOOTY_API_URL)
    return pd.DataFrame(response.json()["data"])
