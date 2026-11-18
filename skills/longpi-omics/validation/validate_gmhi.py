#!/usr/bin/env python3
"""Validate micro_gmhi2020 against the authors' published GMHI_output.csv (Gupta 2020 example, 25 samples).

usage: LONGPI_OMICS_SLOW=1 python3 validate_gmhi.py <dir with species_relative_abundances.csv and GMHI_output.csv>
(both files from the authors' GMHI_2020 script repository; fetched once, not redistributed)
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import metagenome  # noqa: E402


def main(d: str) -> int:
    if os.environ.get("LONGPI_OMICS_SLOW") != "1":
        print("set LONGPI_OMICS_SLOW=1 to run")
        return 0
    d = Path(d)
    with open(d / "species_relative_abundances.csv", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    header, body = rows[0], rows[1:]
    with open(d / "GMHI_output.csv", encoding="utf-8") as fh:
        pub = {r[0]: float(r[1]) for r in list(csv.reader(fh))[1:]}
    ref = metagenome.load_gmhi()
    diffs, per = [], {}
    for j, s in enumerate(header[1:], 1):
        sp = {r[0]: float(r[j]) for r in body if float(r[j]) > 0}
        v = metagenome.gmhi(sp, ref)["gmhi"]
        diffs.append(abs(v - pub[s]))
        per[s] = {"ours": v, "published": pub[s]}
    out = {"tool_id": "micro_gmhi2020", "version": metagenome.VERSION,
           "dataset": "Gupta 2020 example profile (25 MetaPhlAn2 samples) and the authors' GMHI_output.csv",
           "metric": "max |GMHI ours - published|", "value": max(diffs), "passed": max(diffs) < 1e-9,
           "date": "2026-11-18", "details": {"n": len(diffs), "per_sample": per}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "micro_gmhi2020.json").write_text(json.dumps(out, indent=1))
    print(out["metric"], out["value"], out["passed"])
    # Shannon vs scipy.stats.entropy (independent reference implementation) on the same 25 profiles
    from scipy.stats import entropy
    import scipy
    sd = []
    for j, s in enumerate(header[1:], 1):
        sp = {r[0]: float(r[j]) for r in body if float(r[j]) > 0 and "unclassified" not in r[0]}
        sd.append(abs(metagenome.shannon(sp) - float(entropy(list(sp.values())))))
    out2 = {"tool_id": "micro_shannon", "version": metagenome.VERSION,
            "dataset": "Gupta 2020 example profile (25 MetaPhlAn2 samples)",
            "metric": "max |Shannon ours - scipy.stats.entropy| (nats)", "value": max(sd), "passed": max(sd) < 1e-12,
            "date": "2026-11-18", "details": {"n": len(sd), "reference_impl": "scipy " + scipy.__version__}}
    (HERE / "results" / "micro_shannon.json").write_text(json.dumps(out2, indent=1))
    print(out2["metric"], out2["value"], out2["passed"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
