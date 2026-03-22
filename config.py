import os
from dotenv import load_dotenv

load_dotenv()

MEXC_API_KEY = os.getenv("MEXC_API_KEY")
MEXC_SECRET_KEY = os.getenv("MEXC_SECRET_KEY")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = "https://api.mexc.com"
WS_URL = "wss://wbs.mexc.com/ws"

MIN_TRADE = 5
REPORT_INTERVAL = 300
BALANCE_FILE = "balance.json"