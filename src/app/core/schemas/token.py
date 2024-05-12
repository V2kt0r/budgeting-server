from datetime import datetime

from pydantic import BaseModel

from .mixins import TimestampSchema


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username_or_email: str


class TokenBlacklistBase(BaseModel):
    token: str
    expires_at: datetime


class TokenBlacklist(TimestampSchema, TokenBlacklistBase):
    pass


class TokenBlacklistCreate(TokenBlacklistBase):
    pass


class TokenBlacklistUpdate(TokenBlacklistBase):
    pass
