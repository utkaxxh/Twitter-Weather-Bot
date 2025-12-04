import tweepy
import requests
import os
import sys
from datetime import datetime
import pytz

# 1. Load Environment Variables
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")

# 2. Verify variables
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, OPENWEATHER_API_KEY]):
    print("❌ Error: One or more environment variables are missing.")
    sys.exit(1)

def calculate_aqi(pm25):
    """
    Converts raw PM2.5 (µg/m³) to US EPA AQI (0-500 scale).
    Formula based on standard US EPA breakpoints.
    """
    c = float(pm25)
    
    # Breakpoints: (Concentration Low, Concentration High, Index Low, Index High)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500)
    ]

    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= c <= c_high:
            aqi = ((i_high - i_low) / (c_high - c_low)) * (c - c_low) + i_low
            return int(round(aqi))
    
    # If off the charts (>500.4), just return 500+
    return 500

def get_aqi_label(aqi_score):
    """
    Returns label and emoji based on the 0-500 AQI score
    """
    if aqi_score <= 50:
        return "Good", "🟢", ""
    elif aqi_score <= 100:
        return "Moderate", "🟡", ""
    elif aqi_score <= 150:
        return "Unhealthy for Sensitive Groups", "🟠", "\n⚠️ Sensitive groups should wear masks."
    elif aqi_score <= 200:
        return "Unhealthy", "🔴", "\n⚠️ Air is unhealthy. Wear a mask."
    elif aqi_score <= 300:
        return "Very Unhealthy", "🟣", "\n⚠️ Health alert! Avoid outdoor activities."
    else:
        return "Hazardous", "☠️", "\n🚨 Emergency conditions!"

def get_weather_data():
    try:
        # --- STEP 1: Weather & Coords ---
        city = "Nagpur"
        country_code = "IN"
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={OPENWEATHER_API_KEY}&units=metric"
        
        response = requests.get(weather_url)
        data = response.json()
        
        if response.status_code != 200:
            print(f"❌ Error fetching weather: {data.get('message', 'Unknown error')}")
            sys.exit(1)
            
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]

        # --- STEP 2: Air Quality ---
        aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        aqi_response = requests.get(aqi_url)
        aqi_data = aqi_response.json()

        aqi_score = "N/A"
        aqi_label = "N/A"
        warning_emoji = ""
        health_tip = ""

        if aqi_response.status_code == 200:
            # 1. Get raw PM2.5 (µg/m³)
            pm2_5_raw = aqi_data['list'][0]['components']['pm2_5']
            
            # 2. Convert to US EPA scale (0-500)
            aqi_score = calculate_aqi(pm2_5_raw)
            
            # 3. Get label
            aqi_label, warning_emoji, health_tip = get_aqi_label(aqi_score)

        # --- Format Tweet ---
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).strftime("%d %b %Y")
        
        tweet_text = (
            f"📍 Weather Update for #Nagpur ({today})\n\n"
            f"🌡️ Temperature: {temp}°C\n"
            f"☁️ Condition: {desc}\n"
            f"💧 Humidity: {humidity}%\n"
            f"🍃 Air Quality: {aqi_label} ({aqi_score}) {warning_emoji}"
            f"{health_tip}\n\n"
        )
        return tweet_text

    except Exception as e:
        print(f"❌ Exception in get_weather_data: {e}")
        sys.exit(1)

def post_tweet(text):
    try:
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )

        response = client.create_tweet(text=text)
        print(f"✅ Tweet posted successfully! Tweet ID: {response.data['id']}")
        
    except tweepy.Errors.Forbidden as e:
        print(f"❌ 403 Forbidden Error. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Weather Bot...")
    weather_update = get_weather_data()
    print(f"📝 Generated Tweet:\n{weather_update}")
    post_tweet(weather_update)
