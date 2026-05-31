import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_historical_prices(ticker: str, period: str = "5y") -> pd.DataFrame:
    """
    Fetches historical OHLCV data for a given ticker.
    
    Args:
        ticker (str): The stock ticker (e.g., 'RELIANCE.NS').
        period (str): The period to fetch (e.g., '5y', 'max').
        
    Returns:
        pd.DataFrame: A pandas DataFrame containing the historical prices.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            print(f"Warning: No price data found for {ticker}")
            return df
            
        # Clean up the dataframe
        df = df.reset_index()
        # yfinance sometimes returns timezone-aware datetimes, ensure it's simple dates
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        df.set_index('Date', inplace=True)
        
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Simple test
    ticker = "RELIANCE.NS"
    print(f"Fetching data for {ticker}...")
    df = fetch_historical_prices(ticker)
    print(df.head())
    print(df.tail())
