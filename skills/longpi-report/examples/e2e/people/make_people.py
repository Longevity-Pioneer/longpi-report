#!/usr/bin/env python3
"""Two synthetic people for the 1.1.2 end-to-end test (fixed seed; every value invented).

P1  male, 48, urban; LDL and fasting glucose drifting up, statin since 2025-03; father CHD at 52;
    Apple Watch since 2021, steps up from ~5,000 to ~9,500 since 2026-06; FIT screening 2026-02.
P2  female, 61; hypertension (I10) on amlodipine since 2022; type 2 diabetes in mother; HBsAg positive
    (B18.1) with yearly liver ultrasound + AFP; Huawei watch, steady ~6,500 steps; coronary calcium score 35.
Omics inputs (VCF / chip, methylation, proteomics, metabolomics, metagenome) are added by the omics layer
next to these files; person.json points to observations.json written by that layer.
Writes P1/ and P2/ with person.json and daily.csv. Raw-data "documents" are the JSON fields themselves.
"""
from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
rng = random.Random(20261118)


def days(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def lab(d, **kw):
    return {"date": d, "source": "年度体检（合成）", "items": {k: list(v) for k, v in kw.items()}}


def p1() -> dict:
    labs = []
    for i, y in enumerate(range(2022, 2027)):
        ldl = 3.4 + 0.18 * i if y < 2025 else 2.4 + 0.05 * (y - 2025)
        labs.append(lab(f"{y}-05-1{i}", albumin=(46.5 - 0.2 * i, "g/L"), creatinine=(82 + i, "umol/L"),
                        glucose=(5.4 + 0.12 * i, "mmol/L"), glucose_fasting=(5.4 + 0.12 * i, "mmol/L"),
                        crp=(1.4 + 0.1 * i, "mg/L"), lymph_pct=(31 - 0.4 * i, "%"), mcv=(90.5, "fL"), rdw=(12.6 + 0.05 * i, "%"),
                        alp=(72 + i, "U/L"), wbc=(6.1 + 0.1 * i, "10^9/L"), ldl=(round(ldl, 2), "mmol/L"), hdl=(1.08, "mmol/L"),
                        tc=(round(ldl + 1.7, 2), "mmol/L"), tg=(1.7 + 0.08 * i, "mmol/L"), hba1c=(5.6 + 0.08 * i, "%"),
                        apob=(round(0.95 + 0.06 * i if y < 2025 else 0.80, 2), "g/L"), lpa=(180, "mg/L"),
                        alt=(28 + i, "U/L"), ast=(24, "U/L"), uric_acid=(410 + 5 * i, "umol/L"), platelets=(230, "10^9/L")))
    return {
        "schema": "longpi.person/1", "synthetic": True, "as_of": "2026-11-10",
        "person": {"code": "P1", "label": "P1（合成）", "sex": "M", "birth": "1978-06", "region": {"north": True, "urban": True}},
        "labs": labs,
        "vitals": [{"date": l["date"], "sbp": 128 + 2 * i, "dbp": 82 + i, "pulse": 72, "setting": "office"} for i, l in enumerate(labs)],
        "anthropometrics": [{"date": l["date"], "height_cm": 173, "weight_kg": 79 + 0.6 * i, "waist_cm": 92 + i} for i, l in enumerate(labs)],
        "fitness": [{"date": "2026-09-20", "grip_kg": 41}],
        "lifestyle": {"smoking": {"status": "former", "quit_year": 2017}, "alcohol": {"grams_per_week": 80}, "sleep_h": 6.5,
                      "resistance_sessions_week": {"value": 2, "since": "2026-07"}},
        "conditions": [{"name": "高脂血症", "icd10": "E78.5", "diagnosed": "2025"}],
        "medications": [{"name": "阿托伐他汀", "dose": "20 mg qn", "since": "2025-03", "class": "statin"}],
        "family_history": [{"relation": "father", "condition": "冠心病", "disease_id": "chd", "age_at_dx": 52}],
        "screenings": [{"test": "crc_fit", "date": "2026-02", "result": "阴性", "report": True}],
        "imaging": [{"date": "2026-05-14", "type": "腹部超声", "finding": "轻度脂肪肝"}],
        "wearables": {"device": "Apple Watch", "daily_csv": "daily.csv"},
        "genetic_preferences": {"show_opt_in": False, "secondary_findings": True},
        "observations_file": "observations.json",
    }


def p2() -> dict:
    labs = []
    for i, y in enumerate(range(2022, 2027)):
        labs.append(lab(f"{y}-04-2{i}", albumin=(43.0 - 0.3 * i, "g/L"), creatinine=(66 + 1.5 * i, "umol/L"),
                        glucose=(5.9 + 0.05 * i, "mmol/L"), glucose_fasting=(5.9 + 0.05 * i, "mmol/L"),
                        crp=(2.6, "mg/L"), lymph_pct=(29, "%"), mcv=(92, "fL"), rdw=(13.4 + 0.1 * i, "%"),
                        alp=(88 + 2 * i, "U/L"), wbc=(5.6, "10^9/L"), ldl=(3.1, "mmol/L"), hdl=(1.35, "mmol/L"),
                        tc=(5.0, "mmol/L"), tg=(1.5, "mmol/L"), hba1c=(6.0 + 0.04 * i, "%"),
                        alt=(36 + 2 * i, "U/L"), ast=(33 + i, "U/L"), platelets=(190 - 4 * i, "10^9/L"),
                        cystatin_c=(round(0.95 + 0.03 * i, 2), "mg/L")))
    labs[-1]["items"]["nt_probnp"] = [110, "pg/mL"]
    return {
        "schema": "longpi.person/1", "synthetic": True, "as_of": "2026-11-10",
        "person": {"code": "P2", "label": "P2（合成）", "sex": "F", "birth": "1965-03", "region": {"north": False, "urban": True}},
        "labs": labs,
        "vitals": [{"date": l["date"], "sbp": 146 - 3 * i if i < 1 else 136 - i, "dbp": 86, "pulse": 76, "setting": "office"} for i, l in enumerate(labs)],
        "anthropometrics": [{"date": l["date"], "height_cm": 158, "weight_kg": 61.5, "waist_cm": 84} for l in labs],
        "fitness": [{"date": "2026-08-02", "grip_kg": 23}],
        "lifestyle": {"smoking": {"status": "never"}, "alcohol": {"grams_per_week": 0}, "sleep_h": 7.0},
        "conditions": [{"name": "高血压", "icd10": "I10", "diagnosed": "2021", "treated": True},
                       {"name": "慢性乙型肝炎病毒携带", "icd10": "B18.1", "diagnosed": "2005"}],
        "medications": [{"name": "氨氯地平", "dose": "5 mg qd", "since": "2022-01", "class": "antihypertensive"}],
        "family_history": [{"relation": "mother", "condition": "2 型糖尿病", "disease_id": "t2d", "age_at_dx": 58}],
        "screenings": [{"test": "liver_us_afp", "date": "2026-04", "result": "未见占位", "report": True},
                       {"test": "mammography", "date": "2023-09", "result": "BI-RADS 2", "report": True}],
        "imaging": [{"date": "2026-04-20", "type": "冠脉 CT 钙化积分", "finding": "Agatston 35", "measures": {"cac_agatston": 35}}],
        "wearables": {"device": "Huawei Watch", "daily_csv": "daily.csv"},
        "genetic_preferences": {"show_opt_in": False, "secondary_findings": True},
        "observations_file": "observations.json",
    }


def daily(code: str, start: date, end: date, steps_fn, rhr_fn, sleep_fn, src: str):
    out = HERE / code / "daily.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "metric", "value", "source"])
        for d in days(start, end):
            if rng.random() < 0.04:
                continue
            w.writerow([d.isoformat(), "steps", round(max(300, rng.gauss(steps_fn(d), 1800))), src])
            w.writerow([d.isoformat(), "rhr", round(rng.gauss(rhr_fn(d), 2.5), 1), src])
            w.writerow([d.isoformat(), "sleep_h", round(max(3, rng.gauss(sleep_fn(d), 0.7)), 2), src])
            w.writerow([d.isoformat(), "hrv", round(max(10, rng.gauss(38, 8)), 1), src])
            if d.day == 1:
                w.writerow([d.isoformat(), "vo2max", round(rng.gauss(36 if d < date(2026, 6, 1) else 39, 0.8), 1), src])


def main() -> int:
    for code, person in (("P1", p1()), ("P2", p2())):
        (HERE / code).mkdir(exist_ok=True)
        (HERE / code / "person.json").write_text(json.dumps(person, ensure_ascii=False, indent=1), encoding="utf-8")
    daily("P1", date(2021, 3, 1), date(2026, 11, 10), lambda d: 5000 if d < date(2026, 6, 1) else 9500,
          lambda d: 66 if d < date(2026, 6, 1) else 61, lambda d: 6.4, "Apple Watch")
    daily("P2", date(2023, 1, 1), date(2026, 11, 10), lambda d: 6500, lambda d: 70, lambda d: 6.9, "Huawei Watch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
