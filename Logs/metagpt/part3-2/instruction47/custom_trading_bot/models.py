from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class Position(BaseModel):
    symbol: str = Field(..., description="Trading symbol, e.g., 'BTC/USDT'")
    side: Literal["long", "short"] = Field(..., description="Position side")
    entryPrice: float = Field(..., description="Entry price of the position")
    markPrice: float = Field(..., description="Current mark price")
    contracts: float = Field(..., description="Number of contracts/position size")
    timestamp: Optional[datetime] = Field(None, description="Time when position was opened")
    unrealizedPnl: Optional[float] = Field(0.0, description="Unrealized PnL for the position")

class Trade(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    side: Literal["long", "short"] = Field(..., description="Trade side")
    entry_price: float = Field(..., description="Entry price")
    exit_price: float = Field(..., description="Exit price")
    pnl: float = Field(..., description="Profit and loss for the trade")
    reason: str = Field(..., description="Reason for trade exit (stop_loss, take_profit, signal_flip, manual, etc.)")
    entry_time: Optional[datetime] = Field(None, description="Trade entry time")
    exit_time: Optional[datetime] = Field(None, description="Trade exit time")

class Alert(BaseModel):
    timestamp: datetime = Field(..., description="Time of alert")
    event: str = Field(..., description="Alert event description")
    level: Literal["info", "warning", "error"] = Field("info", description="Alert level")

class BotStatus(BaseModel):
    running: bool = Field(..., description="Is the bot running")
    last_trade: Optional[Trade] = Field(None, description="Last trade executed")
    last_alert: Optional[Alert] = Field(None, description="Last alert sent")
    start_time: datetime = Field(..., description="Bot start time")
    trade_count: int = Field(0, description="Total number of trades")
    alert_count: int = Field(0, description="Total number of alerts")
    uptime_sec: Optional[float] = Field(None, description="Bot uptime in seconds")

class BacktestResult(BaseModel):
    initial_balance: float = Field(..., description="Initial balance for backtest")
    final_balance: float = Field(..., description="Final balance after backtest")
    total_return: float = Field(..., description="Total return percentage")
    max_drawdown: float = Field(..., description="Maximum drawdown percentage")
    total_trades: int = Field(..., description="Total number of trades")
    win_rate: float = Field(..., description="Win rate percentage")
    trades: List[Trade] = Field(default_factory=list, description="List of trades executed")
    equity_curve: List[float] = Field(default_factory=list, description="Equity curve over time")