import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY", "")

if not TELEGRAM_TOKEN:
    print("⚠️ Warning: TELEGRAM_TOKEN not found in environment variables.")
if not OPENWEATHER_KEY:
    print("⚠️ Warning: OPENWEATHER_KEY not found in environment variables.")
