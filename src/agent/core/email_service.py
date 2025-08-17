import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from loguru import logger

from agent.model.models_email import (CancelAppointment, SendAppointment,
                                      UpdateAppointment)
from agent.setting import settings

from .template_email import EmailContent, EmailTemplates


class GmailServiceSMTP:
    """
    Gmail SMTP service for sending emails.
    """

    def __init__(self):
        self.email = settings.ACCOUNT_GMAIL
        self.app_password = settings.PASSWORD_GMAIL
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT

    def send_email(self, content: EmailContent) -> Dict[str, Any]:
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{content.sender_name} <{self.email}>"
            msg["To"] = ", ".join(content.recipients)
            msg["Subject"] = content.subject

            # Add HTML and plain text parts
            text_part = MIMEText(content.text_body, "plain", "utf-8")
            html_part = MIMEText(content.html_body, "html", "utf-8")

            msg.attach(text_part)
            msg.attach(html_part)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.app_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {content.recipients}")
            return {"success": True, "message": "Email sent successfully"}

        except Exception as e:
            logger.error(f"Gmail SMTP error: {e}")
            return {"success": False, "message": f"Failed to send email: {str(e)}"}

    async def async_send_email(self, content: EmailContent) -> Dict[str, Any]:
        # TODO: Implement asynchronous email sending using a library like aiosmtplib
        raise NotImplementedError("Asynchronous email sending is not yet implemented.")


class EmailNotificationService:
    """Main email service with provider switching"""

    def __init__(self):
        self.primary_provider = GmailServiceSMTP()
        logger.info("Email service initialized")

    def send_appointment_created(self, data: SendAppointment) -> Dict[str, Any]:
        """Send appointment confirmation email"""
        template = EmailTemplates.appointment_created(
            data.patient_name,
            data.event_id,
            data.appointment_datetime,
            data.appointment_type,
            data.duration,
            data.location,
        )

        template.recipients = [data.patient_email]

        result = self.primary_provider.send_email(template)
        return result

    def send_appointment_updated(self, data: UpdateAppointment) -> Dict[str, Any]:
        """Send appointment update email"""
        template = EmailTemplates.appointment_updated(
            data.patient_name,
            data.title,
            data.new_datetime,
            data.description,
            data.location,
        )
        template.recipients = [data.patient_email]
        return self.primary_provider.send_email(template)

    def send_appointment_cancelled(self, data: CancelAppointment) -> Dict[str, Any]:
        """Send appointment cancellation email"""
        template = EmailTemplates.appointment_cancelled(
            data.patient_name,
            data.event_id,
            data.appointment_datetime,
            data.appointment_type,
            data.reason,
        )
        template.recipients = [data.patient_email]
        return self.primary_provider.send_email(template)


EMAIL_SERVICE: EmailNotificationService = EmailNotificationService()
