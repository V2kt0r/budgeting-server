from fastcrud import FastCRUD

from ...models.links.user_tag import UserTag
from ...schemas.links.user_tag import (
    UserTagCreateInternal,
    UserTagDelete,
    UserTagUpdate,
    UserTagUpdateInternal,
)

CRUDUserTag = FastCRUD[
    UserTag,
    UserTagCreateInternal,
    UserTagUpdate,
    UserTagUpdateInternal,
    UserTagDelete,
]
crud_user_tag = CRUDUserTag(UserTag)
