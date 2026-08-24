import pandas as pd

from ggsheet import get_records


def load_prices():
    records = get_records("Daily_Prices")

    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

    return df


if __name__ == "__main__":
    prices = load_prices()
    print(prices)