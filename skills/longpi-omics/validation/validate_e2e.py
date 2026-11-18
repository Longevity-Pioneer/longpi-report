#!/usr/bin/env python3
"""Run every subcommand on the E2E inputs twice (determinism) and check build detection / GRCh37-38
consistency. Writes results/determinism.json and results/geno_build.json, and the E2E observations to
examples/e2e/expected/ (P1_observations.json, P2_observations.json)."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SK = HERE.parent
OMICS = SK / "scripts" / "omics.py"
E2E = SK.parent / "longpi-report" / "examples" / "e2e"
FIXG = SK / "tests" / "fixtures" / "genotype"
PGS = ["PGS002262", "PGS002259", "PGS003353", "PGS000050", "PGS000070", "PGS000662", "PGS003850"]
DATE = "2026-11-18"


def run(args):
    r = subprocess.run([sys.executable, str(OMICS), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(r.stdout + r.stderr)
    return r.stdout


def person_runs(out, who):
    sys.path.insert(0, str(SK / "scripts"))
    import run_e2e
    run_e2e.build(who, out)


def main():
    res = {"dataset": "examples/e2e synthetic P1/P2 inputs, all subcommands", "date": DATE, "files": {}}
    ok = True
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for who in ("P1", "P2"):
            a, b = td / f"{who}_a.json", td / f"{who}_b.json"
            person_runs(a, who)
            person_runs(b, who)
            same = a.read_bytes() == b.read_bytes()
            res["files"][who] = {"bytes": a.stat().st_size, "identical": same}
            ok &= same
            exp = E2E / "expected"
            exp.mkdir(exist_ok=True)
            (exp / f"{who}_observations.json").write_bytes(a.read_bytes())
        # build detection and GRCh37/38 consistency
        b38, b37 = td / "b38.json", td / "b37.json"
        pg = sum((["--pgs", p] for p in PGS), [])
        run(["genotype", str(E2E / "P1_genotypes_GRCh38.vcf"), "--out", str(b38), *pg])
        run(["genotype", str(FIXG / "P1_genotypes_GRCh37_lifted.vcf"), "--out", str(b37), *pg])
        g38 = json.loads(b38.read_text())["genetics"]
        g37 = json.loads(b37.read_text())["genetics"]
        chip = json.loads((E2E / "expected" / "P2_observations.json").read_text())["genetics"]
        cmp = {
            "build_P1_vcf_header": g38["build"], "build_P1_lifted_markers": g37["build"], "build_P2_chip_markers": chip["build"],
            "prs_identical": [(x["pgs_id"], x["raw"], x["z"]) for x in g37["prs"]] == [(x["pgs_id"], x["raw"], x["z"]) for x in g38["prs"]],
            "apoe_identical": g37["apoe"] == g38["apoe"],
            "clinvar_identical": [m["clinvar_id"] for m in g37["monogenic"]] == [m["clinvar_id"] for m in g38["monogenic"]],
            "pgx_identical": [(x["gene"], x["diplotype"]) for x in g37["pgx"]] == [(x["gene"], x["diplotype"]) for x in g38["pgx"]],
            "ancestry_identical": g37["ancestry"] == g38["ancestry"],
            "prs_GRCh38": [(x["pgs_id"], x["z"], x["coverage"]) for x in g38["prs"]],
        }
        passed = (cmp["build_P1_vcf_header"] == "GRCh38" and cmp["build_P1_lifted_markers"] == "GRCh37"
                  and cmp["build_P2_chip_markers"] == "GRCh37" and all(cmp[k] for k in cmp if k.endswith("_identical")))
    res["passed"] = ok
    (HERE / "results" / "determinism.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    doc = {"tool_id": "geno_build", "version": "0.1.0",
           "dataset": "1000G EAS sample: GRCh38 VCF vs UCSC-chain lift to GRCh37 (no contig header); 23andMe-style GRCh37 chip",
           "metric": "correct build on 3 files and identical PRS/APOE/ClinVar/PGx/ancestry across builds",
           "value": passed, "passed": passed, "date": DATE, "details": cmp}
    (HERE / "results" / "geno_build.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(json.dumps(res, indent=1))
    print(json.dumps(cmp, indent=1))


if __name__ == "__main__":
    main()
