from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from models.user import UserReadUnauthorized


class UserRating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    rating_defence: float
    rating_offence: float
    overall_rating: float
    latest_result_at_update_id: Optional[int] = Field(default=None, foreign_key="resultsubmission.id")
    created_dt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="ratings")

    # add this so that it can be accessed
    __mapper_args__ = {"eager_defaults": True}

    async def get_new_rating(self, rating_delta_defence: float = 0, rating_delta_offence: float = 0) -> "UserRatingBase":
        return UserRatingCreate(
            user_id=self.user_id,
            rating_defence=self.rating_defence + rating_delta_defence,
            rating_offence=self.rating_offence + rating_delta_offence,
            overall_rating=(
               self.rating_defence + rating_delta_defence
               + self.rating_offence + rating_delta_offence
           ) / 2
        )


class UserRatingCreate(SQLModel):
    user_id: int
    rating_defence: float
    rating_offence: float
    overall_rating: float
    latest_result_at_update_id: Optional[int]


class UserRatingRead(SQLModel):
    id: int
    user: UserReadUnauthorized
    rating_defence: float
    rating_offence: float
    overall_rating: float
    latest_result_at_update_id: Optional[int]
    created_dt: datetime
