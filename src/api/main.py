from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

models.SqlAlchemyBase.metadata.create_all(bind=engine)

app = FastAPI()


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/users/login/", response_model=schemas.UserOut)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.login_user(db, email=user.email, password=user.password)
    if not db_user:
        raise HTTPException(status_code=404, detail="Email or password not correct")
    return db_user


@app.get("/users/", response_model=List[schemas.UserOut])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_users = crud.get_users(db, skip=skip, limit=limit)
    return db_users


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/by_email/{email}", response_model=schemas.UserOut)
def read_users_by_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/by_nickname/{nickname}", response_model=schemas.UserOut)
def read_users_by_email(nickname: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_nickname(db, nickname=nickname)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/users/{user_id}/results_for_approval/", response_model=List[schemas.ResultSubmissionOut])
def read_results_for_approval(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_results_for_review(db, reviewer_id=db_user.id)


@app.post("/results/", response_model=schemas.ResultSubmissionOut)
def create_result(result: schemas.ResultSubmissionCreate, db: Session = Depends(get_db)):
    return crud.create_result(db=db, result=result)


@app.get("/results/", response_model=List[schemas.UserOut])
def read_users(reviever=None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if not reviever:
        db_results = crud.get_results(db, skip=skip, limit=limit)
    return db_results


@app.get("/results/{result_id}", response_model=schemas.ResultSubmissionOut)
def read_result(result_id: int, db: Session = Depends(get_db)):
    db_result = crud.get_result(db, result_id=result_id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="User result found")
    return db_result


# @app.post("/result_approvals/", response_model=schemas.ResultApproval)
# def approve_result(result_approval: schemas.ResultApprovalBase, db: Session = Depends(get_db)):
#     result = crud.get_result(db, result_id=result_approval.result_submission_id)
#     if result is None:
#         raise HTTPException(status_code=404, detail="Result to be validated not found")
#     if result_approval.reviewer_id == result.submitter_id:
#         raise HTTPException(
#             status_code=400, detail="Review user can not be the same as the user that submitted the result"
#         )
#
#     return crud.create_result_approval(db=db, result_approval=result_approval)
