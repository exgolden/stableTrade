"""
 V1 functions neccesary to create graphs
"""
from typing import List
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from binance_lib_v1 import klines, rsi, moving_average


def candlestick_chart(klines: List[List[float]], symbol: str) -> None:
    """
    Creates a candlestick chart from kline data.

    """

