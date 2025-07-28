from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI RBAC App"
    debug: bool = False
    version: str = "1.0.0"

    database_url: str = "sqlite:///./app.db"

    # JWT
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: list = ["*"]

    first_superuser_username: str = "admin"
    first_superuser_email: str = "admin@example.com"
    first_superuser_password: str = "admin123"

    class Config:
        env_file = ".env"

settings = Settings()