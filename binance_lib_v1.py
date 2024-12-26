"""
 V1 functions neccesary to run the Binance API
"""
import base64
import os
import dotenv
import requests
import time

# Temporal imports for tesing
dotenv.load_dotenv()
API = os.getenv("API_KEY")
KEY = os.getenv("SECRET_KEY")
if not API or not KEY:
    raise ValueError("No API key or Secret key found in configuration")
BASE_ENPOINT = "https://api.binance.com"

# General module

def status_analyzer(status_code : str):
    """
    Retrieves a message and performs action based on the requests status.
    Args:
        status_code (str): Status code for the request.
    """
    match status_code:
        case "403":
            return "Web Application Limit has been violated."
        case "409":
            return "Cancel/Replace order partially succesfull."
        case "429":
            return "Request limit broken."
        case "418":
            return "IP has been banned."
        case _:
            return {"code": status_code, "message": msg}

def public_executor(params: dict, url: str) -> dict:
    """
    Executes a GET request for a public endpoint (No key nor signature required).
    Args:
        params (dict): Query parameters.
        url (str): URL to perform the query.
    Returns:
        dict: Contains all the info from the response
    """
    endpoint = BASE_ENPOINT + url
    timestamp = int(time.time() * 1000)
    params["timestamp"] = timestamp
    try:
        response = requests.get(
                endpoint,
                data=params
                )
    except Exception as e:
        raise e
