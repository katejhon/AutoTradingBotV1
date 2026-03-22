import os, time, requests, pandas as pd
from datetime import datetime
from config import BASE_URL, MEXC_API_KEY
from positions import positions
from ws_client import prices

MIN_TRADE = 5  # minimum USDT per trade

# ---------------- ACCOUNT ----------------
def get_balance():
    """Return dict of all non-zero balances from MEXC"""
    try:
        url = f"{BASE_URL}/api/v3/account?timestamp={int(time.time()*1000)}"
        headers = {"X-MEXC-APIKEY": MEXC_API_KEY}
        res = requests.get(url, headers=headers, timeout=10).json()
        return {a['asset']: float(a['free']) for a in res.get('balances', []) if float(a['free']) > 0}
    except:
        return {}

def total_balance():
    """Calculate total balance in USDT including all tokens"""
    bal = get_balance()
    total = 0
    for asset, qty in bal.items():
        if asset == "USDT":
            total += qty
        else:
            total += qty * prices.get(asset + "USDT", 0)
    return total

def get_pnl():
    """Compute PNL based on total balance vs starting balance"""
    if not hasattr(get_pnl, "start_balance"):
        get_pnl.start_balance = total_balance()
        get_pnl.last_day = datetime.now().day

    today = datetime.now().day
    if today != get_pnl.last_day:
        get_pnl.start_balance = total_balance()
        get_pnl.last_day = today

    total = total_balance()
    pnl = total - get_pnl.start_balance
    pct = pnl / get_pnl.start_balance * 100 if get_pnl.start_balance else 0
    return pnl, pct

# ---------------- OHLCV ----------------
def get_ohlcv_df(symbol, interval="1m", limit=50):
    """Fetch latest OHLCV for a symbol"""
    try:
        url = f"{BASE_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
        df = pd.DataFrame(requests.get(url, timeout=10).json(),
                          columns=["open_time","open","high","low","close","volume",
                                   "ct","qav","trades","tb","tq","ignore"])
        df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)
        return df
    except Exception as e:
        print(f"Error fetching OHLCV {symbol}: {e}")
        return pd.DataFrame()

# ---------------- DYNAMIC TOKEN FILTER ----------------
def get_top_tokens(limit=20):
    """Return top tokens based on 24hr volume and price movement"""
    try:
        url = f"{BASE_URL}/api/v3/exchangeInfo"
        res = requests.get(url, timeout=10).json()
        symbols = [s['symbol'] for s in res['symbols'] if s['quoteAsset']=='USDT' and s['status']=='TRADING']
        
        # Filter by 24h volume
        filtered = []
        for s in symbols:
            ticker = requests.get(f"{BASE_URL}/api/v3/ticker/24hr?symbol={s}", timeout=5).json()
            if float(ticker.get('quoteVolume', 0)) > 5000:  # Only liquid tokens
                filtered.append(s)
        return filtered[:limit]
    except Exception as e:
        print(f"Error fetching top tokens: {e}")
        return []
