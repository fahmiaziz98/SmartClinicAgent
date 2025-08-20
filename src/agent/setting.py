"""Application settings for the agent."""

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import model_validator
from pydantic_settings import BaseSettings

_ = load_dotenv(find_dotenv())


class Settings(BaseSettings):
    """
    Manages application-wide settings using Pydantic's BaseSettings.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    GOOGLE_API_KEY: str
    
    # Mem0 API key
    MEM0_API_KEY: str

    # Gmail service
    ACCOUNT_GMAIL: str
    PASSWORD_GMAIL: str
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # Google Calendar
    CALENDAR_ID: str
    SERVICE_ACCOUNT_FILE: str
    SCOPES_CALENDER: List[str] = ["https://www.googleapis.com/auth/calendar"]
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None

    # Storage Configuration
    FAISS_INDEX: str = str(BASE_DIR / "fais_index")
    DOCS_PATH: str = str(BASE_DIR / "src" / "agent" / "docs")

    LANGSMITH_TRACING_V2: str
    LANGSMITH_PROJECT: str
    LANGSMITH_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @model_validator(mode="after")
    def set_google_credentials(self) -> "Settings":
        if self.SERVICE_ACCOUNT_FILE:
            self.GOOGLE_APPLICATION_CREDENTIALS = str(
                self.BASE_DIR / self.SERVICE_ACCOUNT_FILE
            )
        return self

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Path(self.FAISS_INDEX).mkdir(exist_ok=True)


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()


settings = get_settings()
