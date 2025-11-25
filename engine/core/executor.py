import importlib
import time
import traceback
from datetime import datetime
from typing import Optional

from engine.core.database import init_db, BotConfig, Log, RedisClient

class BotExecutor:
    def __init__(self, bot_id: int):
        self.bot_id = bot_id
        self.redis = RedisClient()
        
        # Initialize DB session
        Session = init_db()
        self.session = Session()
        
        # Load Config
        self.config = self._load_config()
        if not self.config:
            raise ValueError(f"Bot configuration not found for ID: {bot_id}")
            
        # Load Strategy
        self.strategy = self._load_strategy()
        
    def _load_config(self) -> Optional[BotConfig]:
        """Loads bot configuration from SQLite."""
        return self.session.query(BotConfig).filter_by(id=self.bot_id).first()

    def _load_strategy(self):
        """Dynamically imports and instantiates the strategy."""
        strategy_path = self.config.strategy_name
        try:
            # Assuming strategy_name is like "strategies.active.btc_hybrid"
            module_name, class_name = strategy_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            strategy_class = getattr(module, class_name)
            
            # Convert config to dict for strategy init
            config_dict = {
                'symbol': self.config.symbol,
                'leverage': self.config.leverage
            }
            return strategy_class(config_dict)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Failed to load strategy '{strategy_path}': {e}")

    def _log_error(self, message: str):
        """Logs error to SQLite and Redis."""
        print(f"ERROR: {message}")
        
        # Log to SQLite
        log_entry = Log(level="ERROR", message=message)
        self.session.add(log_entry)
        self.session.commit()
        
        # Update Redis status
        self.redis.set_live_state(f"bot:{self.bot_id}:status", "ERROR")

    def run_cycle(self):
        """Executes one trading cycle."""
        try:
            # 1. Fetch Market Data (Mock)
            # In real implementation, this would come from CCXT
            market_data = {
                'close': 100.0,  # Placeholder
                'volume': 1000
            }
            
            # 2. Analyze
            signal = self.strategy.analyze(market_data)
            
            # 3. Execute
            if signal and signal.get('action') in ['GO_LONG', 'GO_SHORT']:
                # Placeholder for Risk Manager check
                # if risk_manager.check(...):
                print(f"Opening Order: {signal['action']} for {self.config.symbol}")
            
            # 4. Update Heartbeat
            self.redis.set_live_state(f"bot:{self.bot_id}:status", "RUNNING")
            self.redis.set_live_state(f"bot:{self.bot_id}:last_check", str(datetime.utcnow()))
            
        except Exception as e:
            error_msg = f"Cycle failed: {str(e)}\n{traceback.format_exc()}"
            self._log_error(error_msg)
