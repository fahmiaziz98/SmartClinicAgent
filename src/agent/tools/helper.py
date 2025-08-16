import pytz
from loguru import logger
from datetime import datetime, time, timedelta
from typing import Any, Dict

from googleapiclient.errors import HttpError
from src.agent.core import CALENDAR_SERVICE
from src.agent.setting import settings
from src.agent.utils import format_event_details


DOCTOR_SCHEDULE = {
    0: (time(16, 0), time(20, 0)),
    1: None,
    2: (time(16, 0), time(20, 0)),
    3: None,
    4: (time(16, 0), time(20, 0)),
    5: (time(8, 0), time(12, 0)),
    6: None,
}


class ScheduleValidationError(Exception):
    """Custom exception for schedule validation errors"""

    pass


def is_within_doctor_schedule(
    appointment_datetime: datetime, duration_minutes: int = 30
) -> bool:
    """
    Check if an appointment is within the doctor's schedule.

    Args:
        appointment_datetime: The datetime of the appointment.
        duration_minutes: The duration of the appointment in minutes.

    Returns:
        bool: True if the appointment is within the doctor's schedule, False otherwise.

    Raises:
        ValueError: If duration_minutes is not positive
        ScheduleValidationError: If appointment is outside schedule with detailed reason
    """
    logger.info(
        f"Checking appointment: {appointment_datetime} (duration: {duration_minutes}min)"
    )

    # Input validation
    if duration_minutes <= 0:
        raise ValueError("Duration must be positive")

    weekday = appointment_datetime.weekday()
    schedule = DOCTOR_SCHEDULE.get(weekday)

    if not schedule:
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        raise ScheduleValidationError(
            f"Doctor is not available on {day_names[weekday]}. "
            f"Available days: Monday, Wednesday, Friday (16:00-20:00), Saturday (08:00-12:00)"
        )

    start_time, end_time = schedule

    if appointment_datetime.tzinfo is not None:
        start_dt = datetime.combine(
            appointment_datetime.date(), start_time, tzinfo=appointment_datetime.tzinfo
        )
        end_dt = datetime.combine(
            appointment_datetime.date(), end_time, tzinfo=appointment_datetime.tzinfo
        )
    else:
        start_dt = datetime.combine(appointment_datetime.date(), start_time)
        end_dt = datetime.combine(appointment_datetime.date(), end_time)

    appointment_end = appointment_datetime + timedelta(minutes=duration_minutes)

    if appointment_datetime < start_dt:
        raise ScheduleValidationError(
            f"Appointment starts too early. "
            f"Doctor starts at {start_time.strftime('%H:%M')} WIB, "
            f"but appointment is at {appointment_datetime.strftime('%H:%M')}"
        )

    if appointment_datetime >= end_dt:
        raise ScheduleValidationError(
            f"Appointment starts too late. Doctor ends at {end_time.strftime('%H:%M')} WIB, "
            f"but appointment is at {appointment_datetime.strftime('%H:%M')}"
        )

    if appointment_end > end_dt:
        raise ScheduleValidationError(
            f"Appointment ends too late. "
            f"Doctor ends at {end_time.strftime('%H:%M')} WIB, "
            f"but {duration_minutes}-minute appointment would end "
            f"at {appointment_end.strftime('%H:%M')}"
        )


    logger.info("✅ Appointment is within doctor's schedule")
    return True


def create_event(
    title: str,
    start_datetime: datetime,
    end_datetime: datetime,
    description: str = "",
    location: str = "",
    timezone: str = "Asia/Jakarta",
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
            "summary": title,
            "description": description,
            "location": location,
            "start": {"dateTime": start_datetime.isoformat(), "timeZone": timezone},
            "end": {"dateTime": end_datetime.isoformat(), "timeZone": timezone},
        }

        event = (
            CALENDAR_SERVICE.events()
            .insert(
                calendarId=settings.CALENDAR_ID,
                body=event_body,
            )
            .execute()
        )


        formatted_event = format_event_details(event)

        return {
            "success": True,
            "event": formatted_event,
            "event_id": event.get("id"),
            "message": f'Event "{title}" was created successfully.',
        }

    except HttpError as error:
        return {
            "success": False,
            "event": None,
            "event_id": None,
            "message": f"An error occurred while creating the event: {error}",
        }
