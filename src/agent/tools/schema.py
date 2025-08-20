from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InputGetDoctorSchedule(BaseModel):
    """Input model for retrieving a list of events from Google Calendar"""

    start_datetime: datetime = Field(description="Start date and time to filter events (format: YYYY-MM-DD HH:MM:SS)")
    end_datetime: datetime = Field(description="End date and time to filter events (format: YYYY-MM-DD HH:MM:SS)")
    max_results: int = Field(
        default=30,
        description="Maximum number of events to retrieve (default: 10, maximum: 250)",
    )


class InputGetEventById(BaseModel):
    """Input model to retrieve event details by ID"""

    event_id: str = Field(description="Unique ID of the event to retrieve details")


class InputCreateAppointment(BaseModel):
    """Input model for appointment with doctor"""

    patient_name: str = Field(description="Patient Name")
    patient_email: str = Field(description="Email patient")
    appointment_datetime: datetime = Field(description="Appointment time (format: YYYY-MM-DD HH:MM:SS)")
    duration_minutes: int = Field(default=30, description="Duration appointment in minutes (default: 30 minutes)")
    appointment_type: str = Field(
        default="Consulation",
        description="Type of appointment (Consultation, Follow-up, Medical Check-up, dll)",
    )
    symptoms: Optional[str] = Field(default="", description="Patient Complaints or symptons")
    notes: Optional[str] = Field(default="", description="Notes for the appointment")
    phone_number: Optional[str] = Field(default="", description="Phone number of patient")


class InputUpdateAppointment(BaseModel):
    """Model input to update existing events"""

    event_id: str = Field(description="Unique event ID to be updated")
    patient_name: str = Field(description="New patient name or exiting")
    patient_email: str = Field(description="New patient email or exiting")
    title: Optional[str] = Field(
        default=None,
        description="New title for the event (optional, leave blank if not changed)",
    )
    start_datetime: Optional[datetime] = Field(default=None, description="New start time for event (optional)")
    end_datetime: Optional[datetime] = Field(default=None, description="New end time for event (optional)")
    description: Optional[str] = Field(default=None, description="New description for event (optional)")
    location: Optional[str] = Field(default=None, description="New location for the event (optional)")


class InputCancelAppointment(BaseModel):
    """Input model for deleting events from the calendar"""

    event_id: str = Field(description="Unique ID of the event to be deleted")
    reason: str = Field(description="Reason for deleting the event")
    patient_name: str = Field(description="Name of the patient")
    patient_email: str = Field(description="Email of the patient")
    appointment_datetime: datetime = Field(description="Date and time of the appointment")
    appointment_type: str = Field(description="Type of the appointment")


class InputKnowledgeBase(BaseModel):
    """Input model for querying the knowledge base."""

    query: str = Field(description="The query to be answered by the knowledge base.")
