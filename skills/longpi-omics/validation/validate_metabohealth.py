#!/usr/bin/env python3
"""Validate metab_metabohealth2019 against MiMIR 1.5 comp.mort_score on MiMIR's 500-sample synthetic set.

Step 1 (in R): Rscript validation/mimir_reference.R <MiMIR source> <dir>  -> mimir_synthetic_mortscore.csv
Step 2: LONGPI_OMICS_SLOW=1 python3 validate_metabohealth.py <dir>
Checks (a) our within-dataset implementation == MiMIR (numerical reproduction), and (b) reports how far
the single-sample BBMRI-NL reference scaling departs from within-dataset scaling on the same data.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import metabolomics  # noqa: E402


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def main(d: str) -> int:
    if os.environ.get("LONGPI_OMICS_SLOW") != "1":
        print("set LONGPI_OMICS_SLOW=1 to run")
        return 0
    ref = metabolomics.load_ref()
    keys = list(ref["markers"])
    rows, mimir = [], []
    with open(Path(d) / "mimir_synthetic_mortscore.csv") as fh:
        for r in csv.DictReader(fh):
            rows.append({k: (None if r[k] in ("NA", "") else float(r[k])) for k in keys})
            mimir.append(None if r["mortScore"] in ("NA", "") else float(r["mortScore"]))
    ours = metabolomics.metabohealth_dataset(rows, ref)
    pairs = [(a, b) for a, b in zip(ours, mimir) if a is not None and b is not None]
    na_agree = all((a is None) == (b is None) for a, b in zip(ours, mimir))
    diff = max(abs(a - b) for a, b in pairs)
    # single-sample reference scaling on the rows without zeros/NA
    refsc, dsc = [], []
    for r, b in zip(rows, mimir):
        if b is None or any(r[k] is None for k in keys):
            continue
        s, _ = metabolomics.metabohealth_reference(r, ref)
        if s is not None:
            refsc.append(s)
            dsc.append(b)
    mean_shift = sum(a - b for a, b in zip(refsc, dsc)) / len(refsc)
    out = {"tool_id": "metab_metabohealth2019", "version": metabolomics.VERSION,
           "dataset": "MiMIR 1.5 synthetic_metabolic_dataset (500 synthetic Nightingale profiles); reference = MiMIR comp.mort_score run in R",
           "metric": "max |within-dataset MetaboHealth ours - MiMIR|", "value": diff,
           "passed": diff < 1e-9 and na_agree, "date": "2026-11-18",
           "details": {"n_scored": len(pairs), "na_pattern_identical": na_agree,
                       "single_sample_reference_vs_within_dataset": {
                           "n": len(refsc), "pearson": pearson(refsc, dsc), "mean_shift": mean_shift,
                           "note": "the shipped single-sample path uses BBMRI-NL log mean/SD; agreement with within-dataset scaling is data dependent"}}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "metab_metabohealth2019.json").write_text(json.dumps(out, indent=1))
    print(out["metric"], diff, out["passed"], out["details"]["single_sample_reference_vs_within_dataset"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
