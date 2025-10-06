from fastapi import APIRouter, HTTPException, Depends
from typing import List
import numpy as np
import logging
from sqlalchemy.orm import Session
from . import schemas, models, crud
from .database import get_db
from .config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/top-items", response_model=List[schemas.Item])
def get_top_items(region: str = "theforge", limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.Item).order_by(models.Item.rank_score.desc()).limit(limit).all()
    result = []
    for item in items:
        # The database may return byte strings for integers, so we need to handle that.
        type_id = item.type_id
        if isinstance(type_id, bytes):
            type_id = int.from_bytes(type_id, 'little')

        result.append({
            "type_id": type_id,
            "name": str(item.name),
            "buy_price": float(item.buy_price) if item.buy_price is not None else 0.0,
            "sell_price": float(item.sell_price) if item.sell_price is not None else 0.0,
            "profit_per_unit": float(item.profit_per_unit) if item.profit_per_unit is not None else 0.0,
            "roi_percent": float(item.roi_percent) if item.roi_percent is not None else 0.0,
            "avg_daily_volume": float(item.avg_daily_volume) if item.avg_daily_volume is not None else 0.0,
            "volatility": float(item.volatility) if item.volatility is not None else 0.0,
        })
    return result

@router.get("/item/{type_id}", response_model=schemas.ItemDetail)
def get_item(type_id: int, db: Session = Depends(get_db)):
    logger.info(f"get_item called with type_id: {type_id}")
    item = db.query(models.Item).filter(models.Item.type_id == type_id).first()
    logger.info(f"Database query result for item: {item}")
    if not item:
        logger.error(f"Item with type_id {type_id} not found in database.")
        raise HTTPException(status_code=404, detail="Item not found")

    history = db.query(models.MarketHistory).filter(models.MarketHistory.item_id == item.id).order_by(models.MarketHistory.date.desc()).all()
    history_data = [
        {"date": h.date.isoformat(), "price": h.sell_price, "volume": h.volume} for h in history
    ]

    item_type_id = item.type_id
    if isinstance(item_type_id, bytes):
        item_type_id = int.from_bytes(item_type_id, 'little')

    item_data = {
        "type_id": item_type_id,
        "name": str(item.name),
        "buy_price": float(item.buy_price) if item.buy_price is not None else 0.0,
        "sell_price": float(item.sell_price) if item.sell_price is not None else 0.0,
        "profit_per_unit": float(item.profit_per_unit) if item.profit_per_unit is not None else 0.0,
        "roi_percent": float(item.roi_percent) if item.roi_percent is not None else 0.0,
        "avg_daily_volume": float(item.avg_daily_volume) if item.avg_daily_volume is not None else 0.0,
        "volatility": float(item.volatility) if item.volatility is not None else 0.0,
    }

    return {"item": item_data, "history": history_data}

@router.get("/regions", response_model=List[schemas.Region])
def get_regions(db: Session = Depends(get_db)):
    # Placeholder data
    return [{"region_id": 10000002, "name": "The Forge"}]

@router.get("/categories", response_model=List[schemas.Category])
def get_categories(db: Session = Depends(get_db)):
    # Placeholder data
    return [{"category_id": 6, "name": "Ship"}]

@router.post("/refresh")
def refresh_data(db: Session = Depends(get_db)):
    crud.update_all_item_data(db, settings.REGION_ID)
    return {"message": "Data refresh complete."}