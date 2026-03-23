import asyncio, time, pandas as pd, requests
from strategy import ai_signal_multi, indicators
from exchange_async import *
from notifier import buy, sell, fail
from state import BotState
from config import COOLDOWN, MIN_TRADE, RISK_PER_TRADE

class Trader:
    def __init__(self, state: BotState, symbols):
        self.state = state
        self.symbols = symbols

    async def get_klines(self, symbol, interval="1m"):
        url = f"{BASE_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit=100"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                df = pd.DataFrame(data)
                df.columns = ["t","o","h","l","c","v","ct","q"]
                for col in ["o","h","l","c","v"]:
                    df[col] = df[col].astype(float)
                return df

    async def get_multi_tf(self, symbol):
        df1 = indicators(await self.get_klines(symbol))
        df5 = indicators(await self.get_klines(symbol, "5m"))
        df15 = indicators(await self.get_klines(symbol, "15m"))
        return df1, df5, df15

    async def trade_symbol(self, symbol):
        if symbol in self.state.last_trade and time.time() - self.state.last_trade[symbol] < COOLDOWN:
            return

        df1, df5, df15 = await self.get_multi_tf(symbol)
        if not ai_signal_multi(df1, df5, df15):
            return
        if not self.state.can_trade():
            return

        balance = await get_balance()
        usdt = max(MIN_TRADE, balance * RISK_PER_TRADE)
        price = self.state.price_cache.get(symbol, df1['c'].iloc[-1])
        qty = float(f"{usdt / price:.6f}")

        try:
            executed_qty, avg_price = await market_buy(symbol, qty)
            tp = avg_price * 1.01
            sl = avg_price * 0.99

            self.state.positions[symbol] = {"entry": avg_price, "qty": executed_qty, "tp": tp, "sl": sl}
            self.state.save_positions()

            await buy(symbol, avg_price, executed_qty, tp, sl)

            self.state.last_trade[symbol] = time.time()
            self.state.trades_today += 1
            self.state.save_risk()
        except Exception as e:
            await fail(symbol, str(e))

    async def monitor_positions(self):
        while True:
            for symbol, pos in list(self.state.positions.items()):
                price = self.state.price_cache.get(symbol, await get_price(symbol))
                if price >= pos['tp'] or price <= pos['sl']:
                    try:
                        qty, sell_price = await market_sell(symbol, pos['qty'])
                        pnl = (sell_price - pos['entry']) / pos['entry'] * 100
                        await sell(symbol, pos['qty'], sell_price * qty, pnl)
                        del self.state.positions[symbol]
                        self.state.save_positions()
                    except Exception as e:
                        await fail(symbol, str(e))
            await asyncio.sleep(2)