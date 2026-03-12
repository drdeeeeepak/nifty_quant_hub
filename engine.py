import pandas as pd
import pandas_ta_classic as ta

class TechnicalEngine:
    def __init__(self, kite_instance):
        self.kite = kite_instance

    def get_data(self, token, interval="day", days=60):
        to_date = pd.Timestamp.now()
        from_date = to_date - pd.Timedelta(days=days)
        try:
            data = self.kite.historical_data(token, from_date, to_date, interval)
            return pd.DataFrame(data)
        except:
            return pd.DataFrame()

    def calculate_ths(self, df):
        if df.empty or len(df) < 35:
            return {"final": 0, "pred": "No Data", "rsi": 0}
        
        df['ema3'] = ta.ema(df['close'], length=3)
        df['ema8'] = ta.ema(df['close'], length=8)
        df['ema16'] = ta.ema(df['close'], length=16)
        df['ema30'] = ta.ema(df['close'], length=30)
        df['rsi'] = ta.rsi(df['close'], length=14)
        bb = ta.bbands(df['close'], length=20, std=2)
        
        last = df.iloc[-1]
        p1 = int(sum([10 for e in ['ema3', 'ema8', 'ema16', 'ema30'] if last['close'] > last[e]]))
        p2 = int((10 if last['ema3'] > last['ema8'] else 0) + (10 if last['ema8'] > last['ema16'] else 0) + (5 if last['ema16'] > last['ema30'] else 0))
        p3 = int(20 if last['rsi'] > 60 else (10 if last['rsi'] > 45 else 0))
        
        final = p1 + p2 + p3
        return {
            "TOTAL THS": final,
            "Price": round(last['close'], 2),
            "RSI": int(round(last['rsi'])),
            "AI Prediction": "Bullish" if final > 55 else "Neutral"
        }
