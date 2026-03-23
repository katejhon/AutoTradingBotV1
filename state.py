import json, os
from config import *

POSITIONS_FILE = "positions.json"
RISK_FILE = "risk.json"

class BotState:
    def __init__(self):
        self.positions = {}
        self.last_trade = {}
        self.price_cache = {}
        self.trades_today = 0
        self.daily_pnl = 0
        self.load_positions()
        self.load_risk()

    # ---------------- Positions ----------------
    def load_positions(self):
        if os.path.exists(POSITIONS_FILE):
            with open(POSITIONS_FILE) as f:
                self.positions = json.load(f)

    def save_positions(self):
        with open(POSITIONS_FILE, "w") as f:
            json.dump(self.positions, f, indent=4)

    # ---------------- Risk ----------------
    def load_risk(self):
        if os.path.exists(RISK_FILE):
            with open(RISK_FILE) as f:
                data = json.load(f)
                self.trades_today = data.get("trades_today", 0)
                self.daily_pnl = data.get("daily_pnl", 0)

    def save_risk(self):
        with open(RISK_FILE, "w") as f:
            json.dump({
                "trades_today": self.trades_today,
                "daily_pnl": self.daily_pnl
            }, f)

    def can_trade(self):
        return self.trades_today < MAX_TRADES_PER_DAY and self.daily_pnl > MAX_DRAWDOWN