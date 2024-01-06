from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = Field(..., validation_alias="ENV")

    POSTGRES_USER: str = Field(..., validation_alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., validation_alias="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(..., validation_alias="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(..., validation_alias="POSTGRES_PORT")
    POSTGRES_DB: str = Field(..., validation_alias="POSTGRES_DB")

    GCP_SERVICE_ACCOUNT_FILEPATH: str = Field(
        ..., validation_alias="GCP_SERVICE_ACCOUNT_FILEPATH"
    )

    AUTH_SECRET_KEY: str = Field(..., validation_alias="AUTH_SECRET_KEY")
    AUTH_ALGORITHM: str = Field(..., validation_alias="AUTH_ALGORITHM")
    AUTH_TOKEN_EXPIRE_MIN: int = Field(..., validation_alias="AUTH_TOKEN_EXPIRE_MIN")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )


settings = Settings()
