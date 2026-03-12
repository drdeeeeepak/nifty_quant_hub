import streamlit as st
import pandas as pd
import datetime
import engine  
import pandas_ta_classic as ta
import plotly.graph_objects as go

st.set_page_config(page_title="Historical Verification", layout="wide")

if 'access_token' not in st.session_state:
    st.warning("⚠️ Please log in on the Home page.")
    st.stop()

st.title("📉 Historical Verification & Pure Data")

# --- SELECTION & DUAL LOOKBACK CONTROLS ---
token_map = {"NIFTY 50 SPOT": 256265}
token_map.update(engine.CONSTITUENTS)

symbol = st.selectbox("Select Instrument to Verify", list(token_map.keys()))

col_left, col_right = st.columns(2)
with col_left:
    chart_days = st.slider("Chart Lookback (Days)", 5, 60, 14)
with col_right:
    table_days = st.slider("Table Lookback (Days)", 10, 250, 60)

# Fetch 350 days to ensure EMA200 and BB Middle are fully calculated
token = token_map[symbol]
to_date = datetime.datetime.now()
from_date = to_date - datetime.timedelta(days=350) 

try:
    with st.spinner("Fetching data..."):
        data = st.session_state.kite.historical_data(token, from_date, to_date, "day")
        df = pd.DataFrame(data)
        
        # Indicators
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

    # --- 1. GRAPH (Customized Styles) ---
    st.subheader(f"📈 {symbol}: Price & Indicator Plot")
    
    # Filter for Chart Lookback
    chart_df = df.tail(chart_days).copy()
    
    fig = go.Figure()

    # Bollinger Bands (Single color Gray)
    fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['BB_Upper'], name='BB Upper', line=dict(color='rgba(173, 181, 189, 0.3)', width=1)))
    fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['BB_Lower'], name='BB Lower', line=dict(color='rgba(173, 181, 189, 0.3)', width=1), fill='tonexty'))
    
    # BB Middle Line (Added as requested)
    fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['BB_Mid'], name='BB Middle', line=dict(color='rgba(173, 181, 189, 0.6)', width=1)))
    
    # EMA 3 (Yellow Dotted)
    fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['ema3'], name='EMA 3 (Dotted)', line=dict(color='#FFD700', width=2, dash='dot')))
    
    # LTP (Blue Solid)
    fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['close'], name='LTP (Solid Blue)', line=dict(color='#1E90FF', width=3)))

    fig.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=20, b=20), hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # --- 2. CONDITIONALLY COLORED TABLE (Table Lookback) ---
    st.subheader("📋 Pure Data Verification")
    
    # Filter for Table Lookback
    table_raw_df = df.tail(table_days).copy()

    table_df = table_raw_df[['date', 'close', 'ema3', 'ema8', 'ema16', 'ema30', 'ema200', 'BB_Upper', 'BB_Mid', 'BB_Lower']].copy()
    table_df = table_df.rename(columns={'close': 'ltp'})
    table_df['date'] = table_df['date'].dt.date
    table_df = table_df.sort_values(by='date', ascending=False)

    def color_ema(row):
        styles = [''] * len(row)
        ema_cols = ['ema3', 'ema8', 'ema16', 'ema30', 'ema200']
        for col_name in ema_cols:
            col_idx = row.index.get_loc(col_name)
            val = row[col_name]
            if pd.isna(val):
                styles[col_idx] = 'background-color: #333; color: #888;'
            elif row['ltp'] > val:
                styles[col_idx] = 'background-color: rgba(0, 255, 0, 0.2); color: #00ff00;'
            else:
                styles[col_idx] = 'background-color: rgba(255, 0, 0, 0.2); color: #ff4b4b;'
        return styles

    styled_df = table_df.style.apply(color_ema, axis=1).format(precision=2)
    st.dataframe(styled_df, use_container_width=True, height=500)

except Exception as e:
    st.error(f"Error generating view: {e}")
