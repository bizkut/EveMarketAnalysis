import requests
import pandas as pd
import bz2
import io
import logging
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from sqlalchemy import desc
from . import models
import urllib.parse

EVEREF_MARKET_ORDERS_URL = "https://data.everef.net/market-orders"
logger = logging.getLogger(__name__)

def get_historical_market_orders(db: Session, region_id: int):
    """
    Fetches historical market order data for a given region,
    starting from the last processed file date and skipping files that have already been processed.
    """
    all_orders = []
    base_history_url = f"{EVEREF_MARKET_ORDERS_URL}/history/"

    last_processed_file = db.query(models.ProcessedFile).order_by(desc(models.ProcessedFile.file_date)).first()
    start_date = (last_processed_file.file_date + timedelta(days=1)) if last_processed_file else datetime.now(timezone.utc) - timedelta(days=30)

    days_to_fetch = (datetime.now(timezone.utc) - start_date).days + 1

    for i in range(days_to_fetch):
        date = start_date + timedelta(days=i)
        if date > datetime.now(timezone.utc):
            continue

        date_str = date.strftime("%Y-%m-%d")
        year_str = date.strftime("%Y")

        dir_url = urllib.parse.urljoin(base_history_url, f"{year_str}/{date_str}/")

        try:
            logger.info(f"Fetching directory listing from {dir_url}")
            dir_response = requests.get(dir_url)
            dir_response.raise_for_status()

            soup = BeautifulSoup(dir_response.content, 'html.parser')
            links = [a['href'] for a in soup.find_all('a') if a['href'].endswith('.v3.csv.bz2')]

            if not links:
                logger.warning(f"No data files found for {date_str}")
                continue

            for link in links:
                processed_file_entry = db.query(models.ProcessedFile).filter_by(filename=link).first()
                if processed_file_entry:
                    logger.info(f"Skipping already processed file: {link}")
                    continue

                file_url = urllib.parse.urljoin(dir_url, link)

                logger.info(f"Fetching historical market orders from {file_url}")
                response = requests.get(file_url, stream=True)
                response.raise_for_status()

                decompressed_data = bz2.decompress(response.content)
                df = pd.read_csv(io.BytesIO(decompressed_data))
                df = df[df['region_id'] == region_id]
                all_orders.append(df)

                processed_file = models.ProcessedFile(filename=link, file_date=date)
                db.add(processed_file)
                db.commit()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"No data found for {date_str} at URL {dir_url}")
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