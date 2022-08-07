from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from models.user import UserRead


class UserRating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    rating: float
    latest_result_at_update_id: Optional[int] = Field(default=None, foreign_key="resultsubmission.id")
    created_dt: Optional[datetime] = Field(default_factory=datetime.utcnow)

    user: "User" = Relationship(back_populates="ratings")

    def get_new_rating(self, rating_delta: float) -> "UserRatingBase":
        return UserRatingCreate(
            user_id=self.user_id,
            rating=self.rating + rating_delta
        )


class UserRatingBase(SQLModel):
    user_id: int
    rating: float
    latest_result_at_update_id: Optional[int]


class UserRatingCreate(UserRatingBase):
    pass


class UserRatingRead(SQLModel):
    id: int
    user: UserRead
    rating: float
    latest_result_at_update_id: Optional[int]
    created_dt: datetime
