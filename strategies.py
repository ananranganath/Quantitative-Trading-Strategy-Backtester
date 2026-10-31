import pandas as pd

from data import load_prices

def ma_crossover(prices, short_window=50, long_window=200):
    """Hold the stock when the short average is above the long average."""
    df = prices[["close"]].copy()

    # Rolling averages. The first 49 (or 199) days have no value yet,
    # because there isn't enough history.
    df["ma_short"] = df["close"].rolling(short_window).mean()
    df["ma_long"] = df["close"].rolling(long_window).mean()

    # Signal: 1 = in the market, 0 = out. Days without enough history count as 0.
    df["signal"] = (df["ma_short"] > df["ma_long"]).astype(int)

    # Look-ahead fix: the signal uses today's closing price so we can
    # only act on it after the close. Today's signal sets tomorrow's position.
    df["position"] = df["signal"].shift(1).fillna(0).astype(int)

    return df

def trade_dates(df):
    """Return only the days the postion changed: a list of buys and sells."""
    changes = df["position"].diff().fillna(0)
    trades = df.loc[changes != 0, ["close", "position"]].copy()
    trades["action"] = trades["position"].map({1: "BUY", 0: "SELL"})
    return trades[["close", "action"]]

if __name__ == "__main__":
    df = ma_crossover(load_prices("SPY"))

    print("Last 5 days:")
    print(df.tail().round(2))

    trades = trade_dates(df)
    print("\nTrades:")
    print(trades.round(2))

    print(f"\n{len(trades)} trades. In the market {df['position'].mean():.0%} of days.")

