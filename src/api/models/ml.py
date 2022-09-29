from datetime import datetime
from typing import Union, List, Optional

from pydantic import AnyHttpUrl
from sqlalchemy import Column, String
from sqlmodel import SQLModel, Field


class RowForML(SQLModel):
    result_to_predict: bool
    result_id: Union[int, None]
    result_dt: Union[datetime, None]
    result_approved: Union[bool, None]
    team1_id: int
    team2_id: int
    goals_team1: Union[int, None]
    goals_team2: Union[int, None]
    team1_defender_user_id: int
    team1_attacker_user_id: int
    team2_defender_user_id: int
    team2_attacker_user_id: int
    team1_defender_overall_rating_before_game: float
    team1_defender_defensive_rating_before_game: float
    team1_defender_offensive_rating_before_game: float
    team1_attacker_overall_rating_before_game: float
    team1_attacker_defensive_rating_before_game: float
    team1_attacker_offensive_rating_before_game: float
    team2_defender_overall_rating_before_game: float
    team2_defender_defensive_rating_before_game: float
    team2_defender_offensive_rating_before_game: float
    team2_attacker_overall_rating_before_game: float
    team2_attacker_defensive_rating_before_game: float
    team2_attacker_offensive_rating_before_game: float
    goal_diff: Union[int, None]


class RowForMLInternal(RowForML):
    teams_switched: bool


class DataForML(SQLModel):
    data: List[RowForML]


class DataForMLInternal(SQLModel):
    data: List[RowForMLInternal]


class MLModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    model_name: str
    model_url: AnyHttpUrl
    created_dt: datetime = Field(default_factory=datetime.utcnow)


class MLModelCreate(SQLModel):
    model_name: str = Field(sa_column=Column("model_name", String, unique=True))
    model_url: AnyHttpUrl = Field(sa_column=Column("model_url", String, unique=True))


class MLModelRead(SQLModel):
    id: int
    model_name: str
    created_dt: datetime = Field(default_factory=datetime.utcnow)


class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ml_model_id: int = Field(default=None, foreign_key="mlmodel.id")
    result_id: int = Field(default=None, foreign_key="resultsubmission.id")
    predicted_goal_diff: int
    created_dt: datetime = Field(default_factory=datetime.utcnow)