import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List
import pandas as pd

def utc_to_local(utc_dt: datetime, tz_offset: int = 0) -> datetime:
    """
    Convert UTC datetime to local time with given offset in hours.
    """
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(timezone.utc).astimezone(
        timezone(timedelta(hours=tz_offset))
    )

def timestamp_to_str(ts: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert a timestamp (seconds) to a formatted string.
    """
    return datetime.fromtimestamp(ts).strftime(fmt)

def ms_to_str(ms: int, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Convert a timestamp in milliseconds to a formatted string.
    """
    return datetime.fromtimestamp(ms / 1000.0).strftime(fmt)

def format_trade(trade: Dict[str, Any]) -> str:
    """
    Format a trade dictionary for logging or display.
    """
    entry_time = trade.get("entry_time")
    exit_time = trade.get("exit_time")
    entry_price = trade.get("entry_price")
    exit_price = trade.get("exit_price")
    side = trade.get("side")
    pnl = trade.get("pnl")
    reason = trade.get("reason", "")
    return (f"Trade [{side}] Entry: {entry_price} at {entry_time}, "
            f"Exit: {exit_price} at {exit_time}, PnL: {pnl:.2f}, Reason: {reason}")

def format_alert(alert: Dict[str, Any]) -> str:
    """
    Format an alert dictionary for logging or display.
    """
    ts = alert.get("timestamp", time.time())
    event = alert.get("event", "")
    return f"ALERT at {timestamp_to_str(ts)}: {event}"

def safe_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary, returning default if not found.
    """
    return d[key] if key in d else default

def handle_exception(e: Exception, logger: Optional[logging.Logger] = None, context: str = ""):
    """
    Handle exceptions by logging them.
    """
    msg = f"Exception in {context}: {str(e)}"
    if logger:
        logger.error(msg)
    else:
        print(msg)

def df_to_dict_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert a pandas DataFrame to a list of dictionaries.
    """
    return df.to_dict(orient="records")

def dict_list_to_df(dict_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of dictionaries to a pandas DataFrame.
    """
    return pd.DataFrame(dict_list)

def round_float(val: Any, digits: int = 4) -> float:
    """
    Safely round a float value.
    """
    try:
        return round(float(val), digits)
    except Exception:
        return 0.0

def validate_symbol(symbol: str) -> bool:
    """
    Validate trading symbol format (e.g., 'BTC/USDT').
    """
    return isinstance(symbol, str) and "/" in symbol and len(symbol.split("/")) == 2

def retry_on_exception(func, retries: int = 3, delay: float = 1.0, logger: Optional[logging.Logger] = None):
    """
    Retry a function on exception up to a number of times.
    """
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            if logger:
                logger.warning(f"Retry {attempt+1}/{retries} failed: {e}")
            time.sleep(delay)
    if logger:
        logger.error(f"All {retries} retries failed for function {func.__name__}")
    return None