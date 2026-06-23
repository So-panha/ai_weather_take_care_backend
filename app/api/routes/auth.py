from fastapi import APIRouter, Depends, status, Request, Body
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from app.api.deps import SessionDep, CurrentUser
from app.schemas.token import Token, GoogleToken
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.core.rate_limit import limiter
from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, db: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Supports email or username as the 'username' field.
    """
    return await auth_service.authenticate(db, form_data)

@router.post("/google", response_model=Token)
async def login_with_google(db: SessionDep, token_in: GoogleToken):
    """
    Authenticate user via Google ID Token.
    Registers the user if they don't exist.
    """
    return await auth_service.google_login_or_register(db, token_in)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(db: SessionDep, user_in: UserCreate):
    """
    Register a new user.
    """
    return await user_service.create_user(db, user_in)
    
@router.post("/logout")
async def logout(current_user: CurrentUser):
    """
    Logout the current user.
    """
    return {"message": "Successfully logged out. Please discard your token on client side."}

@router.post("/refresh", response_model=Token)
async def refresh_access_token(db: SessionDep, refresh_token: str = Body(..., embed=True)):
    """
    Use a valid refresh token to get a new access token and refresh token.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")
    except JWTError:
        raise UnauthorizedException("Invalid or expired refresh token")

    user = await db.get(User, int(user_id))
    if not user or user.is_deleted:
        raise UnauthorizedException("User not found")

    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)
    return Token(access_token=new_access_token, refresh_token=new_refresh_token)
