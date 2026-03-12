import sys
import logging
import asyncio
from config import BotConfig
from exchange import Exchange
from strategy import TrendStrategy
from risk import RiskManager
from data import DataFeed
from monitor import Monitor
from notifier import Notifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main")

async def main():
    # Load configuration
    config_path = "config.json"
    try:
        config = BotConfig.load(config_path)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Initialize Exchange
    exchange = Exchange()
    try:
        exchange.connect(config.api_key, config.api_secret)
    except Exception as e:
        logger.error(f"Failed to connect to exchange: {e}")
        sys.exit(1)

    # Initialize Strategy
    strategy = TrendStrategy(config.strategy_params)

    # Initialize Risk Manager
    risk_manager = RiskManager(config.risk_params)

    # Initialize Data Feed
    data_feed = DataFeed()
    data_feed.subscribe(config.assets)

    # Initialize Monitor and Notifier
    monitor = Monitor()
    notifier = Notifier(config.notification_settings)

    async def on_data_update(symbol: str):
        try:
            data = data_feed.get_latest(symbol)
            signal = strategy.generate_signal(data)
            positions = exchange.get_positions()
            position = next((p for p in positions if p['symbol'] == symbol), None)

            risk_ok = risk_manager.check_risk(position, signal)
            if risk_ok:
                # Determine order parameters
                side = "buy" if signal == "long" else "sell"
                qty = config.strategy_params.get("position_size", 1.0)
                price = data.iloc[-1]["close"]
                order_type = config.strategy_params.get("order_type", "market")
                order = exchange.place_order(symbol, side, qty, price, order_type)
                monitor.log_trade(order)
                notifier.send_push(f"Trade executed: {order}")
            else:
                monitor.alert(f"Risk check failed for {symbol} with signal {signal}")
                notifier.send_push(f"Risk event: {symbol} signal {signal} blocked by risk manager")
        except Exception as e:
            logger.error(f"Error in data update for {symbol}: {e}")

    # Register callback for data updates
    data_feed.on_update(on_data_update)

    # Main event loop
    logger.info("Custom Trading Bot started.")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")

if __name__ == "__main__":
    asyncio.run(main())