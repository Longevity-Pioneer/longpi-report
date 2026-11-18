#!/usr/bin/env python3
"""Generate the SYNTHETIC non-genome E2E inputs (seeded, reproducible). No real person's data is used.

usage: make_e2e_synthetic.py <out_dir> <SomaScan_V4.0_5K_Annotated_Content csv (from organage, for SeqIds + median RFU)>
Writes P1_methylation_beta.csv, P1_nightingale.csv, P2_somascan.csv, P2_species_abundance.tsv.
"""
from __future__ import annotations

import csv
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import methylation, proteomics  # noqa: E402

SEED = 20261118


def methyl(out: Path, target_horvath=50.0, target_hannum=49.0):
    rng = random.Random(SEED)
    cl = methylation.load_coefs()
    h, n = cl["horvath"], cl["hannum"]
    beta = {c: min(0.98, max(0.02, v + rng.gauss(0, 0.02))) for c, v in h["impute"].items()}
    for c, v in n["impute"].items():
        beta.setdefault(c, min(0.98, max(0.02, v + rng.gauss(0, 0.02))))

    def shift(clock, target, cpgs):
        # move betas along sign(coef) until the clock hits the target (bisection on t)
        lo, hi = -0.2, 0.2
        base = dict(beta)
        for _ in range(60):
            t = (lo + hi) / 2
            trial = dict(base)
            for c in cpgs:
                trial[c] = min(0.98, max(0.02, base[c] + t * (1 if clock["coef"][c] > 0 else -1)))
            v = methylation.compute_clock(clock, trial)["value"]
            if v < target:
                lo = t
            else:
                hi = t
        beta.update({c: trial[c] for c in cpgs})

    shift(h, target_horvath, sorted(h["coef"]))
    shift(n, target_hannum, sorted(set(n["coef"]) - set(h["coef"])))
    drop = set(sorted(h["coef"])[::70][:5]) | {sorted(n["coef"])[3]}  # ~1.4% of clock CpGs missing
    filler = [f"cg{rng.randrange(10**7, 3 * 10**7):08d}" for _ in range(200)]
    with open(out, "w", newline="") as fh:
        fh.write("# SYNTHETIC methylation beta values for test person P1 (generated, not a real sample)\n")
        w = csv.writer(fh)
        w.writerow(["ID_REF", "SYNTH_P1"])
        for c in sorted(set(beta) | set(filler)):
            if c in drop:
                w.writerow([c, "NA"])
            elif c in beta:
                w.writerow([c, f"{beta[c]:.4f}"])
            else:
                w.writerow([c, f"{min(0.98, max(0.02, rng.betavariate(2, 2))):.4f}"])
    print("wrote", out)


def soma(out: Path, annot: Path):
    rng = random.Random(SEED + 2)
    oa = proteomics.load_organage()
    with open(annot, encoding="latin1") as fh:
        rows = list(csv.DictReader(fh))
    key = [k for k in rows[0] if k.endswith("SeqId")][0]
    med = {}
    for r in rows:
        try:
            med[r[key]] = float(r["Median Normal Plasma (RFU)"])
        except (ValueError, KeyError):
            med[r[key]] = 1000.0
    model_mean = {}
    for organ in oa["organs"].values():
        for p in organ["proteins"]:
            model_mean[p["seqid"]] = (p["mean"], p["scale"])
    v4 = oa["scale_v4_to_v41"]
    person_z = rng.gauss(0.15, 0.1)  # a mild global "older" shift
    passthrough = {"7655-11": 420.0, "4374-45": 1650.0, "2609-59": 158000.0, "4337-49": 2300.0,
                   "4673-13": 32.0, "8484-24": 9800.0}
    with open(out, "w", newline="") as fh:
        fh.write("# SYNTHETIC SomaScan-like ANML RFU for test person P2 (generated; SeqIds of the v4.0 5K menu)\n")
        w = csv.writer(fh)
        w.writerow(["SeqId", "SYNTH_P2"])
        for s in sorted(med, key=lambda x: tuple(int(t) for t in x.split("-"))):
            if s in passthrough:
                v = passthrough[s]
            elif s in model_mean:
                m, sd = model_mean[s]
                log41 = m + sd * (person_z + rng.gauss(0, 0.3))
                v = 10 ** log41 / v4.get(s, 1.0)  # write in v4 units
            else:
                v = med[s] * math.exp(rng.gauss(0, 0.3))
            w.writerow([s, f"{max(v, 1.0):.1f}"])
    print("wrote", out)


# Nightingale 2016-platform biomarkers (classic names, mmol/L unless noted; albumin in that platform's signal units)
NIGHTINGALE = [
    ("XXL_VLDL_P", "mol/L", 1.9e-10), ("XXL_VLDL_L", "mmol/L", 0.041), ("XL_VLDL_L", "mmol/L", 0.19),
    ("L_VLDL_L", "mmol/L", 0.62), ("M_VLDL_L", "mmol/L", 1.08), ("S_VLDL_L", "mmol/L", 1.02),
    ("S_HDL_L", "mmol/L", 0.96), ("M_HDL_L", "mmol/L", 0.71), ("VLDL_D", "nm", 37.4), ("LDL_D", "nm", 23.5),
    ("HDL_D", "nm", 9.8), ("Serum_C", "mmol/L", 5.31), ("LDL_C", "mmol/L", 2.07), ("HDL_C", "mmol/L", 1.21),
    ("Serum_TG", "mmol/L", 1.62), ("ApoB", "g/L", 1.02), ("ApoA1", "g/L", 1.43), ("TotFA", "mmol/L", 11.9),
    ("PUFA_FA", "%", 35.8), ("MUFA_FA", "%", 26.1), ("SFA_FA", "%", 34.2), ("DHA", "mmol/L", 0.15),
    ("Glc", "mmol/L", 5.6), ("Lac", "mmol/L", 1.42), ("Cit", "mmol/L", 0.10), ("Ala", "mmol/L", 0.33),
    ("Gln", "mmol/L", 0.49), ("His", "mmol/L", 0.056), ("Ile", "mmol/L", 0.061), ("Leu", "mmol/L", 0.070),
    ("Val", "mmol/L", 0.172), ("Phe", "mmol/L", 0.047), ("Tyr", "mmol/L", 0.052), ("AcAce", "mmol/L", 0.031),
    ("bOHBut", "mmol/L", 0.09), ("Crea", "mmol/L", 0.071), ("Alb", "signal", 0.0861), ("Gp", "mmol/L", 1.49),
]


def nightingale(out: Path):
    with open(out, "w", newline="") as fh:
        fh.write("# SYNTHETIC Nightingale NMR (2016 platform naming) results for test person P1 (generated)\n")
        w = csv.writer(fh)
        w.writerow(["Sample"] + [n for n, _, _ in NIGHTINGALE])
        w.writerow(["unit"] + [u for _, u, _ in NIGHTINGALE])
        w.writerow(["SYNTH_P1"] + [f"{v:.6g}" for _, _, v in NIGHTINGALE])
    print("wrote", out)


# Species with taxonomy (MetaPhlAn2 naming); includes GMHI health-prevalent and health-scarce species.
TAXA = [
    ("Bacteroidetes", "Bacteroidia", "Bacteroidales", "Bacteroidaceae", "Bacteroides", "Bacteroides_vulgatus", 14.2),
    ("Bacteroidetes", "Bacteroidia", "Bacteroidales", "Bacteroidaceae", "Bacteroides", "Bacteroides_uniformis", 8.1),
    ("Bacteroidetes", "Bacteroidia", "Bacteroidales", "Bacteroidaceae", "Bacteroides", "Bacteroides_stercoris", 3.3),
    ("Bacteroidetes", "Bacteroidia", "Bacteroidales", "Prevotellaceae", "Prevotella", "Prevotella_copri", 11.5),
    ("Bacteroidetes", "Bacteroidia", "Bacteroidales", "Rikenellaceae", "Alistipes", "Alistipes_putredinis", 4.0),
    ("Bacteroidetes", "Bacteroidia", "Bacteroidales", "Rikenellaceae", "Alistipes", "Alistipes_senegalensis", 0.9),
    ("Bacteroidetes", "Bacteroidia", "Bacteroidales", "Bacteroidales_noname", "Bacteroidales_noname", "Bacteroidales_bacterium_ph8", 0.4),
    ("Firmicutes", "Clostridia", "Clostridiales", "Ruminococcaceae", "Faecalibacterium", "Faecalibacterium_prausnitzii", 9.6),
    ("Firmicutes", "Clostridia", "Clostridiales", "Lachnospiraceae", "Roseburia", "Roseburia_intestinalis", 2.2),
    ("Firmicutes", "Clostridia", "Clostridiales", "Lachnospiraceae", "Eubacterium", "Eubacterium_rectale", 6.3),
    ("Firmicutes", "Clostridia", "Clostridiales", "Ruminococcaceae", "Ruminococcus", "Ruminococcus_bromii", 2.8),
    ("Firmicutes", "Clostridia", "Clostridiales", "Lachnospiraceae", "Blautia", "Blautia_obeum", 1.9),
    ("Firmicutes", "Clostridia", "Clostridiales", "Lachnospiraceae", "Lachnospiraceae_noname", "Lachnospiraceae_bacterium_8_1_57FAA", 0.6),
    ("Firmicutes", "Clostridia", "Clostridiales", "Lachnospiraceae", "Ruminococcus", "Ruminococcus_gnavus", 1.1),
    ("Firmicutes", "Clostridia", "Clostridiales", "Lachnospiraceae", "Clostridium", "Clostridium_bolteae", 0.5),
    ("Firmicutes", "Clostridia", "Clostridiales", "Ruminococcaceae", "Flavonifractor", "Flavonifractor_plautii", 0.3),
    ("Firmicutes", "Erysipelotrichia", "Erysipelotrichales", "Erysipelotrichaceae", "Erysipelotrichaceae_noname", "Clostridium_ramosum", 0.2),
    ("Firmicutes", "Bacilli", "Lactobacillales", "Streptococcaceae", "Streptococcus", "Streptococcus_salivarius", 1.4),
    ("Firmicutes", "Bacilli", "Lactobacillales", "Streptococcaceae", "Streptococcus", "Streptococcus_vestibularis", 0.3),
    ("Firmicutes", "Negativicutes", "Selenomonadales", "Veillonellaceae", "Veillonella", "Veillonella_atypica", 0.2),
    ("Actinobacteria", "Actinobacteria", "Bifidobacteriales", "Bifidobacteriaceae", "Bifidobacterium", "Bifidobacterium_adolescentis", 3.9),
    ("Actinobacteria", "Actinobacteria", "Bifidobacteriales", "Bifidobacteriaceae", "Bifidobacterium", "Bifidobacterium_longum", 2.7),
    ("Actinobacteria", "Actinobacteria", "Bifidobacteriales", "Bifidobacteriaceae", "Bifidobacterium", "Bifidobacterium_catenulatum", 0.8),
    ("Actinobacteria", "Coriobacteriia", "Eggerthellales", "Eggerthellaceae", "Eggerthella", "Eggerthella_lenta", 0.15),
    ("Actinobacteria", "Actinobacteria", "Coriobacteriales", "Coriobacteriaceae", "Collinsella", "Collinsella_aerofaciens", 1.6),
    ("Proteobacteria", "Betaproteobacteria", "Burkholderiales", "Sutterellaceae", "Sutterella", "Sutterella_wadsworthensis", 0.7),
    ("Proteobacteria", "Gammaproteobacteria", "Enterobacterales", "Enterobacteriaceae", "Escherichia", "Escherichia_coli", 1.8),
    ("Proteobacteria", "Gammaproteobacteria", "Enterobacterales", "Enterobacteriaceae", "Klebsiella", "Klebsiella_pneumoniae", 0.25),
    ("Verrucomicrobia", "Verrucomicrobiae", "Verrucomicrobiales", "Akkermansiaceae", "Akkermansia", "Akkermansia_muciniphila", 1.2),
    ("Euryarchaeota", "Methanobacteria", "Methanobacteriales", "Methanobacteriaceae", "Methanobrevibacter", "Methanobrevibacter_smithii", 0.5),
]


def species(out: Path):
    tot = sum(t[-1] for t in TAXA)
    with open(out, "w") as fh:
        fh.write("#mpa_v20_m200 (SYNTHETIC profile for test person P2; generated, not a real sample)\n")
        fh.write("#clade_name\tNCBI_tax_id\trelative_abundance\tadditional_species\n")
        for p, c, o, f, g, s, a in TAXA:
            king = "Archaea" if p == "Euryarchaeota" else "Bacteria"
            lin = f"k__{king}|p__{p}|c__{c}|o__{o}|f__{f}|g__{g}|s__{s}"
            fh.write(f"{lin}\t\t{a / tot * 100:.5f}\t\n")
    print("wrote", out)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    methyl(out / "P1_methylation_beta.csv")
    nightingale(out / "P1_nightingale.csv")
    soma(out / "P2_somascan.csv", Path(sys.argv[2]))
    species(out / "P2_species_abundance.tsv")
