"""Compute color-class-dependent statistics for the manuscript before/after
the 1G7K (DsRed) re-assignment from green→red.

Snapshots are written to /tmp/1g7k_{before,after}.json so we can diff exactly
which reported manuscript numbers shift.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

CSV = Path("data/merged_complete_data.csv")
GEOM_COLS = ["minor_axis", "major_axis", "eccentricity", "circularity",
             "barrel_length", "b_factor_ratio", "chrom_contacts"]


def stat_block(df, label):
    out = {"label": label, "n_total": int(len(df))}
    out["color_counts_all"] = df["color_class"].value_counts(dropna=False).to_dict()
    canon = df[df["canonical_cohort"] == True]
    out["color_counts_canonical"] = canon["color_class"].value_counts(dropna=False).to_dict()
    # Per-color geometry means (canonical cohort only — that's what the manuscript reports)
    per_color = {}
    for color in ["green", "red", "yellow", "cyan", "orange", "blue"]:
        sub = canon[canon["color_class"] == color]
        per_color[color] = {"n": int(len(sub))}
        for col in GEOM_COLS:
            vals = sub[col].dropna()
            if len(vals) > 0:
                per_color[color][col] = {
                    "n": int(len(vals)),
                    "mean": float(vals.mean()),
                    "std": float(vals.std()),
                    "median": float(vals.median()),
                }
    out["per_color_geom_canonical"] = per_color

    # Stokes shifts per color (manuscript line 889-891)
    stokes = {}
    for color in ["green", "red", "yellow", "cyan", "orange", "blue"]:
        vals = canon[canon["color_class"] == color]["stokes_shift"].dropna()
        if len(vals) > 0:
            stokes[color] = {"n": int(len(vals)), "mean": float(vals.mean()), "std": float(vals.std())}
    out["stokes_canonical"] = stokes

    # Red vs green Mann-Whitney for the canonical cohort
    rg = {}
    red = canon[canon["color_class"] == "red"]
    green = canon[canon["color_class"] == "green"]
    for col in GEOM_COLS:
        r = red[col].dropna()
        g = green[col].dropna()
        if len(r) >= 5 and len(g) >= 5:
            u, p = stats.mannwhitneyu(r, g, alternative="two-sided")
            rg[col] = {"n_red": int(len(r)), "n_green": int(len(g)),
                       "median_red": float(r.median()), "median_green": float(g.median()),
                       "mean_red": float(r.mean()), "mean_green": float(g.mean()),
                       "U": float(u), "p": float(p)}
    out["red_vs_green_canonical"] = rg

    # em_max ↔ geometry Spearman (canonical cohort)
    spearman = {}
    sub = canon.dropna(subset=["em_max"])
    for col in GEOM_COLS + ["convex_area"]:
        s = sub.dropna(subset=[col])
        if len(s) >= 10:
            rho, p = stats.spearmanr(s["em_max"], s[col])
            spearman[col] = {"n": int(len(s)), "rho": float(rho), "p": float(p)}
    out["em_max_spearman_canonical"] = spearman

    # b_factor_ratio ↔ lit_qy (manuscript ρ ≈ −0.446 reported)
    sub = canon.dropna(subset=["b_factor_ratio", "lit_qy"])
    if len(sub) >= 10:
        rho, p = stats.spearmanr(sub["b_factor_ratio"], sub["lit_qy"])
        out["qy_vs_bratio_canonical"] = {"n": int(len(sub)), "rho": float(rho), "p": float(p)}

    return out


def main():
    mode = sys.argv[1]  # 'before' or 'after'
    df = pd.read_csv(CSV)
    snap = stat_block(df, mode)
    out_path = Path(f"/tmp/1g7k_{mode}.json")
    out_path.write_text(json.dumps(snap, indent=2, default=str))
    print(f"wrote {out_path}")
    print(f"red count (canonical): {snap['color_counts_canonical'].get('red')}")
    print(f"green count (canonical): {snap['color_counts_canonical'].get('green')}")


if __name__ == "__main__":
    main()
