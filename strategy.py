import pandas as pd
import ta

def add_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    df['ema_fast'] = ta.trend.EMAIndicator(df['close'],9).ema_indicator()
    df['ema_slow'] = ta.trend.EMAIndicator(df['close'],21).ema_indicator()
    df['ema_long'] = ta.trend.EMAIndicator(df['close'],50).ema_indicator()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], 14).average_true_range()
    df['avg_volume'] = df['volume'].rolling(20).mean()
    return df

def decide_buy(df):
    last = df.iloc[-1]
    trend_ok = last['ema_fast'] > last['ema_slow'] > last['ema_long']
    rsi_ok = last['rsi'] > 45
    vol_ok = last['volume'] > last['avg_volume'] * 1.3
    atr_ok = last['atr'] > 0
    return trend_ok and rsi_ok and vol_ok and atr_ok

def compute_tp(entry, atr, qty):
    return [
        {'price': entry + atr, 'qty': qty*0.3, 'executed': False},
        {'price': entry + atr*1.5, 'qty': qty*0.4, 'executed': False},
        {'price': entry + atr*2, 'qty': qty*0.3, 'executed': False},
    ]