from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from app.repositories.user_repository import user_repository
from app.models.user import UserStatus
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.schemas.token import Token, GoogleToken
from app.core.config import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import uuid

class AuthService:
    def __init__(self):
        self.max_failed_attempts = 5

    async def authenticate(self, db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> Token:
        # form_data.username can be email or username
        user = await user_repository.get_by_email(db, email=form_data.username)
        if not user:
            user = await user_repository.get_by_username(db, username=form_data.username)
            
        if not user or user.is_deleted:
            raise UnauthorizedException("Incorrect username/email or password")
            
        if user.status == UserStatus.LOCKED:
            raise ForbiddenException("Account is locked due to multiple failed login attempts.")
        if user.status == UserStatus.INACTIVE:
            raise ForbiddenException("Account is inactive.")

        if not verify_password(form_data.password, user.hashed_password):
            attempts = user.failed_login_attempts + 1
            update_data = {"failed_login_attempts": attempts}
            if attempts >= self.max_failed_attempts:
                update_data["status"] = UserStatus.LOCKED
            await user_repository.update(db, db_obj=user, obj_in=update_data)
            await db.commit()
            raise UnauthorizedException("Incorrect username/email or password")

        # Reset failed attempts on success
        if user.failed_login_attempts > 0:
            await user_repository.update(db, db_obj=user, obj_in={"failed_login_attempts": 0})
            await db.commit()

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def google_login_or_register(self, db: AsyncSession, token_data: GoogleToken) -> Token:
        try:
            # Verify token with Google
            import logging
            logging.getLogger().info("Verifying Google token...")
            if not settings.GOOGLE_CLIENT_ID:
                raise UnauthorizedException("Google Auth is not configured on the server.")

            id_info = id_token.verify_oauth2_token(
                token_data.token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            email = id_info.get("email")
            if not email:
                raise UnauthorizedException("Invalid Google token: No email found.")
            
            # Check if user exists
            user = await user_repository.get_by_email(db, email=email)
            
            if not user:
                # Create user
                username = id_info.get("name") or email.split("@")[0]
                user_by_name = await user_repository.get_by_username(db, username=username)
                if user_by_name:
                    username = f"{username}_{str(uuid.uuid4())[:8]}"
                    
                create_data = {
                    "email": email,
                    "username": username,
                    "hashed_password": None
                }
                user = await user_repository.create(db, obj_in=create_data)
                await db.flush()
                await db.commit()
                await db.refresh(user)
            else:
                if user.is_deleted or user.status == UserStatus.INACTIVE:
                    raise ForbiddenException("Account disabled")
                if user.status == UserStatus.LOCKED:
                    raise ForbiddenException("Account is locked")
                    
            # Issue our JWT
            access_token = create_access_token(subject=user.id)
            refresh_token = create_refresh_token(subject=user.id)

            return Token(access_token=access_token, refresh_token=refresh_token)

        except ValueError as e:
            raise UnauthorizedException("Invalid Google token")

auth_service = AuthService()
