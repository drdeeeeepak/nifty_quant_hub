import streamlit as st
import pandas as pd
from kiteconnect import KiteConnect

st.set_page_config(page_title="Nifty Quant Hub", layout="wide", page_icon="📈")
st.title("📈 Nifty Quant Hub - Central Command")

# ==========================================
# 1. KITE API CREDENTIALS (from Streamlit Secrets)
# ==========================================
# Make sure these are set in your Streamlit Cloud dashboard or local secrets.toml
try:
    API_KEY = st.secrets["KITE_API_KEY"]
    API_SECRET = st.secrets["KITE_API_SECRET"]
except Exception:
    st.error("API Credentials not found. Please configure st.secrets.")
    st.stop()

# Initialize KiteConnect
kite = KiteConnect(api_key=API_KEY)

# ==========================================
# 2. THE LOGIN & AUTHORIZATION FLOW
# ==========================================
if 'access_token' not in st.session_state:
    # Check if we just redirected back from Kite with a request token in the URL
    query_params = st.query_params
    
    if 'request_token' in query_params:
        request_token = query_params['request_token']
        try:
            # Generate the all-day access token
            data = kite.generate_session(request_token, api_secret=API_SECRET)
            st.session_state['access_token'] = data["access_token"]
            
            # Clean up the URL so it doesn't look messy or trigger a re-login on refresh
            st.query_params.clear()
            st.rerun() # Refresh the page to show the authenticated view
            
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            st.button("Try Again")
            st.stop()
    else:
        # We are not logged in and have no token. Show the Login Button.
        login_url = kite.login_url()
        st.warning("⚠️ You are not connected to Zerodha.")
        st.markdown(f'<a href="{login_url}" target="_self"><button style="background-color:#FF5722; color:white; padding:10px 24px; border:none; border-radius:4px; cursor:pointer;">Login to Kite API</button></a>', unsafe_allow_html=True)
        st.stop()

# ==========================================
# 3. AUTHENTICATED STATE
# ==========================================
# If the script reaches here, we are successfully logged in for the day.
kite.set_access_token(st.session_state['access_token'])
st.session_state['kite'] = kite # Save the active session for the other pages

st.success("🟢 Connected to Zerodha Kite API.")

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
            
            # B. Fetch Options Chain
            # --- PLACEHOLDER FOR YOUR CHAIN FETCH LOGIC ---
            # You will query the specific Nifty strikes here.
            # Mock Data to keep the UI from crashing while you build the exact fetcher:
            mock_data = {
                'strike': [21900, 22000, 22100, 22200, 21900, 22000, 22100, 22200],
                'instrument_type': ['CE', 'CE', 'CE', 'CE', 'PE', 'PE', 'PE', 'PE'],
                'volume': [150000, 850000, 300000, 100000, 200000, 450000, 950000, 120000],
                'oi': [2500000, 6500000, 3200000, 1500000, 3100000, 5200000, 7800000, 1800000]
            }
            options_df = pd.DataFrame(mock_data)
            st.session_state['options_df'] = options_df
            
            # C. Fetch OHLC Data for Market Profile (Dummy data to prevent crashes)
            # You will use active_kite.historical_data() here
            dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq='5min')
            dummy_ohlc = pd.DataFrame({'close': [22000]*100, 'low': [21950]*100, 'high': [22050]*100}, index=dates)
            st.session_state['df_daily'] = dummy_ohlc
            st.session_state['df_weekly'] = dummy_ohlc
            
            st.success("✅ Live Data Engine Primed! You can now navigate to the Analysis Pages.")
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")

st.divider()
st.subheader("Data Engine Control")
st.markdown("Click below to pull the latest Nifty data before switching to the analysis tabs.")

if st.button("Fetch / Refresh Live Data", type="primary"):
    fetch_live_market_data(kite)
