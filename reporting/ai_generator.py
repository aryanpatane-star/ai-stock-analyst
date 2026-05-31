import os
import google.generativeai as genai

def generate_ai_call(ticker: str, current_fundamentals: dict, matches: list, outcome_summaries: list, api_key: str) -> str:
    """
    Generates a natural language trading call using Google Gemini.
    
    Args:
        ticker: The stock ticker.
        current_fundamentals: Dict of fundamental metrics.
        matches: List of historical match dictionaries.
        outcome_summaries: List of strings describing what happened after each match.
        api_key: The Google Gemini API key.
        
    Returns:
        A markdown string containing the final AI call.
    """
    
    prompt = f"""
    You are an expert AI Stock Analyst. Analyze the following data for {ticker} and provide a clear, actionable trading call (BUY, SELL, or HOLD) with detailed reasoning.
    
    Current Fundamentals:
    {current_fundamentals}
    
    We have found historical patterns in the stock's price action that are mathematically similar (using Dynamic Time Warping) to the last 30 days of price action.
    
    Historical Outcomes:
    """
    for match, outcome in zip(matches, outcome_summaries):
        prompt += f"- Date Matched: {match['start_date']} to {match['end_date']}. Outcome: {outcome}\n"
        
    prompt += """
    Based on the fundamental context and how this pattern played out historically, what is your prediction for the next 30 days? 
    What are the potential upside targets and downside risks? 
    Format your response in Markdown with clear headings.
    """

    if not api_key:
        return "⚠️ **GEMINI_API_KEY not provided.**\n\nPlease provide a Gemini API key to view the AI analysis."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest') # or whatever is available
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI call: {e}"
