import asyncio, json, websockets
from logger import log_error, log_info
from notifier import alert

WS_URL = "wss://wbs.mexc.com/ws"

async def websocket_prices(symbols, cache):
    while True:
        try:
            async with websockets.connect(
                WS_URL,
                ping_interval=20,
                ping_timeout=10
            ) as ws:

                for s in symbols:
                    await ws.send(json.dumps({
                        "method": "SUBSCRIPTION",
                        "params": [f"spot@public.ticker.v3.api@{s}"],
                        "id": 1
                    }))

                log_info("✅ WebSocket Connected")

                while True:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=30)
                        data = json.loads(msg)

                        if "d" in data:
                            cache[data["s"]] = float(data["d"]["p"])

                    except asyncio.TimeoutError:
                        # keep connection alive
                        await ws.ping()

        except Exception as e:
            log_error(f"WS Error: {e}")
            log_error(f"WebSocket reconnecting...\n{e}")
            await asyncio.sleep(5)
