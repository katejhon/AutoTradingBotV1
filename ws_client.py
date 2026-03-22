import asyncio, websockets, json
from config import WS_URL

prices = {}

async def ws_subscribe(symbols):
    while True:
        try:
            async with websockets.connect(WS_URL) as ws:
                for s in symbols:
                    sub = {
                        "method": "SUBSCRIPTION",
                        "params": [f"spot@public.deals.v3.api@{s}"],
                        "id": 1
                    }
                    await ws.send(json.dumps(sub))

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if "d" in data:
                        symbol = data["s"]
                        price = float(data["d"]["p"])
                        prices[symbol] = price

        except:
            await asyncio.sleep(5)