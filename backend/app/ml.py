import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy.orm import Session
import joblib
from . import models
import os
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)
MODEL_DIR = "backend/models"
os.makedirs(MODEL_DIR, exist_ok=True)

def create_features(db: Session):
    """
    Creates a feature set for training the ML model.
    """
    logger.info("Creating features for ML model...")

    items = db.query(models.Item).all()
    if not items:
        logger.warning("No items found to create features for.")
        return None, None

    features = []
    targets = []

    for item in items:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

        history_30d = db.query(models.MarketHistory).filter(
            models.MarketHistory.item_id == item.id,
            models.MarketHistory.date >= thirty_days_ago
        ).all()

        history_7d = [h for h in history_30d if h.date >= seven_days_ago]

        if not history_30d or not history_7d:
            continue

        df_30d = pd.DataFrame([(h.date, h.sell_price, h.volume) for h in history_30d], columns=['date', 'price', 'volume']).dropna()
        df_7d = pd.DataFrame([(h.date, h.sell_price, h.volume) for h in history_7d], columns=['date', 'price', 'volume']).dropna()

        if df_30d.empty or df_7d.empty:
            continue

        # Create features
        avg_price_30d = df_30d['price'].mean()
        avg_price_7d = df_7d['price'].mean()
        volume_30d = df_30d['volume'].sum()
        volume_7d = df_7d['volume'].sum()
        price_volatility = df_30d['price'].std()

        # Create target
        # For simplicity, we'll try to predict the price 1 day in the future.
        # A more robust implementation would use a proper time-series approach.
        target_date = datetime.now(timezone.utc).date() + timedelta(days=1)
        target_history = db.query(models.MarketHistory.sell_price).filter(
            models.MarketHistory.item_id == item.id,
            func.date(models.MarketHistory.date) == target_date
        ).first()

        if target_history:
            features.append([
                item.type_id,
                avg_price_30d,
                avg_price_7d,
                volume_30d,
                volume_7d,
                price_volatility,
            ])
            targets.append(target_history[0])

    if not features:
        logger.warning("Could not generate any features.")
        return None, None

    X = pd.DataFrame(features, columns=['type_id', 'avg_price_30d', 'avg_price_7d', 'volume_30d', 'volume_7d', 'price_volatility'])
    y = pd.Series(targets)

    return X, y

def train_generalized_model(db: Session):
    """
    Trains a generalized price prediction model on all items and saves it to a file.
    """
    logger.info("Training generalized price prediction model...")
    X, y = create_features(db)

    if X is None or y is None or X.empty or y.empty:
        logger.error("Failed to create features for training.")
        return

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    model_path = f"{MODEL_DIR}/generalized_model.joblib"
    joblib.dump(model, model_path)
    logger.info(f"Generalized model saved to {model_path}")

def predict_prices(db: Session):
    """
    Predicts next-day prices for all items using the generalized model.
    """
    model_path = f"{MODEL_DIR}/generalized_model.joblib"
    if not os.path.exists(model_path):
        logger.warning("No trained generalized model found.")
        return {}

    model = joblib.load(model_path)

    X, _ = create_features(db)
    if X is None:
        logger.warning("Could not generate features for prediction.")
        return {}

    predictions = model.predict(X)

    # Get standard deviation of predictions from each tree as a confidence score
    individual_tree_predictions = np.array([tree.predict(X) for tree in model.estimators_])
    prediction_std_dev = np.std(individual_tree_predictions, axis=0)

    # Normalize the confidence score (lower std dev is better)
    confidence_scores = 1 - (prediction_std_dev / np.mean(predictions))

    # Create a dictionary of type_id -> (predicted_price, confidence_score)
    results = {}
    for index, row in X.iterrows():
        type_id = int(row['type_id'])
        results[type_id] = (predictions[index], confidence_scores[index])

    return results