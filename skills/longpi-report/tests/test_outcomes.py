"""Disease outcome definitions (registry/outcomes) follow registry_contract.md section 4 and are source-verified."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lp import registry as RG  # noqa: E402

FIRST_13 = {"t2d", "chd", "stroke", "htn", "ckd", "masld", "crc", "lung_ca", "liver_ca", "gastric_ca", "breast_ca",
            "prostate_ca", "ad"}
SCREENABLE = {"crc", "lung_ca", "liver_ca", "gastric_ca", "breast_ca"}


class OutcomeRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = RG.load()
        cls.oc = cls.reg["outcomes"]

    def test_first_batch_present(self):
        self.assertTrue(FIRST_13 <= set(self.oc), sorted(FIRST_13 - set(self.oc)))

    def test_contract_fields(self):
        for oid, o in self.oc.items():
            for k in ("id", "name_zh", "icd10", "sex", "incidence", "diagnosed_codes", "horizon_lifetime_age", "license", "evidence"):
                self.assertIn(k, o, f"{oid}: {k}")
            self.assertEqual(o["incidence"]["unit"], "per_100k_py")
            self.assertEqual(o["horizon_lifetime_age"], 90)
            self.assertTrue(o["license"]["commercial_use"], oid)
            self.assertTrue(all(c.startswith("ICD10:") for c in o["diagnosed_codes"]), oid)
            for k in ("source", "year", "region", "quality_zh"):
                self.assertIn(k, o["incidence"], f"{oid}: incidence.{k}")

    def test_bands_disjoint_positive_and_sex_consistent(self):
        for oid, o in self.oc.items():
            rows = o["incidence"]["by_sex_age"]
            sexes = {r["sex"] for r in rows}
            self.assertEqual(sexes, {"M", "F"} if o["sex"] == "both" else {o["sex"]}, oid)
            for s in sexes:
                bands = sorted((r["age_lo"], r["age_hi"]) for r in rows if r["sex"] == s)
                for (a_lo, a_hi), (b_lo, _) in zip(bands, bands[1:]):
                    self.assertLess(a_hi, b_lo, f"{oid} {s} overlapping bands")
                self.assertLessEqual(bands[-1][1], 89, oid)
            # a band may be 0 only when documented as not modelled (AD under 60); every outcome must cover 30-89
            self.assertTrue(all(r["rate"] >= 0 for r in rows), oid)
            self.assertTrue(any(r["rate"] > 0 for r in rows), oid)
            for s in sexes:
                bands = sorted((r["age_lo"], r["age_hi"]) for r in rows if r["sex"] == s)
                self.assertEqual(bands[0][0], 30, f"{oid} {s}: must start at 30 (engine uses the nearest band outside the table)")
                self.assertTrue(all(b[0] == a[1] + 1 for a, b in zip(bands, bands[1:])), f"{oid} {s}: gap between bands")

    def test_definition_recorded(self):
        for oid, o in self.oc.items():
            self.assertTrue(o.get("definition_zh"), oid)

    def test_fine_bands_where_reviewed(self):
        """Prostate and CKD under 60 are in 5-year bands (no single diluted band)."""
        for oid, sex in (("prostate_ca", "M"), ("ckd", "M"), ("ckd", "F")):
            young = [r for r in self.oc[oid]["incidence"]["by_sex_age"] if r["sex"] == sex and r["age_hi"] < 60]
            self.assertTrue(all(r["age_hi"] - r["age_lo"] == 4 for r in young), oid)
            rates = [r["rate"] for r in sorted(young, key=lambda r: r["age_lo"])]
            self.assertEqual(rates, sorted(rates), oid)

    def test_mortality_share_for_screenable_cancers(self):
        for oid in SCREENABLE:
            ms = self.oc[oid]["mortality_share"]["by_sex_age"]
            self.assertTrue(ms, oid)
            self.assertTrue(all(0 < r["share"] < 0.5 for r in ms), oid)

    def test_sources_recorded_and_all_checks_found(self):
        for oid, o in self.oc.items():
            for key in o["incidence"].get("source_keys", []):
                src = RG.source(key)
                self.assertIsNotNone(src, f"{oid}: source {key} missing")
                self.assertEqual(len(src["sha256"]), 64)
                checks = [c for c in src["checks"] if c["term"] == f"outcome:{oid}"]
                self.assertTrue(all(c["found"] for c in src["checks"]), key)
                if key != "pmcid:PMC11256708":
                    self.assertTrue(checks, f"{oid}: no verification record in {key}")


if __name__ == "__main__":
    unittest.main()
