import pytest

from api.services.security import get_password_hash, verify_password


def test_hash_and_verify_password():
    hashed_password = get_password_hash("my_little_secret")

    assert hashed_password != "my_little_secret", "Hashed password should not be the same as the plain password"
    assert verify_password("my_little_secret", hashed_password), "Password verification does not work"
    pytest.raises(ValueError, verify_password, "my_little_secret", "not_the_hashed_password")
