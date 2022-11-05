# FootyTracker ML microservice to predict goal differences of matches

The service is used for suggesting the most fair teams, by calling it with different team combinations and using the 
one with the minimum expected goal difference.

At the moment the model is a Bayesian model that estimates each users offensive and defensive strength.