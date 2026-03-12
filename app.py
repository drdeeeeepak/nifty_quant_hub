import streamlit as st
import pandas as pd
import datetime, os
from kiteconnect import KiteConnect
import engine

st.set_page_config(page_title="Nifty Quant Hub", layout="wide")
TOKEN_FILE = "token.txt"

# --- CLOUD SECRETS COMPATIBILITY ---
if "KITE_API_KEY" in st.secrets:
    API_KEY = st.secrets["KITE_API_KEY"]
    API_SECRET = st.secrets["KITE_API_SECRET"]
else:
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("KITE_API_KEY")
    API_SECRET = os.getenv("KITE_API_SECRET")

if 'kite' not in st.session_state:
    st.session_state.kite = KiteConnect(api_key=API_KEY)

# --- MASTER TOKEN LOGIC ---
def clear_token_file():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

def load_stored_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f: 
            token = f.read().strip()
        if token:
            try:
                # Test the token to ensure it hasn't expired (6 AM reset)
                st.session_state.kite.set_access_token(token)
                st.session_state.kite.profile() 
                st.session_state.access_token = token
                return True
            except:
                clear_token_file()
                return False
    return False

# --- OAUTH LOGIN REDIRECT HANDLING ---
params = st.query_params
if "request_token" in params:
    try:
        user_session = st.session_state.kite.generate_session(params["request_token"], api_secret=API_SECRET)
        token = user_session["access_token"]
        st.session_state.access_token = token
        st.session_state.kite.set_access_token(token)
        # Save for the whole day
        with open(TOKEN_FILE, "w") as f: 
            f.write(token)
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")
        clear_token_file()

# --- MAIN ROUTING ---
if 'access_token' not in st.session_state:
    if load_stored_token():
        st.rerun()
    else:
        st.title("🔐 Login to Nifty Quant Hub")
        st.link_button("Authorize Kite", st.session_state.kite.login_url(), type="primary")
else:
    st.sidebar.success(f"User: {st.session_state.kite.profile()['user_name']}")
    st.title("🚀 Nifty Quant Hub: Active")
    st.write("---")
    st.subheader("👈 Select an Analysis Module from the sidebar")
    st.info("Your Zerodha session is active. You only need to log in once per day.")
    
    if st.sidebar.button("Logout"):
        clear_token_file()
        st.session_state.clear()
        st.rerun()
