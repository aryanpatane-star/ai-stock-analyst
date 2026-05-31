import numpy as np
import pandas as pd
from fastdtw import fastdtw

def normalize_series(series: pd.Series) -> np.ndarray:
    """
    Min-Max normalizes a time series so patterns can be compared regardless of absolute price.
    """
    s_min = series.min()
    s_max = series.max()
    if s_max == s_min:
        return np.zeros(len(series))
    return ((series - s_min) / (s_max - s_min)).values

def find_historical_match(df: pd.DataFrame, window_size: int = 30, top_n: int = 3):
    """
    Finds the most similar historical price action to the current recent window.
    
    Args:
        df (pd.DataFrame): Historical price data with 'Close' column.
        window_size (int): The number of days to compare (e.g., last 30 days).
        top_n (int): Number of top matches to return.
        
    Returns:
        list of dicts containing match details (start_date, end_date, distance).
    """
    if len(df) < window_size * 2:
        print("Not enough data to find a historical match.")
        return []
        
    # Extract the current pattern (last 'window_size' days)
    current_series = df['Close'].iloc[-window_size:]
    current_norm = normalize_series(current_series)
    
    matches = []
    
    # We iterate over the historical data, stopping before the current window
    # to avoid matching the current window with itself.
    search_space_end = len(df) - window_size - 10 # 10 days buffer
    
    if search_space_end < window_size:
        return []
        
    for i in range(search_space_end - window_size):
        hist_window = df['Close'].iloc[i : i + window_size]
        hist_norm = normalize_series(hist_window)
        
        # Calculate Dynamic Time Warping distance
        distance, path = fastdtw(current_norm, hist_norm, dist=lambda a, b: abs(a - b))
        
        start_date = df.index[i]
        end_date = df.index[i + window_size - 1]
        
        matches.append({
            'start_date': start_date,
            'end_date': end_date,
            'distance': distance,
            'index_start': i,
            'index_end': i + window_size - 1
        })
        
    # Sort matches by distance (lowest is most similar)
    matches.sort(key=lambda x: x['distance'])
    
    # Filter overlapping matches to ensure distinct periods
    distinct_matches = []
    for match in matches:
        if not distinct_matches:
            distinct_matches.append(match)
            continue
            
        # Check for overlap with existing distinct matches
        overlap = False
        for dm in distinct_matches:
            if abs(match['index_start'] - dm['index_start']) < window_size:
                overlap = True
                break
                
        if not overlap:
            distinct_matches.append(match)
            if len(distinct_matches) == top_n:
                break
                
    return distinct_matches

if __name__ == "__main__":
    # Test script if run directly
    # Need to import price_data here
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from data_ingestion.price_data import fetch_historical_prices
    
    ticker = "RELIANCE.NS"
    print(f"Testing DTW match for {ticker}...")
    df = fetch_historical_prices(ticker, period="2y")
    if not df.empty:
        matches = find_historical_match(df, window_size=30, top_n=3)
        for i, m in enumerate(matches):
            print(f"Match {i+1}: {m['start_date']} to {m['end_date']} (Distance: {m['distance']:.4f})")
