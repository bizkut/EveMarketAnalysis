import requests
from .config import settings

def get_market_history(type_id: int, region_id: int):
    """
    Fetches market history for a given item type and region from the ESI API.
    """
    url = f"{settings.ESI_BASE_URL}/markets/{region_id}/history/"
    params = {"type_id": type_id}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market history for type_id {type_id}: {e}")
        return None

def get_type_name(type_id: int):
    """
    Fetches the name for a given type_id from the ESI API.
    """
    url = f"{settings.ESI_BASE_URL}/universe/types/{type_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("name", "Unknown")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching type name for type_id {type_id}: {e}")
        return "Unknown"