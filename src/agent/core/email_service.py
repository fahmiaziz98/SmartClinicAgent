import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from loguru import logger
from datetime import datetime
from typing import Dict, Any
from .template_email import EmailContent, EmailTemplates
from src.agent.setting import settings


class GmailServiceSMTP:
    """
    Gmail SMTP service for sending emails.
    """
    def __init__(self):
        self.email = settings.ACCOUNT_GMAIL
        self.app_password = settings.PASSWORD_GMAIL
        self.smtp_server = settings.SMPT_SERVER
        self.smtp_port = settings.SMPT_PORT

    def send_email(self, content: EmailContent) -> Dict[str, Any]:
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{content.sender_name} <{self.email}>"
            msg['To'] = ", ".join(content.recipients)
            msg['Subject'] = content.subject

            # Add HTML and plain text parts
            text_part = MIMEText(content.text_body, 'plain', 'utf-8')
            html_part = MIMEText(content.html_body, 'html', 'utf-8')

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

    def send_appointment_created(
        self,
        event_id: str,
        patient_name: str,
        patient_email: str,
        appointment_datetime: datetime,
        appointment_type: str,
        duration: int,
        location: str
    ) -> Dict[str, Any]:
        """Send appointment confirmation email"""
        template = EmailTemplates.appointment_created(
                patient_name,
                event_id,
                appointment_datetime,
                appointment_type,
                duration,
                location
        )

        template.recipients = [patient_email]

        result = self.primary_provider.send_email(template)
        return result

    def send_appointment_updated(self,
        patient_name: str,
        title: str,
        patient_email: str,
        new_datetime: datetime,
        description: str,
        location: str
    ) -> Dict[str, Any]:
        """Send appointment update email"""
        template = EmailTemplates.appointment_updated(
            patient_name,
            title,
            new_datetime,
            description,
            location
        )
        template.recipients = [patient_email]
        return self.primary_provider.send_email(template)

    def send_appointment_cancelled(
        self,
        patient_name: str,
        event_id: str,
        patient_email: str,
        appointment_datetime: datetime,
        appointment_type: str,
        reason: str = ""
    ) -> Dict[str, Any]:
        """Send appointment cancellation email"""
        template = EmailTemplates.appointment_cancelled(
            patient_name, event_id, appointment_datetime, appointment_type, reason
        )
        template.recipients = [patient_email]
        return self.primary_provider.send_email(template)


email_service: EmailNotificationService = EmailNotificationService()