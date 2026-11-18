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
from lp_omics import proteomics  # noqa: E402

E2E = HERE.parents[2] / "skills" / "longpi-report" / "examples" / "e2e"


def run_cli(*args, check=True):
    return subprocess.run([sys.executable, str(SCRIPTS / "omics.py"), *args], capture_output=True, text=True, check=check)


class TestParsing(unittest.TestCase):
    def test_seqid_forms(self):
        self.assertEqual(proteomics.norm_seqid("seq.10000.28"), "10000-28")
        self.assertEqual(proteomics.norm_seqid("10000-28"), "10000-28")
        self.assertIsNone(proteomics.norm_seqid("OID00123"))

    def test_version_by_count(self):
        self.assertEqual(proteomics.detect_soma_version(5284), "v4")
        self.assertEqual(proteomics.detect_soma_version(7288), "v4.1")
        self.assertEqual(proteomics.detect_soma_version(10776), "v5")
        self.assertIsNone(proteomics.detect_soma_version(300))

    def test_olink_long_passthrough_only(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "olink.csv"
            p.write_text("SampleID,OlinkID,UniProt,Assay,NPX\nXSECRET1,OID20125,Q99988,GDF15,5.12\n"
                         "XSECRET1,OID20000,P01034,CST3,7.80\nXSECRET1,OID29999,P99999,OTHER,1.0\n")
            out = Path(td) / "o.json"
            run_cli("proteomics", str(p), "--out", str(out), "--age", "60", "--sex", "F")
            txt = out.read_text()
            doc = json.loads(txt)
            codes = {o["code"]: o for o in doc["observations"]}
            self.assertEqual(set(codes), {"UNIPROT:Q99988", "UNIPROT:P01034"})
            self.assertEqual(codes["UNIPROT:Q99988"]["unit"], "NPX")
            self.assertEqual(codes["UNIPROT:Q99988"]["platform_probe"], "OID20125")
            self.assertNotIn("XSECRET1", txt)


class TestOrganAge(unittest.TestCase):
    def test_flattened_model_linear(self):
        oa = proteomics.load_organage()
        heart = oa["organs"]["Heart"]
        logv = {p["seqid"]: p["mean"] for p in heart["proteins"]}  # all z = 0
        pred, missing = proteomics.organ_age(heart, logv, 1)
        self.assertEqual(missing, [])
        self.assertAlmostEqual(pred, heart["intercept"] + heart["coef_sex_f"], places=10)

    def test_missing_protein_refuses(self):
        heart = proteomics.load_organage()["organs"]["Heart"]
        logv = {p["seqid"]: p["mean"] for p in heart["proteins"][1:]}
        pred, missing = proteomics.organ_age(heart, logv, 0)
        self.assertIsNone(pred)
        self.assertEqual(len(missing), 1)

    def test_interp(self):
        self.assertAlmostEqual(proteomics.interp_linear_extrapolate([1, 2, 3], [10, 20, 30], 2.5), 25)
        self.assertAlmostEqual(proteomics.interp_linear_extrapolate([1, 2, 3], [10, 20, 30], 4), 40)
        self.assertAlmostEqual(proteomics.interp_linear_extrapolate([1, 2, 3], [10, 20, 30], 0), 0)

    def test_p2_e2e(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "a.json", Path(td) / "b.json"
            for o in (a, b):
                run_cli("proteomics", str(E2E / "P2_somascan.csv"), "--age", "61", "--sex", "F",
                        "--out", str(o), "--person-code", "P2", "--date", "2026-10-20")
            self.assertEqual(a.read_bytes(), b.read_bytes())
            doc = json.loads(a.read_text())
            codes = {o["code"]: o for o in doc["observations"]}
            self.assertIn("LP:prot.organage_heart_gap", codes)
            self.assertIn("LP:prot.organage_organismal_gap", codes)
            self.assertEqual(sum(1 for c in codes if c.startswith("LP:prot.organage_")), 13)
            self.assertIn("UNIPROT:P16860", codes)
            self.assertEqual(codes["UNIPROT:P16860"]["platform_probe"], "7655-11")
            self.assertEqual(codes["LP:prot.organage_heart_gap"]["platform"], "SomaScan v4")
            for c, o in codes.items():
                if c.startswith("LP:prot."):
                    self.assertLess(abs(o["value"]), 25)

    def test_no_age_no_clock(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "o.json"
            run_cli("proteomics", str(E2E / "P2_somascan.csv"), "--out", str(out))
            doc = json.loads(out.read_text())
            self.assertFalse(any(o["code"].startswith("LP:prot.") for o in doc["observations"]))
            self.assertIn("skipped", doc["provenance"][0])


if __name__ == "__main__":
    unittest.main()
