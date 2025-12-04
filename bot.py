import os
import sys
import requests
from datetime import datetime, timedelta

CITY = "Nagpur"
LAT = 21.1458
LON = 79.0882


# ------------------------------------------------
# TWEET USING TWITTER API V2
# ------------------------------------------------
def tweet(text):
    bearer = os.getenv("TWITTER_BEARER_TOKEN")

    if not bearer:
        print("Missing TWITTER_BEARER_TOKEN!")
        return

    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={"text": text}, headers=headers)

    if response.status_code != 201:
        print("Tweet failed:", response.status_code, response.text)
    else:
        print("Tweet posted:", text)


# ------------------------------------------------
# WEATHER from OpenWeather
# ------------------------------------------------
def get_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "Missing OPENWEATHER_API_KEY"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={api_key}&units=metric"
    r = requests.get(url).json()

    try:
        temp = r["main"]["temp"]
        humidity = r["main"]["humidity"]
        desc = r["weather"][0]["description"].title()
        wind = r["wind"]["speed"]

        return (
            f"{CITY} Weather Update\n"
            f"{desc}\n"
            f"Temp: {temp}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind: {wind} m/s"
        )
    except Exception:
        return "Weather data unavailable right now."


# ------------------------------------------------
# AQI from OpenWeather (Air Pollution API)
# ------------------------------------------------
def get_aqi():
    api_key = os.getenv("OPENWEATHER_API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={api_key}"
    r = requests.get(url).json()

    try:
        aqi_index = r["list"][0]["main"]["aqi"]
        pm25 = r["list"][0]["components"]["pm2_5"]

        # AQI meaning per OpenWeather scale
        meaning = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }.get(aqi_index, "Unknown")

        return (
            f"{CITY} Air Quality Update\n"
            f"AQI: {aqi_index} ({meaning})\n"
            f"PM2.5: {pm25} µg/m³"
        )
    except Exception:
        return f"AQI data unavailable for {CITY} right now."


# ------------------------------------------------
# SUNSET (sunrise-sunset API)
# ------------------------------------------------
def get_sunset():
    url = f"https://api.sunrise-sunset.org/json?lat={LAT}&lng={LON}&formatted=0"
    r = requests.get(url).json()

    try:
        sunset_utc = r["results"]["sunset"]

        sunset_local = (
            datetime.fromisoformat(sunset_utc.replace("Z", "+00:00"))
            + timedelta(hours=5, minutes=30)
        )
        sunset_str = sunset_local.strftime("%I:%M %p")

        return f"{CITY} Sunset Time\nSunset today at {sunset_str}"

    except Exception:
        return "Sunset data not available."


# ------------------------------------------------
# MAIN HANDLER
# ------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bot.py [weather|aqi|sunset]")
        sys.exit(1)

    task = sys.argv[1].lower()

    if task == "weather":
        tweet(get_weather())

    elif task == "aqi":
        tweet(get_aqi())

    elif task == "sunset":
        tweet(get_sunset())

    else:
        print("Unknown command:", task)
