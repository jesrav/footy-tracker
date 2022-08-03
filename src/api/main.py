import os
from typing import List

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlmodel import SQLModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse

import crud.rating
import crud.result
import crud.user
import models.rating
import models.result
import models.user
from database import engine, create_db_and_tables, get_session

SQLModel.metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/users/", response_model=models.user.UserRead)
def create_user(user: models.user.UserCreate, session: Session = Depends(get_session)):
    preexisting_user = crud.user.get_user_by_email(session, email=user.email)
    if preexisting_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.user.create_user(session=session, user=user)


@app.post("/users/login/", response_model=models.user.UserRead)
def login_user(user: models.user.UserLogin, session: Session = Depends(get_session)):
    user = crud.user.login_user(session, email=user.email, password=user.password)
    if not user:
        raise HTTPException(status_code=404, detail="Email or password not correct")
    return user


@app.get("/users/", response_model=List[models.user.UserRead])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = crud.user.get_users(session, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=models.user.UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    users = crud.user.get_user(session, user_id=user_id)
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")
    return users


@app.get("/users/by_email/{email}", response_model=models.user.UserRead)
def read_users_by_email(email: str, session: Session = Depends(get_session)):
    user = crud.user.get_user_by_email(session, email=email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/by_nickname/{nickname}", response_model=models.user.UserRead)
def read_users_by_email(nickname: str, session: Session = Depends(get_session)):
    user = crud.user.get_user_by_nickname(session, nickname=nickname)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/users/{user_id}/results_for_approval/", response_model=List[models.result.ResultSubmissionRead])
def read_results_for_approval(user_id: int, session: Session = Depends(get_session)):
    user = crud.user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.result.get_results_for_validation(session, validator_id=user.id)


@app.post("/users/{user_id}/validate_result/{result_id}/", response_model=models.result.ResultSubmissionRead)
def validate_result(user_id: int, result_id: int, approved: bool, session: Session = Depends(get_session)):
    user = crud.user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    result = crud.result.get_result(session, result_id=result_id)
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

    validated_result = crud.result.validate_result(session, validator_id=user.id, result_id=result_id, approved=approved)

    if approved:
        _ = crud.rating.update_ratings(session, result=validated_result)

    session.refresh(validated_result)
    return validated_result


@app.post("/results/", response_model=models.result.ResultSubmissionRead)
def create_result(
        result: models.result.ResultSubmissionCreate,
        background_tasks: BackgroundTasks,
        session: Session = Depends(get_session)
):
    result = crud.result.create_result(session=session, result=result)
    for user in result.users_to_notify:
        background_tasks.add_task(send_results_for_validation_email, user.email)
    return result


@app.get("/results/", response_model=List[models.user.UserRead])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    results = crud.result.get_results(session, skip=skip, limit=limit)
    return results


@app.get("/results/{result_id}", response_model=models.result.ResultSubmissionRead)
def read_result(result_id: int, session: Session = Depends(get_session)):
    result = crud.result.get_result(session, result_id=result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="User result found")
    return result


@app.get("/ratings/{user_id}", response_model=List[models.rating.UserRatingRead])
def read_ratings(user_id: int, skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    user = crud.user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.rating.get_ratings(session, user_id=user_id, skip=skip, limit=limit)


@app.get("/ratings/{user_id}/latest", response_model=models.rating.UserRatingRead)
def read_latest_rating(user_id: int, session: Session = Depends(get_session)):
    user = crud.user.get_user(session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.rating.get_latest_user_rating(session, user_id=user_id)


async def send_results_for_validation_email(email: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email("jesravnbol@hotmail.com")
    to_email = To(email)
    subject = "You have new results to validate. See them at https://footy-tracker.azurewebsites.net/account."
    content = Content("text/plain", "and easy to do anywhere, even with Python")
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    return response.status_code
