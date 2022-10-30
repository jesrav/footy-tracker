import arviz as az
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm
from sklearn.base import BaseEstimator, TransformerMixin


RANDOM_SEED = 8927
rng = np.random.default_rng(RANDOM_SEED)
az.style.use("arviz-darkgrid")


def magic_footy_sigmoid(x):
    """"Magic footy sigmoid that outputs value between -10 and 10"""
    if x >= 0:
        z = math.exp(-x)
        return 20 * (1 / (1 + z)) - 10
    else:
        z = math.exp(x)
        return 20 * (z / (1 + z)) - 10


df = pd.read_csv('footy-data.csv')

#users = list(set(
#    df['team1_defender_user_id'].tolist()
#    + df['team1_attacker_user_id'].tolist()
#    + df['team2_defender_user_id'].tolist()
#    + df['team2_attacker_user_id'].tolist()
#))

#team1_def_idx = df.team1_defender_user_id.apply(lambda x: users.index(x))
#team1_att_idx = df.team1_attacker_user_id.apply(lambda x: users.index(x))
#team2_def_idx = df.team2_defender_user_id.apply(lambda x: users.index(x))
#team2_att_idx = df.team2_attacker_user_id.apply(lambda x: users.index(x))


class FootyModel(BaseEstimator, TransformerMixin):
    def __init__(self, mc_sample_size=1500, mc_tune_size=1500):
        self.model = pm.Model()
        self.users = None
        self.trace = None
        self.attack_strengths = None
        self.defensive_strengths = None
        self.mc_sample_size = mc_sample_size
        self.mc_tune_size = mc_tune_size

    def fit(self, df):
        self.users = list(set(
            df['team1_defender_user_id'].tolist()
            + df['team1_attacker_user_id'].tolist()
            + df['team2_defender_user_id'].tolist()
            + df['team2_attacker_user_id'].tolist()
        ))
        team1_def_idx = df.team1_defender_user_id.apply(lambda x: self.users.index(x))
        team1_att_idx = df.team1_attacker_user_id.apply(lambda x: self.users.index(x))
        team2_def_idx = df.team2_defender_user_id.apply(lambda x: self.users.index(x))
        team2_att_idx = df.team2_attacker_user_id.apply(lambda x: self.users.index(x))

        with pm.Model(coords={"user": self.users}) as model:
            # constant data
            team1_def = pm.ConstantData("team1_def", team1_def_idx, dims="match")
            team1_att = pm.ConstantData("team1_att", team1_att_idx, dims="match")
            team2_def = pm.ConstantData("team2_def", team2_def_idx, dims="match")
            team2_att = pm.ConstantData("team2_att", team2_att_idx, dims="match")

            # global model parameters
            sd_att = pm.HalfNormal("sd_att", sigma=2)
            sd_def = pm.HalfNormal("sd_def", sigma=2)
            sd = pm.HalfNormal("sd", sigma=1)

            # User-specific model parameters
            attack_strength = pm.Normal("attack_strength", mu=0, sigma=sd_att, dims="user")
            defensive_strength = pm.Normal("defensive_strength", mu=0, sigma=sd_def, dims="user")

            team1_theta = attack_strength[team1_att_idx] + defensive_strength[team1_def_idx]
            team2_theta = attack_strength[team2_att_idx] + defensive_strength[team2_def_idx]

            # likelihood of observed data
            goal_diff = pm.Normal(
                "goal_diff",
                mu=team1_theta - team2_theta,
                sigma=sd,
                observed=df["goal_diff"],
                dims="match",
            )
            self.trace = pm.sample(self.mc_sample_size, tune=1500, cores=1)

        attack_strengths_values = self.trace.posterior["attack_strength"].mean(dim=("chain", "draw")).values
        self.attack_strengths = {u: attack_strengths_values[i] for i, u in enumerate(self.users)}

        defensive_strengths_values = self.trace.posterior["defensive_strength"].mean(
            dim=("chain", "draw")).values
        self.defensive_strengths = {u: defensive_strengths_values[i] for i, u in enumerate(self.users)}



footy_model = FootyModel()
footy_model.fit(df)


##########################################################################
# Analysis
##########################################################################
az.summary(footy_model.trace, kind="diagnostics")

trace_hdi = az.hdi(footy_model.trace)

_, ax = plt.subplots(figsize=(12, 6))
ax.scatter(footy_model.users, footy_model.trace.posterior["attack_strength"].median(dim=("chain", "draw")), color="C0", alpha=1, s=100)
ax.vlines(
    footy_model.users,
    trace_hdi["attack_strength"].sel({"hdi": "lower"}),
    trace_hdi["attack_strength"].sel({"hdi": "higher"}),
    alpha=0.6,
    lw=5,
    color="C0",
)
ax.set_xlabel("Users")
ax.set_ylabel("Posterior Attack Strength")
ax.set_title("HDI of user Attack Strength");
plt.show()


_, ax = plt.subplots(figsize=(12, 6))
ax.scatter(footy_model.users, footy_model.trace.posterior["defensive_strength"].median(dim=("chain", "draw")), color="C0", alpha=1, s=100)
ax.vlines(
    footy_model.users,
    trace_hdi["defensive_strength"].sel({"hdi": "lower"}),
    trace_hdi["defensive_strength"].sel({"hdi": "higher"}),
    alpha=0.6,
    lw=5,
    color="C0",
)
ax.set_xlabel("Users")
ax.set_ylabel("Posterior Defensive Strength")
ax.set_title("HDI of user Defensive Strength");
plt.show()
