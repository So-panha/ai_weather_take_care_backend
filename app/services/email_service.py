import logging

logger = logging.getLogger(__name__)

class EmailService:
    async def send_verification_email(self, email: str, token: str):
        # Mocking email sending
        logger.info(f"Mock email logic: Sending verification email to {email} with token {token}")

    async def send_password_reset_email(self, email: str, token: str):
        # Mocking email sending
        logger.info(f"Mock email logic: Sending password reset email to {email} with token {token}")

email_service = EmailService()
