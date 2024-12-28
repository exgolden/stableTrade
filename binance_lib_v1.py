"""
 V1 functions neccesary to run the Binance API
"""
import base64
import sys
import os
import dotenv
import requests
import time

from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from requests.models import Request

# Temporal imports for tesing
# from cryptography.hazmat.primitives.serialization import load_pem_private_key
# dotenv.load_dotenv()
# API_KEY = os.getenv("API_KEY_2")
URL = "https://testnet.binance.vision/api"
# PATH = os.getenv("PATH")
# if not API_KEY:
#     raise ValueError("API_KEY is not set in the environment variables.")
# if not PATH:
#     raise ValueError("PATH to the private key is not set in the environment variables.")
# with open(PATH, 'rb') as f:
    # private_key = load_pem_private_key(data=f.read(),
                                       # password=None)
# General module
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
        response = public_executor("/v3/ping")
        return response == {}
    except Exception as e:
        print(f"Healthcheck failed for default endpoint: {URL}: {e}")
        return False

# Market data module
# def get_current_price(symbol: str) -> dict:
#     """
#     Fetches the current price of a specific trading pair.
#     Args:
#         symbol (str): The trading pair symbol.
#     Returns:
#         dict: A dictionary containing the symbol and its current price.
#     Raises:
#         ValueError: If the response does not include expected keys.
#         RuntimeError: If the request fails for any reason.
#     """
#     endpoint = f"/api/v3/ticker/price?symbol={symbol}"
#     try:
#         repsonse = public_executor({}, endpoint)
#     except Exception as e:
        raise e





# Testing
print(healthcheck())



