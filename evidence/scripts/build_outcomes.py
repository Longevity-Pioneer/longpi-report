#!/usr/bin/env python3
"""Build registry/outcomes/<id>.json (Chinese baseline incidence and, for screenable cancers, cause-of-death shares).

Pipeline
  1. fetch_outcome_sources.py   -> registry/sources/<key>.json (fetched page, sha256, table text)
  2. build_outcomes.py --transcribe
                                -> evidence/outcomes/<table>.csv: the rows used, transcribed from the stored
                                   source text (cell copied as printed, with table block / row / column locator)
  3. build_outcomes.py          -> registry/outcomes/*.json, verification record in registry/sources/*.json[checks],
                                   evidence/results/outcomes_checks.json (verification + sanity checks)

Derivations (all documented in each outcome's quality_zh, `derived: true` where applied):
  - cancers: registry-area age-specific rates of a source year are moved to the 2022 national level with one factor
    per sex, factor = national 2022 ASR (Segi; Han et al. JNCC 2024, Table 1/2) / source-year ASR (Segi; same
    paper as the age table). Age shape is the source year's. Mortality is treated the same way (ASMR).
  - mortality_share = cancer-specific mortality (2022 level) / all-cause mortality, both per person-year, all-cause
    = mean single-year central death rate mx over the band from the WPP 2024 China life table (year 2022).
  - T2D / hypertension / CKD: published age-only rates split by sex with the published sex ratio k = rate_M / rate_F,
    assuming equal person-time by sex in each band: rate_F = 2r/(1+k), rate_M = k * rate_F (CKD: r * sex/crude).
  - CHD / stroke: national surveillance event rates (first + recurrent) x first-onset share 518.38/620.33.

Every number written to an outcome is either a transcribed value (checked verbatim against the stored source text)
or computed from transcribed values listed in `inputs`; build fails if any transcribed value is not found.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/longpi-report"
REG = SKILL / "registry"
SRC_DIR = REG / "sources"
OUT_DIR = REG / "outcomes"
CSV_DIR = ROOT / "evidence/outcomes"
RESULTS = ROOT / "evidence/results/outcomes_checks.json"
LIFETABLE = SKILL / "data/lifetable_china_wpp2024.json"
WPP_YEAR = "2022"
TODAY = dt.date.today().isoformat()
HORIZON = 90


def safe_key(key: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in key)


def load_source(key: str) -> dict:
    p = SRC_DIR / (safe_key(key) + ".json")
    if not p.exists():
        raise SystemExit(f"missing source {key}; run fetch_outcome_sources.py first")
    return json.loads(p.read_text(encoding="utf-8"))


def norm(s: str) -> str:
    return (s.replace("–", "-").replace("—", "-").replace("−", "-").replace("‐", "-")
            .replace(" ", " ").replace(" ", " ").strip())


def blocks(text: str) -> dict:
    """{block id: [rows as cell lists]}; PMC tables are '[Table block i]', excerpt sections are '[...]' headers."""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"\[Table block (\d+)\]", line)
        if m:
            cur = int(m.group(1)); out[cur] = []; continue
        if line.startswith("[") and "]" in line[:200]:
            cur = line[1:line.index("]")]; out[cur] = []; continue
        if cur is not None:
            out[cur].append([c.strip() for c in line.split(" | ")])
    return out


def find_row(rows, label, label_col=0, section=None, occurrence=0):
    """section: header row label, or a path 'AD/Male' (first 'Male' header after the 'AD' header)."""
    start = 0
    for sec in (section.split("/") if section else []):
        idx = [i for i, r in enumerate(rows) if i >= start and len(r) >= 1 and norm(r[0]) == norm(sec)]
        if not idx:
            raise KeyError(f"section {section!r} not found")
        start = idx[0] + 1
    hits = [r for r in rows[start:] if len(r) > label_col and norm(r[label_col]) == norm(label)]
    if len(hits) <= occurrence:
        raise KeyError(f"row {label!r} (section {section}) not found")
    return hits[occurrence]


NUM = re.compile(r"-?\d[\d,]*\.?\d*")


def cell_number(cell: str) -> str:
    """First number in a cell as printed ('3.48 (0.44-6.53)' -> '3.48'; '1,063.97' kept)."""
    m = NUM.search(cell.replace(" ", "") if re.fullmatch(r"[\d ]+\d", cell.strip()) else cell)
    if not m:
        raise ValueError(f"no number in cell {cell!r}")
    return m.group(0)


def to_float(s: str) -> float:
    return float(s.replace(",", ""))


# ----------------------------------------------------------------------------- transcription specs
# Each spec -> one CSV. rows: (sex, age_lo, age_hi, row label, column index[, section]) or for scalars (name, label, col).

def five_year(labels_fmt, lo=30, hi=85, top_label=None):
    """[(age_lo, age_hi, label)] for 5-year bands; top band (hi) is open-ended in the source and capped at 89."""
    out = []
    for a in range(lo, hi + 1, 5):
        lab = top_label if (a == hi and top_label) else labels_fmt.format(a)
        out.append((a, a + 4 if a < hi else 89, lab))
    return out


def age_rows(bands, cols, **kw):
    return [dict(sex=s, age_lo=lo, age_hi=hi, label=lab, col=c, **kw) for s, c in cols.items() for lo, hi, lab in bands]


NAT = "pmcid:PMC11256708"
SPECS = {
    # ---- national 2022 level (Han et al. 2024, Table 1 incidence, Table 2 mortality; Segi ASR)
    "cancer_national_2022_asr": dict(source=NAT, scalars=[
        *[dict(name=f"{m}_{site}_{s}", block=b, label=lab, col=c, unit="per_100k_segi")
          for m, b in (("asir", 0), ("asmr", 1))
          for site, lab, cols in (("crc", "Colon-rectum", {"M": 7, "F": 10}), ("lung", "Lung", {"M": 7, "F": 10}),
                                  ("liver", "Liver", {"M": 7, "F": 10}), ("gastric", "Stomach", {"M": 7, "F": 10}),
                                  ("breast", "Female breast", {"F": 10}), ("prostate", "Prostate", {"M": 7}))
          for s, c in cols.items()]]),
    # ---- colorectal 2011 (registry areas)
    "crc_2011_incidence": dict(source="pmcid:PMC4329182", block=2, unit="per_100k",
                               rows=age_rows(five_year("{}-", top_label="85+"), {"M": 2, "F": 3})),
    "crc_2011_mortality": dict(source="pmcid:PMC4329182", block=4, unit="per_100k",
                               rows=age_rows(five_year("{}-", top_label="85+"), {"M": 2, "F": 3})),
    "crc_2011_summary": dict(source="pmcid:PMC4329182", scalars=[
        dict(name="asir_M", block=1, label="Male", col=5), dict(name="asir_F", block=1, label="Female", col=5),
        dict(name="cum074_M", block=1, label="Male", col=6), dict(name="cum074_F", block=1, label="Female", col=6),
        dict(name="asmr_M", block=3, label="Male", col=5), dict(name="asmr_F", block=3, label="Female", col=5)]),
    # ---- lung 2011
    "lung_2011_incidence": dict(source="pmcid:PMC4718125", block=2, unit="per_100k",
                                rows=age_rows(five_year("{}–", top_label="85+"), {"M": 2, "F": 3})),
    "lung_2011_mortality": dict(source="pmcid:PMC4718125", block=4, unit="per_100k",
                                rows=age_rows(five_year("{}–", top_label="85+"), {"M": 2, "F": 3})),
    "lung_2011_summary": dict(source="pmcid:PMC4718125", scalars=[
        dict(name="asir_M", block=1, label="Male", col=5), dict(name="asir_F", block=1, label="Female", col=5),
        dict(name="cum074_M", block=1, label="Male", col=6), dict(name="cum074_F", block=1, label="Female", col=6),
        dict(name="asmr_M", block=3, label="Male", col=5), dict(name="asmr_F", block=3, label="Female", col=5)]),
    # ---- liver 2009
    "liver_2009_incidence": dict(source="pmcid:PMC3845572", block=2, unit="per_100k",
                                 rows=age_rows(five_year("{}–", top_label="85–"), {"M": 2, "F": 3})),
    "liver_2009_mortality": dict(source="pmcid:PMC3845572", block=4, unit="per_100k",
                                 rows=age_rows(five_year("{}–", top_label="85–"), {"M": 2, "F": 3})),
    "liver_2009_summary": dict(source="pmcid:PMC3845572", scalars=[
        dict(name="asir_M", block=1, label="Male", label_col=1, col=6), dict(name="asir_F", block=1, label="Female", label_col=1, col=6),
        dict(name="cum074_M", block=1, label="Male", label_col=1, col=7), dict(name="cum074_F", block=1, label="Female", label_col=1, col=7),
        dict(name="asmr_M", block=3, label="Male", label_col=1, col=6), dict(name="asmr_F", block=3, label="Female", label_col=1, col=6)]),
    # ---- stomach 2014
    "gastric_2014_incidence": dict(source="pmcid:PMC6037587", block=2, unit="per_100k",
                                   rows=age_rows(five_year("{}–", top_label="85+"), {"M": 2, "F": 3})),
    "gastric_2014_mortality": dict(source="pmcid:PMC6037587", block=4, unit="per_100k",
                                   rows=age_rows(five_year("{}–", top_label="85+"), {"M": 2, "F": 3})),
    "gastric_2014_summary": dict(source="pmcid:PMC6037587", scalars=[
        dict(name="asir_M", block=1, label="Male", col=5), dict(name="asir_F", block=1, label="Female", col=5),
        dict(name="cum074_M", block=1, label="Male", col=6), dict(name="cum074_F", block=1, label="Female", col=6),
        dict(name="asmr_M", block=3, label="Male", col=5), dict(name="asmr_F", block=3, label="Female", col=5)]),
    # ---- female breast 2013
    "breast_2013_incidence": dict(source="pmcid:PMC5415464", block=2, unit="per_100k",
                                  rows=age_rows(five_year("{}"), {"F": 1})),
    "breast_2013_mortality": dict(source="pmcid:PMC5415464", block=4, unit="per_100k",
                                  rows=age_rows(five_year("{}"), {"F": 1})),
    "breast_2013_summary": dict(source="pmcid:PMC5415464", scalars=[
        dict(name="asir_F", block=1, label="All", col=5), dict(name="cum074_F", block=1, label="All", col=6),
        dict(name="asmr_F", block=3, label="All", col=5)]),
    # ---- prostate, Jiangsu 2019 (total column of each age group)
    "prostate_2019_jiangsu": dict(source="pmcid:PMC11431764", block=3, unit="per_100k", rows=[
        dict(sex="M", age_lo=30, age_hi=59, label="2019", col=1), dict(sex="M", age_lo=60, age_hi=69, label="2019", col=4),
        dict(sex="M", age_lo=70, age_hi=79, label="2019", col=7), dict(sex="M", age_lo=80, age_hi=89, label="2019", col=10)]),
    "prostate_2019_jiangsu_summary": dict(source="pmcid:PMC11431764", scalars=[
        dict(name="asir_M", block=2, label="2019", col=4)]),
    # ---- type 2 diabetes: age rates (per 1000 PY) and sex rates (per 1000 PY)
    "t2d_age": dict(source="pmcid:PMC6169758", block=1, unit="per_1000_py", rows=[
        dict(sex="both", age_lo=30, age_hi=39, label="30 to <40", col=3), dict(sex="both", age_lo=40, age_hi=49, label="40 to <50", col=3),
        dict(sex="both", age_lo=50, age_hi=59, label="50 to <60", col=3), dict(sex="both", age_lo=60, age_hi=69, label="60 to <70", col=3),
        dict(sex="both", age_lo=70, age_hi=89, label="≥70", col=3)]),
    "t2d_sex": dict(source="pmcid:PMC12226831", scalars=[
        dict(name="rate_M", block=2, label="Male", col=3, unit="per_1000_py"),
        dict(name="rate_F", block=2, label="Female", col=3, unit="per_1000_py")]),
    # ---- hypertension (CHNS, per 100 PY, last column = total hypertension)
    "htn_chns": dict(source="pmcid:PMC6443580", block=1, unit="per_100_py", rows=[
        dict(sex="both", age_lo=30, age_hi=34, label="18–34", col=5), dict(sex="both", age_lo=35, age_hi=49, label="35–49", col=5),
        dict(sex="both", age_lo=50, age_hi=64, label="50–64", col=5), dict(sex="both", age_lo=65, age_hi=89, label="≥ 65", col=5)]),
    "htn_chns_sex": dict(source="pmcid:PMC6443580", scalars=[
        dict(name="rate_M", block=1, label="Male", col=5, unit="per_100_py"),
        dict(name="rate_F", block=1, label="Female", col=5, unit="per_100_py")]),
    # ---- CHD and stroke, national surveillance 2023 (excerpt sections)
    **{f"{oc}_2023": dict(source="doi:10.1016/j.jacc.2025.08.060",
                          block="Figure 1 Incidence Rates of CVD, CHD, and Stroke by Sex and Age Groups Across 262 Surveillance Sites in China, 2023; columns: Age Group (Years) | Male | Female, per 100,000",
                          unit="per_100k", rows=[dict(sex=s, age_lo=lo, age_hi=hi, label=lab, col=c, section=sec)
                                                for s, c in (("M", 1), ("F", 2))
                                                for lo, hi, lab in ((30, 34, "25-34"), (35, 44, "35-44"), (45, 54, "45-54"),
                                                                    (55, 64, "55-64"), (65, 74, "65-74"), (75, 89, "≥75"))])
       for oc, sec in (("chd", "CHD"), ("stroke", "Stroke"))},
    "cvd_2023_onset": dict(source="doi:10.1016/j.jacc.2025.08.060", scalars=[
        dict(name="first_onset", block="Results, first-onset vs recurrent", regex=r"([\d.]+)/100,000 for first-onset CVD events"),
        dict(name="all_events", block="Abstract, RESULTS", regex=r"crude CVD incidence rate was ([\d.]+) per 100,000")]),
    # ---- CKD (CKB, ICD-coded), per 100,000 PY
    "ckd_ckb": dict(source="pmcid:PMC13156572", scalars=[
        dict(name="crude", block=2, label="Crude rates", col=1), dict(name="sex_M", block=2, label="Male", col=1),
        dict(name="sex_F", block=2, label="Female", col=1), dict(name="age_lt60", block=2, label="< 60 yrs", col=1),
        dict(name="age_60_69", block=2, label="60–69 yrs", col=1), dict(name="age_ge70", block=2, label="≥ 70 yrs", col=1)]),
    # ---- MASLD (Shanghai Songjiang), per 100 PY
    "masld_songjiang": dict(source="pmcid:PMC11882351", block=2, unit="per_100_py", rows=age_rows(
        [(30, 39, "18–39"), (40, 49, "40–49"), (50, 59, "50–59"), (60, 69, "60–69"), (70, 89, "≥70")], {"M": 3, "F": 5})),
    # ---- Alzheimer disease (Ji County), per 1000 PY, AD column = 5
    # ---- fix/outcome-baselines additions
    "prostate_jiangsu_population": dict(source="pmcid:PMC11431764", block=1, unit="persons", rows=[
        dict(sex="both", age_lo=lo, age_hi=lo + 4 if lo else 0, label=lab, col=1) for lo, lab in (
            (0, "0–"), (1, "1–4"), (5, "5–9"), (10, "10–14"), (15, "15–19"), (20, "20–24"), (25, "25–29"), (30, "30–34"),
            (35, "35–39"), (40, "40–44"), (45, "45–49"), (50, "50–54"), (55, "55–59"), (60, "60–64"), (65, "65–69"))]),
    "t2d_zhejiang": dict(source="pmcid:PMC6995322", block=1, unit="per_100k", rows=[
        dict(sex=s, age_lo=lo, age_hi=hi, label=lab, col=3, section=sec)
        for s, sec in (("M", "Males"), ("F", "Females"))
        for lo, hi, lab in ((30, 39, "30-39"), (40, 49, "40-49"), (50, 59, "50-59"), (60, 69, "60-69"), (70, 79, "70-79"), (80, 89, "≥80"))]),
    "ad_taiwan_2010": dict(source="pmcid:PMC6878786", block=2, unit="per_1000_py", rows=[
        dict(sex=s, age_lo=lo, age_hi=hi, label=lab, col=7, section=sec)
        for s, sec in (("M", "AD/Male"), ("F", "AD/Female"))
        for lo, hi, lab in ((65, 69, "65–69"), (70, 74, "70–74"), (75, 79, "75–79"), (80, 84, "80–84"), (85, 89, "≥85"))]),
    "ad_taiwan_2010_crude": dict(source="pmcid:PMC6878786", scalars=[
        dict(name="ad_crude_2010", block=0, label="Crude", col=7, occurrence=1, unit="per_1000_py")]),
    "ad_china_4region": dict(source="pmid:26086181", scalars=[
        dict(name="ad_ge65", block="Abstract", regex=r"dementia, ([\d.]+)/1000 person-years for AD", unit="per_1000_py"),
        dict(name="dementia_ge65", block="Abstract", regex=r"years was ([\d.]+)/1000 person-years for dementia", unit="per_1000_py")]),
    "ad_jicounty": dict(source="pmcid:PMC8021353", block=1, unit="per_1000_py", rows=[
        *[dict(sex="M", age_lo=lo, age_hi=hi, label=lab, col=5, section="Man") for lo, hi, lab in ((60, 69, "60–69"), (70, 79, "70–79"), (80, 89, "80"))],
        *[dict(sex="F", age_lo=lo, age_hi=hi, label=lab, col=5, section="Woman") for lo, hi, lab in ((60, 69, "60–69"), (70, 79, "70–79"), (80, 89, "80–"))]]),
}

CSV_FIELDS = ["source_key", "locator", "kind", "name", "sex", "age_lo", "age_hi", "row_label", "column", "value", "unit"]


def transcribe():
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    for name, sp in SPECS.items():
        src = load_source(sp["source"])
        bl = blocks(src["text"])
        out = []
        for r in sp.get("rows", []):
            rows = bl[sp["block"]]
            row = find_row(rows, r["label"], section=r.get("section"))
            out.append(dict(source_key=sp["source"], locator=f"table block {sp['block']}" if isinstance(sp["block"], int) else sp["block"][:60],
                            kind="age_rate", name="", sex=r["sex"], age_lo=r["age_lo"], age_hi=r["age_hi"], row_label=r["label"],
                            column=r["col"], value=cell_number(row[r["col"]]), unit=sp["unit"]))
        for s in sp.get("scalars", []):
            if "regex" in s:
                body = "\n".join(" | ".join(x) for x in bl[s["block"]])
                val, lab, col = re.search(s["regex"], body).group(1), s["regex"], ""
            else:
                row = find_row(bl[s["block"]], s["label"], label_col=s.get("label_col", 0), occurrence=s.get("occurrence", 0))
                val, lab, col = cell_number(row[s["col"]]), s["label"], s["col"]
            loc = f"table block {s['block']}" if isinstance(s["block"], int) else s["block"][:60]
            out.append(dict(source_key=sp["source"], locator=loc, kind="scalar", name=s["name"], sex="", age_lo="", age_hi="",
                            row_label=lab, column=col, value=val, unit=s.get("unit", "per_100k")))
        p = CSV_DIR / f"{name}.csv"
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            w.writeheader()
            w.writerows(out)
        print(f"transcribed {name:32s} {len(out):3d} values -> {p.relative_to(ROOT)}")


# ----------------------------------------------------------------------------- reading + verification

def read_csv(name):
    with (CSV_DIR / f"{name}.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


VERIFY = {"checked": 0, "found": 0, "missing": []}
CHECKS_BY_SOURCE: dict = {}


def verify_value(row: dict, used_by: str):
    """The transcribed value must appear as a whole number token in the source text, on the row it was read from."""
    src = load_source(row["source_key"])
    text = norm(src["text"])
    v = row["value"]
    pat = re.compile(r"(?<![\d.])" + re.escape(v) + r"(?![\d])")
    lines = [ln for ln in text.splitlines() if pat.search(ln)]
    lab = norm(row["row_label"])
    if row["kind"] == "age_rate" or (row["kind"] == "scalar" and row["column"] != ""):
        ok_lines = [ln for ln in lines if any(norm(c) == lab for c in ln.split(" | "))]
    else:  # regex-located sentence
        ok_lines = [ln for ln in lines if re.search(row["row_label"].replace("([\\d.]+)", re.escape(v)), ln)]
    found = bool(ok_lines)
    VERIFY["checked"] += 1
    VERIFY["found"] += found
    if not found:
        VERIFY["missing"].append(f"{row['source_key']} {row['row_label']} {v}")
    CHECKS_BY_SOURCE.setdefault(row["source_key"], []).append(
        {"term": used_by, "number": v, "found": found, "context": (ok_lines[0][:160] if ok_lines else "")})
    return to_float(v)


def age_table(name, used_by, scale=1.0):
    """{sex: [(lo, hi, value*scale, raw_str)]} from an age-rate CSV, every value verified."""
    out = {}
    for r in read_csv(name):
        if r["kind"] != "age_rate":
            continue
        val = verify_value(r, used_by)
        out.setdefault(r["sex"], []).append((int(r["age_lo"]), int(r["age_hi"]), val * scale, r["value"]))
    return out


def caption(key, block):
    """Table caption as stored in the source text (used as evidence.quote: it is the source's own wording)."""
    for line in load_source(key)["text"].splitlines():
        if line.startswith(f"[Table block {block}]"):
            return line.split("] ", 1)[1].strip()
    raise KeyError(f"{key}: no table block {block}")


def scalars(name, used_by):
    return {r["name"]: verify_value(r, used_by) for r in read_csv(name) if r["kind"] == "scalar"}


# ----------------------------------------------------------------------------- life table / sanity

LT = json.loads(LIFETABLE.read_text(encoding="utf-8"))


def mx(sex, age):
    return LT["mx"][sex][WPP_YEAR][min(age, 100)]


def band_mx(sex, lo, hi):
    return sum(mx(sex, a) for a in range(lo, hi + 1)) / (hi - lo + 1)


def rate_at(bands, age):
    for lo, hi, r, *_ in bands:
        if lo <= age <= hi:
            return r
    return 0.0


def lifetime_risk(bands, sex, start=30, stop=HORIZON):
    """P(diagnosis in [start, stop)) given alive and disease-free at `start`; competing all-cause mortality from WPP."""
    surv, p = 1.0, 0.0
    for a in range(start, stop):
        h = rate_at(bands, a) / 1e5
        m = mx(sex, a)
        q = 1 - math.exp(-(h + m))
        p += surv * q * (h / (h + m) if h + m > 0 else 0)
        surv *= 1 - q
    return p


def cum_rate(bands, lo=30, hi=74):
    """Registry cumulative rate (sum of 5-year rates x 5, no competing risk), %, over [lo, hi]."""
    return sum(rate_at(bands, a) for a in range(lo, hi + 1)) / 1e5 * 100


def monotone_breaks(bands, ignore_last=True):
    vals = [r for _, _, r, *_ in sorted(bands)]
    if ignore_last:
        vals = vals[:-1]
    return sum(1 for a, b in zip(vals, vals[1:]) if b < a * 0.97)


# ----------------------------------------------------------------------------- outcome assembly

def rows_out(bands, key="rate", nd=2):
    return [{"sex": s, "age_lo": lo, "age_hi": hi, key: round(v, nd if key == "rate" else 5)}
            for s, bl in bands.items() for lo, hi, v, *_ in sorted(bl)]


def rec(oid, name_zh, icd, sex, inc_rows, inc_meta, diag, lic_note, quote, url, ms=None):
    o = {"id": oid, "name_zh": name_zh, "icd10": icd, "sex": sex,
         "incidence": {"unit": "per_100k_py", "by_sex_age": inc_rows, **inc_meta},
         "diagnosed_codes": diag, "horizon_lifetime_age": HORIZON,
         "license": {"commercial_use": True, "note": lic_note},
         "evidence": {"quote": quote, "url": url, "verified_at": TODAY, "verifier": "evidence/scripts/build_outcomes.py",
                      "numbers_verified": True}}
    if ms is not None:
        o["mortality_share"] = ms
    return o


FACTS_NOTE = ("所用数字为已发表论文表格中的统计事实，按出处引用；registry/sources 只保存核对所需的表格单元格（数字与行列名），"
              "不保存论文正文。论文本身的许可：{lic}。该许可约束论文文本与图表的再发布，不约束对统计事实的引用；"
              "如需更保守的口径，可只保留出处与派生结果。")

CANCERS = {
    "crc": dict(name="结直肠癌", icd=["C18", "C19", "C20"], sex="both", src="pmcid:PMC4329182", year=2011, tag="crc_2011",
                site_en="Colon-rectum"),
    "lung_ca": dict(name="肺癌", icd=["C33", "C34"], sex="both", src="pmcid:PMC4718125", year=2011, tag="lung_2011", nat="lung"),
    "liver_ca": dict(name="肝癌", icd=["C22"], sex="both", src="pmcid:PMC3845572", year=2009, tag="liver_2009", nat="liver"),
    "gastric_ca": dict(name="胃癌", icd=["C16"], sex="both", src="pmcid:PMC6037587", year=2014, tag="gastric_2014", nat="gastric"),
    "breast_ca": dict(name="乳腺癌", icd=["C50"], sex="F", src="pmcid:PMC5415464", year=2013, tag="breast_2013", nat="breast"),
}
CANCERS["crc"]["nat"] = "crc"


def build_cancer(oid, c, nat, report):
    used = f"outcome:{oid}"
    summ = scalars(f"{c['tag']}_summary", used)
    sexes = ["F"] if c["sex"] == "F" else ["M", "F"]
    f_inc = {s: nat[f"asir_{c['nat']}_{s}"] / summ[f"asir_{s}"] for s in sexes}
    f_mort = {s: nat[f"asmr_{c['nat']}_{s}"] / summ[f"asmr_{s}"] for s in sexes}
    raw_inc = age_table(f"{c['tag']}_incidence", used)
    raw_mort = age_table(f"{c['tag']}_mortality", used)
    inc = {s: [(lo, hi, v * f_inc[s], raw) for lo, hi, v, raw in raw_inc[s]] for s in sexes}
    mort = {s: [(lo, hi, v * f_mort[s], raw) for lo, hi, v, raw in raw_mort[s]] for s in sexes}
    share = {s: [(lo, hi, v / 1e5 / band_mx(s, lo, hi), raw) for lo, hi, v, raw in mort[s]] for s in sexes}
    src = load_source(c["src"])
    factors = "；".join(f"{'男' if s == 'M' else '女'}发病×{f_inc[s]:.3f}、死亡×{f_mort[s]:.3f}" for s in sexes)
    quality = (f"年龄形状取自国家癌症中心{c['year']}年全国肿瘤登记地区{c['name']}分性别 5 岁组年龄别发病率与死亡率（原表逐字核对）；"
               f"再按性别乘以同一系数，使世标率等于 2022 年全国估计值（Han 等 2024 年《国家癌症中心杂志》表 1、表 2），"
               f"系数 = 2022 年全国世标率 ÷ {c['year']}年登记地区世标率（{factors}）。假定各年龄组变化幅度相同，"
               f"登记地区与全国的差别也并入该系数。85 岁及以上组原为开放组，此处截至 89 岁。")
    if oid == "crc":
        quality += "来源口径为 C18–C21（含肛门，占比很小）。"
    if oid == "liver_ca":
        quality += "形状年份较早（2009 年），此后肝癌年龄别发病整体后移，60 岁以下可能略偏高、高龄略偏低。"
    inc_meta = {"source": f"{src['citation']} × 2022 年全国水平：{load_source(NAT)['citation']}",
                "source_keys": [c["src"], NAT], "year": 2022, "shape_year": c["year"], "region": "China",
                "derived": True, "quality_zh": quality,
                "inputs": {"age_table": f"evidence/outcomes/{c['tag']}_incidence.csv",
                           "asr_source_year": {s: summ[f"asir_{s}"] for s in sexes},
                           "asr_2022": {s: nat[f"asir_{c['nat']}_{s}"] for s in sexes},
                           "factor": {s: round(f_inc[s], 4) for s in sexes}}}
    ms = {"by_sex_age": rows_out(share, key="share"), "source": f"{src['citation']}（年龄别死亡率）× 2022 年全国死亡世标率（{load_source(NAT)['citation']}）；"
          f"全因死亡率：WPP 2024 中国生命表 {WPP_YEAR} 年各单岁 mx 在年龄组内平均",
          "year": 2022, "derived": True, "source_keys": [c["src"], NAT, "data/lifetable_china_wpp2024.json"],
          "method_zh": "死因占比 = 该癌种年龄别死亡率（按 2022 年全国死亡世标率校准）÷ 同性别同年龄组全因死亡率",
          "inputs": {"asmr_source_year": {s: summ[f"asmr_{s}"] for s in sexes},
                     "asmr_2022": {s: nat[f"asmr_{c['nat']}_{s}"] for s in sexes},
                     "factor": {s: round(f_mort[s], 4) for s in sexes}}}
    o = rec(oid, c["name"], c["icd"], c["sex"], rows_out(inc), inc_meta, [f"ICD10:{x}" for x in c["icd"]],
            FACTS_NOTE.format(lic=src["licence"]),
            quote=caption(c["src"], 2), url=src["url"], ms=ms)
    rep = {"shape_year": c["year"], "factor_incidence": f_inc, "factor_mortality": f_mort}
    for s in sexes:
        rep[f"cum0_74_source_{s}"] = summ[f"cum074_{s}"]
        rep[f"cum30_74_from_raw_rates_{s}"] = round(cum_rate([(lo, hi, v) for lo, hi, v, _ in raw_inc[s]]), 3)
        rep[f"cum30_74_scaled_{s}"] = round(cum_rate(inc[s]), 3)
        rep[f"lifetime_30_90_{s}"] = round(lifetime_risk(inc[s], s), 4)
        rep[f"monotone_breaks_{s}"] = monotone_breaks(inc[s])
        rep[f"max_share_{s}"] = round(max(v for *_, v, _ in [(lo, hi, v, r) for lo, hi, v, r in share[s]]), 4)
        rep[f"share_by_band_{s}"] = {f"{lo}-{hi}": round(v, 4) for lo, hi, v, _ in share[s]}
    report[oid] = rep
    return o


def split_sex(both, k, scale):
    """both: [(lo,hi,r,raw)], k = rate_M/rate_F -> {M: [...], F: [...]}, equal person-time assumed."""
    f = 2 / (1 + k)
    return {"F": [(lo, hi, r * f * scale, raw) for lo, hi, r, raw in both],
            "M": [(lo, hi, r * f * k * scale, raw) for lo, hi, r, raw in both]}


def build_all():
    report = {}
    outs = {}
    nat = scalars("cancer_national_2022_asr", "national_2022_level")
    for oid, c in CANCERS.items():
        outs[oid] = build_cancer(oid, c, nat, report)

    # prostate: 70-79 and 80+ as published; 30-69 in 5-year bands from a log-linear age curve fitted to two published
    # constraints of the same source (population-weighted mean over ages 0-59 and over 60-69), then x national factor
    used = "outcome:prostate_ca"
    js = scalars("prostate_2019_jiangsu_summary", used)
    f = nat["asir_prostate_M"] / js["asir_M"]
    raw = {(lo, hi): v for lo, hi, v, _ in age_table("prostate_2019_jiangsu", used)["M"]}
    pop = {lo: v for lo, hi, v, _ in age_table("prostate_jiangsu_population", used)["both"]}
    r059, r6069 = raw[(30, 59)], raw[(60, 69)]
    w059 = sum(v for a0, v in pop.items() if a0 < 60)
    w6069 = pop[60] + pop[65]
    five = [a0 for a0 in pop if a0 >= 20]  # ages under 20: rate taken as 0

    def curve(A, b, a0):
        return A * math.exp(b * (a0 + 2.5 - 62.5))

    lo_b, hi_b = 0.01, 1.0
    for _ in range(200):  # bisection on slope b; level A fixed by the 60-69 constraint
        b_ = (lo_b + hi_b) / 2
        A = r6069 * w6069 / sum(curve(1, b_, a0) * pop[a0] for a0 in (60, 65))
        m059 = sum(curve(A, b_, a0) * pop[a0] for a0 in five if a0 < 60) / w059
        lo_b, hi_b = (b_, hi_b) if m059 > r059 else (lo_b, b_)
    slope = b_
    bands = [(a0, a0 + 4, curve(A, slope, a0) * f, "") for a0 in range(30, 70, 5)]
    bands += [(70, 79, raw[(70, 79)] * f, ""), (80, 89, raw[(80, 89)] * f, "")]
    inc = {"M": bands}
    src = load_source("pmcid:PMC11431764")
    outs["prostate_ca"] = rec("prostate_ca", "前列腺癌", ["C61"], "M", rows_out(inc), {
        "source": f"{src['citation']} × 2022 年全国水平：{load_source(NAT)['citation']}", "source_keys": ["pmcid:PMC11431764", NAT],
        "year": 2022, "shape_year": 2019, "region": "China (age shape: Jiangsu Province)", "derived": True,
        "quality_zh": (f"未找到可逐字核对的全国或登记地区前列腺癌 5 岁组发病表。江苏省肿瘤登记地区 2019 年只给出 0–59、60–69、70–79、≥80 岁 4 组率"
                       f"（原表逐字核对）。70–79、80–89 岁直接采用；30–69 岁按 5 岁组重建：假定发病率随年龄按指数上升，"
                       f"用同一论文的两个约束拟合斜率与水平——按该文人口年龄构成加权，0–59 岁平均率等于 {r059}、60–69 岁平均率等于 {r6069}"
                       f"（20 岁以下按 0 计），得斜率 {slope:.4f}/岁（约每 {math.log(2) / slope:.1f} 年翻倍）。"
                       f"全部组再乘系数 {f:.3f} = 2022 年全国世标率 ÷ 江苏 2019 年世标率。人口构成表为男女合计，假定男性年龄构成相同；"
                       "江苏与全国的地区差别、PSA 筛查普及度差别并入系数。"),
        "inputs": {"asr_source_year": {"M": js["asir_M"]}, "asr_2022": {"M": nat["asir_prostate_M"]}, "factor": {"M": round(f, 4)},
                   "age_slope_per_year": round(slope, 5), "constraints": {"mean_0_59": r059, "mean_60_69": r6069}}},
        ["ICD10:C61"], FACTS_NOTE.format(lic=src["licence"]),
        quote=caption("pmcid:PMC11431764", 3), url=src["url"])
    chk059 = sum(curve(A, slope, a0) * pop[a0] for a0 in five if a0 < 60) / w059
    chk6069 = sum(curve(A, slope, a0) * pop[a0] for a0 in (60, 65)) / w6069
    report["prostate_ca"] = {"factor": f, "age_slope": slope, "refit_mean_0_59": round(chk059, 3), "refit_mean_60_69": round(chk6069, 3),
                             "lifetime_30_90_M": round(lifetime_risk(inc["M"], "M"), 4), "cum30_74_scaled_M": round(cum_rate(inc["M"]), 3),
                             "bands": {f"{lo}-{hi}": round(v, 2) for lo, hi, v, _ in bands}}

    # T2D
    # Clinician-diagnosed, registered T2DM (Zhejiang surveillance): matches the engine's diagnosed-code logic.
    # The biochemically defined cohorts are still verified and reported, for comparison only.
    used = "outcome:t2d"
    inc = age_table("t2d_zhejiang", used)
    cmp_age = age_table("t2d_age", "comparison:t2d")["both"]
    cmp_sex = scalars("t2d_sex", "comparison:t2d")
    s1 = load_source("pmcid:PMC6995322")
    outs["t2d"] = rec("t2d", "2 型糖尿病", ["E11"], "both", rows_out(inc), {
        "source": s1["citation"], "source_keys": ["pmcid:PMC6995322"], "year": 2017,
        "region": "China (Zhejiang Province diabetes surveillance, 90 districts, ~48 million residents)", "derived": False,
        "quality_zh": ("浙江省糖尿病监测系统 2007–2017 年登记的、由有资质的医生在当地医院与卫生服务中心诊断的 2 型糖尿病新发病例，"
                       "分性别 10 岁组平均发病率（每 10 万人年，原表逐字采用）；≥80 岁组用于 80–89 岁。"
                       "选择理由：引擎只在观测中出现诊断编码时判定“已发生”，基线应是“被诊断”的发病率；登记系统的分母是全体常住居民，"
                       "未诊断者留在分母中，与引擎口径一致。对照：按 OGTT 主动检测的 10 省随访队列为 13.1/19.9/23.5 每千人年"
                       "（18–44/45–59/≥60 岁），按空腹血糖的体检队列为 2.18/5.45/12.50/17.61/22.39 每千人年（30–39 至 ≥70 岁），"
                       "30–49 岁比本表高 3–6 倍以上，差额主要是未诊断的糖尿病（我国约一半糖尿病人未被诊断），且 10 省队列的基线与随访检测方法不同。"
                       "若引擎日后把化验达标（HbA1c ≥6.5% 或空腹血糖 ≥7.0 mmol/L）也判为“已发生”，应改用 OGTT 口径。"
                       "局限：单一省份、经济较发达；登记覆盖在 2015 年扩大，年度发病率有波动；风险项效应量多来自生化定义的队列，与“被诊断”口径存在差别。"),
        "inputs": {"comparison_biochemical_per_1000_py": {"check_up_cohort_by_age": {f"{lo}-{hi}": v for lo, hi, v, _ in cmp_age},
                                                          "ogtt_cohort_by_sex": cmp_sex}}},
        ["ICD10:E11", "ICD10:E14"], FACTS_NOTE.format(lic=s1["licence"]),
        quote=caption("pmcid:PMC6995322", 1), url=s1["url"])
    report["t2d"] = {**{f"lifetime_30_90_{s}": round(lifetime_risk(inc[s], s), 4) for s in "MF"},
                     "comparison_lifetime_30_90_checkup_FPG_F": round(lifetime_risk([(lo, hi, v * 100) for lo, hi, v, _ in cmp_age], "F"), 4)}

    # hypertension
    used = "outcome:htn"
    age = age_table("htn_chns", used)["both"]
    sx = scalars("htn_chns_sex", used)
    k = sx["rate_M"] / sx["rate_F"]
    inc = split_sex(age, k, 1000.0)
    s1 = load_source("pmcid:PMC6443580")
    outs["htn"] = rec("htn", "高血压", ["I10", "I11", "I12", "I13", "I15"], "both", rows_out(inc), {
        "source": s1["citation"], "source_keys": ["pmcid:PMC6443580"], "year": 2011,
        "region": "China (China Health and Nutrition Survey, 9 provinces)", "derived": True,
        "quality_zh": (f"中国健康与营养调查 1989–2011 年队列（5.3 万人，11.9 万人年，5208 例；血压 ≥140/90 mmHg 或服降压药）的年龄组发病率，"
                       f"按同表男女发病率之比（{sx['rate_M']}/{sx['rate_F']} = {k:.3f}）拆分男女，假定男女人时相等。"
                       "年龄组较宽：18–34 岁组用于 30–34 岁，≥65 岁组用于 65–89 岁；队列跨 22 年，早期随访的诊断阈值与测量方法与现在不同。"),
        "inputs": {"sex_ratio_M_over_F": round(k, 4), "unit_conversion": "per 100 PY × 1000"}},
        ["ICD10:I10", "ICD10:I11", "ICD10:I12", "ICD10:I13", "ICD10:I15"], FACTS_NOTE.format(lic=s1["licence"]),
        quote=caption("pmcid:PMC6443580", 1), url=s1["url"])
    report["htn"] = {"sex_ratio": k, **{f"lifetime_30_90_{s}": round(lifetime_risk(inc[s], s), 4) for s in "MF"}}

    # CHD and stroke
    sj = load_source("doi:10.1016/j.jacc.2025.08.060")
    for oid, name, icd, tag in (("chd", "冠心病", ["I20", "I21", "I22", "I23", "I24", "I25"], "chd_2023"),
                                ("stroke", "卒中", ["I60", "I61", "I62", "I63", "I64"], "stroke_2023")):
        used = f"outcome:{oid}"
        on = scalars("cvd_2023_onset", used)
        fo = on["first_onset"] / on["all_events"]
        t = age_table(tag, used, scale=fo)
        scope = ("冠心病事件口径为急性心肌梗死（I21–I22）、需血运重建的心绞痛（I20）与心脏性猝死（I46.1），不含仅门诊诊断的稳定型冠心病，"
                 "因此低于“任何冠心病诊断”的发病率；") if oid == "chd" else "卒中口径为 I60、I61、I63、I64；"
        outs[oid] = rec(oid, name, icd, "both", rows_out(t), {
            "source": sj["citation"], "source_keys": ["doi:10.1016/j.jacc.2025.08.060"], "year": 2023,
            "region": "China (national CVD surveillance, 262 sites, 30 provinces)", "derived": True,
            "quality_zh": (f"2023 年国家心血管病事件监测（262 个监测点，覆盖约 2.4 亿人）分性别年龄组发病率（论文图 1 的数值标签，PDF 文字层）。"
                           f"{scope}监测事件含复发，按全部心血管事件中首发的比例（{on['first_onset']}/{on['all_events']} = {fo:.3f}）折算为首发率，"
                           "假定各病种、各年龄组首发比例相同。25–34 岁组用于 30–34 岁，≥75 岁组用于 75–89 岁（开放组，85 岁以上可能低估）。"
                           "出版方网站拒绝脚本下载，原文摘录经网页阅读服务取得并保存在 evidence/outcomes/excerpts/。"),
            "inputs": {"first_onset_share": round(fo, 4)}},
            [f"ICD10:{x}" for x in icd], FACTS_NOTE.format(lic=sj["licence"]),
            quote="Figure 1 Incidence Rates of CVD, CHD, and Stroke by Sex and Age Groups Across 262 Surveillance Sites in China, 2023",
            url=sj["url"])
        report[oid] = {"first_onset_share": fo, **{f"lifetime_30_90_{s}": round(lifetime_risk(t[s], s), 4) for s in "MF"},
                       **{f"risk_35_80_{s}": round(lifetime_risk(t[s], s, 35, 80), 4) for s in "MF"},
                       **{f"monotone_breaks_{s}": monotone_breaks(t[s], ignore_last=False) for s in "MF"}}

    # CKD
    used = "outcome:ckd"
    ck = scalars("ckd_ckb", used)
    # The source gives <60 / 60-69 / >=70 only (supplement checked: age shares of cases, no finer rates). 30-59 is split
    # into 5-year bands with the age slope implied by the two upper bands (constant exponential slope), anchored at 60-69.
    slope = math.log(ck["age_ge70"] / ck["age_60_69"]) / 10.0
    implied_mean_age_lt60 = 65 - math.log(ck["age_60_69"] / ck["age_lt60"]) / slope
    young = [(a0, a0 + 4, ck["age_60_69"] * math.exp(slope * (a0 + 2.5 - 65))) for a0 in range(30, 60, 5)]
    bands = young + [(60, 69, ck["age_60_69"]), (70, 89, ck["age_ge70"])]
    inc = {s: [(lo, hi, r * ck[f"sex_{s}"] / ck["crude"], "") for lo, hi, r in bands] for s in "MF"}
    s1 = load_source("pmcid:PMC13156572")
    outs["ckd"] = rec("ckd", "慢性肾脏病", ["N18"], "both", rows_out(inc), {
        "source": s1["citation"], "source_keys": ["pmcid:PMC13156572"], "year": 2018,
        "region": "China (China Kadoorie Biobank, 10 areas)", "derived": True,
        "quality_zh": ("中国慢性病前瞻性研究（CKB，50 万人，30–79 岁入组，2009–2018 年，5662 例）中经住院与医保记录确认、以 ICD-10 编码的慢性肾脏病"
                       "（糖尿病肾病、高血压肾病、肾小球肾炎、慢性小管间质性肾炎、梗阻性肾病、N18 等）。"
                       "原文（含补充材料）只给出 <60、60–69、≥70 岁三组及男女两组发病率，没有更细的年龄组或年龄×性别交叉。"
                       f"30–59 岁按 5 岁组外推：假定发病率随年龄按常数指数斜率上升，斜率取 60–69 岁与 ≥70 岁两组之比（{ck['age_ge70']}/{ck['age_60_69']}，"
                       f"按相隔 10 岁计，{slope:.4f}/岁），以 60–69 岁组为锚；据此 <60 岁组平均率 {ck['age_lt60']} 对应的平均年龄为 {implied_mean_age_lt60:.1f} 岁，"
                       "与 CKB 60 岁以下随访人群的年龄分布相符，作为一致性检查。"
                       f"性别按 年龄组率 × 性别率 ÷ 总体粗率（{ck['crude']}）合成。"
                       "口径：“临床诊断并留下住院或医保记录”的慢性肾病，远低于按 eGFR<60 或蛋白尿筛查定义的发病率（约低一个数量级），"
                       "对应的风险项必须用同一口径（例如以 CKB 等就医记录结局估计的效应量），不能直接套用 eGFR 定义的效应量；"
                       "≥70 岁组用于 70–89 岁（入组最高 79 岁，高龄外推）。"),
        "inputs": {**{k2: ck[k2] for k2 in ck}, "age_slope_per_year": round(slope, 5),
                   "implied_mean_age_lt60": round(implied_mean_age_lt60, 1)}},
        ["ICD10:N18", "ICD10:E11.2", "ICD10:I12", "ICD10:N03", "ICD10:N11"], FACTS_NOTE.format(lic=s1["licence"]),
        quote=caption("pmcid:PMC13156572", 2), url=s1["url"])
    report["ckd"] = {f"lifetime_30_90_{s}": round(lifetime_risk(inc[s], s), 4) for s in "MF"}

    # MASLD
    used = "outcome:masld"
    inc = age_table("masld_songjiang", used, scale=1000.0)
    s1 = load_source("pmcid:PMC11882351")
    outs["masld"] = rec("masld", "代谢相关脂肪性肝病", ["K76.0"], "both", rows_out(inc), {
        "source": s1["citation"], "source_keys": ["pmcid:PMC11882351"], "year": 2023,
        "region": "China (Shanghai, Songjiang community cohort)", "derived": False,
        "quality_zh": ("上海松江社区成人队列（基线 2016–2017 年，随访至 2023 年，13052 名基线无 MASLD 者，约 5.7 万人年）超声脂肪肝 + 至少一项心血管代谢危险因素"
                       "定义的 MASLD 发病密度（每 100 人年，×1000 换算为每 10 万人年，数值未改）。单一城市郊区队列；18–39 岁组用于 30–39 岁，≥70 岁组用于 70–89 岁。"
                       "MASLD 可逆，同一研究报告了较高的恢复率，因此按发病率积分的“终身风险”会远高于横断面患病率，宜作为“10 年内出现”的风险解读。"),
        "inputs": {"unit_conversion": "per 100 PY × 1000"}},
        ["ICD10:K76.0", "ICD10:K75.81"], FACTS_NOTE.format(lic=s1["licence"]),
        quote=caption("pmcid:PMC11882351", 2), url=s1["url"])
    report["masld"] = {f"lifetime_30_90_{s}": round(lifetime_risk(inc[s], s), 4) for s in "MF"}
    report["masld"].update({f"risk_10y_from_50_{s}": round(lifetime_risk(inc[s], s, 50, 60), 4) for s in "MF"})

    # AD
    # Level: mainland four-region cohort (AD 8.2/1000 PY at >=65, crude). Age-sex shape: Taiwan national insurance AD
    # incidence 2010 (5-year bands from 65), scaled by 8.2 / Taiwan crude AD >=65 (2010). 60-64 = half of 65-69.
    used = "outcome:ad"
    tw = age_table("ad_taiwan_2010", used, scale=100.0)
    twc = scalars("ad_taiwan_2010_crude", used)["ad_crude_2010"]
    cn = scalars("ad_china_4region", used)
    k = cn["ad_ge65"] / twc
    inc = {}
    for s in "MF":
        rows = [(lo, hi, v * k, raw) for lo, hi, v, raw in tw[s]]
        r6569 = rows[0][2]
        inc[s] = [(30, 59, 0.0, ""), (60, 64, r6569 / 2, "")] + rows
    jc = age_table("ad_jicounty", "comparison:ad", scale=100.0)
    st, s1 = load_source("pmcid:PMC6878786"), load_source("pmid:26086181")
    outs["ad"] = rec("ad", "阿尔茨海默病", ["G30"], "both", rows_out(inc), {
        "source": f"水平：{s1['citation']}；年龄与性别形状：{st['citation']}", "source_keys": ["pmid:26086181", "pmcid:PMC6878786"],
        "year": 2010, "region": "China (level: 4 mainland regions; age-sex shape: Taiwan national health insurance)", "derived": True,
        "quality_zh": (f"水平取自中国大陆四地区分层整群抽样队列（1997 年入组 16921 名 ≥55 岁非痴呆者，随访 4.5 年，三步法诊断）："
                       f"≥65 岁 AD 粗发病率 {cn['ad_ge65']}/1000 人年（全因痴呆 {cn['dementia_ge65']}，AD 约占 {cn['ad_ge65'] / cn['dementia_ge65']:.0%}）；"
                       "该文分年龄性别的表不在公开文本中（仅摘要可逐字核对）。分年龄性别形状取台湾全民健保 2010 年 AD 新发率"
                       f"（65–69 至 ≥85 岁 5 岁组，男女分列，原表逐字核对），整体乘以 {cn['ad_ge65']} ÷ 台湾同年 ≥65 岁 AD 粗率 {twc} = {k:.3f}，"
                       "以修正健保诊断的漏报。假定两地 ≥65 岁人群年龄构成相近（台湾老龄化程度略高，系数可能略偏小）。"
                       "60–64 岁取 65–69 岁率的一半（AD 发病约每 5 岁翻倍，台湾表中 65–69→70–74 岁约 ×2），30–59 岁记为 0（早发型 AD 极少，不计入）；"
                       "≥85 岁组用于 85–89 岁。对照：天津蓟县农村小样本队列 80 岁以上 AD 为 59.31（男）/69.96（女）每千人年，"
                       "约为本表的 3–5 倍，已不再采用。这是 AD 本身，不是全因痴呆。"),
        "inputs": {"ad_ge65_mainland_per_1000": cn["ad_ge65"], "taiwan_crude_ad_ge65_2010_per_1000": twc, "factor": round(k, 4),
                   "unit_conversion": "per 1000 PY × 100",
                   "comparison_jicounty_per_100k": {s: {f"{lo}-{hi}": round(v, 1) for lo, hi, v, _ in jc[s]} for s in "MF"}}},
        ["ICD10:G30", "ICD10:F00"], FACTS_NOTE.format(lic=st["licence"]),
        quote=caption("pmcid:PMC6878786", 2), url=st["url"])
    report["ad"] = {"factor": k, **{f"lifetime_30_90_{s}": round(lifetime_risk(inc[s], s), 4) for s in "MF"},
                    **{f"comparison_jicounty_lifetime_{s}": round(lifetime_risk(jc[s], s), 4) for s in "MF"}}
    return outs, report


REGISTRY_CANCER_DEF = ("肿瘤登记报告的新发病例：医院、病理科、死因登记等多渠道收集，按 ICD-10/ICD-O-3 编码，病理或临床诊断，"
                       "含仅凭死亡证明的病例（DCO，约 1–3%）；不含筛查发现但未确诊者")
DEFINITIONS = {
    "crc": REGISTRY_CANCER_DEF + "。部位 C18–C21。",
    "lung_ca": REGISTRY_CANCER_DEF + "。部位 C33–C34。",
    "liver_ca": REGISTRY_CANCER_DEF + "。部位 C22（原发性肝癌）。",
    "gastric_ca": REGISTRY_CANCER_DEF + "。部位 C16。",
    "breast_ca": REGISTRY_CANCER_DEF + "。部位 C50，仅女性。",
    "prostate_ca": REGISTRY_CANCER_DEF + "。部位 C61；发病率受 PSA 筛查普及度影响。",
    "t2d": "医生诊断并登记的 2 型糖尿病（医院与基层卫生服务机构诊断，WHO 标准：随机血糖 ≥11.1、空腹血糖 ≥7.0 或 OGTT 2 小时 ≥11.1 mmol/L 伴症状），"
           "录入省级糖尿病监测系统；不含未被诊断的生化糖尿病。",
    "htn": "随访测量血压 ≥140/90 mmHg 或正在服用降压药（队列体检测量，含未诊断者）。",
    "chd": "监测系统收集的冠心病事件：急性心肌梗死（I21–I22，致死与非致死）、需 PCI/支架或搭桥的心绞痛（I20）、心脏性猝死（I46.1）；"
           "按首发比例折算为首发事件；不含仅门诊诊断的稳定型冠心病。",
    "stroke": "监测系统收集的卒中事件：局灶或全面脑功能障碍持续 >24 小时且无其他非血管原因，含蛛网膜下腔出血、脑出血、脑梗死、未分类卒中"
              "（I60、I61、I63、I64，致死与非致死）；按首发比例折算为首发事件；不含短暂性脑缺血发作。",
    "ckd": "住院或医保记录中以 ICD-10 编码的慢性肾脏病（糖尿病肾病、高血压肾病、肾小球肾炎、慢性小管间质性肾炎、梗阻性肾病、N18 等），"
           "即“临床诊断并就医”的慢性肾病；不是按 eGFR<60 或尿白蛋白筛查定义。",
    "masld": "腹部超声发现肝脂肪变，并至少有一项心血管代谢危险因素（超重/腰围、血糖、血压、甘油三酯、HDL 异常），排除过量饮酒等其他原因；"
             "社区队列主动超声检查发现，含无症状者。",
    "ad": "阿尔茨海默病：水平来自大陆队列的三步法诊断（筛查 → 临床评估 → 按 DSM/NINCDS-ADRDA 标准确诊），年龄形状来自健保诊断编码；"
          "不含血管性痴呆等其他类型痴呆。",
}
EXTRA = {"masld": {"report_lifetime": False,
                   "report_lifetime_why_zh": "脂肪肝可以逆转，逐年累加的终身发病风险会高估，只报告 10 年风险"}}


def finalize(oid, o):
    """Insert definition_zh after sex and keep fields owned by the engine side (EXTRA)."""
    out = {}
    for k, v in o.items():
        out[k] = v
        if k == "sex":
            out["definition_zh"] = DEFINITIONS[oid]
    out.update(EXTRA.get(oid, {}))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcribe", action="store_true", help="(re)write evidence/outcomes/*.csv from stored source text")
    a = ap.parse_args(argv)
    if a.transcribe:
        transcribe()
    outs, report = build_all()
    if VERIFY["missing"]:
        print("VERIFICATION FAILED:", *VERIFY["missing"], sep="\n  ")
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for oid, o in outs.items():
        (OUT_DIR / f"{oid}.json").write_text(json.dumps(finalize(oid, o), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for key, checks in CHECKS_BY_SOURCE.items():
        p = SRC_DIR / (safe_key(key) + ".json")
        s = json.loads(p.read_text(encoding="utf-8"))
        uniq = {(c["term"], c["number"], c["context"]): c for c in checks}
        s["checks"] = sorted(uniq.values(), key=lambda c: (c["term"], c["context"]))
        p.write_text(json.dumps(s, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    summary = {"generated": TODAY, "wpp_year": WPP_YEAR,
               "reference_points_not_used_in_build": {
                   "henan_2020_lifetime_risk_pct": {"lung_M": 8.73, "breast_F": 4.14, "stomach_M": 5.08, "prostate_M": 1.24,
                                                    "colorectal_both": 2.55, "liver_M": 3.47,
                                                    "source": "Chen Q et al. JNCC 2024, PMC12010400 (55 registries, one province)"},
                   "cmcs_stroke_lifetime_to_80_from_35_pct": {"M": 18.0, "F": 14.7, "source": "Chinese Multi-Provincial Cohort, PMC5106079"},
                   "hong_kong_t2d_lifetime_from_20_pct": {"M": 65.1, "F": 66.6, "source": "PLOS Med 2022 doi:10.1371/journal.pmed.1004045"}},
               "verification": {"transcribed_values_checked": VERIFY["checked"], "found_verbatim": VERIFY["found"],
                                "per_source": {k: {"checked": len(v), "found": sum(c["found"] for c in v)} for k, v in CHECKS_BY_SOURCE.items()}},
               "sanity": report}
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(summary, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    print(f"verification: {VERIFY['found']}/{VERIFY['checked']} transcribed values found verbatim in stored source text")
    for k, v in summary["verification"]["per_source"].items():
        print(f"  {k:34s} {v['found']}/{v['checked']}")
    print("sanity (lifetime risk 30->90 with WPP 2022 competing mortality; cum = registry cumulative rate %):")
    for oid, r in report.items():
        keep = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if not k.startswith("share_by_band")}
        print(f"  {oid:10s} {keep}")
    print(f"wrote {len(outs)} outcomes -> {OUT_DIR.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
