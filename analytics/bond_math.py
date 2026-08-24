import pandas as pd
import numpy as np
from scipy.optimize import brentq


FACE_VALUE = 100
COUPON_FREQUENCY = 2


def years_to_maturity(maturity_date, valuation_date):
    maturity_date = pd.Timestamp(maturity_date)
    valuation_date = pd.Timestamp(valuation_date)

    days = (maturity_date - valuation_date).days

    return max(days / 365.25, 0)


def bond_price_from_yield(face_value, coupon_rate, years, ytm, frequency=2):
    """
    Price a plain-vanilla fixed-rate bond.

    coupon_rate and ytm should be decimals:
    5.25% -> 0.0525
    """

    periods = max(round(years * frequency), 1)
    coupon_payment = (face_value * coupon_rate / frequency)
    discount_rate = ytm / frequency
    price = 0

    for period in range(1, periods + 1):
        cash_flow = coupon_payment
        if period == periods:
            cash_flow += face_value
        price += cash_flow / (
            (1 + discount_rate) ** period
        )
    return price


def calculate_ytm(price, coupon_rate, years, face_value=100, frequency=2):
    """
    Solve for yield-to-maturity numerically.
    """

    if years <= 0:
        return np.nan

    def objective(ytm):
        theoretical_price = bond_price_from_yield(
            face_value=face_value,
            coupon_rate=coupon_rate,
            years=years,
            ytm=ytm,
            frequency=frequency
        )

        return theoretical_price - price

    try:
        return brentq(
            objective,
            -0.05,
            1.00
        )

    except ValueError:
        return np.nan


def interpolate_treasury_yield(
    years,
    treasury_row
):
    """
    Estimate Treasury yield corresponding to
    a corporate bond's maturity.
    """

    maturities = np.array([
        2,
        5,
        10,
        30
    ])

    yields = np.array([
        treasury_row["2Y"],
        treasury_row["5Y"],
        treasury_row["10Y"],
        treasury_row["30Y"]
    ])

    return np.interp(
        years,
        maturities,
        yields
    )


def calculate_spread_bps(
    corporate_yield,
    treasury_yield
):
    """
    Yields should be percentages here.

    Example:
    corporate = 5.50
    treasury = 4.25

    spread = 125 bps
    """

    return (
        corporate_yield - treasury_yield
    ) * 100
    
def calculate_modified_duration(
    coupon_rate,
    ytm,
    years,
    face_value=100,
    frequency=2
):
    periods = max(round(years * frequency), 1)

    coupon_payment = (
        face_value * coupon_rate / frequency
    )

    rate = ytm / frequency

    weighted_pv = 0
    total_pv = 0

    for period in range(1, periods + 1):

        cash_flow = coupon_payment

        if period == periods:
            cash_flow += face_value

        pv = cash_flow / (
            (1 + rate) ** period
        )

        time_years = period / frequency

        weighted_pv += time_years * pv
        total_pv += pv

    macaulay_duration = (
        weighted_pv / total_pv
    )

    modified_duration = (
        macaulay_duration /
        (1 + rate)
    )

    return modified_duration


def calculate_dv01(
    price,
    modified_duration
):
    """
    DV01 per $100 face value.
    """

    return (
        modified_duration *
        price *
        0.0001
    )

def build_bond_analytics(
    bonds,
    prices,
    treasury
):
    latest_prices = (
        prices
        .sort_values("Date")
        .groupby("CUSIP")
        .tail(1)
    )

    df = bonds.merge(
        latest_prices,
        on="CUSIP",
        how="left"
    )

    latest_treasury = (
        treasury
        .sort_values("Date")
        .iloc[-1]
    )

    results = []

    for _, row in df.iterrows():

        years = years_to_maturity(
            row["Maturity"],
            row["Date"]
        )

        coupon_decimal = (
            row["Coupon"] / 100
        )

        ytm_decimal = calculate_ytm(
            price=row["Price"],
            coupon_rate=coupon_decimal,
            years=years
        )

        ytm_percent = (
            ytm_decimal * 100
            if pd.notna(ytm_decimal)
            else np.nan
        )

        treasury_yield = (
            interpolate_treasury_yield(
                years,
                latest_treasury
            )
        )

        spread_bps = (
            calculate_spread_bps(
                ytm_percent,
                treasury_yield
            )
            if pd.notna(ytm_percent)
            else np.nan
        )

        duration = (
            calculate_modified_duration(
                coupon_rate=coupon_decimal,
                ytm=ytm_decimal,
                years=years
            )
            if pd.notna(ytm_decimal)
            else np.nan
        )

        dv01 = (
            calculate_dv01(
                row["Price"],
                duration
            )
            if pd.notna(duration)
            else np.nan
        )

        results.append({
            "Date": row["Date"],
            "CUSIP": row["CUSIP"],
            "Issuer": row["Issuer"],
            "Price": row["Price"],
            "Years_To_Maturity": years,
            "Yield": ytm_percent,
            "Treasury_Yield": treasury_yield,
            "Spread_bps": spread_bps,
            "Duration": duration,
            "DV01": dv01
        })

    return pd.DataFrame(results)