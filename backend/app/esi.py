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

def get_regions():
    """
    Fetches a list of all region IDs from the ESI API.
    """
    url = f"{settings.ESI_BASE_URL}/universe/regions/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching regions: {e}")
        return []

def get_region_info(region_id: int):
    """
    Fetches information for a given region_id from the ESI API.
    """
    url = f"{settings.ESI_BASE_URL}/universe/regions/{region_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching region info for region_id {region_id}: {e}")
        return None

def get_item_categories():
    """
    Fetches a list of all item category IDs from the ESI API.
    """
    url = f"{settings.ESI_BASE_URL}/universe/categories/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching item categories: {e}")
        return []

def get_item_category_info(category_id: int):
    """
    Fetches information for a given category_id from the ESI API.
    """
    url = f"{settings.ESI_BASE_URL}/universe/categories/{category_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching item category info for category_id {category_id}: {e}")
        return None