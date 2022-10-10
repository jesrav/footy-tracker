from pydantic import AnyHttpUrl, BaseSettings, validator
from typing import List, Union


class Settings(BaseSettings):
    DEV_MODE: bool = True
    BLOB_STORAGE_BASE_URL: str
    BLOB_PROFILE_IMAGE_CONTAINER: str = "profileimages"
    BLOB_STORAGE_CON_STR: str
    BASE_WEB_API_URL: str

    class Config:
        case_sensitive = True


settings = Settings()

