from typing import Annotated

from fastapi import APIRouter, Depends, Response
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import UnauthorizedException
from ...core.schemas.utils import Message
from ...core.security import blacklist_token, oauth2_scheme

router = APIRouter(tags=["login"])


@router.post("/logout", response_model=Message)
async def logout(
    response: Response,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Message:
    try:
        await blacklist_token(token=access_token, db=db)
        response.delete_cookie(key="refresh_token")

        return Message(message="Logged out successfully")

    except JWTError:
        raise UnauthorizedException("Invalid token.")
