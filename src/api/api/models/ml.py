from datetime import datetime
from typing import Union, List, Optional

from pydantic import AnyHttpUrl, root_validator
from sqlalchemy import Column, Integer, ForeignKey
from sqlmodel import SQLModel, Field, Relationship


class RowForML(SQLModel):
    result_to_predict: bool
    result_id: Union[int, None]
    result_dt: Union[datetime, None]
    result_approved: Union[bool, None]
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
    """Internally a row for the ML data also has an attribute that indicates if the teams have been switched,
    meaning that team1 and team2 are switched."""
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
    predictions: "Prediction" = Relationship(
        sa_relationship_kwargs={
            "cascade": "all, delete",  # Instruct the ORM how to track changes to local objects
        },
    )


class MLModelCreate(SQLModel):
    model_name: str
    model_url: AnyHttpUrl


class MLModelUpdate(SQLModel):
    model_name: Optional[str]
    model_url: Optional[AnyHttpUrl]

    @root_validator(pre=False)
    def one_value_must_be_changed(cls, values):
        model_name = values.get('model_name')
        model_url = values.get('model_url')
        if not model_name and not model_url:
            raise ValueError('At least one of model_name or model_url must be changed.')
        return values


class MLModelRead(SQLModel):
    id: int
    model_name: str
    user_id: int
    created_dt: datetime = Field(default_factory=datetime.utcnow)


class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ml_model_id: int = Field(
        default=None, sa_column=Column(Integer, ForeignKey("mlmodel.id", ondelete="CASCADE"))
    )
    result_id: int = Field(default=None, foreign_key="resultsubmission.id")
    predicted_goal_diff: float
    created_dt: datetime = Field(default_factory=datetime.utcnow)
    result: "ResultSubmission" = Relationship()


class PredictionRead(SQLModel):
    id: int
    ml_model_id: int
    result_id: int
    predicted_goal_diff: float
    created_dt: datetime
    result_goal_diff: Optional[float]


class MLMetric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prediction_id: int
    result_id: int
    ml_model_id: int
    prediction_dt: datetime
    result_goal_diff: int
    predicted_goal_diff: float
    rolling_short_window_mae: float
    rolling_long_window_mae: float
