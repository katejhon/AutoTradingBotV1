# report.py
from positions import positions
from utils import total_balance, get_pnl, prices
import asyncio

async def send_report(bot):
    """Send 5-minutes report with all tokens held, ranked by PNL"""
    total = total_balance()
    pnl, pct = get_pnl()

    # Collect data for tokens held
    token_list = []
    for symbol, pos in positions.items():
        # Skip if qty is zero
        if pos.qty <= 0:
            continue

        token_price = prices.get(symbol, pos.entry)
        pnl_token_pct = (token_price - pos.entry) / pos.entry * 100
        token_list.append({
            'symbol': symbol,
            'price': token_price,
            'entry': pos.entry,
            'qty': pos.qty - pos.executed_qty,
            'pnl': pnl_token_pct
        })

    # Sort by PNL descending
    token_list.sort(key=lambda x: x['pnl'], reverse=True)

    # Build the message
    msg = f"📊 5-MIN REPORT\n💰 Balance: {total:.2f} USDT\n📈 PNL: {pct:.2f}%\n\n"
    for t in token_list:
        msg += (
            f"{t['symbol']}\n"
            f"Token Price: {t['price']:.4f}\n"
            f"Entry: {t['entry']:.4f}\n"
            f"Qty: {t['qty']:.6f}\n"
            f"PNL: {t['pnl']:.2f}%\n\n"
        )

    # Send report
    await bot.send_message(chat_id=bot.chat_id, text=msg)