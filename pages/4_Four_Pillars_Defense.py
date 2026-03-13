# pages/4_Four_Pillars_Defense.py
import streamlit as st
import options_engine as oe

st.set_page_config(page_title="Four Pillars Defense", layout="wide")
st.title("🛡️ The Four Pillars Defense Matrix")

# oe.get_pillar_states() returns a dictionary calculating highest vs 2nd highest strikes 
# and flags if the 2nd highest is > 75%. It also returns shift direction (Inward/Outward).
states = oe.get_pillar_states() 

def render_pillar(title, data):
    st.subheader(title)
    if data['ratio'] < 0.75:
        st.success(f"🟢 **FORTRESS** (Challenger is at {data['ratio']*100:.1f}%)")
        st.write(f"Highest: {data['max_strike']} | 2nd Highest: {data['second_strike']}")
    else:
        shift_type = data['shift_direction'] # "Inward" (closer to ATM) or "Outward" (OTM)
        st.error(f"🚨 **WEAKNESS: Shifting {shift_type}** (Challenger at {data['ratio']*100:.1f}%)")
        st.write(f"Highest: {data['max_strike']} is being challenged by {data['second_strike']}.")

col1, col2 = st.columns(2)
with col1:
    render_pillar("Call Volume (Immediate Resistance)", states['call_vol'])
    render_pillar("Call OI (Structural Resistance)", states['call_oi'])

with col2:
    render_pillar("Put Volume (Immediate Support)", states['put_vol'])
    render_pillar("Put OI (Structural Support)", states['put_oi'])

st.divider()

# Predictive Summation Logic
st.subheader("Predictive Edge")
put_solid = states['put_vol']['ratio'] < 0.75 and states['put_oi']['ratio'] < 0.75
call_weak = states['call_vol']['ratio'] >= 0.75 and states['call_oi']['ratio'] >= 0.75

if put_solid and call_weak:
    st.info("📈 **Trend Day Up Probability:** Put support is a Fortress, Call resistance is fragmented/shifting.")
elif (not put_solid) and (not call_weak): # Call solid, Put weak
    st.info("📉 **Trend Day Down Probability:** Call resistance is a Fortress, Put support is fragmented/shifting.")
elif put_solid and (not call_weak):
    st.info("↔️ **Range Bound / Premium Decay:** Both sides are Fortresses. Perfect for Iron Condors.")
else:
    st.warning("⚠️ **Volatile / Breakout:** Both sides show weakness. Avoid neutral premium selling.")
