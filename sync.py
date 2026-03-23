from exchange_async import get_all_balances, get_my_trades
from state import BotState

async def sync_positions(state: BotState, symbols):
    balances = await get_all_balances()
    new_positions = {}

    for symbol in symbols:
        asset = symbol.replace("USDT", "")
        qty = balances.get(asset, 0)
        if qty <= 0:
            continue

        try:
            trades = await get_my_trades(symbol)
            total_qty = 0
            total_cost = 0
            for t in trades:
                if t["isBuyer"]:
                    q = float(t["qty"])
                    p = float(t["price"])
                    total_qty += q
                    total_cost += q * p

            if total_qty > 0:
                entry = total_cost / total_qty
                new_positions[symbol] = {
                    "entry": entry,
                    "qty": qty,
                    "tp": entry * 1.01,
                    "sl": entry * 0.99
                }
        except:
            continue

    state.positions.clear()
    state.positions.update(new_positions)
    state.save_positions()