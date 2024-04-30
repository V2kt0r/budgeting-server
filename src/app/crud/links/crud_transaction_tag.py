from fastcrud import FastCRUD

from ...models.links.transaction_tag import TransactionTag
from ...schemas.links.transaction_tag import (
    TransactionTagCreateInternal,
    TransactionTagDelete,
    TransactionTagUpdate,
    TransactionTagUpdateInternal,
)

CRUDTransactionTag = FastCRUD[
    TransactionTag,
    TransactionTagCreateInternal,
    TransactionTagUpdate,
    TransactionTagUpdateInternal,
    TransactionTagDelete,
]
crud_transaction_tag = CRUDTransactionTag(TransactionTag)
