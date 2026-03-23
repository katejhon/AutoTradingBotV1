import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MEXC_API_KEY")
API_SECRET = os.getenv("MEXC_SECRET_KEY")
BASE_URL = "https://api.mexc.com"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MIN_TRADE = 5
TRADE_INCREMENT = 0.5
RISK_PER_TRADE = 0.05
MAX_TRADES_PER_DAY = 50
MAX_DRAWDOWN = -5
COOLDOWN = 300