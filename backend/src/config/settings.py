from pydantic import Field
from pydantic_settings import BaseSettings ,SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    PUBLIC_BASE_URL: str

   
    COQUI_MODEL: str

    AUDIO_OUTPUT_DIR: str

    # ✅ REDIS
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_SESSION_TTL: int
    deepgram_api_key: str = Field(..., alias="DEEPGRAM_API_KEY")

    model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore"
)


settings = Settings()