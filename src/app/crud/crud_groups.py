from fastcrud import FastCRUD

from ..models.group import Group
from ..schemas.group import (
    GroupCreateInternal,
    GroupDelete,
    GroupUpdateInternal,
    GroupUpdate,
)

CRUDGroup = FastCRUD[
    Group,
    GroupCreateInternal,
    GroupUpdate,
    GroupUpdateInternal,
    GroupDelete,
]
crud_groups = CRUDGroup(Group)
