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
            logger.info(f"Preparing to send verification email to {email}")
            
            message = MIMEMultipart("alternative")
            message["From"] = settings.SMTP_SENDER
            message["To"] = email
            message["Subject"] = "Verify your email address"

            verification_link = f"{settings.BASE_URL}/api/auth/verify/{token}"
            
            # Plain text version
            text = f"""
            Welcome to our platform!
            
            Please verify your email address by clicking the link below:
            {verification_link}
            
            This link will expire in 24 hours.
            """
            
            # HTML version
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #333;">Welcome to our platform!</h2>
                <p>Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 4px; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                <p style="color: #666; font-size: 12px;">
                    This link will expire in 24 hours. If you did not request this verification, 
                    please ignore this email.
                </p>
            </body>
            </html>
            """
            
            message.attach(MIMEText(text, "plain"))
            message.attach(MIMEText(html, "html"))

            # Create SSL context
            ssl_context = ssl.create_default_context()
            
            logger.info(f"Attempting SMTP connection to {settings.SMTP_HOST}:{settings.SMTP_PORT}")
            
            async with SMTP(
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                use_tls=True,
                tls_context=ssl_context,
                timeout=30
            ) as smtp:
                logger.info("Attempting login...")
                await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                logger.info("Sending message...")
                await smtp.send_message(message)
                
                logger.info("Email sent successfully")

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