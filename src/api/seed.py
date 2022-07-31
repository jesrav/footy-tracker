from sqlmodel import Session, select

import crud
import schemas
from database import engine


nicknames = [
    "TheMan",
    "Elo",
    "Fock",
    "Nanny"
]

users = [
    schemas.UserCreate(
        nickname=nicname,
        email=f"{nicname.lower()}@mail.com",
        password=nicname.lower(),
    ) for nicname in nicknames
]

with Session(engine) as session:
    for user in users:
        crud.create_user(session=session, user=user)

with Session(engine) as session:
    crud.create_result(
        session=session,
        result=schemas.ResultSubmissionCreate(
            submitter_id=1,
            team1=schemas.TeamCreate(
                defender_user_id=1,
                attacker_user_id=2,
            ),
            team2=schemas.TeamCreate(
                defender_user_id=3,
                attacker_user_id=4,
            ),
            goals_team1=1,
            goals_team2=10,
        )
    )


with Session(engine) as session:
    statement = select(schemas.ResultSubmission)
    r = session.exec(statement).first()
    print(r.team1)