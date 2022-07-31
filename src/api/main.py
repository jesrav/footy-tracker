from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlmodel import SQLModel

import crud, schemas
from database import engine, create_db_and_tables, get_session

SQLModel.metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
    user = crud.get_user_by_email(session, email=user.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(session=session, user=user)


@app.post("/users/login/", response_model=schemas.UserRead)
def login_user(user: schemas.UserLogin, session: Session = Depends(get_session)):
    user = crud.login_user(session, email=user.email, password=user.password)
    if not user:
        raise HTTPException(status_code=404, detail="Email or password not correct")
    return user


@app.get("/users/", response_model=List[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = crud.get_users(session, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    users = crud.get_user(session, user_id=user_id)
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users


@app.get("/users/by_email/{email}", response_model=schemas.UserRead)
def read_users_by_email(email: str, session: Session = Depends(get_session)):
    user = crud.get_user_by_email(session, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/by_nickname/{nickname}", response_model=schemas.UserRead)
def read_users_by_email(nickname: str, session: Session = Depends(get_session)):
    user = crud.get_user_by_nickname(session, nickname=nickname)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/{user_id}/results_for_approval/", response_model=List[schemas.ResultSubmissionRead])
def read_results_for_approval(user_id: int, session: Session = Depends(get_session)):
    user = crud.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_results_for_validation(session, validator_id=user.id)


@app.post("/users/{user_id}/validate_result/{result_id}/", response_model=schemas.ResultSubmissionRead)
def validate_result(user_id: int, result_id: int, approved: bool, session: Session = Depends(get_session)):
    user = crud.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = crud.get_result(session, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result submission not found")

    if result.submitter_id == user_id:
        raise HTTPException(status_code=400, detail="User can not validate result that they submitted themselves")

    # Validator must not be on one of the teams and must not be the same team as the submitter
    if user_id in [result.team1.defender_user_id, result.team1.attacker_user_id]:
        validator_team = result.team1
    elif user_id in [result.team2.defender_user_id, result.team2.attacker_user_id]:
        validator_team = result.team2
    else:
        validator_team = None
    if not validator_team:
        raise HTTPException(status_code=400, detail="Validating user must be part of one of the teams int the match")
    if result.submitter_id in [validator_team.defender_user_id, validator_team.attacker_user_id]:
        raise HTTPException(
            status_code=400, detail="Validating user can not be on the same team as the user that submitted the result"
        )

    validated_result = crud.validate_result(session, validator_id=user.id, result_id=result_id, approved=approved)

    if approved:
        _ = crud.update_ratings(session, result=validated_result)

    session.refresh(validated_result)
    return validated_result


@app.post("/results/", response_model=schemas.ResultSubmissionRead)
def create_result(result: schemas.ResultSubmissionCreate, session: Session = Depends(get_session)):
    return crud.create_result(session=session, result=result)


@app.get("/results/", response_model=List[schemas.UserRead])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    results = crud.get_results(session, skip=skip, limit=limit)
    return results


@app.get("/results/{result_id}", response_model=schemas.ResultSubmissionRead)
def read_result(result_id: int, session: Session = Depends(get_session)):
    result = crud.get_result(session, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User result found")
    return result


@app.get("/ratings/{user_id}", response_model=List[schemas.UserRatingRead])
def read_ratings(user_id: int, skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    user = crud.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_ratings(session, user_id=user_id, skip=skip, limit=limit)


@app.get("/ratings/{user_id}/latest", response_model=schemas.UserRatingRead)
def read_latest_rating(user_id: int, session: Session = Depends(get_session)):
    user = crud.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_latest_user_rating(session, user_id=user_id)

#
# @app.post("/results/approve/", response_model=schemas.ResultSubmissionOut)
# def approve_result(result_approval: schemas.ResultApprovalBase, session: Session = Depends(get_session)):
#     result = crud.get_result(session, result_id=result_approval.result_submission_id)
#     if result is None:
#         raise HTTPException(status_code=404, detail="Result to be validated not found")
#     if result_approval.reviewer_id == result.submitter_id:
#         raise HTTPException(
#             status_code=400, detail="Review user can not be the same as the user that submitted the result"
#         )
#
#     return crud.create_result_approval(session=session, result_approval=result_approval)
