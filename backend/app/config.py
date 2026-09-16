from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://office:office@db:5432/office"
    jwt_secret: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    jwt_ttl_hours: int = 12
    office_tz: str = "Europe/Moscow"


settings = Settings()
