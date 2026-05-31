import yfinance as yf

def fetch_fundamental_data(ticker: str) -> dict:
    """
    Fetches basic fundamental data and company info for a given ticker.
    
    Args:
        ticker (str): The stock ticker (e.g., 'RELIANCE.NS').
        
    Returns:
        dict: A dictionary containing key fundamental metrics.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract relevant info
        fundamentals = {
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A"),
            "MarketCap": info.get("marketCap", "N/A"),
            "TrailingPE": info.get("trailingPE", "N/A"),
            "ForwardPE": info.get("forwardPE", "N/A"),
            "DividendYield": info.get("dividendYield", "N/A"),
            "52WeekHigh": info.get("fiftyTwoWeekHigh", "N/A"),
            "52WeekLow": info.get("fiftyTwoWeekLow", "N/A"),
            "LongBusinessSummary": info.get("longBusinessSummary", "N/A")
        }
        
        return fundamentals
    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
        return {}

if __name__ == "__main__":
    ticker = "RELIANCE.NS"
    print(f"Fetching fundamentals for {ticker}...")
    funds = fetch_fundamental_data(ticker)
    for k, v in funds.items():
        if k == "LongBusinessSummary":
            print(f"{k}: {v[:100]}...")
        else:
            print(f"{k}: {v}")
