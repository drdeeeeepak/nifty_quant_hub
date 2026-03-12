import streamlit as st
import pandas as pd
from engine import TechnicalEngine

st.set_page_config(page_title="Market Charts", layout="wide")

if 'access_token' not in st.session_state:
    st.warning("Please log in on the Home page.")
    st.stop()

st.title("📉 Historical Trend Analysis")

# Initialize Engine
eng = TechnicalEngine(st.session_state.kite)

# Mapping common names to Kite Tokens
TOKENS = {
    "NIFTY 50": 256265,
    "RELIANCE": 738561,
    "HDFCBANK": 341249,
    "ICICIBANK": 1270529
}

selection = st.selectbox("Select Instrument to Analyze", list(TOKENS.keys()))
days_to_lookback = st.slider("Select Days", 10, 100, 60)

if st.button("Generate Technical Chart"):
    with st.spinner("Fetching Data..."):
        token = TOKENS[selection]
        df = eng.get_historical_data(token, days=days_to_lookback)
        
        if not df.empty:
            # Show Price Chart
            st.subheader(f"{selection} Price Progress")
            st.line_chart(df.set_index('date')['close'])
            
            # Show Data Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Price", f"₹{df['close'].iloc[-1]}")
            col2.metric("High (Period)", f"₹{df['high'].max()}")
            col3.metric("Low (Period)", f"₹{df['low'].min()}")
            
            # Show Raw Data for verification
            with st.expander("View Raw OHLC Data"):
                st.dataframe(df.tail(10))
        else:
            st.error("Could not fetch data. Check your API connection.")
