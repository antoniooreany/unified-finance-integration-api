from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    provider_base_url: str = "http://localhost:5000"
    provider_api_key: str = "test-api-key-not-a-secret"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
