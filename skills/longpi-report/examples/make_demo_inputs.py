#!/usr/bin/env python3
"""Generate the synthetic demo person D01 (fixed seed). Every value is invented.

Writes examples/demo_person.json and examples/demo/{daily.csv, cgm.csv, bp.csv}.
The shape follows the original LongPi demo page: an office worker, 38, never smoked,
LDL and blood pressure drifting up, hs-CRP falling, aerobic training since June 2026.
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "demo"
rng = random.Random(20261023)


def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def steps_level(d: date) -> float:
    y = d.year + (d.timetuple().tm_yday - 1) / 365.25
    if y < 2020:
        return 9000
    if y < 2022.9:
        return 9000 - (y - 2020) / 2.9 * 2900          # down to ~6,100
    if y < 2026.0:
        return 6300 + (y - 2022.9) / 3.1 * 700
    return 7000 + min(1, (y - 2026.0) / 0.8) * 1400    # back to ~8,400


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    as_of = date(2026, 10, 20)
    rows = []
    for d in daterange(date(2018, 1, 1), as_of):
        wk = d.weekday() >= 5
        s = steps_level(d) * (0.85 if wk else 1.05) * math.exp(rng.gauss(0, 0.28))
        rows.append((d.isoformat(), "steps", round(s), "iPhone"))
    watch = list(daterange(date(2021, 3, 1), date(2023, 8, 31))) + list(daterange(date(2026, 4, 1), as_of))
    for d in watch:
        wk = d.weekday() >= 5
        new = d >= date(2026, 4, 1)
        train = max(0.0, (d - date(2026, 6, 1)).days / 140) if new else 0.0
        train = min(train, 1.0)
        if rng.random() < 0.94:
            rows.append((d.isoformat(), "sleep_h", round(min(9.8, max(4.6, rng.gauss(7.55 if wk else 6.95, 0.62))), 2), "Watch"))
        rhr = (69 - 5 * train if new else 67) + rng.gauss(0, 1.6)
        rows.append((d.isoformat(), "rhr", round(rhr), "Watch"))
        hrv = (32 + 6 * train if new else 34) + (3 if wk else 0) + rng.gauss(0, 4)
        rows.append((d.isoformat(), "hrv", round(max(15, hrv), 1), "Watch"))
        if d.weekday() == 2:
            vo = (34 + 3 * train if new else 35.5) + rng.gauss(0, 0.5)
            rows.append((d.isoformat(), "vo2max", round(vo, 1), "Watch"))
    with open(OUT / "daily.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "metric", "value", "source"])
        w.writerows(rows)

    # 14-day CGM, 15-minute readings, three meal peaks; walk after dinner on some days
    meals = []
    with open(OUT / "cgm.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["timestamp", "glucose_mmol_l"])
        for day in range(14):
            d0 = datetime(2026, 10, 1) + timedelta(days=day)
            walk = rng.random() < 0.5
            mt = {"早餐": d0 + timedelta(hours=7, minutes=30 + rng.randint(-15, 15)),
                  "午餐": d0 + timedelta(hours=12, minutes=20 + rng.randint(-15, 20)),
                  "晚餐": d0 + timedelta(hours=18, minutes=40 + rng.randint(-20, 20))}
            amp = {"早餐": rng.gauss(2.0, 0.4), "午餐": rng.gauss(3.1, 0.5), "晚餐": rng.gauss(2.4 - (0.9 if walk else 0), 0.4)}
            for k, t in mt.items():
                meals.append({"time": t.strftime("%Y-%m-%d %H:%M"), "label": k + ("（饭后散步）" if k == "晚餐" and walk else "")})
            for i in range(96):
                t = d0 + timedelta(minutes=15 * i)
                g = 5.0 + 0.25 * math.sin(2 * math.pi * (i / 96)) + rng.gauss(0, 0.12)
                for k, m in mt.items():
                    dt = (t - m).total_seconds() / 3600
                    if 0 <= dt <= 3:
                        g += amp[k] * (dt / 0.75) * math.exp(1 - dt / 0.75)
                if t.hour < 6:
                    g -= 0.1
                w.writerow([t.strftime("%Y-%m-%d %H:%M"), round(g, 1)])

    # home blood pressure: morning and evening; early readings noisier (posture), slow decline in 2026
    with open(OUT / "bp.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["datetime", "sbp", "dbp", "pulse"])
        for d in daterange(date(2025, 6, 1), as_of):
            if rng.random() < 0.25:
                continue
            frac = (d - date(2025, 6, 1)).days / (as_of - date(2025, 6, 1)).days
            sbp0 = 136 - 4 * frac
            noise = 8 if d < date(2025, 9, 1) else 5
            for hh, extra in ((7, 1.5), (21, -1.0)):
                if rng.random() < 0.85:
                    s = sbp0 + extra + rng.gauss(0, noise)
                    w.writerow([f"{d.isoformat()} {hh:02d}:{rng.randint(0, 50):02d}", round(s), round(s * 0.635 + rng.gauss(0, 3)), round(rng.gauss(68, 5))])

    labs = [
        {"date": "2023-04-16", "source": "年度体检", "items": {
            "albumin": [46.8, "g/L"], "creatinine": [82, "umol/L"], "glucose": [5.1, "mmol/L"], "lymph_pct": [31.5, "%"],
            "mcv": [89.5, "fL"], "rdw": [13.0, "%"], "alp": [66, "U/L"], "wbc": [6.1, "10^9/L"],
            "ldl": [3.21, "mmol/L"], "hdl": [1.18, "mmol/L"], "tc": [5.02, "mmol/L"], "tg": [1.34, "mmol/L"],
            "hba1c": [5.3, "%"], "glucose_fasting": [5.1, "mmol/L"], "alt": [31, "U/L"], "ast": [24, "U/L"], "uric_acid": [398, "umol/L"],
            "platelets": [236, "10^9/L"]}},
        {"date": "2024-05-12", "source": "年度体检", "items": {
            "albumin": [45.9, "g/L"], "creatinine": [85, "umol/L"], "glucose": [5.3, "mmol/L"], "crp": [2.8, "mg/L"], "lymph_pct": [30.2, "%"],
            "mcv": [89.8, "fL"], "rdw": [12.95, "%"], "alp": [71, "U/L"], "wbc": [6.6, "10^9/L"],
            "ldl": [3.58, "mmol/L"], "hdl": [1.12, "mmol/L"], "tc": [5.41, "mmol/L"], "tg": [1.62, "mmol/L"],
            "hba1c": [5.5, "%"], "glucose_fasting": [5.3, "mmol/L"], "alt": [44, "U/L"], "ast": [29, "U/L"], "uric_acid": [421, "umol/L"],
            "vitd": [21.4, "ng/mL"], "platelets": [228, "10^9/L"]}},
        {"date": "2025-05-20", "source": "年度体检", "items": {
            "albumin": [46.4, "g/L"], "creatinine": [84, "umol/L"], "glucose": [5.2, "mmol/L"], "crp": [1.4, "mg/L"], "lymph_pct": [31.8, "%"],
            "mcv": [89.6, "fL"], "rdw": [13.0, "%"], "alp": [69, "U/L"], "wbc": [6.1, "10^9/L"],
            "ldl": [3.92, "mmol/L"], "hdl": [1.15, "mmol/L"], "tc": [5.76, "mmol/L"], "tg": [1.48, "mmol/L"],
            "hba1c": [5.6, "%"], "glucose_fasting": [5.4, "mmol/L"], "alt": [38, "U/L"], "ast": [27, "U/L"], "uric_acid": [409, "umol/L"],
            "vitd": [27.9, "ng/mL"], "platelets": [241, "10^9/L"]}},
        {"date": "2026-05-18", "source": "年度体检", "items": {
            "albumin": [47.0, "g/L"], "creatinine": [83, "umol/L"], "glucose": [5.0, "mmol/L"], "crp": [0.6, "mg/L"], "lymph_pct": [33.4, "%"],
            "mcv": [89.2, "fL"], "rdw": [12.95, "%"], "alp": [67, "U/L"], "wbc": [5.7, "10^9/L"],
            "ldl": [3.64, "mmol/L"], "hdl": [1.21, "mmol/L"], "tc": [5.51, "mmol/L"], "tg": [1.29, "mmol/L"],
            "hba1c": [5.5, "%"], "glucose_fasting": [4.9, "mmol/L"], "alt": [29, "U/L"], "ast": [23, "U/L"], "uric_acid": [392, "umol/L"],
            "vitd": [34.2, "ng/mL"], "platelets": [233, "10^9/L"], "lpa": [18, "nmol/L"]}},
    ]
    person = {
        "schema": "longpi.person/1", "synthetic": True, "as_of": as_of.isoformat(),
        "person": {"code": "D01", "label": "演示用户 D01", "sex": "M", "birth": "1988-10", "region": {"north": False, "urban": True}},
        "labs": labs,
        "vitals": [{"date": "2023-04-16", "sbp": 124, "dbp": 79, "pulse": 72, "setting": "office"},
                   {"date": "2024-05-12", "sbp": 131, "dbp": 83, "pulse": 74, "setting": "office"},
                   {"date": "2025-05-20", "sbp": 136, "dbp": 86, "pulse": 73, "setting": "office"},
                   {"date": "2026-05-18", "sbp": 133, "dbp": 84, "pulse": 70, "setting": "office"}],
        "anthropometrics": [{"date": "2024-05-12", "height_cm": 175, "weight_kg": 77.5, "waist_cm": 93},
                            {"date": "2026-05-18", "height_cm": 175, "weight_kg": 76.0, "waist_cm": 92}],
        "fitness": [],
        "lifestyle": {"smoking": {"status": "never"}, "alcohol": {"grams_per_week": 50},
                      "sleep_h": 7.0, "activity_note": "2026-06 起每周有氧 ≥120 分钟", "diet_note": "工作日外卖较多"},
        "conditions": [],
        "medications": [],
        "family_history": [{"relation": "father", "condition": "高血压", "age_at_dx": 52}],
        "imaging": [{"date": "2024-05-12", "type": "腹部超声", "finding": "轻度脂肪肝"},
                    {"date": "2026-05-18", "type": "腹部超声", "finding": "肝脏回声未见明显异常"},
                    {"date": "2026-05-18", "type": "心电图", "finding": "窦性心律，正常心电图"}],
        "other_tests": [{"date": "2026-05-18", "name": "尿微量白蛋白/肌酐比", "value": "8 mg/g", "note": "正常"}],
        "genetics": {"date": "2025-02-10", "source": "消费级基因芯片（演示）",
                     "pgx": [{"gene": "CYP2C19", "result": "*1/*2", "phenotype": "中间代谢型"},
                             {"gene": "SLCO1B1", "result": "rs4149056 TC", "phenotype": "转运功能轻度降低"},
                             {"gene": "CYP2C9", "result": "*1/*1", "phenotype": "正常代谢型"},
                             {"gene": "VKORC1", "result": "-1639 AG", "phenotype": "华法林敏感性中等"}],
                     "traits": [{"name": "咖啡因代谢", "result": "CYP1A2 慢代谢型（演示）"}]},
        "methylation": [{"date": "2026-05-18", "vendor": "某厂商靶向甲基化（演示）", "clock_type": "first_generation",
                         "bio_age": 36.2, "chrono_age": 37.6,
                         "organs": {"肾": 33.9, "脑": 35.0, "肺": 35.8, "代谢": 36.4, "免疫": 37.0, "骨骼肌肉": 37.2, "心脏": 38.1, "肝": 39.6, "血管": 40.3}}],
        "wearables": {"daily_csv": "demo/daily.csv", "cgm_csv": "demo/cgm.csv", "bp_csv": "demo/bp.csv", "device": "Apple Watch（演示）"},
        "meals": meals,
    }
    (HERE / "demo_person.json").write_text(json.dumps(person, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", HERE / "demo_person.json", "and", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
