"""Readers and daily summaries for wearable, CGM and home blood-pressure data.

Supported inputs
  * Apple Health export.xml (streamed; multi-GB files are fine)
  * a generic daily CSV:  date,metric,value[,source]   (metrics: steps, sleep_h, rhr, hrv,
    vo2max, weight, body_fat, walking_speed, sbp, dbp)
  * CGM CSV (LibreView, Dexcom Clarity, Sibionics-style): timestamp + glucose columns auto-detected
  * home BP CSV: datetime,sbp,dbp[,pulse]

Everything is reduced to per-day series so the engine sees one shape.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import re
from xml.parsers import expat
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HK = {
    "HKQuantityTypeIdentifierStepCount": "steps",
    "HKQuantityTypeIdentifierRestingHeartRate": "rhr",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv",
    "HKQuantityTypeIdentifierVO2Max": "vo2max",
    "HKQuantityTypeIdentifierBodyMass": "weight",
    "HKQuantityTypeIdentifierBodyFatPercentage": "body_fat",
    "HKQuantityTypeIdentifierWalkingSpeed": "walking_speed",
    "HKQuantityTypeIdentifierBloodPressureSystolic": "sbp",
    "HKQuantityTypeIdentifierBloodPressureDiastolic": "dbp",
    "HKQuantityTypeIdentifierBloodGlucose": "glucose",
    "HKQuantityTypeIdentifierOxygenSaturation": "spo2",
    "HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances": "breathing_dist",
    "HKQuantityTypeIdentifierRespiratoryRate": "resp_rate",
}
WORKOUT_ZH = {"Walking": "步行", "Running": "跑步", "Cycling": "骑车", "Elliptical": "椭圆机", "Swimming": "游泳", "Hiking": "徒步",
              "TraditionalStrengthTraining": "力量训练", "FunctionalStrengthTraining": "功能性力量训练", "CoreTraining": "核心训练",
              "HighIntensityIntervalTraining": "高强度间歇", "Yoga": "瑜伽", "Pilates": "普拉提", "Rowing": "划船",
              "StairClimbing": "爬楼梯", "Badminton": "羽毛球", "Basketball": "篮球", "Soccer": "足球", "TableTennis": "乒乓球",
              "Tennis": "网球", "Dance": "舞蹈", "MindAndBody": "身心训练", "Flexibility": "柔韧训练", "Other": "其他"}
ASLEEP = {
    "HKCategoryValueSleepAnalysisAsleep", "HKCategoryValueSleepAnalysisAsleepUnspecified",
    "HKCategoryValueSleepAnalysisAsleepCore", "HKCategoryValueSleepAnalysisAsleepDeep",
    "HKCategoryValueSleepAnalysisAsleepREM",
}
SUM_METRICS = {"steps"}


_NUMERIC_DMY = re.compile(r"\s*(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})\b")


def _parse_dt(s: str, order: Optional[str] = None) -> datetime:
    """Parse a timestamp. Year-first forms are unambiguous; for 24-10-2026 / 10/24/2026 style stamps
    pass order="dmy" or "mdy" (decided once per file by _numeric_date_order)."""
    s = s.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=None)
        except ValueError:
            continue
    m = _NUMERIC_DMY.match(s)
    if m and order in ("dmy", "mdy"):
        a, b, y = (int(g) for g in m.groups())
        day, month = (a, b) if order == "dmy" else (b, a)
        rest = s[m.end():].strip()
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                t = datetime.strptime(rest, fmt)
                return datetime(y, month, day, t.hour, t.minute, t.second)
            except ValueError:
                continue
    raise ValueError(f"unrecognised timestamp {s!r}")


def _numeric_date_order(stamps: Iterable[str], where: object = "") -> Optional[str]:
    """For files whose dates are dd-mm-yyyy or mm-dd-yyyy, decide which from the whole column:
    a first field above 12 means day-first, a second field above 12 means month-first."""
    firsts, seconds = [], []
    for s in stamps:
        m = _NUMERIC_DMY.match(s or "")
        if m:
            firsts.append(int(m.group(1)))
            seconds.append(int(m.group(2)))
    if not firsts:
        return None
    if max(firsts) > 12 and max(seconds) <= 12:
        return "dmy"
    if max(seconds) > 12 and max(firsts) <= 12:
        return "mdy"
    raise ValueError(f"{where}: cannot tell whether dates are day-month-year or month-day-year; "
                     "rewrite the time column as YYYY-MM-DD HH:MM")


class Daily:
    """metric -> {date: value}; sums for steps, medians for the rest."""

    def __init__(self) -> None:
        self.raw: Dict[str, Dict[date, Dict[str, List[float]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.sleep_intervals: Dict[str, List[Tuple[datetime, datetime]]] = defaultdict(list)
        self.workouts: List[Tuple[date, str, float, str]] = []   # (day, activity, minutes, source)

    def add(self, metric: str, day: date, value: float, source: str = "") -> None:
        self.raw[metric][day][source].append(value)

    def series(self, metric: str) -> Dict[date, float]:
        out = {}
        for day, by_src in self.raw.get(metric, {}).items():
            if metric in SUM_METRICS:
                # phone and watch both count steps; take the larger per-source total, never the sum
                out[day] = max(sum(v) for v in by_src.values())
            else:
                vals = [x for v in by_src.values() for x in v]
                out[day] = statistics.median(vals)
        if metric == "sleep_h" and self.sleep_intervals:
            out.update(self._sleep_series())
        return dict(sorted(out.items()))

    def _sleep_series(self) -> Dict[date, float]:
        # merge overlapping asleep intervals within each source; per night keep the longest source
        best: Dict[date, float] = {}
        for src, ivs in self.sleep_intervals.items():
            ivs = sorted(ivs)
            merged: List[List[datetime]] = []
            for a, b in ivs:
                if merged and a <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], b)
                else:
                    merged.append([a, b])
            per_night: Dict[date, float] = defaultdict(float)
            for a, b in merged:
                night = (b - timedelta(hours=12)).date() + timedelta(days=1)  # assign to wake-up morning
                per_night[night] += (b - a).total_seconds() / 3600
            for d, h in per_night.items():
                if 2.0 <= h <= 16.0 and h > best.get(d, 0):
                    best[d] = round(h, 2)
        return best

    def to_json(self) -> dict:
        raw = {m: {d.isoformat(): {src: ([sum(v)] if m in SUM_METRICS else v) for src, v in by_src.items()}
                   for d, by_src in days.items()} for m, days in self.raw.items()}
        sleep = {src: [[a.isoformat(), b.isoformat()] for a, b in ivs] for src, ivs in self.sleep_intervals.items()}
        return {"raw": raw, "sleep": sleep, "workouts": [[d.isoformat(), a, m, src] for d, a, m, src in self.workouts]}

    @classmethod
    def from_json(cls, obj: dict) -> "Daily":
        d = cls()
        for m, days in obj["raw"].items():
            for day, by_src in days.items():
                for src, vals in by_src.items():
                    d.raw[m][date.fromisoformat(day)][src].extend(vals)
        for src, ivs in obj["sleep"].items():
            d.sleep_intervals[src] = [(datetime.fromisoformat(a), datetime.fromisoformat(b)) for a, b in ivs]
        d.workouts = [(date.fromisoformat(x[0]), x[1], x[2], x[3]) for x in obj.get("workouts", [])]
        return d

    def workouts_by_month(self) -> Dict[str, Dict[str, float]]:
        out: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for d, act, mins, _ in self.workouts:
            out[d.strftime("%Y-%m")][act] += mins
        return {m: dict(v) for m, v in sorted(out.items())}

    def metrics(self) -> List[str]:
        names = set(self.raw.keys())
        if self.sleep_intervals:
            names.add("sleep_h")
        return sorted(names)


def read_apple_health(path: Path, daily: Optional[Daily] = None) -> Daily:
    """Stream export.xml with expat. No element tree is kept, so memory stays flat for multi-GB exports.

    The internal DTD at the top is skipped (nothing in the body needs it, and some iOS versions wrote
    declarations that strict parsers reject); control characters that XML 1.0 forbids are dropped.
    """
    daily = daily or Daily()

    def on_start(name: str, a: dict) -> None:
        if name == "Workout":
            try:
                mins = float(a["duration"]) * {"min": 1.0, "s": 1 / 60, "hr": 60.0}.get(a.get("durationUnit", "min"), 1.0)
                act = a.get("workoutActivityType", "").replace("HKWorkoutActivityType", "") or "Other"
                daily.workouts.append((_parse_dt(a["startDate"]).date(), WORKOUT_ZH.get(act, act), round(mins, 1), a.get("sourceName", "")))
            except (KeyError, TypeError, ValueError):
                pass
            return
        if name != "Record":
            return
        typ = a.get("type", "")
        src = a.get("sourceName", "")
        try:
            if typ == "HKCategoryTypeIdentifierSleepAnalysis":
                if a.get("value") in ASLEEP:
                    daily.sleep_intervals[src].append((_parse_dt(a["startDate"]), _parse_dt(a["endDate"])))
            elif typ in HK:
                metric = HK[typ]
                v = float(a["value"])
                unit = a.get("unit", "")
                if metric in ("body_fat", "spo2") and v <= 1.0:
                    v *= 100
                elif metric == "weight" and unit == "lb":
                    v *= 0.45359237
                elif metric == "walking_speed" and unit == "km/hr":
                    v /= 3.6
                elif metric == "walking_speed" and unit == "mi/hr":
                    v *= 0.44704
                elif metric == "glucose" and unit.lower().startswith("mg"):
                    v /= 18.016
                daily.add(metric, _parse_dt(a["startDate"]).date(), v, src)
        except (KeyError, TypeError, ValueError):
            pass

    parser = expat.ParserCreate()
    parser.StartElementHandler = on_start
    try:
        with open(path, "rb") as fh:
            parser.Parse(_strip_doctype(fh.read(1 << 20)).translate(None, _XML_BAD_BYTES), False)
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                parser.Parse(chunk.translate(None, _XML_BAD_BYTES), False)
            parser.Parse(b"", True)
    except expat.ExpatError as e:
        raise ValueError(f"{path}: not well-formed XML at line {e.lineno}, column {e.offset} ({expat.ErrorString(e.code)}); "
                         "re-export from the Health app, or repair that line and rerun") from None
    return daily


APPLE_PARSER_VERSION = 3


def read_apple_health_cached(path: Path) -> Daily:
    """read_apple_health with a sidecar cache (<export>.longpi-cache.json), reused while the export's
    size and modification time are unchanged. A multi-GB export takes minutes to read the first time."""
    path = Path(path)
    st = path.stat()
    key = {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "parser": APPLE_PARSER_VERSION}
    cache = path.with_name(path.name + ".longpi-cache.json")
    try:
        obj = json.loads(cache.read_text(encoding="utf-8"))
        if obj.get("key") == key:
            return Daily.from_json(obj["daily"])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    daily = read_apple_health(path)
    try:
        cache.write_text(json.dumps({"key": key, "daily": daily.to_json()}, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    return daily


_XML_BAD_BYTES = bytes(c for c in range(32) if c not in (9, 10, 13))
_DTD_END = re.compile(rb"\]\s*>")


def _strip_doctype(head: bytes) -> bytes:
    """Remove '<!DOCTYPE ... [ internal subset ]>' from the first chunk of the file."""
    i = head.find(b"<!DOCTYPE")
    if i < 0:
        return head
    gt, br = head.find(b">", i), head.find(b"[", i)
    if br != -1 and (gt == -1 or br < gt):
        m = _DTD_END.search(head, br)
        return head[:i] + head[m.end():] if m else head
    return head[:i] + head[gt + 1:] if gt != -1 else head


def read_daily_csv(path: Path, daily: Optional[Daily] = None) -> Daily:
    daily = daily or Daily()
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for r in csv.DictReader(fh):
            try:
                d = datetime.strptime(r["date"].strip()[:10], "%Y-%m-%d").date()
                daily.add(r["metric"].strip(), d, float(r["value"]), r.get("source", "") or "")
            except (KeyError, ValueError):
                continue
    return daily


# --------------------------------------------------------------------------- CGM

def read_cgm_csv(path: Path) -> List[Tuple[datetime, float]]:
    """Return [(timestamp, mmol/L)] sorted. Detects header row, columns and units."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    hdr_i, t_col, g_col = None, None, None
    for i, row in enumerate(rows[:30]):
        low = [c.strip().lower() for c in row]
        t = next((j for j, c in enumerate(low) if any(k in c for k in ("timestamp", "time", "时间", "date"))), None)
        g = next((j for j, c in enumerate(low) if any(k in c for k in ("glucose", "血糖", "historic", "sgv"))), None)
        if t is not None and g is not None:
            hdr_i, t_col, g_col = i, t, g
            break
    if hdr_i is None:
        raise ValueError("cannot find timestamp and glucose columns")
    body = [r for r in rows[hdr_i + 1:] if len(r) > max(t_col, g_col)]
    order = _numeric_date_order([r[t_col] for r in body], path)
    out = []
    for row in body:
        try:
            out.append((_parse_dt(row[t_col], order), float(row[g_col])))
        except ValueError:
            continue
    if not out:
        return out
    if statistics.median(v for _, v in out) > 30:  # mg/dL
        out = [(t, v / 18.016) for t, v in out]
    return sorted(out)


def cgm_metrics(pts: List[Tuple[datetime, float]]) -> dict:
    vals = [v for _, v in pts]
    if len(vals) < 96:
        return {}
    mean = statistics.fmean(vals)
    sd = statistics.pstdev(vals)
    mg = mean * 18.016
    days = (pts[-1][0] - pts[0][0]).total_seconds() / 86400
    return {
        "days": round(days, 1),
        "n": len(vals),
        "mean": round(mean, 2),
        "sd": round(sd, 2),
        "cv_pct": round(100 * sd / mean, 1),
        "gmi_pct": round(3.31 + 0.02392 * mg, 2),  # Bergenstal 2018, Diabetes Care
        "tir_3_9_10_pct": round(100 * sum(3.9 <= v <= 10.0 for v in vals) / len(vals), 1),
        "titr_3_9_7_8_pct": round(100 * sum(3.9 <= v <= 7.8 for v in vals) / len(vals), 1),
        "below_3_9_pct": round(100 * sum(v < 3.9 for v in vals) / len(vals), 1),
        "above_7_8_pct": round(100 * sum(v > 7.8 for v in vals) / len(vals), 1),
        "fasting_like": round(statistics.median(v for t, v in pts if 4 <= t.hour < 6), 2) if any(4 <= t.hour < 6 for t, _ in pts) else None,
    }


def cgm_meal_peaks(pts: List[Tuple[datetime, float]], meals: Iterable[Tuple[datetime, str]]) -> List[dict]:
    """Peak and rise within 2 h after each logged meal (baseline = value at meal time)."""
    out = []
    for mt, label in meals:
        base = [v for t, v in pts if abs((t - mt).total_seconds()) <= 15 * 60]
        win = [v for t, v in pts if mt <= t <= mt + timedelta(hours=2)]
        if base and win:
            out.append({"time": mt.isoformat(sep=" ", timespec="minutes"), "meal": label,
                        "peak": round(max(win), 2), "rise": round(max(win) - base[0], 2)})
    return out


# --------------------------------------------------------------------------- home BP

def read_bp_csv(path: Path) -> List[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    stamp = lambda r: r.get("datetime") or r.get("time") or r.get("date") or ""
    order = _numeric_date_order((stamp(r) for r in rows), path)
    out = []
    for r in rows:
        try:
            out.append({"t": _parse_dt(stamp(r), order), "sbp": float(r["sbp"]), "dbp": float(r["dbp"]),
                        "pulse": float(r["pulse"]) if r.get("pulse") else None})
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(out, key=lambda x: x["t"])


def home_bp_summary(readings: List[dict], end: date, days: int = 28) -> Optional[dict]:
    """Mean of the last `days` days (guideline-style home BP average; first day discarded)."""
    sel = [r for r in readings if end - timedelta(days=days) < r["t"].date() <= end]
    if len(sel) < 6:
        return None
    first_day = min(r["t"].date() for r in sel)
    sel2 = [r for r in sel if r["t"].date() != first_day] or sel
    morning = [r for r in sel2 if r["t"].hour < 12]
    evening = [r for r in sel2 if r["t"].hour >= 12]
    f = lambda rs, k: round(statistics.fmean(r[k] for r in rs), 1) if rs else None
    return {"n": len(sel2), "sbp": f(sel2, "sbp"), "dbp": f(sel2, "dbp"),
            "morning_sbp": f(morning, "sbp"), "evening_sbp": f(evening, "sbp"),
            "from": min(r["t"].date() for r in sel2).isoformat(), "to": max(r["t"].date() for r in sel2).isoformat()}


# --------------------------------------------------------------------------- summaries

def recent_window(series: Dict[date, float], end: date, days: int) -> List[float]:
    start = end - timedelta(days=days)
    return [v for d, v in series.items() if start < d <= end]


def monthly_median(series: Dict[date, float]) -> List[Tuple[str, float]]:
    by: Dict[str, List[float]] = defaultdict(list)
    for d, v in series.items():
        by[d.strftime("%Y-%m")].append(v)
    return [(m, statistics.median(v)) for m, v in sorted(by.items())]


def coverage_spans(days: Iterable[date], max_gap_days: int = 45) -> List[Tuple[str, str]]:
    ds = sorted(set(days))
    if not ds:
        return []
    spans, a, prev = [], ds[0], ds[0]
    for d in ds[1:]:
        if (d - prev).days > max_gap_days:
            spans.append((a.strftime("%Y-%m"), prev.strftime("%Y-%m")))
            a = d
        prev = d
    spans.append((a.strftime("%Y-%m"), prev.strftime("%Y-%m")))
    return spans


def slope_per_year(series: Dict[date, float], end: date, days: int) -> Optional[float]:
    pts = [((d - end).days / 365.25, v) for d, v in series.items() if (end - d).days < days]
    if len(pts) < 10:
        return None
    mx = statistics.fmean(p[0] for p in pts)
    my = statistics.fmean(p[1] for p in pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    if sxx <= 0:
        return None
    return sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
