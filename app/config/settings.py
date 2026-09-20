from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database Configuration
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    # JWT Security Configuration (Loaded securely from .env - no hardcoding)
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        safe_password = quote_plus(self.db_password)
        return (
            f"postgresql+psycopg2://{self.db_user}:{safe_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
