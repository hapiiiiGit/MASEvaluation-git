import asyncio
import logging
from typing import List, Callable, Dict, Any, Optional
import threading
import pandas as pd
import ccxt
import time

class DataFeed:
    """
    DataFeed class for subscribing to symbols, retrieving latest market data,
    and handling update callbacks. Uses polling via ccxt for CoinDCX Futures.
    """

    def __init__(self, poll_interval: float = 2.0):
        self.logger = logging.getLogger("DataFeed")
        self.symbols: List[str] = []
        self.callbacks: List[Callable[[str], None]] = []
        self.latest_data: Dict[str, pd.DataFrame] = {}
        self.poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._exchange: Optional[ccxt.coincdx] = None

    def subscribe(self, symbols: List[str]):
        """
        Subscribe to a list of trading symbols.
        """
        self.symbols = list(set(self.symbols) | set(symbols))
        self.logger.info(f"Subscribed to symbols: {self.symbols}")

    def set_exchange(self, exchange: ccxt.coincdx):
        """
        Set the ccxt exchange client for data fetching.
        """
        self._exchange = exchange

    def get_latest(self, symbol: str) -> pd.DataFrame:
        """
        Get the latest OHLCV data for a symbol.
        """
        if symbol in self.latest_data:
            return self.latest_data[symbol]
        else:
            raise ValueError(f"No data available for symbol: {symbol}")

    def on_update(self, callback: Callable[[str], None]):
        """
        Register a callback to be called when new data is available for a symbol.
        The callback receives the symbol as argument.
        """
        self.callbacks.append(callback)

    def _fetch_ohlcv(self, symbol: str, timeframe: str = "1m", limit: int = 100) -> pd.DataFrame:
        """
        Fetch OHLCV data for a symbol using ccxt.
        """
        if not self._exchange:
            raise RuntimeError("Exchange client not set in DataFeed.")
        try:
            ohlcv = self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    def _polling_loop(self):
        """
        Polling loop to fetch data and trigger callbacks.
        """
        self.logger.info("DataFeed polling loop started.")
        while self._running:
            for symbol in self.symbols:
                df = self._fetch_ohlcv(symbol)
                if not df.empty:
                    prev_df = self.latest_data.get(symbol)
                    # Only trigger update if new data is available
                    if prev_df is None or not df.equals(prev_df):
                        self.latest_data[symbol] = df
                        for cb in self.callbacks:
                            try:
                                cb(symbol)
                            except Exception as e:
                                self.logger.error(f"Error in data update callback for {symbol}: {e}")
            time.sleep(self.poll_interval)
        self.logger.info("DataFeed polling loop stopped.")

    def start(self, exchange: ccxt.coincdx = None):
        """
        Start the data feed polling loop in a background thread.
        Optionally set the exchange client.
        """
        if exchange:
            self.set_exchange(exchange)
        if not self._exchange:
            raise RuntimeError("Exchange client must be set before starting DataFeed.")
        if self._running:
            self.logger.warning("DataFeed already running.")
            return
        self._running = True
        self._thread = threading.Thread(target=self._polling_loop, daemon=True)
        self._thread.start()
        self.logger.info("DataFeed started.")

    def stop(self):
        """
        Stop the data feed polling loop.
        """
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None
        self.logger.info("DataFeed stopped.")