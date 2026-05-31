import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_historical_match(df: pd.DataFrame, current_window_size: int, match_start: str, match_end: str, ticker: str):
    """
    Creates a side-by-side subplot of the current price action vs the historically matched price action.
    """
    current_df = df.iloc[-current_window_size:]
    
    # Filter historical match df
    # Ensure indices are aligned by converting strings to datetime if needed, 
    # but df.index should already be date/datetime
    hist_df = df.loc[match_start:match_end]
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        f"Current Action (Last {current_window_size} Days)", 
        f"Historical Match ({match_start} to {match_end})"
    ))
    
    # Current Candlestick
    fig.add_trace(go.Candlestick(
        x=current_df.index,
        open=current_df['Open'],
        high=current_df['High'],
        low=current_df['Low'],
        close=current_df['Close'],
        name='Current'
    ), row=1, col=1)
    
    # Historical Candlestick
    fig.add_trace(go.Candlestick(
        x=hist_df.index,
        open=hist_df['Open'],
        high=hist_df['High'],
        low=hist_df['Low'],
        close=hist_df['Close'],
        name='Historical'
    ), row=1, col=2)
    
    fig.update_layout(
        title=f"{ticker} - Pattern Similarity Match",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        xaxis2_rangeslider_visible=False,
        template="plotly_dark",
        height=500
    )
    
    return fig
