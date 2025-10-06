import pandas as pd
import numpy as np

def calculate_p_buy(sell_orders: pd.DataFrame) -> float:
    """
    Calculates P_buy, the 7-day average of the lowest 10% of sell orders.
    """
    if sell_orders.empty:
        return 0.0

    # Get the lowest 10% of sell orders
    lowest_10_percent = sell_orders[sell_orders['price'] <= sell_orders['price'].quantile(0.1)]

    # Calculate the average price of these orders
    return lowest_10_percent['price'].mean()

def calculate_p_sell(buy_orders: pd.DataFrame) -> float:
    """
    Calculates P_sell, the 7-day average of the highest 10% of buy orders.
    """
    if buy_orders.empty:
        return 0.0

    # Get the highest 10% of buy orders
    highest_10_percent = buy_orders[buy_orders['price'] >= buy_orders['price'].quantile(0.9)]

    # Calculate the average price of these orders
    return highest_10_percent['price'].mean()

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

def calculate_avg_daily_volume(orders: pd.DataFrame, days: int) -> float:
    """
    Calculates the average daily volume over a given number of days.
    """
    if orders.empty:
        return 0.0
    total_volume = orders['volume_remain'].sum()
    return total_volume / days

def calculate_volatility(orders: pd.DataFrame) -> float:
    """
    Calculates the price volatility (standard deviation of daily price changes).
    """
    if orders.empty:
        return 0.0
    # This is a simplified approach. A more accurate calculation would require daily price data.
    # For now, we'll use the standard deviation of all order prices.
    return orders['price'].std()

def calculate_rank_score(roi_percent: float, avg_daily_volume: float) -> float:
    """
    Calculates the rank score.
    """
    return roi_percent * np.log(1 + avg_daily_volume)