from fastapi_mail import FastMail, MessageSchema
from typing import List
from pydantic import EmailStr
from app.core.config import MAIL_CONFIG

async def send_email(to: List[EmailStr], subject: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=to,
        body=body,
        subtype="html"
    )
    fm = FastMail(MAIL_CONFIG)
    await fm.send_message(message)
