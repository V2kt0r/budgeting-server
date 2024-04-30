from fastcrud import FastCRUD

from ...models.links.transaction_item_tag import TransactionItemTag
from ...schemas.links.transaction_item_tag import (
    TransactionItemTagCreateInternal,
    TransactionItemTagDelete,
    TransactionItemTagUpdate,
    TransactionItemTagUpdateInternal,
)

CRUDTransactionItemTag = FastCRUD[
    TransactionItemTag,
    TransactionItemTagCreateInternal,
    TransactionItemTagUpdate,
    TransactionItemTagUpdateInternal,
    TransactionItemTagDelete,
]
crud_transaction_item_tag = CRUDTransactionItemTag(TransactionItemTag)
