from fastcrud import FastCRUD

from ..models.transaction_item import TransactionItem
from ..schemas.transaction_item import (
    TransactionItemCreateInternal,
    TransactionItemDelete,
    TransactionItemUpdateInternal,
    TransactionItemUpdate,
)

CRUDTransactionItem = FastCRUD[
    TransactionItem,
    TransactionItemCreateInternal,
    TransactionItemUpdate,
    TransactionItemUpdateInternal,
    TransactionItemDelete,
]
crud_transaction_item = CRUDTransactionItem(TransactionItem)
