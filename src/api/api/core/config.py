from pydantic import AnyHttpUrl, BaseSettings, validator
from typing import List, Union


class Settings(BaseSettings):

    # ML Settings
    N_HISTORICAL_ROWS_FOR_PREDICTION = 100
    METRICS_SHORT_WINDOW_SIZE = 20
    METRICS_LONG_WINDOW_SIZE = 100

    # Rating settings
    INITIAL_USER_RATING = 1500
    ELO_WIDTH = 400
    K_FACTOR = 60
    EGG_FACTOR = 1

    # JWT
    JWT_SECRET: str = "mysecret"
    ALGORITHM: str = "HS256"

    # OAUTH2
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/footy"

    ML_MODEL_URL: str = "model microservice url"

    class Config:
        case_sensitive = True


settings = Settings()
