import streamlit as st
import pandas as pd
import datetime, os
from kiteconnect import KiteConnect
import engine

# --- CLOUD SECRETS COMPATIBILITY ---
if "KITE_API_KEY" in st.secrets:
    API_KEY = st.secrets["KITE_API_KEY"]
    API_SECRET = st.secrets["KITE_API_SECRET"]
else:
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("KITE_API_KEY")
    API_SECRET = os.getenv("KITE_API_SECRET")

st.set_page_config(page_title="Nifty Power Grid Pro", layout="wide")
TOKEN_FILE = "token.txt"

if 'kite' not in st.session_state:
    st.session_state.kite = KiteConnect(api_key=API_KEY)

def clear_token_file():
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "w") as f: f.write("")
    except: pass

def load_stored_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f: token = f.read().strip()
        if not token: return None
        try:
            st.session_state.kite.set_access_token(token)
            st.session_state.kite.profile()
            return token
        except:
            clear_token_file()
            return None
    return None

# --- AUTHENTICATION LOGIC ---
params = st.query_params
if "request_token" in params:
    try:
        user_session = st.session_state.kite.generate_session(params["request_token"], api_secret=API_SECRET)
        st.session_state.access_token = user_session["access_token"]
        st.session_state.kite.set_access_token(user_session["access_token"])
        with open(TOKEN_FILE, "w") as f: f.write(user_session["access_token"])
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")
        clear_token_file()

if 'access_token' not in st.session_state:
    stored = load_stored_token()
    if stored: 
        st.session_state.access_token = stored
        st.rerun()
    else:
        st.title("🔐 Login to Nifty Power Grid")
        st.link_button("Authorize Kite", st.session_state.kite.login_url(), type="primary")
else:
    st.sidebar.success(f"User: {st.session_state.kite.profile()['user_name']}")
    st.title("🚀 Nifty Quant Hub: Active")
    st.write("---")
    st.subheader("👈 Select an Analysis Module from the sidebar")
    st.info("Your Zerodha session is active and shared across all app pages.")
    
    if st.sidebar.button("Logout"):
        clear_token_file()
        st.session_state.clear()
        st.rerun()
