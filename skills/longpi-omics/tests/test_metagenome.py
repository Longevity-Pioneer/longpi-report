import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
from lp_omics import metagenome  # noqa: E402

FIX = HERE / "fixtures"
E2E = HERE.parents[2] / "skills" / "longpi-report" / "examples" / "e2e"


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPTS / "omics.py"), *args], capture_output=True, text=True, check=True)


class TestGMHI(unittest.TestCase):
    def test_hand_computed(self):
        # 2 health-prevalent species (0.3, 0.2), 1 health-scarce (0.1), filler 0.4
        ref = metagenome.load_gmhi()
        sp = {"s__Bifidobacterium_adolescentis": 30.0, "s__Sutterella_wadsworthensis": 20.0,
              "s__Eggerthella_lenta": 10.0, "s__Bacteroides_vulgatus": 40.0}
        g = metagenome.gmhi(sp, ref)
        psi_mh = (2 / 7) * -(0.3 * math.log(0.3) + 0.2 * math.log(0.2))
        psi_mn = (1 / 31) * -(0.1 * math.log(0.1))
        self.assertAlmostEqual(g["gmhi"], math.log10((psi_mh + 1e-5) / (psi_mn + 1e-5)), places=12)

    def test_floor_and_exclusion(self):
        ref = metagenome.load_gmhi()
        sp = {"s__Bifidobacterium_adolescentis": 50.0, "s__Eggerthella_lenta": 0.0001,
              "s__Bacteroides_unclassified": 49.9999}
        g = metagenome.gmhi(sp, ref)
        self.assertEqual(g["R_MN"], 0)  # 0.0001 / 50.0001 ~ 2e-6 < 1e-5 floor
        self.assertEqual(g["R_MH"], 1)

    def test_shannon_matches_scipy(self):
        from scipy.stats import entropy
        sp = {"s__a": 10.0, "s__b": 30.0, "s__c": 60.0}
        self.assertAlmostEqual(metagenome.shannon(sp), float(entropy([10, 30, 60])), places=12)

    def test_clr(self):
        c = metagenome.clr({"a": 1.0, "b": 0.0, "c": 4.0})
        self.assertAlmostEqual(sum(c.values()), 0.0, places=12)
        self.assertLess(c["b"], c["a"])


class TestDetection(unittest.TestCase):
    def test_16s_refused(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "amp.tsv"
            p.write_text("taxonomy\tS1\nD_0__Bacteria;D_1__Firmicutes;D_5__Blautia\t10\n"
                         "D_0__Bacteria;D_1__Bacteroidetes;D_5__Bacteroides\t90\n")
            out = Path(td) / "obs.json"
            run_cli("metagenome", str(p), "--out", str(out), "--person-code", "T1")
            doc = json.loads(out.read_text())
            self.assertEqual(doc["observations"], [])
            self.assertIn("16S", doc["provenance"][0]["skipped"])

    def test_detect_genus_only(self):
        k = metagenome.detect_kind(["k__Bacteria|p__Firmicutes|g__Blautia", "k__Bacteria|p__Bacteroidetes|g__Bacteroides"])
        self.assertEqual(k["kind"], "16S/amplicon")

    def test_low_depth_refused(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "obs.json"
            run_cli("metagenome", str(E2E / "P2_species_abundance.tsv"), "--out", str(out), "--reads", "50000")
            doc = json.loads(out.read_text())
            self.assertEqual(doc["observations"], [])


class TestE2E(unittest.TestCase):
    def test_p2_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "a.json", Path(td) / "b.json"
            for o in (a, b):
                run_cli("metagenome", str(E2E / "P2_species_abundance.tsv"), "--out", str(o), "--person-code", "P2",
                        "--date", "2026-10-20")
            self.assertEqual(a.read_bytes(), b.read_bytes())
            doc = json.loads(a.read_text())
            codes = {o["code"]: o for o in doc["observations"]}
            self.assertIn("LP:micro.gmhi", codes)
            self.assertIn("LP:micro.shannon", codes)

    def test_sample_ids_stripped(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "m.tsv"
            p.write_text("clade_name\tSECRETSAMPLE01\tOTHERSAMPLE02\n"
                         "k__Bacteria|p__Actinobacteria|g__Bifidobacterium|s__Bifidobacterium_adolescentis\t60\t10\n"
                         "k__Bacteria|p__Bacteroidetes|g__Bacteroides|s__Bacteroides_vulgatus\t40\t90\n")
            out = Path(td) / "obs.json"
            run_cli("metagenome", str(p), "--sample", "SECRETSAMPLE01", "--out", str(out))
            txt = out.read_text()
            self.assertNotIn("SECRETSAMPLE01", txt)
            self.assertNotIn("OTHERSAMPLE02", txt)


if __name__ == "__main__":
    unittest.main()
