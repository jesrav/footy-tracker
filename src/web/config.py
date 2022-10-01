from pydantic import AnyHttpUrl, BaseSettings, validator
from typing import List, Union


class Settings(BaseSettings):
    BLOB_STORAGE_BASE_URL: str
    BLOB_PROFILE_IMAGE_CONTAINER: str = "profileimages"
    BLOB_STORAGE_CON_STR: str

    class Config:
        case_sensitive = True


settings = Settings()

