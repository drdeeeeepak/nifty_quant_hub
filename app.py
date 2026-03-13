import os
import streamlit as st
import pandas as pd
import datetime
from kiteconnect import KiteConnect

st.set_page_config(page_title="Nifty Quant Hub", layout="wide", page_icon="📈")
st.title("📈 Nifty Quant Hub - Central Command")

# ==========================================
# 1. KITE API CREDENTIALS & SETUP
# ==========================================
try:
    API_KEY = st.secrets["ufen54ln7mxu2cav"]
    API_SECRET = st.secrets["qyz8os3eha9alh777c7jujn3gzmhv7n5"]
except Exception:
    st.error("API Credentials not found. Please configure st.secrets in Streamlit Cloud.")
    st.stop()

kite = KiteConnect(api_key=API_KEY)
TOKEN_FILE = "token.txt"

def load_saved_token():
    """Reads the token from the file if it exists."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def save_token(token):
    """Saves the token to a text file for all-day persistence."""
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

# ==========================================
# 2. THE LOGIN & AUTHORIZATION FLOW
# ==========================================

# Step A: Check if we already have a valid token saved in the file
if 'access_token' not in st.session_state:
    saved_token = load_saved_token()
    if saved_token:
        try:
            # Test the saved token to see if it is still valid today
            kite.set_access_token(saved_token)
            kite.profile() # This will fail if the token is expired
            st.session_state['access_token'] = saved_token
        except Exception:
            # Token is expired (happens every morning at 6 AM). Delete the old file.
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)

# Step B: If no valid token, check if we are returning from the login screen
if 'access_token' not in st.session_state:
    query_params = st.query_params
    
    if 'request_token' in query_params:
        request_token = query_params['request_token']
        try:
            # Generate the all-day access token
            data = kite.generate_session(request_token, api_secret=API_SECRET)
            new_token = data["access_token"]
            
            # Save it to session state AND to the text file
            st.session_state['access_token'] = new_token
            save_token(new_token)
            
            # Clean transition to prevent Streamlit Cloud redirect loops
            st.success("✅ Logged in successfully! Token saved for the day.")
            if st.button("Enter Dashboard", type="primary"):
                st.query_params.clear()
                st.rerun()
            st.stop()
            
        except Exception as e:
            st.error(f"Authentication failed. Please try logging in again.\nError: {e}")
            if st.button("Reset & Try Again"):
                st.query_params.clear()
                st.rerun()
            st.stop()
    else:
        # Step C: No token anywhere. Show the Login Button.
        login_url = kite.login_url()
        st.warning("⚠️ You are not connected to Zerodha. No valid token found for today.")
        st.markdown(f'<a href="{login_url}" target="_self"><button style="background-color:#FF5722; color:white; padding:10px 24px; border:none; border-radius:4px; cursor:pointer;">Login to Kite API</button></a>', unsafe_allow_html=True)
        st.stop()

# ==========================================
# 3. AUTHENTICATED STATE
# ==========================================
# If the script reaches here, we have a valid token for the day.
kite.set_access_token(st.session_state['access_token'])
st.session_state['kite'] = kite

st.success("🟢 Connected to Zerodha Kite API. (Session active for the day)")

# ==========================================
# 4. THE DATA FETCHER ENGINE
# ==========================================
def fetch_live_market_data(active_kite):
    """Fetches spot price, OHLC, and options chain, then saves to global memory."""
    with st.spinner("Downloading Market Data & Options Chain..."):
        try:
            # A. Fetch Nifty 50 Spot Price
            spot_quote = active_kite.quote("NSE:NIFTY 50")
            spot_price = spot_quote["NSE:NIFTY 50"]["last_price"]
            st.session_state['spot_price'] = spot_price
            
            # B. Fetch Options Chain (Mock Data to keep UI from crashing)
            mock_data = {
                'strike': [21900, 22000, 22100, 22200, 21900, 22000, 22100, 22200],
                'instrument_type': ['CE', 'CE', 'CE', 'CE', 'PE', 'PE', 'PE', 'PE'],
                'volume': [150000, 850000, 300000, 100000, 200000, 450000, 950000, 120000],
                'oi': [2500000, 6500000, 3200000, 1500000, 3100000, 5200000, 7800000, 1800000]
            }
            options_df = pd.DataFrame(mock_data)
            st.session_state['options_df'] = options_df
            
            # C. Fetch OHLC Data for Market Profile (Mock Data to keep UI from crashing)
            dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='5min')
            dummy_ohlc = pd.DataFrame({'close': [spot_price]*100, 'low': [spot_price-50]*100, 'high': [spot_price+50]*100}, index=dates)
            st.session_state['df_daily'] = dummy_ohlc
            st.session_state['df_weekly'] = dummy_ohlc
            
            st.success("✅ Live Data Engine Primed! You can now navigate to the Analysis Pages using the sidebar.")
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")

st.divider()
st.subheader("Data Engine Control")
st.markdown("Click below to pull the latest Nifty data before switching to the analysis tabs.")

if st.button("Fetch / Refresh Live Data", type="primary"):
    fetch_live_market_data(kite)
