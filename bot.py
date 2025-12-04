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

# 2. Debugging: Verify variables are present (without printing the actual secrets)
if not all([CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, OPENWEATHER_API_KEY]):
    print("❌ Error: One or more environment variables are missing.")
    sys.exit(1)

def get_weather():
    try:
        # Nagpur coordinates or query
        city = "Nagpur"
        country_code = "IN"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&appid={OPENWEATHER_API_KEY}&units=metric"
        
        response = requests.get(url)
        data = response.json()
        
        if response.status_code != 200:
            print(f"❌ Error fetching weather: {data.get('message', 'Unknown error')}")
            sys.exit(1)
            
        # Extract data
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        
        # Get current date for Nagpur
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist).strftime("%d %b %Y")
        
        # Format the tweet text
        tweet_text = (
            f"📍 Weather Update for #Nagpur ({today})\n\n"
            f"🌡️ Temperature: {temp}°C\n"
            f"☁️ Condition: {desc}\n"
            f"💧 Humidity: {humidity}%\n\n"
            f"#NagpurWeather #WeatherUpdate"
        )
        return tweet_text

    except Exception as e:
        print(f"❌ Exception in get_weather: {e}")
        sys.exit(1)

def post_tweet(text):
    try:
        # 3. Authenticate with Twitter API v2 (Required for Free Tier)
        client = tweepy.Client(
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_TOKEN_SECRET
        )

        # 4. Post the tweet
        response = client.create_tweet(text=text)
        print(f"✅ Tweet posted successfully! Tweet ID: {response.data['id']}")
        
    except tweepy.Errors.Forbidden as e:
        print(f"❌ 403 Forbidden Error. This usually means your API keys don't have Write permissions.")
        print(f"Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting Weather Bot...")
    weather_update = get_weather()
    print(f"📝 Generated Tweet:\n{weather_update}")
    post_tweet(weather_update)
