# pages/3_Wall_Integrity_Risk.py
import streamlit as st
import options_engine as oe

st.set_page_config(page_title="Wall Integrity & Risk", layout="wide")
st.title("🧱 Options Wall Integrity & Risk Parameters")

# --- Section 1: Macro Option Filters (VIX & GEX) ---
st.subheader("1. System Filters")
col1, col2 = st.columns(2)

with col1:
    vix_val = oe.get_current_vix() # Fetches India VIX
    if 13 <= vix_val <= 19:
        st.success(f"🟢 India VIX: {vix_val} (Optimal for Credit Spreads: 13-19)")
    else:
        st.warning(f"🟡 India VIX: {vix_val} (Outside optimal 13-19 zone)")

with col2:
    total_gex = oe.get_total_gex() # Calculates Gamma Exposure
    if total_gex > 0:
        st.success(f"🟢 Total GEX: +{total_gex} (Positive - Favorable for selling)")
    else:
        st.error(f"🔴 Total GEX: {total_gex} (Negative - High risk of expansion)")

st.divider()

# --- Section 2: Expiry & Trade Lifecycle ---
st.subheader("2. Contract Selection & Adjustments")
st.info("""
**Execution Blueprint:**
* **Entry:** Trade Monthly contracts (30-45 DTE) to maximize premium capture while flattening the Gamma curve.
* **Exit:** Close out positions strictly at **21 DTE** to avoid late-stage Gamma explosion.
* **Adjustments:** Use the **30-Minute Opening Range Breakout (ORB)**. If the underlying spot breaches the 30-min ORB against the spread, trigger the defensive adjustment.
""")

st.divider()

# --- Section 3: Time Stability ---
st.subheader("3. Wall Stability Check")
st.markdown("A structural wall is only valid if the highest concentration strike holds its position for at least **120 minutes**.")

call_hold_time, put_hold_time = oe.get_strike_hold_times() # Checks Kite historical data for the session

col3, col4 = st.columns(2)
with col3:
    st.metric("Call Max Strike Stability", f"{call_hold_time} mins", 
              delta="Stable" if call_hold_time >= 120 else "Unstable", delta_color="normal" if call_hold_time >= 120 else "inverse")
with col4:
    st.metric("Put Max Strike Stability", f"{put_hold_time} mins", 
              delta="Stable" if put_hold_time >= 120 else "Unstable", delta_color="normal" if put_hold_time >= 120 else "inverse")
