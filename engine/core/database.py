import os
from datetime import datetime
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import redis

# --- Configuration ---
DB_PATH = "data/db/trading.db"
DB_URL = f"sqlite:///{DB_PATH}"

# --- SQLAlchemy Setup ---
Base = declarative_base()

class BotConfig(Base):
    __tablename__ = 'bot_config'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    leverage = Column(Integer, default=1)
    strategy_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    side = Column(String, nullable=False) # 'buy' or 'sell'

class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    level = Column(String, nullable=False)
    message = Column(String, nullable=False)

# --- Redis Client ---
class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set_live_state(self, key: str, value: str, ttl: int = 60):
        """Sets a key-value pair with a TTL (default 60s)."""
        try:
            self.client.setex(key, ttl, value)
        except redis.RedisError as e:
            print(f"Redis Error (set): {e}")

    def get_live_state(self, key: str) -> Optional[str]:
        """Gets a value by key."""
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            print(f"Redis Error (get): {e}")
            return None

# --- Initialization ---
def init_db():
    """Creates the database tables if they don't exist."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
