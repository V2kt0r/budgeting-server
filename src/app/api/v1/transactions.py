import uuid as uuid_pkg
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import (
    DuplicateValueException,
    ForbiddenException,
    NotFoundException,
)
from ...crud.crud_groups import crud_groups
from ...schemas.group import Group as GroupSchema
from ...schemas.transaction import TransactionCreate, TransactionRead
from ...schemas.user import User as UserSchema
from ..dependencies import get_current_user

router = APIRouter(tags=["transactions"])


@router.post("/transaction", response_model=TransactionRead, status_code=201)
async def write_transaction(
    *,
    request: Request,
    transaction_create: TransactionCreate,
    group_uuid: Annotated[
        uuid_pkg.UUID | None,
        Query(
            title="Group UUID",
            description="The UUID of the group that the transaction belongs to. Leave it empty if the transaction is personal",
        ),
    ] = None,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> Any:
    group: GroupSchema | None = None
    if group_uuid is not None:
        group = await crud_groups.get(
            db=db,
            return_as_model=True,
            schema_to_select=GroupSchema,
            uuid=group_uuid,
            is_deleted=False,
        )
        if group is None:
            raise NotFoundException("Group not found")

        # TODO: check if current user belongs to the group
        # TODO: add the transaction to the group

    # TODO: add the transaction to the user
