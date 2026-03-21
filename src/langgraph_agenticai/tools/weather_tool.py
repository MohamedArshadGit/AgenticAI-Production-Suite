import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
load_dotenv()

@tool
def get_weather(city: str = None, latitude: float = None, longitude: float = None) -> str:
    """
    Get current weather conditions for a city or coordinates.
    Use this when the user asks about weather, temperature, forecast,
    or climate conditions anywhere.

    You can call this tool in two ways:
        1. By city name  : get_weather(city="London")
        2. By coordinates: get_weather(latitude=51.5, longitude=-0.1)

    When the user asks about weather in THEIR location, first call
    get_location() to get their coordinates, then pass latitude and
    longitude here directly.

    Examples:
        "What is the weather in Dubai?"     → city="Dubai"
        "Is it raining in Paris?"           → city="Paris"
        "What is the weather here?"         → use get_location() first,
                                              then pass lat/lon here
    """
    try:
        api_key = os.getenv('OPENWEATHER_API_KEY')

        if not api_key:
            return "Error: OPENWEATHER_API_KEY not found in environment variables."

        # OpenWeatherMap url
        base_url = "https://api.openweathermap.org/data/2.5/weather"

        if latitude is not None and longitude is not None: # y we use not none? and not this-> if latitude and longitude : Ans: if latitude and longitude:# 0.0 is falsy → False — misses valid coordinate
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": api_key,
                "units": "metric"    # celsius, use "imperial" for fahrenheit
            }
        elif city is not None:
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric"
            }
        else:
            return "Error: Please provide either a city name or latitude and longitude."

        response = requests.get(base_url, params=params, timeout=5)
        data = response.json()

        # OpenWeatherMap returns cod 200 for success
        if data.get("cod") != 200:
            return f"Error: {data.get('message', 'Could not fetch weather data.')}"

        # extract weather details from response
        weather = data.get("weather", [{}])[0]  # first weather condition
        #                              ^^^^
        #                              fallback is list with empty dict
        #                              so [0] never crashes
        main = data.get("main", {})
        wind = data.get("wind", {})
        sys = data.get("sys", {})

        return (
            f"City: {data.get('name')}, "
            f"Country: {sys.get('country')}, "
            f"Temperature: {main.get('temp')}°C, "
            f"Feels Like: {main.get('feels_like')}°C, "
            f"Min: {main.get('temp_min')}°C, "
            f"Max: {main.get('temp_max')}°C, "
            f"Humidity: {main.get('humidity')}%, "
            f"Description: {weather.get('description')}, "
            f"Wind Speed: {wind.get('speed')} m/s, "
            f"Visibility: {data.get('visibility')} m"
        )

    except requests.exceptions.Timeout:
        return "Error: Weather request timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to weather service."
    except Exception as e:
        return f"Error: {str(e)}"