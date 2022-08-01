from sqlmodel import Session

import crud
import crud.result
import crud.user
import models
import models.result
import models.team
import models.user
from database import engine


nicknames = [
    "TheMan",
    "Elo",
    "Fock",
    "Nanny"
]

users = [
    models.user.UserCreate(
        nickname=nicname,
        email=f"{nicname.lower()}@mail.com",
        password=nicname.lower(),
    ) for nicname in nicknames
]

with Session(engine) as session:
    for user in users:
        crud.user.create_user(session=session, user=user)

with Session(engine) as session:
    crud.result.create_result(
        session=session,
        result=models.result.ResultSubmissionCreate(
            submitter_id=1,
            team1=models.team.TeamCreate(
                defender_user_id=1,
                attacker_user_id=2,
            ),
            team2=models.team.TeamCreate(
                defender_user_id=3,
                attacker_user_id=4,
            ),
            goals_team1=1,
            goals_team2=10,
        )
    )
