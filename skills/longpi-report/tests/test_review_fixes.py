"""Regression tests for the 2026-11-18 adversarial reviews (math, robustness/privacy, evidence)."""
import copy
import json
import math
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(SKILL / "tests"))

from lp import registry as RG  # noqa: E402

MAIN = SKILL / "registry"
P1 = SKILL / "examples" / "e2e" / "people" / "P1"


def person_p1(**extra):
    p = json.loads((P1 / "person.json").read_text(encoding="utf-8"))
    p.pop("observations_file", None)
    p.update(extra)
    return p


def run(person, obs=None, base=P1, n=300, seed=3):
    from lp import derive as DV, engine as EN
    tmp = Path(tempfile.mkdtemp())
    try:
        shutil.copy(base / "daily.csv", tmp / "daily.csv")
        if obs is not None:
            (tmp / "obs.json").write_text(json.dumps({"schema": "longpi.observations/1", "observations": obs}), encoding="utf-8")
            person = dict(person, observations_file="obs.json")
        d = DV.derive(person, tmp)
        dm = EN.P()["data_menu"]
        saved, dm["n_draws"] = dm["n_draws"], 60
        try:
            return EN.run(person, d, n_draws=n, seed=seed)
        finally:
            dm["n_draws"] = saved
    finally:
        shutil.rmtree(tmp)


def o(code, value, date="2026-06-01", method="tool", **kw):
    return dict({"code": code, "value": value, "unit": "", "datetime": date, "method": method, "flags": []}, **kw)


class Math(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        RG.use(MAIN)

    def test_every_release_term_population_neutral(self):
        """Sampling each term's own reference distribution gives E[exp l] = 1 (all shapes, coefficient applied first)."""
        from lp import terms as TM
        rng = random.Random(5)
        for t in RG.ext_terms(RG.load()):
            for oc in t["effect"]:
                p = TM.draw_effect(t, oc, None)
                for sex, age in (("M", 50), ("F", 62)):
                    try:
                        vals = [math.exp(TM.normalised(t, p, TM._sample_reference(t, sex, age, rng), sex, age, 0.6)) for _ in range(6000)]
                    except (KeyError, TypeError):
                        continue
                    self.assertAlmostEqual(sum(vals) / len(vals), 1.0, delta=0.05, msg=(t["id"], oc, sex))

    def test_screening_is_counted(self):
        p = person_p1(screenings=[{"test": "crc_fit", "date": "2026-03", "report": True}])
        p["person"] = dict(p["person"], birth="1970-06")          # 56: inside the 50-75 screening age
        r = run(p)
        rows = {b["id"]: b for b in r["index120"]["behavior"]["behaviors"]}
        self.assertIn("ext.screen_crc_fit", rows, list(rows))
        self.assertGreater(rows["ext.screen_crc_fit"]["points"], 0)
        self.assertNotIn("ext.screen_crc_fit", [g["id"] for g in r["index120"]["behavior"]["how_to_gain"]])

    def test_icd10_prefix_matches_terms(self):
        a = run(person_p1(conditions=[{"name": "2 型糖尿病", "icd10": "E11"}]))
        b = run(person_p1(conditions=[{"name": "2 型糖尿病", "icd10": "E11.9"}]))
        ca = next(d for d in a["diseases"]["diseases"] if d["id"] == "chd")
        cb = next(d for d in b["diseases"]["diseases"] if d["id"] == "chd")
        self.assertAlmostEqual(ca["risk10"]["mean"], cb["risk10"]["mean"], places=4)

    def test_hbv_not_assumed_negative(self):
        r = run(person_p1())
        self.assertNotIn("ext.hbv", [t["id"] for t in r["extension"]["terms"]])

    def test_lifetime_not_below_ten_year_in_old_age(self):
        r = run(person_p1(person={"code": "O", "sex": "M", "age": 86.0}, labs=[], vitals=[], anthropometrics=[], fitness=[]))
        for d in r["diseases"]["diseases"]:
            if d["status"] == "estimated" and d.get("lifetime"):
                self.assertGreaterEqual(d["lifetime"]["mean"], d["risk10"]["mean"] - 1e-9, d["id"])

    def test_nan_observation_dropped(self):
        r = run(person_p1(), obs=[o("LOINC:33863-2", float("nan"), unit="mg/L", method="lab")])
        self.assertTrue(any(x["why"] == "数值无效" for x in r["extension"]["dropped_observations"]))
        self.assertNotIn("ext.cystatin_c", [t["id"] for t in r["extension"]["terms"] if t["status"] == "counted"])

    def test_apoe_integer_count(self):
        p = person_p1(genetic_preferences={"show_opt_in": True, "secondary_findings": True})
        r = run(p, obs=[o("LP:apoe_e4_count", 2)])
        ad = next(d for d in r["diseases"]["diseases"] if d["id"] == "ad")
        drv = {x["id"]: x["hr"] for x in ad["drivers"]}
        self.assertGreater(drv.get("ext.apoe_e4", 0), 1.5)

    def test_adding_unmeasured_term_changes_nothing(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(MAIN, tmp / "registry")
        shutil.copytree(SKILL / "data", tmp / "data")
        t = json.loads((MAIN / "terms" / "ext.cystatin_c.json").read_text(encoding="utf-8"))
        t["id"], t["input"]["code"] = "ext.zz_unmeasured", "LOINC:2532-0"
        (tmp / "registry" / "terms" / "ext.zz_unmeasured.json").write_text(json.dumps(t), encoding="utf-8")
        RG.freeze(tmp / "registry")
        a = run(person_p1())
        RG.use(tmp / "registry")
        try:
            b = run(person_p1())
        finally:
            RG.use(MAIN)
        self.assertEqual(a["longpi_age"]["value"], b["longpi_age"]["value"])
        self.assertEqual(json.dumps(a["diseases"], sort_keys=True), json.dumps(b["diseases"], sort_keys=True))


class Privacy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        RG.use(MAIN)

    def test_string_false_does_not_consent(self):
        from lp import schema
        p = person_p1(genetic_preferences={"show_opt_in": "false", "secondary_findings": "no"})
        rep = schema.check(p, P1)
        self.assertTrue(any("genetic_preferences" in e for e in rep["errors"]))
        from lp import terms as TM
        self.assertEqual(TM.preferences(p), {"show_opt_in": False, "secondary_findings": False})

    def test_hidden_genetics_do_not_leak(self):
        from lp import schema
        obs = [o("LP:apoe_e4_count", 2, method="tool"), o("LP:apoe_e4_count", 0, method="vendor"),
               o("LP:monogenic:HGNC:1100", 1), o("HGNC:1100", 1), o("LP:apoe_e2_count", 1)]
        r = run(person_p1(genetic_preferences={"show_opt_in": False, "secondary_findings": False}), obs=obs)
        blob = json.dumps(r, ensure_ascii=False) + schema.fact_sheet({"results": r})
        for w in ("apoe", "HGNC:1100", "monogenic"):
            self.assertNotIn(w, blob.lower() if w == "apoe" else blob)

    def test_narrative_cannot_name_hidden_results(self):
        from lp import schema
        out = {"results": {"diseases": {"preferences": {"show_opt_in": False, "secondary_findings": False}},
                           "longpi_age": {"value": {"median": 40.0}}}}
        probs = schema.check_narrative({"summary": "APOE ε4/ε4 纯合，BRCA1 致病变异"}, out)
        self.assertTrue(any("不能出现" in x for x in probs))


class Render(unittest.TestCase):
    def test_images_and_captions_are_safe(self):
        from lp import render
        n = {"training": {"sessions": [{"name": "s", "exercises": [
            {"name": "e", "steps": ["a"], "images": ['data:image/png;base64,AAAA" onerror="x', "/etc/hosts", "../../../etc/hosts"],
             "captions": ['<img src=x onerror="x">']}]}]}}
        r = render.inline_training_images(n, SKILL / "examples")
        self.assertEqual(r["training"]["sessions"][0]["exercises"][0]["images"], [])
        body = (SKILL / "assets" / "report_body.html").read_text(encoding="utf-8")
        self.assertIn("esc((ex.captions", body)
        self.assertIn("Content-Security-Policy", (SKILL / "assets" / "report_head.html").read_text(encoding="utf-8"))


class Validation(unittest.TestCase):
    def test_bad_inputs_are_errors_not_tracebacks(self):
        from lp import schema
        bad = [
            {"conditions": [{"name": "2型糖尿病"}]},
            {"conditions": None},
            {"lifestyle": {"alcohol": {"grams_per_week": "lots"}}},
            {"medications": [{"name": "x", "class": ["statin"]}]},
            {"screenings": ["crc"]},
            {"genetic_preferences": []},
            {"methylation": [{"date": "2026-01", "clock_type": "GrimAge2", "bio_age": -50}]},
        ]
        for patch in bad:
            p = person_p1(**patch)
            rep = schema.check(p, P1)
            self.assertTrue(rep["errors"], patch)
        p = person_p1()
        p["labs"][0]["items"]["albumin"] = [1e30, "g/L"]
        self.assertTrue(schema.check(p, P1)["errors"])
        p = person_p1()
        p["labs"][0]["date"] = "2026-05-14<img onerror=1>"
        self.assertTrue(schema.check(p, P1)["errors"])


if __name__ == "__main__":
    unittest.main()


class E2EFixes(unittest.TestCase):
    """From the Sonnet end-to-end run."""

    def test_past_due_date_flagged(self):
        from lp import schema
        out = {"results": {"as_of": "2026-11-10", "longpi_age": {"value": {"median": 40.0}}}}
        probs = schema.check_narrative({"clinical": [{"action": "复查", "due": "2026-10"}]}, out)
        self.assertTrue(any("早于数据截至日期" in p for p in probs))

    def test_no_none_half_life_and_no_absent_drivers(self):
        RG.use(MAIN)
        r = run(person_p1())
        blob = json.dumps(r["diseases"], ensure_ascii=False)
        self.assertNotIn("None 年", blob)
        for d in r["diseases"]["diseases"]:
            for x in d.get("drivers", []):
                self.assertNotIn("已确诊 2 型糖尿病", x["name"])   # P1 has no diabetes: not a driver
