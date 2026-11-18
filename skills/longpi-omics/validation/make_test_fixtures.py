#!/usr/bin/env python3
"""Copy a small offline reference cache for the unit tests into tests/fixtures/omics-ref (public data only)."""
import gzip
import json
import random
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import common  # noqa: E402
from lp_omics.genotype import clinvar, gtio, prs  # noqa: E402

FIX = HERE.parent / "tests" / "fixtures" / "omics-ref"
E2E = HERE.parents[1] / "longpi-report" / "examples" / "e2e"
PGS = ["PGS002262", "PGS003353", "PGS000050", "PGS000070"]


def main():
    if FIX.exists():
        shutil.rmtree(FIX)
    src = common.ref_dir()
    (FIX / "1kg").mkdir(parents=True)
    shutil.copy(src / "1kg" / "integrated_call_samples_v3.20130502.ALL.panel", FIX / "1kg")
    for pid in PGS + ["PGS000013"]:
        d = FIX / "pgs" / pid
        d.mkdir(parents=True)
        prs.fetch_metadata(pid)
        for f in sorted((src / "pgs" / pid).iterdir()):
            if f.name.endswith((".txt.gz", "_meta.json", "_ref.json.gz")) and "PGS000013_hmPOS" not in f.name:
                shutil.copy(f, d / f.name)
    # ClinVar mini caches: every reportable record at a position present in the E2E genotype files,
    # the planted variant, plus 300 random reportable/benign records per build
    rnd = random.Random(3)
    pos = {"GRCh38": set(), "GRCh37": set()}
    for f, b in ((E2E / "P1_genotypes_GRCh38.vcf", "GRCh38"), (E2E / "P2_wgs_LDLR_GRCh38.vcf", "GRCh38"),
                 (HERE.parent / "tests" / "fixtures" / "genotype" / "P1_genotypes_GRCh37_lifted.vcf", "GRCh37")):
        for line in open(f):
            if not line.startswith("#"):
                c, p = line.split("\t")[:2]
                pos[b].add((gtio.norm_chrom(c), int(p)))
    for line in open(E2E / "P2_chip_23andme_GRCh37.txt"):
        if not line.startswith("#"):
            f = line.split("\t")
            pos["GRCh37"].add((gtio.norm_chrom(f[1]), int(f[2])))
    planted = json.loads((E2E / "genotype_sources.json").read_text())["planted_P2"]["clinvar_id"]
    for b in ("GRCh38", "GRCh37"):
        cv = clinvar.load_cache(b)
        keep = {k: r for k, r in cv["records"].items() if (r["chrom"], r["pos"]) in pos[b] or r["id"] == planted}
        others = sorted(k for k in cv["records"] if k not in keep)
        for k in rnd.sample(others, 300):
            keep[k] = cv["records"][k]
        doc = {k: v for k, v in cv.items() if k != "records"}
        doc.update({"n": len(keep), "records": keep, "fixture_note": "subset of the real ClinVar ACMG SF cache for tests"})
        d = FIX / "clinvar" / b
        d.mkdir(parents=True)
        with gzip.open(d / "clinvar_acmg_sf.json.gz", "wt", encoding="utf-8") as fh:
            json.dump(doc, fh, sort_keys=True)
    (HERE.parent / "tests" / "fixtures" / "no_terms").mkdir(exist_ok=True)
    (HERE.parent / "tests" / "fixtures" / "no_terms" / ".keep").write_text("")
    tot = sum(f.stat().st_size for f in FIX.rglob("*") if f.is_file())
    print("fixture bytes", tot)


if __name__ == "__main__":
    main()
