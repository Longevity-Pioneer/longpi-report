"""Engine 1.1.2: registry migration, new terms, guardrails, disease risk, 120 Index behaviour part.

The ext tests run on tests/fixtures/registry_ext (made-up numbers, for mechanics only)."""
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
import core_registry  # noqa: E402

FIX = SKILL / "tests" / "fixtures"
EXT = FIX / "registry_ext"
MAIN = SKILL / "registry"


def _strip(r):
    r = json.loads(json.dumps(r))
    for k in ("engine_version", "extension", "diseases"):
        r.pop(k, None)
    r["longpi_age"].pop("extension_delta", None)
    r["index120"].pop("behavior", None)
    if "system_ages" in r:
        r["system_ages"]["unassigned"].pop("registry_terms", None)
    return r


def run(person, base=SKILL / "examples", n=300, seed=3, menu=60):
    from lp import derive as DV, engine as EN
    d = DV.derive(person, base)
    dm = EN.P()["data_menu"]
    saved, dm["n_draws"] = dm["n_draws"], menu
    try:
        return EN.run(person, d, n_draws=n, seed=seed)
    finally:
        dm["n_draws"] = saved


def demo():
    return json.loads((SKILL / "examples" / "demo_person.json").read_text(encoding="utf-8"))


class Migration(unittest.TestCase):
    """Core terms moved to the registry: numbers identical to engine 1.1.1 (fixtures made before the move).
    Run on the release registry with the new terms removed (the demo person has data some new terms use)."""

    @classmethod
    def setUpClass(cls):
        RG.use(core_registry.path())

    @classmethod
    def tearDownClass(cls):
        RG.use(MAIN)

    def test_identical_to_1_1_1(self):
        from lp import derive as DV, engine as EN
        for k in ("demo", "no_blood", "minimal_f52"):
            f = json.loads((FIX / "regression_1_1_1" / f"{k}.json").read_text(encoding="utf-8"))
            d = DV.derive(f["person"], SKILL / "examples")
            r = EN.run(f["person"], d, n_draws=600, seed=11)
            self.assertEqual(json.dumps(_strip(f["results"]), sort_keys=True), json.dumps(_strip(r), sort_keys=True), k)

    def test_manifest_detects_change(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            shutil.copytree(MAIN, tmp / "r")
            p = tmp / "r" / "terms" / "core.bp.json"
            t = json.loads(p.read_text(encoding="utf-8"))
            t["spec"]["rr"]["value"] = 0.5
            p.write_text(json.dumps(t), encoding="utf-8")
            with self.assertRaises(RG.RegistryError):
                RG.verify_manifest(tmp / "r")
        finally:
            shutil.rmtree(tmp)

    def test_no_ext_terms_in_release_registry_are_unverified(self):
        for t in RG.ext_terms(RG.load(str(MAIN))):
            self.assertTrue((t.get("evidence") or {}).get("numbers_verified"), t["id"])
            self.assertEqual(RG.validate_term(t), [], t["id"])


class Ext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        RG.use(EXT)

    @classmethod
    def tearDownClass(cls):
        RG.use(MAIN)

    def _obsfile(self, obs, genetics=None):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        f = tmp / "obs.json"
        f.write_text(json.dumps({"schema": "longpi.observations/1", "observations": obs, "genetics": genetics or {}}), encoding="utf-8")
        return str(f)

    def test_unmeasured_terms_change_nothing(self):
        p = demo()
        # the fixture registry adds terms the demo person has data for (steps, ldl); remove those inputs
        q = copy.deepcopy(p)
        q.pop("wearables")
        for l in q["labs"]:
            for k in ("ldl", "glucose_fasting"):
                l["items"].pop(k, None)
        c = run(q)
        RG.use(core_registry.path())
        d = run(q)
        RG.use(EXT)
        self.assertEqual(c["longpi_age"]["value"], d["longpi_age"]["value"])

    def test_population_neutral(self):
        from lp import terms as TM
        rng = random.Random(1)
        for t in RG.ext_terms(RG.load(str(EXT))):
            for oc in t["effect"]:
                if t["transform"]["shape"] not in ("loglinear", "residualized", "hinge"):
                    continue
                p = TM.draw_effect(t, oc, None)
                mu, sd = TM.ref_moments(t, "M", 50)
                for c in (1.0, 0.4):   # coefficient applied before normalising: neutral for any coefficient
                    vals = [math.exp(TM.normalised(t, p, rng.gauss(mu, sd), "M", 50, c)) for _ in range(40000)]
                    self.assertAlmostEqual(sum(vals) / len(vals), 1.0, delta=0.02, msg=(t["id"], oc, c))

    def test_guardrail_caps_a_wild_term(self):
        from lp import terms as TM
        raw = {"a": 1.0, "b": 0.1}
        out, bound = TM._clamp(raw, 0.15, 0.30)
        self.assertTrue(bound)
        self.assertLessEqual(abs(out["a"]), 0.15 + 1e-12)
        self.assertLessEqual(abs(sum(out.values())), 0.30 + 1e-12)

    def test_guardrail_in_engine(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(EXT, tmp / "r")
        p = tmp / "r" / "terms" / "ext.test_apob.json"
        t = json.loads(p.read_text(encoding="utf-8"))
        t["effect"]["all_cause"] = {"hr": 11.0, "lo": 10.4, "hi": 11.6, "per": 0.25}
        t["overlap"]["coef"] = 1.0
        t["group"] = None
        p.write_text(json.dumps(t), encoding="utf-8")
        RG.freeze(tmp / "r")
        RG.use(tmp / "r")
        try:
            q = demo()
            q["labs"][-1]["items"]["apob"] = [2.0, "g/L"]
            r = run(q)
        finally:
            RG.use(EXT)
        row = next(x for x in r["extension"]["terms"] if x["id"] == "ext.test_apob")
        self.assertLessEqual(row["years"]["p90"] * r["gompertz_b"], 0.15 + 1e-6)
        self.assertGreater(r["extension"]["guardrail"]["draws_bound_share"], 0.9)

    def test_steps_raise_index_not_longpi_age(self):
        """Acceptance §9.7: 4000 -> 9000 steps sustained 8 weeks: 120 Index up, LongPi Age unchanged."""
        p = demo()
        lo = copy.deepcopy(p)
        hi = copy.deepcopy(p)
        for q, v in ((lo, 4000), (hi, 9000)):
            q.pop("wearables")
            q["observations_file"] = self._obsfile([{"code": "LP:steps_daily_mean", "value": v, "unit": "steps/day", "datetime": p["as_of"],
                                                     "method": "device", "flags": [], "sustained_weeks": 10}])
        a, b = run(lo), run(hi)
        self.assertEqual(a["longpi_age"]["value"], b["longpi_age"]["value"])
        self.assertGreater(b["index120"]["behavior"]["total_index"]["median"], a["index120"]["behavior"]["total_index"]["median"])
        # measured VO2max takes over part of it (mediation): the steps credit shrinks, so no double count
        hi2 = copy.deepcopy(hi)
        hi2.setdefault("fitness", []).append({"date": p["as_of"], "vo2max": 45.0, "method": "cpet"})
        c = run(hi2)
        sb = next(x for x in b["index120"]["behavior"]["behaviors"] if x["id"] == "ext.test_steps")
        sc = next(x for x in c["index120"]["behavior"]["behaviors"] if x["id"] == "ext.test_steps")
        self.assertLess(abs(math.log(sc["hr"])), abs(math.log(sb["hr"])))

    def test_behaviour_not_sustained(self):
        p = demo()
        p.pop("wearables")
        p["observations_file"] = self._obsfile([{"code": "LP:steps_daily_mean", "value": 9000, "unit": "steps/day", "datetime": p["as_of"],
                                                 "method": "device", "flags": [], "sustained_weeks": 3}])
        r = run(p)
        row = next(x for x in r["extension"]["terms"] if x["id"] == "ext.test_steps")
        self.assertEqual(row["status"], "not_sustained")
        self.assertEqual(r["index120"]["behavior"]["behavior_points"], 0.0)

    def test_prs_lifetime_vs_glucose_current(self):
        """Acceptance §9.6: PRS up -> lifetime rises more in absolute terms; glucose up -> 10-year rises more relatively."""
        p = demo()
        def with_obs(prs, fpg):
            q = copy.deepcopy(p)
            q.pop("wearables")
            for l in q["labs"]:
                l["items"].pop("glucose_fasting", None)
            q["labs"][-1]["items"]["glucose_fasting"] = [fpg, "mmol/L"]
            q["observations_file"] = self._obsfile([{"code": "PGS:PGS999999", "value": prs, "unit": "SD", "datetime": "2025-01-01",
                                                     "method": "tool", "flags": []}])
            r = run(q)
            return next(x for x in r["diseases"]["diseases"] if x["id"] == "t2d")
        base, prs, glu = with_obs(0.0, 5.2), with_obs(2.0, 5.2), with_obs(0.0, 6.6)
        self.assertGreater(prs["risk10"]["median"], base["risk10"]["median"])
        self.assertGreater(prs["lifetime"]["median"] - base["lifetime"]["median"], prs["risk10"]["median"] - base["risk10"]["median"])
        rel10 = glu["risk10"]["median"] / base["risk10"]["median"]
        rell = glu["lifetime"]["median"] / base["lifetime"]["median"]
        self.assertGreater(rel10, rell)

    def test_diagnosed(self):
        p = demo()
        p["conditions"] = [{"name": "2 型糖尿病", "icd10": "E11", "diagnosed": "2024"}]
        r = run(p)
        t2d = next(x for x in r["diseases"]["diseases"] if x["id"] == "t2d")
        self.assertEqual(t2d["status"], "diagnosed")

    def test_disclosure_defaults(self):
        p = demo()
        p["observations_file"] = self._obsfile([
            {"code": "LP:apoe_e4_count", "value": 2, "unit": "", "datetime": "2025-01-01", "method": "tool", "flags": []},
            {"code": "LP:monogenic:HGNC:1101", "value": 1, "unit": "", "datetime": "2025-01-01", "method": "tool", "flags": []}])
        r = run(p)
        ids = {x["id"] for x in r["extension"]["terms"]}
        self.assertNotIn("ext.test_apoe", ids)
        self.assertNotIn("ext.test_brca2", ids)
        self.assertEqual(r["extension"]["hidden_count"], 2)
        p["genetic_preferences"] = {"show_opt_in": True, "secondary_findings": True}
        r = run(p)
        ids = {x["id"] for x in r["extension"]["terms"]}
        self.assertIn("ext.test_apoe", ids)
        self.assertIn("ext.test_brca2", ids)

    def test_transient_and_treated(self):
        p = demo()
        p["labs"][-1]["items"]["apob"] = [1.6, "g/L"]
        p["labs"][-1]["flags"] = ["acute_illness"]
        r = run(p)
        row = next(x for x in r["extension"]["terms"] if x["id"] == "ext.test_apob")
        self.assertEqual(row["status"], "not_counted")
        q = demo()
        q["labs"][0]["items"]["apob"] = [1.4, "g/L"]
        q["labs"][-1]["items"]["apob"] = [0.8, "g/L"]
        q["medications"] = [{"name": "阿托伐他汀", "class": "statin", "since": q["labs"][-1]["date"]}]
        r = run(q)
        row = next(x for x in r["extension"]["terms"] if x["id"] == "ext.test_apob")
        self.assertAlmostEqual(row["level"], 1.4, delta=0.01)
        self.assertTrue(any("用药前" in n for n in row["notes"]))

    def test_deterministic(self):
        p = demo()
        p["labs"][-1]["items"]["apob"] = [1.2, "g/L"]
        a, b = run(p), run(p)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))
        self.assertEqual(a["extension"]["registry"]["version"], RG.load()["version"])


class Longitudinal(unittest.TestCase):
    def test_slope_recovered(self):
        from lp import longitudinal as LG
        rng = random.Random(4)
        rows = [{"t": 2015 + i, "value": 100 + 2.0 * i + rng.gauss(0, 1)} for i in range(10)]
        out = LG.level_and_slope(rows, [1.0] * 10, 2025.0, ref_sd=20.0)
        self.assertAlmostEqual(out["slope"], 2.0, delta=0.5)
        self.assertTrue(out["slope_informed"])
        one = LG.level_and_slope(rows[:1], [1.0], 2025.0, ref_sd=20.0)
        self.assertIsNone(one["slope"])


if __name__ == "__main__":
    unittest.main()
