"""The methylation / proteomics / metabolomics / metagenome paths must never touch the network."""
import socket
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import omics  # noqa: E402

E2E = HERE.parents[2] / "skills" / "longpi-report" / "examples" / "e2e"


def _boom(*a, **k):
    raise AssertionError(f"network access attempted: {a[:1]}")


class TestOffline(unittest.TestCase):
    def test_no_network(self):
        cmds = [
            ["methylation", str(E2E / "P1_methylation_beta.csv"), "--age", "48", "--sex", "M"],
            ["metabolomics", str(E2E / "P1_nightingale.csv")],
            ["proteomics", str(E2E / "P2_somascan.csv"), "--age", "61", "--sex", "F"],
            ["metagenome", str(E2E / "P2_species_abundance.tsv")],
        ]
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(socket, "socket", _boom), \
                mock.patch.object(socket, "create_connection", _boom), \
                mock.patch.object(urllib.request, "urlopen", _boom):
            out = Path(td) / "obs.json"
            for c in cmds:
                self.assertEqual(omics.main(c + ["--out", str(out), "--person-code", "PX"]), 0)
            txt = out.read_text()
            self.assertNotIn("SYNTH_P", txt)  # sample column names stripped


if __name__ == "__main__":
    unittest.main()
