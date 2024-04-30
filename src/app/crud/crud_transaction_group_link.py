from fastcrud import FastCRUD

from ..models.transaction_group_link import TransactionGroupLink
from ..schemas.transaction_group_link import (
    TransactionGroupLinkCreateInternal,
    TransactionGroupLinkDelete,
    TransactionGroupLinkUpdate,
    TransactionGroupLinkUpdateInternal,
)

CRUDTransactionGroupLink = FastCRUD[
    TransactionGroupLink,
    TransactionGroupLinkCreateInternal,
    TransactionGroupLinkUpdate,
    TransactionGroupLinkUpdateInternal,
    TransactionGroupLinkDelete,
]
crud_transaction_group_links = CRUDTransactionGroupLink(TransactionGroupLink)
