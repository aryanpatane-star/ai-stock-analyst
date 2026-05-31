import streamlit as st
import pandas as pd
import sys
import os

# Ensure local modules can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_ingestion.price_data import fetch_historical_prices
from data_ingestion.fundamental_data import fetch_fundamental_data
from pattern_recognition.dtw_matcher import find_historical_match
from reporting.charting import plot_historical_match
from reporting.ai_generator import generate_ai_call

st.set_page_config(page_title="AI Stock Backtester", layout="wide")

st.title("AI-Driven Stock Pattern Backtester")
st.markdown("Find historical similarities in stock price action and analyze the fundamental context.")

# Sidebar for inputs
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Gemini API Key (Optional)", type="password", help="Enter your Gemini API key to enable AI Analyst Calls. Get one at aistudio.google.com")
    ticker = st.text_input("Stock Ticker", value="RELIANCE.NS")
    period = st.selectbox("Historical Period", ["2y", "5y", "10y", "max"], index=1)
    window_size = st.slider("Pattern Window (Days)", min_value=10, max_value=90, value=30)
    analyze_btn = st.button("Analyze Pattern")

if analyze_btn:
    with st.spinner(f"Fetching data for {ticker}..."):
        df = fetch_historical_prices(ticker, period=period)
        fundamentals = fetch_fundamental_data(ticker)
        
    if df.empty:
        st.error(f"Failed to fetch price data for {ticker}. Check the ticker symbol.")
    else:
        st.subheader("Fundamental Overview")
        cols = st.columns(4)
        cols[0].metric("Sector", fundamentals.get("Sector", "N/A"))
        cols[1].metric("Industry", fundamentals.get("Industry", "N/A"))
        cols[2].metric("P/E Ratio", fundamentals.get("TrailingPE", "N/A"))
        cols[3].metric("Div Yield", fundamentals.get("DividendYield", "N/A"))
        
        with st.spinner("Searching for historical pattern matches (DTW)..."):
            matches = find_historical_match(df, window_size=window_size, top_n=3)
            
        if not matches:
            st.warning("Not enough historical data to find matches.")
        else:
            st.subheader("Top Historical Pattern Matches")
            outcome_summaries = []
            
            for i, match in enumerate(matches):
                st.markdown(f"### Match {i+1}: {match['start_date']} to {match['end_date']}")
                st.markdown(f"**Similarity Score (DTW Distance):** {match['distance']:.2f} (Lower is better)")
                
                # Plot
                fig = plot_historical_match(
                    df, 
                    current_window_size=window_size, 
                    match_start=match['start_date'], 
                    match_end=match['end_date'],
                    ticker=ticker
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # We can calculate what happened *after* this match
                # 30 days after the end_date
                try:
                    match_end_idx = df.index.get_loc(match['end_date'])
                    future_idx = min(match_end_idx + 30, len(df) - 1)
                    future_date = df.index[future_idx]
                    price_at_match_end = df.iloc[match_end_idx]['Close']
                    price_30d_later = df.iloc[future_idx]['Close']
                    
                    pct_change = ((price_30d_later - price_at_match_end) / price_at_match_end) * 100
                    
                    st.info(f"**Outcome 30 days later:** Price moved from {price_at_match_end:.2f} to {price_30d_later:.2f} ({pct_change:+.2f}%)")
                    outcome_summaries.append(f"Price moved from {price_at_match_end:.2f} to {price_30d_later:.2f} ({pct_change:+.2f}%)")
                except Exception as e:
                    st.write("Could not calculate future outcome.")
                    outcome_summaries.append("Outcome unknown.")
                    
            st.success("Pattern Analysis Complete!")
            
            st.header("AI Analyst Call")
            
            # Determine which API key to use (sidebar input overrides environment variable)
            final_api_key = api_key_input if api_key_input else os.environ.get("GEMINI_API_KEY")
            
            if not final_api_key:
                st.warning("⚠️ Please enter a Gemini API Key in the sidebar to generate the AI Analyst call.")
            else:
                with st.spinner("Generating AI Trading Call..."):
                    ai_call = generate_ai_call(ticker, fundamentals, matches, outcome_summaries, final_api_key)
                    st.markdown(ai_call)
