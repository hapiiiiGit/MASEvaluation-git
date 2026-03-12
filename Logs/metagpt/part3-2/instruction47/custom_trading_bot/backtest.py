import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from strategy import TrendStrategy
from risk import RiskManager

class Backtester:
    """
    Backtester class for running strategy backtests and reporting results.
    Includes run and report methods as per system design.
    """

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.trades: list = []
        self.equity_curve: list = []
        self.initial_balance: float = 10000.0  # Default initial balance for backtest
        self.final_balance: float = self.initial_balance
        self.max_drawdown: float = 0.0
        self.total_return: float = 0.0
        self.win_rate: float = 0.0
        self.total_trades: int = 0
        self.profitable_trades: int = 0

    def run(self, strategy: TrendStrategy, data: pd.DataFrame, risk: RiskManager) -> Dict[str, Any]:
        """
        Run backtest for the given strategy and data, using the provided risk manager.
        :param strategy: TrendStrategy instance
        :param data: pd.DataFrame with OHLCV data
        :param risk: RiskManager instance
        :return: Results dictionary
        """
        balance = self.initial_balance
        position = None
        entry_price = 0.0
        position_side = None
        position_size = 0.0
        self.trades = []
        self.equity_curve = [balance]
        self.max_drawdown = 0.0
        self.total_trades = 0
        self.profitable_trades = 0

        for i in range(1, len(data)):
            window = data.iloc[:i+1]
            signal = strategy.generate_signal(window)
            price = window["close"].iloc[-1]
            timestamp = window["timestamp"].iloc[-1] if "timestamp" in window.columns else i

            # Simulate position management
            if position is None and signal in ["long", "short"]:
                # Open new position
                position = {
                    "side": signal,
                    "entryPrice": price,
                    "markPrice": price,
                    "contracts": 1,
                    "timestamp": timestamp
                }
                entry_price = price
                position_side = signal
                position_size = 1
                self.total_trades += 1
            elif position is not None:
                # Update mark price
                position["markPrice"] = price

                # Check for stop-loss/take-profit
                stop_loss_triggered = risk.apply_stop_loss(position)
                take_profit_triggered = risk.apply_take_profit(position)

                # Close position if triggered or opposite signal
                close_position = False
                reason = ""
                if stop_loss_triggered:
                    close_position = True
                    reason = "stop_loss"
                elif take_profit_triggered:
                    close_position = True
                    reason = "take_profit"
                elif signal != position_side and signal in ["long", "short"]:
                    close_position = True
                    reason = "signal_flip"

                if close_position:
                    # Calculate PnL
                    pnl = 0.0
                    if position_side == "long":
                        pnl = (price - entry_price) * position_size
                    elif position_side == "short":
                        pnl = (entry_price - price) * position_size
                    balance += pnl
                    self.trades.append({
                        "entry_price": entry_price,
                        "exit_price": price,
                        "side": position_side,
                        "pnl": pnl,
                        "reason": reason,
                        "entry_time": position["timestamp"],
                        "exit_time": timestamp
                    })
                    if pnl > 0:
                        self.profitable_trades += 1
                    position = None
                    entry_price = 0.0
                    position_side = None
                    position_size = 0.0

            self.equity_curve.append(balance)
            # Update max drawdown
            peak = max(self.equity_curve)
            drawdown = (peak - balance) / peak if peak > 0 else 0
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown

        self.final_balance = balance
        self.total_return = (self.final_balance - self.initial_balance) / self.initial_balance
        self.win_rate = (self.profitable_trades / self.total_trades) if self.total_trades > 0 else 0.0

        self.results = {
            "initial_balance": self.initial_balance,
            "final_balance": self.final_balance,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
            "total_trades": self.total_trades,
            "win_rate": self.win_rate,
            "trades": self.trades,
            "equity_curve": self.equity_curve
        }
        return self.results

    def report(self) -> Dict[str, Any]:
        """
        Return the backtest results.
        :return: Results dictionary
        """
        return self.results