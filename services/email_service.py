from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException, status
import ssl
import logging

from core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_verification_email(email: str, token: str):
        try:
            logger.info(f"Step 5: Preparing to send verification email to {email}")
            
            message = MIMEMultipart()
            message["From"] = settings.SMTP_SENDER
            message["To"] = email
            message["Subject"] = "Verify your email address"

            verification_link = f"{settings.BASE_URL}/api/auth/verify/{token}"
            body = f"""
            Welcome to our platform!
            
            Please verify your email address by clicking the link below:
            {verification_link}
            
            This link will expire in 24 hours.
            """
            message.attach(MIMEText(body, "plain"))

            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            logger.info(f"Step 6: Attempting SMTP connection to {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            
            async with SMTP(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                use_tls=True,  # Use SSL from the start
                tls_context=ssl_context,
                timeout=30
            ) as smtp:
                logger.info("Step 7: Attempting login...")
                await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                logger.info("Step 8: Sending message...")
                await smtp.send_message(message)
                
                logger.info("Step 9: Email sent successfully")

        except TimeoutError as e:
            logger.error(f"SMTP timeout error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email service timed out. Please try again later."
            )
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send verification email: {str(e)}"
            ) 