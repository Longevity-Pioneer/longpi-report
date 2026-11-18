import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
from lp_omics import methylation  # noqa: E402

E2E = HERE.parents[2] / "skills" / "longpi-report" / "examples" / "e2e"
FIX = HERE / "fixtures"


def run_cli(*args, check=True):
    return subprocess.run([sys.executable, str(SCRIPTS / "omics.py"), *args], capture_output=True, text=True, check=check)


def write_matrix(path, beta: dict, sample="S1", ids=None):
    lines = [f"ID_REF,{sample}"]
    for k in (ids or sorted(beta)):
        v = beta.get(k)
        lines.append(f"{k},{'' if v is None else v}")
    path.write_text("\n".join(lines) + "\n")


class TestClockMath(unittest.TestCase):
    def setUp(self):
        self.clocks = methylation.load_coefs()

    def test_coefficient_counts(self):
        self.assertEqual(len(self.clocks["horvath"]["coef"]), 353)
        self.assertEqual(len(self.clocks["hannum"]["coef"]), 71)
        self.assertAlmostEqual(self.clocks["horvath"]["intercept"], 0.695507258, places=8)

    def test_anti_trafo(self):
        self.assertAlmostEqual(methylation.anti_trafo(0.0), 20.0)
        self.assertAlmostEqual(methylation.anti_trafo(1.0), 41.0)
        self.assertAlmostEqual(methylation.anti_trafo(-1.0), 21 * math.exp(-1) - 1)

    def test_all_missing_imputed_equals_median_profile(self):
        h = self.clocks["horvath"]
        med = methylation.compute_clock(h, dict(h["impute"]))
        # drop 10% -> imputed with the same medians -> identical value
        some = dict(list(sorted(h["impute"].items()))[35:])
        res = methylation.compute_clock(h, some)
        self.assertAlmostEqual(res["value"], med["value"], places=10)
        self.assertEqual(res["n_missing"], 35)

    def test_refuse_above_20pct_missing(self):
        h = self.clocks["horvath"]
        some = dict(list(sorted(h["impute"].items()))[80:])  # 80/353 = 22.7% missing
        res = methylation.compute_clock(h, some)
        self.assertFalse(res["computed"])


class TestPlatform(unittest.TestCase):
    def test_epic_v2_collapse_and_detect(self):
        ids = [f"cg{i:08d}_TC1{i % 2}" for i in range(100)]
        self.assertTrue(methylation.detect_platform(ids)["platform"].startswith("EPIC v2"))
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.csv"
            p.write_text("ProbeID,S1\ncg00000029_TC11,0.2\ncg00000029_TC12,0.4\ncg00000108_BC21,0.9\n")
            beta, plat = methylation.read_beta(str(p), None)
            self.assertAlmostEqual(beta["cg00000029"], 0.3)
            self.assertEqual(plat["platform"], "EPIC v2 (935K)")

    def test_counts(self):
        self.assertEqual(methylation.detect_platform(["cg%08d" % i for i in range(485000)])["platform"], "450K")
        self.assertEqual(methylation.detect_platform(["cg%08d" % i for i in range(866000)])["platform"], "EPIC v1 (850K)")

    def test_m_values_converted(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.csv"
            p.write_text("ID,S1\ncg1,0\ncg2,3.5\ncg3,-2\n")
            beta, plat = methylation.read_beta(str(p), None)
            self.assertAlmostEqual(beta["cg1"], 0.5)
            self.assertIn("M-value", plat["value_scale"])


class TestCLI(unittest.TestCase):
    def test_p1_e2e_deterministic_and_codes(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "a.json", Path(td) / "b.json"
            for o in (a, b):
                run_cli("methylation", str(E2E / "P1_methylation_beta.csv"), "--age", "48", "--sex", "M",
                        "--out", str(o), "--person-code", "P1", "--date", "2026-09-01")
            self.assertEqual(a.read_bytes(), b.read_bytes())
            doc = json.loads(a.read_text())
            codes = {o["code"]: o for o in doc["observations"]}
            for c in ("LP:clock.horvath", "LP:clock.horvath_accel", "LP:clock.hannum", "LP:clock.hannum_accel"):
                self.assertIn(c, codes)
            self.assertTrue(20 < codes["LP:clock.horvath"]["value"] < 80)
            self.assertFalse(any("phenoage" in c or "grimage" in c for c in codes))
            self.assertGreater(codes["LP:clock.horvath"]["missing_fraction"], 0)

    def test_sample_ids_not_in_output(self):
        h = methylation.load_coefs()["horvath"]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.csv"
            write_matrix(p, dict(h["impute"]), sample="GSM_SECRET_123")
            out = Path(td) / "o.json"
            run_cli("methylation", str(p), "--out", str(out))
            self.assertNotIn("GSM_SECRET_123", out.read_text())

    def test_vendor_passthrough_and_unknown_clock(self):
        with tempfile.TemporaryDirectory() as td:
            v = Path(td) / "v.json"
            v.write_text(json.dumps({"vendor": "Vendor Lab", "clocks": {"grimage2": {"value": 52.0, "accel": 2.5},
                                                                          "dunedinpace": {"value": 1.04}}}))
            out = Path(td) / "o.json"
            run_cli("methylation", "--vendor-json", str(v), "--out", str(out))
            doc = json.loads(out.read_text())
            codes = {o["code"]: o for o in doc["observations"]}
            self.assertEqual(codes["LP:clock.grimage2_accel"]["method"], "vendor")
            self.assertTrue(codes["LP:clock.grimage2_accel"]["vendor_derived"])
            self.assertEqual(codes["LP:clock.dunedinpace"]["value"], 1.04)
            v.write_text(json.dumps({"clocks": {"made_up_clock": {"value": 1}}}))
            r = run_cli("methylation", "--vendor-json", str(v), "--out", str(out), check=False)
            self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
