from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Banco e IA
    SUPABASE_URL: str
    SUPABASE_KEY: str
    GEMINI_API_KEY: str

    # Nova Infra: Z-API
    ZAPI_INSTANCE_ID: str
    ZAPI_INSTANCE_TOKEN: str
    ZAPI_CLIENT_TOKEN: str  # Se você estiver usando segurança extra

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()