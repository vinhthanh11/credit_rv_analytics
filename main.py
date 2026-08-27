import argparse

from data.bonds import load_bonds
from data.prices import load_prices
from data.treasury import load_treasury

from analytics.bond_math import build_bond_analytics

from analytics.relative_value import (
    add_peer_relative_value,
    rank_opportunities,
    get_cheap_bonds,
    get_rich_bonds
)


def main():

    parser = argparse.ArgumentParser(
        description="Credit Relative Value Analytics"
    )

    parser.add_argument(
        "--command",
        choices=[
            "data",
            "analytics",
            "rv"
        ],
        default="rv"
    )

    args = parser.parse_args()

    # ------------------------------------------
    # Load data
    # ------------------------------------------

    bonds = load_bonds("Bonds")
    prices = load_prices("Daily_Prices")
    treasury = load_treasury("Treasury")

    # ------------------------------------------
    # DATA CHECK
    # ------------------------------------------

    if args.command == "data":

        print("\nBONDS")
        print(bonds.head())

        print("\nPRICES")
        print(prices.head())

        print("\nTREASURY")
        print(treasury.head())

        return

    # ------------------------------------------
    # Bond analytics
    # ------------------------------------------

    analytics = build_bond_analytics(
        bonds,
        prices,
        treasury
    )

    if args.command == "analytics":

        print("\nBOND ANALYTICS")

        print(
            analytics[
                [
                    "Issuer",
                    "Price",
                    "Yield",
                    "Treasury_Yield",
                    "Spread_bps",
                    "Duration",
                    "DV01"
                ]
            ]
            .round(2)
            .to_string(index=False)
        )

        return

    # ------------------------------------------
    # Relative Value
    # ------------------------------------------

    rv = add_peer_relative_value(
        analytics,
        bonds
    )

    ranked = rank_opportunities(rv)

    print("\nRELATIVE VALUE")

    print(
        ranked[
            [
                "Issuer",
                "Rating",
                "Sector",
                "Spread_bps",
                "Peer_Spread_Median_bps",
                "RV_Residual_bps",
                "RV_ZScore",
                "RV_Signal"
            ]
        ]
        .round(2)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()