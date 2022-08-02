from datetime import datetime
from typing import List, Optional

from sqlmodel import Session, select

from crud.team import get_team, create_team
from models import result as result_models


def create_result(session: Session, result: result_models.ResultSubmissionCreate) -> result_models.ResultSubmission:
    team1_db = get_team(session, team=result.team1)
    if not team1_db:
        team1_db = create_team(session, team=result.team1)
    team2_db = get_team(session, team=result.team2)
    if not team2_db:
        team2_db = create_team(session, team=result.team2)

    result = result_models.ResultSubmission(
        submitter_id=result.submitter_id,
        team1_id=team1_db.id,
        team2_id=team2_db.id,
        goals_team1=result.goals_team1,
        goals_team2=result.goals_team2,
    )
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


def get_results(session: Session, skip: int = 0, limit: int = 100) -> List[result_models.ResultSubmission]:
    statement = select(result_models.ResultSubmission).offset(skip).limit(limit)
    return session.exec(statement).all()


def get_results_for_validation(session: Session, validator_id: int) -> List[result_models.ResultSubmission]:
    """Get results for validation for user

    A user will only get results where they participated, that were not submitted by a teammate.

    :param session: Database session
    :param validator_id: User id of validator (reviewer)
    :return: A list of result submissions.
    """
    statement = select(result_models.ResultSubmission).filter(
        result_models.ResultSubmission.approved == None,
        result_models.ResultSubmission.submitter_id != validator_id
    )
    results = session.exec(statement).all()

    results_with_validator_participation = [
        r for r in results if validator_id in
       [r.team1.defender_user_id, r.team1.attacker_user_id, r.team2.defender_user_id, r.team2.attacker_user_id]
    ]
    validator_teams = [
        r.team1
        if validator_id in [r.team1.defender_user_id, r.team1.attacker_user_id]
        else r.team2
        for r in results_with_validator_participation
    ]
    results_validator_and_submitter_not_teammates = [
        r for i, r in enumerate(results_with_validator_participation)
        if r.submitter_id not in [validator_teams[i].defender_user_id, validator_teams[i].attacker_user_id]
    ]
    return results_validator_and_submitter_not_teammates


def validate_result(
        session: Session, validator_id: int, result_id: int, approved: bool
) -> result_models.ResultSubmission:
    statement = select(result_models.ResultSubmission).filter(result_models.ResultSubmission.id == result_id)
    result = session.exec(statement).one()
    result.validator_id = validator_id
    result.approved = approved
    result.validation_dt = datetime.utcnow()
    session.commit()
    return result


def get_result(session: Session, result_id: int) -> Optional[result_models.ResultSubmission]:
    statement = select(result_models.ResultSubmission).filter(result_models.ResultSubmission.id == result_id)
    return session.exec(statement).one()