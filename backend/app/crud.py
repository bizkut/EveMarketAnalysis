from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import pandas as pd
import logging
from . import models, schemas, everef, calculations, esi, ml
from .config import settings
from .database import SessionLocal, engine

logger = logging.getLogger(__name__)

def get_or_create_item(db: Session, type_id: int):
    """
    Gets an item from the database or creates it if it doesn't exist.
    The item name is fetched from the ESI API if the item is created.
    """
    item = db.query(models.Item).filter(models.Item.type_id == type_id).first()
    if not item:
        name = esi.get_type_name(type_id)
        item = models.Item(type_id=type_id, name=name)
        db.add(item)
        db.commit()
        db.refresh(item)
    return item

def update_market_history(db: Session, region_id: int):
    """
    Fetches new market order data from Everef and inserts it into the database.
    """
    logger.info("Fetching new market data...")
    new_orders = everef.get_historical_market_orders(db, region_id)

    if new_orders is None or new_orders.empty:
        logger.info("No new market data found.")
        return

    logger.info(f"Found {len(new_orders)} new market orders to process.")

    new_orders['issued'] = pd.to_datetime(new_orders['issued'])

    item_cache = {}
    history_to_insert = []

    unique_type_ids = [int(tid) for tid in new_orders['type_id'].unique()]
    for type_id in unique_type_ids:
        if type_id not in item_cache:
            item_cache[type_id] = get_or_create_item(db, type_id)

    for _, row in new_orders.iterrows():
        type_id = int(row['type_id'])
        item = item_cache.get(type_id)

        if item:
            history_to_insert.append({
                'item_id': item.id,
                'date': row['issued'],
                'buy_price': row['price'] if row['is_buy_order'] else None,
                'sell_price': row['price'] if not row['is_buy_order'] else None,
                'volume': row['volume_remain']
            })

    if history_to_insert:
        logger.info(f"Bulk inserting {len(history_to_insert)} market history records.")
        db.bulk_insert_mappings(models.MarketHistory, history_to_insert)
        db.commit()

    logger.info("Market history update complete.")

def train_all_models(db: Session):
    """
    Trains the generalized price prediction model.
    """
    logger.info("Training generalized price prediction model...")
    ml.train_generalized_model(db)
    logger.info("Model training complete.")

def update_item_calculations_and_predictions(db: Session, tax_rate: float, broker_fee: float):
    """
    Calculates profitability metrics and predicts next-day prices for all items.
    """
    logger.info("Updating item calculations and predictions...")

    predictions = ml.predict_prices(db)

    items = db.query(models.Item).all()

    for item in items:
        p_buy = calculations.calculate_p_buy(db, item.id)
        p_sell = calculations.calculate_p_sell(db, item.id)

        if p_buy == 0 or p_sell == 0:
            logger.warning(f"Skipping item {item.name} (ID: {item.type_id}) due to missing buy or sell price data.")
            continue

        profit_per_unit = calculations.calculate_profit_per_unit(p_sell, p_buy, tax_rate, broker_fee)
        roi_percent = calculations.calculate_roi_percent(profit_per_unit, p_buy)
        avg_daily_volume = calculations.calculate_avg_daily_volume(db, item.id)
        volatility = calculations.calculate_volatility(db, item.id)
        rank_score = calculations.calculate_rank_score(roi_percent, avg_daily_volume)

        predicted_sell_price, confidence_score = predictions.get(item.type_id, (None, None))

        item.buy_price = p_buy
        item.sell_price = p_sell
        item.profit_per_unit = profit_per_unit
        item.roi_percent = roi_percent
        item.avg_daily_volume = avg_daily_volume
        item.volatility = volatility
        item.rank_score = rank_score
        item.predicted_sell_price = predicted_sell_price
        item.confidence_score = confidence_score

        db.add(item)

    db.commit()
    logger.info("Item calculations and predictions update complete.")

def populate_regions(db: Session):
    """
    Populates the regions table with data from the ESI API.
    """
    logger.info("Populating regions table...")
    region_ids = esi.get_regions()
    for region_id in region_ids:
        region_info = esi.get_region_info(region_id)
        if region_info:
            region = models.Region(
                region_id=region_id,
                name=region_info['name']
            )
            db.merge(region)
    db.commit()
    logger.info("Regions table populated.")

def populate_categories(db: Session):
    """
    Populates the categories table with data from the ESI API.
    """
    logger.info("Populating categories table...")
    category_ids = esi.get_item_categories()
    for category_id in category_ids:
        category_info = esi.get_item_category_info(category_id)
        if category_info:
            category = models.Category(
                category_id=category_id,
                name=category_info['name']
            )
            db.merge(category)
    db.commit()
    logger.info("Categories table populated.")

def update_all_item_data(db: Session, region_id: int, train_models: bool = False, tax_rate: float = settings.TAX_RATE, broker_fee: float = settings.BROKER_FEE):
    """
    Orchestrates the entire data refresh process.
    """
    update_market_history(db, region_id)
    if train_models:
        train_all_models(db)
    update_item_calculations_and_predictions(db, tax_rate=tax_rate, broker_fee=broker_fee)