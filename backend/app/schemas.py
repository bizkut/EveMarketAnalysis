from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    type_id: int
    name: str
    buy_price: float
    sell_price: float
    profit_per_unit: float
    roi_percent: float
    avg_daily_volume: float
    volatility: float
    predicted_change_percent: Optional[float] = None
    confidence_score: Optional[float] = None

class ItemHistory(BaseModel):
    date: str
    price: float
    volume: int

class ItemDetail(BaseModel):
    item: Item
    history: List[ItemHistory]

class Region(BaseModel):
    region_id: int
    name: str

class Category(BaseModel):
    category_id: int
    name: str