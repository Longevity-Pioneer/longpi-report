#!/usr/bin/env python3
"""Assemble one analysis table from NHANES 1999-2018 and the 2019 public-use Linked Mortality Files.

Usage: nhanes_build.py <raw_dir> <out_parquet>

Rows: adults (>= 20 y at exam) eligible for mortality linkage, not pregnant.
Columns are harmonised across cycles (variable names changed between cycles).
Units follow the PhenoAge equation where relevant: albumin g/L, creatinine umol/L,
glucose mmol/L, CRP mg/dL, lymphocyte %, MCV fL, RDW %, ALP U/L, WBC 10^3/uL.
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

CYCLES = {1999: "", 2001: "_B", 2003: "_C", 2005: "_D", 2007: "_E", 2009: "_F",
          2011: "_G", 2013: "_H", 2015: "_I", 2017: "_J"}

# stem lists per cycle (same roles, different file names)
FILES = {
    "demo": ["DEMO"], "bpx": ["BPX"], "bmx": ["BMX"], "smq": ["SMQ"], "slq": ["SLQ"],
    "diq": ["DIQ"], "bpq": ["BPQ"], "mcq": ["MCQ"], "alq": ["ALQ"], "paq": ["PAQ"],
    "bio": ["BIOPRO", "L40", "LAB18"], "cbc": ["CBC", "L25", "LAB25"],
    "crp": ["CRP", "L11", "LAB11"], "hscrp": ["HSCRP"], "ghb": ["GHB", "L10", "LAB10"],
    "tc": ["TCHOL", "L13", "LAB13"], "hdl": ["HDL"], "ldl": ["TRIGLY", "L13AM", "LAB13AM"],
    "glu": ["GLU", "L10AM", "LAB10AM"], "cvx": ["CVX"], "mgx": ["MGX"],
}

VARS = {
    # demographics
    "sex": ["RIAGENDR"], "age": ["RIDAGEYR"], "race1": ["RIDRETH1"], "race3": ["RIDRETH3"],
    "preg": ["RIDEXPRG"], "wt2": ["WTMEC2YR"], "wt4": ["WTMEC4YR"], "psu": ["SDMVPSU"],
    "strata": ["SDMVSTRA"], "educ": ["DMDEDUC2"], "pir": ["INDFMPIR"],
    # PhenoAge inputs
    "albumin_gL": ["LBDSALSI"], "creat_umol": ["LBDSCRSI"], "glucose_mmol": ["LBDSGLSI"],
    "alp": ["LBXSAPSI", "LBDSAPSI"], "wbc": ["LBXWBCSI"], "lymph_pct": ["LBXLYPCT"],
    "mcv": ["LBXMCVSI"], "rdw": ["LBXRDW"], "crp_mgdl": ["LBXCRP"], "hscrp_mgl": ["LBXHSCRP"],
    # other labs
    "alt": ["LBXSATSI"], "ast": ["LBXSASSI"], "ggt": ["LBXSGTSI"], "plt": ["LBXPLTSI"],
    "hba1c": ["LBXGH"], "tc": ["LBXTC"], "hdl": ["LBDHDD", "LBXHDD", "LBDHDL"],
    "ldl": ["LBDLDL"], "tg": ["LBXTR"], "fpg_mgdl": ["LBXGLU"], "fast_wt": ["WTSAF2YR"],
    # exam
    "sbp1": ["BPXSY1"], "sbp2": ["BPXSY2"], "sbp3": ["BPXSY3"], "sbp4": ["BPXSY4"],
    "dbp1": ["BPXDI1"], "dbp2": ["BPXDI2"], "dbp3": ["BPXDI3"], "dbp4": ["BPXDI4"],
    "pulse60": ["BPXPLS"], "bmi": ["BMXBMI"], "waist": ["BMXWAIST"], "height": ["BMXHT"],
    "weight": ["BMXWT"],
    # questionnaires
    "smq020": ["SMQ020"], "smq040": ["SMQ040"], "sleep_h": ["SLD010H", "SLD012"],
    "diq010": ["DIQ010"], "diq050": ["DIQ050"], "diq070": ["DIQ070"],
    "bpq020": ["BPQ020"], "bpq050a": ["BPQ050A"],
    "chf": ["MCQ160B"], "chd": ["MCQ160C"], "mi": ["MCQ160E"], "stroke": ["MCQ160F"], "cancer": ["MCQ220"],
    # fitness and strength
    "vo2max": ["CVDESVO2", "CVDVOMAX"], "grip_sum": ["MGDCGSZ"],
}
GRIP_TRIALS = [f"MGXH{h}T{t}" for h in (1, 2) for t in (1, 2, 3)]


def read_xpt(path: Path) -> pd.DataFrame:
    df = pd.read_sas(path, format="xport", encoding="latin-1")
    df["SEQN"] = df["SEQN"].astype(int)
    return df.set_index("SEQN")


def load_cycle(raw: Path, year: int) -> pd.DataFrame:
    suf = CYCLES[year]
    folder = raw / "nhanes" / str(year)
    parts = []
    for role, stems in FILES.items():
        for stem in stems:
            f = folder / f"{stem}{suf}.xpt"
            if f.exists():
                parts.append(read_xpt(f))
                break
    df = parts[0]
    for p in parts[1:]:
        dup = [c for c in p.columns if c in df.columns]
        df = df.join(p.drop(columns=dup), how="left")
    out = pd.DataFrame(index=df.index)
    for name, cands in VARS.items():
        col = next((c for c in cands if c in df.columns), None)
        out[name] = df[col] if col else np.nan
    trials = [c for c in GRIP_TRIALS if c in df.columns]
    out["grip_max"] = df[trials].max(axis=1) if trials else np.nan
    out["cycle"] = year
    return out


def load_mortality(raw: Path, year: int) -> pd.DataFrame:
    span = f"{year}_{year + 1}"
    f = raw / "nhanes_mort" / f"NHANES_{span}_MORT_2019_PUBLIC.dat"
    recs = []
    for line in f.read_text().splitlines():
        if not line.strip():
            continue
        seqn = int(line[0:6])
        num = lambda s: int(s) if s.strip().isdigit() else np.nan  # '.' marks missing
        elig, mort, ucod, pexm = line[14:15], line[15:16], line[16:19].strip(), line[45:48]
        recs.append((seqn, num(elig), num(mort), ucod if ucod.isdigit() else None, num(pexm)))
    return pd.DataFrame(recs, columns=["SEQN", "eligstat", "mortstat", "ucod", "permth_exm"]).set_index("SEQN")


def main() -> int:
    raw, out = Path(sys.argv[1]), Path(sys.argv[2])
    frames = []
    for year in CYCLES:
        df = load_cycle(raw, year).join(load_mortality(raw, year), how="left")
        frames.append(df)
        print(year, df.shape, "eligible adults:", int(((df.age >= 20) & (df.eligstat == 1)).sum()))
    d = pd.concat(frames)
    d = d[(d.age >= 20) & (d.eligstat == 1) & (d.permth_exm.notna())]
    d = d[~(d.preg == 1)]
    d["male"] = (d.sex == 1).astype(int)
    # 20-year MEC weight: 4-year weights for 1999-2002, 2-year weights after (NCHS analytic guidelines)
    d["wt_mec"] = np.where(d.cycle <= 2001, d.wt4 * 2 / 10, d.wt2 / 10)
    d["sbp"] = d[["sbp1", "sbp2", "sbp3", "sbp4"]].replace(0, np.nan).mean(axis=1)
    d["dbp"] = d[["dbp1", "dbp2", "dbp3", "dbp4"]].replace(0, np.nan).mean(axis=1)
    d["crp_mgdl_h"] = d.crp_mgdl.where(d.crp_mgdl.notna(), d.hscrp_mgl / 10.0)
    d["years"] = d.permth_exm / 12.0
    d["died"] = (d.mortstat == 1).astype(int)
    d["smoke"] = np.select([d.smq020 == 2, (d.smq020 == 1) & (d.smq040 == 3),
                            (d.smq020 == 1) & d.smq040.isin([1, 2])], ["never", "former", "current"], default="")
    d["diabetes_dx"] = (d.diq010 == 1).astype(float).where(d.diq010.isin([1, 2, 3]))
    d["asian"] = (d.race3 == 6).astype(int)
    d.to_parquet(out)
    print("final", d.shape, "deaths", int(d.died.sum()), "person-years", round(d.years.sum()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
