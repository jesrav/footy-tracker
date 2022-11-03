from typing import Dict

import pymc as pm
from sklearn.base import BaseEstimator, TransformerMixin

from schemas import FootyStrength


class UserStrengthModel(BaseEstimator, TransformerMixin):
    """Bayesian model where each user has an attack and defensive strength.

    The goal difference is modelled as a normal distribution where the mean (expected goal difference)
    has a contribution from each player's attack or defensive strength.
    This way we can directly interpret the strength of each player on offense or defense as their expected
    contribution to the goal difference.
    We wrap a pymc3 model in a sklearn transformer, so we can use it with a fit/predict api.
    """
    def __init__(self, mc_sample_size=1500, mc_tune_size=1500):
        self.users = None
        self.trace = None
        self.attack_strengths = None
        self.defensive_strengths = None
        self.mc_sample_size = mc_sample_size
        self.mc_tune_size = mc_tune_size

    def fit(self, X, y):
        self.users = list(set(
            X['team1_defender_user_id'].tolist()
            + X['team1_attacker_user_id'].tolist()
            + X['team2_defender_user_id'].tolist()
            + X['team2_attacker_user_id'].tolist()
        ))
        team1_def_idx = X.team1_defender_user_id.apply(lambda x: self.users.index(x))
        team1_att_idx = X.team1_attacker_user_id.apply(lambda x: self.users.index(x))
        team2_def_idx = X.team2_defender_user_id.apply(lambda x: self.users.index(x))
        team2_att_idx = X.team2_attacker_user_id.apply(lambda x: self.users.index(x))

        with pm.Model(coords={"user": self.users}) as model:
            # constant data
            team1_def = pm.ConstantData("team1_def", team1_def_idx, dims="match")
            team1_att = pm.ConstantData("team1_att", team1_att_idx, dims="match")
            team2_def = pm.ConstantData("team2_def", team2_def_idx, dims="match")
            team2_att = pm.ConstantData("team2_att", team2_att_idx, dims="match")

            # global model parameters
            sd_att = pm.HalfNormal("sd_att", sigma=5)
            sd_def = pm.HalfNormal("sd_def", sigma=5)
            sd = pm.HalfNormal("sd", sigma=5)

            # User-specific attack and defense model parameters
            attack_strength = pm.Normal("attack_strength", mu=0, sigma=sd_att, dims="user")
            defensive_strength = pm.Normal("defensive_strength", mu=0, sigma=sd_def, dims="user")

            team1_theta = attack_strength[team1_att_idx] + defensive_strength[team1_def_idx]
            team2_theta = attack_strength[team2_att_idx] + defensive_strength[team2_def_idx]

            # likelihood of observed data
            goal_diff = pm.Normal(
                "goal_diff",
                mu=team1_theta - team2_theta,
                sigma=sd,
                observed=y,
                dims="match",
            )
            self.trace = pm.sample(self.mc_sample_size, tune=1500, cores=1)

        attack_strengths_values = self.trace.posterior["attack_strength"].mean(dim=("chain", "draw")).values
        self.attack_strengths = {u: attack_strengths_values[i] for i, u in enumerate(self.users)}

        defensive_strengths_values = self.trace.posterior["defensive_strength"].mean(dim=("chain", "draw")).values
        self.defensive_strengths = {u: defensive_strengths_values[i] for i, u in enumerate(self.users)}
        return self

    def predict(self, X):
        X = X.copy()
        X["teadm1_def_strength"] = X.team1_defender_user_id.apply(lambda x: self.defensive_strengths.get(x, 0))
        X["team1_att_strength"] = X.team1_attacker_user_id.apply(lambda x: self.attack_strengths.get(x, 0))
        X["team2_def_strength"] = X.team2_defender_user_id.apply(lambda x: self.defensive_strengths.get(x, 0))
        X["team2_att_strength"] = X.team2_attacker_user_id.apply(lambda x: self.attack_strengths.get(x, 0))
        X["team1_theta"] = X.teadm1_def_strength + X.team1_att_strength
        X["team2_theta"] = X.team2_def_strength + X.team2_att_strength
        return (X["team1_theta"] - X["team2_theta"]).clip(-10, 10)

    def to_minimal_representation(self) -> Dict[int, FootyStrength]:
        return {
            int(u): FootyStrength(
                attack_strength=float(self.attack_strengths[u]),
                defensive_strength=float(self.defensive_strengths[u]),
            )
            for u in self.users
        }
