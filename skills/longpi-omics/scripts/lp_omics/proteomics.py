"""Proteomics matrix (SomaScan RFU / Olink NPX) -> organ ages (organage, Oh et al. 2023; SomaScan) + outcome proteins.

Clocks implemented: organage (Oh HS-H, Rutledge J et al. Nature 2023), MIT licence, SomaScan v4 / v4.1 / v5
(rescaled to v4.1 with the package's per-SeqId factors). 13 models: 11 organs + organismal + conventional.
Not implemented: ProtAge (Argentieri et al. Nat Med 2024, Olink) and the Olink organ clocks (Oh et al. 2025) -
see SKILL.md for the licence reasoning. Olink input therefore yields single-protein passthrough only.
"""
from __future__ import annotations

import bisect
import re
from pathlib import Path

from . import common, tables

VERSION = "0.1.0"
PDIR = common.DATA_DIR / "proteomics"
SEQID = re.compile(r"^(?:seq\.)?(\d{4,5})[-.](\d{1,3})$", re.I)
OLINKID = re.compile(r"^OID\d{5}$")

# Single proteins with published outcome (mortality / cardiovascular / kidney) evidence; passed through
# in platform units. SeqIds from the SomaScan v4.0 annotated content file (as shipped with organage).
PASSTHROUGH = {
    "P16860": {"name": "NT-proBNP", "seqid": "7655-11"},
    "Q99988": {"name": "GDF15", "seqid": "4374-45"},
    "P01034": {"name": "Cystatin C", "seqid": "2609-59"},
    "P02741": {"name": "CRP", "seqid": "4337-49"},
    "P05231": {"name": "IL-6", "seqid": "4673-13"},
    "P41159": {"name": "Leptin", "seqid": "8484-24"},
}
SOMA_TO_UNIPROT = {v["seqid"]: k for k, v in PASSTHROUGH.items()}


def add_arguments(p):
    p.add_argument("matrix", help="SomaScan (SeqId x sample or sample x SeqId) or Olink (long or wide NPX) table")
    p.add_argument("--sample", default=None, help="sample column/row to use when several are present")
    p.add_argument("--age", type=float, default=None, help="chronological age (required for organ age gaps)")
    p.add_argument("--sex", choices=["M", "F"], default=None, help="sex (required for organ age gaps)")
    p.add_argument("--assay-version", choices=["v4", "v4.1", "v5"], default=None,
                   help="SomaScan version; auto-detected from the number of SeqIds when omitted")
    p.add_argument("--specimen", default="plasma")


def norm_seqid(s: str) -> str | None:
    m = SEQID.match(s.strip())
    return f"{int(m.group(1))}-{int(m.group(2))}" if m else None


def read_matrix(path: str, sample: str | None) -> dict:
    """Return {"platform": "somascan"|"olink", "values": {id: value}, "uniprot": {id: acc}}."""
    header, rows = tables.read_table(path)
    low = [h.lower() for h in header]
    # Olink long format
    if "npx" in low and ("olinkid" in low or "uniprot" in low):
        i_npx = low.index("npx")
        i_oid = low.index("olinkid") if "olinkid" in low else None
        i_uni = low.index("uniprot") if "uniprot" in low else None
        i_s = low.index("sampleid") if "sampleid" in low else None
        samples = sorted({r[i_s] for r in rows}) if i_s is not None else [None]
        if sample is None and len(samples) > 1:
            raise ValueError(f"Olink table has {len(samples)} samples; pass --sample")
        want = sample if sample is not None else samples[0]
        vals, uni = {}, {}
        for r in rows:
            if i_s is not None and r[i_s] != want:
                continue
            key = r[i_oid] if i_oid is not None else r[i_uni]
            v = tables.num(r[i_npx])
            if v is not None:
                vals[key] = v
            if i_uni is not None:
                uni[key] = r[i_uni]
        if not vals:
            raise ValueError("no NPX values for the selected sample")
        return {"platform": "olink", "values": vals, "uniprot": uni, "layout": "long"}
    # SomaScan, analytes in rows
    first_col = [r[0] for r in rows]
    n_seq_rows = sum(1 for x in first_col if norm_seqid(x))
    n_seq_cols = sum(1 for h in header if norm_seqid(h))
    if n_seq_rows >= max(1, 0.5 * len(rows)) and n_seq_rows >= n_seq_cols:
        col = tables.pick_column(header, sample)
        vals = {}
        for r in rows:
            k = norm_seqid(r[0])
            v = tables.num(r[col])
            if k and v is not None:
                vals[k] = v
        return {"platform": "somascan", "values": vals, "uniprot": {}, "layout": "analyte_rows",
                "n_analytes": n_seq_rows}
    if n_seq_cols >= 1:
        # samples in rows: first column = sample id
        if sample is not None:
            sel = [r for r in rows if r[0] == sample]
        else:
            sel = rows
        if len(sel) != 1:
            raise ValueError(f"{len(sel)} sample rows match; pass --sample")
        vals = {}
        for h, x in zip(header, sel[0]):
            k = norm_seqid(h)
            v = tables.num(x) if k else None
            if k and v is not None:
                vals[k] = v
        return {"platform": "somascan", "values": vals, "uniprot": {}, "layout": "sample_rows",
                "n_analytes": n_seq_cols}
    # Olink wide: columns = UniProt or OlinkID
    n_oid = sum(1 for h in header if OLINKID.match(h))
    if n_oid:
        col_ok = [i for i, h in enumerate(header) if OLINKID.match(h)]
        sel = [r for r in rows if sample is None or r[0] == sample]
        if len(sel) != 1:
            raise ValueError(f"{len(sel)} sample rows match; pass --sample")
        vals = {header[i]: tables.num(sel[0][i]) for i in col_ok if tables.num(sel[0][i]) is not None}
        return {"platform": "olink", "values": vals, "uniprot": {}, "layout": "wide"}
    raise ValueError("could not recognise SomaScan SeqIds or Olink NPX columns")


def detect_soma_version(n: int) -> str | None:
    if n >= 10000:
        return "v5"
    if n >= 6500:
        return "v4.1"
    if n >= 4500:
        return "v4"
    return None


def load_organage() -> dict:
    return common.load_json(PDIR / "organage_somascan.json")


def interp_linear_extrapolate(xs: list[float], ys: list[float], x: float) -> float:
    if len(xs) == 1:
        return ys[0]
    i = bisect.bisect_left(xs, x)
    i = min(max(i, 1), len(xs) - 1)
    x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def organ_age(model: dict, log10_rfu: dict, sex_f: int) -> tuple[float | None, list[str]]:
    missing = [p["seqid"] for p in model["proteins"] if p["seqid"] not in log10_rfu]
    if missing:
        return None, missing
    s = model["intercept"] + model["coef_sex_f"] * sex_f
    for p in model["proteins"]:  # stored order -> deterministic sum
        z = (log10_rfu[p["seqid"]] - p["mean"]) / p["scale"]
        s += p["coef"] * z
    return s, []


def run(args) -> dict:
    import math

    m = read_matrix(args.matrix, args.sample)
    src = Path(args.matrix).name
    obs, prov, summary = [], [], []
    tool_ids = ["prot_organage2023", "prot_passthrough"]
    plat_label = None
    qc = {"layout": m["layout"], "n_values": len(m["values"])}
    if m["platform"] == "somascan":
        ver = args.assay_version or detect_soma_version(m.get("n_analytes", len(m["values"])))
        qc["assay_version"] = ver
        qc["version_source"] = "argument" if args.assay_version else "SeqId count"
        plat_label = f"SomaScan {ver}" if ver else "SomaScan (version unknown)"
        summary.append(f"proteomics: {plat_label}, {len(m['values'])} SeqIds with values")
        nonpos = sum(1 for v in m["values"].values() if v <= 0)
        if m["values"] and sum(m["values"].values()) / len(m["values"]) < 50:
            qc["warning"] = "values look log-transformed; organage needs ANML-normalised RFU"
        oa = load_organage()
        clock_prov = {"step": "proteomics.organage", "tool": "prot_organage2023", "version": VERSION,
                      "ref_data": {"coefficients": oa["source"], "models": oa["models"]}, "qc": qc}
        if ver is None:
            clock_prov["skipped"] = "SomaScan version not identifiable; pass --assay-version"
        elif args.age is None or args.sex is None:
            clock_prov["skipped"] = "--age and --sex are required for organ age gaps"
        elif qc.get("warning") or nonpos:
            clock_prov["skipped"] = qc.get("warning") or f"{nonpos} non-positive RFU values"
        else:
            scale = oa["scale_v4_to_v41"] if ver == "v4" else oa["scale_v5_to_v41"] if ver == "v5" else {}
            logv = {}
            for k, v in m["values"].items():
                f = scale.get(k, 1.0) if ver != "v4.1" else 1.0
                logv[k] = math.log10(v * f)
            sex_f = 1 if args.sex == "F" else 0
            results = {}
            for organ in sorted(oa["organs"]):
                model = oa["organs"][organ]
                pred, missing = organ_age(model, logv, sex_f)
                if pred is None:
                    results[organ] = {"computed": False, "n_missing": len(missing)}
                    continue
                yhat = interp_linear_extrapolate(model["lowess"]["x"], model["lowess"]["y"], args.age)
                gap = pred - yhat
                gz = (gap - model["agegap_scaler"]["mean"]) / model["agegap_scaler"]["scale"] \
                    - (0 - model["agegap_scaler"]["mean"]) / model["agegap_scaler"]["scale"]
                code = f"LP:prot.organage_{organ.lower()}_gap"
                o = common.make_obs(code, common.r(gap, 3), unit="years", tool="prot_organage2023",
                                    platform=plat_label, specimen=args.specimen, source_file=src,
                                    datetime=args.date)
                o["predicted_age"] = common.r(pred, 3)
                o["agegap_z"] = common.r(gz, 4)
                obs.append(o)
                results[organ] = {"computed": True, "n_proteins": len(model["proteins"])}
                summary.append(f"  organage {organ}: gap {gap:+.2f} y (z {gz:+.2f})")
            clock_prov["results"] = results
        prov.append(clock_prov)
        lookup = {seq: acc for seq, acc in SOMA_TO_UNIPROT.items()}
        unit = "RFU"
    else:
        plat_label = "Olink"
        summary.append(f"proteomics: Olink NPX, {len(m['values'])} assays; no open-licence Olink clock implemented")
        prov.append({"step": "proteomics.organage", "tool": "prot_organage2023", "version": VERSION,
                     "skipped": "Olink input: organage models are SomaScan-only", "qc": qc})
        lookup = {}
        for k in m["values"]:
            acc = m["uniprot"].get(k) or (k if re.match(r"^[OPQ]\d[A-Z0-9]{3}\d$", k) else None)
            if acc in PASSTHROUGH:
                lookup[k] = acc
        unit = "NPX"
    passed = []
    for probe in sorted(lookup):
        acc = lookup[probe]
        if probe not in m["values"]:
            continue
        o = common.make_obs(f"UNIPROT:{acc}", common.r(m["values"][probe], 4), unit=unit, tool="prot_passthrough",
                            platform=plat_label, specimen=args.specimen, source_file=src, datetime=args.date)
        o["platform_probe"] = probe
        o["analyte_name"] = PASSTHROUGH[acc]["name"]
        obs.append(o)
        passed.append(PASSTHROUGH[acc]["name"])
    prov.append({"step": "proteomics.passthrough", "tool": "prot_passthrough", "version": VERSION,
                 "ref_data": {"proteins": sorted(PASSTHROUGH)}, "passed": passed})
    summary.append(f"  passthrough proteins: {', '.join(passed) or 'none'}")
    return {"tool_ids": tool_ids, "observations": obs, "provenance": prov, "summary": summary}
