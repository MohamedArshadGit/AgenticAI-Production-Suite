import requests

def get_location()->dict:
    """
    Get the current location of the user based on their IP address.
    Use this when the user asks about their location, nearby places,
    local time, local weather, or any question that needs to know
    where the user currently is.

    Returns:
        dict with city, country, latitude, longitude, timezone
    """
    try:
        response =requests.get("http://ip-api.com/json/",timeout=5) # 5 sec.# ip-api.com detects location from IP address
        data =response.json()
        
        if data.get("status")=="success":
            return{
                "status":data.get("status"),
                "city": data.get("city"),
                "region": data.get("regionName"),
                "country": data.get("country"),
                "latitude": data.get("lat"),
                "longitude": data.get("lon"),
                "timezone": data.get("timezone"),  # e.g. "Europe/London"
                "isp": data.get("isp")

            }
        else:
            return{"status":data.get("status"),
            "message": data.get("message", "Could not determine location.")} #("Could not determine location") fallback if data.get("message") is empty


    except requests.exceptions.ConnectTimeout:

        return {
            "status": "error",
            "message": "Location request timed out. Check your internet connection."
        }
    
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Could not connect to location service. Check your internet."
        }
    except Exception as e:
        return {"status": "error",
                "message": str(e)
                }


    
