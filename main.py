import argparse

from ggsheet import get_records
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
        description="Credit Data Check"
    )

    parser.add_argument("--command", choices=["data"])
    args = parser.parse_args()

    if args.command == "data":
        # Load data from Bonds, Daily Prices, Treasury Sheets with appropriate format
        print(load_bonds("Bonds").head(5))
        print(load_prices("Daily_Prices").head(5))
        print(load_treasury("Treasury").head(5))
        return


    bonds = load_bonds("Bonds")
    prices = load_prices("Daily_Prices")
    treasury = load_treasury("Treasury")

    # ------------------------------------------
    # Bond analytics
    # ------------------------------------------

    analytics = build_bond_analytics(
        bonds,
        prices,
        treasury
    )

    # ------------------------------------------
    # Relative value
    # ------------------------------------------

    rv = add_peer_relative_value(
        analytics,
        bonds
    )

    ranked = rank_opportunities(rv)

    print("\nRELATIVE VALUE ANALYTICS")

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

    # ------------------------------------------
    # Cheap opportunities
    # ------------------------------------------

    cheap = get_cheap_bonds(rv)

    print("\nCHEAP BONDS")

    if cheap.empty:

        print("No cheap bonds found.")

    else:

        print(
            cheap[
                [
                    "Issuer",
                    "Rating",
                    "Sector",
                    "Spread_bps",
                    "RV_Residual_bps",
                    "RV_ZScore",
                    "RV_Signal"
                ]
            ]
            .round(2)
            .to_string(index=False)
        )

    # ------------------------------------------
    # Rich opportunities
    # ------------------------------------------

    rich = get_rich_bonds(rv)

    print("\nRICH BONDS")

    if rich.empty:

        print("No rich bonds found.")

    else:

        print(
            rich[
                [
                    "Issuer",
                    "Rating",
                    "Sector",
                    "Spread_bps",
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