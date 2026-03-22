import time, requests
from config import BASE_URL, MEXC_API_KEY

def place_market(symbol, side, qty):
    """Place a market order"""
    while True:
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": qty,
            "timestamp": int(time.time()*1000)
        }
        res = requests.post(BASE_URL + "/api/v3/order?" + sign(params),
                            headers={"X-MEXC-APIKEY": MEXC_API_KEY}).json()
        if "orderId" in res:
            return res
        qty += 0.5

def fetch_open_orders():
    """Fetch all current open orders"""
    try:
        params = {"timestamp": int(time.time()*1000)}
        url = f"{BASE_URL}/api/v3/openOrders?{sign(params)}"
        headers = {"X-MEXC-APIKEY": MEXC_API_KEY}
        return requests.get(url, headers=headers, timeout=10).json()
    except:
        return []

def load_existing_positions():
    """Load open positions from open orders"""
    orders = fetch_open_orders()
    from positions import add_position
    from ws_client import prices
    for order in orders:
        symbol = order['symbol']
        side = order['side']
        qty = float(order['origQty'])
        price = float(order['price']) if order['price'] != "0" else prices.get(symbol, 0)
        if side == "BUY":
            atr = 0.5 * price
            tp_orders = [
                {"price": price + atr, "qty": qty * 0.3, "executed": False},
                {"price": price + atr * 1.5, "qty": qty * 0.4, "executed": False},
                {"price": price + atr * 2, "qty": qty * 0.3, "executed": False},
            ]
            sl_price = price * 0.97
            add_position(symbol, price, qty, tp_orders, sl_price)
