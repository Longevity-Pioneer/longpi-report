"""Nightingale NMR metabolomics table -> MetaboHealth (Deelen 2019) mortality score.

Single-sample scoring replaces Deelen's within-cohort standardisation with BBMRI-NL reference log
means/SDs (see data/metabolomics/metabohealth_deelen2019.json). `metabohealth_dataset()` reproduces the
original within-dataset procedure and is used for validation against MiMIR.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

from . import common, tables

VERSION = "0.1.0"
NIGHTINGALE_HINTS = {"xxl_vldl_p", "xxl_vldl_l", "glyca", "gp", "alb", "albumin", "leu", "s_hdl_l", "vldl_d",
                     "pufa_fa", "pufa_pct", "acace", "glc", "glucose", "his", "ldl_c", "apob", "apoa1"}
# simple unit conversions into the reference units
TO_MMOL = {("glc", "mg/dl"): 1 / 18.016, ("lac", "mg/dl"): 1 / 9.008}


def add_arguments(p):
    p.add_argument("table", help="Nightingale results (samples in rows, biomarkers in columns; or transposed)")
    p.add_argument("--sample", default=None, help="row/column to use when several samples are present")
    p.add_argument("--specimen", default="plasma")
    p.add_argument("--non-fasting", action="store_true", help="sample was non-fasting (flag)")


def load_ref() -> dict:
    return common.load_json(common.DATA_DIR / "metabolomics" / "metabohealth_deelen2019.json")


def _canon(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"\s*\(.*\)$", "", s)  # drop "(mmol/l)" suffix
    return s.replace("-", "_").replace(" ", "_")


def _unit_in_name(name: str) -> str | None:
    m = re.search(r"\(([^)]*)\)\s*$", name)
    return m.group(1).strip().lower() if m else None


def read_nightingale(path: str, sample: str | None) -> tuple[dict, dict, dict]:
    """Return (values by canonical name, units by canonical name, qc)."""
    header, rows = tables.read_table(path)
    canon_header = [_canon(h) for h in header]
    hits_cols = sum(1 for h in canon_header if h in NIGHTINGALE_HINTS)
    hits_rows = sum(1 for r in rows if _canon(r[0]) in NIGHTINGALE_HINTS)
    units: dict[str, str] = {}
    if hits_cols >= hits_rows:
        unit_row = None
        data_rows = []
        for r in rows:
            if r[0].strip().lower() in ("unit", "units"):
                unit_row = r
            else:
                data_rows.append(r)
        sel = [r for r in data_rows if sample is None or r[0] == sample]
        if len(sel) != 1:
            raise ValueError(f"{len(sel)} sample rows match; pass --sample")
        vals = {}
        for i, h in enumerate(header[1:], 1):
            c = canon_header[i]
            v = tables.num(sel[0][i])
            if v is not None:
                vals[c] = v
            u = (unit_row[i].strip().lower() if unit_row else None) or _unit_in_name(h)
            if u:
                units[c] = u
        layout = "samples_in_rows"
    else:
        col = tables.pick_column(header, sample)
        ucol = canon_header.index("unit") if "unit" in canon_header else None
        vals = {}
        for r in rows:
            c = _canon(r[0])
            v = tables.num(r[col])
            if v is not None:
                vals[c] = v
            u = (r[ucol].strip().lower() if ucol is not None else None) or _unit_in_name(r[0])
            if u:
                units[c] = u
        layout = "biomarkers_in_rows"
    n_hint = len(set(vals) & NIGHTINGALE_HINTS)
    qc = {"layout": layout, "n_biomarkers": len(vals), "platform": "Nightingale NMR" if n_hint >= 5 else "unknown"}
    return vals, units, qc


def map_markers(vals: dict, units: dict, ref: dict) -> tuple[dict, list[str], list[str]]:
    out, missing, notes = {}, [], []
    for key, aliases in ref["aliases"].items():
        found = next((a for a in aliases if a in vals), None)
        if found is None:
            missing.append(key)
            continue
        x = vals[found]
        u = units.get(found)
        if u and (key, u.replace(" ", "")) in TO_MMOL:
            x = x * TO_MMOL[(key, u.replace(" ", ""))]
            notes.append(f"{key}: converted {u} -> mmol/L")
        elif u and u not in ("mmol/l", "%", "nm", "mmol/l ", "ratio", "a.u.", "signal") and key != "alb":
            raise ValueError(f"{key}: unit {u!r} not supported (expected mmol/L)")
        out[key] = x
    return out, missing, notes


def z_reference(key: str, x: float, m: dict) -> float | None:
    if m.get("plus_one"):
        x = x + 1.0
    if x <= 0:
        return None
    return (math.log(x) - m["logMEAN"]) / m["logSD"]


def metabohealth_reference(markers: dict, ref: dict) -> tuple[float | None, dict]:
    det, s = {}, 0.0
    bad = []
    for key in sorted(ref["markers"]):
        m = ref["markers"][key]
        z = z_reference(key, markers[key], m)
        if z is None:
            bad.append(key)
            continue
        det[key] = z
        s += m["beta"] * z
    if bad:
        return None, {"nonpositive": bad}
    return s, {"z": det}


def metabohealth_dataset(rows: list[dict], ref: dict) -> list[float | None]:
    """Deelen/MiMIR procedure on a cohort: +1 to columns with zeros, ln, scale within the dataset."""
    keys = list(ref["markers"])
    cols = {}
    for k in keys:
        xs = [r.get(k) for r in rows]
        if any(x == 0 for x in xs if x is not None):
            xs = [None if x is None else x + 1 for x in xs]
        lx = [None if x is None else math.log(x) for x in xs]
        ok = [v for v in lx if v is not None]
        mu = sum(ok) / len(ok)
        sd = math.sqrt(sum((v - mu) ** 2 for v in ok) / (len(ok) - 1))
        # R's scale() yields NaN for a constant column; mirror that as None
        cols[k] = [None if v is None or sd == 0 else (v - mu) / sd for v in lx]
    out = []
    for i in range(len(rows)):
        zs = [cols[k][i] for k in keys]
        out.append(None if any(z is None for z in zs) else sum(ref["markers"][k]["beta"] * z for k, z in zip(keys, zs)))
    return out


def run(args) -> dict:
    ref = load_ref()
    vals, units, qc = read_nightingale(args.table, args.sample)
    src = Path(args.table).name
    obs, summary = [], [f"metabolomics: {qc['platform']}, {qc['n_biomarkers']} biomarkers"]
    flags = ["non_fasting"] if args.non_fasting else []
    prov = {"step": "metabolomics.metabohealth", "tool": "metab_metabohealth2019", "version": VERSION,
            "ref_data": {"betas": ref["betas_source"], "reference": ref["reference_source"]}, "qc": qc}
    skipped = None
    if qc["platform"] != "Nightingale NMR":
        skipped = "input not recognised as Nightingale NMR biomarker table"
        markers, missing, notes = {}, [], []
    else:
        markers, missing, notes = map_markers(vals, units, ref)
        qc["unit_notes"] = notes
        if missing:
            skipped = f"missing MetaboHealth markers: {', '.join(missing)}"
        elif markers["alb"] > 1.0 or units.get("alb", units.get("albumin", "")) in ("g/l", "g/dl"):
            skipped = ("albumin reported in g/L (Nightingale 2020 platform); the open BBMRI-NL reference uses the "
                       "2016 platform albumin scale - not scored to avoid a unit-driven shift")
    if skipped is None:
        score, det = metabohealth_reference(markers, ref)
        if score is None:
            skipped = f"non-positive values for {', '.join(det['nonpositive'])} (log undefined)"
        else:
            o = common.make_obs("LP:metab.metabohealth", common.r(score, 4), unit="score (SD units)",
                                tool="metab_metabohealth2019", platform="Nightingale NMR", specimen=args.specimen,
                                source_file=src, datetime=args.date, flags=flags)
            o["scaling"] = "BBMRI-NL reference log mean/SD (single-sample approximation of within-cohort scaling)"
            obs.append(o)
            prov["z"] = {k: common.r(v, 4) for k, v in det["z"].items()}
            summary.append(f"  MetaboHealth {score:+.3f}")
    if skipped:
        prov["skipped"] = skipped
        summary.append("  " + skipped)
    return {"tool_ids": ["metab_metabohealth2019"], "observations": obs, "provenance": [prov], "summary": summary}
