import streamlit as st
import pandas as pd
from engine import TechnicalEngine

st.title("⚡ Power Grid")

if 'access_token' not in st.session_state:
    st.stop()

engine = TechnicalEngine(st.session_state.kite)
tokens = {"NIFTY 50": 256265, "RELIANCE": 738561}

if st.button("Scan Market"):
    results = []
    for name, tk in tokens.items():
        df = engine.get_data(tk)
        res = engine.calculate_ths(df)
        res['Entity'] = name
        results.append(res)
    st.table(pd.DataFrame(results))
