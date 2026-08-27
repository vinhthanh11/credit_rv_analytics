import pandas as pd

from ggsheet import get_records


def load_treasury(sheet_name):
    records = get_records(sheet_name)

    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for column in ["2Y", "5Y", "10Y", "30Y"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df


if __name__ == "__main__":
    treasury = load_treasury()
    print(treasury)