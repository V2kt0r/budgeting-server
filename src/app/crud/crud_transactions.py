from fastcrud import FastCRUD

from ..models.transaction import Transaction
from ..schemas.transaction import (
    TransactionCreateInternal,
    TransactionDelete,
    TransactionUpdateInternal,
    TransactionUpdate,
)

CRUDTransaction = FastCRUD[
    Transaction,
    TransactionCreateInternal,
    TransactionUpdate,
    TransactionUpdateInternal,
    TransactionDelete,
]
crud_transactions = CRUDTransaction(Transaction)
