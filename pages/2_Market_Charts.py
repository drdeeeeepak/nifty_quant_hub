import streamlit as st
import pandas as pd
import datetime
import engine

st.set_page_config(page_title="Historical Verification", layout="wide")

if 'access_token' not in st.session_state:
    st.stop()

st.title("📉 Historical Verification & Pure Data")

# Selection
token_map = {"NIFTY 50 SPOT": 256265}
token_map.update(engine.CONSTITUENTS)
symbol = st.selectbox("Select Instrument to Verify", list(token_map.keys()))
days = st.slider("Lookback Period", 10, 100, 60)

# Data
token = token_map[symbol]
to_date = datetime.datetime.now()
from_date = to_date - datetime.timedelta(days=days)

try:
    data = st.session_state.kite.historical_data(token, from_date, to_date, "day")
    df = pd.DataFrame(data)
    s = engine.calculate_ths(df) # Run scoring for indicators

    # 1. Prediction Layer
    st.success(f"**Current AI Prediction:** {s['pred']} (Score: {s['final']})")

    # 2. Historical Plotting
    st.subheader("Price vs. EMA Grid Progress")
    chart_df = df[['date', 'close', 'ema8', 'ema16', 'ema30']].set_index('date')
    st.line_chart(chart_df)

    # 3. Pure Data Confirmation
    st.subheader("Pure Data: OHLC & Indicator Levels")
    pure_df = df[['date', 'open', 'high', 'low', 'close', 'ema8', 'ema30', 'rsi']].copy()
    pure_df['date'] = pure_df['date'].dt.date
    st.dataframe(pure_df.sort_values(by='date', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error fetching data: {e}")
