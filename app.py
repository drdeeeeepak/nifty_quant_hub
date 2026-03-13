import os
import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect

st.set_page_config(page_title="Nifty Quant Hub", layout="wide", page_icon="📈")
st.title("📈 Nifty Quant Hub - Central Command")

# ==========================================
# 1. KITE API CREDENTIALS
# ==========================================
try:
    API_KEY = st.secrets["KITE_API_KEY"]
    API_SECRET = st.secrets["KITE_API_SECRET"]
except Exception:
    st.error("API Credentials not found in st.secrets.")
    st.stop()

kite = KiteConnect(api_key=API_KEY)
TOKEN_FILE = "token.txt"

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def save_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)

# ==========================================
# 2. SILENT AUTHENTICATION LOGIC
# ==========================================

# Step A: Try to load a saved token first
if 'access_token' not in st.session_state:
    saved = load_token()
    if saved:
        try:
            kite.set_access_token(saved)
            kite.profile() # Test if token is still valid
            st.session_state['access_token'] = saved
            st.session_state['kite'] = kite
        except Exception:
            # Token expired. Delete the file.
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)

# Step B: Check if Zerodha just sent us back with a request_token in the URL
if 'access_token' not in st.session_state and 'request_token' in st.query_params:
    req_token = st.query_params['request_token']
    try:
        # Exchange for the real token
        data = kite.generate_session(req_token, api_secret=API_SECRET)
        acc_token = data["access_token"]
        
        # Save to memory and file
        st.session_state['access_token'] = acc_token
        save_token(acc_token)
        
        # Set the kite object
        kite.set_access_token(acc_token)
        st.session_state['kite'] = kite
        
        # SILENTLY clear the URL so it doesn't trigger again, NO hard redirects!
        st.query_params.clear()
        
    except Exception as e:
        st.error(f"Failed to generate session: {e}")
        st.query_params.clear()

# ==========================================
# 3. DASHBOARD ROUTER (The UI)
# ==========================================

# If we have the token, show the Dashboard!
if 'access_token' in st.session_state:
    
    # Failsafe: Ensure kite is in session state
    if 'kite' not in st.session_state:
        kite.set_access_token(st.session_state['access_token'])
        st.session_state['kite'] = kite
        
    st.success("🟢 Connected to Zerodha Kite API. (Session active for the day)")
    
    # --- Data Fetcher ---
    def fetch_live_market_data(active_kite):
        with st.spinner("Downloading Market Data & Options Chain..."):
            try:
                spot_quote = active_kite.quote("NSE:NIFTY 50")
                spot_price = spot_quote["NSE:NIFTY 50"]["last_price"]
                st.session_state['spot_price'] = spot_price
                
                # Mock Options Data
                mock_data = {
                    'strike': [21900, 22000, 22100, 22200, 21900, 22000, 22100, 22200],
                    'instrument_type': ['CE', 'CE', 'CE', 'CE', 'PE', 'PE', 'PE', 'PE'],
                    'volume': [150000, 850000, 300000, 100000, 200000, 450000, 950000, 120000],
                    'oi': [2500000, 6500000, 3200000, 1500000, 3100000, 5200000, 7800000, 1800000]
                }
                st.session_state['options_df'] = pd.DataFrame(mock_data)
                
                # Mock OHLC Data
                dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='5min')
                dummy_ohlc = pd.DataFrame({'close': [spot_price]*100, 'low': [spot_price-50]*100, 'high': [spot_price+50]*100}, index=dates)
                st.session_state['df_daily'] = dummy_ohlc
                st.session_state['df_weekly'] = dummy_ohlc
                
                st.success("✅ Live Data Engine Primed! Use the sidebar to view Analysis Pages.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")

    st.divider()
    st.subheader("Data Engine Control")
    if st.button("Fetch / Refresh Live Data", type="primary"):
        fetch_live_market_data(st.session_state['kite'])

# If we DO NOT have the token, show the Login Button
else:
    login_url = kite.login_url()
    st.warning("⚠️ You are not connected to Zerodha. No valid token found.")
    st.markdown(f'<a href="{login_url}" target="_self"><button style="background-color:#FF5722; color:white; padding:10px 24px; border:none; border-radius:4px; cursor:pointer;">Login to Kite API</button></a>', unsafe_allow_html=True)
