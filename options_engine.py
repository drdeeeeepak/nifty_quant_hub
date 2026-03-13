import pandas as pd
import numpy as np
import datetime

# Note: For accurate GEX, we will use standard Black-Scholes approximations. 
# You will need to import py_vollib or scipy if calculating greeks locally.

def analyze_pillar(options_df, option_type, metric, spot_price):
    """
    Analyzes a specific pillar (CE Volume, PE Volume, CE OI, PE OI) for the 75% Wall Integrity rule.
    """
    # Filter for the correct instrument type (CE or PE)
    filtered_df = options_df[options_df['instrument_type'] == option_type].copy()
    
    # Sort descending by the target metric (volume or oi)
    sorted_df = filtered_df.sort_values(by=metric, ascending=False).reset_index(drop=True)
    
    if len(sorted_df) < 2:
        return None # Not enough data
        
    max_row = sorted_df.iloc[0]
    sec_row = sorted_df.iloc[1]
    
    max_strike = max_row['strike']
    max_val = max_row[metric]
    sec_strike = sec_row['strike']
    sec_val = sec_row[metric]
    
    # Calculate Challenger Ratio
    ratio = sec_val / max_val if max_val > 0 else 0
    
    # Determine Shift Direction (Only relevant if ratio >= 0.75)
    shift_direction = "None"
    if ratio >= 0.75:
        if option_type == 'CE':
            # CE shifts inward if challenger is a lower strike (closer to spot)
            shift_direction = "Inward" if sec_strike < max_strike else "Outward"
        elif option_type == 'PE':
            # PE shifts inward if challenger is a higher strike (closer to spot)
            shift_direction = "Inward" if sec_strike > max_strike else "Outward"

    return {
        'max_strike': max_strike,
        'max_val': max_val,
        'second_strike': sec_strike,
        'second_val': sec_val,
        'ratio': ratio,
        'shift_direction': shift_direction
    }

def get_pillar_states(options_df, spot_price):
    """
    Runs the 75% analysis across all Four Pillars.
    Expects options_df to have columns: ['strike', 'instrument_type', 'volume', 'oi']
    """
    return {
        'call_vol': analyze_pillar(options_df, 'CE', 'volume', spot_price),
        'call_oi': analyze_pillar(options_df, 'CE', 'oi', spot_price),
        'put_vol': analyze_pillar(options_df, 'PE', 'volume', spot_price),
        'put_oi': analyze_pillar(options_df, 'PE', 'oi', spot_price)
    }

def get_current_vix(kite):
    """
    Fetches the current India VIX value.
    Requires an active kite object.
    """
    try:
        # India VIX instrument token usually needs to be fetched from the instrument list
        # For example purposes, assuming instrument_token for INDIA VIX is 264969
        quote = kite.quote("NSE:INDIA VIX")
        return quote["NSE:INDIA VIX"]["last_price"]
    except Exception as e:
        print(f"Error fetching VIX: {e}")
        return 0.0

def get_strike_hold_times(kite, max_call_strike, max_put_strike, current_time):
    """
    Evaluates if the max strikes have maintained their dominant position for >= 120 minutes.
    (This requires a database or running state in your app to track historical max strikes throughout the day).
    
    Returns: (call_hold_time_mins, put_hold_time_mins)
    """
    # IMPLEMENTATION NOTE: 
    # To do this natively without a database, you would need to fetch 1-min historical data 
    # for the entire options chain for the day and walk forward. 
    # For Streamlit state management, it's easier to store the timestamp when a new max strike is formed
    # in st.session_state and compare it to datetime.now().
    
    # Placeholder return simulating stable walls:
    return 125, 130 

def get_total_gex(options_df, spot_price):
    """
    Calculates the Total Gamma Exposure (GEX) of the chain.
    Positive GEX = MMs suppress volatility (Good for credit selling).
    Negative GEX = MMs amplify volatility (Bad for credit selling).
    """
    # Requires option greek calculations. 
    # If Kite provides Gamma in the quote, sum(Call Gamma * OI) - sum(Put Gamma * OI).
    # Placeholder return for UI setup:
    return 1500000 

def check_120_min_stability(call_hold_time, put_hold_time):
    """
    Returns the minimum stability time between the two walls.
    """
    return min(call_hold_time, put_hold_time)
