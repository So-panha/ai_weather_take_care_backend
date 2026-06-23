from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db
from app.models.user import User, Role
from app.schemas.token import TokenPayload
from app.core.exceptions import UnauthorizedException, ForbiddenException

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise UnauthorizedException("Could not validate credentials")
    except JWTError:
        raise UnauthorizedException("Could not validate credentials")
    
    user = await session.get(User, int(token_data.sub))
    if not user:
        raise UnauthorizedException("User not found")
    if user.is_deleted:
        raise UnauthorizedException("Inactive user")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_admin(current_user: CurrentUser) -> User:
    if current_user.role != Role.ADMIN:
        raise ForbiddenException("The user doesn't have enough privileges")
    return current_user

CurrentAdmin = Annotated[User, Depends(get_current_admin)]
