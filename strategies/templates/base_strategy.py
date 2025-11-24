from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Standard Interface for all 'Vibe Coded' strategies.
    The engine will call these methods automatically.
    """

    def __init__(self, config):
        self.config = config
        self.symbol = config.get('symbol')
        self.leverage = config.get('leverage', 1)

    @abstractmethod
    def analyze(self, market_data):
        """
        Analyze market data (candles, indicators).
        Returns:
            dict: {'action': 'GO_LONG' | 'GO_SHORT' | 'WAIT', 'reason': '...'}
        """
        pass

    @abstractmethod
    def check_exit(self, position, market_data):
        """
        Check if we should close the position (TP/SL/Signal Flip).
        Returns:
            bool: True to close, False to hold
        """
        pass

    def get_position_size(self, wallet_balance):
        """
        Calculate position size based on risk settings.
        """
        risk_per_trade = self.config.get('risk_per_trade', 0.01)
        return wallet_balance * risk_per_trade
