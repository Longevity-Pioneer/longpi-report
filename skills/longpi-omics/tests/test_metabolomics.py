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
from lp_omics import metabolomics  # noqa: E402

E2E = HERE.parents[2] / "skills" / "longpi-report" / "examples" / "e2e"


def run_cli(*args, check=True):
    return subprocess.run([sys.executable, str(SCRIPTS / "omics.py"), *args], capture_output=True, text=True, check=check)


def reference_profile(ref):
    """Marker values at the reference log-mean -> every z = 0 -> score 0."""
    out = {}
    for k, m in ref["markers"].items():
        x = math.exp(m["logMEAN"])
        out[k] = x - 1 if m.get("plus_one") else x
    return out


class TestScore(unittest.TestCase):
    def setUp(self):
        self.ref = metabolomics.load_ref()

    def test_fourteen_markers(self):
        self.assertEqual(len(self.ref["markers"]), 14)

    def test_reference_profile_scores_zero(self):
        s, _ = metabolomics.metabohealth_reference(reference_profile(self.ref), self.ref)
        self.assertAlmostEqual(s, 0.0, places=10)

    def test_one_sd_glycA(self):
        prof = reference_profile(self.ref)
        m = self.ref["markers"]["gp"]
        prof["gp"] = math.exp(m["logMEAN"] + m["logSD"])
        s, _ = metabolomics.metabohealth_reference(prof, self.ref)
        self.assertAlmostEqual(s, m["beta"], places=10)

    def test_dataset_mode_zero_rule(self):
        prof = reference_profile(self.ref)
        rows = []
        for i in range(5):
            r = {k: v * (1 + 0.05 * i) for k, v in prof.items()}
            r["acace"] = [0.0, 0.02, 0.04, 0.05, 0.08][i]
            r["glc"] = 4 + i
            rows.append(r)
        out = metabolomics.metabohealth_dataset(rows, self.ref)
        self.assertEqual(len(out), 5)
        self.assertTrue(all(v is not None for v in out))


class TestCLI(unittest.TestCase):
    def test_p1_e2e(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "a.json", Path(td) / "b.json"
            for o in (a, b):
                run_cli("metabolomics", str(E2E / "P1_nightingale.csv"), "--out", str(o), "--person-code", "P1",
                        "--date", "2026-09-01")
            self.assertEqual(a.read_bytes(), b.read_bytes())
            txt = a.read_text()
            doc = json.loads(txt)
            self.assertEqual([o["code"] for o in doc["observations"]], ["LP:metab.metabohealth"])
            self.assertNotIn("SYNTH_P1", txt)

    def test_albumin_gL_refused_and_missing_marker(self):
        ref = metabolomics.load_ref()
        prof = reference_profile(ref)
        names = {"pufa_fa": "PUFA_pct", "gp": "GlycA", "glc": "Glucose", "s_hdl_l": "S_HDL_L",
                 "xxl_vldl_l": "XXL_VLDL_L", "alb": "Albumin", "phe": "Phe", "acace": "Acetoacetate",
                 "ile": "Ile", "vldl_d": "VLDL_size", "leu": "Leu", "val": "Val", "his": "His", "lac": "Lactate"}
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "n.csv"
            cols = list(names)
            vals = [prof[k] for k in cols]
            vals[cols.index("alb")] = 41.0
            p.write_text("Sample," + ",".join(names[k] for k in cols) + "\nX1," + ",".join(f"{v:.6g}" for v in vals) + "\n")
            out = Path(td) / "o.json"
            run_cli("metabolomics", str(p), "--out", str(out))
            doc = json.loads(out.read_text())
            self.assertEqual(doc["observations"], [])
            self.assertIn("albumin", doc["provenance"][0]["skipped"])
            # 2020 names, albumin on the 2016 scale -> scored, ~0
            vals[cols.index("alb")] = prof["alb"]
            p.write_text("Sample," + ",".join(names[k] for k in cols) + "\nX1," + ",".join(f"{v:.10g}" for v in vals) + "\n")
            run_cli("metabolomics", str(p), "--out", str(out))
            doc = json.loads(out.read_text())
            self.assertAlmostEqual(doc["observations"][0]["value"], 0.0, places=3)
            # drop a marker -> not scored
            p.write_text("Sample," + ",".join(names[k] for k in cols[1:]) + "\nX1," +
                         ",".join(f"{v:.6g}" for v in vals[1:]) + "\n")
            run_cli("metabolomics", str(p), "--out", str(out))
            doc = json.loads(out.read_text())
            self.assertIn("pufa_fa", doc["provenance"][0]["skipped"])

    def test_glucose_mgdl_converted(self):
        ref = metabolomics.load_ref()
        vals, units, _ = {"glc": 90.08}, {"glc": "mg/dl"}, None
        m, missing, notes = metabolomics.map_markers(vals, units, ref)
        self.assertAlmostEqual(m["glc"], 90.08 / 18.016, places=6)
        self.assertTrue(notes)


if __name__ == "__main__":
    unittest.main()
