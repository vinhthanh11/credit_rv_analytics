import pandas as pd
import numpy as np


def add_peer_relative_value(analytics_df, bonds_df):
    """
    Add peer-based relative value metrics.

    Peer group:
        Rating + Sector

    Positive RV residual:
        Bond trades wider than peer median -> potentially CHEAP

    Negative RV residual:
        Bond trades tighter than peer median -> potentially RICH
    """

    # Add bond reference information
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

    # --------------------------------------------------
    # Peer group statistics
    # --------------------------------------------------

    group_cols = [
        "Rating",
        "Sector"
    ]

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

    # --------------------------------------------------
    # Relative value residual
    # --------------------------------------------------

    df["RV_Residual_bps"] = (
        df["Spread_bps"]
        - df["Peer_Spread_Median_bps"]
    )

    # --------------------------------------------------
    # Z-score
    # --------------------------------------------------

    df["RV_ZScore"] = (
        (
            df["Spread_bps"]
            - df["Peer_Spread_Mean_bps"]
        )
        /
        df["Peer_Spread_Std_bps"]
    )

    # Avoid divide-by-zero / missing std
    df["RV_ZScore"] = (
        df["RV_ZScore"]
        .replace([np.inf, -np.inf], np.nan)
    )

    # --------------------------------------------------
    # Signal
    # --------------------------------------------------

    def classify_signal(row):

        residual = row["RV_Residual_bps"]
        zscore = row["RV_ZScore"]

        if pd.isna(residual):
            return "N/A"

        # Stronger signal
        if (
            residual >= 25
            and (
                pd.isna(zscore)
                or zscore >= 1.0
            )
        ):
            return "Strong Cheap"

        if (
            residual <= -25
            and (
                pd.isna(zscore)
                or zscore <= -1.0
            )
        ):
            return "Strong Rich"

        # Normal signal
        if residual >= 15:
            return "Cheap"

        if residual <= -15:
            return "Rich"

        return "Fair"

    df["RV_Signal"] = (
        df.apply(
            classify_signal,
            axis=1
        )
    )

    return df


def rank_opportunities(df):
    """
    Rank bonds by absolute relative-value dislocation.

    Larger absolute residual means a larger deviation
    from the peer median.
    """

    ranked = df.copy()

    ranked["RV_Absolute_bps"] = (
        ranked["RV_Residual_bps"].abs()
    )

    ranked = ranked.sort_values(
        "RV_Absolute_bps",
        ascending=False
    )

    return ranked


def get_cheap_bonds(df):
    """
    Return bonds trading wider than peers.
    """

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
            "RV_Residual_bps",
            ascending=False
        )
    )


def get_rich_bonds(df):
    """
    Return bonds trading tighter than peers.
    """

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
            "RV_Residual_bps",
            ascending=True
        )
    )