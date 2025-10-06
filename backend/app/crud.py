from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import pandas as pd
import logging
from . import models, schemas, everef, calculations, esi
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

def update_all_item_data(db: Session, region_id: int, days: int = 30):
    """
    Fetches historical market data, calculates profitability metrics for each item,
    and updates the database.
    """
    logger.info("Starting data refresh process.")
    logger.info(f"Fetching historical market data for the last {days} days...")
    historical_data = everef.get_historical_market_orders(region_id, days=days)

    if historical_data is None or historical_data.empty:
        logger.error("Failed to fetch historical market data or no data was returned.")
        return

    # Convert 'issued' column to datetime objects once
    historical_data['issued'] = pd.to_datetime(historical_data['issued'])

    type_ids = historical_data['type_id'].unique()
    logger.info(f"Found {len(type_ids)} unique items to process.")

    for i, type_id_np in enumerate(type_ids):
        type_id = int(type_id_np)
        logger.info(f"Processing item {i+1}/{len(type_ids)}: type_id {type_id}")

        item_orders = historical_data.loc[historical_data['type_id'] == type_id].copy()

        # Ensure timezone-aware comparison
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        seven_day_orders = item_orders.loc[item_orders['issued'] >= seven_days_ago]

        sell_orders = seven_day_orders.loc[seven_day_orders['is_buy_order'] == False]
        buy_orders = seven_day_orders.loc[seven_day_orders['is_buy_order'] == True]

        p_buy = calculations.calculate_p_buy(sell_orders)
        p_sell = calculations.calculate_p_sell(buy_orders)

        if p_buy == 0 or p_sell == 0:
            logger.warning(f"Skipping type_id {type_id} due to missing buy or sell price data in the last 7 days.")
            continue

        profit_per_unit = calculations.calculate_profit_per_unit(p_sell, p_buy, settings.TAX_RATE, settings.BROKER_FEE)
        roi_percent = calculations.calculate_roi_percent(profit_per_unit, p_buy)
        avg_daily_volume = calculations.calculate_avg_daily_volume(item_orders, 30)
        volatility = calculations.calculate_volatility(item_orders)
        rank_score = calculations.calculate_rank_score(roi_percent, avg_daily_volume)

        item = get_or_create_item(db, type_id=type_id)
        item.buy_price = p_buy
        item.sell_price = p_sell
        item.profit_per_unit = profit_per_unit
        item.roi_percent = roi_percent
        item.avg_daily_volume = avg_daily_volume
        item.volatility = volatility
        item.rank_score = rank_score

        db.add(item)

    db.commit()
    logger.info("Database update complete.")
