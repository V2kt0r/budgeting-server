from fastcrud import FastCRUD

from ...models.links.transaction_receipt import TransactionReceipt
from ...schemas.links.transaction_receipt import (
    TransactionReceiptCreateInternal,
    TransactionReceiptDelete,
    TransactionReceiptUpdate,
    TransactionReceiptUpdateInternal,
)

CRUDTransactionReceipt = FastCRUD[
    TransactionReceipt,
    TransactionReceiptCreateInternal,
    TransactionReceiptUpdate,
    TransactionReceiptUpdateInternal,
    TransactionReceiptDelete,
]
crud_transaction_receipt = CRUDTransactionReceipt(TransactionReceipt)
