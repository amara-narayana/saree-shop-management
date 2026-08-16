from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/saree_inventory"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Payment
    PAYMENT_PROVIDER: str = "test"
    PAYMENT_MODE: str = "test"
    PAYMENT_API_KEY: str = "test_api_key"
    PAYMENT_API_SECRET: str = "test_api_secret"
    PAYMENT_WEBHOOK_SECRET: str = "test_webhook_secret"
    
    # Application
    APP_NAME: str = "Saree Inventory Management System"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
