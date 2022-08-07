from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class UserRating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    rating_defence: float
    rating_offence: float
    latest_result_at_update_id: Optional[int] = Field(default=None, foreign_key="resultsubmission.id")
    created_dt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="ratings")

    def get_new_rating(self, rating_delta_defence: float = 0, rating_delta_offence: float = 0) -> "UserRatingBase":
        return UserRatingCreate(
            user_id=self.user_id,
            rating_defence=self.rating_defence + rating_delta_defence,
            rating_offence=self.rating_offence + rating_delta_offence
        )


class UserRatingBase(SQLModel):
    user_id: int
    rating_defence: float
    rating_offence: float
    latest_result_at_update_id: Optional[int]


class UserRatingCreate(UserRatingBase):
    pass


class UserRatingRead(UserRatingBase):
    id: int
    created_dt: datetime