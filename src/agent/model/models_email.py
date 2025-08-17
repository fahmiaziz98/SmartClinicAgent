from dataclasses import dataclass


@dataclass
class SendAppointment:
    event_id: str
    patient_name: str
    patient_email: str
    appointment_datetime: str
    appointment_type: str
    duration: int
    location: str


@dataclass
class UpdateAppointment:
    patient_name: str
    patient_email: str
    title: str
    new_datetime: str
    description: str
    location: str


@dataclass
class CancelAppointment:
    patient_name: str
    patient_email: str
    event_id: str
    appointment_datetime: str
    appointment_type: str
    reason: str = ""
