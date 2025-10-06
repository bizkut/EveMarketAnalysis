from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer)
    buy_price = Column(Float, nullable=True)
    sell_price = Column(Float, nullable=True)
    profit_per_unit = Column(Float, nullable=True)
    roi_percent = Column(Float, nullable=True)
    avg_daily_volume = Column(Float, nullable=True)
    volatility = Column(Float, nullable=True)
    rank_score = Column(Float, nullable=True)
    predicted_sell_price = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    market_history = relationship("MarketHistory", back_populates="item", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="item")

class MarketHistory(Base):
    __tablename__ = "market_history"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    date = Column(DateTime)
    buy_price = Column(Float)
    sell_price = Column(Float)
    volume = Column(Integer)

    item = relationship("Item", back_populates="market_history")

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    date = Column(DateTime, default=datetime.utcnow)
    predicted_buy_price = Column(Float)
    predicted_sell_price = Column(Float)
    confidence_score = Column(Float)

    item = relationship("Item", back_populates="predictions")

class Region(Base):
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, unique=True, index=True)
    name = Column(String, index=True)

class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    file_date = Column(DateTime, index=True)
    file_date = Column(DateTime, index=True)
    processed_at = Column(DateTime, default=datetime.utcnow)