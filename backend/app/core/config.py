from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "EcoSphere AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Compatibility properties for main.py
    PROJECT_NAME: str = "EcoSphere AI"
    API_V1_STR: str = "/api/v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
