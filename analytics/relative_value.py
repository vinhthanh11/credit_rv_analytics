import pandas as pd
import numpy as np


# --------------------------------------------------
# Peer Median Relative Value
# --------------------------------------------------

def add_peer_relative_value(analytics_df, bonds_df):
    """
    Add peer-based and maturity-adjusted relative value.

    Peer group:
        Rating + Sector

    Positive residual:
        Wider than peers / fair curve -> potentially CHEAP

    Negative residual:
        Tighter than peers / fair curve -> potentially RICH
    """

    df = analytics_df.merge(
        bonds_df[
            [
                "CUSIP",
                "Rating",
                "Sector",
                "Maturity"
            ]
        ],
        on="CUSIP",
        how="left"
    )

    group_cols = [
        "Rating",
        "Sector"
    ]

    # --------------------------------------------------
    # Existing peer statistics
    # --------------------------------------------------

    df["Peer_Count"] = (
        df
        .groupby(group_cols)["CUSIP"]
        .transform("count")
    )

    df["Peer_Spread_Median_bps"] = (
        df
        .groupby(group_cols)["Spread_bps"]
        .transform("median")
    )

    df["Peer_Spread_Mean_bps"] = (
        df
        .groupby(group_cols)["Spread_bps"]
        .transform("mean")
    )

    df["Peer_Spread_Std_bps"] = (
        df
        .groupby(group_cols)["Spread_bps"]
        .transform("std")
    )

    # Existing median-based RV
    df["RV_Residual_bps"] = (
        df["Spread_bps"]
        - df["Peer_Spread_Median_bps"]
    )

    df["RV_ZScore"] = (
        (
            df["Spread_bps"]
            - df["Peer_Spread_Mean_bps"]
        )
        /
        df["Peer_Spread_Std_bps"]
    )

    df["RV_ZScore"] = (
        df["RV_ZScore"]
        .replace([np.inf, -np.inf], np.nan)
    )

    # --------------------------------------------------
    # NEW: Maturity-adjusted relative value
    # --------------------------------------------------

    df = add_maturity_adjusted_relative_value(
        df,
        group_cols=group_cols
    )

    # --------------------------------------------------
    # Signal based on maturity-adjusted RV
    # --------------------------------------------------

    df["RV_Signal"] = (
        df["Maturity_Adjusted_RV_bps"]
        .apply(classify_signal)
    )

    return df


# --------------------------------------------------
# Credit Curve
# --------------------------------------------------

def add_maturity_adjusted_relative_value(
    df,
    group_cols=None
):
    """
    Fit:

        Spread = alpha + beta * Years_To_Maturity

    separately for each Rating + Sector peer group.

    Then:

        Maturity_Adjusted_RV
            = Actual Spread - Fair Spread
    """

    if group_cols is None:
        group_cols = [
            "Rating",
            "Sector"
        ]

    result_groups = []

    for _, group in df.groupby(group_cols):

        group = group.copy()

        valid = group[
            [
                "Years_To_Maturity",
                "Spread_bps"
            ]
        ].dropna()

        # Need at least 2 different maturities
        if (
            len(valid) < 2
            or valid["Years_To_Maturity"].nunique() < 2
        ):
            group["Curve_Slope"] = np.nan
            group["Curve_Intercept"] = np.nan
            group["Fair_Spread_bps"] = (
                group["Peer_Spread_Median_bps"]
            )

        else:

            # Linear regression:
            # Spread = alpha + beta * maturity

            slope, intercept = np.polyfit(
                valid["Years_To_Maturity"],
                valid["Spread_bps"],
                1
            )

            group["Curve_Slope"] = slope
            group["Curve_Intercept"] = intercept

            group["Fair_Spread_bps"] = (
                intercept
                + slope
                * group["Years_To_Maturity"]
            )

        # Actual - Fair
        group["Maturity_Adjusted_RV_bps"] = (
            group["Spread_bps"]
            - group["Fair_Spread_bps"]
        )

        # Residual dispersion
        residual_std = (
            group["Maturity_Adjusted_RV_bps"]
            .std()
        )

        if (
            pd.isna(residual_std)
            or residual_std == 0
        ):
            group["Maturity_Adjusted_ZScore"] = np.nan

        else:
            group["Maturity_Adjusted_ZScore"] = (
                group["Maturity_Adjusted_RV_bps"]
                / residual_std
            )

        result_groups.append(group)

    return pd.concat(
        result_groups,
        ignore_index=True
    )


# --------------------------------------------------
# Signal Classification
# --------------------------------------------------

def classify_signal(residual):
    """
    Classify maturity-adjusted residual.
    """

    if pd.isna(residual):
        return "N/A"

    if residual >= 20:
        return "Strong Cheap"

    if residual >= 10:
        return "Cheap"

    if residual <= -20:
        return "Strong Rich"

    if residual <= -10:
        return "Rich"

    return "Fair"


# --------------------------------------------------
# Opportunity Ranking
# --------------------------------------------------

def rank_opportunities(df):
    """
    Rank by absolute maturity-adjusted RV.
    """

    ranked = df.copy()

    ranked["RV_Absolute_bps"] = (
        ranked[
            "Maturity_Adjusted_RV_bps"
        ].abs()
    )

    return ranked.sort_values(
        "RV_Absolute_bps",
        ascending=False
    )


# --------------------------------------------------
# Cheap Bonds
# --------------------------------------------------

def get_cheap_bonds(df):

    return (
        df[
            df["RV_Signal"].isin(
                [
                    "Cheap",
                    "Strong Cheap"
                ]
            )
        ]
        .sort_values(
            "Maturity_Adjusted_RV_bps",
            ascending=False
        )
    )


# --------------------------------------------------
# Rich Bonds
# --------------------------------------------------

def get_rich_bonds(df):

    return (
        df[
            df["RV_Signal"].isin(
                [
                    "Rich",
                    "Strong Rich"
                ]
            )
        ]
        .sort_values(
            "Maturity_Adjusted_RV_bps",
            ascending=True
        )
    )