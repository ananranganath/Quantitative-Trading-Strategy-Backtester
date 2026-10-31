import sqlite3

import pandas as pd

DB_PATH = "prices.db"

def load_prices(ticker):
    """Load one ticker's daily prices from SQLite, indexed by date."""
    # The ? is a placeholder. Passing the ticker separately is safer than pasting it into the SQL string.
    query = """
        SELECT date, open, high, low, close, volume
        FROM prices
        WHERE ticker = ?
        ORDER BY date
    """
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(query, conn, params=(ticker,), parse_dates=["date"])
    if df.empty:
        raise ValueError(f"No prices found for {ticker}. DId you run load_data.py?")

    # Using the date as the index makes time-based calculations easy.
    return df.set_index("date")