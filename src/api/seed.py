from passlib.handlers.sha2_crypt import sha512_crypt as crypto

import crud
import schemas
from database import SessionLocal

db = SessionLocal()

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
for user in users:
    crud.create_user(db, user)

