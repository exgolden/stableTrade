"""
 V1 functions neccesary to run the Binance API
"""
import sys
import math
import requests
import time
from typing import List
# from cryptography.hazmat.primitives.hashes import SHA256
# from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
# from requests.models import Request

# Temporal imports for tesing
# from cryptography.hazmat.primitives.serialization import load_pem_private_key
# dotenv.load_dotenv()
# API_KEY = os.getenv("API_KEY_2")
URL = "https://testnet.binance.vision"
# PATH = os.getenv("PATH")
# if not API_KEY:
#     raise ValueError("API_KEY is not set in the environment variables.")
# if not PATH:
#     raise ValueError("PATH to the private key is not set in the environment variables.")
# with open(PATH, 'rb') as f:
    # private_key = load_pem_private_key(data=f.read(),
                                       # password=None)
# General module
def interval_validation(interval: str, range_minutes: int) -> dict:
    """
    Validates the interval and the current range to ensure data retrieval.
    Checks that the interval is valid.
    Checks that the range is greater or equal than the interval.
    Args:
        interval (str): The interval for candlesticks.
        range_minutes (int): The number of minutes for the range of data.
    Returns:
        dict: A dictionary containing:
            - "is_valid" (bool): Whether the validation passed.
            - "error" (str | None): An error message if validation fails, or 'None' if validation passes.
    """
    VALID_INTERVALS = ["1m", "3m", "5m", "15m", "30m", "1h",
                   "2h", "4h", "6h", "8h", "12h", "1d"]
    INTERVAL_DURATIONS = {
        "1m": 1,
        "3m": 3,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "2h": 120,
        "4h": 240,
        "6h": 360,
        "8h": 480,
        "12h": 720, 
        "1d": 1440,
    }
    if interval not in VALID_INTERVALS:
        return {
                "is_valid": False,
                "error": f"Invalid interval '{interval}'. Valid intervals are: {', '.join(VALID_INTERVALS)}."
                }
    if range_minutes < INTERVAL_DURATIONS[interval]:
        return {
                "is_valid": False,
                "error": f"The range ({range_minutes}m) must be >= to the interval's duration ({INTERVAL_DURATIONS[interval]}m)."
                }
    return {"is_valid": True, "error": None}

def status_code_analyzer(response: dict) -> dict:
    """
    Analyzes the response and returns a descriptive message.
    Returns a dictionary where the first element ('termination') is a boolean indicating
    if the app must exit, and the second ('message') is the status description.
    Args:
        response (dict): Response the API request.
    Returns:
        dict: Contains the termination status and a descriptive message:
        ValueError: If the 'status_code' key is missing in the response.
    Raises:
        ValueError: If the status code is not present.
    """
    if "status_code" not in response:
        raise ValueError("The response does not contain a 'status_code' key.")
    match response["status_code"]:
        case 403:
            return {"termination": True, "message": "Web Application Limit has been violated."}
        case 429:
            return {"termination": True, "message": "Request limit broken."}
        case 418:
            return {"termination": True, "message": "IP has been banned."}
        case _:
            return {"termination": False, "message": f"Unhandled status code {response['status_code']}: Further investigation needed."}

def api_code_analyzer(response: dict) -> str:
    """
    Analyzes and returns a descriptive message for a specific API error code.
    This function is called after confirming no critical HTTP status code has been returned.
    Args:
        response (dict): JSON response from the Binance API.
    Returns:
        str: Descriptive message for the error code.
     Raises:
        ValueError: If the code is not recognized or does not map to a known error type.
    """
    if "code" not in response:
        raise ValueError("The response does not contain a 'code' key for error analysis.")
    match response["code"]:
        case -1121:
            return "Invalid trading pair symbol."
        case _:
            return f"Unhandled code {response['code']}: Further investigation needed."

def public_executor(endpoint: str) -> dict:
    """
    Executes GET requests for a public endpoint (No key nor signature required).
    Args:
        endpoint (str): Relative URL to perform the query.
    Returns:
        dict: Parsed JSON response from the API.
    Raises:
        RuntimeError: If the request fails or returns a non-200 status code.
    """
    final_endpoint = URL + endpoint
    try:
        response = requests.get(final_endpoint)
        if response.status_code == 200:
            return response.json()
        status_code_message = status_code_analyzer({"status_code": response.status_code})
        print(f"Request failed with status {response.status_code}: {response.text}")
        if status_code_message["termination"]:
            sys.exit(1)
        json_response = response.json()
        if "code" in json_response:
            api_error_message = api_code_analyzer(json_response)
            raise RuntimeError(f"API Error: {api_error_message}")
        raise RuntimeError(f"Unhandled status code: {response.status_code}")
    except requests.RequestException as e:
        raise RuntimeError(f"Error during request execution: {e}")

# def private_executor(params: dict, endpoint: str) -> dict:
#     """
#     Executes a POST requests for a private endpoint (Key and signature required).
#     Args:
#         method (str): HTTP methos for the query.
#         params (dict): Query parameters.
#         endpoint (str): Relative URL to perform the query.
#     Returns:
#         dict: Parsed JSON response from the API.
#     Raises:
#         RuntimeError: If the request fails or returns a non-200 status code.
#     """
#     final_endpoint = URL + endpoint
#     timestamp = int(time.time() * 1000)
#     params["timestamp"] = timestamp
#     payload = "&".join([f"{param} = {value}" for param, value in params.items()])
#     signature =  base64.b64encode(
#         private_key.sign(
#             payload.encode('ASCII'),
#             PKCS1v15(),
#             SHA256()
#         )
#     )
#     params["signature"] = signature
#     headers = {
#         'X-MBX-APIKEY': API_KEY,
#     }
#     try:
#         response = requests.get(final_endpoint, headers=headers, params=params)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             error_message = status_analyzer(response.status_code)
#             print(f"Error: {error_message}")
#         if response.status_code in [403, 418, 429]:
#             sys.exit(1)
#         raise RuntimeError(f"Request failed with status {response.status_code}: {response.text}")
#     except requests.RequestException as e:
        raise RuntimeError(f"Error during request execution: {e}")

# Healthcheck module
def healthcheck() -> bool:
    """
    Verifies the health of the default endpoint by checking its response.
    Returns:
        bool: True if the base endpoint is reachable and functioning correctly 
              (returns an empty dictionary as the response), False otherwise.
    """
    try:
        response = public_executor("/api/v3/ping")
        return response == {}
    except Exception as e:
        print(f"Healthcheck failed for default endpoint: {URL}: {e}")
        return False

# Market data module
def get_current_price(symbol: str) -> dict:
    """
    Fetches the current price of a specific trading pair.
    Args:
        symbol (str): The trading pair symbol.
    Returns:
        dict: A dictionary containing the symbol and its current price.
    Raises:
        ValueError: If the response does not include expected keys.
    """
    endpoint = f"/api/v3/ticker/price?symbol={symbol}"
    response = public_executor(endpoint)
    return response

def get_klines(symbol: str, interval: str, range_minutes: int) -> list:
    """
    Fetches the most recent candlestick data for a specific symbol.
    Args:
        symbol (str): The trading pair symbol.
        interval (int): The interval for each candlestick.
        range_minutes (int): The number of minutes for the range data to return.
    Returns:
        list: A list of candlestickd ata, where each one is a list of details:
            [
                Open time,
                Open price,
                High price,
                Low price,
                Close price,
                Volume,
                Close time
            ]
    Raises:
        ValueError: If the interval or range validation fails.
        RuntimeError: If the API requst fails.
    """
    validation_result = interval_validation(interval, range_minutes)
    if not validation_result["is_valid"]:
        raise ValueError(f"Interval validation failed: {validation_result['error']}")
    end_time = int(time.time() * 1000)
    start_time = end_time - (range_minutes * 60 * 1000)
    endpoint = f"/api/v3/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}"
    response = public_executor(endpoint)
    if not isinstance(response, list):
        raise ValueError(f"Unexpected response structure: {response}")
    return response

# Technical indicators module
def moving_average(klines: List[List[float]], window: int) -> List[float]:
    """
    Calculates the moving average for a Kline set over a specific window.
    MA is computed using the closing price (index 4).
    Args:
        klines (List[List[float]]): Candlestick data.
        window (int): Number of perios for the moving average.
    Returns:
        List[float]: List of MA for each period.
    Raises:
        ValueError: If the window is greater than the number of Klines.
    """
    if len(klines) < window:
        raise ValueError(f"The size of window cannot be greater than the number of klines.")
    closing_prices = [float(kline[4]) for kline in klines]
    moving_average_list = []
    for i in range(len(closing_prices)):
        if i < window - 1:
            moving_average_list.append(None)
        else:
            window_prices = closing_prices[i - window + 1 : i + 1]
            moving_average_list.append(sum(window_prices) / window)
    return moving_average_list

def standard_deviation(klines: List[List[float]]) -> float:
    """
    Calculates the standard deviation of the closing prices from kline.
    Args:
        klines (List[List[float]]): Candlestick data.
    Returns:
        float: The standard deviation from the closing prices.
    """
    closing_prices = [float(kline[4]) for kline in klines]
    mean_price = sum(closing_prices) / len(closing_prices)
    squared_deviation = [(price - mean_price) ** 2 for price in closing_prices]
    variance = sum(squared_deviation) / len(closing_prices)
    standard_dev = math.sqrt(variance)
    return standard_dev

def rsi(klines: List[List[float]], period: int) -> List[int]:
    """
    Calculates the Relative Strenght Index for a given period.
    Args:
        klines (List[List[float]]): Candlestick data.
        period (int): The number of periods to use in the RSI calculation.
    Returns:
        List[float]: A list of RSI values, where None represents periods
        without enough data.
    """
    closing_prices = [float(kline[4]) for kline in klines]
    rsi_values = []
    gains = []
    losses = []
    for i in range(1, len(closing_prices)):
        change = closing_prices[i] - closing_prices[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rsi_values.extend([None] * period)
    for i in range(period, len(gains)):
        gain = gains[i]
        loss = losses[i]
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi = math.trunc(rsi)
        rsi_values.append(rsi)
    return rsi_values




































klines = get_klines("FDUSDUSDT", "5m", 480)
print(standard_deviation((klines)))
# rsi_valuse = rsi(klines, 14)
# print((rsi_valuse))
#





# Testing
# print(healthcheck())
# print(get_current_price("FDUSDUSDT"))
# print(get_klines("FDUSDUSDT", "5m", 15))
# klines = get_klines("FDUSDUSDT", "3m", 60)
# print(moving_average(klines, 5))
