import streamlit as st
import pandas as pd
import datetime
import engine

st.set_page_config(page_title="Power Grid Scan", layout="wide")

if 'access_token' not in st.session_state:
    st.switch_page("app.py")
st.title("⚡ Nifty 50 Power Grid: Execution Engine")

auto_refresh = st.sidebar.toggle("Auto-Refresh (5 Mins)", value=True)
manual_run = st.button("🚀 Run Full Market Scan")

@st.fragment(run_every=300 if auto_refresh else None)
def run_market_scan():
    results = []
    total_weighted_score = 0
    st.caption(f"Last scan: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    with st.spinner('Scanning Market Health...'):
        try:
            all_ins = pd.DataFrame(st.session_state.kite.instruments("NFO"))
            nifty_fut = int(all_ins[(all_ins['name'] == 'NIFTY') & (all_ins['instrument_type'] == 'FUT') & (all_ins['expiry'].astype(str).str.contains('2026-03'))].iloc[0]['instrument_token'])
        except: 
            nifty_fut = 12803330

        token_map = {"NIFTY 50 SPOT": 256265, "NIFTY MAR FUT": nifty_fut}
        token_map.update(engine.CONSTITUENTS)
        
        to_date = datetime.datetime.now()
        from_date = to_date - datetime.timedelta(days=60)
        
        for symbol, token in token_map.items():
            try:
                data = st.session_state.kite.historical_data(token, from_date, to_date, "day")
                df = pd.DataFrame(data)
                s = engine.calculate_ths(df)
                
                weights = {"RELIANCE": 9.78, "HDFCBANK": 6.70, "ICICIBANK": 4.82, "BHARTIARTL": 4.51, "INFY": 4.12, "TCS": 3.75, "ITC": 3.62, "SBIN": 3.45, "AXISBANK": 3.10, "LT": 3.05}
                weight = weights.get(symbol, 0)
                if symbol in weights:
                    total_weighted_score += (s['final'] * weight)
                
                results.append({
                    "Entity": symbol,
                    "Price/EMA (40)": int(s['p1']), "EMA Grid (25)": int(s['p2']),
                    "RSI Score (20)": int(s['p3']), "BB Zone (15)": int(s['p4']),
                    "TOTAL THS": int(s['final']), "RSI": int(s['rsi']),
                    "Squeeze": "🎯" if s['squeeze'] else "---",
                    "Price": int(round(df['close'].iloc[-1])), "AI Prediction": s['pred']
                })
            except:
                results.append({"Entity": symbol, "TOTAL THS": 0, "AI Prediction": "Error"})

    total_weight = 47.13
    wns = int(round(total_weighted_score / total_weight))
    spot_ths = next((x['TOTAL THS'] for x in results if x['Entity'] == "NIFTY 50 SPOT"), 0)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("WNS Engine", f"{wns}/100")
    c2.metric("Nifty Spot", f"{spot_ths}/100")
    c3.metric("Gap", f"{int(spot_ths - wns)}")
    st.table(pd.DataFrame(results))

if manual_run or True: run_market_scan()
