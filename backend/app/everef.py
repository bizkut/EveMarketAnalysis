import requests
import pandas as pd
import bz2
import io
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

EVEREF_MARKET_ORDERS_URL = "https://data.everef.net/market-orders"
logger = logging.getLogger(__name__)

def get_latest_market_orders(region_id: int):
    """
    Fetches the latest market order snapshot from Everef, filters it by region,
    and returns it as a pandas DataFrame.
    """
    url = f"{EVEREF_MARKET_ORDERS_URL}/market-orders-latest.v3.csv.bz2"
    try:
        logger.info(f"Fetching latest market orders from {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        decompressed_data = bz2.decompress(response.content)
        df = pd.read_csv(io.BytesIO(decompressed_data))
        df = df[df['region_id'] == region_id]
        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching latest market orders from Everef: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred while processing Everef data: {e}")
        return None

def get_historical_market_orders(region_id: int, days: int):
    """
    Fetches historical market order data for a given region and number of days.
    """
    all_orders = []
    base_history_url = f"{EVEREF_MARKET_ORDERS_URL}/history"

    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        year_str = date.strftime("%Y")

        dir_url = f"{base_history_url}/{year_str}/{date_str}/"

        try:
            logger.info(f"Fetching directory listing from {dir_url}")
            dir_response = requests.get(dir_url)
            dir_response.raise_for_status()

            soup = BeautifulSoup(dir_response.content, 'html.parser')
            links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.v3.csv.bz2')]

            if not links:
                logger.warning(f"No data files found for {date_str}")
                continue

            latest_file_path = links[-1]

            # The hrefs can be relative or absolute, so we need to handle both cases.
            if latest_file_path.startswith('/'):
                file_url = f"https://data.everef.net{latest_file_path}"
            else:
                file_url = f"{dir_url}{latest_file_path}"

            logger.info(f"Fetching historical market orders from {file_url}")
            response = requests.get(file_url, stream=True)
            response.raise_for_status()

            decompressed_data = bz2.decompress(response.content)
            df = pd.read_csv(io.BytesIO(decompressed_data))
            df = df[df['region_id'] == region_id]
            all_orders.append(df)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"No data found for {date_str} at URL {file_url}")
                continue
            else:
                logger.error(f"HTTP error fetching historical directory from Everef: {e}")
                continue
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching historical market orders from Everef: {e}")
            continue
        except Exception as e:
            logger.error(f"An error occurred while processing Everef data: {e}")
            continue

    if not all_orders:
        return None

    return pd.concat(all_orders, ignore_index=True)