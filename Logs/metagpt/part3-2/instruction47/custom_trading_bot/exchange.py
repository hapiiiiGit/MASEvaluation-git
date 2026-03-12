import ccxt
import logging
from typing import Dict, List, Optional

class Exchange:
    """
    Exchange class for CoinDCX Futures integration using ccxt.
    Supports connect, get_balance, fetch_ticker, place_order, cancel_order, and get_positions.
    """

    def __init__(self):
        self.api_key: Optional[str] = None
        self.api_secret: Optional[str] = None
        self.client: Optional[ccxt.coincdx] = None
        self.logger = logging.getLogger("Exchange")

    def connect(self, api_key: str, api_secret: str):
        """
        Connect to CoinDCX Futures using provided API credentials.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        try:
            self.client = ccxt.coincdx({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future'
                }
            })
            # Test authentication
            self.client.check_required_credentials()
            self.logger.info("Connected to CoinDCX Futures.")
        except Exception as e:
            self.logger.error(f"Failed to connect to CoinDCX Futures: {e}")
            raise

    def get_balance(self) -> Dict:
        """
        Get account balance.
        """
        if not self.client:
            raise RuntimeError("Exchange not connected.")
        try:
            balance = self.client.fetch_balance()
            self.logger.info("Fetched account balance.")
            return balance
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            raise

    def fetch_ticker(self, symbol: str) -> Dict:
        """
        Fetch ticker data for a symbol.
        """
        if not self.client:
            raise RuntimeError("Exchange not connected.")
        try:
            ticker = self.client.fetch_ticker(symbol)
            self.logger.info(f"Fetched ticker for {symbol}.")
            return ticker
        except Exception as e:
            self.logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise

    def place_order(self, symbol: str, side: str, qty: float, price: float, type_: str) -> Dict:
        """
        Place an order on CoinDCX Futures.
        :param symbol: Trading symbol (e.g., 'BTC/USDT')
        :param side: 'buy' or 'sell'
        :param qty: Quantity to trade
        :param price: Price for limit orders; ignored for market orders
        :param type_: 'market' or 'limit'
        :return: Order response dict
        """
        if not self.client:
            raise RuntimeError("Exchange not connected.")
        try:
            order_type = type_.lower()
            params = {}
            if order_type == "market":
                order = self.client.create_order(
                    symbol=symbol,
                    type="market",
                    side=side,
                    amount=qty,
                    params=params
                )
            elif order_type == "limit":
                order = self.client.create_order(
                    symbol=symbol,
                    type="limit",
                    side=side,
                    amount=qty,
                    price=price,
                    params=params
                )
            else:
                raise ValueError(f"Unsupported order type: {type_}")
            self.logger.info(f"Placed {order_type} order: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error placing order for {symbol}: {e}")
            raise

    def cancel_order(self, order_id: str, symbol: Optional[str] = None) -> Dict:
        """
        Cancel an order by order_id.
        :param order_id: The order ID to cancel
        :param symbol: Trading symbol (required by some exchanges)
        :return: Cancel response dict
        """
        if not self.client:
            raise RuntimeError("Exchange not connected.")
        try:
            if symbol:
                result = self.client.cancel_order(order_id, symbol)
            else:
                result = self.client.cancel_order(order_id)
            self.logger.info(f"Cancelled order {order_id}.")
            return result
        except Exception as e:
            self.logger.error(f"Error cancelling order {order_id}: {e}")
            raise

    def get_positions(self) -> List[Dict]:
        """
        Get current open positions.
        :return: List of position dicts
        """
        if not self.client:
            raise RuntimeError("Exchange not connected.")
        try:
            # CoinDCX Futures positions are fetched via fetch_positions
            positions = self.client.fetch_positions()
            self.logger.info("Fetched open positions.")
            return positions
        except Exception as e:
            self.logger.error(f"Error fetching positions: {e}")
            raise