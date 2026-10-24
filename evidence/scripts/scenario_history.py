#!/usr/bin/env python3
"""Historical pace of mortality improvement, as an empirical basis for the scenario weights.

Usage: scenario_history.py <derived_dir> <results_dir>

For each country/area with complete death registration (WPP 2024 estimates), sex and
20-year window ending by 2019 (pre-COVID), compute the average annual rate of decline
of single-age death rates at ages 60-89 and 90-99 (mean over single ages of the log change).
Also China (WPP 2000-2019 estimates and 2026-2100 medium projection) for comparison.
"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

derived, results = Path(sys.argv[1]), Path(sys.argv[2])
hq = pd.read_csv(derived / "wpp2024_hq_countries_mx.csv")
cn = pd.read_csv(derived / "wpp2024_china_mx.csv")

def rate(df, y0, y1, a0, a1):
    a = df[(df.year == y0) & df.age.between(a0, a1)].set_index("age").mx
    b = df[(df.year == y1) & df.age.between(a0, a1)].set_index("age").mx
    j = a.index.intersection(b.index)
    return float(-(np.log(b[j]) - np.log(a[j])).mean() / (y1 - y0))

rows = []
for (loc, name, sex), g in hq.groupby(["loc_id", "location", "sex"]):
    for y0 in range(1970, 2000):
        y1 = y0 + 20
        rows.append({"loc": name, "sex": sex, "y0": y0, "y1": y1,
                     "r60_89": rate(g, y0, y1, 60, 89), "r90_99": rate(g, y0, y1, 90, 99)})
h = pd.DataFrame(rows)
def share(x, lo, hi): return float(((x >= lo) & (x < hi)).mean())
out = {"windows": int(len(h)), "countries": int(h["loc"].nunique()),
       "r60_89": {"median": float(h.r60_89.median()), "p10": float(h.r60_89.quantile(.1)), "p90": float(h.r60_89.quantile(.9)),
                  "share_lt_0.5pct": share(h.r60_89, -1, 0.005), "share_0.5_2.5pct": share(h.r60_89, 0.005, 0.025),
                  "share_ge_2.5pct": share(h.r60_89, 0.025, 1)},
       "r90_99": {"median": float(h.r90_99.median()), "p10": float(h.r90_99.quantile(.1)), "p90": float(h.r90_99.quantile(.9)),
                  "share_lt_0.5pct": share(h.r90_99, -1, 0.005), "share_0.5_2.5pct": share(h.r90_99, 0.005, 2.5),
                  "share_ge_2.5pct": share(h.r90_99, 0.025, 1)}}
# most recent windows only (1999-2019)
rec = h[h.y0 == 1999]
out["recent_1999_2019"] = {"r60_89_median": float(rec.r60_89.median()), "r90_99_median": float(rec.r90_99.median()),
                           "by_country": rec.groupby("loc").r60_89.mean().round(4).to_dict()}
china = {}
for sex in ("M", "F"):
    g = cn[cn.sex == sex]
    china[sex] = {"2000_2019_r60_89": rate(g, 2000, 2019, 60, 89), "2000_2019_r90_99": rate(g, 2000, 2019, 90, 99),
                  "2026_2050_r60_89": rate(g, 2026, 2050, 60, 89), "2026_2050_r90_99": rate(g, 2026, 2050, 90, 99),
                  "2050_2100_r60_89": rate(g, 2050, 2100, 60, 89), "2050_2100_r90_99": rate(g, 2050, 2100, 90, 99)}
out["china"] = china
h.to_csv(results / "scenario_history_windows.csv", index=False)
(results / "scenario_history.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({k: v for k, v in out.items() if k != "recent_1999_2019"}, indent=1, ensure_ascii=False))
print("recent medians", out["recent_1999_2019"]["r60_89_median"], out["recent_1999_2019"]["r90_99_median"])
