from fastcrud import FastCRUD

from ..models.token_blacklist import TokenBlacklist
from ..schemas.token import TokenBlacklistCreate, TokenBlacklistUpdate

CRUDTokenBlacklist = FastCRUD[
    TokenBlacklist,
    TokenBlacklistCreate,
    TokenBlacklistUpdate,
    TokenBlacklistUpdate,
    None,
]
crud_token_blacklist = CRUDTokenBlacklist(TokenBlacklist)
