"""Invariant and reproduction tests (standard library only): python3 -m unittest discover -s tests"""
from __future__ import annotations

import json
import math
import random
import statistics
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from lp import clinical, clock, domains as DM, engine as EN, mortality as M, units, wearables as WR  # noqa: E402


class PhenoAge(unittest.TestCase):
    def test_matches_bioage_phenoage_calc(self):
        # BioAge phenoage_calc(orig = TRUE) value reproduced by longevity-skills/accelerated-biological-aging-risk
        v = dict(albumin=45, creatinine=80, glucose=5.0, crp=2.0, lymph_pct=32, mcv=90, rdw=13.2, alp=70, wbc=6.5)
        self.assertAlmostEqual(clock.phenoage(v, 58), 50.475248839667486, places=9)

    def test_linear_in_predictor(self):
        v = dict(albumin=45, creatinine=80, glucose=5.0, crp=2.0, lymph_pct=32, mcv=90, rdw=13.2, alp=70, wbc=6.5)
        a = clock.phenoage(v, 50)
        v2 = dict(v, rdw=14.2)
        self.assertAlmostEqual(clock.phenoage(v2, 50) - a, clock.years_per_unit("rdw"), places=6)

    def test_noise_is_plausible(self):
        v = dict(albumin=45, creatinine=80, glucose=5.0, crp=1.0, lymph_pct=32, mcv=90, rdw=13.0, alp=70, wbc=6.0)
        sd, shares = clock.noise_sd(v)
        self.assertTrue(1.0 < sd < 3.0, sd)
        self.assertAlmostEqual(sum(shares.values()), 1.0, places=9)


class Units(unittest.TestCase):
    def test_conversions(self):
        self.assertAlmostEqual(units.to_canonical("crp", 0.2, "mg/dL"), 2.0)
        self.assertAlmostEqual(units.to_canonical("glucose", 90.0, "mg/dL"), 90 / 18.016)
        self.assertAlmostEqual(units.to_canonical("albumin", 4.5, "g/dL"), 45.0)
        self.assertAlmostEqual(units.to_canonical("hba1c", 48, "mmol/mol"), 48 / 10.929 + 2.15)
        with self.assertRaises(ValueError):
            units.to_canonical("ldl", 3.0, "furlongs")

    def test_chinese_unit_spellings_and_passthrough(self):
        self.assertAlmostEqual(units.to_canonical("wbc", 6.1, "×10^9/L"), 6.1)
        self.assertAlmostEqual(units.to_canonical("platelets", 233, "×10⁹/L"), 233)
        self.assertAlmostEqual(units.to_canonical("lpa", 156, "mg/L"), 156)   # not convertible, kept as reported


class Smoking(unittest.TestCase):
    def test_levels_by_date(self):
        from datetime import date
        p = {"lifestyle": {"smoking": {"status": "former", "quit_year": 2023}}}
        self.assertEqual(EN.smoking_level(p, date(2022, 6, 1)), "current")
        self.assertEqual(EN.smoking_level(p, date(2025, 6, 1)), "former_lt5")
        self.assertEqual(EN.smoking_level(p, date(2028, 6, 1)), "former_ge5")
        self.assertEqual(EN.smoking_level({"lifestyle": {"smoking": {"status": "former"}}}, date(2026, 1, 1)), "pop:former")
        self.assertIsNone(EN.smoking_level({}, date(2026, 1, 1)))


class Mortality(unittest.TestCase):
    def setUp(self):
        self.ref = M.Reference("M")

    def test_gompertz_slope(self):
        b = self.ref.gompertz_slope(2026)
        self.assertTrue(0.09 < b < 0.11, b)

    def test_life_expectancy_matches_wpp(self):
        t = json.loads((SKILL / "data" / "lifetable_china_wpp2024.json").read_text())
        s = M.survival_from(M.cohort_hazards(self.ref, 0.0, 2026, {"kind": "period"}), 0.0)
        le = M.life_expectancy(M.survival_ages(0.0, len(s)), s)
        self.assertLess(abs(le - t["e0"]["M"]["2026"]), 0.6, (le, t["e0"]["M"]["2026"]))

    def test_frailty_identity(self):
        s = M.survival_from(M.cohort_hazards(self.ref, 40.0, 2026, {"kind": "wpp"}), 40.0)
        same = M.individual_survival(s, 1.0, 0.16)
        for a, b in zip(s, same):
            self.assertAlmostEqual(a, b, places=12)

    def test_hazard_ratio_attenuates_at_extreme_age(self):
        s = M.survival_from(M.cohort_hazards(self.ref, 40.0, 2026, {"kind": "period"}), 40.0)
        R, s2 = 1.5, 0.16
        si = M.individual_survival(s, R, s2)
        h = lambda S, i: -math.log(S[i + 1] / S[i])
        hr_start = h(si, 1) / h(s, 1)
        hr_late = h(si, 75) / h(s, 75)   # ~ age 115
        self.assertAlmostEqual(hr_start, R, delta=0.03)
        self.assertLess(hr_late, hr_start)
        self.assertGreater(hr_late, 1.0)

    def test_old_age_hazard_below_plateau(self):
        for x in range(96, 131):
            self.assertLessEqual(self.ref.mu_period(x, 2026), 0.7 + 1e-9)

    def test_index_monotone_in_risk(self):
        s = M.survival_from(M.cohort_hazards(self.ref, 40.0, 2026, {"kind": "wpp"}), 40.0)
        ages = M.survival_ages(40.0, len(s))
        p_ref = M.at_age(ages, s, 120)
        idx = [100 + 10 * math.log10(M.at_age(ages, M.individual_survival(s, R, 0.16), 120) / p_ref) for R in (0.6, 0.8, 1.0, 1.25, 1.6)]
        self.assertTrue(all(a > b for a, b in zip(idx, idx[1:])), idx)
        self.assertAlmostEqual(idx[2], 100.0, places=6)


class Domains(unittest.TestCase):
    def test_population_mean_hazard_is_one(self):
        rng = random.Random(1)
        for sp in DM.domain_specs():
            p = DM.draw_params(sp, None)
            for sex in ("M", "F"):
                n, tot = 20000, 0.0
                for _ in range(n):
                    x = DM.draw_from_population(sp, sex, 45, rng)
                    tot += math.exp(DM.log_hr(sp, p, x, sex, 45))
                self.assertAlmostEqual(tot / n, 1.0, delta=0.03, msg=(sp["id"], sex, tot / n))

    def test_quadrature_matches_closed_form(self):
        b = math.log(0.89) / 3.5
        got = math.log(DM.expect_normal(lambda x: math.exp(b * x), 40.0, 8.0))
        self.assertAlmostEqual(got, b * 40 + 0.5 * (b * 8) ** 2, places=10)


class Clinical(unittest.TestCase):
    def test_china_par_table2(self):
        tc, hdl = 210 * 0.0259, 55 * 0.0259
        for age, exp in ((40, 2.2), (50, 5.4), (60, 11.0), (70, 19.6)):
            r = clinical.china_par("M", age, 130, False, tc, hdl, 80, False, True, True, True, False)
            self.assertAlmostEqual(r["risk_10y_pct"], exp, delta=0.15)
        for age, exp in ((40, 2.4), (50, 5.4), (60, 10.1), (70, 17.1)):
            r = clinical.china_par("F", age, 130, False, tc, hdl, 80, False, True, True, True, False)
            self.assertAlmostEqual(r["risk_10y_pct"], exp, delta=0.15)


def _rec(typ, src, t0, t1, value, unit="", inner=""):
    u = f' unit="{unit}"' if unit else ""
    head = f' <Record type="{typ}" sourceName="{src}"{u} startDate="{t0} +0800" endDate="{t1} +0800" value="{value}"'
    return head + (f">{inner}</Record>\n" if inner else "/>\n")


def apple_export() -> str:
    """A small export.xml shaped like Apple's: internal DTD, metadata children, two step sources,
    watch sleep stages inside an InBed record, a third-party sleep app, a workout, a control character."""
    hk, sl = "HKQuantityTypeIdentifier", "HKCategoryValueSleepAnalysis"
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE HealthData [\n'
         '<!ELEMENT HealthData (ExportDate,Me,(Record|Workout|ActivitySummary)*)>\n'
         '<!ATTLIST Record\n  type CDATA #REQUIRED\n  sourceName CDATA #REQUIRED\n>\n]>\n<HealthData locale="zh_CN">\n'
         ' <ExportDate value="2026-10-24 09:00:00 +0800"/>\n')
    x += _rec(hk + "StepCount", "iPhone", "2026-10-23 08:00:00", "2026-10-23 08:10:00", 3000, "count")
    x += _rec(hk + "StepCount", "iPhone", "2026-10-23 18:00:00", "2026-10-23 18:10:00", 2000, "count")
    x += _rec(hk + "StepCount", "Watch", "2026-10-23 08:00:00", "2026-10-23 08:10:00", 6500, "count",
              '<MetadataEntry key="HKMetadataKeySyncVersion" value="1"/>')
    x += _rec(hk + "RestingHeartRate", "Watch", "2026-10-23 06:00:00", "2026-10-23 23:00:00", 58, "count/min")
    x += _rec(hk + "BodyMass", "Scale\x0b", "2026-10-23 07:00:00", "2026-10-23 07:00:00", 165, "lb")
    x += _rec(hk + "WalkingSpeed", "iPhone", "2026-10-23 08:00:00", "2026-10-23 08:05:00", 3, "mi/hr")
    x += _rec("HKCategoryTypeIdentifierSleepAnalysis", "Watch", "2026-10-22 23:00:00", "2026-10-23 07:00:00", sl + "InBed")
    for v, a, b in (("AsleepCore", "2026-10-22 23:30:00", "2026-10-23 01:00:00"), ("AsleepDeep", "2026-10-23 01:00:00", "2026-10-23 02:00:00"),
                    ("Awake", "2026-10-23 02:00:00", "2026-10-23 02:15:00"), ("AsleepREM", "2026-10-23 02:15:00", "2026-10-23 03:30:00"),
                    ("AsleepCore", "2026-10-23 03:30:00", "2026-10-23 06:30:00")):
        x += _rec("HKCategoryTypeIdentifierSleepAnalysis", "Watch", a, b, sl + v)
    x += _rec("HKCategoryTypeIdentifierSleepAnalysis", "AutoSleep", "2026-10-22 23:40:00", "2026-10-23 06:00:00", sl + "AsleepUnspecified")
    x += (' <Workout workoutActivityType="HKWorkoutActivityTypeRunning" sourceName="Watch" startDate="2026-10-23 19:00:00 +0800" '
          'endDate="2026-10-23 19:30:00 +0800">\n  <WorkoutStatistics type="HKQuantityTypeIdentifierStepCount" sum="9999" unit="count"/>\n </Workout>\n'
          ' <ActivitySummary dateComponents="2026-10-23" activeEnergyBurned="500"/>\n</HealthData>\n')
    return x


class Wearables(unittest.TestCase):
    def test_apple_health_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "export.xml"
            f.write_text(apple_export(), encoding="utf-8")
            d = WR.read_apple_health(f)
            day = date(2026, 10, 23)
            self.assertEqual(d.series("steps")[day], 6500)  # larger source, not phone + watch, not the workout total
            self.assertEqual(d.series("rhr")[day], 58)
            self.assertAlmostEqual(d.series("weight")[day], 165 * 0.45359237)
            self.assertAlmostEqual(d.series("walking_speed")[day], 3 * 0.44704)
            self.assertAlmostEqual(d.series("sleep_h")[day], 6.75)  # watch stages without Awake/InBed beat AutoSleep's 6.33 h
            c1 = WR.read_apple_health_cached(f)
            self.assertTrue((Path(tmp) / "export.xml.longpi-cache.json").exists())
            c2 = WR.read_apple_health_cached(f)
            for m in ("steps", "rhr", "weight", "walking_speed", "sleep_h"):
                self.assertEqual(c1.series(m), d.series(m))
                self.assertEqual(c2.series(m), d.series(m))

    def test_numeric_dates_resolved_per_file(self):
        meta = "Glucose Data,Generated on,10-24-2026 09:00 UTC,Generated by,x\n"
        head = "Device,Serial Number,Device Timestamp,Record Type,Historic Glucose mmol/L,Scan Glucose mmol/L\n"
        want = [(datetime(2026, 10, 5, 8, 0), 5.5), (datetime(2026, 10, 13, 8, 0), 6.1)]
        with tempfile.TemporaryDirectory() as tmp:
            cases = {"us": ("10-13-2026 08:00", "10-05-2026 08:00"), "eu": ("13-10-2026 08:00", "05-10-2026 08:00")}
            for name, (t1, t2) in cases.items():
                f = Path(tmp) / f"{name}.csv"
                f.write_text(meta + head + f"Libre,1,{t1},0,6.1,\nLibre,1,{t2},0,5.5,\nLibre,1,{t2},1,,5.6\n", encoding="utf-8")
                self.assertEqual(WR.read_cgm_csv(f), want, name)
            f = Path(tmp) / "ambiguous.csv"
            f.write_text(head + "Libre,1,05-10-2026 08:00,0,5.5,\nLibre,1,06-10-2026 08:00,0,5.7,\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                WR.read_cgm_csv(f)
            f = Path(tmp) / "bp.csv"
            f.write_text("datetime,sbp,dbp\n10/24/2026 07:30,128,82\n10/05/2026 21:00,131,84\n", encoding="utf-8")
            self.assertEqual([r["t"] for r in WR.read_bp_csv(f)], [datetime(2026, 10, 5, 21, 0), datetime(2026, 10, 24, 7, 30)])


class DataValue(unittest.TestCase):
    """More data never widens the interval; what is not measured is neutral for the point estimate."""

    @classmethod
    def setUpClass(cls):
        cls.dm = EN.P()["data_menu"]
        cls.saved_n = cls.dm["n_draws"]
        cls.dm["n_draws"] = 300

    @classmethod
    def tearDownClass(cls):
        cls.dm["n_draws"] = cls.saved_n

    def test_blood_test_offered_and_narrows(self):
        base = {"as_of": "2026-10-20", "person": {"code": "X", "sex": "M", "age": 50.0}, "labs": []}
        m0 = EN.Model(base, {}, n_draws=300, seed=5)
        dv0 = EN.data_value(m0)
        self.assertEqual(dv0["completeness_pct"], 0)                     # age and sex only
        self.assertEqual(dv0["items"][0]["id"], "blood_panel")          # the most informative single step
        self.assertLess(dv0["width_all"], dv0["width_now"])
        blood = {"albumin": [45, "g/L"], "creatinine": [80, "umol/L"], "glucose": [5.2, "mmol/L"], "crp": [1.0, "mg/L"],
                 "lymph_pct": [31, "%"], "mcv": [90, "fL"], "rdw": [13.0, "%"], "alp": [70, "U/L"], "wbc": [6.2, "10^9/L"]}
        m1 = EN.Model(dict(base, labs=[{"date": "2026-10-01", "items": blood}]), {}, n_draws=300, seed=5)
        dv1 = EN.data_value(m1)
        self.assertLess(dv1["width_now"], dv0["width_now"] - 1.0)
        self.assertGreater(dv1["completeness_pct"], 0)
        for it in dv1["items"]:
            self.assertGreater(it["narrows_by"], 0)

    def test_grimage_counted_and_shrunk(self):
        pf = SKILL / "examples" / "demo_person.json"
        person = json.loads(pf.read_text(encoding="utf-8"))
        from lp import derive
        derived = derive.derive(person, pf.parent)
        m0 = EN.Model(person, derived, n_draws=300, seed=5)
        self.assertIsNone(m0.meth_mobs)                                  # demo report is first-generation: not counted
        g = EN.P()["methylation"]["clocks"]["GrimAge2"]
        a0, a1 = g["ref"]["M"]
        person["methylation"].append({"date": "2026-05-18", "clock_type": "GrimAge2", "bio_age": a0 + a1 * 37.6 + 10.0, "chrono_age": 37.6})
        m1 = EN.Model(person, derived, n_draws=300, seed=5)
        self.assertEqual(m1.meth["clock"], "GrimAge2")
        self.assertAlmostEqual(m1.meth["accel"], 10.0, places=1)
        terms = [m1.meth_term(m1.draw()) for _ in range(300)]
        mean = statistics.fmean(terms)
        unshrunk = g["beta"] * m1.meth_mobs - 0.5 * g["beta"] ** 2 * g["sd_resid"] ** 2
        self.assertGreater(mean, 0.0)
        self.assertLess(mean, unshrunk)                                  # laboratory offset shrinks the measured residual


class Modules(unittest.TestCase):
    """Exercise library, abnormal blood tests, default asks, rendering of the optional modules."""

    def test_exercise_library_complete(self):
        from lp import render
        lib = render.exercise_library()["exercises"]
        self.assertGreaterEqual(len(lib), 20)
        self.assertEqual(len({e["id"] for e in lib}), len(lib))
        for e in lib:
            for k in ("name", "target", "steps", "cues", "default_dose", "category"):
                self.assertTrue(e.get(k), (e["id"], k))
            for img in e["images"]:
                self.assertTrue((SKILL / img).is_file(), img)

    def test_abnormal_blood_test_flagged_and_excluded(self):
        blood = {"albumin": [45, "g/L"], "creatinine": [80, "umol/L"], "glucose": [5.2, "mmol/L"], "crp": [1.0, "mg/L"],
                 "lymph_pct": [31, "%"], "mcv": [65, "fL"], "rdw": [19.0, "%"], "alp": [70, "U/L"], "wbc": [6.2, "10^9/L"]}
        p = {"as_of": "2026-10-20", "person": {"code": "X", "sex": "M", "age": 40.0}, "labs": [{"date": "2026-03-01", "items": blood}]}
        pts = EN.phenoage_points(p, "M", 40.0 - 2026.8, EN.parse_date("2026-10-20"))
        self.assertEqual(pts[0]["flags"], ["rbc_abnormal"])
        p2 = json.loads(json.dumps(p)); p2["labs"][0]["clock_exclude"] = ["mcv", "rdw"]
        pts2 = EN.phenoage_points(p2, "M", 40.0 - 2026.8, EN.parse_date("2026-10-20"))
        self.assertEqual(pts2[0]["flags"], [])
        self.assertLess(pts2[0]["gap"], pts[0]["gap"] - 3)               # MCV 65 / RDW 19 add years
        self.assertGreater(pts2[0]["noise_sd"], pts[0]["noise_sd"])       # leaving analytes out costs precision
        p3 = json.loads(json.dumps(p)); p3["labs"][0]["clock_exclude"] = True
        self.assertEqual(EN.phenoage_points(p3, "M", 40.0 - 2026.8, EN.parse_date("2026-10-20")), [])

    def test_demo_report_has_modules(self):
        from lp import render, schema
        res = json.loads((SKILL / "examples" / "output" / "results.json").read_text(encoding="utf-8"))
        n = json.loads((SKILL / "examples" / "demo_narrative.json").read_text(encoding="utf-8"))
        self.assertEqual(schema.check_narrative(n, res), [])
        self.assertTrue(res["results"]["asks_default"]["items"])
        r = render.inline_training_images(n, SKILL / "examples")
        ex = r["training"]["sessions"][0]["exercises"][0]
        self.assertTrue(ex["steps"] and ex["images"][0].startswith("data:image/jpeg;base64,"))
        bad = json.loads(json.dumps(n)); bad["training"]["sessions"][0]["exercises"].append({"ref": "no_such_move"})
        self.assertTrue(any("no_such_move" in x for x in schema.check_narrative(bad, res)))


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from lp import derive
        pf = SKILL / "examples" / "demo_person.json"
        person = json.loads(pf.read_text(encoding="utf-8"))
        cls.derived = derive.derive(person, pf.parent)
        dm = EN.P()["data_menu"]
        saved, dm["n_draws"] = dm["n_draws"], 200
        try:
            cls.res = EN.run(person, cls.derived, n_draws=300, seed=3)
        finally:
            dm["n_draws"] = saved
        cls.person = person

    def test_outputs(self):
        la = self.res["longpi_age"]
        self.assertTrue(25 < la["value"]["median"] < 50)
        self.assertLessEqual(la["value"]["p10"], la["value"]["median"])
        self.assertLessEqual(la["value"]["median"], la["value"]["p90"])
        self.assertEqual(set(self.res["index120"]["scenarios"]), {"S1", "S2", "S3"})
        self.assertTrue(self.res["interventions"])
        dv = self.res["data_value"]
        self.assertLess(dv["width_all"], dv["width_now"])
        self.assertLess(dv["width_now"], dv["width_none"])
        self.assertTrue(0 <= dv["completeness_pct"] <= 100)

    def test_missing_everything_is_neutral(self):
        p = {"as_of": "2026-10-20", "person": {"code": "X", "sex": "M", "age": 45.0}, "labs": []}
        dm = EN.P()["data_menu"]
        saved, dm["n_draws"] = dm["n_draws"], 100
        try:
            r = EN.run(p, {"wearables": {}, "data": {}}, n_draws=1500, seed=5)
        finally:
            dm["n_draws"] = saved
        self.assertAlmostEqual(r["longpi_age"]["value"]["median"], 45.0, delta=0.35)

    def test_demo_narrative_passes_checks(self):
        from lp import schema
        n = json.loads((SKILL / "examples" / "demo_narrative.json").read_text(encoding="utf-8"))
        out = {"results": self.res}
        problems = [p for p in schema.check_narrative(n, out) if "不一致" not in p]   # the demo narrative quotes the 1500-draw run
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
