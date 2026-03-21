import requests
from langchain_core.tools import tool

@tool
def get_location() -> str:
    """
    Get the current location of the user based on their IP address.
    Use this when the user asks about their location, nearby places,
    local time, local weather, or any question that needs to know
    where the user currently is.
    """
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5) # 5 sec.# ip-api.com detects location from IP address
        data =response.json()
        data = response.json()

        if data.get("status") == "success":
            return (
                f"City: {data.get('city')}, "
                f"Region: {data.get('regionName')}, "
                f"Country: {data.get('country')}, "
                f"Latitude: {data.get('lat')}, "
                f"Longitude: {data.get('lon')}, "
                f"Timezone: {data.get('timezone')}, "
                f"ISP: {data.get('isp')}"
            )
        else:
            return f"Could not determine location: {data.get('message', 'Unknown error')}"

    except requests.exceptions.ConnectTimeout:
        return "Location request timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return "Could not connect to location service. Check your internet."
    except Exception as e:
        return f"Error: {str(e)}"


    
