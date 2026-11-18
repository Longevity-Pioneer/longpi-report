"""Standardised observations (engine 1.1.2): every input as {code, value, unit, datetime, method, flags, ...}.

Two sources, merged:
  1. person.json fields (labs, vitals, anthropometrics, fitness, lifestyle, conditions, family history, screenings,
     imaging measures, medications, wearables) converted with data/observation_codes.json;
  2. an observations.json written by the omics layer or the reading step (person.json: "observations_file").

Validity rules (PRD §2.1c), applied per term by lp.terms:
  - method precedence  lab > tool > vendor > device > self_report; same rank -> most recent
  - flags              treated / acute_illness / pregnancy / post_exercise / non_fasting / antibiotics_3m / transfusion
  - treated            a value measured while on a drug class that lowers it is flagged `treated`
The 1.1.1 domains keep reading person.json directly (lp.engine.collect_inputs); this module feeds the new terms,
disease risk and the 120 Index only.
"""
from __future__ import annotations

import json
import statistics
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from . import units as U

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
METHOD_RANK = {"lab": 5, "tool": 4, "vendor": 3, "device": 2, "self_report": 1}
FLAGS = ("treated", "acute_illness", "pregnancy", "post_exercise", "non_fasting", "antibiotics_3m", "transfusion")


@lru_cache(maxsize=1)
def codes() -> dict:
    return json.loads((DATA_DIR / "observation_codes.json").read_text(encoding="utf-8"))


def _d(s) -> date:
    from .engine import parse_date
    return parse_date(s)


def _num(v):
    if isinstance(v, (list, tuple)):
        return v[0], (v[1] if len(v) > 1 else None)
    if isinstance(v, dict):
        return v.get("value"), v.get("unit")
    return v, None


def _treated_windows(person: dict) -> Dict[str, List[tuple]]:
    """code -> [(start, end)] while a drug class that lowers it was taken."""
    tm = codes()["medications"]["treated_map"]
    out: Dict[str, List[tuple]] = {}
    for med in person.get("medications") or []:
        cls = med.get("class")
        if cls not in tm or not med.get("since"):
            continue
        start = _d(med["since"])
        end = _d(med["until"]) if med.get("until") else date(9999, 1, 1)
        for c in tm[cls]:
            out.setdefault(c, []).append((start, end))
    return out


def from_person(person: dict, derived: Optional[dict] = None) -> List[dict]:
    cm = codes()
    obs: List[dict] = []
    tw = _treated_windows(person)

    def add(code, value, unit, when, method, src, flags=None, **kw):
        if value is None:
            return
        fl = list(flags or [])
        if when is not None and code in tw and any(a <= when <= b for a, b in tw[code]):
            fl.append("treated")
        obs.append(dict({"obs_id": f"p{len(obs)}", "code": code, "value": value, "unit": unit,
                         "datetime": when.isoformat() if when else None, "method": method, "source_file": src,
                         "flags": sorted(set(fl)), "sd": None, "tool": None, "vendor_derived": False}, **kw))

    for l in person.get("labs", []):
        d = _d(l["date"])
        fl = list(l.get("flags") or [])
        if l.get("clock_exclude") is True and "acute_illness" not in fl:
            fl.append("acute_illness")
        for k, v in (l.get("items") or {}).items():
            if k not in cm["labs"]:
                continue
            code, unit = cm["labs"][k]
            x, u = _num(v)
            if x is None:
                continue
            try:
                x = U.to_canonical(k, float(x), u)
            except Exception:   # unknown unit spelling: keep as given, the term's unit check decides
                x = float(x)
            add(code, x, unit, d, "lab", l.get("source", "体检"), fl)
    for v in person.get("vitals", []):
        d = _d(v["date"])
        meth = "lab" if v.get("setting", "office") == "office" else "device"
        for k, (code, unit) in cm["vitals"].items():
            if v.get(k) is not None:
                add(code, float(v[k]), unit, d, meth, "生命体征")
    for a in person.get("anthropometrics", []):
        d = _d(a["date"])
        for k, (code, unit) in cm["anthropometrics"].items():
            if a.get(k) is not None:
                add(code, float(a[k]), unit, d, "lab", "体格测量")
        if a.get("bmi") is None and a.get("height_cm") and a.get("weight_kg"):
            add("LOINC:39156-5", a["weight_kg"] / (a["height_cm"] / 100) ** 2, "kg/m2", d, "lab", "体格测量（身高体重计算）")
    for f in person.get("fitness", []):
        d = _d(f["date"])
        for k, (code, unit) in cm["fitness"].items():
            if f.get(k) is not None:
                add(code, float(f[k]), unit, d, "lab" if f.get("method") == "cpet" or k == "grip_kg" else "device", "体能测试")
    w = (derived or {}).get("wearables", {})
    as_of = _d(person["as_of"])
    for k, (code, unit) in cm["wearables"].items():
        if w.get(k) is not None:
            add(code, float(w[k]), unit, as_of, "device", "可穿戴设备", sustained_weeks=w.get(k + "_sustained_weeks"))
    ls = person.get("lifestyle") or {}
    sm = ls.get("smoking") or {}
    if sm.get("status") in ("never", "former", "current"):
        add("LP:smoking_status", sm["status"], "category", as_of, "self_report", "问卷")
    al = ls.get("alcohol") or {}
    gw = al.get("grams_per_week", 7 * al["grams_per_day"] if al.get("grams_per_day") is not None else None)
    if gw is not None:
        add("LP:alcohol_g_week", float(gw), "g/week", as_of, "self_report", "问卷")
    for key, code in (("mvpa_min_week", "LP:mvpa_min_week"), ("resistance_sessions_week", "LP:resistance_sessions_week")):
        v = ls.get(key)
        if isinstance(v, dict) and v.get("value") is not None:
            weeks = None
            if v.get("since"):
                weeks = max(0, (as_of - _d(v["since"])).days // 7)
            add(code, float(v["value"]), "", as_of, "self_report", "问卷", sustained_weeks=weeks)
    for c in person.get("conditions") or []:
        if c.get("icd10"):
            when = _d(str(c["diagnosed"])) if c.get("diagnosed") else None
            add("ICD10:" + str(c["icd10"]).upper(), 1, "", when, "self_report" if not c.get("source") else "lab", "已确诊疾病")
    for fh in person.get("family_history") or []:
        if fh.get("disease_id") and fh.get("relation") in ("father", "mother", "brother", "sister", "son", "daughter", "sibling", "parent", "child"):
            add("LP:fh:" + fh["disease_id"], 1, "", None, "self_report", "家族史",
                age_at_dx=fh.get("age_at_dx"), relation=fh.get("relation"))
    for s in person.get("screenings") or []:
        if s.get("test") and s.get("date"):
            d = _d(s["date"])
            add("LP:screen." + s["test"], round((as_of - d).days / 365.25, 2), "years_since", d,
                "lab" if s.get("report") else "self_report", "筛查记录", result=s.get("result"))
    for im in person.get("imaging") or []:
        for k, v in (im.get("measures") or {}).items():
            code = "LP:" + k
            if code in cm["lp_codes"]:
                add(code, float(v), "", _d(im["date"]), "lab", im.get("type", "影像"))
    return obs


CORE_INPUT_KEYS = {"labs": ("albumin", "creatinine", "glucose", "glucose_fasting", "crp", "lymph_pct", "mcv", "rdw", "alp", "wbc", "ldl", "hba1c"),
                   "vitals": ("sbp", "pulse"), "anthropometrics": ("height_cm", "weight_kg", "bmi"), "fitness": ("vo2max", "grip_kg"),
                   "wearables": ("rhr_30d", "sleep_h_median", "vo2max_recent")}


def core_codes() -> List[str]:
    """Codes the 1.1.1 model already reads from person.json (not 'unbuilt' even without an ext term)."""
    cm = codes()
    return [cm[sec][k][0] for sec, keys in CORE_INPUT_KEYS.items() for k in keys if k in cm[sec]]


def load_file(person: dict, base: Optional[Path]) -> dict:
    f = person.get("observations_file")
    if not f:
        return {}
    p = Path(f) if Path(f).is_absolute() or base is None else Path(base) / f
    doc = json.loads(p.read_text(encoding="utf-8"))
    if doc.get("schema") != "longpi.observations/1":
        raise ValueError(f"{p}: schema 必须是 longpi.observations/1")
    return doc


class Observations:
    """All observations of one person, indexed by code."""

    def __init__(self, person: dict, derived: Optional[dict] = None, base: Optional[Path] = None):
        self.person = person
        self.doc = load_file(person, base)
        self.items = from_person(person, derived) + [dict(o, obs_id=o.get("obs_id") or f"f{i}")
                                                     for i, o in enumerate(self.doc.get("observations", []))]
        self.genetics = self.doc.get("genetics") or {}
        self.provenance = self.doc.get("provenance") or []
        self.by_code: Dict[str, List[dict]] = {}
        for o in self.items:
            self.by_code.setdefault(o["code"], []).append(o)

    def has(self, code: str) -> bool:
        return code in self.by_code

    def series(self, code: str, at: date, methods: Optional[List[str]] = None, exclude_flags=(),
               max_years: float = 10.0) -> List[dict]:
        """Usable observations of `code` up to `at`, best method only (precedence), oldest first."""
        rows = []
        for o in self.by_code.get(code, []):
            when = _d(o["datetime"]) if o.get("datetime") else None
            if when is not None and (when > at or (at - when).days > max_years * 365.25):
                continue
            if methods and o.get("method") not in methods:
                continue
            if any(f in exclude_flags for f in o.get("flags") or []):
                continue
            rows.append(o)
        if not rows:
            return []
        best = max(METHOD_RANK.get(o.get("method"), 0) for o in rows)
        rows = [o for o in rows if METHOD_RANK.get(o.get("method"), 0) == best]
        return sorted(rows, key=lambda o: o.get("datetime") or "")

    def conflicts(self, code: str, at: date, tol_sd: float) -> Optional[dict]:
        """Latest value of each method; flagged when two differ by more than 2 x tol_sd."""
        latest = {}
        for o in self.by_code.get(code, []):
            if o.get("datetime") and _d(o["datetime"]) > at:
                continue
            m = o.get("method")
            if m not in latest or (o.get("datetime") or "") > (latest[m].get("datetime") or ""):
                latest[m] = o
        nums = {m: o["value"] for m, o in latest.items() if isinstance(o.get("value"), (int, float))}
        if len(nums) < 2 or tol_sd <= 0:
            return None
        lo, hi = min(nums.values()), max(nums.values())
        if hi - lo > 2 * tol_sd:
            return {"code": code, "values": nums}
        return None


def weekly(rows: List[dict]) -> List[dict]:
    """Dense series (wearables, CGM) -> weekly means with sd/sqrt(n)."""
    buckets: Dict[str, List[dict]] = {}
    for o in rows:
        d = _d(o["datetime"])
        key = (d - timedelta(days=d.weekday())).isoformat()
        buckets.setdefault(key, []).append(o)
    out = []
    for k in sorted(buckets):
        vals = [float(o["value"]) for o in buckets[k]]
        sd = statistics.pstdev(vals) / max(1, len(vals)) ** 0.5 if len(vals) > 1 else None
        out.append(dict(buckets[k][-1], value=statistics.fmean(vals), datetime=k, sd=sd, n_aggregated=len(vals)))
    return out
