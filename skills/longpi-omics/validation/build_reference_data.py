#!/usr/bin/env python3
"""Build committed reference data from public 1000 Genomes genotypes (run once; network).

Writes scripts/lp_omics/data/aisnp_1kg_freqs.json: per-AISNP allele frequencies in the five 1000G
superpopulations (2504 unrelated samples, NYGC 30x GRCh38 phased panel) plus per-superpopulation
allele counts so validation can do leave-one-out.
Also builds the EAS PRS reference for each PGS id given on the command line.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from lp_omics import common  # noqa: E402
from lp_omics.genotype import core, kg, prs  # noqa: E402


def main(pgs_ids):
    panel = core.load_panel()
    samples = kg.sample_panel()
    names = [s for s, *_ in samples]
    sp = {s: p for s, _, p, _ in samples}
    ais = [s for s in panel.values() if s["group"] == "aisnp_kidd55"]
    recs = kg.query_sites([(s["chrom"], s["pos_GRCh38"]) for s in ais], names)
    out = {}
    for s in ais:
        cand = recs.get((s["chrom"], s["pos_GRCh38"]), [])
        cand = [c for c in cand if len(c[0]) == 1 and len(c[1]) == 1 and {c[0], c[1]} <= set(s["alleles_GRCh38"])]
        if not cand:
            print("missing in 1000G", s["rsid"])
            continue
        ref, alt, gts = cand[0]
        ac = {k: 0 for k in core.SUPERPOPS}
        an = {k: 0 for k in core.SUPERPOPS}
        for name, g in zip(names, gts):
            a = g.replace("|", "/").split("/")
            if any(x not in "01" for x in a):
                continue
            ac[sp[name]] += sum(x == "1" for x in a)
            an[sp[name]] += len(a)
        out[s["rsid"]] = {"ref": ref, "alt": alt, "ac": ac, "an": an,
                          "af": {k: round(ac[k] / an[k], 6) for k in core.SUPERPOPS}}
    doc = {"source": kg.PANEL_NAME + "; superpopulation labels from integrated_call_samples_v3.20130502.ALL.panel",
           "alleles": "ref/alt on the GRCh38 + strand", "snps": out}
    (common.DATA_DIR / "aisnp_1kg_freqs.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print("aisnp", len(out))
    for pid in pgs_ids:
        p = prs.build_reference(pid)
        ref = prs.load_reference(pid)
        print(pid, ref["n_weight_variants"], ref["n_in_panel"], p)


if __name__ == "__main__":
    main(sys.argv[1:])
