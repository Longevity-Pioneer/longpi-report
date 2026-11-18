"""DNA methylation beta matrix -> Horvath 2013 and Hannum 2013 clocks (open coefficients); vendor clocks pass through.

Licence policy: DNAm PhenoAge, GrimAge, GrimAge2, DunedinPACE, Horvath skin&blood and DNAmTL are
commercially licensed. They are NEVER computed from raw beta values here; a vendor's result can be
passed through with --vendor-json (method "vendor", vendor_derived true).
"""
from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path

from . import common, tables

VERSION = "0.1.0"
MDIR = common.DATA_DIR / "methylation"
MAX_MISSING = 0.20  # refuse a clock when more than 20% of its CpGs are absent
EPIC_V2_SUFFIX = re.compile(r"^(cg\d{8})_[A-Z]{2}\d+$")
PROBE = re.compile(r"^(cg|ch\.|rs)\S*$")

# Clocks that must never be computed from raw data (vendor passthrough only).
RESTRICTED = {"dnam_phenoage", "phenoage", "grimage", "grimage2", "dunedinpace", "horvath_skinblood", "dnamtl"}
VENDOR_NAMES = RESTRICTED | {"horvath", "hannum"}


def add_arguments(p):
    p.add_argument("matrix", nargs="?", help="beta matrix (CSV/TSV, CpG IDs in the first column, one column per sample)")
    p.add_argument("--sample", default=None, help="column to use when the matrix has several samples")
    p.add_argument("--age", type=float, default=None, help="chronological age in years (needed for *_accel)")
    p.add_argument("--sex", choices=["M", "F"], default=None)
    p.add_argument("--specimen", default="whole_blood")
    p.add_argument("--vendor-json", default=None,
                   help='vendor clock results, e.g. {"vendor": "X lab", "clocks": {"grimage2": {"value": 50.2, "accel": 1.3}}}')


def anti_trafo(x: float, adult_age: float = 20.0) -> float:
    """Horvath 2013 inverse age transform F^-1."""
    if x < 0:
        return (1 + adult_age) * math.exp(x) - 1
    return (1 + adult_age) * x + adult_age


def load_coefs():
    clocks = {}
    with open(MDIR / "horvath2013_coef.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    intercept = [float(r["CoefficientTraining"]) for r in rows if r["CpGmarker"] == "(Intercept)"][0]
    clocks["horvath"] = {
        "tool": "meth_horvath2013", "intercept": intercept,
        "coef": {r["CpGmarker"]: float(r["CoefficientTraining"]) for r in rows if r["CpGmarker"] != "(Intercept)"},
        "impute": {r["CpGmarker"]: float(r["medianByCpG"]) for r in rows if r["CpGmarker"] != "(Intercept)"},
        "impute_source": "Horvath 2013 Additional file 3 medianByCpG (author's gold standard)",
        "transform": "horvath_anti_trafo",
        "ref": "Horvath S. Genome Biol 2013;14:R115",
    }
    with open(MDIR / "hannum2013_coef.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    clocks["hannum"] = {
        "tool": "meth_hannum2013", "intercept": 0.0,
        "coef": {r["CpGmarker"]: float(r["CoefficientTraining"]) for r in rows},
        "impute": {r["CpGmarker"]: float(r["median_sesame450k"]) for r in rows},
        "impute_source": "biolearn 0.9.1 sesame_450k_median (Hannum published no imputation reference)",
        "transform": "identity",
        "ref": "Hannum G et al. Mol Cell 2013;49:359-367",
    }
    return clocks


def load_accel_reference() -> dict:
    p = MDIR / "accel_reference.json"
    return common.load_json(p) if p.exists() else {}


def detect_platform(probe_ids: list[str]) -> dict:
    n = len(probe_ids)
    n_v2 = sum(1 for p in probe_ids if EPIC_V2_SUFFIX.match(p))
    if n_v2 > 0.5 * n:
        plat = "EPIC v2 (935K)"
    elif n >= 800_000:
        plat = "EPIC v1 (850K)"
    elif n >= 400_000:
        plat = "450K"
    elif n >= 20_000:
        plat = "27K or subset"
    else:
        plat = "subset (platform not identifiable from probe count)"
    return {"platform": plat, "n_probes": n, "n_epic_v2_suffixed": n_v2}


def read_beta(path: str, sample: str | None) -> tuple[dict, dict]:
    header, rows = tables.read_table(path)
    col = tables.pick_column(header, sample)
    raw: dict[str, list[float]] = {}
    ids = []
    for row in rows:
        pid = row[0]
        ids.append(pid)
        v = tables.num(row[col])
        m = EPIC_V2_SUFFIX.match(pid)
        key = m.group(1) if m else pid
        if v is not None:
            raw.setdefault(key, []).append(v)
        else:
            raw.setdefault(key, [])
    plat = detect_platform(ids)
    vals = [x for xs in raw.values() for x in xs]
    if not vals:
        raise ValueError("matrix contains no numeric values")
    lo, hi = min(vals), max(vals)
    scale = "beta"
    if lo < -0.001 or hi > 1.001:
        # M-values: beta = 2^M / (1 + 2^M)
        scale = "M-value (converted to beta)"
        raw = {k: [2 ** x / (1 + 2 ** x) for x in xs] for k, xs in raw.items()}
    # EPIC v2 replicate probes collapse to the cg ID by mean
    beta = {k: (sum(xs) / len(xs)) for k, xs in raw.items() if xs}
    plat["value_scale"] = scale
    plat["n_cpg_with_value"] = len(beta)
    return beta, plat


def compute_clock(clock: dict, beta: dict) -> dict:
    cpgs = sorted(clock["coef"])
    missing = [c for c in cpgs if c not in beta]
    frac = len(missing) / len(cpgs)
    out = {"n_cpg": len(cpgs), "n_missing": len(missing), "missing_fraction": common.r(frac, 4),
           "missing_cpgs": missing, "impute_source": clock["impute_source"]}
    if frac > MAX_MISSING:
        out["computed"] = False
        out["reason"] = f"missing fraction {frac:.3f} > {MAX_MISSING}"
        return out
    s = clock["intercept"]
    for c in cpgs:  # sorted order -> deterministic float sum
        b = beta[c] if c in beta else clock["impute"][c]
        s += clock["coef"][c] * b
    value = anti_trafo(s) if clock["transform"] == "horvath_anti_trafo" else s
    out["computed"] = True
    out["value"] = value
    return out


def run(args) -> dict:
    obs, prov, summary = [], [], []
    tool_ids = ["meth_horvath2013", "meth_hannum2013", "meth_vendor_passthrough"]
    ref = load_accel_reference()
    src = Path(args.matrix).name if args.matrix else None
    platform_info = None
    if args.matrix:
        beta, platform_info = read_beta(args.matrix, args.sample)
        summary.append(f"methylation: platform {platform_info['platform']}, {platform_info['n_cpg_with_value']} CpGs with values")
        for name, clock in load_coefs().items():
            res = compute_clock(clock, beta)
            step = {"step": f"methylation.{name}", "tool": clock["tool"], "version": VERSION,
                    "ref_data": {"coefficients": clock["ref"], "impute": clock["impute_source"],
                                 "accel_reference": ref.get(name, {}).get("dataset")},
                    "params": {"max_missing_fraction": MAX_MISSING},
                    "qc": {k: v for k, v in res.items() if k not in ("value",)} | {"platform": platform_info}}
            prov.append(step)
            if not res["computed"]:
                summary.append(f"  {name}: not computed ({res['reason']})")
                continue
            common_kw = dict(unit="years", tool=clock["tool"], platform=platform_info["platform"],
                             specimen=args.specimen, source_file=src, datetime=args.date)
            o = common.make_obs(f"LP:clock.{name}", common.r(res["value"], 3), **common_kw)
            o["missing_fraction"] = res["missing_fraction"]
            obs.append(o)
            msg = f"  {name}: {res['value']:.2f} y (missing {res['n_missing']}/{res['n_cpg']})"
            if args.age is not None and name in ref:
                a, b = ref[name]["intercept"], ref[name]["slope"]
                accel = res["value"] - (a + b * args.age)
                oa = common.make_obs(f"LP:clock.{name}_accel", common.r(accel, 3), **common_kw)
                oa["reference"] = ref[name]["dataset"]
                obs.append(oa)
                msg += f", accel {accel:+.2f} y"
            summary.append(msg)
    if args.vendor_json:
        v = common.load_json(Path(args.vendor_json))
        vendor = v.get("vendor")
        for name, rec in sorted((v.get("clocks") or {}).items()):
            key = name.lower()
            if key not in VENDOR_NAMES:
                raise ValueError(f"unknown vendor clock {name!r}; allowed: {sorted(VENDOR_NAMES)}")
            if key == "phenoage":
                key = "dnam_phenoage"
            kw = dict(method="vendor", vendor_derived=True, tool="meth_vendor_passthrough",
                      specimen=args.specimen, source_file=Path(args.vendor_json).name, datetime=args.date,
                      platform=vendor)
            unit = "years/year" if key == "dunedinpace" else "years"
            if rec.get("value") is not None:
                obs.append(common.make_obs(f"LP:clock.{key}", float(rec["value"]), unit=unit, **kw))
            if rec.get("accel") is not None:
                obs.append(common.make_obs(f"LP:clock.{key}_accel", float(rec["accel"]), unit=unit, **kw))
        prov.append({"step": "methylation.vendor", "tool": "meth_vendor_passthrough", "version": VERSION,
                     "ref_data": {"vendor": vendor}})
        summary.append(f"methylation: vendor clocks passed through: {sorted((v.get('clocks') or {}))}")
    if not args.matrix and not args.vendor_json:
        raise SystemExit("methylation: give a beta matrix and/or --vendor-json")
    return {"tool_ids": tool_ids, "observations": obs, "provenance": prov, "summary": summary}
