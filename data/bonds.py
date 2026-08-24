import pandas as pd

from ggsheet import get_records


def load_bonds():
    records = get_records("Bonds")

    df = pd.DataFrame(records)

    if df.empty:
        return df

    df["Coupon"] = pd.to_numeric(df["Coupon"], errors="coerce")
    df["Maturity"] = pd.to_datetime(df["Maturity"], errors="coerce")

    return df


if __name__ == "__main__":
    bonds = load_bonds()
    print(bonds)