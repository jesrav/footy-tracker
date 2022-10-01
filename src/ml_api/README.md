# FootyTracker ML microservice to predict goal differences of matches

The service is used for suggesting the most fair teams, by calling it with different team combinations and using the 
one with the minimum expected goal difference.

At the moment it is simply a modified sigmoid transformation of the difference in team ratings.