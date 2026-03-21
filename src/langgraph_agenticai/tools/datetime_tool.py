from datetime import datetime
import pytz
from langchain_core.tools import tool

@tool
def get_datetime(timezone: str = "UTC") -> str:
    """
    Get the current date and time for a given timezone.
    Use this when the user asks about current time, date, or day of the week.
    Timezone string e.g. 'UTC', 'Europe/London', 'Asia/Kolkata'. Defaults to UTC.
    """
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)

        return (
            f"Timezone: {timezone}, "
            f"Date: {now.strftime('%Y-%m-%d')}, " # strftime = string format time .It converts a datetime object into a readable string.
            f"Time: {now.strftime('%H:%M:%S')}, "
            f"Day: {now.strftime('%A')}, "
            f"Full: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )

    except pytz.UnknownTimeZoneError: # Only catches when pytz can't understand your timezone.
        return f"Unknown timezone: '{timezone}'. Try 'UTC' or 'Europe/London'."
    
    except Exception as e: # this exception is to catch everything
        return f"Error: {str(e)}"

# Python has special codes for each part of date/time:
# pythonnow.strftime("%A")    # Saturday        → full weekday name
# now.strftime("%a")    # Sat             → short weekday name
# now.strftime("%d")    # 21              → day number
# now.strftime("%B")    # March           → full month name
# now.strftime("%b")    # Mar             → short month name
# now.strftime("%Y")    # 2026            → full year
# now.strftime("%y")    # 26              → short year
# now.strftime("%H")    # 14              → hour (24hr)
# now.strftime("%I")    # 02              → hour (12hr)
# now.strftime("%M")    # 30              → minutes
# now.strftime("%S")    # 45              → seconds
# now.strftime("%p")    # PM              → AM/PM


