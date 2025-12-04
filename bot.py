import os
import sys
import requests
import tweepy
from datetime import datetime

CITY = "Nagpur"
LAT = 21.1458
LON = 79.0882

# Twitter authentication
def twitter_client():
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_SECRET")

    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    return tweepy.API(auth)


# 1. WEATHER (Open Meteo)
def fetch_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&current_weather=true"
    )

    r = requests.get(url)
    data = r.json()

    cw = data.get("current_weather", {})
    temp = cw.get("temperature")
    wind = cw.get("windspeed")
    code = cw.get("weathercode")

    condition = weather_code_to_text(code)

    return f"🌤 Nagpur Morning Weather\n\nTemperature: {temp}°C\nWind: {wind} km/h\nCondition: {condition}"


# Simple mapping for open meteo codes
def weather_code_to_text(code):
    mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Rime Fog",
        51: "Light Drizzle",
        53: "Moderate Drizzle",
        55: "Dense Drizzle",
        61: "Light Rain",
        63: "Moderate Rain",
        65: "Heavy Rain",
        71: "Light Snow",
        80: "Rain showers",
    }
    return mapping.get(code, "Weather update")


# 2. AQI (World Air Quality Index)
def fetch_aqi():
    token = os.getenv("OPENWEATHER_API_KEY")  # Reusing same variable name for simplicity
    if not token:
        return "AQI token missing."

    url = f"https://api.waqi.info/feed/{CITY}/?token={token}"

    r = requests.get(url)
    data = r.json()

    if data.get("status") != "ok":
        return "AQI data not available."

    aqi = data["data"]["aqi"]

    return f"🌫 Nagpur Air Quality Update\n\nAQI: {aqi}\nStatus: {aqi_category(aqi)}"


def aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very Unhealthy"
    return "Hazardous"


# 3. SUNSET (Open Meteo)
def fetch_sunset():
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&daily=sunset"
        f"&timezone=Asia/Kolkata"
    )
    r = requests.get(url)
    data = r.json()

    sunset = data["daily"]["sunset"][0]
    return f"🌇 Nagpur Sunset Today\n\nSunset Time: {sunset}"


# Tweet helper
def tweet(text):
    try:
        api = twitter_client()
        api.update_status(text)
        print("Tweet posted.")
    except Exception as e:
        print("Error tweeting:", e)


# Entry point
def main():
    if len(sys.argv) < 2:
        print("Usage: python bot.py [weather|aqi|sunset]")
        return

    mode = sys.argv[1]

    if mode == "weather":
        tweet(fetch_weather())
    elif mode == "aqi":
        tweet(fetch_aqi())
    elif mode == "sunset":
        tweet(fetch_sunset())
    else:
        print("Invalid argument.")


if __name__ == "__main__":
    main()

