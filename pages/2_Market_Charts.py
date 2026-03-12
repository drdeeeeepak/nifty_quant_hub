import streamlit as st
import pandas as pd
import datetime
import engine  # Importing your original engine
import pandas_ta_classic as ta

st.set_page_config(page_title="Historical Verification", layout="wide")

if 'access_token' not in st.session_state:
    st.warning("⚠️ Please log in on the Home page.")
    st.stop()

st.title("📉 Historical Verification & Pure Data")

# Selection
token_map = {"NIFTY 50 SPOT": 256265}
token_map.update(engine.CONSTITUENTS)
symbol = st.selectbox("Select Instrument to Verify", list(token_map.keys()))
days = st.slider("Lookback Period", 10, 100, 60)

# Data Fetching
token = token_map[symbol]
to_date = datetime.datetime.now()
from_date = to_date - datetime.timedelta(days=days)

try:
    with st.spinner("Fetching pure data..."):
        data = st.session_state.kite.historical_data(token, from_date, to_date, "day")
        df = pd.DataFrame(data)
        
        # Run your exact engine scoring logic
        s = engine.calculate_ths(df) 
        
        # Manually extract BB columns for display (Your engine uses length=20, std=2)
        bb = ta.bbands(df['close'], length=20, std=2)
        df['BB_Lower'] = bb.iloc[:, 0]
        df['BB_Mid'] = bb.iloc[:, 1]
        df['BB_Upper'] = bb.iloc[:, 2]

    # 1. Prediction Layer
    st.success(f"**Current AI Prediction:** {s['pred']} (Score: {s['final']})")

    # 2. Historical Plotting (Now with Bollinger Bands)
    st.subheader("Price vs. EMA Grid & Bollinger Bands")
    # We include Close, EMAs from your engine, and the new BB levels
    chart_cols = ['date', 'close', 'ema8', 'ema16', 'ema30', 'BB_Upper', 'BB_Mid', 'BB_Lower']
    chart_df = df[chart_cols].set_index('date')
    st.line_chart(chart_df)

    # 3. Pure Data Confirmation (Now with BB Columns)
    st.subheader("Pure Data: OHLC, RSI, & Bollinger Levels")
    # Adding BB levels to the tabulated data below the chart
    pure_cols = ['date', 'open', 'high', 'low', 'close', 'rsi', 'BB_Upper', 'BB_Mid', 'BB_Lower']
    pure_df = df[pure_cols].copy()
    pure_df['date'] = pure_df['date'].dt.date
    
    st.dataframe(
        pure_df.sort_values(by='date', ascending=False), 
        use_container_width=True
    )

except Exception as e:
    st.error(f"Error fetching data: {e}")
