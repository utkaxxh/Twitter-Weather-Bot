import os
import requests
from datetime import datetime
import pytz
import tweepy

# -----------------------------------
# CONFIG
CITY = "Nagpur"
COUNTRY = "IN"
TIMEZONE = "Asia/Kolkata"

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
AQI_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

# Twitter (X) API
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# -----------------------------------
# AUTH
def twitter_client():
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )
    return tweepy.API(auth)

# -----------------------------------
# FETCH WEATHER
def fetch_weather():
    params = {
        "q": f"{CITY},{COUNTRY}",
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    resp = requests.get(WEATHER_URL, params=params).json()
    temp = resp["main"]["temp"]
    desc = resp["weather"][0]["description"].title()
    humidity = resp["main"]["humidity"]
    feels = resp["main"]["feels_like"]
    return f"Weather update for {CITY}: {temp}°C, {desc}. Feels like {feels}°C. Humidity {humidity}%."

# -----------------------------------
# FETCH AQI
def fetch_aqi():
    params = {
        "q": f"{CITY},{COUNTRY}",
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }
    # fetch lat/lon first
    w = requests.get(WEATHER_URL, params=params).json()
    lat = w["coord"]["lat"]
    lon = w["coord"]["lon"]

    resp = requests.get(AQI_URL, params={"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY}).json()
    aqi = resp["list"][0]["main"]["aqi"]

    aqi_text = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",

