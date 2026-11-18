#!/usr/bin/env python3
"""Validate prot_organage2023 against the authors' organage package on their 200-sample example data.

usage: LONGPI_OMICS_SLOW=1 python3 validate_organage.py <organage-main checkout>
Writes validation/results/prot_organage2023.json.
(The organage package itself unpickles its models; it is run here only as the reference implementation.)
"""
from __future__ import annotations

import io
import json
import math
import os
import re
import sys
import warnings
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import proteomics  # noqa: E402


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def notebook_values(nb_path: Path):
    """Rows printed in the authors' example notebook (first organ block of `res`)."""
    nb = json.load(open(nb_path))
    for c in nb["cells"]:
        if "estimate_organ_ages()" in "".join(c.get("source", [])):
            for o in c.get("outputs", []):
                txt = "".join(o.get("data", {}).get("text/plain", []))
                rows = re.findall(r"^(\d+)\s+(\d+)\s+([01])\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)", txt, re.M)
                if rows:
                    # the first five printed rows belong to the first organ block (Adipose)
                    return [(int(r[0]), float(r[3]), float(r[5])) for r in rows[:5]]
    return []


def main(src: str):
    if os.environ.get("LONGPI_OMICS_SLOW") != "1":
        print("set LONGPI_OMICS_SLOW=1 to run")
        return 0
    src = Path(src)
    sys.path.insert(0, str(src / "src"))
    import types
    import pandas as pd
    pkg = types.ModuleType("organage")  # bypass the package __init__ (needs installed metadata)
    pkg.__path__ = [str(src / "src" / "organage")]
    sys.modules["organage"] = pkg
    from organage import OrganAge

    md = pd.read_csv(src / "tests" / "md_hot.csv").set_index("ID")
    dp = pd.read_csv(src / "tests" / "df_prot.csv").set_index("ID")
    with warnings.catch_warnings(), redirect_stdout(io.StringIO()):
        warnings.simplefilter("ignore")
        ref = OrganAge.CreateOrganAgeObject()
        ref.add_data(md, dp)
        ref.normalize(assay_version="v4.1")
        res = ref.estimate_organ_ages()
    oa = proteomics.load_organage()
    diffs_pred, diffs_gap, a_all, b_all = [], [], [], []
    per_organ = {}
    for organ in sorted(oa["organs"]):
        model = oa["organs"][organ]
        sub = res[res.Organ == organ]
        dmax = 0.0
        for sid, row in sub.iterrows():
            logv = {k: math.log10(v) for k, v in dp.loc[sid].items() if v > 0}
            pred, missing = proteomics.organ_age(model, logv, int(md.loc[sid, "Sex_F"]))
            assert not missing
            yhat = proteomics.interp_linear_extrapolate(model["lowess"]["x"], model["lowess"]["y"], float(md.loc[sid, "Age"]))
            gap = pred - yhat
            diffs_pred.append(abs(pred - row.Predicted_Age))
            diffs_gap.append(abs(gap - row.AgeGap))
            dmax = max(dmax, abs(gap - row.AgeGap))
            a_all.append(gap)
            b_all.append(row.AgeGap)
        per_organ[organ] = {"n": int(len(sub)), "max_abs_diff_gap": dmax}
    nbv = notebook_values(src / "docs" / "Predict organage example.ipynb")
    nb_check = []
    first = res.Organ.iloc[0]
    for sid, pred_pub, gap_pub in nbv:
        model = oa["organs"][first]
        logv = {k: math.log10(v) for k, v in dp.loc[sid].items() if v > 0}
        pred, _ = proteomics.organ_age(model, logv, int(md.loc[sid, "Sex_F"]))
        yhat = proteomics.interp_linear_extrapolate(model["lowess"]["x"], model["lowess"]["y"], float(md.loc[sid, "Age"]))
        nb_check.append({"id": sid, "organ": first, "published_pred": pred_pub, "ours_pred": round(pred, 6),
                         "published_gap": gap_pub, "ours_gap": round(pred - yhat, 6)})
    nb_max = max((abs(x["ours_gap"] - x["published_gap"]) for x in nb_check), default=None)
    out = {
        "tool_id": "prot_organage2023", "version": proteomics.VERSION,
        "dataset": "organage example data (tests/df_prot.csv, 200 samples x SomaScan v4.1) and the notebook's printed outputs",
        "metric": "max |age gap ours - organage package| over 13 models x 200 samples (years)",
        "value": max(diffs_gap), "passed": max(diffs_gap) < 1e-6 and (nb_max is None or nb_max < 1e-5),
        "date": "2026-11-18",
        "details": {"max_abs_diff_predicted_age": max(diffs_pred), "pearson_gap": pearson(a_all, b_all),
                    "n_comparisons": len(diffs_gap), "per_organ": per_organ,
                    "notebook_rows_checked": len(nb_check), "notebook_max_abs_diff_gap": nb_max,
                    "notebook_rows": nb_check,
                    "reference_impl": "organage main (MIT), sklearn " + __import__("sklearn").__version__},
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "prot_organage2023.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("metric", "value", "passed")}), out["details"]["notebook_max_abs_diff_gap"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
