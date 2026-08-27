from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "VoxShield AI Voice Security API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    MAX_UPLOAD_SIZE_MB: int = 15
    MIN_AUDIO_DURATION_SECONDS: float = 0.5

    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    REQUEST_TIMEOUT_SECONDS: int = 30

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://voxshield.vercel.app",
        "https://voxshield-frontend.vercel.app",
        "https://voxshield-git-feature-backend-ai-manu132005.vercel.app",
    ]

    LOG_LEVEL: str = "INFO"
    MODEL_PATH: str = "./models/anti_spoofing_resnet.pt"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
