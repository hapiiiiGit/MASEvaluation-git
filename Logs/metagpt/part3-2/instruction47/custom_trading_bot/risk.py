import logging
from typing import Dict, Any, Optional

class RiskManager:
    """
    Implements risk management for the trading bot.
    Includes check_risk, apply_stop_loss, and apply_take_profit methods.
    """

    def __init__(self, params: Dict[str, Any]):
        self.params = params.copy()
        self.max_drawdown = float(self.params.get("max_drawdown", 0.2))  # 20% default
        self.stop_loss_pct = float(self.params.get("stop_loss_pct", 0.05))  # 5% default
        self.take_profit_pct = float(self.params.get("take_profit_pct", 0.1))  # 10% default
        self.max_position_size = float(self.params.get("max_position_size", 1.0))  # 1 contract default
        self.logger = logging.getLogger("RiskManager")

    def check_risk(self, position: Optional[Dict[str, Any]], signal: str) -> bool:
        """
        Check if a new trade is allowed based on risk parameters.
        :param position: Current position dict for the symbol (can be None if no position)
        :param signal: Trading signal ('long', 'short', 'neutral')
        :return: True if trade is allowed, False otherwise
        """
        # If no signal, do not trade
        if signal not in ["long", "short"]:
            self.logger.info("Signal is neutral, no trade.")
            return False

        # If no position, allow trade
        if position is None:
            self.logger.info("No open position, trade allowed.")
            return True

        # Check position size
        position_size = float(position.get("contracts", 0))
        if position_size >= self.max_position_size:
            self.logger.warning(f"Position size {position_size} exceeds max {self.max_position_size}.")
            return False

        # Check drawdown (if available)
        unrealized_pnl = float(position.get("unrealizedPnl", 0))
        entry_value = float(position.get("entryPrice", 0)) * position_size if position.get("entryPrice") else 0
        if entry_value > 0:
            drawdown = -unrealized_pnl / entry_value
            if drawdown > self.max_drawdown:
                self.logger.warning(f"Drawdown {drawdown:.2%} exceeds max {self.max_drawdown:.2%}.")
                return False

        self.logger.info("Risk check passed, trade allowed.")
        return True

    def apply_stop_loss(self, position: Dict[str, Any]) -> bool:
        """
        Check if stop-loss should be triggered for the position.
        :param position: Current position dict
        :return: True if stop-loss should be triggered, False otherwise
        """
        entry_price = float(position.get("entryPrice", 0))
        current_price = float(position.get("markPrice", 0))
        side = position.get("side", "").lower()
        if entry_price == 0 or current_price == 0 or side not in ["long", "short"]:
            self.logger.info("Insufficient data for stop-loss check.")
            return False

        stop_loss_triggered = False
        if side == "long":
            if (current_price / entry_price - 1) <= -self.stop_loss_pct:
                stop_loss_triggered = True
        elif side == "short":
            if (entry_price / current_price - 1) <= -self.stop_loss_pct:
                stop_loss_triggered = True

        if stop_loss_triggered:
            self.logger.info(f"Stop-loss triggered for {side} position at price {current_price}.")
        return stop_loss_triggered

    def apply_take_profit(self, position: Dict[str, Any]) -> bool:
        """
        Check if take-profit should be triggered for the position.
        :param position: Current position dict
        :return: True if take-profit should be triggered, False otherwise
        """
        entry_price = float(position.get("entryPrice", 0))
        current_price = float(position.get("markPrice", 0))
        side = position.get("side", "").lower()
        if entry_price == 0 or current_price == 0 or side not in ["long", "short"]:
            self.logger.info("Insufficient data for take-profit check.")
            return False

        take_profit_triggered = False
        if side == "long":
            if (current_price / entry_price - 1) >= self.take_profit_pct:
                take_profit_triggered = True
        elif side == "short":
            if (entry_price / current_price - 1) >= self.take_profit_pct:
                take_profit_triggered = True

        if take_profit_triggered:
            self.logger.info(f"Take-profit triggered for {side} position at price {current_price}.")
        return take_profit_triggered