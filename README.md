# 🚀 AlgoTrade Fleet Command

**A centralized architecture for managing multiple Binance Futures bots.**

This project transitions from running monolithic, isolated scripts to a **Controller-Worker** architecture. It allows you to "plug in" different trading logic (strategies) without rewriting the connection, error handling, or risk management code every time.

## 🏗 Architecture

### 1. The Engine (`/engine`)
The "muscle" of the operation. It handles:
- Binance API connection (Reconnections, Latency checks).
- Order execution and error handling (Retries, Timeouts).
- Global Risk Management (Kill switch if account drops X%).
- Logging and Database persistence.

### 2. The Strategies (`/strategies`)
The "brain" of the operation. 
- **Vibe Coding Friendly:** Each strategy is a simple file that answers three questions: *Should I enter? How much? Should I exit?*
- Strategies do not talk to the API directly; they talk to the Engine.

### 3. The Dashboard (`/dashboard`) (Planned)
A web interface to view PnL, stop/start bots, and change configurations without touching code.

---

## 🛠 Project Structure

```text
root/
├── config/              # JSON configurations (Symbol, Leverage, etc.)
├── dashboard/           # Web Frontend (React/Next.js)
├── data/                # Local databases & Logs
├── engine/              # Core System Logic (Don't touch this often)
│   ├── connectors/      # Binance API wrappers
│   ├── risk/            # Global risk guard
│   └── executor.py      # Main execution loop
├── strategies/          # Create botting strategies here
│   ├── templates/       # Copy these for new AI prompts
│   └── active/          # Live strategies
├── .env                 # API Keys (Ignored by Git)
└── main.py              # Entry point
```

## ⚡ Workflow for "Vibe Coding"

When creating a new bot with AI, you no longer ask it to "Write a bot from scratch." Instead:

1. **Copy the Template:** Take the code from `strategies/templates/base_strategy.py`.
2. **Prompt the AI:** 
   > "I have a standardized Python Strategy class. Please implement a new class inheriting from `BaseStrategy` that executes the following logic [Insert Her Logic Here]..."
3. **Plug it in:** Save the resulting file into `strategies/active/` and update `config/strategies.json`.

## 🔒 Security
- **API Keys:** Stored in `.env` (never committed to GitHub).
- **Risk Guard:** The Engine checks `engine/risk/global_guard.py` before every trade. If daily drawdown > 3%, all bots pause.

## 🚀 Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Setup Keys:**
   Rename `.env.example` to `.env` and add your Binance Keys.
3. **Run the Fleet:**
   ```bash
   python main.py
   ```