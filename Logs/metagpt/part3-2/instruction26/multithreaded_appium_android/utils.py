import time
import functools
from typing import Callable, Any, Type, Tuple, Optional
from datetime import datetime

def format_timestamp(ts: Optional[float] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a timestamp (float) to a human-readable string.
    If ts is None, use current time.
    """
    if ts is None:
        ts = time.time()
    return datetime.fromtimestamp(ts).strftime(fmt)

def retry(
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    tries: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
    logger: Optional[Any] = None
) -> Callable:
    """
    Decorator for retrying a function if exceptions occur.
    :param exceptions: Exceptions to catch and retry.
    :param tries: Number of attempts.
    :param delay: Initial delay between retries.
    :param backoff: Multiplier applied to delay after each failure.
    :param logger: Optional logger to log retry attempts.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            while _tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    msg = f"{func.__name__} failed with {e}, retrying in {_delay} seconds..."
                    if logger:
                        logger.log(msg, "WARNING")
                    else:
                        print(msg)
                    time.sleep(_delay)
                    _tries -= 1
                    _delay *= backoff
            # Last attempt
            return func(*args, **kwargs)
        return wrapper
    return decorator

def safe_get(d: dict, keys: list, default=None):
    """
    Safely get a nested value from a dictionary.
    :param d: The dictionary.
    :param keys: List of keys representing the path.
    :param default: Default value if any key is missing.
    """
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks of specified size.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """
    Check if a TCP port is open on a given host.
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return True
        except Exception:
            return False

def get_free_port() -> int:
    """
    Get a free TCP port from the OS.
    """
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]