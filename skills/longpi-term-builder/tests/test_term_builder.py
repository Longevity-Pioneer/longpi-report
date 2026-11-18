"""Offline tests for the term builder (recorded HTTP fixtures): python3 -m unittest discover -s tests"""
from __future__ import annotations

import copy
import datetime as dt
import json
import math
import os
import random
import shutil
import sys
import tempfile
import unittest
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "fixtures"
os.environ["LONGPI_TB_FIXTURES"] = str(FIX / "http")
sys.path.insert(0, str(HERE.parent / "scripts"))

import term_builder as T  # noqa: E402
from lp import registry as RG  # noqa: E402

REAL_REG = T.REPORT_DIR / "registry"


def spec(name: str) -> dict:
    return json.loads((FIX / "specs" / name).read_text(encoding="utf-8"))


def temp_registry() -> Path:
    d = Path(tempfile.mkdtemp(prefix="lp_reg_"))
    shutil.copy(REAL_REG / "groups.json", d / "groups.json")
    (d / "VERSION").write_text("2026.11.18-1\n", encoding="utf-8")
    (d / "terms").mkdir()
    for p in (REAL_REG / "terms").glob("core.*.json"):
        shutil.copy(p, d / "terms" / p.name)
    RG.freeze(d)
    os.environ["LONGPI_TB_CACHE"] = str(d / "_cache")     # fresh source cache per test (outside the registry files)
    return d


def normal_term(hr=1.2, per=1.0, mean=0.0, sd=1.0, clip=None, shape="loglinear", direction="higher_worse"):
    return {"id": "ext.t", "kind": "state", "transform": {"shape": shape, "clip": clip},
            "reference": {"kind": "normal", "by_sex_age": [{"sex": "both", "age_lo": 18, "age_hi": 99, "mean": mean, "sd": sd}],
                          "source": "t"},
            "effect": {"all_cause": {"hr": hr, "lo": hr * 0.9, "hi": hr * 1.1, "per": per, "direction": direction}},
            "overlap": {"coef": 0.5}}


class Privacy(unittest.TestCase):
    def setUp(self):
        T.REQUEST_LOG.clear()
        self.reg = temp_registry()

    def tearDown(self):
        shutil.rmtree(self.reg, ignore_errors=True)

    def test_network_carries_only_identifiers(self):
        s = spec("good_steps.json")
        s2 = spec("no_source_loinc.json")
        T.verify(s, self.reg)
        T.verify(s2, self.reg)
        self.assertTrue(T.REQUEST_LOG)
        allowed_values = {"35247352", "1884-6"}
        for url in T.REQUEST_LOG:
            u = urllib.parse.urlparse(url)
            self.assertIn(u.hostname, T.ALLOWED_HOSTS)
            for k, vals in urllib.parse.parse_qs(u.query).items():
                for v in vals:
                    if k in T._FIXED_PARAMS:
                        continue
                    stripped = v.replace("EXT_ID:", "").replace(" AND SRC:MED", "")
                    self.assertIn(stripped, allowed_values, f"{k}={v} in {url}")

    def test_personal_values_refused(self):
        for bad in ("张三", "John Smith", "5.6 mmol/L", "1990-01-02", "LDL 3.4", "patient U01"):
            with self.assertRaises(T.PrivacyError):
                T.assert_public_identifier(bad)
        with self.assertRaises(T.PrivacyError):
            T.http_get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=zhang+san+ldl+3.4")
        with self.assertRaises(T.PrivacyError):
            T.http_get("https://example.com/api?id=123")
        with self.assertRaises(T.PrivacyError):
            T.http_get("http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=1")

    def test_identifiers_accepted(self):
        for ok in ("35247352", "PMC9424424", "10.1016/S2468-2667(21)00302-9", "PGS000018", "PPM000123", "1884-6",
                   "E11", "B18.1", "P16860", "210"):
            self.assertEqual(T.assert_public_identifier(ok), ok)


class Numbers(unittest.TestCase):
    def test_variants_and_boundaries(self):
        self.assertTrue(T.find_number(1.1, "HR 1.10 (1.04-1.16)"))
        self.assertTrue(T.find_number(0.6, "was 0·60 (95% CI 0·51–0·71)"))
        self.assertFalse(T.find_number(1.1, "HR 1.15 (1.04-1.16)"))
        self.assertFalse(T.find_number(1.1, "HR 11.1"))
        self.assertFalse(T.find_number(5, "3.5 and 15"))
        self.assertTrue(T.find_number(3013, "there were 3013 deaths"))

    def test_derived(self):
        e = {"hr": 1.15, "lo": 1.118, "hi": 1.181, "derived": {"from": {"hr": 0.55, "lo": 0.49, "hi": 0.62}, "pow": -0.23316}}
        self.assertIsNone(T._check_derived(e))
        e["hi"] = 1.17
        self.assertIsNotNone(T._check_derived(e))


class Verify(unittest.TestCase):
    def setUp(self):
        self.reg = temp_registry()

    def tearDown(self):
        shutil.rmtree(self.reg, ignore_errors=True)

    def test_good_spec_auto_accept(self):
        r = T.verify(spec("good_steps.json"), self.reg)
        self.assertEqual(r["verdict"], "auto_accept", r)
        self.assertTrue(all(c["found"] for c in r["checks"]))
        self.assertFalse((self.reg / "sources").exists())   # verify never writes into the frozen registry
        RG.verify_manifest(self.reg)
        src = json.loads(T._cache_path("pmid:35247352").read_text(encoding="utf-8"))
        for k in ("url", "fetched_at", "sha256", "text"):
            self.assertIn(k, src)

    def test_changed_number_goes_qualitative(self):
        s = spec("good_steps.json")
        s["effect"]["all_cause"]["hr_below"]["derived"]["from"]["hr"] = 0.56
        s["effect"]["all_cause"]["hr_below"]["hr"] = round(0.56 ** -0.23316, 4)
        r = T.verify(s, self.reg)
        self.assertEqual(r["verdict"], "qualitative")
        self.assertTrue(any("未在 quote" in f for f in r["fail"]))

    def test_quote_not_in_source(self):
        s = spec("good_steps.json")
        s["evidence"]["quote"] = "the adjusted HR for all-cause mortality was 0.55 (0.49-0.62) in everybody"
        r = T.verify(s, self.reg)
        self.assertEqual(r["verdict"], "qualitative")
        self.assertTrue(any("子串" in f for f in r["fail"]))

    def test_low_grade_events_direction(self):
        s = spec("good_steps.json")
        s["evidence"]["grade"] = "C"
        s["population"]["events"] = 80
        r = T.verify(s, self.reg)
        self.assertTrue(any("等级" in f for f in r["fail"]))
        self.assertTrue(any("< 100" in f for f in r["fail"]))
        s2 = spec("no_source_loinc.json")
        s2["effect"]["all_cause"]["direction"] = "higher_better"
        r2 = T.verify(s2, self.reg)
        self.assertTrue(any("higher_better" in f for f in r2["fail"]))

    def test_unknown_code_invalid(self):
        s = spec("good_steps.json")
        s["input"]["code"] = "LP:not_a_registered_code"
        self.assertEqual(T.verify(s, self.reg)["verdict"], "invalid")

    def test_non_commercial_invalid(self):
        s = spec("good_steps.json")
        s["license"]["commercial_use"] = False
        self.assertEqual(T.verify(s, self.reg)["verdict"], "invalid")

    def test_transport_required_for_non_east_asian(self):
        s = spec("good_steps.json")
        s["transport"] = {"ancestry": "mixed", "shrink": 1.0, "sd_inflate": 1.0}
        r = T.verify(s, self.reg)
        self.assertTrue(any("非东亚" in f for f in r["fail"]))
        self.assertFalse(T.is_east_asian("multinational (US, Europe, Japan)"))
        self.assertTrue(T.is_east_asian("Chinese (CKB)"))

    def test_overlap_rules(self):
        t = normal_term()
        t["overlap"] = {"coef": 0.5, "overlaps_with": ["core.lipid"], "rationale_zh": "x"}
        t["adjusted_for"] = ["age", "sex"]
        self.assertIsNotNone(T.overlap_rule(t))            # only age/sex -> <= 0.3
        t["overlap"]["coef"] = 0.3
        self.assertIsNone(T.overlap_rule(t))
        t["overlap"] = {"coef": 0.8, "overlaps_with": ["core.lipid", "core.bp"], "rationale_zh": "x"}
        t["adjusted_for"] = ["age", "sex", "core.lipid"]
        self.assertIsNotNone(T.overlap_rule(t))            # partial -> <= 0.6
        t["adjusted_for"].append("core.bp")
        self.assertIsNone(T.overlap_rule(t))               # full -> <= 1

    def test_dedupe_by_code(self):
        s = spec("good_steps.json")
        other = copy.deepcopy(s)
        other["id"] = "ext.other_steps"
        (self.reg / "terms" / "ext.other_steps.json").write_text(json.dumps(other), encoding="utf-8")
        r = T.verify(s, self.reg)
        self.assertEqual(r["verdict"], "invalid")
        self.assertTrue(any("同一指标" in m for m in r["invalid"]))


class Normalisation(unittest.TestCase):
    def test_loglinear_closed_form(self):
        t = normal_term(hr=1.3, per=0.5, mean=2.0, sd=0.7)
        b = math.log(1.3) / 0.5
        self.assertAlmostEqual(T.log_mean_exp_ref(t, "all_cause", "M", 50), b * 2.0 + 0.5 * (b * 0.7) ** 2, places=9)

    def test_residualized_prs_jensen(self):
        t = normal_term(hr=1.5, per=1.0, shape="residualized")
        self.assertAlmostEqual(T.log_mean_exp_ref(t, "all_cause", "F", 40), 0.5 * math.log(1.5) ** 2, places=9)

    def test_indicator_categorical_hinge(self):
        ind = {"id": "ext.i", "kind": "genetic", "transform": {"shape": "indicator"},
               "reference": {"kind": "prevalence", "prevalence": 0.01, "source": "t"},
               "effect": {"crc": {"hr": 5.0, "lo": 4, "hi": 6, "direction": "higher_worse"}}}
        self.assertAlmostEqual(T.log_mean_exp_ref(ind, "crc", "M", 50), math.log(0.99 + 0.05), places=12)
        cat = {"id": "ext.c", "kind": "exposure", "transform": {"shape": "categorical"},
               "reference": {"kind": "categorical", "p": {"never": 0.5, "current": 0.5}, "source": "t"},
               "effect": {"lung_ca": {"levels": {"never": {"hr": 1}, "current": {"hr": 3.0, "lo": 2, "hi": 4}}}}}
        self.assertAlmostEqual(T.log_mean_exp_ref(cat, "lung_ca", "M", 50), math.log(2.0), places=12)
        hin = {"id": "ext.h", "kind": "behavior", "transform": {"shape": "hinge", "knot_lo": 8000, "clip": [1000, 20000]},
               "reference": {"kind": "normal", "mean": 6000, "sd": 2500, "source": "t"},
               "effect": {"all_cause": {"hr_below": {"hr": 1.15, "lo": 1.1, "hi": 1.2, "per": 1000}}}}
        rng = random.Random(1)
        L = T.log_mean_exp_ref(hin, "all_cause", "M", 50)
        xs = [T.f_raw(hin, "all_cause", rng.gauss(6000, 2500)) for _ in range(200000)]
        self.assertAlmostEqual(math.log(sum(math.exp(x) for x in xs) / len(xs)), L, delta=0.003)
        self.assertEqual(T.f_raw(hin, "all_cause", 9000), 0.0)

    def test_lognormal_matches_mc(self):
        t = {"id": "ext.l", "kind": "state", "transform": {"shape": "loglinear", "log_x": True, "clip": [0.1, 100]},
             "reference": {"kind": "lognormal", "meanlog": 0.3, "sdlog": 0.9, "source": "t"},
             "effect": {"all_cause": {"hr": 1.2, "lo": 1.1, "hi": 1.3, "per": math.log(2), "direction": "higher_worse"}}}
        rng = random.Random(2)
        xs = [math.exp(T.f_raw(t, "all_cause", math.exp(rng.gauss(0.3, 0.9)))) for _ in range(200000)]
        self.assertAlmostEqual(math.log(sum(xs) / len(xs)), T.log_mean_exp_ref(t, "all_cause", "M", 60), delta=0.003)


class PopulationCheck(unittest.TestCase):
    def test_normalised_terms_pass(self):
        a, b = normal_term(), normal_term(hr=1.5, shape="residualized")
        b["id"] = "ext.t2"
        a["overlap"]["coef"] = b["overlap"]["coef"] = 1.0
        res = T.check_population([a, b], n=8000)
        self.assertTrue(res["ok"], res["fails"])

    def test_coefficient_jensen_deficit_reported(self):
        # c*l with l normalised before the coefficient: population mean = exp(-c(1-c)Var f/2) < 1
        terms = []
        for i in range(4):
            t = normal_term(hr=1.8, shape="residualized")
            t["id"] = f"ext.j{i}"
            terms.append(t)
        res = T.check_population(terms, n=8000)
        self.assertFalse(res["ok"])
        self.assertTrue(any("合计" in f for f in res["fails"]))

    def test_unnormalised_term_caught(self):
        bad = normal_term(hr=1.6, shape="residualized")
        bad["id"] = "ext.bad"
        # a stale/wrong stored normaliser (e.g. an engine that treats residualized inputs as already centred)
        bad["reference"]["log_norm"] = {"all_cause": [{"sex": "both", "age_lo": 18, "age_hi": 99, "value": 0.0}]}
        res = T.check_population([bad], n=4000)
        self.assertFalse(res["ok"])
        self.assertTrue(any("ext.bad" in f for f in res["fails"]))

    def test_bad_reference_caught(self):
        cat = {"id": "ext.c", "kind": "exposure", "transform": {"shape": "categorical"},
               "reference": {"kind": "categorical", "p": {"never": 0.4, "current": 0.4}, "source": "t"},
               "effect": {"lung_ca": {"levels": {"never": {"hr": 1}, "current": {"hr": 3.0, "lo": 2, "hi": 4}}}}}
        self.assertFalse(T.check_population([cat], n=4000)["ok"])
        gap = normal_term()
        gap["reference"]["by_sex_age"] = [{"sex": "M", "age_lo": 18, "age_hi": 99, "mean": 0, "sd": 1}]
        res = T.check_population([gap], n=2000)
        self.assertFalse(res["ok"])
        self.assertTrue(any("未覆盖" in f for f in res["fails"]))

    def test_direction_caught(self):
        t = normal_term(hr=0.8, direction="higher_worse")
        self.assertFalse(T.check_population([t], n=1000)["ok"])


class AddFreeze(unittest.TestCase):
    def setUp(self):
        self.reg = temp_registry()

    def tearDown(self):
        shutil.rmtree(self.reg, ignore_errors=True)

    def test_add_bumps_version_and_freezes(self):
        r = T.add([spec("good_steps.json")], self.reg, today=dt.date(2026, 11, 18), n_pop=2000)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["version"], "2026.11.18-2")
        self.assertTrue((self.reg / "terms" / "ext.test_steps.json").exists())
        RG.verify_manifest(self.reg)
        t = json.loads((self.reg / "terms" / "ext.test_steps.json").read_text(encoding="utf-8"))
        self.assertTrue(t["evidence"]["numbers_verified"])
        src = json.loads((self.reg / "sources" / "pmid_35247352.json").read_text(encoding="utf-8"))
        self.assertTrue(any(c["term"] == "ext.test_steps" for c in src["checks"]))
        r2 = T.add([spec("good_steps.json")], self.reg, today=dt.date(2026, 11, 18), n_pop=2000)
        self.assertFalse(r2["ok"])                       # exists, no --replace
        self.assertEqual(T.bump_version(self.reg, dt.date(2026, 11, 19)), "2026.11.19-1")

    def test_qualitative_requires_flag(self):
        s = spec("no_source_loinc.json")
        self.assertFalse(T.add([s], self.reg, n_pop=1000)["ok"])
        r = T.add([s], self.reg, qualitative=True, why="测试：无来源", n_pop=1000)
        self.assertTrue(r["ok"], r)
        q = json.loads((self.reg / "qualitative" / "ext.test_apob.json").read_text(encoding="utf-8"))
        self.assertEqual(q["why_qualitative_zh"], "测试：无来源")

    def test_refuses_to_freeze_unnormalised(self):
        before = (self.reg / "MANIFEST.json").read_text(encoding="utf-8")
        s = spec("good_steps.json")
        s["reference"]["log_norm"] = {"all_cause": [{"sex": "both", "age_lo": 18, "age_hi": 99, "value": -0.5}]}
        r = T.add([s], self.reg, n_pop=2000)
        self.assertFalse(r["ok"])
        self.assertIn("人群中性", r["error"])
        self.assertFalse((self.reg / "terms" / "ext.test_steps.json").exists())
        self.assertEqual((self.reg / "MANIFEST.json").read_text(encoding="utf-8"), before)


class Codes(unittest.TestCase):
    def test_lp_patterns(self):
        for ok in ("LP:steps_daily_mean", "LP:clock.horvath_accel", "LP:prot.organage_heart_gap", "LP:screen.crc_fit",
                   "LP:fh:crc", "LP:metab.metabohealth"):
            self.assertTrue(T.check_code(ok, offline=True)[0], ok)
        for bad in ("LP:fh:not_a_disease", "LP:unknown_thing", "nocolon"):
            self.assertFalse(T.check_code(bad, offline=True)[0], bad)

    def test_loinc_fixture(self):
        self.assertTrue(T.check_code("LOINC:1884-6")[0])


class BlindScorer(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(HERE / "blind"))
        import score_blind
        self.S = score_blind

    def task(self, tid):
        return json.loads((HERE / "blind" / f"{tid}.task.json").read_text(encoding="utf-8"))

    def test_eleven_tasks_without_numbers(self):
        tasks = sorted((HERE / "blind").glob("*.task.json"))
        self.assertEqual(len(tasks), 11)
        for p in tasks:
            txt = p.read_text(encoding="utf-8")
            self.assertNotRegex(txt, r"\d\.\d", p.name)          # no effect sizes or CIs in the task
            self.assertNotIn("pmid", txt.lower())

    def test_rescaled_loglinear_and_hinge(self):
        bp = {"effect": {"all_cause": {"hr": 1.0929 ** 0.5, "lo": 1, "hi": 1.1, "per": 5}}, "transform": {"shape": "loglinear"}}
        self.assertTrue(self.S.score(self.task("bp"), bp)["pass"])
        bp["effect"]["all_cause"]["hr"] = 1.25
        self.assertFalse(self.S.score(self.task("bp"), bp)["pass"])
        sl = {"transform": {"shape": "hinge"}, "effect": {"all_cause": {"hr_below": {"hr": 1.06, "per": 1},
                                                                         "hr_above": {"hr": 1.30, "per": 1}}}}
        r = self.S.score(self.task("sleep"), sl)
        self.assertFalse(r["pass"])
        self.assertEqual([x["pass"] for x in r["rows"]], [True, False])

    def test_categorical_and_methylation(self):
        sm = {"transform": {"shape": "categorical"}, "effect": {"all_cause": {"levels": {
            "never": {"hr": 1}, "former_lt5": {"hr": 1.2}, "former_ge5": {"hr": 1.0}, "current": {"hr": 1.34}}}}}
        self.assertTrue(self.S.score(self.task("smoking"), sm)["pass"])
        me = {"transform": {"shape": "residualized"}, "effect": {"all_cause": {"hr": 1.055, "per": 1}}}
        self.assertTrue(self.S.score(self.task("methylation"), me)["pass"])


class RealRegistry(unittest.TestCase):
    def test_frozen_registry_population_neutral(self):
        terms = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((REAL_REG / "terms").glob("*.json"))]
        RG.verify_manifest(REAL_REG)
        res = T.check_population(terms, n=3000)
        self.assertTrue(res["ok"], res["fails"][:5])


if __name__ == "__main__":
    unittest.main()
