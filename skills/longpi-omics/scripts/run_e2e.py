#!/usr/bin/env python3
"""Write observations.json for the synthetic E2E people from their omics inputs.

  python3 skills/longpi-omics/scripts/run_e2e.py                    # -> examples/e2e/people/P{1,2}/observations.json
  python3 skills/longpi-omics/scripts/run_e2e.py --people-dir DIR   # other location
  python3 skills/longpi-omics/scripts/run_e2e.py --print            # only print the commands

Each person's file is rebuilt from scratch (deleted first), so reruns are byte-identical.
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E2E = HERE.parents[1] / "longpi-report" / "examples" / "e2e"
PGS = ["PGS002262", "PGS003353", "PGS000050", "PGS000070"]


def commands(person: str, out: Path) -> list[list[str]]:
    o = ["--out", str(out), "--person-code", person]
    pg = sum((["--pgs", p] for p in PGS), [])
    if person == "P1":
        return [
            ["genotype", str(E2E / "P1_genotypes_GRCh38.vcf"), *o, "--sex", "M", "--date", "2026-05-18", *pg],
            ["methylation", str(E2E / "P1_methylation_beta.csv"), *o, "--age", "48", "--sex", "M", "--date", "2026-05-18"],
            ["metabolomics", str(E2E / "P1_nightingale.csv"), *o, "--date", "2026-05-18"],
        ]
    return [
        ["genotype", str(E2E / "P2_chip_23andme_GRCh37.txt"), *o, "--sex", "F", *pg],
        ["genotype", str(E2E / "P2_wgs_LDLR_GRCh38.vcf"), *o, "--source-type", "wgs", "--monogenic-only",
         "--date", "2026-06-02"],
        ["proteomics", str(E2E / "P2_somascan.csv"), *o, "--age", "61", "--sex", "F", "--date", "2026-06-02"],
        ["metagenome", str(E2E / "P2_species_abundance.tsv"), *o, "--date", "2026-06-02"],
    ]


def build(person: str, out: Path, extra: list[str] | None = None, quiet: bool = True) -> None:
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    for cmd in commands(person, out):
        r = subprocess.run([sys.executable, str(HERE / "omics.py"), *cmd, *(extra or [])],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(f"failed: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
        if not quiet:
            print(r.stdout, end="")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--people-dir", default=str(E2E / "people"))
    ap.add_argument("--print", action="store_true", help="print the commands instead of running them")
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args()
    for p in ("P1", "P2"):
        out = Path(a.people_dir) / p / "observations.json"
        if a.print:
            for c in commands(p, out):
                print("python3 skills/longpi-omics/scripts/omics.py " + " ".join(shlex.quote(x) for x in c))
            continue
        build(p, out, ["--offline"] if a.offline else None, quiet=False)
        print(f"{p}: {out}")


if __name__ == "__main__":
    main()
