#!/usr/bin/env python3
"""Assemble tools/REGISTRY.json from static tool metadata + measured validation results.

A tool is `admitted` only when its validation result passed AND its determinism check passed.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
OUT = HERE.parent / "tools" / "REGISTRY.json"
PY = ["python>=3.9"]
GEN = "scripts/lp_omics/genotype/"

TOOLS = [
    {"id": "geno_qc", "module": GEN + "core.py:qc", "inputs": ["vcf", "chip_txt"], "outputs": ["genetics.qc"],
     "license": "MIT (this repository)", "deps": PY, "validation_from": "determinism"},
    {"id": "geno_build", "module": GEN + "core.py:detect_build", "inputs": ["vcf", "chip_txt"], "outputs": ["genetics.build"],
     "license": "MIT (this repository)", "deps": PY, "validation_from": "geno_build"},
    {"id": "ancestry_aisnp", "module": GEN + "core.py:ancestry", "inputs": ["vcf", "chip_txt"], "outputs": ["genetics.ancestry"],
     "license": "MIT; Kidd 55 AISNP list (Kidd 2014, facts); 1000 Genomes frequencies (open, no restrictions)",
     "deps": PY, "validation_from": "ancestry_aisnp"},
    {"id": "prs_score", "module": GEN + "prs.py", "inputs": ["vcf", "chip_txt"], "outputs": ["PGS:*", "genetics.prs"],
     "license": "MIT; per-score licence checked from PGS Catalog, non-commercial scores refused",
     "deps": PY + ["bcftools>=1.15 (building the EAS reference only)"], "validation_from": "prs_score"},
    {"id": "apoe_genotype", "module": GEN + "core.py:apoe", "inputs": ["vcf", "chip_txt"],
     "outputs": ["LP:apoe_e4_count", "genetics.apoe"], "license": "MIT (this repository)", "deps": PY,
     "validation_from": "apoe_genotype"},
    {"id": "clinvar_acmg", "module": GEN + "clinvar.py", "inputs": ["vcf", "chip_txt"],
     "outputs": ["LP:monogenic:<HGNC>", "genetics.monogenic"],
     "license": "MIT; ClinVar data are public domain (NCBI); ACMG SF v3.2 gene list (facts)",
     "deps": PY + ["bcftools>=1.15 (building the ClinVar subset only)"], "validation_from": "clinvar_acmg"},
    {"id": "pgx_cpic", "module": GEN + "pgx.py", "inputs": ["vcf", "chip_txt"], "outputs": ["genetics.pgx"],
     "license": "MIT; CPIC allele definitions are CC0", "deps": PY, "validation_from": "pgx_cpic"},
    {"id": "impute_beagle", "module": GEN + "impute.py", "inputs": ["vcf", "chip_txt", "reference_panel"],
     "outputs": ["(adds imputed calls to the genotype set)"],
     "license": "MIT wrapper; Beagle 5.x is GPLv3 and is run as a separate program", "deps": PY + ["java>=11", "beagle 5.x jar"],
     "validation_from": "impute_beagle", "optional": True},
    {"id": "meth_horvath2013", "module": "scripts/lp_omics/methylation.py", "inputs": ["beta_matrix"],
     "outputs": ["LP:clock.horvath", "LP:clock.horvath_accel"],
     "license": "MIT; coefficients Horvath 2013 Genome Biol Additional file 3 (open access)", "deps": PY,
     "validation_from": "meth_horvath2013"},
    {"id": "meth_hannum2013", "module": "scripts/lp_omics/methylation.py", "inputs": ["beta_matrix"],
     "outputs": ["LP:clock.hannum", "LP:clock.hannum_accel"],
     "license": "MIT; coefficients Hannum 2013 Mol Cell Table S3 (as transcribed in biolearn, BSD)", "deps": PY,
     "validation_from": "meth_hannum2013"},
    {"id": "meth_vendor_passthrough", "module": "scripts/lp_omics/methylation.py", "inputs": ["vendor_json"],
     "outputs": ["LP:clock.<name>", "LP:clock.<name>_accel"], "license": "MIT; values are the vendor's", "deps": PY,
     "validation_from": "determinism"},
    {"id": "prot_organage2023", "module": "scripts/lp_omics/proteomics.py", "inputs": ["somascan_rfu"],
     "outputs": ["LP:prot.organage_<organ>_gap"], "license": "MIT (organage, Oh et al. 2023 Nature)", "deps": PY,
     "validation_from": "prot_organage2023"},
    {"id": "prot_passthrough", "module": "scripts/lp_omics/proteomics.py", "inputs": ["somascan_rfu", "olink_npx"],
     "outputs": ["UNIPROT:*"], "license": "MIT (this repository)", "deps": PY, "validation_from": "determinism"},
    {"id": "metab_metabohealth2019", "module": "scripts/lp_omics/metabolomics.py", "inputs": ["nightingale_nmr"],
     "outputs": ["LP:metab.metabohealth"],
     "license": "MIT; betas Deelen 2019 Nat Commun (CC BY 4.0); reference mean/SD numbers from MiMIR", "deps": PY,
     "validation_from": "metab_metabohealth2019"},
    {"id": "micro_gmhi2020", "module": "scripts/lp_omics/metagenome.py", "inputs": ["metaphlan_species"],
     "outputs": ["LP:micro.gmhi"], "license": "MIT; species lists Gupta 2020 Nat Commun (CC BY 4.0)", "deps": PY,
     "validation_from": "micro_gmhi2020"},
    {"id": "micro_shannon", "module": "scripts/lp_omics/metagenome.py", "inputs": ["metaphlan_species"],
     "outputs": ["LP:micro.shannon"], "license": "MIT (this repository)", "deps": PY, "validation_from": "micro_shannon"},
]

NOT_ADMITTED = [
    {"id": "meth_phenoage2018", "reason": "DNAm PhenoAge coefficients: commercial use requires a licence (UCLA TDG / Clock Foundation per biolearn usage metadata); vendor values only"},
    {"id": "meth_grimage", "reason": "GrimAge / GrimAge2 commercial licence; vendor values only"},
    {"id": "meth_dunedinpace", "reason": "DunedinPACE commercial licence; vendor values only"},
    {"id": "prot_protage2024", "reason": "Argentieri 2024 ProtAge (Olink): coefficient licence could not be verified"},
]


def main():
    det = json.loads((RES / "determinism.json").read_text()) if (RES / "determinism.json").exists() else {}
    tools = []
    for t in TOOLS:
        t = dict(t)
        src = t.pop("validation_from")
        val = None
        if src != "determinism" and (RES / f"{src}.json").exists():
            v = json.loads((RES / f"{src}.json").read_text())
            val = {k: v[k] for k in ("dataset", "metric", "value", "passed", "date")}
        elif src == "determinism" and det:
            val = {"dataset": det.get("dataset"), "metric": "two runs byte-identical (functional check only)",
                   "value": det.get("passed"), "passed": bool(det.get("passed")), "date": det.get("date")}
        t["version"] = "0.1.0"
        t["validation"] = val
        t["deterministic"] = bool(det.get("passed"))
        t["admitted"] = bool(val and val["passed"] and t["deterministic"])
        tools.append(t)
    doc = {"schema": "longpi.tool_registry/1",
           "admission_rule": "reproduces a known answer on public data; two runs byte-identical; licence permits commercial use; no personal data sent over the network",
           "tools": tools, "not_admitted": NOT_ADMITTED}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    for t in tools:
        print(t["id"], t["admitted"], (t["validation"] or {}).get("value"))


if __name__ == "__main__":
    main()
