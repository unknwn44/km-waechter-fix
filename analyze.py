# analyze.py
# Key finding: km_since_service (r=0.40), avg_daily_km (r=0.25), and load_factor (r=0.22)
# separate cars that broke down from those that did not. Total mileage and age do not (r≈0.00).

import pandas as pd


def load_and_validate(path: str = "fleet_history.csv") -> pd.DataFrame:
    """Load the fleet history CSV and verify the expected columns are present."""
    df = pd.read_csv(path)
    required = {"car_id", "odometer_km", "km_since_service", "avg_daily_km",
                "load_factor", "age_years", "broke_down"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {missing}")
    return df


def compare_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each numeric feature, compute the group means (broke vs did-not) and their
    Pearson correlation with broke_down. Returns a summary DataFrame, sorted by |corr|.
    """
    features = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
    broke = df[df["broke_down"] == 1]
    ok    = df[df["broke_down"] == 0]

    rows = []
    for col in features:
        bm   = broke[col].mean()
        om   = ok[col].mean()
        corr = df[col].corr(df["broke_down"])
        rows.append({
            "feature":        col,
            "mean_broke_down": round(bm, 2),
            "mean_ok":         round(om, 2),
            "difference_pct":  round((bm - om) / om * 100, 1) if om != 0 else 0.0,
            "correlation":     round(corr, 3),
        })

    summary = pd.DataFrame(rows).sort_values("correlation", ascending=False, key=abs)
    return summary


def build_risk_scores(df: pd.DataFrame, signal_cols: list[str]) -> pd.DataFrame:
    """
    Min-max scale each signal column to [0, 1], average the scaled values,
    then multiply by 100 to produce a 0–100 risk score. Higher = riskier.

    Only columns that genuinely separate the two groups are included (signal_cols).
    """
    scored = df[["car_id", "broke_down"]].copy()

    scaled_parts = []
    for col in signal_cols:
        lo, hi = df[col].min(), df[col].max()
        scaled = (df[col] - lo) / (hi - lo) if hi > lo else pd.Series(0.0, index=df.index)
        scaled_parts.append(scaled)

    # Average the scaled signals and scale to 0–100
    scored["risk_score"] = round(sum(scaled_parts) / len(scaled_parts) * 100, 1)
    return scored.sort_values("risk_score", ascending=False).reset_index(drop=True)


def main() -> None:
    df = load_and_validate()

    # ------------------------------------------------------------------ #
    # Step 1 — Compare the two groups column by column                    #
    # ------------------------------------------------------------------ #
    print("=" * 65)
    print("GROUP COMPARISON  (broke_down=1 vs broke_down=0)")
    print(f"Fleet: {len(df)} cars  |  Broke down: {df['broke_down'].sum()}")
    print("=" * 65)
    summary = compare_groups(df)
    print(summary.to_string(index=False))
    print()

    # ------------------------------------------------------------------ #
    # Step 2 — Decide which columns to use in the score                   #
    # ------------------------------------------------------------------ #
    # Threshold: |correlation| > 0.15 and |difference_pct| > 10 %
    # odometer_km and age_years both fall well below both bars.
    SIGNAL_COLS = ["km_since_service", "avg_daily_km", "load_factor"]

    print("Columns used for risk score:", SIGNAL_COLS)
    print("Columns excluded (no signal): odometer_km, age_years")
    print()

    # ------------------------------------------------------------------ #
    # Step 3 — Build and rank risk scores                                  #
    # ------------------------------------------------------------------ #
    scored = build_risk_scores(df, SIGNAL_COLS)

    print("=" * 65)
    print("TOP 10 HIGHEST-RISK CARS")
    print("=" * 65)
    top10 = scored.head(10)[["car_id", "risk_score", "broke_down"]]
    top10 = top10.rename(columns={"broke_down": "actually_broke"})
    print(top10.to_string(index=False))
    print()

    # ------------------------------------------------------------------ #
    # Step 4 — Validation: do high-risk cars actually break down more?     #
    # ------------------------------------------------------------------ #
    top_half    = scored.head(60)
    bottom_half = scored.tail(60)
    top_rate    = top_half["broke_down"].mean() * 100
    bottom_rate = bottom_half["broke_down"].mean() * 100
    print(f"Breakdown rate in top-risk half:    {top_rate:.1f}%")
    print(f"Breakdown rate in bottom-risk half: {bottom_rate:.1f}%")
    print()
    print("Cars flagged by the 80% km rule today but NOT in the top-10 risk list:")
    KM_WARN = 15000 * 0.80
    rule_flagged = df[df["km_since_service"] >= KM_WARN]["car_id"].tolist()
    top10_ids    = scored.head(10)["car_id"].tolist()
    only_rule    = [c for c in rule_flagged if c not in top10_ids]
    print(" ", only_rule if only_rule else "none")
    print()
    print("Cars in the top-10 risk list that the 80% rule has NOT yet flagged:")
    early_warn = [c for c in top10_ids if c not in rule_flagged]
    print(" ", early_warn if early_warn else "none")


if __name__ == "__main__":
    main()
