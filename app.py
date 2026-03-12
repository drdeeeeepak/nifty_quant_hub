import streamlit as st
from kiteconnect import KiteConnect

st.set_page_config(page_title="Nifty Quant Hub", layout="wide")

if 'kite' not in st.session_state:
    st.session_state.kite = KiteConnect(api_key=st.secrets["KITE_API_KEY"])

params = st.query_params
if "request_token" in params:
    session = st.session_state.kite.generate_session(params["request_token"], api_secret=st.secrets["KITE_API_SECRET"])
    st.session_state.access_token = session["access_token"]
    st.session_state.kite.set_access_token(session["access_token"])
    st.rerun()

if 'access_token' not in st.session_state:
    st.title("🛡️ Nifty Quant Hub")
    st.link_button("Login to Zerodha", st.session_state.kite.login_url(), type="primary")
else:
    st.title("🚀 Quant Hub Active")
    st.info("Check the sidebar for your analysis modules.")
