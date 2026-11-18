"""Fixes from the Sonnet end-to-end run: two genotype files per person, truncated cached downloads."""
import gzip
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))

import omics  # noqa: E402
from lp_omics import common  # noqa: E402

E2E = HERE.parents[1] / "longpi-report" / "examples" / "e2e"


class TwoGenotypeFiles(unittest.TestCase):
    def setUp(self):
        self._env = os.environ.get("LONGPI_OMICS_OFFLINE")

    def tearDown(self):
        # the CLI's --offline sets a process-wide flag; do not leak it into other tests
        if self._env is None:
            os.environ.pop("LONGPI_OMICS_OFFLINE", None)
        else:
            os.environ["LONGPI_OMICS_OFFLINE"] = self._env

    def _run(self, order):
        td = Path(tempfile.mkdtemp())
        out = td / "obs.json"
        for f in order:
            omics.main(["genotype", str(E2E / f), "--out", str(out), "--person-code", "P2", "--sex", "F",
                        "--pgs", "PGS002262", "--offline", "--registry", str(td / "none")])
        return json.loads(out.read_text(encoding="utf-8"))

    def test_chip_then_wgs_and_wgs_then_chip_keep_both(self):
        for order in (("P2_chip_23andme_GRCh37.txt", "P2_wgs_LDLR_GRCh38.vcf"),
                      ("P2_wgs_LDLR_GRCh38.vcf", "P2_chip_23andme_GRCh37.txt")):
            d = self._run(order)
            codes = {o["code"] for o in d["observations"]}
            self.assertIn("LP:monogenic:HGNC:6547", codes, order)
            self.assertIn("LP:apoe_e4_count", codes, order)
            self.assertIn("PGS:PGS002262", codes, order)
            self.assertTrue(d["genetics"].get("pgx"), order)
            self.assertIn("chip", d["genetics"]["source_file"], order)


class CorruptCache(unittest.TestCase):
    def test_truncated_gzip_is_not_reused(self):
        td = Path(tempfile.mkdtemp())
        good = td / "x.txt.gz"
        with gzip.open(good, "wb") as fh:
            fh.write(b"a" * 200000)
        raw = good.read_bytes()
        good.write_bytes(raw[: len(raw) // 2])
        self.assertFalse(common.cached_ok(good))
        self.assertFalse(good.exists())


if __name__ == "__main__":
    unittest.main()
