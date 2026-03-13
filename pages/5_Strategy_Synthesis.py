import streamlit as st
import datetime
import engine         
import options_engine as oe  

st.set_page_config(page_title="Master Synthesis", layout="wide", page_icon="🧠")
st.title("🧠 Master Synthesis & Execution")

# Safeguard: Check for all required data
required_keys = ['kite', 'df_daily', 'df_weekly', 'options_df', 'spot_price']
missing_keys = [key for key in required_keys if key not in st.session_state]

if missing_keys:
    st.warning(f"⚠️ Waiting for background data: {', '.join(missing_keys)}")
    st.stop()

# Load data from session state
kite = st.session_state['kite']
df_daily = st.session_state['df_daily']
df_weekly = st.session_state['df_weekly']
options_df = st.session_state['options_df']
spot_price = st.session_state['spot_price']

# PASSED ALL REQUIRED ARGUMENTS
macro_regime = engine.get_macro_regime(df_daily, df_weekly) 
profile_shape = engine.get_profile_shape(df_daily) 
weekly_location = engine.get_weekly_location(spot_price, df_weekly)

vix_val = oe.get_current_vix(kite)
vix_pass = 13 <= vix_val <= 19

total_gex = oe.get_total_gex(options_df, spot_price)
gex_pass = total_gex > 0

call_hold_time, put_hold_time = oe.get_strike_hold_times(kite, 22500, 21500, datetime.datetime.now())
min_stability = min(call_hold_time, put_hold_time)
stability_pass = min_stability >= 120

states = oe.get_pillar_states(options_df, spot_price)
put_solid = states['put_vol']['ratio'] < 0.75 and states['put_oi']['ratio'] < 0.75
call_solid = states['call_vol']['ratio'] < 0.75 and states['call_oi']['ratio'] < 0.75

# ... (The rest of the UI rendering code for Page 5 remains exactly the same) ...

st.subheader("System State")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Macro Regime", macro_regime)
c2.metric("Systemic Risk", "Clear" if vix_pass and gex_pass else "Elevated")
# etc...
