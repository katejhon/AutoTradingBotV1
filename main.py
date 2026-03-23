import asyncio
from state import BotState
from trader import Trader
from notifier import start
from report import loop as report_loop
from websocket import websocket_prices
from exchange_async import get_top_symbols
from sync import sync_positions

async def main():
    state = BotState()
    await start()
    symbols = await get_top_symbols()
    trader = Trader(state, symbols)

    await sync_positions(state, symbols)

    asyncio.create_task(websocket_prices(symbols, state.price_cache))
    await asyncio.gather(
        trader.monitor_positions(),
        report_loop(state),
        trader_loop(trader)
    )

async def trader_loop(trader):
    while True:
        for symbol in trader.symbols:
            await trader.trade_symbol(symbol)
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())