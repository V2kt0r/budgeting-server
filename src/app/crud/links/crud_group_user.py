from fastcrud import FastCRUD

from ...models.links.group_user import GroupUser
from ...schemas.links.group_user import (
    GroupUserCreateInternal,
    GroupUserDelete,
    GroupUserUpdate,
    GroupUserUpdateInternal,
)

CRUDGroupUser = FastCRUD[
    GroupUser,
    GroupUserCreateInternal,
    GroupUserUpdate,
    GroupUserUpdateInternal,
    GroupUserDelete,
]
crud_group_user = CRUDGroupUser(GroupUser)
