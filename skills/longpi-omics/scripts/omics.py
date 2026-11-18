#!/usr/bin/env python3
"""LongPi omics layer CLI: secondary omics data -> observations.json (longpi.observations/1).

Subcommands (each merges its results into --out, replacing its own previous output):
  genotype      VCF or 23andMe-style text -> QC, build, ancestry, PRS, APOE, ClinVar (ACMG SF), PGx
  methylation   beta matrix -> Horvath 2013 / Hannum 2013 / DNAm PhenoAge (open coefficients)
  proteomics    SomaScan / Olink matrix -> open-licence proteomic clocks + outcome proteins
  metabolomics  Nightingale NMR table -> MetaboHealth
  metagenome    species abundance table -> GMHI, Shannon
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lp_omics import common  # noqa: E402

MODULES = {
    "genotype": "lp_omics.genotype.cli",
    "methylation": "lp_omics.methylation",
    "proteomics": "lp_omics.proteomics",
    "metabolomics": "lp_omics.metabolomics",
    "metagenome": "lp_omics.metagenome",
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="omics.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    mods = {}
    for name, modname in MODULES.items():
        try:
            mod = importlib.import_module(modname)
        except ModuleNotFoundError as e:  # a module not yet installed in this checkout
            if not e.name or not e.name.startswith("lp_omics"):
                raise
            continue
        p = sub.add_parser(name, help=(mod.__doc__ or "").strip().splitlines()[0])
        p.add_argument("--out", required=True, help="observations.json to create or merge into")
        p.add_argument("--person-code", default=None, help="person code written to observations.json (no names)")
        p.add_argument("--date", default=None, help="sample date YYYY-MM-DD for the observations")
        mod.add_arguments(p)
        mods[name] = mod
    args = ap.parse_args(argv)
    mod = mods[args.cmd]
    doc = common.load_doc(Path(args.out), args.person_code)
    res = mod.run(args)
    common.merge(doc, tool_ids=res["tool_ids"], observations=res["observations"],
                 provenance=res["provenance"], genetics=res.get("genetics"),
                 extra_blocks=res.get("extra_blocks"))
    common.write_doc(doc, Path(args.out))
    for line in res.get("summary", []):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
