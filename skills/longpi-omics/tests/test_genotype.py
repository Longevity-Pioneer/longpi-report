"""Offline tests for the genotype pipeline (fixtures: tests/fixtures/omics-ref, examples/e2e)."""
import gzip
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SCRIPTS = SKILL / "scripts"
E2E = SKILL.parent / "longpi-report" / "examples" / "e2e"
FIX = HERE / "fixtures"
REF = FIX / "omics-ref"
sys.path.insert(0, str(SCRIPTS))

from lp_omics import common  # noqa: E402
from lp_omics.genotype import clinvar, core, gtio, pgx, prs  # noqa: E402

PGS = ["PGS000070", "PGS002262"]


def run_cli(*args, ref=REF, env_extra=None):
    env = dict(os.environ, LONGPI_OMICS_REF=str(ref), **(env_extra or {}))
    r = subprocess.run([sys.executable, str(SCRIPTS / "omics.py"), *args], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise AssertionError(r.stdout + r.stderr)
    return r.stdout


def genotype(inp, out, *extra):
    args = ["genotype", str(inp), "--out", str(out), "--offline", "--registry", str(FIX / "no_terms")]
    for p in PGS:
        args += ["--pgs", p]
    return run_cli(*args, *extra)


class TestGenotypeE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.td = Path(tempfile.mkdtemp())
        cls.p1 = cls.td / "p1.json"
        genotype(E2E / "P1_genotypes_GRCh38.vcf", cls.p1, "--person-code", "P1", "--sex", "M")
        cls.doc1 = json.loads(cls.p1.read_text())

    def test_schema_and_blocks(self):
        d = self.doc1
        self.assertEqual(d["schema"], "longpi.observations/1")
        g = d["genetics"]
        for k in ("build", "source_type", "qc", "ancestry", "prs", "apoe", "monogenic", "pgx"):
            self.assertIn(k, g)
        self.assertEqual(g["build"], "GRCh38")
        self.assertEqual(g["qc"]["inferred_sex"], "M")
        self.assertEqual(g["qc"]["sex_check"], "ok")
        self.assertGreater(g["ancestry"]["EAS"], 0.8)
        codes = {o["code"] for o in d["observations"]}
        self.assertIn("LP:apoe_e4_count", codes)
        for o in d["observations"]:
            for k in ("obs_id", "code", "value", "unit", "datetime", "method", "platform", "specimen",
                      "source_file", "source_locator", "sd", "flags", "tool", "vendor_derived", "sustained_weeks"):
                self.assertIn(k, o)

    def test_prs_scored_with_reference(self):
        prs_ = {r["pgs_id"]: r for r in self.doc1["genetics"]["prs"]}
        for p in PGS:
            r = prs_[p]
            self.assertTrue(r["scored"], r)
            self.assertGreaterEqual(r["coverage"], 0.8)
            self.assertEqual(r["ref"], "1000G EAS (n 504)")
            self.assertTrue(0 <= r["percentile"] <= 100)
            self.assertTrue(-6 < r["z"] < 6)

    def test_no_sample_id_or_paths(self):
        text = self.p1.read_text()
        self.assertNotIn(str(Path.home()), text)
        for sid in json.loads((FIX / "genotype" / "forbidden_strings.json").read_text()):
            self.assertNotIn(sid, text)

    def test_determinism(self):
        out2 = self.td / "p1b.json"
        genotype(E2E / "P1_genotypes_GRCh38.vcf", out2, "--person-code", "P1", "--sex", "M")
        self.assertEqual(self.p1.read_bytes(), out2.read_bytes())

    def test_grch37_lift_identical(self):
        out37 = self.td / "p1_37.json"
        genotype(FIX / "genotype" / "P1_genotypes_GRCh37_lifted.vcf", out37, "--person-code", "P1", "--sex", "M")
        d37 = json.loads(out37.read_text())
        g37, g38 = d37["genetics"], self.doc1["genetics"]
        self.assertEqual(g37["build"], "GRCh37")
        self.assertEqual(g37["apoe"], g38["apoe"])
        for a, b in zip(g37["prs"], g38["prs"]):
            self.assertEqual((a["pgs_id"], a["raw"], a["z"], a["percentile"]), (b["pgs_id"], b["raw"], b["z"], b["percentile"]))
        self.assertEqual([m["clinvar_id"] for m in g37["monogenic"]], [m["clinvar_id"] for m in g38["monogenic"]])
        self.assertEqual([(x["gene"], x["diplotype"]) for x in g37["pgx"]], [(x["gene"], x["diplotype"]) for x in g38["pgx"]])

    def test_chip_and_planted_variant(self):
        out = self.td / "p2.json"
        genotype(E2E / "P2_chip_23andme_GRCh37.txt", out, "--person-code", "P2", "--sex", "F")
        genotype(E2E / "P2_wgs_LDLR_GRCh38.vcf", self.td / "p2wgs.json", "--person-code", "P2", "--source-type", "wgs")
        d = json.loads(out.read_text())
        self.assertEqual(d["genetics"]["build"], "GRCh37")
        self.assertEqual(d["genetics"]["source_type"], "chip")
        self.assertEqual(d["genetics"]["qc"]["inferred_sex"], "F")
        w = json.loads((self.td / "p2wgs.json").read_text())
        mono = w["genetics"]["monogenic"]
        self.assertEqual([m["gene"] for m in mono], ["LDLR"])
        self.assertTrue(mono[0]["counts_in_engine"])
        self.assertIn("LP:monogenic:HGNC:6547", {o["code"] for o in w["observations"]})

    def test_chip_rare_call_not_counted(self):
        # the planted LDLR variant written as a chip line: listed, never counted
        chip = self.td / "chip_plp.txt"
        src = json.loads((E2E / "genotype_sources.json").read_text())["planted_P2"]
        cv37 = clinvar.load_cache("GRCh37", REF / "clinvar" / "GRCh37" / "clinvar_acmg_sf.json.gz")
        rec = next(r for r in cv37["records"].values() if r["id"] == src["clinvar_id"])
        lines = (E2E / "P2_chip_23andme_GRCh37.txt").read_text()
        chip.write_text(lines + f"rs000\t{rec['chrom']}\t{rec['pos']}\t{rec['ref']}{rec['alt']}\n")
        out = self.td / "chip_plp.json"
        genotype(chip, out, "--person-code", "P2", "--build", "GRCh37")
        d = json.loads(out.read_text())
        mono = d["genetics"]["monogenic"]
        self.assertEqual(len(mono), 1)
        self.assertFalse(mono[0]["counts_in_engine"])
        self.assertFalse(mono[0]["confirmed_clinical"])
        self.assertIn("Weedon", mono[0]["note"])
        self.assertFalse(any(o["code"].startswith("LP:monogenic") for o in d["observations"]))

    def test_merge_idempotent(self):
        out = self.td / "merge.json"
        doc = common.new_doc("P1")
        doc["observations"].append(common.make_obs("LOINC:1884-6", 1.1, unit="g/L", method="lab", tool=None))
        common.write_doc(doc, out)
        genotype(E2E / "P1_genotypes_GRCh38.vcf", out, "--person-code", "P1")
        genotype(E2E / "P1_genotypes_GRCh38.vcf", out, "--person-code", "P1")
        d = json.loads(out.read_text())
        self.assertEqual(sum(o["code"] == "LOINC:1884-6" for o in d["observations"]), 1)
        self.assertEqual(sum(o["code"] == "LP:apoe_e4_count" for o in d["observations"]), 1)


class TestUnits(unittest.TestCase):
    def test_trim_and_spdi(self):
        self.assertEqual(clinvar.trim(100, "TA", "T"), (101, "A", ""))
        self.assertEqual(clinvar.trim(100, "A", "AGT"), (101, "", "GT"))
        self.assertEqual(clinvar.spdi("GRCh38", "13", 32340300, "GA", "G"), "NC_000013.11:32340300:A:")

    def test_review_stars(self):
        self.assertEqual(clinvar.review_stars("reviewed_by_expert_panel"), 3)
        self.assertEqual(clinvar.review_stars("criteria_provided,_single_submitter"), 1)
        self.assertFalse(clinvar.reportable({"clnsig": "Conflicting_classifications_of_pathogenicity",
                                             "revstat": "criteria_provided,_multiple_submitters,_no_conflicts"}))
        self.assertFalse(clinvar.reportable({"clnsig": "Pathogenic", "revstat": "criteria_provided,_single_submitter"}))
        self.assertTrue(clinvar.reportable({"clnsig": "Likely_pathogenic", "revstat": "reviewed_by_expert_panel"}))

    def test_license_filter(self):
        self.assertTrue(prs.license_allowed(prs.DEFAULT_LICENSE))
        self.assertTrue(prs.license_allowed("Creative Commons Attribution 4.0 International (CC BY 4.0)"))
        for bad in ["Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY-NC-ND 4.0)",
                    "Freely available to the academic community for research use. Parties interested in using the scores "
                    "for commercial purposes should contact the Broad Office",
                    "This PRS model is provided for academic research purposes only, not-for-profit use."]:
            self.assertFalse(prs.license_allowed(bad), bad)

    def test_license_refused_in_cli(self):
        td = Path(tempfile.mkdtemp())
        out = td / "o.json"
        run_cli("genotype", str(E2E / "P1_genotypes_GRCh38.vcf"), "--out", str(out), "--offline",
                "--registry", str(FIX / "no_terms"), "--pgs", "PGS000013", "--no-clinvar")
        d = json.loads(out.read_text())
        r = d["genetics"]["prs"][0]
        self.assertFalse(r["scored"])
        self.assertIn("licence", r["reason"])
        self.assertFalse(any(o["code"] == "PGS:PGS000013" for o in d["observations"]))

    def test_low_coverage_not_scored(self):
        sf = prs.ScoreFile("PGS000070", "GRCh38", REF / "pgs" / "PGS000070" / "PGS000070_hmPOS_GRCh38.txt.gz")
        ref = prs.load_reference("PGS000070") if False else json.load(
            gzip.open(REF / "pgs" / "PGS000070" / "PGS000070_EAS1kg_ref.json.gz", "rt"))
        g = gtio.Genotypes("vcf", "wgs", {}, {}, {}, {"records": 0}, [], 0, [])
        r = prs.score_person(g, sf, ref)
        self.assertFalse(r["scored"])
        self.assertIsNone(r["z"])

    def test_dosage_alignment(self):
        g = gtio.Genotypes("chip", "chip", {}, {("1", 10): [gtio.Call("1", 10, None, (), ("T", "T"), None)],
                                                  ("1", 11): [gtio.Call("1", 11, None, (), ("A", "T"), None)]},
                           {}, {"records": 2}, [], 0, [])
        self.assertEqual(gtio.dosage(g, "1", 10, "A", "G"), (2, "flipped"))   # T/T on the other strand = A/A
        self.assertEqual(gtio.dosage(g, "1", 11, "A", "T"), (1, "ok"))        # palindromic, taken as + strand
        self.assertEqual(gtio.dosage(g, "1", 12, "A", "G"), (None, "absent"))

    def test_apoe_table(self):
        panel = core.load_panel()

        def mk(a, b):
            calls = {}
            for rs, al in (("rs429358", a), ("rs7412", b)):
                s = panel[rs]
                calls[(s["chrom"], s["pos_GRCh38"])] = [gtio.Call(s["chrom"], s["pos_GRCh38"], None, (), al, rs)]
            return gtio.Genotypes("chip", "chip", {}, calls, {}, {"records": 2}, [], 0, [])
        self.assertEqual(core.apoe(mk(("T", "T"), ("C", "C")), "GRCh38", panel)["genotype"], "e3/e3")
        self.assertEqual(core.apoe(mk(("C", "T"), ("C", "C")), "GRCh38", panel)["genotype"], "e3/e4")
        a = core.apoe(mk(("C", "C"), ("C", "C")), "GRCh38", panel)
        self.assertEqual((a["genotype"], a["e4_count"], a["disclosure"]), ("e4/e4", 2, "opt_in"))
        self.assertEqual(core.apoe(mk(("T", "T"), ("C", "T")), "GRCh38", panel)["genotype"], "e2/e3")

    def test_pgx_rules(self):
        panel = core.load_panel()

        def person(spec):
            calls = {}
            for rs, al in spec.items():
                s = panel[rs]
                calls[(s["chrom"], s["pos_GRCh38"])] = [gtio.Call(s["chrom"], s["pos_GRCh38"], None, (), al, rs)]
            return gtio.Genotypes("chip", "chip", {}, calls, {}, {"records": len(spec)}, [], 0, [])
        r = {x["gene"]: x for x in pgx.call_all(person({"rs4244285": ("G", "A"), "rs4986893": ("G", "A"),
                                                         "rs12248560": ("C", "C"), "rs1800460": ("C", "T"),
                                                         "rs1142345": ("T", "C"), "rs1799853": ("C", "T"),
                                                         "rs1057910": ("A", "C"), "rs776746": ("C", "C")}), "GRCh38", panel)}
        self.assertEqual(r["CYP2C19"]["diplotype"], "*2/*3")
        self.assertEqual(r["CYP2C19"]["phenotype"], "慢代谢型")
        self.assertEqual(r["TPMT"]["diplotype"], "*1/*3A")
        self.assertEqual(r["TPMT"]["phenotype"], "中间代谢型")
        self.assertTrue(r["CYP2C9"]["phenotype"].startswith("慢代谢型"))  # *2/*3: activity score 0.5 = poor (CPIC)
        self.assertEqual(r["CYP3A5"]["phenotype"], "慢代谢型（非表达者）")

    def test_build_detection_by_markers(self):
        panel = core.load_panel()
        calls, by = {}, {}
        for s in list(panel.values())[:20]:
            calls[(s["chrom"], s["pos_GRCh37"])] = [gtio.Call(s["chrom"], s["pos_GRCh37"], None, (), ("A", "A"), s["rsid"])]
            by[s["rsid"]] = (s["chrom"], s["pos_GRCh37"])
        g = gtio.Genotypes("chip", "chip", {}, calls, by, {"records": 20}, [], 0, [])
        self.assertEqual(core.detect_build(g, panel)["build"], "GRCh37")


if __name__ == "__main__":
    unittest.main()
