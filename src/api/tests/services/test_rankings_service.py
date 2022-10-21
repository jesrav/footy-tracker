import pytest

from api.models.rating import UserRating
from api.services.ranking import calculate_rankings


@pytest.mark.asyncio
async def test_calculate_rankings():
    latest_ratings = [
        UserRating(
            user_id=1,
            rating_defence=1500,
            rating_offence=1700,
            overall_rating=1600,
            latest_result_at_update_id=2,
        ),
        UserRating(
            user_id=2,
            rating_defence=1400,
            rating_offence=1400,
            overall_rating=1400,
            latest_result_at_update_id=2,
        ),
        UserRating(
            user_id=3,
            rating_defence=1800,
            rating_offence=1500,
            overall_rating=1700,
            latest_result_at_update_id=2,
        ),
        UserRating(
            user_id=4,
            rating_defence=1500,
            rating_offence=1200,
            overall_rating=1350,
            latest_result_at_update_id=2,
        ),
    ]
    assert await calculate_rankings(latest_ratings, rating_type="overall") == {1: 2, 3: 1, 2: 3, 4: 4}, \
        "Rankings not correct for overall"
    assert await calculate_rankings(latest_ratings, rating_type="defence") == {1: 2, 3: 1, 2: 4, 4: 3}, \
        "Rankings not correct for defence"
    assert await calculate_rankings(latest_ratings, rating_type="offence") == {1: 1, 3: 2, 2: 3, 4: 4}, \
        "Rankings not correct for offence"
