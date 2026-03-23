import asyncio, json, websockets

WS_URL = "wss://wbs.mexc.com/ws"

async def websocket_prices(symbols, price_cache):
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                for symbol in symbols:
                    await ws.send(json.dumps({
                        "method": "SUBSCRIPTION",
                        "params": [f"spot@public.deals.v3.api@{symbol}"],
                        "id": 1
                    }))
                print("✅ WebSocket Connected")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if "d" in data:
                        try:
                            symbol = data["s"]
                            price = float(data["d"]["p"])
                            price_cache[symbol] = price
                        except:
                            continue
        except Exception as e:
            print("⚠️ WS Reconnecting:", e)
            await asyncio.sleep(5)