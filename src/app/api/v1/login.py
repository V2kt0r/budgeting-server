from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas.token import Token, TokenData, TokenPair
from ...core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from ...schemas.user import User

router = APIRouter(tags=["Login"])


@router.post("/login", response_model=TokenPair)
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TokenPair:
    user: User | None = await authenticate_user(
        username_or_email=form_data.username, password=form_data.password, db=db
    )
    if not user:
        raise UnauthorizedException("Wrong username, email or password.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = await create_refresh_token(data={"sub": user.username})

    return TokenPair(
        access_token=Token(access_token=access_token, token_type="bearer"),
        refresh_token=Token(access_token=refresh_token, token_type="bearer"),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh_access_token(
    *,
    request: Request,
    refresh_token: Token = Body(
        description="Refresh token.",
        examples=[
            Token(
                access_token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.1XZ8w3QbK4wYJH9n9Hw1dL6GQwH3d0xZD3bZ0qU9b0g",
                token_type="bearer",
            )
        ],
    ),
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> TokenPair:
    user_data: TokenData | None = await verify_token(
        refresh_token.access_token, db
    )
    if not user_data:
        raise UnauthorizedException("Invalid refresh token.")

    new_access_token = await create_access_token(
        data={"sub": user_data.username_or_email}
    )
    new_refresh_token = await create_refresh_token(
        data={"sub": user_data.username_or_email}
    )
    return TokenPair(
        access_token=Token(access_token=new_access_token, token_type="bearer"),
        refresh_token=Token(
            access_token=new_refresh_token, token_type="bearer"
        ),
    )
