from sendgrid.helpers.mail import Mail, From
from sendgrid import SendGridAPIClient
import os

SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL")

def getSendGridClient() -> SendGridAPIClient:
    if not SENDGRID_API_KEY:
        raise RuntimeError("SENDGRID_API_KEY not configured")

    return SendGridAPIClient(SENDGRID_API_KEY)

def send_template_email(
    to_email: str,
    template_id: str,
    dynamic_data: dict,
):
    """
    Send email using SendGrid Dynamic Template
    """

    message = Mail(
        from_email=From(
            email=SENDGRID_FROM_EMAIL,
        ),

        to_emails=to_email,
    )

    message.template_id = template_id
    message.dynamic_template_data = dynamic_data

    try:
        sg = getSendGridClient()
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        raise RuntimeError(f"SendGrid error: {str(e)}")
