"""Turn a person file plus raw wearable/CGM/BP files into model inputs and chart series."""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from . import units, wearables as WR
from .engine import parse_date

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# analytes charted in the lab-trend panel, in display order; first match wins
LAB_PANEL = [
    ("ldl", "LDL-C"), ("hba1c", "HbA1c"), ("crp", "hs-CRP"), ("tg", "甘油三酯"), ("alt", "ALT"),
    ("vitd", "25-OH 维生素 D"), ("uric_acid", "尿酸"), ("apob", "ApoB"), ("glucose_fasting", "空腹血糖"),
    ("creatinine", "肌酐"), ("hdl", "HDL-C"), ("ast", "AST"), ("ggt", "GGT"),
]


def _lab_refs() -> dict:
    return json.loads((DATA_DIR / "lab_reference.json").read_text(encoding="utf-8"))


def normalise_labs(person: dict) -> None:
    """Convert every lab item to its canonical unit in place: items[k] = [value, unit]."""
    for l in person.get("labs", []):
        for k, v in list(l["items"].items()):
            val, unit = (v[0], v[1] if len(v) > 1 else None) if isinstance(v, list) else (v, None)
            ana = "glucose" if k == "glucose_fasting" else k
            try:
                cv = units.to_canonical(ana, float(val), unit)
            except (ValueError, TypeError):
                continue
            l["items"][k] = [round(cv, 4), units.CANONICAL.get(ana, unit or "")]


def wearable_daily(person: dict, base: Path) -> Optional[WR.Daily]:
    w = person.get("wearables", {}) or {}
    daily = None
    if w.get("apple_health_xml"):
        daily = WR.read_apple_health_cached(base / w["apple_health_xml"])
    if w.get("daily_csv"):
        daily = WR.read_daily_csv(base / w["daily_csv"], daily)
    return daily


def derive(person: dict, base: Path) -> dict:
    as_of = parse_date(person["as_of"])
    normalise_labs(person)
    out: Dict = {"wearables": {}, "data": {}}
    dw, dd = out["wearables"], out["data"]
    daily = wearable_daily(person, base)
    coverage: List[dict] = []
    if daily:
        series = {m: daily.series(m) for m in ("steps", "sleep_h", "rhr", "hrv", "vo2max", "spo2", "breathing_dist")}
        rhr30 = WR.recent_window(series["rhr"], as_of, 30)
        if len(rhr30) >= 10:
            dw["rhr_30d"] = round(statistics.median(rhr30), 1)
        sl = WR.recent_window(series["sleep_h"], as_of, 90)
        if len(sl) >= 20:
            dw["sleep_h_median"] = round(statistics.median(sl), 2)
        vo = WR.recent_window(series["vo2max"], as_of, 90)
        if vo:
            dw["vo2max_recent"] = round(statistics.median(vo), 1)
        st = WR.recent_window(series["steps"], as_of, 90)
        if len(st) >= 20:
            dw["steps_90d"] = round(statistics.median(st))
        # charts: last 200 days of daily values
        start = as_of - timedelta(days=200)
        days = sorted({d for s in series.values() for d in s if start < d <= as_of})
        dd["recent"] = [{"d": d.isoformat(), "sleep": series["sleep_h"].get(d), "rhr": series["rhr"].get(d),
                         "hrv": round(series["hrv"][d], 1) if d in series["hrv"] else None,
                         "steps": round(series["steps"][d]) if d in series["steps"] else None,
                         "vo2": series["vo2max"].get(d),
                         "spo2": round(series["spo2"][d], 1) if d in series["spo2"] else None,
                         "bd": round(series["breathing_dist"][d], 1) if d in series["breathing_dist"] else None} for d in days]
        sp = WR.recent_window(series["spo2"], as_of, 90)
        if len(sp) >= 10:
            dw["spo2_90d"] = round(statistics.median(sp), 1)
        bd = sorted(WR.recent_window(series["breathing_dist"], as_of, 90))
        if len(bd) >= 10:
            dw["breathing_dist_90d"] = {"median": round(statistics.median(bd), 1), "p90": round(bd[int(0.9 * (len(bd) - 1))], 1), "nights": len(bd)}
        wm = daily.workouts_by_month()
        if wm:
            dd["workouts_monthly"] = [{"m": m, "by": {k: round(v) for k, v in by.items()}} for m, by in list(wm.items())[-12:]]
            last90 = [w for w in daily.workouts if 0 <= (as_of - w[0]).days < 90]
            if last90:
                agg: Dict[str, float] = defaultdict(float)
                for _, act, mins, _ in last90:
                    agg[act] += mins
                dw["workouts_90d"] = {"sessions": len(last90), "minutes": round(sum(agg.values())),
                                      "by_type": {k: round(v) for k, v in sorted(agg.items(), key=lambda x: -x[1])}}
        sl200 = [r["sleep"] for r in dd["recent"] if r["sleep"] is not None]
        if sl200:
            dd["sleep_stats"] = {"n": len(sl200), "median": round(statistics.median(sl200), 2),
                                 "lt7_pct": round(100 * sum(x < 7 for x in sl200) / len(sl200), 1)}
        dd["steps_monthly"] = [{"m": m, "steps": round(v)} for m, v in WR.monthly_median(series["steps"])]
        hrv = series["hrv"]
        if len(hrv) >= 30:
            dw["hrv_60d"] = round(statistics.median(WR.recent_window(hrv, as_of, 60)), 1)
        trend = WR.slope_per_year(series["rhr"], as_of, 180)
        if trend is not None:
            dw["rhr_trend_per_year"] = round(trend, 2)
        trend = WR.slope_per_year(series["vo2max"], as_of, 365) if len(series["vo2max"]) >= 10 else None
        if trend is not None:
            dw["vo2max_trend_per_year"] = round(trend, 2)
        if series["steps"]:
            coverage.append({"src": "步数（手机/手表）", "spans": WR.coverage_spans(series["steps"].keys())})
        watch_days = set(series["rhr"]) | set(series["sleep_h"])
        if watch_days:
            coverage.append({"src": "智能手表", "spans": WR.coverage_spans(watch_days)})
    w = person.get("wearables", {}) or {}
    if w.get("cgm_csv"):
        pts = WR.read_cgm_csv(base / w["cgm_csv"])
        if pts:
            dd["cgm_metrics"] = WR.cgm_metrics(pts)
            step = max(1, len(pts) // 1500)
            dd["cgm"] = [[t.strftime("%Y-%m-%d %H:%M"), round(v, 1)] for t, v in pts[::step]]
            meals = [(datetime.strptime(m["time"], "%Y-%m-%d %H:%M"), m.get("label", "")) for m in person.get("meals", [])]
            if meals:
                dd["cgm_meals"] = WR.cgm_meal_peaks(pts, meals)
            coverage.append({"src": "CGM", "spans": WR.coverage_spans({t.date() for t, _ in pts}, 3)})
    if w.get("bp_csv"):
        bp = WR.read_bp_csv(base / w["bp_csv"])
        hb = WR.home_bp_summary(bp, as_of, 28)
        if hb:
            dw["home_bp"] = hb
        if bp:
            coverage.append({"src": "家庭血压计", "spans": WR.coverage_spans({r["t"].date() for r in bp})})
            dd["home_bp_series"] = [[r["t"].strftime("%Y-%m-%d %H:%M"), r["sbp"], r["dbp"]] for r in bp[-400:]]
    # labs panel
    refs = _lab_refs()
    labs_by: Dict[str, List] = defaultdict(list)
    for l in person.get("labs", []):
        for k, v in l["items"].items():
            labs_by[k].append((l["date"], v[0], v[1]))
    panel = {}
    for k, label in LAB_PANEL:
        pts = sorted(labs_by.get(k, []))
        if len(pts) >= 2 or (k in ("ldl", "hba1c", "crp") and pts):
            r = refs.get(k, {})
            panel[label] = {"unit": pts[0][2], "pts": [[d[:7], round(v, 2)] for d, v, _ in pts], **r}
        if len(panel) >= 6:
            break
    sbp = sorted((v["date"], v["sbp"]) for v in person.get("vitals", []) if v.get("sbp") and v.get("setting", "office") == "office")
    if len(sbp) >= 2:
        panel = {"收缩压（体检）": {"unit": "mmHg", "pts": [[d[:7], s] for d, s in sbp], "ref_hi": 130, "ref_label": "<130"}, **panel}
    dd["labs"] = dict(list(panel.items())[:6])
    # coverage of dated records
    lab_dates = [parse_date(l["date"]) for l in person.get("labs", [])]
    if lab_dates:
        coverage.insert(0, {"src": "体检化验", "spans": [(d.strftime("%Y-%m"), d.strftime("%Y-%m")) for d in sorted(set(lab_dates))]})
    g = person.get("genetics") or {}
    if g.get("date"):
        coverage.append({"src": "基因检测", "spans": [(g["date"][:7], g["date"][:7])]})
    for mth in person.get("methylation", []):
        coverage.append({"src": "血液甲基化", "spans": [(mth["date"][:7], mth["date"][:7])]})
    dd["coverage"] = [{"src": c["src"], "spans": [list(s) for s in c["spans"]]} for c in coverage]
    meth = sorted(person.get("methylation", []), key=lambda m: m["date"])
    if meth:
        m = meth[-1]
        dd["methylation"] = {"date": m["date"], "vendor": m.get("vendor", ""), "clock_type": m.get("clock_type", "unknown"),
                             "bio_age": m.get("bio_age"), "chrono": m.get("chrono_age"), "organs": m.get("organs", {})}
    return out
