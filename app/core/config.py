# from typing import List, Union
# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env", env_ignore_empty=True, extra="ignore"
#     )

#     PROJECT_NAME: str = "AI Weather Care"
#     VERSION: str = "1.0.0"
#     API_V1_STR: str = "/api/v1"

#     BACKEND_CORS_ORIGINS: List[str] = ["*"]
        
#     # Database
#     DATABASE_URL: str

#     # JWT
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
#     REFRESH_TOKEN_EXPIRE_DAYS: int = 7

#     # Rate Limit
#     RATE_LIMITING_ENABLED: bool = True
#     REDIS_URL: str = "redis://localhost:6379/0"

#     # API Keys
#     OPENWEATHERMAP_API_KEY: str = ""
#     GEMINI_API_KEY: str = ""
#     GOOGLE_CLIENT_ID: str = ""

#     # Email
#     SMTP_TLS: bool = True
#     SMTP_PORT: int = 587
#     SMTP_HOST: str = "smtp.gmail.com"
#     SMTP_USER: str = ""
#     SMTP_PASSWORD: str = ""
#     EMAILS_FROM_EMAIL: str = ""

# settings = Settings()




from typing import List, Union, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str = "AI Weather Care"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    BACKEND_CORS_ORIGINS: List[str] = ["*"]
        
    # --- Database Settings ---
    # These match your individual environment keys
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_PORT: str = "5432"
    
    # This becomes optional in the config because we can auto-build it
    DATABASE_URL: Optional[str] = None

    # --- Automatically Build DATABASE_URL if missing ---
    @model_validator(mode="after")
    def assemble_db_connection(self) -> "Settings":
        if not self.DATABASE_URL:
            if all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_SERVER, self.POSTGRES_DB]):
                self.DATABASE_URL = (
                    f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                    f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
                )
        
        if self.DATABASE_URL:
            # Handle 'postgres://' (common in Render/Heroku) and 'postgresql://' for asyncpg
            if self.DATABASE_URL.startswith("postgres://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
            elif self.DATABASE_URL.startswith("postgresql://") and not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            
            # Ensure ssl=require is added for Render/Production if not already present
            if "ssl=" not in self.DATABASE_URL:
                separator = "&" if "?" in self.DATABASE_URL else "?"
                self.DATABASE_URL += f"{separator}ssl=require"
            
        print(f"--- DEBUG: CONNECTING TO DATABASE WITH URL: {self.DATABASE_URL} ---")
        return self

    # --- JWT ---
    SECRET_KEY: str = "fallback_temporary_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Rate Limit ---
    # Disabled by default so it doesn't crash on Render without a Redis container
    RATE_LIMITING_ENABLED: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- API Keys ---
    OPENWEATHERMAP_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""

    # --- Email ---
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = ""

settings = Settings()