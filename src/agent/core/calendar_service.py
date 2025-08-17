from typing import Optional

from google.oauth2 import service_account
from googleapiclient.discovery import Resource, build
from loguru import logger

from src.agent.setting import settings


class GoogleCalendarService:
    """
    Singleton service for Google Calendar API operations.

    This service manages Google Calendar API authentication and provides
    a singleton pattern for efficient resource usage.
    """

    _instance: Optional["GoogleCalendarService"] = None
    _service: Optional[Resource] = None

    def __new__(cls) -> "GoogleCalendarService":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(GoogleCalendarService, cls).__new__(cls)
        return cls._instance

    def get_service(self) -> Resource:
        """
        Get or create Google Calendar service.

        Returns:
            Google Calendar API service instance.

        Raises:
            Exception: If service creation fails.
        """
        if self._service is not None:
            return self._service

        try:
            self._service = self._create_service()
            logger.info("Google Calendar service initialized successfully")
            return self._service
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            raise

    def _create_service(self) -> Resource:
        """Create Google Calendar service with credentials."""
        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_APPLICATION_CREDENTIALS, scopes=settings.SCOPES_CALENDER
        )
        return build("calendar", "v3", credentials=credentials)

    def reset_service(self):
        """Reset service instance (useful for testing)."""
        self._service = None


# create a global instance of the service
CALENDAR_SERVICE: GoogleCalendarService = GoogleCalendarService().get_service()
