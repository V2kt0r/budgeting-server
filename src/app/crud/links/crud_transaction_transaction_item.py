from fastcrud import FastCRUD

from ...models.links.transaction_transaction_item import (
    TransactionTransactionItem,
)
from ...schemas.links.transaction_transaction_item import (
    TransactionTransactionItemCreateInternal,
    TransactionTransactionItemDelete,
    TransactionTransactionItemUpdate,
    TransactionTransactionItemUpdateInternal,
)

CRUDTransactionTransactionItem = FastCRUD[
    TransactionTransactionItem,
    TransactionTransactionItemCreateInternal,
    TransactionTransactionItemUpdate,
    TransactionTransactionItemUpdateInternal,
    TransactionTransactionItemDelete,
]
crud_transaction_transaction_item = CRUDTransactionTransactionItem(
    TransactionTransactionItem
)
