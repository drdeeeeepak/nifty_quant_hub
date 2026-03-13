import pandas as pd
import numpy as np
import pandas_ta_classic as ta

# MARCH 2026 WEIGHTS (Kite Instrument Tokens)
CONSTITUENTS = {
    "RELIANCE": 738561, "HDFCBANK": 341249, "ICICIBANK": 1270529, 
    "BHARTIARTL": 2714625, "INFY": 408065, "TCS": 2953217, 
    "ITC": 424961, "SBIN": 779521, "AXISBANK": 1510401, "LT": 2939649
}

def calculate_ths(df):
    """Calculates all Pillars with clean Integer Scores."""
    if df is None or df.empty or len(df) < 35:
        return {"final": 0, "p1": 0, "p2": 0, "p3": 0, "p4": 0, "squeeze": False, "rsi": 0, "pred": "No Data"}
    
    # 1. Indicators
    df['ema3'] = ta.ema(df['close'], length=3)
    df['ema8'] = ta.ema(df['close'], length=8)
    df['ema16'] = ta.ema(df['close'], length=16)
    df['ema30'] = ta.ema(df['close'], length=30)
    df['rsi'] = ta.rsi(df['close'], length=14)
    bb = ta.bbands(df['close'], length=20, std=2)
    
    last = df.iloc[-1]
    bb_mid, bb_upper = bb.iloc[-1, 1], bb.iloc[-1, 2]
    
    # 2. Pillar Integer Scoring
    p1 = int(sum([10 for e in ['ema3', 'ema8', 'ema16', 'ema30'] if last['close'] > last[e]]))
    p2 = int((10 if last['ema3'] > last['ema8'] else 0) + (10 if last['ema8'] > last['ema16'] else 0) + (5 if last['ema16'] > last['ema30'] else 0))
    p3 = int(20 if last['rsi'] > 60 else (10 if last['rsi'] > 45 else 0))
    p4 = int(15 if bb_mid < last['close'] < bb_upper else (5 if last['close'] > bb_upper else 0))
    
    final = p1 + p2 + p3 + p4
    df['bw'] = (bb.iloc[:, 2] - bb.iloc[:, 0]) / bb.iloc[:, 1]
    squeeze = df['bw'].iloc[-1] < df['bw'].rolling(20).mean().iloc[-1]

    # 3. Predictions
    if last['rsi'] < 30: pred = "Oversold: Bounce Possible"
    elif final < 25: pred = "Bearish: Sell on Rise"
    elif final > 75 and squeeze: pred = "Squeeze: Bullish Blast"
    elif final > 55: pred = "Bullish: Hold"
    else: pred = "Neutral: Sideways"

    return {"final": final, "p1": p1, "p2": p2, "p3": p3, "p4": p4, "squeeze": squeeze, "rsi": int(round(last['rsi'])), "pred": pred}

# ==========================================
# MARKET PROFILE & MACRO REGIME LOGIC
# ==========================================

def get_market_profile(df, tick=5):
    """Fast Market Profile algorithm using 1-min data histograms."""
    if df is None or df.empty:
        return None, None, None
        
    low = df['low'].min()
    high = df['high'].max()
    
    bins = np.arange(low, high + tick, tick)
    counts = np.zeros(len(bins))
    
    for _, row in df.iterrows():
        candle_bins = np.arange(row['low'], row['high'] + tick, tick)
        idx = np.searchsorted(bins, candle_bins)
        # Prevent out-of-bounds indexing
        idx = idx[idx < len(counts)] 
        counts[idx] += 1
        
    poc_index = np.argmax(counts)
    poc = bins[poc_index]
    
    total = counts.sum()
    target = total * 0.70
    
    sorted_idx = np.argsort(counts)[::-1]
    cumulative = 0
    value_bins = []
    
    for i in sorted_idx:
        cumulative += counts[i]
        value_bins.append(bins[i])
        if cumulative >= target:
            break
            
    vah = max(value_bins)
    val = min(value_bins)
    
    return poc, vah, val

def get_macro_regime(df_daily, df_weekly):
    """
    Evaluates the overarching market structure by combining RSI and Market Profile.
    """
    if df_daily is None or df_daily.empty or df_weekly is None or df_weekly.empty:
        return "Waiting for Data..."
        
    # Get current price and RSI from the daily dataframe
    df_daily['rsi'] = ta.rsi(df_daily['close'], length=14)
    spot_price = df_daily['close'].iloc[-1]
    rsi_daily = df_daily['rsi'].iloc[-1]
    
    # Get the Weekly Profile levels (Wednesday-Tuesday cycle)
    weekly_poc, weekly_vah, weekly_val = get_market_profile(df_weekly)
    
    if weekly_vah is None:
        return "Insufficient Profile Data"

    # Evaluate the Regime Rules
    if spot_price > weekly_vah and rsi_daily > 60:
        return "Bullish Expansion"
    
    elif spot_price < weekly_val and rsi_daily < 40:
        return "Bearish Expansion"
        
    elif weekly_val <= spot_price <= weekly_vah and 46 <= rsi_daily <= 54:
        return "Balanced Rotation"
        
    elif weekly_val <= spot_price <= weekly_vah and rsi_daily > 54:
        return "Controlled Bullish Drift"
        
    elif weekly_val <= spot_price <= weekly_vah and rsi_daily < 46:
        return "Controlled Bearish Drift"
        
    else:
        return "Mixed / Transitioning"
