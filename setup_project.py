import os
import sys

def create_file(path, content=""):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + "\n")
    print(f"✅ Created: {path}")

def create_folder(path):
    os.makedirs(path, exist_ok=True)
    print(f"📁 Created: {path}/")

def main():
    root = "."
    
    # --- 1. PROJECT STRUCTURE ---
    folders = [
        "config",
        "data/logs",
        "data/db",
        "dashboard",
        "engine",
        "engine/connectors",
        "engine/core",
        "engine/risk",
        "strategies",
        "strategies/active",
        "strategies/templates",
    ]
    
    for folder in folders:
        create_folder(os.path.join(root, folder))

    # --- 2. GITIGNORE & ENVIRONMENT ---
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
venv/
.pytest_cache/

# Environment Variables
.env
.env.local

# IDEs
.vscode/
.idea/

# Logs and Data
data/logs/*
data/db/*.db
*.log
"""
    create_file(os.path.join(root, ".gitignore"), gitignore_content)
    
    env_content = """
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
ENV_TYPE=PAPER_TRADING
# Set to PRODUCTION for real money
"""
    create_file(os.path.join(root, ".env.example"), env_content)
    # Also create the real .env (user should edit this)
    create_file(os.path.join(root, ".env"), env_content)

    # --- 3. STRATEGY TEMPLATE (THE CRITICAL PART) ---
    # This abstracts the code so she can focus on logic
    base_strategy_content = """
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    \"\"\"
    Standard Interface for all 'Vibe Coded' strategies.
    The engine will call these methods automatically.
    \"\"\"

    def __init__(self, config):
        self.config = config
        self.symbol = config.get('symbol')
        self.leverage = config.get('leverage', 1)

    @abstractmethod
    def analyze(self, market_data):
        \"\"\"
        Analyze market data (candles, indicators).
        Returns:
            dict: {'action': 'GO_LONG' | 'GO_SHORT' | 'WAIT', 'reason': '...'}
        \"\"\"
        pass

    @abstractmethod
    def check_exit(self, position, market_data):
        \"\"\"
        Check if we should close the position (TP/SL/Signal Flip).
        Returns:
            bool: True to close, False to hold
        \"\"\"
        pass

    def get_position_size(self, wallet_balance):
        \"\"\"
        Calculate position size based on risk settings.
        \"\"\"
        risk_per_trade = self.config.get('risk_per_trade', 0.01)
        return wallet_balance * risk_per_trade
"""
    create_file(os.path.join(root, "strategies/templates/base_strategy.py"), base_strategy_content)

    # --- 4. CONFIGURATION ---
    config_content = """
{
    "global_settings": {
        "max_daily_drawdown_percent": 3.0,
        "max_open_positions": 3,
        "dry_run": true
    },
    "active_bots": [
        {
            "id": "btc_conservative_01",
            "strategy_file": "btc_hybrid_trend.py",
            "symbol": "BTCUSDT",
            "timeframe": "15m",
            "leverage": 3
        }
    ]
}
"""
    create_file(os.path.join(root, "config/strategies.json"), config_content)

    # --- 5. ENGINE BOILERPLATE ---
    
    # Main Entry Point
    main_content = """
import time
import json
from dotenv import load_dotenv
import os

# Load Environment
load_dotenv()

def main():
    print("🚀 Initializing AlgoTrade Fleet...")
    
    api_key = os.getenv("BINANCE_API_KEY")
    if not api_key or "your_api_key" in api_key:
        print("❌ Error: .env file not configured.")
        return

    print("✅ Environment loaded.")
    print("📡 Connecting to Binance Futures...")
    
    # TODO: Initialize Engine Here
    # engine = TradingEngine()
    # engine.start()

    while True:
        print("💓 System Heartbeat - Waiting for strategy execution...")
        time.sleep(10)

if __name__ == "__main__":
    main()
"""
    create_file(os.path.join(root, "main.py"), main_content)

    # Requirements
    reqs = """
ccxt
pandas
pandas_ta
python-dotenv
fastapi
uvicorn
pydantic
requests
"""
    create_file(os.path.join(root, "requirements.txt"), reqs)

    print("\n✨ PROJECT SETUP COMPLETE! ✨")
    print("1. Go to the folder and run: pip install -r requirements.txt")
    print("2. Edit .env with your keys.")
    print("3. Start coding strategies in /strategies/active/")

if __name__ == "__main__":
    main()