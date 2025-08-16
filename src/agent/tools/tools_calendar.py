import pytz
from loguru import logger
from datetime import datetime
from typing import Any, Dict, Optional, List, Callable
from datetime import timedelta

from googleapiclient.errors import HttpError
from langchain_core.tools import tool

from .helper import create_event
from agent.hitl import human_in_the_loop
from src.agent.core import CALENDAR_SERVICE, EMAIL_SERVICE
from .schema import (
    InputGetDoctorSchedule,
    InputGetEventById,
    InputCreateAppointment,
    InputUpdateAppointment,
    InputCancelAppointment,
)
from src.agent.setting import settings
from src.agent.utils import format_event, format_event_details


@tool("get_doctor_schedule_appointments", args_schema=InputGetDoctorSchedule, return_direct=True)
def get_doctor_schedule_appointments(
    start_datetime: datetime,
    end_datetime: datetime,
    max_results: int = 30,
) -> Dict[str, Any]:
    """
    Use this tool exclusively to retrieve the doctor’s appointment schedule,
    such as available dates and times.
    This tool is not intended for looking up patient records or personal details.
    Its primary purpose is to provide schedule information that can help patients choose a suitable time when creating a new appointment
    Args:
        start_datetime: The start time for searching events.
        end_datetime: The end time for searching events.
        max_results: The maximum number of events to return.

    Returns:
        Dict containing:
        - success: Boolean operation status
        - events: List of events
        - count: Number of events found
        - message: Status message
    """
    try:
        logger.info("Using tools get_doctor_schedule_appointments")
        # Format time to ISO format
        time_min_iso = start_datetime.isoformat() + 'Z'
        time_max_iso = end_datetime.isoformat() + 'Z'

        event_results = CALENDAR_SERVICE.events().list(
            calendarId=settings.CALENDAR_ID,
            timeMin=time_min_iso,
            timeMax=time_max_iso,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = event_results.get('items', [])
        formatted_events = [format_event(event) for event in events]

        logger.success("Succesfully get events...")
        return {
            'success': True,
            'events': formatted_events,
            'count': len(formatted_events),
            'message': f'Succes retrieve {len(formatted_events)} event'
        }

    except HttpError as error:
        logger.error(f"Error in get_doctor_schedule_appointments: {error}")
        return {
            'success': False,
            'events': [],
            'count': 0,
            'message': f'Error event: {error}'
        }
    
@tool("get_event_by_id", args_schema=InputGetEventById, return_direct=True)
def get_event_by_id(event_id: str) -> Dict[str, Any]:
    """
    Use this tool when the user requests to search for an event by ID.
    It retrieves all available details for the specified event.

    Args:
        event_id: ID of the event to retrieve

    Returns:
        Dict containing:
        - Success: Boolean the status of the operation
        - event: Full event details
        - message: Status message
    """
    try:
        logger.info("Using tool get_event_by_id")

        event = CALENDAR_SERVICE.events().get(
            calendarId=settings.CALENDAR_ID,
            eventId=event_id
        ).execute()

        formatted_event = format_event_details(event)
        logger.success("Succesfully get_event_by_id...")

        return {
            'success': True,
            'event': formatted_event,
            'message': 'Succesfully get events'
        }

    except HttpError as error:
        logger.error(f"Error in get_event_by_id: {error}")
        return {
            'success': False,
            'event': None,
            'message': f'Error get event: {error}'
        }
    
@tool("create_doctor_appointment", args_schema=InputCreateAppointment, return_direct=True)
def create_doctor_appointment(
    patient_name: str,
    patient_email: str,
    appointment_datetime: datetime,
    duration_minutes: int = 30,
    appointment_type: str = "Consultation",
    symptoms: Optional[str] = "",
    notes: Optional[str] = "",
    phone_number: Optional[str] = ""
):
    """
    Use this tool to create an appointment with a doctor.
    This tool is specifically designed for managing doctor appointment creation

    Args:
        patient_name: Name of the patient
        patient_email: Email of the patient
        appointment_datetime: Date and time of the appointment
        duration_minutes: Duration of the appointment in minutes
        appointment_type: Type of the appointment
        symptoms: Symptoms of the patient
        notes: Notes for the appointment
        phone_number: Phone number of the patient

    Returns:
        Dict contains:
        - success: Boolean operation status
        - message: Status message
    """
    try:
        logger.info("Using tools create_doctor_appointment...")

        end_datetime = appointment_datetime + timedelta(minutes=duration_minutes)
        timezone = "Asia/Jakarta"

        title = f"[{appointment_type}] {patient_name}"
        description = [
            f"Patient Name: {patient_name}",
            f"Patient Email: {patient_email}",
            f"Duration: {duration_minutes} minutes",
            f"Appointment Type: {appointment_type}"
        ]
        if symptoms:
            description.append(f"Symptoms: {symptoms}")
        if notes:
            description.append(f"Notes: {notes}")
        if phone_number:
            description.append(f"Phone Number: {phone_number}")

        descriptions = "\n".join(description)

        result = create_event(
            title=title,
            start_datetime=appointment_datetime,
            end_datetime=end_datetime,
            description=descriptions,
            location="Klinik Sehat Bersama, Jl. Merdeka No. 123, Jakarta Pusat",
            timezone=timezone
        )

        if result['success']:
            EMAIL_SERVICE.send_appointment_created(
                event_id=result['event_id'],
                patient_name=patient_name,
                patient_email=patient_email,
                appointment_datetime=appointment_datetime.strftime('%d %B %Y, %H:%M WIB'),
                appointment_type=appointment_type,
                duration=duration_minutes,
                location="Klinik Sehat Bersama, Jl. Merdeka No. 123, Jakarta Pusat"
            )

            return {
                'success': True,
                'event_id': result['event_id'],
                'message': f"✅ Appointment created and confirmation email sent to {patient_email}!"
            }

    except Exception as error:
        logger.error(f"Error in create_doctor_appointment: {error}")
        return {
            'success': False,
            'event_id': None,
            'message': f'❌ Error creating appointment: {str(error)}'
        }
    
@tool("update_doctor_appointment", args_schema=InputUpdateAppointment, return_direct=True)
def update_doctor_appointment(
    event_id: str,
    patient_name: str,    
    patient_email: str,   
    title: Optional[str] = None,
    start_datetime: Optional[datetime] = None,
    end_datetime: Optional[datetime] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Use this tool to update an existing appointment in Google Calendar.
    Only the specified fields will be updated;
    all other fields will remain unchanged.

    Args:
        event_id: ID of the event to be updated
        title: New title (optional)
        start_datetime: New start time (optional)
        end_datetime: New end time (optional)
        description: New description (optional)
        location: New location (optional)
        attendees: List of new attendees (optional)

    Returns:
        Dict contains:
        - success: Boolean the status of the operation
        - Event: Event details after update
        - message: Status message
    """
    try:
        logger.info("Using tools update_doctor_appointment...")
        timezone = "Asia/Jakarta"
        tz = pytz.timezone(timezone)


        existing_event = CALENDAR_SERVICE.events().get(
            calendarId=settings.CALENDAR_ID,
            eventId=event_id
        ).execute()

        # Update field yang diberikan
        if title is not None:
            existing_event['summary'] = title
        if description is not None:
            existing_event['description'] = description
        if location is not None:
            existing_event['location'] = location
        if start_datetime is not None:
            start_datetime = tz.localize(start_datetime)
            existing_event['start'] = {
                'dateTime': start_datetime.isoformat(),
                'timeZone': timezone,
            }
        if end_datetime is not None:
            end_datetime = tz.localize(end_datetime)
            existing_event['end'] = {
                'dateTime': end_datetime.isoformat(),
                'timeZone': timezone,
            }

        # Update event
        updated_event = CALENDAR_SERVICE.events().update(
            calendarId=settings.CALENDAR_ID,
            eventId=event_id,
            body=existing_event
        ).execute()

        formatted_event = format_event_details(updated_event)
        logger.success("Success update appointment...")
        if formatted_event:
            EMAIL_SERVICE.send_appointment_updated(
                patient_name=patient_name,
                patient_email=patient_email,
                title=formatted_event['title'],
                new_datetime=formatted_event['start_time'],
                description=formatted_event['description'],
                location=formatted_event['location']
            )

        return {
            'success': True,
            'message': f'appointment "{event_id}" successfully update'
        }

    except HttpError as error:
        logger.error(f"Error update_doctor_appointment: {error}")
        return {
            'success': False,
            'message': f'Error update appointment: {error}'
        }
    
@tool("cancel_doctor_appointment", args_schema=InputCancelAppointment, return_direct=True)
def cancel_doctor_appointment(
    event_id: str,
    reason: str,
    patient_name: str,
    patient_email: str,
    appointment_datetime: datetime,
    appointment_type: str
) -> Dict[str, Any]:
    """
    Use this tool to Delete an event from Google Calendar.
    This tool will permanently remove the event from the calendar.
    All participants will be notified of the event cancellation.

    Args:
        event_id: ID of the event to be deleted
        reason: Reason for deleting the event
        patient_name: Name of the patient
        patient_email: Email of the patient
        appointment_datetime: Date and time of the appointment
        appointment_type: Type of the appointment

    Returns:
        Dict containing:
        - Success: Boolean the status of the operation
        - Message: Status message
    """
    try:
        logger.info("Using tools cancel_doctor_appointment...")
        _ = CALENDAR_SERVICE.events().delete(
            calendarId=settings.CALENDAR_ID,
            eventId=event_id
        ).execute()

        logger.success("Success delete appointment...")
        EMAIL_SERVICE.send_appointment_cancelled(
            patient_name=patient_name,
            event_id=event_id,
            patient_email=patient_email,
            appointment_datetime=appointment_datetime.strftime('%d %B %Y, %H:%M WIB'),
            appointment_type=appointment_type,
            reason=reason
        )
        return {
            'success': True,
            'message': f'Appointment "{event_id}" success deleted'
        }

    except HttpError as error:
        logger.error(f"Error cancel_doctor_appointment: {error}")
        return {
            'success': False,
            'message': f'Error delete appointment: {error}'
        }
    

# Register sensitif tool
HITL_CREATE_APPOINTMENT = human_in_the_loop(create_doctor_appointment)
HITL_UPDATE_APPOINTMENT = human_in_the_loop(update_doctor_appointment)
HITL_CANCEL_APPOINTMENT = human_in_the_loop(cancel_doctor_appointment)

TOOLS_CALENDAR: List[Callable[..., Any]] = [
    get_doctor_schedule_appointments,
    get_event_by_id,

    # sensitif tools
    HITL_CREATE_APPOINTMENT,
    HITL_UPDATE_APPOINTMENT,
    HITL_CANCEL_APPOINTMENT
]