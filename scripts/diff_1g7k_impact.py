"""Diff before/after snapshots and highlight changes that affect manuscript text."""
import json
from pathlib import Path


def fmt(v):
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def diff(label, before, after):
    if before == after:
        return None
    return f"  {label}: {fmt(before)} -> {fmt(after)}"


def main():
    b = json.loads(Path("/tmp/1g7k_before.json").read_text())
    a = json.loads(Path("/tmp/1g7k_after.json").read_text())
    changes = []

    # Counts
    for k in ["color_counts_all", "color_counts_canonical"]:
        for color in set(list(b[k].keys()) + list(a[k].keys())):
            if b[k].get(color) != a[k].get(color):
                changes.append(f"{k}[{color}]: {b[k].get(color)} -> {a[k].get(color)}")

    # Per-color geometry (canonical)
    for color in ["green", "red"]:
        bc = b["per_color_geom_canonical"].get(color, {})
        ac = a["per_color_geom_canonical"].get(color, {})
        for key in set(list(bc.keys()) + list(ac.keys())):
            if key == "n":
                if bc.get(key) != ac.get(key):
                    changes.append(f"per_color[{color}].n: {bc.get(key)} -> {ac.get(key)}")
                continue
            if not isinstance(bc.get(key), dict):
                continue
            for stat in ["mean", "std", "median"]:
                bv = bc[key].get(stat)
                av = ac.get(key, {}).get(stat)
                if bv is None or av is None:
                    continue
                if abs(bv - av) > 1e-6:
                    delta = av - bv
                    pct = 100 * delta / bv if bv else 0
                    changes.append(f"per_color[{color}].{key}.{stat}: {bv:.4f} -> {av:.4f}  (Δ={delta:+.4f}, {pct:+.2f}%)")

    # Stokes
    for color in ["green", "red"]:
        bs = b["stokes_canonical"].get(color, {})
        as_ = a["stokes_canonical"].get(color, {})
        for stat in ["n", "mean", "std"]:
            bv = bs.get(stat)
            av = as_.get(stat)
            if bv != av:
                if isinstance(bv, (int, float)) and isinstance(av, (int, float)):
                    changes.append(f"stokes[{color}].{stat}: {bv:.4f} -> {av:.4f}")
                else:
                    changes.append(f"stokes[{color}].{stat}: {bv} -> {av}")

    # Red vs green tests
    for col, ba in b["red_vs_green_canonical"].items():
        aa = a["red_vs_green_canonical"].get(col, {})
        for stat in ["n_red", "n_green", "median_red", "median_green", "mean_red", "mean_green", "p"]:
            bv = ba.get(stat)
            av = aa.get(stat)
            if bv is None or av is None:
                continue
            if isinstance(bv, float):
                if abs(bv - av) > 1e-6:
                    changes.append(f"red_vs_green[{col}].{stat}: {bv:.4g} -> {av:.4g}")
            else:
                if bv != av:
                    changes.append(f"red_vs_green[{col}].{stat}: {bv} -> {av}")

    # Spearman with em_max
    for col, ba in b["em_max_spearman_canonical"].items():
        aa = a["em_max_spearman_canonical"].get(col, {})
        for stat in ["n", "rho", "p"]:
            bv = ba.get(stat)
            av = aa.get(stat)
            if bv is None or av is None:
                continue
            if isinstance(bv, float):
                if abs(bv - av) > 1e-5:
                    changes.append(f"em_max_spearman[{col}].{stat}: {bv:.4g} -> {av:.4g}")
            else:
                if bv != av:
                    changes.append(f"em_max_spearman[{col}].{stat}: {bv} -> {av}")

    # QY vs b_factor_ratio
    bq = b.get("qy_vs_bratio_canonical", {})
    aq = a.get("qy_vs_bratio_canonical", {})
    for stat in ["n", "rho", "p"]:
        bv = bq.get(stat)
        av = aq.get(stat)
        if bv is None or av is None:
            continue
        if isinstance(bv, float):
            if abs(bv - av) > 1e-5:
                changes.append(f"qy_vs_bratio.{stat}: {bv:.4g} -> {av:.4g}")
        else:
            if bv != av:
                changes.append(f"qy_vs_bratio.{stat}: {bv} -> {av}")

    if not changes:
        print("NO CHANGES")
    else:
        for c in sorted(changes):
            print(c)


if __name__ == "__main__":
    main()
