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

st.title("📉 Historical Verification & Multi-Stock Hub")

# --- SELECTION ---
token_map = {"NIFTY 50 SPOT": 256265}
token_map.update(engine.CONSTITUENTS)

options = ["All"] + list(token_map.keys())
selection = st.selectbox("Select Instrument to Verify", options)

# Common Date Range for all calculations
to_date = datetime.datetime.now()
from_date = to_date - datetime.timedelta(days=350) 

def get_processed_data(symbol, token):
    data = st.session_state.kite.historical_data(token, from_date, to_date, "day")
    df = pd.DataFrame(data)
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
    return df

# --- CONDITIONAL COLORING FUNCTION ---
def color_levels(row):
    styles = [''] * len(row)
    target_cols = ['ema3', 'ema8', 'ema16', 'ema30', 'ema200', 'BB_Upper', 'BB_Mid', 'BB_Lower']
    ltp = row['ltp']
    
    for col_name in target_cols:
        if col_name in row.index:
            col_idx = row.index.get_loc(col_name)
            val = row[col_name]
            if pd.isna(val):
                styles[col_idx] = 'background-color: #333; color: #888;'
            elif ltp > val:
                styles[col_idx] = 'background-color: rgba(0, 255, 0, 0.2); color: #00ff00;'
            else:
                styles[col_idx] = 'background-color: rgba(255, 0, 0, 0.2); color: #ff4b4b;'
    return styles

# --- LOGIC FOR "ALL" VIEW ---
if selection == "All":
    if st.button("Fetch All Stocks Summary"):
        all_results = []
        with st.spinner("Compiling All Market Parameters..."):
            for name, token in token_map.items():
                try:
                    df = get_processed_data(name, token)
                    last = df.iloc[-1]
                    all_results.append({
                        "Entity": name, "ltp": round(last['close'], 2),
                        "rsi": int(round(last['rsi'])), "ema3": last['ema3'],
                        "ema8": last['ema8'], "ema16": last['ema16'],
                        "ema30": last['ema30'], "ema200": last['ema200'],
                        "BB_Upper": last['BB_Upper'], "BB_Mid": last['BB_Mid'], "BB_Lower": last['BB_Lower']
                    })
                except: continue
        
        summary_df = pd.DataFrame(all_results)
        styled_summary = summary_df.style.apply(color_levels, axis=1).format(precision=2)
        st.subheader("Today's Snapshot: All Instruments")
        st.dataframe(styled_summary, use_container_width=True, height=600)

# --- LOGIC FOR SINGLE INSTRUMENT VIEW ---
else:
    try:
        chart_days = st.slider("Chart Lookback (Days)", 5, 60, 14)
        df = get_processed_data(selection, token_map[selection])
        
        # 1. GRAPH
        st.subheader(f"📈 {selection}: Price & Indicators")
        chart_df = df.tail(chart_days)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['BB_Upper'], name='BB Upper', line=dict(color='rgba(173, 181, 189, 0.3)', width=1)))
        fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['BB_Lower'], name='BB Lower', line=dict(color='rgba(173, 181, 189, 0.3)', width=1), fill='tonexty'))
        fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['BB_Mid'], name='BB Mid', line=dict(color='rgba(173, 181, 189, 0.5)', width=1)))
        fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['ema3'], name='EMA3 (Dotted)', line=dict(color='yellow', width=2, dash='dot')))
        fig.add_trace(go.Scatter(x=chart_df['date'], y=chart_df['close'], name='LTP (Solid Blue)', line=dict(color='#1E90FF', width=3)))
        fig.update_layout(template="plotly_dark", height=450, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        # 2. TABLE
        st.divider()
        table_days = st.slider("Table Lookback (Days)", 10, 250, 60)
        st.subheader("📋 Pure Data Verification")
        
        table_df = df.tail(table_days)[['date', 'close', 'rsi', 'ema3', 'ema8', 'ema16', 'ema30', 'ema200', 'BB_Upper', 'BB_Mid', 'BB_Lower']].copy()
        table_df = table_df.rename(columns={'close': 'ltp'})
        table_df['date'] = table_df['date'].dt.date
        table_df = table_df.sort_values(by='date', ascending=False)

        styled_df = table_df.style.apply(color_levels, axis=1).format(precision=2)
        st.dataframe(styled_df, use_container_width=True, height=500)

    except Exception as e:
        st.error(f"Error: {e}")
