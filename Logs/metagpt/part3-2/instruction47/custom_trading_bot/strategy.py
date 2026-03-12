import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class TrendStrategy:
    """
    Implements trend-following strategies (EMA, SMA, MACD, RSI).
    Provides generate_signal and update_params methods.
    """

    def __init__(self, params: Dict[str, Any]):
        self.params = params.copy()
        self.indicator = self.params.get("indicator", "EMA")  # Default to EMA
        self.indicator_params = self.params.get("indicator_params", {})
        self.signal_thresholds = self.params.get("signal_thresholds", {"buy": 0, "sell": 0})
        self.last_signal: Optional[str] = None

    def update_params(self, params: Dict[str, Any]):
        self.params.update(params)
        self.indicator = self.params.get("indicator", self.indicator)
        self.indicator_params = self.params.get("indicator_params", self.indicator_params)
        self.signal_thresholds = self.params.get("signal_thresholds", self.signal_thresholds)

    def generate_signal(self, data: pd.DataFrame) -> str:
        """
        Generate trading signal ('long', 'short', 'neutral') based on selected trend indicator.
        :param data: pd.DataFrame with OHLCV data, must contain 'close' column.
        :return: Signal string
        """
        if data is None or len(data) < 2 or "close" not in data.columns:
            return "neutral"

        if self.indicator == "EMA":
            return self._ema_signal(data)
        elif self.indicator == "SMA":
            return self._sma_signal(data)
        elif self.indicator == "MACD":
            return self._macd_signal(data)
        elif self.indicator == "RSI":
            return self._rsi_signal(data)
        else:
            # Default fallback
            return "neutral"

    def _ema_signal(self, data: pd.DataFrame) -> str:
        period = int(self.indicator_params.get("period", 20))
        ema = data["close"].ewm(span=period, adjust=False).mean()
        price = data["close"].iloc[-1]
        prev_ema = ema.iloc[-2]
        curr_ema = ema.iloc[-1]
        # Signal: price crosses above EMA -> long, below -> short
        if price > curr_ema and data["close"].iloc[-2] <= prev_ema:
            return "long"
        elif price < curr_ema and data["close"].iloc[-2] >= prev_ema:
            return "short"
        else:
            return "neutral"

    def _sma_signal(self, data: pd.DataFrame) -> str:
        period = int(self.indicator_params.get("period", 20))
        sma = data["close"].rolling(window=period).mean()
        price = data["close"].iloc[-1]
        prev_sma = sma.iloc[-2]
        curr_sma = sma.iloc[-1]
        if price > curr_sma and data["close"].iloc[-2] <= prev_sma:
            return "long"
        elif price < curr_sma and data["close"].iloc[-2] >= prev_sma:
            return "short"
        else:
            return "neutral"

    def _macd_signal(self, data: pd.DataFrame) -> str:
        fast_period = int(self.indicator_params.get("fast_period", 12))
        slow_period = int(self.indicator_params.get("slow_period", 26))
        signal_period = int(self.indicator_params.get("signal_period", 9))
        close = data["close"]
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        prev_macd = macd.iloc[-2] - signal.iloc[-2]
        curr_macd = macd.iloc[-1] - signal.iloc[-1]
        # MACD crosses above signal -> long, below -> short
        if prev_macd < 0 and curr_macd > 0:
            return "long"
        elif prev_macd > 0 and curr_macd < 0:
            return "short"
        else:
            return "neutral"

    def _rsi_signal(self, data: pd.DataFrame) -> str:
        period = int(self.indicator_params.get("period", 14))
        close = data["close"]
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        curr_rsi = rsi.iloc[-1]
        buy_th = float(self.signal_thresholds.get("buy", 30))
        sell_th = float(self.signal_thresholds.get("sell", 70))
        if curr_rsi < buy_th:
            return "long"
        elif curr_rsi > sell_th:
            return "short"
        else:
            return "neutral"