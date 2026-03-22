from positions import positions
from utils import safe_div
import asyncio
from orders import get_price
from config import REPORT_INTERVAL

async def send_report(bot):
    total = sum([safe_div(get_price(k)*v.qty,1) for k,v in positions.items()])
    msg = f"📊 {REPORT_INTERVAL//60}-MIN REPORT\n\n💰 Balance: {total:.2f} USDT\n\n"
    profit_list=[]
    for symbol,pos in positions.items():
        price = get_price(symbol)
        pnl_token = safe_div((price-pos.entry)*100,pos.entry)
        profit_list.append((symbol,pnl_token,price,pos.qty,pos.entry))
    profit_list.sort(key=lambda x:x[1], reverse=True)
    for s,pnl_token,price,qty,entry in profit_list:
        msg += f"{s}\nToken Price: {price}\nEntry: {entry}\nQty: {qty}\nPNL: {pnl_token:.2f}%\n\n"
    await bot.send_message(chat_id=bot.chat_id, text=msg)

async def report_loop(bot):
    await asyncio.sleep(5)
    while True:
        try:
            await send_report(bot)
        except Exception as e:
            await bot.send_message(chat_id=bot.chat_id, text=f"⚠️ REPORT ERROR: {e}")
        await asyncio.sleep(REPORT_INTERVAL)
