import pytz
from datetime import datetime
from typing import Any, Dict

from googleapiclient.errors import HttpError
from src.agent.core import CALENDAR_SERVICE
from src.agent.setting import settings
from src.agent.utils import format_event_details


def create_event(
    title: str,
    start_datetime: datetime,
    end_datetime: datetime,
    description: str = '',
    location: str = '',
    timezone: str = 'Asia/Jakarta'
) -> Dict[str, Any]:
    """
    Creates a new event in Google Calendar.

    This function constructs and executes a request to the Google Calendar API
    to create a new event with the provided details.

    Args:
        title: The title of the event.
        start_datetime: The start date and time of the event.
        end_datetime: The end date and time of the event.
        description: An optional description for the event.
        location: An optional location for the event.
        timezone: The timezone for the event's start and end times.

    Returns:
        A dictionary containing the operation status and event details:
        - success (bool): True if the event was created successfully, False otherwise.
        - event (Dict | None): Formatted details of the created event, or None on failure.
        - event_id (str | None): The unique ID of the created event, or None on failure.
        - message (str): A status message describing the outcome.
    """
    try:
        tz = pytz.timezone(timezone)
        start_datetime = tz.localize(start_datetime)
        end_datetime = tz.localize(end_datetime)

        event_body = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': timezone},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': timezone},
        }

        event = CALENDAR_SERVICE.events().insert(
            calendarId=settings.CALENDAR_ID,
            body=event_body
        ).execute()

        formatted_event = format_event_details(event)

        return {
            'success': True,
            'event': formatted_event,
            'event_id': event.get('id'),
            'message': f'Event "{title}" was created successfully.'
        }

    except HttpError as error:
        return {
            'success': False,
            'event': None,
            'event_id': None,
            'message': f'An error occurred while creating the event: {error}'
        }
    