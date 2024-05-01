from fastcrud import FastCRUD

from ...models.links.user_transaction import UserTransaction
from ...schemas.links.user_transaction import (
    UserTransactionCreateInternal,
    UserTransactionDelete,
    UserTransactionUpdate,
    UserTransactionUpdateInternal,
)

CRUDUserTransaction = FastCRUD[
    UserTransaction,
    UserTransactionCreateInternal,
    UserTransactionUpdate,
    UserTransactionUpdateInternal,
    UserTransactionDelete,
]
crud_user_transaction = CRUDUserTransaction(UserTransaction)
