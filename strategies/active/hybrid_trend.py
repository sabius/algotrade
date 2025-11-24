# strategies/active/hybrid_trend.py
import pandas_ta as ta
import pandas as pd
from strategies.templates.base_strategy import BaseStrategy

class HybridTrendStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)

    def analyze(self, df):
        """
        Analyzes the dataframe to find entry signals.
        """
        try:
            # Ensure we have enough data
            if len(df) < 200:
                return {'action': 'WAIT', 'reason': 'Not enough data'}

            # 1. Calculate Indicators
            ema8 = df.ta.ema(length=8)
            ema20 = df.ta.ema(length=20)
            ema21 = df.ta.ema(length=21)
            ema50 = df.ta.ema(length=50)
            ema200 = df.ta.ema(length=200)
            adx = df.ta.adx(length=14)
            rsi = df.ta.rsi(length=14)
            macd = df.ta.macd(fast=12, slow=26, signal=9)
            atr = df.ta.atr(length=14)
            vol_sma = df.ta.sma(close=df['Volume'], length=20)

            # Check for warmup
            if ema200.iloc[-1] is None:
                return {'action': 'WAIT', 'reason': 'Indicators warming up'}

            # Get values
            current_price = df['Close'].iloc[-1]
            prev_high = df['High'].iloc[-2]
            prev_low = df['Low'].iloc[-2]
            volume = df['Volume'].iloc[-1]
            
            curr_ema8 = ema8.iloc[-1]
            curr_ema21 = ema21.iloc[-1]
            curr_ema50 = ema50.iloc[-1]
            curr_ema200 = ema200.iloc[-1]
            curr_adx = adx['ADX_14'].iloc[-1]
            curr_rsi = rsi.iloc[-1]
            curr_macd_hist = macd['MACDh_12_26_9'].iloc[-1]
            curr_atr = atr.iloc[-1]
            curr_vol_sma = vol_sma.iloc[-1]

            # 2. ENTRY LOGIC
            atr_pct = curr_atr / current_price
            if not (0.002 <= atr_pct <= 0.025):
                return {'action': 'WAIT', 'reason': f'ATR Filter: {atr_pct:.4f}'}

            vol_check = volume > (0.8 * curr_vol_sma)

            # LONG
            if (curr_ema8 > curr_ema21 and 
                current_price > curr_ema50 and 
                curr_ema50 > curr_ema200 and 
                curr_adx >= 20 and 
                curr_rsi > 50 and 
                curr_macd_hist > 0 and 
                vol_check and 
                current_price > prev_high): # Structure check
                
                return {'action': 'GO_LONG', 'reason': 'Long Trigger Met'}

            # SHORT
            if (curr_ema8 < curr_ema21 and 
                current_price < curr_ema50 and 
                curr_ema50 < curr_ema200 and 
                curr_adx >= 20 and 
                curr_rsi < 50 and 
                curr_macd_hist < 0 and 
                vol_check and 
                current_price < prev_low): # Structure check
                
                return {'action': 'GO_SHORT', 'reason': 'Short Trigger Met'}

            return {'action': 'WAIT', 'reason': 'No signal'}

        except Exception as e:
            return {'action': 'WAIT', 'reason': f'Error in analyze: {str(e)}'}

    def check_exit(self, df, current_price):
        try:
            if not self.state['active']:
                return {'action': 'HOLD', 'reason': 'No active trade'}

            ema20 = df.ta.ema(length=20).iloc[-1]
            ema50 = df.ta.ema(length=50).iloc[-1]
            atr = df.ta.atr(length=14).iloc[-1]

            direction = self.state['direction']
            entry_price = self.state['entry_price']
            current_sl = self.state['sl']

            if direction == 'LONG':
                # Update High
                if current_price > self.state['highest_price']:
                    self.state['highest_price'] = current_price
                
                # Trailing
                potential_sl = self.state['highest_price'] - (2.2 * atr)
                if potential_sl > current_sl:
                    self.state['sl'] = potential_sl
                
                # Hard Exit
                if ema20 < ema50:
                    return {'action': 'CLOSE', 'reason': 'EMA Cross Exit'}

                # TP Logic
                pnl_pct = (current_price - entry_price) / entry_price
                if pnl_pct >= 0.01 and not self.state['tp1_hit']:
                    self.state['tp1_hit'] = True
                    self.state['sl'] = max(entry_price, self.state['sl'])
                    return {'action': 'UPDATE_SL', 'new_sl': self.state['sl'], 'reason': 'TP1 Hit'}
                
                if pnl_pct >= 0.018 and not self.state['tp2_hit']:
                    self.state['tp2_hit'] = True
                    self.state['sl'] = max(entry_price * 1.01, self.state['sl'])
                    return {'action': 'UPDATE_SL', 'new_sl': self.state['sl'], 'reason': 'TP2 Hit'}

            elif direction == 'SHORT':
                # Update Low
                if self.state['lowest_price'] == 0 or current_price < self.state['lowest_price']:
                    self.state['lowest_price'] = current_price
                
                # Trailing
                potential_sl = self.state['lowest_price'] + (2.2 * atr)
                if potential_sl < current_sl:
                    self.state['sl'] = potential_sl

                # Hard Exit
                if ema20 > ema50:
                    return {'action': 'CLOSE', 'reason': 'EMA Cross Exit'}

                # TP Logic
                pnl_pct = (entry_price - current_price) / entry_price
                if pnl_pct >= 0.01 and not self.state['tp1_hit']:
                    self.state['tp1_hit'] = True
                    self.state['sl'] = min(entry_price, self.state['sl'])
                    return {'action': 'UPDATE_SL', 'new_sl': self.state['sl'], 'reason': 'TP1 Hit'}

                if pnl_pct >= 0.018 and not self.state['tp2_hit']:
                    self.state['tp2_hit'] = True
                    self.state['sl'] = min(entry_price * 0.99, self.state['sl'])
                    return {'action': 'UPDATE_SL', 'new_sl': self.state['sl'], 'reason': 'TP2 Hit'}

            return {'action': 'UPDATE_SL', 'new_sl': self.state['sl'], 'reason': 'Trailing Update'}

        except Exception as e:
            return {'action': 'HOLD', 'reason': f'Error: {str(e)}'}