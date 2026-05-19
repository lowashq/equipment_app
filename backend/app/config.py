from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    keycloak_url: str
    keycloak_public_url: str = "http://localhost:8080"
    keycloak_realm: str
    keycloak_client_id: str
    keycloak_client_secret: str = ""
    keycloak_redirect_uri: str = "http://localhost:8000/auth/keycloak/callback"
    keycloak_frontend_redirect_uri: str = "http://localhost:3000/auth/callback"

    decision_engine_url: str

    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str

    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
