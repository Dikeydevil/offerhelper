from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql://offerhelper:offerhelper@localhost:5433/offerhelper"
    )

    GIGACHAT_AUTH_KEY: str

    # JWT
    JWT_SECRET_KEY: str = "super-secret-key-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
