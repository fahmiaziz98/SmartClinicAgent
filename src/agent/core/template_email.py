from dataclasses import dataclass
from datetime import datetime
from typing import List

from src.agent.model.models_email import (CancelAppointment, SendAppointment, 
                                          UpdateAppointment)


@dataclass
class EmailContent:
    """Email content structure"""

    subject: str
    html_body: str
    text_body: str
    recipients: List[str]
    sender_name: str = "Dr. Fahmi Clinic"


class EmailTemplates:
    """Professional email templates for appointments"""

    @staticmethod
    def appointment_created(data: SendAppointment) -> EmailContent:
        subject = f"✅ Appointment Confirmed - Klinik Sehat Bersama"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; }}
                .appointment-details {{ background: white; padding: 15px; border-left: 4px solid #4CAF50; }}
                .event-id {{
                    font-size: 1.5em;
                    font-weight: bold;
                    background: #fffae6;
                    padding: 10px;
                    border: 2px dashed #FFA500;
                    text-align: center;
                    user-select: all;
                    margin: 10px 0;
                }}
                .note {{
                    font-size: 0.9em;
                    color: #d35400;
                    font-style: italic;
                    margin-top: 5px;
                    text-align: center;
                }}
                .footer {{ background: #333; color: white; padding: 15px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🩺 Klinik Sehat Bersama</h1>
                    <h2>Appointment Confirmation</h2>
                </div>

                <div class="content">
                    <h3>Dear {data.patient_name},</h3>
                    <p>Your appointment has been successfully scheduled!</p>

                    <h4>📌 Your Event ID:</h4>
                    <div class="event-id">{data.event_id}</div>
                    <div class="note">Remember this Event ID, it will be required for confirmation or schedule changes.</div>

                    <div class="appointment-details">
                        <h4>📅 Appointment Details:</h4>
                        <ul>
                            <li><strong>Date & Time:</strong> {data.appointment_datetime}</li>
                            <li><strong>Type:</strong> {data.appointment_type}</li>
                            <li><strong>Duration:</strong> {data.duration} minutes</li>
                            <li><strong>Location:</strong> {data.location}</li>
                            <li><strong>Doctor:</strong> Dr. Fahmi</li>
                        </ul>
                    </div>

                    <h4>📝 Important Notes:</h4>
                    <ul>
                        <li>Please arrive 10 minutes early</li>
                        <li>Bring your ID and insurance card</li>
                        <li>If you need to reschedule, contact us at least 24 hours in advance</li>
                    </ul>

                    <h4>📞 Contact Information:</h4>
                    <p>Phone: +62 21 1234 5678<br>
                    Email: info@drfahmiclinic.com<br>
                    WhatsApp: +62 812 3456 7890</p>
                </div>

                <div class="footer">
                    <p>Klinik Sehat Bersama | Jl. Merdeka No. 123, Jakarta Pusat | www.drfahmiclinic.com</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Klinik Sehat Bersama - Appointment Confirmation

        Dear {data.patient_name},

        Your appointment has been successfully scheduled!

        📌 EVENT ID: {data.event_id}
        (Remember this Event ID, it will be required for confirmation or schedule changes.)

        APPOINTMENT DETAILS:
        • Date & Time: {data.appointment_datetime}
        • Type: {data.appointment_type}
        • Duration: {data.duration} minutes
        • Location: {data.location}
        • Doctor: Dr. Fahmi

        IMPORTANT NOTES:
        • Please arrive 10 minutes early
        • Bring your ID and insurance card
        • Contact us 24 hours in advance for rescheduling

        CONTACT:
        Phone: +62 21 1234 5678
        Email: info@drfahmiclinic.com

        Thank you!
        Klinik Sehat Bersama
        """

        return EmailContent(
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            recipients=[],
            sender_name="Alicia Clinical Assistant",
        )

    @staticmethod
    def appointment_updated(data: UpdateAppointment) -> EmailContent:
        subject = f"📅 Appointment Updated - Klinik Sehat Bersama"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #FF9800; color: white; padding: 20px; text-align: center;">
                    <h1>🩺 Klinik Sehat Bersama</h1>
                    <h2>Appointment Updated</h2>
                </div>

                <div style="background: #f9f9f9; padding: 20px;">
                    <h3>Dear {data.patient_name},</h3>
                    <p>Your appointment has been successfully updated!</p>

                    <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #FF9800;">
                        <h4>📅 Updated Details:</h4>
                        <p><strong>Summary:</strong> {data.title}</p>
                        <p><strong>New:</strong> {data.new_datetime}</p>
                        <p><strong>Description:</strong> {data.description}</p>
                        <p><strong>Location:</strong> {data.location}</p>
                    </div>

                    <p>If you have any questions, please contact us.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Klinik Sehat Bersama - Appointment Updated

        Dear {data.patient_name},

        Your appointment has been updated:

        Summary: {data.title}
        New Date: {data.new_datetime}
        Description: {data.description}
        Location: {data.location}

        Contact us if you have any questions.

        Klinik Sehat Bersama
        """

        return EmailContent(
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            recipients=[],
            sender_name="Alicia Clinical Assistance",
        )

    @staticmethod
    def appointment_cancelled(data: CancelAppointment) -> EmailContent:
        subject = f"❌ Appointment Cancelled - Klinik Sehat Bersama"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #f44336; color: white; padding: 20px; text-align: center;">
                    <h1>🩺 Klinik Sehat Bersama</h1>
                    <h2>Appointment Cancelled</h2>
                </div>

                <div style="background: #f9f9f9; padding: 20px;">
                    <h3>Dear {data.patient_name},</h3>
                    <p>Your appointment has been cancelled.</p>

                    <div style="background: #ffebee; padding: 15px; border-left: 4px solid #f44336;">
                        <h4>❌ Cancelled Appointment:</h4>
                        <p><strong>Event ID:</strong> {data.event_id}</p>
                        <p><strong>Date & Time:</strong> {data.appointment_datetime}</p>
                        <p><strong>Type:</strong> {data.appointment_type}</p>
                        <p><strong>Reason:</strong> {data.reason}</p>
                    </div>

                    <p>To reschedule, please contact us:</p>
                    <p>📞 Phone: +62 21 1234 5678<br>
                       📧 Email: info@drfahmiclinic.com</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Klinik Sehat Bersama - Appointment Cancelled

        Dear {data.patient_name},

        Your appointment has been cancelled:
        Event ID: {data.event_id}
        Date & Time: {data.appointment_datetime}
        Type: {data.appointment_type}
        "Reason: {data.reason}

        To reschedule, contact us:
        Phone: +62 21 1234 5678
        Email: info@drfahmiclinic.com

        Klinik Sehat Bersama
        """

        return EmailContent(
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            recipients=[],
            sender_name="Alicia Clinical Assistance",
        )
