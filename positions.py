positions = {}  

class Position:
    def __init__(self, symbol, entry, qty, tp_orders, sl_price):
        self.symbol = symbol
        self.entry = entry
        self.qty = qty
        self.tp_orders = tp_orders
        self.sl_price = sl_price
        self.trail_price = entry
        self.executed_qty = 0
        self.active = True

def add_position(symbol, entry, qty, tp_orders, sl_price):
    positions[symbol] = Position(symbol, entry, qty, tp_orders, sl_price)

def remove_position(symbol):
    if symbol in positions:
        del positions[symbol]