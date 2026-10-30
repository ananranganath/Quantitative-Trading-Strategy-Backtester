import sqlite3

import pandas as pd
import yfinance as yf

#The stocks to download. SPY tracks the S&P 500 and is our benchmark.
TICKERS = ["SPY", "AAPL", "MSFT", "JPM"]
DB_PATH = "prices.db"

def download_prices(ticker):
    """Download 10 years of daily prices for one ticker and then tidy them up."""
    # auto_adust=True corrects prices for splits and dividends,
    # so returns are distorted by thngs like a 4-for-1 split.
    df = yf.Ticker(ticker).history(period="10y", auto_adjust=True)

    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")

    # Keep only the columns we need, and move the date from the index to a column.
    df = df[["Open", "High", "Low", "Close", "Volume"]].reset_index()

    # Lowercase names are easier to write in SQL.
    df.columns = ["date", "open", "high", "low", "close", "volume"]

    # Store dates as plain text like 2024-03-15, which SQLite sorts correctly.
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Label each row with its ticker so all stocks can share one table.
    df["ticker"] = ticker
    return df

def main():
    frames = []
    for ticker in TICKERS:
        print(f"Downloading {ticker}...")
        frames.append(download_prices(ticker))

    # Stack the separate tables into one long table.
    prices = pd.concat(frames, ignore_index=True)

    # Write into SQLite. "replace" means rerunning the script starts fresh
    # instead of adding duplicate rows.
    with sqlite3.connect(DB_PATH) as conn:
        prices.to_sql("prices", conn, if_exists="replace", index=False)

    print(f"Saved {len(prices):,} rows to {DB_PATH}")

if __name__ == "__main__":
    main()