from typing import List, Optional
from pathlib import Path
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())


class Settings(BaseSettings):
    """
    Manages application-wide settings using Pydantic's BaseSettings.

    This class loads configuration from environment variables and a .env file,
    providing a centralized and type-safe way to access settings for various
    services like Gemini, Gmail, Google Calendar, and storage.

    Attributes:
        BASE_DIR (Path): The root directory of the project.
        GEMINI_API_KEY (str): API key for the Gemini service.
    """
    BASE_DIR : Path = Path(__file__).resolve().parent.parent.parent 

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
        """
        Dynamically sets the GOOGLE_APPLICATION_CREDENTIALS path.

        This validator runs after the model is initialized and constructs the
        full path to the service account file, making it available as an
        environment variable for Google Cloud libraries.

        Returns:
            The updated Settings instance.
        """
        if self.SERVICE_ACCOUNT_FILE:
            self.GOOGLE_APPLICATION_CREDENTIALS = str(self.BASE_DIR / self.SERVICE_ACCOUNT_FILE)
        return self

    def __init__(self, **kwargs):
        """
        Initializes the settings object.

        Ensures that the directory for the FAISS index is created if it
        does not already exist.
        """
        super().__init__(**kwargs)
        # Create save directory if it doesn't exist
        Path(self.FAISS_INDEX).mkdir(exist_ok=True)

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the Settings object.

    Using lru_cache ensures that the Settings class is instantiated only once,
    creating a singleton-like pattern. This is efficient as it avoids reloading
    the configuration on every import.

    Returns:
        The singleton Settings instance.
    """
    return Settings()

settings = get_settings()