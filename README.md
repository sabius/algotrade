# 🚀 AlgoTrade Fleet Command

**A centralized architecture for managing multiple Binance Futures bots.**

This project transitions from running monolithic, isolated scripts to a **Controller-Worker** architecture. It allows you to "plug in" different trading logic (strategies) without rewriting the connection, error handling, or risk management code every time.

## 🏗 Architecture

### 1. The Engine (`/engine`)
The "muscle" of the operation. It handles:
- **Database**: SQLAlchemy (SQLite) for persistence and Redis for live state (heartbeats, PnL).
- **Executor**: Dynamic strategy loading and execution cycles.
- **Risk Management**: Global checks before trade execution.

### 2. The Strategies (`/strategies`)
The "brain" of the operation. 
- **Vibe Coding Friendly:** Each strategy is a simple file inheriting from `BaseStrategy`.
- Strategies do not talk to the API directly; they talk to the Engine.

### 3. The Dashboard (`/dashboard`)
A web interface (Flask + Vue.js) to:
- View all active bots and their live status.
- Monitor real-time PnL and recent trades.
- Start/Stop bots with a single click.

---

## 🛠 Project Structure

```text
root/
├── config/              # JSON configurations
├── dashboard/           # Flask + Vue.js Web App
│   ├── app.py           # Flask Backend
│   └── templates/       # Vue.js Frontend
├── data/                # Local databases (SQLite) & Logs
├── engine/              # Core System Logic
│   ├── core/            # Database & Executor logic
│   ├── connectors/      # Binance API wrappers
│   └── risk/            # Global risk guard
├── strategies/          # Botting strategies
│   ├── templates/       # Base classes
│   └── active/          # Live strategies
├── .env                 # API Keys (Ignored by Git)
└── requirements.txt     # Python dependencies
```

## ⚡ Workflow for "Vibe Coding"

When creating a new bot with AI:

1. **Copy the Template:** Take the code from `strategies/templates/base_strategy.py`.
2. **Prompt the AI:** 
   > "I have a standardized Python Strategy class. Please implement a new class inheriting from `BaseStrategy` that executes the following logic..."
3. **Plug it in:** Save the resulting file into `strategies/active/` and update the database configuration.

## � Quick Start

### 1. Prerequisites
- Python 3.12+
- Redis (Must be running locally)

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment
Rename `.env.example` to `.env` and add your Binance Keys.

### 4. Run the Dashboard
The dashboard is the control center for your fleet.
```bash
python dashboard/app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

### 5. Run the Bots
(Coming Soon: A main entry point `main.py` will be updated to launch the executor processes based on the database configuration.)