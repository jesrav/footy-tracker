from passlib.handlers.sha2_crypt import sha512_crypt as crypto

import models
from database import SessionLocal

db = SessionLocal()


users = [
    models.User(
        nickname=name,
        email=f"{name}@mail.com",
        hash_password=crypto.hash(f"{name}", rounds=172_434)
    ) for name in ["a", "b", "c", "d"]
]
for user in users:
    db.add(user)
db.commit()
