import streamlit as st
import engine         # Macro Profile & RSI
import options_engine as oe  # Micro Integrity & Options

st.set_page_config(page_title="Master Synthesis", layout="wide", page_icon="🧠")
st.title("🧠 Master Synthesis & Execution")
st.markdown("Aggregating macro auction structure, options chain integrity, and systemic risk for Nifty 50.")

# ==========================================
# 1. DATA AGGREGATION (Pulling from all modules)
# ==========================================

# -- Page 1 & 2: Macro --
macro_regime = engine.get_macro_regime() # e.g., "Controlled Bullish Drift", "Balanced Rotation"
# Assuming engine can also pass the profile shape and weekly value location for deeper context
profile_shape = engine.get_profile_shape() 
weekly_location = engine.get_weekly_location()

# -- Page 3: Risk & Stability --
vix_val = oe.get_current_vix()
vix_pass = 13 <= vix_val <= 19
total_gex = oe.get_total_gex()
gex_pass = total_gex > 0
call_hold_time, put_hold_time = oe.get_strike_hold_times()
min_stability = min(call_hold_time, put_hold_time)
stability_pass = min_stability >= 120

# -- Page 4: Micro Options Defense --
states = oe.get_pillar_states()
put_solid = states['put_vol']['ratio'] < 0.75 and states['put_oi']['ratio'] < 0.75
call_solid = states['call_vol']['ratio'] < 0.75 and states['call_oi']['ratio'] < 0.75

# Determine Options Bias
options_bias = "Neutral"
if put_solid and not call_solid: options_bias = "Bullish (Call Weakness)"
elif call_solid and not put_solid: options_bias = "Bearish (Put Weakness)"
elif put_solid and call_solid: options_bias = "Locked (Both Fortresses)"
else: options_bias = "Volatile (Dual Weakness)"


# ==========================================
# 2. EXECUTIVE DASHBOARD
# ==========================================
st.subheader("System State")
c1, c2, c3, c4 = st.columns(4)

c1.metric("Macro Regime", macro_regime, weekly_location)
c2.metric("Options Bias", options_bias)
c3.metric("Systemic Risk", "Clear" if vix_pass and gex_pass else "Elevated", 
          f"VIX: {vix_val} | GEX: {'+' if gex_pass else '-'}")
c4.metric("Wall Stability", f"{min_stability} mins", 
          "Pass" if stability_pass else "Wait - Developing")

st.divider()

# ==========================================
# 3. DEEP SYNTHESIS (The "Why")
# ==========================================
st.subheader("🔍 Market Synthesis")

with st.container(border=True):
    # Analyze Alignment between Macro and Micro
    is_aligned = False
    synthesis_text = ""

    if "Bullish" in macro_regime and options_bias == "Bullish (Call Weakness)":
        is_aligned = True
        synthesis_text = f"**Strong Bullish Alignment:** The Macro auction structure is showing {macro_regime} with acceptance {weekly_location}. This structural strength is actively confirmed by market makers: Put support is a highly concentrated Fortress (<75% challenger), while Call resistance is fragmenting, allowing the upward drift to continue."
    
    elif "Bearish" in macro_regime and options_bias == "Bearish (Put Weakness)":
        is_aligned = True
        synthesis_text = f"**Strong Bearish Alignment:** The Macro auction structure is showing {macro_regime} with acceptance {weekly_location}. Market makers confirm this weakness: Call resistance is an impenetrable Fortress, while Put support is shifting outward or fragmenting (>75% challenger), clearing the path for further downside."
    
    elif macro_regime == "Balanced Rotation" and options_bias == "Locked (Both Fortresses)":
        is_aligned = True
        synthesis_text = f"**Total Market Balance:** The Macro auction is printing a {profile_shape} shape, indicating fair value agreement. Options flow confirms this stagnation perfectly—both Call and Put sides are fortified Fortresses. The market is trapped and premium decay is the dominant force."
    
    elif macro_regime == "Balanced Rotation" and options_bias != "Locked (Both Fortresses)":
        synthesis_text = f"**Pending Breakout:** While the Macro structure still shows historical balance ({profile_shape}), the options chain is detecting a shift. The {options_bias} flow suggests market makers are repositioning for a structural break. Wait for the Macro profile to confirm the direction."
    
    else:
        synthesis_text = f"**Structural Conflict Detected:** The Macro engine suggests a {macro_regime}, but the real-time Options flow is contradicting this, showing a {options_bias} bias. This usually indicates a trap or institutional distribution/accumulation hiding behind price action. High risk of mean reversion or sudden volatility."

    st.markdown(synthesis_text)

st.divider()

# ==========================================
# 4. FINAL VERDICT & EXECUTION PLAN
# ==========================================
st.subheader("⚡ Execution Playbook")

# Core safety check
if not (vix_pass and gex_pass and stability_pass):
    st.error("""
    🛑 **STAND DOWN: Risk Parameters Not Met**
    Even if directional signals align, systemic filters demand capital preservation.
    """)
    st.markdown(f"""
    * **VIX Check:** {vix_val} (Target: 13-19)
    * **GEX Check:** {'Positive' if gex_pass else 'Negative'} (Target: Positive)
    * **Stability Check:** {min_stability} mins (Target: >= 120 mins)
    """)

elif not is_aligned:
    st.warning("""
    ⚠️ **NO TRADE: Macro/Micro Divergence**
    Auction structure and Market Maker positioning are fighting each other. Cash is a position. Let the Wednesday-Tuesday profile develop further.
    """)

else:
    # Execution Logic based on aligned states
    if "Bullish" in macro_regime:
        st.success("✅ **APPROVED: Sell Put Credit Spreads (PCS)**")
        with st.expander("View Execution & Management Rules", expanded=True):
            st.markdown(f"""
            * **Structure:** Market is in {macro_regime}. Put wall is solid.
            * **Entry:** Sell the dominant Put Strike identified in the Four Pillars.
            * **Contract Selection:** Use Monthly expiry (30-45 DTE) to flatten Gamma risk.
            * **Exit Strategy:** Close position strictly at 21 DTE.
            * **Defensive Adjustment:** Triggered only if Nifty Spot breaches the **30-Minute ORB low**.
            """)
            
    elif "Bearish" in macro_regime:
        st.success("✅ **APPROVED: Sell Call Credit Spreads (CCS)**")
        with st.expander("View Execution & Management Rules", expanded=True):
            st.markdown(f"""
            * **Structure:** Market is in {macro_regime}. Call wall is solid.
            * **Entry:** Sell the dominant Call Strike identified in the Four Pillars.
            * **Contract Selection:** Use Monthly expiry (30-45 DTE) to flatten Gamma risk.
            * **Exit Strategy:** Close position strictly at 21 DTE.
            * **Defensive Adjustment:** Triggered only if Nifty Spot breaches the **30-Minute ORB high**.
            """)
            
    elif macro_regime == "Balanced Rotation":
        st.success("✅ **APPROVED: Sell Iron Condor / Neutral Premium**")
        with st.expander("View Execution & Management Rules", expanded=True):
            st.markdown(f"""
            * **Structure:** Market is range-bound. Both walls are Fortresses.
            * **Entry:** Sell strikes safely outside the Wednesday-Tuesday Weekly VAH and VAL.
            * **Contract Selection:** Use Monthly expiry (30-45 DTE).
            * **Exit Strategy:** Close position strictly at 21 DTE.
            * **Defensive Adjustment:** Monitor the 75% Challenger ratio. If either wall begins to fragment (>75%), roll the untested side closer to spot to collect credit, or close the tested side.
            """)
