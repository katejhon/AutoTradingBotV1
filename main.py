import asyncio
from state import BotState
from trader import Trader
from websocket import websocket_prices
from notifier import start
from exchange_async import get_top_symbols
from config import ACCOUNTS
from report import loop as report_loop


async def trade_loop(trader):
    while True:
        await asyncio.gather(*(trader.trade(s) for s in trader.symbols))
        await asyncio.sleep(0.5)


async def main():
    state = BotState()
    await start()

    symbols = await get_top_symbols()

    asyncio.create_task(websocket_prices(symbols, state.price_cache))

    tasks = []

    for acc in ACCOUNTS:
        trader = Trader(state, symbols, acc)

        tasks.append(asyncio.create_task(trader.monitor()))

        tasks.append(asyncio.create_task(trade_loop(trader)))

    tasks.append(asyncio.create_task(report_loop(state)))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
