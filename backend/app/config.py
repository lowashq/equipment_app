from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    keycloak_url: str
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str = ""

    decision_engine_url: str

    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
