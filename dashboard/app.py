import os
import sys
from flask import Flask, jsonify, render_template, request

# Add project root to path to allow imports from engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.core.database import init_db, BotConfig, Trade, RedisClient

app = Flask(__name__)

# Initialize DB and Redis
Session = init_db()
redis_client = RedisClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/bots', methods=['GET'])
def get_bots():
    session = Session()
    try:
        bots = session.query(BotConfig).all()
        bot_list = []
        for bot in bots:
            # Fetch live state from Redis
            status = redis_client.get_live_state(f"bot:{bot.id}:status") or "STOPPED"
            last_check = redis_client.get_live_state(f"bot:{bot.id}:last_check")
            
            bot_data = {
                'id': bot.id,
                'symbol': bot.symbol,
                'strategy_name': bot.strategy_name,
                'is_active': bot.is_active,
                'status': status,
                'last_check': last_check
            }
            bot_list.append(bot_data)
        return jsonify(bot_list)
    finally:
        session.close()

@app.route('/api/bot/<int:bot_id>/toggle', methods=['POST'])
def toggle_bot(bot_id):
    session = Session()
    try:
        bot = session.query(BotConfig).filter_by(id=bot_id).first()
        if not bot:
            return jsonify({'error': 'Bot not found'}), 404
        
        bot.is_active = not bot.is_active
        session.commit()
        
        # Update Redis to reflect change immediately if needed, 
        # though the executor would pick it up on next cycle.
        # For now just return the new state.
        return jsonify({'id': bot.id, 'is_active': bot.is_active})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/trades', methods=['GET'])
def get_trades():
    session = Session()
    try:
        # Get last 50 trades
        trades = session.query(Trade).order_by(Trade.timestamp.desc()).limit(50).all()
        trade_list = []
        for trade in trades:
            trade_list.append({
                'id': trade.id,
                'symbol': 'N/A', # Trade model doesn't have symbol yet, assuming single bot or need update
                'entry_price': trade.entry_price,
                'exit_price': trade.exit_price,
                'pnl': trade.pnl,
                'side': trade.side,
                'timestamp': trade.timestamp.isoformat()
            })
        return jsonify(trade_list)
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
