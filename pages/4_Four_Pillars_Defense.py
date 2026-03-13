import streamlit as st
import options_engine as oe

st.set_page_config(page_title="Four Pillars Defense", layout="wide")
st.title("🛡️ The Four Pillars Defense Matrix")

# Safeguard: Ensure data exists
if 'options_df' not in st.session_state or 'spot_price' not in st.session_state:
    st.warning("⚠️ Waiting for Options Chain data. Please ensure the data fetcher is running.")
    st.stop()

options_df = st.session_state['options_df']
spot_price = st.session_state['spot_price']

# PASSED ARGUMENTS HERE
states = oe.get_pillar_states(options_df, spot_price) 

def render_pillar(title, data):
    st.subheader(title)
    if data is None:
        st.write("Insufficient data.")
        return
        
    if data['ratio'] < 0.75:
        st.success(f"🟢 **FORTRESS** (Challenger is at {data['ratio']*100:.1f}%)")
        st.write(f"Highest: {data['max_strike']} | 2nd Highest: {data['second_strike']}")
    else:
        shift_type = data['shift_direction']
        st.error(f"🚨 **WEAKNESS: Shifting {shift_type}** (Challenger at {data['ratio']*100:.1f}%)")
        st.write(f"Highest: {data['max_strike']} is being challenged by {data['second_strike']}.")

col1, col2 = st.columns(2)
with col1:
    render_pillar("Call Volume (Immediate Resistance)", states['call_vol'])
    render_pillar("Call OI (Structural Resistance)", states['call_oi'])

with col2:
    render_pillar("Put Volume (Immediate Support)", states['put_vol'])
    render_pillar("Put OI (Structural Support)", states['put_oi'])
