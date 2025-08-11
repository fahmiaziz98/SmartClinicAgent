from typing import List, Optional
from pathlib import Path
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())


class Settings(BaseSettings):
    BASE_DIR : Path = Path(__file__).resolve().parent.parent.parent 
   
    # Gemini config
    GEMINI_API_KEY: str 
    GEMINI_MODEL_PRO : str = "gemini-2.5-pro"
    GEMINI_MODEL_FLASH : str = "gemini-2.5-flash"
    GEMINI_MODEL_LITE : str = "gemini-2.5-flash-lite"
    GEMINI_MODEL_STANDARD : str = "gemini-1.5-pro"
    TEMPERATURE: float = 1.0

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
    
    # StorageConfiguration 
    FAISS_INDEX: str = str(BASE_DIR / "fais_index")
    DOCS_PATH: str = str(BASE_DIR / "src" / "agent" / "docs")

    LANGSMITH_TRACING_V2: str
    LANGSMITH_PROJECT: str
    LANGSMITH_API_KEY: str
    

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @model_validator(mode='after')
    def set_google_credentials(self) -> 'Settings':
        if self.SERVICE_ACCOUNT_FILE:
            self.GOOGLE_APPLICATION_CREDENTIALS = str(self.BASE_DIR / self.SERVICE_ACCOUNT_FILE)
        return self

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create save directory if it doesn't exist
        Path(self.FAISS_INDEX).mkdir(exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()