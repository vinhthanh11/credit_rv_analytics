import pandas as pd

from ggsheet import get_records


def load_bonds(sheet_name):
    records = get_records(sheet_name)

    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["Coupon"] = pd.to_numeric(df["Coupon"], errors="coerce")
    df["Maturity"] = pd.to_datetime(df["Maturity"], errors="coerce")

    return df


if __name__ == "__main__":
    bonds = load_bonds()
    print(bonds)