from passlib.handlers.sha2_crypt import sha512_crypt as crypto


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return crypto.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return crypto.hash(password, rounds=172_434)
