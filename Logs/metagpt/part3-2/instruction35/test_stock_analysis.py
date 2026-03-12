
import pytest
import pandas as pd
import numpy as np

from your_module import calculate_sma, calculate_ema, calculate_rsi

def test_calculate_sma():
    s = pd.Series([1, 2, 3, 4, 5])
    result = calculate_sma(s, window=2)
    assert np.allclose(result.dropna(), [1.5, 2.5, 3.5, 4.5])

def test_calculate_ema():
    s = pd.Series([1, 2, 3, 4, 5])
    result = calculate_ema(s, window=2)
    assert np.isclose(result.iloc[-1], 4.666666666666667)

def test_calculate_rsi():
    s = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7])
    rsi = calculate_rsi(s, window=3)
    assert rsi.notnull().sum() > 0
