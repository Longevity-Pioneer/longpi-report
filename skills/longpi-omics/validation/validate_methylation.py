#!/usr/bin/env python3
"""Validate meth_horvath2013 / meth_hannum2013 against biolearn 0.9.1 (BSD) as reference implementation.

Real GEO data could not be fetched (network ~10 KB/s on 2026-11-18; GSE41169 is 193 MB), so the check
is implementation-level: 50 seeded pseudo-samples (beta = author median + N(0, 0.08), clipped to
[0.01, 0.99]) scored by our code and by biolearn's LinearMethylationModel with the same coefficient files.

usage: LONGPI_OMICS_SLOW=1 python3 validate_methylation.py <dir containing the biolearn package>
"""
from __future__ import annotations

import json
import math
import os
import random
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import methylation  # noqa: E402


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def main(bl_dir: str) -> int:
    if os.environ.get("LONGPI_OMICS_SLOW") != "1":
        print("set LONGPI_OMICS_SLOW=1 to run")
        return 0
    sys.path.insert(0, bl_dir)
    sys.modules.setdefault("cvxpy", types.ModuleType("cvxpy"))  # only needed by unrelated biolearn models
    import pandas as pd
    import biolearn
    from biolearn.model import model_definitions, LinearMethylationModel

    clocks = methylation.load_coefs()
    rng = random.Random(20261118)
    cpgs = sorted(set(clocks["horvath"]["coef"]) | set(clocks["hannum"]["coef"]))
    med = {}
    for c in cpgs:
        med[c] = clocks["horvath"]["impute"].get(c, clocks["hannum"]["impute"].get(c))
    samples = {}
    for i in range(50):
        samples[f"S{i:02d}"] = {c: min(0.99, max(0.01, med[c] + rng.gauss(0, 0.08))) for c in cpgs}
    df = pd.DataFrame(samples)

    class G:  # minimal GeoData stand-in
        dnam = df

    out = {}
    for name, bl_name in (("horvath", "Horvathv1"), ("hannum", "Hannum")):
        model = LinearMethylationModel.from_definition(model_definitions[bl_name])
        ref = model.predict(G)["Predicted"]
        ours = [methylation.compute_clock(clocks[name], samples[s])["value"] for s in df.columns]
        refv = [float(ref[s]) for s in df.columns]
        diffs = [abs(a - b) for a, b in zip(ours, refv)]
        out[name] = {"max_abs_diff": max(diffs), "pearson": pearson(ours, refv), "n": len(diffs)}
    # biolearn uses the rounded Horvath intercept 0.696 instead of the author's 0.695507258;
    # expected offset for adult ages = 21 * 0.000492742 = 0.01035 years.
    exp_off = 21 * (0.696 - clocks["horvath"]["intercept"])
    for name, tool in (("horvath", "meth_horvath2013"), ("hannum", "meth_hannum2013")):
        tol = 0.0105 if name == "horvath" else 1e-9
        res = {
            "tool_id": tool, "version": methylation.VERSION,
            "dataset": "50 seeded pseudo-samples on the clock CpGs (no real GEO data: bandwidth limit)",
            "metric": "max |ours - biolearn 0.9.1| (years)", "value": out[name]["max_abs_diff"],
            "passed": out[name]["max_abs_diff"] <= tol and out[name]["pearson"] > 0.999999,
            "date": "2026-11-18",
            "details": {"pearson_vs_reference": out[name]["pearson"], "n": out[name]["n"],
                        "reference_impl": f"biolearn {biolearn.__version__ if hasattr(biolearn, '__version__') else '0.9.1'} LinearMethylationModel",
                        "tolerance": tol,
                        "note": ("biolearn rounds the Horvath intercept to 0.696 (author: 0.695507258); "
                                 f"expected constant offset {exp_off:.5f} y for adult ages") if name == "horvath" else
                        "identical coefficients, no intercept",
                        "age_correlation": "not measured: no real public beta data could be downloaded (193 MB GEO series at ~10 KB/s)"},
        }
        (HERE / "results").mkdir(exist_ok=True)
        (HERE / "results" / f"{tool}.json").write_text(json.dumps(res, indent=1))
        print(tool, res["value"], res["details"]["pearson_vs_reference"], res["passed"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
