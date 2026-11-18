#!/usr/bin/env python3
"""Build the derived genotype inputs for the two synthetic E2E people from public 1000 Genomes data.

P1 (male): a 1000G EAS male; GRCh38 single-sample VCF (+ a GRCh37 lift of the same calls for the
           build-consistency validation).
P2 (female): a 1000G EAS female; 23andMe-style chip text on GRCh37, plus a small WGS-derived GRCh38 VCF
           with one planted ClinVar pathogenic LDLR SNV (synthetic) so the monogenic path is exercised.
Sample IDs are replaced by P1/P2. Only panel SNPs, PRS variants, selected ACMG SF gene regions and a
chrX segment are kept.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import common  # noqa: E402
from lp_omics.genotype import clinvar, core, kg, liftover, prs  # noqa: E402

OUT = HERE.parents[1] / "longpi-report" / "examples" / "e2e"
PGS = ["PGS002262", "PGS002259", "PGS003353", "PGS000050", "PGS000070", "PGS000662", "PGS003850"]
GENES = ["BRCA1", "BRCA2", "LDLR", "MLH1", "PCSK9", "TP53"]
XREGION = ("X", 20_000_000, 20_150_000)
GRCH38_LEN = {"1": 248956422, "2": 242193529, "3": 198295559, "4": 190214555, "5": 181538259, "6": 170805979,
              "7": 159345973, "8": 145138636, "9": 138394717, "10": 133797422, "11": 135086622, "12": 133275309,
              "13": 114364328, "14": 107043718, "15": 101991189, "16": 90338345, "17": 83257441, "18": 80373285,
              "19": 58617616, "20": 64444167, "21": 46709983, "22": 50818468, "X": 156040895, "Y": 57227415}


def pick_samples():
    rows = kg.sample_panel()
    m = [s for s, pop, sp, sex in rows if sp == "EAS" and pop == "CHB" and sex == "male"]
    f = [s for s, pop, sp, sex in rows if sp == "EAS" and pop == "CHS" and sex == "female"]
    return m[0], f[0]


def gene_regions(cv):
    span = {}
    for r in cv["records"].values():
        if r["gene"] in GENES:
            a, b = span.get(r["gene"], (10**12, 0))
            span[r["gene"]] = (min(a, r["pos"]), max(b, r["pos"] + len(r["ref"])))
    return [(cv_chrom(cv, g), a - 50, b + 50) for g, (a, b) in sorted(span.items())]


def cv_chrom(cv, gene):
    for r in cv["records"].values():
        if r["gene"] == gene:
            return r["chrom"]


def main():
    s1, s2 = pick_samples()
    print("samples (public 1000G, renamed):", s1, "-> P1;", s2, "-> P2")
    panel = core.load_panel()
    sites = set()
    for s in panel.values():
        sites.add((s["chrom"], s["pos_GRCh38"]))
        if any(len(a) != 1 for a in s["alleles_GRCh38"]):
            sites.add((s["chrom"], s["pos_GRCh38"] - 1))
    for pid in PGS:
        for _, c, p, *_ in prs.fetch_score(pid, "GRCh38").variants():
            if c:
                sites.add((c, p))
    cv38 = clinvar.load_cache("GRCh38")
    regions = gene_regions(cv38) + [XREGION]
    recs = kg.query_sites(sorted(sites), [s1, s2], regions=regions)
    chain = liftover.Chain(common.ref_dir("liftover") / "hg38ToHg19.over.chain.gz")
    OUT.mkdir(parents=True, exist_ok=True)

    def rows_for(k, keep_ref_sites):
        out = []
        for (c, p), lst in recs.items():
            for ref, alt, gts in lst:
                gt = gts[k]
                is_site = (c, p) in sites
                if not is_site and gt.replace("|", "/") in ("0/0", "0"):
                    continue  # variant-only outside scored sites, as in a real WGS VCF
                if not keep_ref_sites and not is_site and gt in ("0/0", "0|0"):
                    continue
                out.append((c, p, ref, alt, gt))
        key = lambda r: ((int(r[0]) if r[0].isdigit() else 23 if r[0] == "X" else 24), r[1], r[2], r[3])
        return sorted(set(out), key=key)

    def write_vcf(path, rows, build, contigs):
        with open(path, "w") as fh:
            fh.write("##fileformat=VCFv4.2\n")
            fh.write("##source=LongPi synthetic E2E person; genotypes derived from a public 1000 Genomes sample (renamed)\n")
            if contigs:
                for c in list(map(str, range(1, 23))) + ["X", "Y"]:
                    fh.write(f"##contig=<ID=chr{c},length={GRCH38_LEN[c]}>\n")
            fh.write("##FILTER=<ID=PASS,Description=\"All filters passed\">\n")
            fh.write("##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
            fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + path.name.split("_")[0] + "\n")
            for c, p, ref, alt, gt in rows:
                fh.write(f"chr{c}\t{p}\t.\t{ref}\t{alt}\t.\tPASS\t.\tGT\t{gt}\n")

    p1 = rows_for(0, True)
    write_vcf(OUT / "P1_genotypes_GRCh38.vcf", p1, "GRCh38", True)
    # GRCh37 lift of the same calls (validation fixture): positions via chain; REF/ALT kept on + strand
    lifted, dropped = [], 0
    for c, p, ref, alt, gt in p1:
        r = chain.convert(c, p)
        if r is None or r[0] != c or r[2] != "+":
            dropped += 1
            continue
        lifted.append((c, r[1], ref, alt, gt))
    lifted.sort(key=lambda r: ((int(r[0]) if r[0].isdigit() else 23), r[1]))
    vdir = HERE.parent / "tests" / "fixtures" / "genotype"
    vdir.mkdir(parents=True, exist_ok=True)
    write_vcf(vdir / "P1_genotypes_GRCh37_lifted.vcf", lifted, "GRCh37", False)
    print("P1 VCF rows", len(p1), "lifted", len(lifted), "dropped", dropped)

    # P2 chip (GRCh37, 23andMe style): all scored sites + region SNVs, genotype letters
    p2 = rows_for(1, True)
    rs_at = {(s["chrom"], s["pos_GRCh38"]): s["rsid"] for s in panel.values()}
    lines, n_chip = [], 0
    for c, p, ref, alt, gt in p2:
        if len(ref) != 1 or len(alt) != 1:
            continue
        r = chain.convert(c, p)
        if r is None or r[0] != c or r[2] != "+":
            continue
        a = gt.replace("|", "/").split("/")
        letters = "".join(ref if x == "0" else alt for x in a if x in "01")
        if len(letters) != len(a):
            letters = "--"
        rid = rs_at.get((c, p)) or f"i{700000000 + n_chip}"
        lines.append((c, r[1], rid, letters))
        n_chip += 1
    lines.sort(key=lambda r: ((int(r[0]) if r[0].isdigit() else 23), r[1]))
    with open(OUT / "P2_chip_23andme_GRCh37.txt", "w") as fh:
        fh.write("# LongPi synthetic E2E person P2. Derived from a public 1000 Genomes sample (renamed); NOT a real customer file.\n")
        fh.write("# This data file generated by 23andMe-style export format at: synthetic\n")
        fh.write("# We are using reference human assembly build 37 (also known as Annotation Release 104).\n")
        fh.write("# rsid\tchromosome\tposition\tgenotype\n")
        for c, p, rid, g in lines:
            fh.write(f"{rid}\t{c}\t{p}\t{g}\n")
    print("P2 chip rows", len(lines))

    # P2 WGS-derived small VCF with one planted LDLR pathogenic SNV (>=2 stars)
    rnd = random.Random(11)
    cands = sorted([r for r in cv38["records"].values() if r["gene"] == "LDLR" and clinvar.reportable(r)
                    and len(r["ref"]) == 1 and len(r["alt"]) == 1 and clinvar.review_stars(r["revstat"]) >= 2],
                   key=lambda r: r["id"])
    plant = rnd.choice(cands)
    rows = [r for r in p2 if r[0] == "19" and not (r[0], r[1]) in sites] + \
           [(plant["chrom"], plant["pos"], plant["ref"], plant["alt"], "0/1")]
    rows = sorted(set(rows), key=lambda r: r[1])
    write_vcf(OUT / "P2_wgs_LDLR_GRCh38.vcf", rows, "GRCh38", True)
    meta = {"P1": {"origin": "1000 Genomes EAS male (CHB), public open-consent; sample ID removed"},
            "P2": {"origin": "1000 Genomes EAS female (CHS), public open-consent; sample ID removed"},
            "planted_P2": {"gene": "LDLR", "clinvar_id": plant["id"], "clnsig": plant["clnsig"],
                           "review_status": plant["revstat"], "GRCh38": f"chr{plant['chrom']}:{plant['pos']} {plant['ref']}>{plant['alt']}",
                           "note": "synthetic heterozygous call added to a WGS-style VCF"},
            "pgs_ids": PGS, "acmg_regions": GENES, "x_region": list(XREGION)}
    (OUT / "genotype_sources.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps(meta["planted_P2"]))


if __name__ == "__main__":
    main()
