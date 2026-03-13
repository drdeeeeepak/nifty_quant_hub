import streamlit as st
import options_engine as oe

st.set_page_config(page_title="Wall Integrity & Risk", layout="wide")
st.title("🧱 Options Wall Integrity & Risk Parameters")

# Safeguard: Check if Kite is connected
if 'kite' not in st.session_state:
    st.error("⚠️ Kite API is not connected. Please log in via the main page.")
    st.stop()

kite = st.session_state['kite']

st.subheader("1. System Filters")
col1, col2 = st.columns(2)

with col1:
    vix_val = oe.get_current_vix(kite) # PASSED KITE HERE
    if 13 <= vix_val <= 19:
        st.success(f"🟢 India VIX: {vix_val} (Optimal: 13-19)")
    else:
        st.warning(f"🟡 India VIX: {vix_val} (Outside optimal zone)")

with col2:
    # Assuming spot_price and options_df are fetched or stored in session state
    spot_price = st.session_state.get('spot_price', 22000)
    options_df = st.session_state.get('options_df', None)
    
    if options_df is not None:
        total_gex = oe.get_total_gex(options_df, spot_price) # PASSED ARGUMENTS
        if total_gex > 0:
            st.success(f"🟢 Total GEX: +{total_gex} (Positive - Favorable)")
        else:
            st.error(f"🔴 Total GEX: {total_gex} (Negative - High risk)")
    else:
        st.info("Waiting for options chain data...")

st.divider()

st.subheader("2. Contract Selection & Adjustments")
st.info("""
**Execution Blueprint:**
* **Entry:** Trade Monthly contracts (30-45 DTE).
* **Exit:** Close out strictly at **21 DTE**.
* **Adjustments:** Trigger defensive adjustments if spot breaches the **30-min ORB**.
""")

st.divider()

st.subheader("3. Wall Stability Check")
# Passing dummy max strikes and current time for the stability check
import datetime
call_hold_time, put_hold_time = oe.get_strike_hold_times(kite, 22500, 21500, datetime.datetime.now())

col3, col4 = st.columns(2)
col3.metric("Call Max Strike Stability", f"{call_hold_time} mins")
col4.metric("Put Max Strike Stability", f"{put_hold_time} mins")
