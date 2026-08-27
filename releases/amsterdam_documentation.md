# Maturity-Adjusted Relative Value

## Big Idea

The original relative-value model compared each bond against the **median spread of its Rating + Sector peer group**.

The problem is that a 3-year bond and a 10-year bond should not necessarily trade at the same spread.

The maturity-adjusted model instead asks:

> **Given this bond's maturity, where should it trade relative to its peer credit curve?**

---

## Logic

For each **Rating + Sector** peer group:

1. Take `Years_To_Maturity` and `Spread_bps`.
2. Fit a simple linear credit curve.
3. Estimate the bond's `Fair_Spread_bps` based on its maturity.
4. Compare the actual spread against the fair spread.
5. Calculate a maturity-adjusted Z-score.
6. Classify the bond as Cheap, Fair, or Rich.

The basic model is:

    Fair Spread = Intercept + Slope × Years to Maturity

Then:

    Maturity-Adjusted RV = Actual Spread - Fair Spread

A positive residual means the bond trades **wider than expected** and may be cheap.

A negative residual means the bond trades **tighter than expected** and may be rich.

---

## Example

Suppose a BBB+ Telecom bond trades at:

    Actual Spread:        170 bp
    Peer Median:          145 bp

Using the original peer-median model:

    Old RV = 170 - 145
           = +25 bp

    Signal: CHEAP

At first glance, the bond looks significantly cheap.

However, this bond has a longer maturity than most of its peers.

The fitted BBB+ Telecom credit curve estimates that a bond with this maturity should trade around:

    Fair Spread:          162 bp

The maturity-adjusted calculation becomes:

    Adjusted RV = 170 - 162
                = +8 bp

    Signal: FAIR

The apparent +25 bp opportunity has therefore fallen to only +8 bp after controlling for maturity.

---

## Why This Matters

### Old Model

    Is this bond wider than the median of its peers?

### New Model

    Is this bond wider than it SHOULD BE
    given where it sits on the credit curve?

This reduces false Cheap/Rich signals caused simply by differences in maturity.

---

## Functions Added

### `add_maturity_adjusted_relative_value()`

Fits a credit curve for each Rating + Sector peer group and calculates:

- `Curve_Slope`
- `Curve_Intercept`
- `Fair_Spread_bps`
- `Maturity_Adjusted_RV_bps`
- `Maturity_Adjusted_ZScore`

### `classify_signal()`

Converts the maturity-adjusted residual into a simple relative-value signal:

    >= +20 bp       Strong Cheap
    +10 to +20 bp   Cheap
    -10 to +10 bp   Fair
    -20 to -10 bp   Rich
    <= -20 bp       Strong Rich

### `rank_opportunities()`

Ranks bonds by the absolute size of their **maturity-adjusted relative-value residual** rather than the original peer-median residual.

---

## Model Evolution

    V1
    Rating + Sector
          ↓
    Peer Median Spread
          ↓
    Actual - Median
          ↓
    Cheap / Fair / Rich


    V2
    Rating + Sector
          ↓
    Fit Credit Curve
          ↓
    Adjust for Maturity
          ↓
    Fair Spread
          ↓
    Actual - Fair
          ↓
    Maturity-Adjusted RV
          ↓
    Cheap / Fair / Rich

The key improvement is moving from a **flat peer comparison** to a simple **credit-curve relative-value model**.