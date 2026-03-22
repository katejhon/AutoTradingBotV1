# main.py
import asyncio
from dotenv import load_dotenv
import os
from telegram import Bot
from ws_client import ws_subscribe
from orders import place_market, load_existing_positions
from strategy import decide_buy, compute_tp
from report import send_report
from positions import positions, add_position, remove_position
from utils import get_top_tokens, get_ohlcv_df, total_balance, prices, MIN_TRADE

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# ---------------- TRADE LOOP ----------------
async def trade_loop():
    await bot.send_message(chat_id=CHAT_ID, text="♻️ Bot restarted (Ultra Mode)")
    load_existing_positions()  # sync function
    all_pairs = get_top_tokens(50)
    asyncio.create_task(ws_subscribe(symbols))

    last_report = 0

    while True:
        try:
            bal = total_balance()
            usdt_bal = bal  # total USDT equivalent
            for s in all_pairs:
                price = prices.get(s, 0)
                if price == 0:
                    continue

                # Fetch OHLCV for strategy
                df = get_ohlcv_df(s)
                if df.empty:
                    continue

                # ---------------- BUY LOGIC ----------------
                if s not in positions and decide_buy(df):
                    trade_usdt = max(MIN_TRADE, usdt_bal * 0.02)
                    qty = trade_usdt / price
                    try:
                        res = place_market(s, "BUY", qty)
                        atr = df.iloc[-1]["close"] * 0.01  # example ATR
                        tp_levels = compute_tp(price, atr, qty)
                        sl_price = price * 0.97
                        add_position(s, price, qty, tp_levels, sl_price)

                        # Notification
                        await bot.send_message(chat_id=CHAT_ID,
                                               text=f"Buy\nToken: {s}\nPrice: {price:.4f}\nQty: {qty:.6f}\nTP: {tp_levels[-1]['price']:.4f}\nSL: {sl_price:.4f}")
                    except Exception as e:
                        await bot.send_message(chat_id=CHAT_ID,
                                               text=f"Buy Failed\nToken: {s}\nPrice: {price:.4f}\nQty: {qty:.6f}\nReason: {e}")

                # ---------------- TP/SL ----------------
                if s in positions:
                    pos = positions[s]
                    cp = price
                    # TP
                    for tp in pos.tp_orders:
                        if not tp["executed"] and cp >= tp["price"]:
                            tp_qty = tp["qty"]
                            if pos.qty - pos.executed_qty < MIN_TRADE:
                                tp_qty = pos.qty - pos.executed_qty
                            place_market(s, "SELL", tp_qty)
                            tp["executed"] = True
                            pos.executed_qty += tp_qty
                            await bot.send_message(chat_id=CHAT_ID,
                                                   text=f"Sell\nToken: {s}\nPrice: {cp:.4f}\nQty: {tp_qty:.6f}\nRemaining: {pos.qty - pos.executed_qty:.6f}")

                    # SL
                    if cp <= pos.sl_price:
                        place_market(s, "SELL", pos.qty - pos.executed_qty)
                        await bot.send_message(chat_id=CHAT_ID,
                                               text=f"Sell\nToken: {s}\nPrice: {cp:.4f}\nQty: {pos.qty - pos.executed_qty:.6f}\nRemaining: 0.000000 (SL Triggered)")
                        remove_position(s)

                    # Remove fully closed positions
                    if pos.executed_qty >= pos.qty:
                        remove_position(s)

            # ---------------- 5-MIN REPORT ----------------
            if time.time() - last_report > 300:  # 5 minutes
                await send_report(bot)
                last_report = time.time()

            await asyncio.sleep(1)

        except Exception as e:
            await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ ERROR: {e}")
            await asyncio.sleep(5)


# ---------------- START BOT ----------------
async def main():
    await trade_loop()


if __name__ == "__main__":
    asyncio.run(main())