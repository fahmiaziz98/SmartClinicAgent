from typing import List
from pathlib import Path
from functools import lru_cache
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
    CALENDER_ID: str
    SERVICE_ACCOUNT_FILE: str
    SCOPES_CALENDER: List[str] = ["https://www.googleapis.com/auth/calendar"] 
    GOOGLE_APPLICATION_CREDENTIALS: str = str(BASE_DIR / SERVICE_ACCOUNT_FILE)
    
    # StorageConfiguration 
    FAISS_INDEX: str = str(BASE_DIR / "fais_index")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create save directory if it doesn't exist
        Path(self.FAISS_INDEX).mkdir(exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()