from pydantic import BaseModel

from .purchase_category import PurchaseCategoryRead


class PurchaseCategoryStatisticsItem(BaseModel):
    purchase_category: PurchaseCategoryRead
    item_count: int
    total: float


class PurchaseCategoryStatistics(BaseModel):
    items: list[PurchaseCategoryStatisticsItem]
    item_count: int
    total: float
