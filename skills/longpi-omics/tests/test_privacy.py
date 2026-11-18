"""P0 privacy: no outgoing request may carry a person's genotypes, values, sample IDs or file contents.

The genotype pipeline is run in-process against an EMPTY reference cache so that every download path
is exercised (PGS metadata + scoring files, 1000G EAS reference build via bcftools, ClinVar subset via
bcftools). urllib and subprocess are monkeypatched: every URL, header, body, command line and region
file is captured and checked. Requested genomic positions must be a subset of public positions
(score variants, fixed SNP panel, ACMG SF gene regions) - never positions taken from the person.
"""
import gzip
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
E2E = HERE.parent.parent / "longpi-report" / "examples" / "e2e"
FIXREF = HERE / "fixtures" / "omics-ref"
sys.path.insert(0, str(SCRIPTS))

import omics  # noqa: E402
from lp_omics import common  # noqa: E402
from lp_omics.genotype import clinvar, core, prs  # noqa: E402

PERSON_VCF = E2E / "P1_genotypes_GRCh38.vcf"


class Capture:
    def __init__(self):
        self.urls, self.bodies, self.headers, self.cmds, self.region_files = [], [], [], [], []

    def urlopen(self, req, *a, **k):
        url = req.full_url if isinstance(req, urllib.request.Request) else req
        data = req.data if isinstance(req, urllib.request.Request) else k.get("data")
        self.urls.append(url)
        self.bodies.append(data)
        if isinstance(req, urllib.request.Request):
            self.headers.append(dict(req.header_items()))
        name = url.rsplit("/", 1)[-1]
        hits = [h for h in list(FIXREF.rglob(name)) + list(FIXREF.rglob(name + "_meta.json")) if h.is_file()]
        if not hits:
            raise OSError(f"no fixture for {url}")
        return io.BytesIO(hits[0].read_bytes())

    def run(self, cmd, *a, **k):
        self.cmds.append(list(map(str, cmd)))
        for i, x in enumerate(cmd):
            if x in ("-R", "-S") and i + 1 < len(cmd):
                self.region_files.append(Path(cmd[i + 1]).read_text())
        if "view" in cmd and "-o" in cmd:  # ClinVar subset: write a minimal valid VCF
            out = Path(cmd[cmd.index("-o") + 1])
            with gzip.open(out, "wt") as fh:
                fh.write("##fileformat=VCFv4.1\n##fileDate=2026-11-15\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")


class TestPrivacy(unittest.TestCase):
    def test_no_person_data_leaves_the_machine(self):
        td = Path(tempfile.mkdtemp())
        ref = td / "ref"
        ref.mkdir()
        out = td / "obs.json"
        cap = Capture()
        env = {"LONGPI_OMICS_REF": str(ref)}
        with mock.patch.dict(os.environ, env), \
                mock.patch.object(urllib.request, "urlopen", cap.urlopen), \
                mock.patch.object(subprocess, "run", cap.run):
            omics.main(["genotype", str(PERSON_VCF), "--out", str(out), "--person-code", "P1",
                        "--pgs", "PGS000070", "--registry", str(td / "none")])
        self.assertTrue(cap.urls, "the run should have fetched public resources")
        # 1) only allow-listed public hosts, no query strings, no request bodies
        for u in cap.urls:
            common.check_public_url(u)
        self.assertTrue(all(b is None for b in cap.bodies))
        # 2) nothing from the person file in URLs, headers, commands or region files
        person = PERSON_VCF.read_text().splitlines()
        sample_col = [l for l in person if l.startswith("#CHROM")][0].split("\t")[9]
        tokens = {sample_col, PERSON_VCF.name, str(PERSON_VCF), "P1"}
        blob = "\n".join(cap.urls + [json.dumps(h) for h in cap.headers] + [" ".join(c) for c in cap.cmds]
                         + cap.region_files)
        for t in tokens:
            self.assertNotIn(t, blob.replace("samples_2504", ""), t)
        self.assertNotIn("0/1", blob)
        self.assertNotIn("0|1", blob)
        # 3) every requested position is public (score variants / panel / ACMG gene regions)
        public = set()
        sf = prs.ScoreFile("PGS000070", "GRCh38", ref / "pgs" / "PGS000070" / "PGS000070_hmPOS_GRCh38.txt.gz")
        for _, c, p, *_ in sf.variants():
            public.add((c, p))
        for s in core.load_panel().values():
            public.add((s["chrom"], s["pos_GRCh38"]))
        acmg = [v["region_GRCh38"] for v in clinvar.load_genes()["genes"].values()]
        n_pos = 0
        for txt in cap.region_files:
            for line in txt.splitlines():
                f = line.split("\t")
                if len(f) != 3:
                    continue  # sample list file (public 1000G ids)
                c, a, b = f[0].replace("chr", ""), int(f[1]), int(f[2])
                n_pos += 1
                ok = (c, a) in public or any(c == r[0] and r[1] - 5000 <= a and b <= r[2] + 5000 for r in acmg)
                self.assertTrue(ok, f"non-public position requested: {line}")
        self.assertGreater(n_pos, 0)
        # 4) sample lists sent to bcftools are public 1000G identifiers only
        ids = {s for s, *_ in __import__("lp_omics.genotype.kg", fromlist=["x"]).sample_panel()}
        for c in cap.cmds:
            if "-S" in c:
                names = Path(c[c.index("-S") + 1]).read_text().split()
                self.assertTrue(set(names) <= ids)

    def test_url_guard(self):
        for bad in ["https://evil.example.com/x", "file:///etc/passwd",
                    "https://ftp.ebi.ac.uk/pub/x?genotype=AG", "ftp://ftp.ncbi.nlm.nih.gov/x"]:
            with self.assertRaises(common.PrivacyError):
                common.check_public_url(bad)


if __name__ == "__main__":
    unittest.main()
