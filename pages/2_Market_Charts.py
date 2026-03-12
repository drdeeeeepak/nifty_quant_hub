import streamlit as st
import pandas as pd
import datetime
import engine  # Your exact engine.py
import pandas_ta_classic as ta
import plotly.graph_objects as go

st.set_page_config(page_title="Historical Verification", layout="wide")

if 'access_token' not in st.session_state:
    st.warning("⚠️ Please log in on the Home page.")
    st.stop()

st.title("📉 Historical Verification & Pure Data")

# Selection Logic
token_map = {"NIFTY 50 SPOT": 256265}
token_map.update(engine.CONSTITUENTS)
symbol = st.selectbox("Select Instrument to Verify", list(token_map.keys()))
days = st.slider("Lookback Period", 10, 200, 60)

# Data Processing
token = token_map[symbol]
to_date = datetime.datetime.now()
from_date = to_date - datetime.timedelta(days=days)

try:
    with st.spinner("Fetching data..."):
        data = st.session_state.kite.historical_data(token, from_date, to_date, "day")
        df = pd.DataFrame(data)
        
        # Calculate Indicators (matching your engine logic)
        df['ema3'] = ta.ema(df['close'], length=3)
        df['ema8'] = ta.ema(df['close'], length=8)
        df['ema16'] = ta.ema(df['close'], length=16)
        df['ema30'] = ta.ema(df['close'], length=30)
        df['ema200'] = ta.ema(df['close'], length=200)
        df['rsi'] = ta.rsi(df['close'], length=14)
        
        bb = ta.bbands(df['close'], length=20, std=2)
        df['BB_Upper'] = bb.iloc[:, 2]
        df['BB_Mid'] = bb.iloc[:, 1]
        df['BB_Lower'] = bb.iloc[:, 0]
        
        # Scoring from your original engine
        s = engine.calculate_ths(df)

    # --- 1. PLOTLY GRAPH (Dotted Price & One-Color BB) ---
    st.subheader(f"📈 {symbol}: Price, EMA3 & Bollinger Bands")
    
    fig = go.Figure()

    # Bollinger Bands (Same color: Gray, with transparency)
    fig.add_trace(go.Scatter(x=df['date'], y=df['BB_Upper'], name='BB Upper', line=dict(color='rgba(173, 181, 189, 0.4)')))
    fig.add_trace(go.Scatter(x=df['date'], y=df['BB_Lower'], name='BB Lower', line=dict(color='rgba(173, 181, 189, 0.4)'), fill='tonexty'))
    
    # EMA 3 (Solid Line)
    fig.add_trace(go.Scatter(x=df['date'], y=df['ema3'], name='EMA 3', line=dict(color='#ffaa00', width=2)))
    
    # Price (Dotted Line)
    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], name='LTP (Dotted)', line=dict(color='white', width=2, dash='dot')))

    fig.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # --- 2. CONDITIONALLY COLORED TABLE ---
    st.subheader("📋 Pure Data Verification")

    # Filter columns as requested
    table_df = df[['date', 'close', 'ema3', 'ema8', 'ema16', 'ema30', 'ema200', 'BB_Upper', 'BB_Mid', 'BB_Lower']].copy()
    table_df = table_df.rename(columns={'close': 'ltp'})
    table_df['date'] = table_df['date'].dt.date
    
    # Sort descending
    table_df = table_df.sort_values(by='date', ascending=False)

    # Conditional Styling Function
    def color_ema(row):
        styles = [''] * len(row)
        ema_cols = ['ema3', 'ema8', 'ema16', 'ema30', 'ema200']
        
        for col_name in ema_cols:
            col_idx = row.index.get_loc(col_name)
            if row['ltp'] > row[col_name]:
                styles[col_idx] = 'background-color: rgba(0, 255, 0, 0.3); color: #00ff00;'
            else:
                styles[col_idx] = 'background-color: rgba(255, 0, 0, 0.3); color: #ff4b4b;'
        return styles

    # Apply styling
    styled_df = table_df.style.apply(color_ema, axis=1).format(precision=2)

    st.dataframe(styled_df, use_container_width=True, height=400)

except Exception as e:
    st.error(f"Error generating view: {e}")
