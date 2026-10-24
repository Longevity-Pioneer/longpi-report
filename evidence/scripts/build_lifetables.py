#!/usr/bin/env python3
"""Extract single-age life tables from UN World Population Prospects 2024.

Inputs (from fetch_public_data.sh):
  <raw>/wpp2024/WPP2024_Life_Table_Complete_Medium_{Male,Female}_{1950-2023,2024-2100}.csv.gz

Outputs:
  <derived>/wpp2024_china_mx.csv        China (LocID 156), both sexes, 1950-2100, ages 0-100+
  <derived>/wpp2024_hq_countries_mx.csv  countries with high-quality death registration, 1950-2023
  <skill_data>/lifetable_china_wpp2024.json  compact table the LongPi engine reads (2000-2100)

Licence of the source data: CC BY 3.0 IGO (United Nations, DESA, Population Division).
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
from collections import defaultdict
from pathlib import Path

CHINA = 156
# Countries/areas whose WPP mortality estimates rest on complete vital registration
# (all are Human Mortality Database members); used for the history of mortality improvement.
HQ = {
    36: "Australia", 40: "Austria", 56: "Belgium", 124: "Canada", 203: "Czechia", 208: "Denmark",
    246: "Finland", 250: "France", 276: "Germany", 344: "China, Hong Kong SAR", 348: "Hungary",
    352: "Iceland", 372: "Ireland", 380: "Italy", 392: "Japan", 410: "Republic of Korea",
    528: "Netherlands", 554: "New Zealand", 578: "Norway", 616: "Poland", 620: "Portugal",
    724: "Spain", 752: "Sweden", 756: "Switzerland", 826: "United Kingdom", 840: "United States of America",
    158: "China, Taiwan Province of China", 702: "Singapore",
}


def rows(path: Path):
    with gzip.open(path, "rt", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            yield r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", type=Path)
    ap.add_argument("derived", type=Path)
    ap.add_argument("skill_data", type=Path)
    a = ap.parse_args()
    a.derived.mkdir(parents=True, exist_ok=True)
    a.skill_data.mkdir(parents=True, exist_ok=True)

    china = []  # (sex, year, age, mx, qx, lx, ex, ax)
    hq = []
    for sex in ("Male", "Female"):
        for span in ("1950-2023", "2024-2100"):
            f = a.raw / "wpp2024" / f"WPP2024_Life_Table_Complete_Medium_{sex}_{span}.csv.gz"
            if not f.exists():
                print(f"missing {f.name}; skipped")
                continue
            n = 0
            for r in rows(f):
                loc = int(r["LocID"])
                if loc != CHINA and (loc not in HQ or span != "1950-2023"):
                    continue
                rec = (sex[0], int(r["Time"]), int(r["AgeGrpStart"]), float(r["mx"]), float(r["qx"]),
                       float(r["lx"]), float(r["ex"]), float(r["ax"]))
                if loc == CHINA:
                    china.append(rec)
                else:
                    hq.append((loc, HQ[loc]) + rec)
                n += 1
            print(f"{f.name}: kept {n} rows")

    with open(a.derived / "wpp2024_china_mx.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sex", "year", "age", "mx", "qx", "lx", "ex", "ax"])
        w.writerows(sorted(china))
    with open(a.derived / "wpp2024_hq_countries_mx.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["loc_id", "location", "sex", "year", "age", "mx", "qx", "lx", "ex", "ax"])
        w.writerows(sorted(hq))

    # Compact engine table: mx by sex, year (2000-2100), age 0..100 (100 = open interval 100+).
    table: dict = {"M": defaultdict(dict), "F": defaultdict(dict)}
    e0: dict = {"M": {}, "F": {}}
    for sex, year, age, mx, qx, lx, ex, ax in china:
        if year < 2000:
            continue
        table[sex][year][age] = mx
        if age == 0:
            e0[sex][year] = ex
    years = sorted(set(table["M"]) & set(table["F"]))  # both sexes present
    table = {s: {y: table[s][y] for y in years} for s in table}
    out = {
        "source": "United Nations, Department of Economic and Social Affairs, Population Division (2024). "
                  "World Population Prospects 2024, complete life tables, medium variant "
                  "(estimates 1950-2023, projections 2024-2100). LocID 156 (China).",
        "url": "https://population.un.org/wpp/",
        "licence": "CC BY 3.0 IGO",
        "quantity": "mx: central death rate by single year of age; age 100 is the open interval 100+",
        "years": years,
        "e0": {s: {str(y): round(v, 3) for y, v in sorted(e0[s].items())} for s in e0},
        "mx": {s: {str(y): [round(table[s][y][x], 7) for x in range(101)] for y in sorted(table[s])} for s in table},
    }
    (a.skill_data / "lifetable_china_wpp2024.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("china rows", len(china), "hq rows", len(hq))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
