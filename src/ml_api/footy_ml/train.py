import json
import pickle

import numpy as np

import arviz as az
from matplotlib import pyplot as plt
from sklearn.model_selection import cross_val_score

from footy_ml.common import get_footy_training_data
from footy_ml.user_strength_model import UserStrengthModel

TARGET = 'goal_diff'
MODEL_TRAINING_OUT_DIR = "model_training_artifacts"


def save_user_parameter_plot(model: UserStrengthModel, parameter_name: str, outdir: str):
    trace_hdi = az.hdi(model.trace)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.scatter(model.users, model.trace.posterior[parameter_name].median(dim=("chain", "draw")), color="C0",
               alpha=1, s=100)
    ax.vlines(
        model.users,
        trace_hdi[parameter_name].sel({"hdi": "lower"}),
        trace_hdi[parameter_name].sel({"hdi": "higher"}),
        alpha=0.6,
        lw=5,
        color="C0",
    )
    ax.set_xlabel("Users")
    ax.set_ylabel(f"Posterior {parameter_name}")
    ax.set_title(f"HDI of user {parameter_name}");
    fig.savefig(f"{outdir}/{parameter_name}.png")


if __name__ == '__main__':
    print("Load data")
    df = get_footy_training_data()

    print("Initialize model")
    footy_model = UserStrengthModel()

    print("Calculate and save cross validation scores for the model")
    cv_scores_fm = cross_val_score(footy_model, df, df[TARGET], cv=5, scoring='neg_mean_squared_error')
    metrics = {"mae_cv": np.sqrt(-cv_scores_fm.mean())}
    with open(f"{MODEL_TRAINING_OUT_DIR}/metrics.json", "w") as f:
       json.dump(metrics, f)

    print("Fit model on entire data set")
    footy_model.fit(df, df.goal_diff)

    print("Save model")
    trained_model_dict = footy_model.to_minimal_representation()
    with open(f"{MODEL_TRAINING_OUT_DIR}/model.pickle", "wb") as f:
        pickle.dump(trained_model_dict, f)

    print("Plot offensive and defensive strength parameters of users")
    save_user_parameter_plot(footy_model, "defensive_strength", MODEL_TRAINING_OUT_DIR)
    save_user_parameter_plot(footy_model, "attack_strength", MODEL_TRAINING_OUT_DIR)
