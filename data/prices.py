import pandas as pd

from ggsheet import get_records


def load_prices(sheet_name):
    records = get_records(sheet_name)

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