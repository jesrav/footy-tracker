import aesara.tensor as at
import arviz as az
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymc as pm

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

users = list(set(
    df['team1_defender_user_id'].tolist()
    + df['team1_attacker_user_id'].tolist()
    + df['team2_defender_user_id'].tolist()
    + df['team2_attacker_user_id'].tolist()
))

team1_def_idx = df.team1_defender_user_id.apply(lambda x: users.index(x))
team1_att_idx = df.team1_attacker_user_id.apply(lambda x: users.index(x))
team2_def_idx = df.team2_defender_user_id.apply(lambda x: users.index(x))
team2_att_idx = df.team2_attacker_user_id.apply(lambda x: users.index(x))

footy_model = pm.Model()

with pm.Model(coords={"user": users}) as model:
    # constant data
    team1_def = pm.ConstantData("team1_def", team1_def_idx, dims="match")
    team1_att = pm.ConstantData("team1_att", team1_att_idx, dims="match")
    team2_def = pm.ConstantData("team2_def", team2_def_idx, dims="match")
    team2_att = pm.ConstantData("team2_att", team2_att_idx, dims="match")

    # global model parameters
    sd_att = pm.HalfNormal("sd_att", sigma=2)
    sd_def = pm.HalfNormal("sd_def", sigma=2)
    intercept = pm.Normal("intercept", mu=3, sigma=1)
    sd = pm.HalfNormal("sd", sigma=1)

    # team-specific model parameters
    atts = pm.Normal("atts_star", mu=0, sigma=sd_att, dims="user")
    defs = pm.Normal("defs_star", mu=0, sigma=sd_def, dims="user")

    team1_theta = at.exp(intercept + atts[team1_att_idx] + defs[team1_def])
    team2_theta = at.exp(intercept + atts[team2_att_idx] + defs[team2_def_idx])

    # likelihood of observed data
    goal_diff = pm.Normal(
        "goal_diff",
        mu=team1_theta - team2_theta,
        sigma=sd,
        observed=df["goal_diff"],
        dims=("match"),
    )
    trace = pm.sample(1000, tune=1000, cores=1)


##########################################################################
# Analysis
##########################################################################
az.summary(trace, kind="diagnostics")

trace_hdi = az.hdi(trace)

_, ax = plt.subplots(figsize=(12, 6))

ax.scatter(users, trace.posterior["atts_star"].median(dim=("chain", "draw")), color="C0", alpha=1, s=100)
ax.vlines(
    users,
    trace_hdi["atts_star"].sel({"hdi": "lower"}),
    trace_hdi["atts_star"].sel({"hdi": "higher"}),
    alpha=0.6,
    lw=5,
    color="C0",
)
ax.set_xlabel("Users")
ax.set_ylabel("Posterior Attack Strength")
ax.set_title("HDI of user Attack Strength");
plt.show()

_, ax = plt.subplots(figsize=(12, 6))

ax.scatter(users, trace.posterior["defs_star"].median(dim=("chain", "draw")), color="C0", alpha=1, s=100)
ax.vlines(
    users,
    trace_hdi["defs_star"].sel({"hdi": "lower"}),
    trace_hdi["defs_star"].sel({"hdi": "higher"}),
    alpha=0.6,
    lw=5,
    color="C0",
)
ax.set_xlabel("Users")
ax.set_ylabel("Posterior Defensive Strength")
ax.set_title("HDI of user Defensive Strength");
plt.show()