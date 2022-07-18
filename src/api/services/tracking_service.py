from src.web.data import db_session
from src.web.data.match import Match


def register_match(
    team1_defender: int,
    team1_attacker: int,
    team2_defender: int,
    team2_attacker: int,
    goals_team1: int,
    goals_team2: int,
) -> Match:
    session = db_session.create_session()

    try:
        match = Match()
        match.team1_defender = team1_defender
        match.team1_attacker = team1_attacker
        match.team2_defender = team2_defender
        match.team2_attacker = team2_attacker
        match.goals_team1 = goals_team1
        match.goals_team2 = goals_team2

        session.add(match)
        session.commit()

        return match
    finally:
        session.close()
