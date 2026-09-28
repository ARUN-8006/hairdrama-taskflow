import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .config import settings


def send_email(to_email: str, subject: str, body: str):
    required = [settings.GMAIL_SENDER, settings.GMAIL_REFRESH_TOKEN, settings.GMAIL_CLIENT_ID, settings.GMAIL_CLIENT_SECRET]
    if not all(required):
        # Local development can run without email credentials. Production should configure them.
        print(f"[EMAIL NOT CONFIGURED] to={to_email} subject={subject}")
        return

    creds = Credentials(
        token=None,
        refresh_token=settings.GMAIL_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GMAIL_CLIENT_ID,
        client_secret=settings.GMAIL_CLIENT_SECRET,
        scopes=["https://www.googleapis.com/auth/gmail.send"],
    )
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    message = EmailMessage()
    message["To"] = to_email
    message["From"] = settings.GMAIL_SENDER
    message["Subject"] = subject
    message.set_content(body)
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
