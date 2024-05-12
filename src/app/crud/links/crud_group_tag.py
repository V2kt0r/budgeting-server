from fastcrud import FastCRUD

from ...models.links.group_tag import GroupTag
from ...schemas.links.group_tag import (
    GroupTagCreateInternal,
    GroupTagDelete,
    GroupTagUpdate,
    GroupTagUpdateInternal,
)

CRUDGroupTag = FastCRUD[
    GroupTag,
    GroupTagCreateInternal,
    GroupTagUpdate,
    GroupTagUpdateInternal,
    GroupTagDelete,
]
crud_group_tag = CRUDGroupTag(GroupTag)
