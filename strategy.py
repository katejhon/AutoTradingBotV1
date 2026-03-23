import pandas as pd

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def indicators(df):
    df['ema'] = df['c'].ewm(span=20).mean()
    df['rsi'] = rsi(df['c'])
    df['atr'] = (df['h'] - df['l']).rolling(14).mean()
    return df

def ai_signal_multi(df1, df5, df15):
    def score(df):
        rsi_v = df['rsi'].iloc[-1]
        ema = df['ema'].iloc[-1]
        price = df['c'].iloc[-1]
        vol = df['v'].iloc[-1]
        avg_vol = df['v'].rolling(20).mean().iloc[-1]

        s = 0
        if rsi_v > 50: s += 1
        if price > ema: s += 1
        if vol > avg_vol: s += 1
        return s

    s1 = score(df1)
    s5 = score(df5)
    s15 = score(df15)
    total = s1 + (s5 * 1.5) + (s15 * 2)
    return total >= 5