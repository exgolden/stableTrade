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
def status_analyzer(status_code : int):
    """
    Analyzes the HTTP status code and returns a descriptive message.
    This function maps specific status codes to their corresponding error messages.
    Args:
        status_code (int): Status code for the request.
    """
    match status_code:
        case 403:
            return "Web Application Limit has been violated."
        case 409:
            return "Cancel/Replace order partially succesfull."
        case 429:
            return "Request limit broken."
        case 418:
            return "IP has been banned."
        case _:
            return f"Unhandled status code {status_code}: Further investigation needed."


def public_executor(params: dict, endpoint: str) -> dict:
    """
    Executes GET requests for a public endpoint (No key nor signature required).
    Args:
        params (dict): Query parameters.
        endpoint (str): Relative URL to perform the query.
    Returns:
        dict: Parsed JSON response from the API.
    Raises:
        RuntimeError: If the request fails or returns a non-200 status code.
    """
    final_endpoint = URL + endpoint
    try:
        response = requests.get(final_endpoint, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_message = status_analyzer(response.status_code)
            print(f"Error: {error_message}")
        if response.status_code in [403, 418, 429]:
            sys.exit(1)
        raise RuntimeError(f"Request failed with status {response.status_code}: {response.text}")
    except requests.RequestException as e:
        raise RuntimeError(f"Error during request execution: {e}")
  

def private_executor(params: dict, endpoint: str) -> dict:
    """
    Executes a POST requests for a private endpoint (Key and signature required).
    Args:
        method (str): HTTP methos for the query.
        params (dict): Query parameters.
        endpoint (str): Relative URL to perform the query.
    Returns:
        dict: Parsed JSON response from the API.
    Raises:
        RuntimeError: If the request fails or returns a non-200 status code.
    """
    final_endpoint = URL + endpoint
    timestamp = int(time.time() * 1000)
    params["timestamp"] = timestamp
    payload = "&".join([f"{param} = {value}" for param, value in params.items()])
    signature =  base64.b64encode(
        private_key.sign(
            payload.encode('ASCII'),
            PKCS1v15(),
            SHA256()
        )
    )
    params["signature"] = signature
    headers = {
        'X-MBX-APIKEY': API_KEY,
    }
    try:
        response = requests.get(final_endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            error_message = status_analyzer(response.status_code)
            print(f"Error: {error_message}")
        if response.status_code in [403, 418, 429]:
            sys.exit(1)
        raise RuntimeError(f"Request failed with status {response.status_code}: {response.text}")
    except requests.RequestException as e:
        raise RuntimeError(f"Error during request execution: {e}")

def healthcheck() -> bool:
    """
    Verifies the health of the default endpoint by checking its response.
    Returns:
        bool: True if the base endpoint is reachable and functioning correctly 
              (returns an empty dictionary as the response), False otherwise.
    """
    try:
        response = public_executor({}, "/v3/ping")
        return response == {}
    except Exception as e:
        print(f"Healthcheck failed for default endpoint: {URL}: {e}")
        return False



# Testing
# print(healthcheck())











