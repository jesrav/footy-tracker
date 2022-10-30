import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.dummy import DummyRegressor
from sklearn .model_selection import cross_val_score

from common import get_footy_training_data
from user_strength_model import UserStrengthModel

FEATURES = [
    'team1_defender_defensive_rating_before_game',
    'team1_attacker_offensive_rating_before_game',
    'team2_defender_defensive_rating_before_game',
    'team2_attacker_offensive_rating_before_game'
]
TARGET = 'goal_diff'

df = get_footy_training_data()

lm = LinearRegression()
dm = DummyRegressor(strategy='mean')
fm = UserStrengthModel()

cv_scores_fm = cross_val_score(fm, df, df[TARGET], cv=5, scoring='neg_mean_squared_error')
print(np.sqrt(-cv_scores_fm.mean()))

cv_scores_lm = cross_val_score(lm, df[FEATURES], df[TARGET], cv=5, scoring='neg_mean_squared_error')
print(np.sqrt(-cv_scores_lm.mean()))

cv_scores_dm = cross_val_score(dm, df[FEATURES], df[TARGET], cv=5, scoring='neg_mean_squared_error')
print(np.sqrt(-cv_scores_dm.mean()))
