import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from . import models

def calculate_p_buy(db: Session, item_id: int) -> float:
    """
    Calculates P_buy, the 7-day average of the lowest 10% of sell orders from the local DB.
    """
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    sell_orders_query = db.query(models.MarketHistory.sell_price).filter(
        models.MarketHistory.item_id == item_id,
        models.MarketHistory.date >= seven_days_ago,
        models.MarketHistory.sell_price.isnot(None)
    )

    sell_prices = [p[0] for p in sell_orders_query.all()]
    if not sell_prices:
        return 0.0

    prices_series = pd.Series(sell_prices)
    quantile_10 = prices_series.quantile(0.1)
    lowest_10_percent_prices = prices_series[prices_series <= quantile_10]

    return lowest_10_percent_prices.mean() if not lowest_10_percent_prices.empty else 0.0

def calculate_p_sell(db: Session, item_id: int) -> float:
    """
    Calculates P_sell, the 7-day average of the highest 10% of buy orders from the local DB.
    """
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    buy_orders_query = db.query(models.MarketHistory.buy_price).filter(
        models.MarketHistory.item_id == item_id,
        models.MarketHistory.date >= seven_days_ago,
        models.MarketHistory.buy_price.isnot(None)
    )

    buy_prices = [p[0] for p in buy_orders_query.all()]
    if not buy_prices:
        return 0.0

    prices_series = pd.Series(buy_prices)
    quantile_90 = prices_series.quantile(0.9)
    highest_10_percent_prices = prices_series[prices_series >= quantile_90]

    return highest_10_percent_prices.mean() if not highest_10_percent_prices.empty else 0.0

def calculate_profit_per_unit(p_sell: float, p_buy: float, tax_rate: float, broker_fee: float) -> float:
    """
    Calculates the profit per unit.
    """
    return p_sell - p_buy - (tax_rate * p_sell) - (broker_fee * p_sell)

def calculate_roi_percent(profit_per_unit: float, p_buy: float) -> float:
    """
    Calculates the return on investment (ROI) in percent.
    """
    if p_buy == 0:
        return 0.0
    return (profit_per_unit / p_buy) * 100

def calculate_avg_daily_volume(db: Session, item_id: int, days: int = 30) -> float:
    """
    Calculates the average daily volume over a given number of days from the local DB.
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=days)

    total_volume = db.query(func.sum(models.MarketHistory.volume)).filter(
        models.MarketHistory.item_id == item_id,
        models.MarketHistory.date >= thirty_days_ago
    ).scalar()

    return (total_volume / days) if total_volume else 0.0

def calculate_volatility(db: Session, item_id: int, days: int = 30) -> float:
    """
    Calculates the price volatility (standard deviation of daily average prices).
    """
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=days)

    prices = db.query(models.MarketHistory.sell_price).filter(
        models.MarketHistory.item_id == item_id,
        models.MarketHistory.date >= thirty_days_ago,
        models.MarketHistory.sell_price.isnot(None)
    ).all()

    if not prices or len(prices) < 2:
        return 0.0

    price_series = pd.Series([p[0] for p in prices])
    return price_series.std()

def calculate_rank_score(roi_percent: float, avg_daily_volume: float) -> float:
    """
    Calculates the rank score.
    """
    return roi_percent * np.log(1 + avg_daily_volume)