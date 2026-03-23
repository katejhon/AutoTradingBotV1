# exchange_async.py
import aiohttp, time, hmac, hashlib
from urllib.parse import urlencode
from config import *

async def sign(params):
    query = urlencode(params)
    sig = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={sig}"

async def request(method, path, params={}):
    params["timestamp"] = int(time.time() * 1000)
    query = await sign(params)
    headers = {"X-MEXC-APIKEY": API_KEY}

    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(BASE_URL + path + "?" + query, headers=headers) as resp:
                return await resp.json()
        async with session.post(BASE_URL + path, data=query, headers=headers) as resp:
            return await resp.json()

async def get_all_balances():
    data = await request("GET", "/api/v3/account")
    balances = {}
    for b in data.get("balances", []):
        total = float(b.get("free", 0)) + float(b.get("locked", 0))
        if total > 0:
            balances[b["asset"]] = total
    return balances

async def get_balance():
    balances = await get_all_balances()
    return balances.get("USDT", 0)

async def get_price(symbol):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/v3/ticker/price?symbol={symbol}") as resp:
            data = await resp.json()
            return float(data["price"])

async def get_top_symbols(limit=50):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/v3/ticker/24hr") as resp:
            data = await resp.json()
            sorted_pairs = sorted(data, key=lambda x: float(x['quoteVolume']), reverse=True)
            return [d['symbol'] for d in sorted_pairs if "USDT" in d['symbol']][:limit]

async def market_buy(symbol, qty):
    res = await request("POST", "/api/v3/order", {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quantity": qty
    })

    if 'orderId' not in res:
        raise Exception(f"Buy failed: {res}")

    order = await get_order(symbol, res['orderId'])
    if order.get("status") != "FILLED":
        raise Exception(f"Order not filled: {order}")

    executed_qty = float(order["executedQty"])
    avg_price = float(order["cummulativeQuoteQty"]) / executed_qty
    return executed_qty, avg_price

async def market_sell(symbol, qty):
    res = await request("POST", "/api/v3/order", {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": qty
    })

    if 'orderId' not in res:
        raise Exception(f"Sell failed: {res}")

    order = await get_order(symbol, res['orderId'])
    if order.get("status") != "FILLED":
        raise Exception(f"Sell not filled: {order}")

    executed_qty = float(order["executedQty"])
    avg_price = float(order["cummulativeQuoteQty"]) / executed_qty
    return executed_qty, avg_price

async def get_my_trades(symbol, limit=50):
    return await request("GET", "/api/v3/myTrades", {
        "symbol": symbol,
        "limit": limit
    })

async def get_order(symbol, order_id):
    return await request("GET", "/api/v3/order", {
        "symbol": symbol,
        "orderId": order_id
    })