from utils import request, sign, safe_div
from config import BASE_URL, API_KEY, API_SECRET, ADJUST_STEP
import asyncio

async def send_failed(bot, symbol, price, qty, reason):
    msg = f"⚠️ BUY FAILED\nToken: {symbol}\nPrice: {price}\nVolume: {qty}\nReason: {reason}"
    await bot.send_message(chat_id=bot.chat_id, text=msg)

def place_market(symbol, qty, side, bot=None):
    original_qty = qty
    while True:
        price = get_price(symbol)
        if price <= 0:
            if bot: asyncio.create_task(send_failed(bot, symbol, price, original_qty, "No price"))
            return {}
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": round(qty,6),
            "timestamp": int(time.time()*1000)
        }
        res = request(BASE_URL+"/api/v3/order?"+sign(params,API_SECRET),
                      headers={"X-MEXC-APIKEY":API_KEY}, method="POST")
        if "orderId" in res:
            return res
        qty += ADJUST_STEP
        if bot: asyncio.create_task(send_failed(bot, symbol, price, original_qty, "Retry +0.5 USDT"))

def place_oco(symbol, qty, tp_price, sl_price):
    params = {
        "symbol": symbol,
        "side": "SELL",
        "quantity": round(qty,6),
        "price": round(tp_price,6),
        "stopPrice": round(sl_price,6),
        "timestamp": int(time.time()*1000)
    }
    res = request(BASE_URL+"/api/v3/order/oco?"+sign(params,API_SECRET),
                  headers={"X-MEXC-APIKEY":API_KEY}, method="POST")
    return res.get("orderId")

def get_price(symbol):
    try:
        res = request(BASE_URL + f"/api/v3/ticker/price?symbol={symbol}")
        return float(res.get("price",0))
    except:
        return 0
