from datetime import datetime # Python built-in — gets current date/time
import pytz # handles timezones properly

def get_datetime(timezone:str ="UTC")->dict: #in timezone argument nothing passed it will take "UTC" as default
    """
    Get the current date and time for a given timezone.

    Args:
        timezone: Timezone string e.g. 'UTC', 'Europe/London', 'Asia/Kolkata'
                  Defaults to UTC if not provided.

    Returns:
        dict with date, time, timezone, day_of_week
    """

    try:
        tz=pytz.timezone(timezone)
        now=datetime.now(tz)

        return {
        "Status":"Success",
        "timezone":timezone,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "datetime_full": now.strftime("%Y-%m-%d %H:%M:%S %Z")
        }
    except pytz.UnknownTimeZoneError: # Only catches when pytz can't understand your timezone.
        return{"status":"Error",
                "message": f"Unknown timezone: {timezone}. Try 'UTC' or 'Europe/London'."
        }

    except Exception as e: # this exception is to catch everything
        return {"status":"Error",
        "message":str(e)}



