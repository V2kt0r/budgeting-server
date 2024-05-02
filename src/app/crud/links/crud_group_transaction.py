from fastcrud import FastCRUD

from ...models.links.group_transaction import GroupTransaction
from ...schemas.links.group_transaction import (
    GroupTransactionCreateInternal,
    GroupTransactionDelete,
    GroupTransactionUpdate,
    GroupTransactionUpdateInternal,
)

CRUDGroupTransaction = FastCRUD[
    GroupTransaction,
    GroupTransactionCreateInternal,
    GroupTransactionUpdate,
    GroupTransactionUpdateInternal,
    GroupTransactionDelete,
]
crud_group_transactions = CRUDGroupTransaction(GroupTransaction)
