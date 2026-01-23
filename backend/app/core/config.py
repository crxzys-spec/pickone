from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    database_url: str = "sqlite:///./app.db"
    environment: str = "development"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    upload_dir: str = "./uploads"
    upload_url_prefix: str = "/uploads"
    upload_base_url: str | None = None
    upload_max_mb: int = 10
    upload_token_ttl_minutes: int = 15
    rate_limit_login_per_minute: int = 10
    rate_limit_public_register_per_hour: int = 20
    rate_limit_public_upload_per_hour: int = 30


settings = Settings()
