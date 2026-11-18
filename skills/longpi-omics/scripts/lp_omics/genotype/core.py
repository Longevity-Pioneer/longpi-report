"""Build detection, sample QC, APOE and ancestry."""
from __future__ import annotations

import math

from .. import common
from . import gtio

CHR1_LEN = {248956422: "GRCh38", 249250621: "GRCh37"}
SUPERPOPS = ["AFR", "AMR", "EAS", "EUR", "SAS"]


def load_panel() -> dict:
    return {s["rsid"]: s for s in common.load_json(common.data_file("snp_panel.json"))["snps"]}


# --------------------------------------------------------------------------- build

def detect_build(g: gtio.Genotypes, panel: dict, extra_markers=()) -> dict:
    """Decide GRCh37 vs GRCh38.

    1) VCF contig header: chr1 length is definitive.
    2) Otherwise, fixed marker SNPs with known positions in both builds: for records carrying an rsID
       compare the position; for VCF records without rsIDs check REF/ALT at each build's position.
    extra_markers: iterable of (chrom, pos37, pos38, {alleles}) e.g. PRS variants.
    """
    ln = g.contig_lengths.get("1")
    if ln in CHR1_LEN:
        return {"build": CHR1_LEN[ln], "method": "VCF contig header (chr1 length)", "votes": {}}
    votes = {"GRCh37": 0, "GRCh38": 0}
    for rs, s in panel.items():
        if rs in g.by_rsid:
            c, p = g.by_rsid[rs]
            for b in votes:
                if p == s[f"pos_{b}"] and s["pos_GRCh37"] != s["pos_GRCh38"]:
                    votes[b] += 1
    markers = [(s["chrom"], s["pos_GRCh37"], s["pos_GRCh38"], set(s["alleles_GRCh38"]) | set(s["alleles_GRCh37"]))
               for s in panel.values()] + list(extra_markers)
    for c, p37, p38, alleles in markers:
        if p37 == p38:
            continue
        for b, p in (("GRCh37", p37), ("GRCh38", p38)):
            for call in g.at(c, p):
                if call.rsid:  # already counted through rsID
                    continue
                obs = {call.ref, *call.alts} if call.ref is not None else set(call.alleles or ())
                if obs and obs <= alleles:
                    votes[b] += 1
    tot = sum(votes.values())
    if tot >= 5 and max(votes.values()) >= 0.9 * tot:
        b = max(votes, key=votes.get)
        return {"build": b, "method": "marker positions in both builds", "votes": votes}
    raise ValueError(f"cannot determine the reference build (votes {votes}); pass --build GRCh37|GRCh38")


# --------------------------------------------------------------------------- QC

def qc(g: gtio.Genotypes, build: str, declared_sex: str | None) -> dict:
    c = g.counters
    call_rate = c["called"] / c["records"] if c["records"] else 0.0
    het = c["auto_het"] / c["auto_called"] if c["auto_called"] else 0.0
    par = gtio.PAR[build]
    xs = [(h, pl, nr) for p, h, pl, nr in g.xcalls if not any(a <= p <= b for a, b in par)]
    notes = list(g.notes)
    if g.fmt == "vcf":
        # heterozygosity among non-reference chrX calls: ~0 in males (haploid / hemizygous), ~0.5+ in females
        nr = [(h, pl) for h, pl, n in xs if n]
        if len(nr) >= 30:
            xhet = sum(h for h, _ in nr) / len(nr)
            haploid = sum(pl == 1 for _, pl in nr) / len(nr)
            inferred = "M" if (haploid > 0.5 or xhet < 0.05) else ("F" if xhet > 0.2 else "unknown")
        else:
            xhet, inferred = None, "unknown"
            notes.append(f"only {len(nr)} non-reference non-PAR chrX calls; sex check not possible")
    elif len(xs) >= 50:
        xhet = sum(h for h, _, _ in xs) / len(xs)
        inferred = "M" if xhet < 0.01 else ("F" if xhet > 0.03 else "unknown")
    else:
        xhet, inferred = None, "unknown"
        notes.append(f"only {len(xs)} non-PAR chrX calls; sex check not possible")
    if declared_sex in ("M", "F") and inferred in ("M", "F"):
        sex_check = "ok" if inferred == declared_sex else "mismatch"
        if sex_check == "mismatch":
            notes.append("genetic sex differs from declared sex: check sample identity before using results")
    elif inferred in ("M", "F"):
        sex_check = "inferred_only"
    else:
        sex_check = "not_assessed"
    if g.fmt == "chip" and call_rate < 0.95:
        notes.append(f"chip call rate {call_rate:.3f} < 0.95")
    if c["auto_called"] and not (0.0 < het < 0.5):
        notes.append(f"autosomal heterozygosity {het:.3f} implausible")
    return {"n_variants": c["records"], "n_called": c["called"], "call_rate": common.r(call_rate, 4),
            "het_rate": common.r(het, 4), "het_rate_basis": "het / called autosomal records in file",
            "x_het_rate": common.r(xhet, 4), "n_x_nonpar": len(xs), "inferred_sex": inferred,
            "declared_sex": declared_sex, "sex_check": sex_check, "notes": notes}


# --------------------------------------------------------------------------- APOE

def apoe(g: gtio.Genotypes, build: str, panel: dict) -> dict | None:
    """rs429358 C = e4; rs7412 T = e2 (+ strand). Unphased; e1 (rs429358 C + rs7412 T) is very rare."""
    def gt(rs, a, b):
        s = panel[rs]
        c, p = s["chrom"], s[f"pos_{build}"]
        d, st = gtio.dosage(g, c, p, a, b)
        return d
    c4 = gt("rs429358", "C", "T")
    t2 = gt("rs7412", "T", "C")
    if c4 is None or t2 is None:
        return None
    table = {(0, 0): "e3/e3", (0, 1): "e2/e3", (0, 2): "e2/e2", (1, 0): "e3/e4", (1, 1): "e2/e4",
             (2, 0): "e4/e4", (1, 2): "e1/e2 (rare)", (2, 1): "e1/e4 (rare)", (2, 2): "e1/e1 (rare)"}
    res = {"genotype": table[(c4, t2)], "e4_count": c4,
           "rs429358": "/".join(sorted(["C"] * c4 + ["T"] * (2 - c4))),
           "rs7412": "/".join(sorted(["T"] * t2 + ["C"] * (2 - t2))),
           "phased": False,
           "disclosure": "opt_in" if c4 == 2 else ("counsel" if c4 == 1 else "standard")}
    if (c4, t2) == (1, 1):
        res["note"] = "e2/e4 assumed; e1/e3 gives the same unphased genotype but is extremely rare"
    return res


# --------------------------------------------------------------------------- ancestry

def ancestry(g: gtio.Genotypes, build: str, panel: dict, freqs: dict, *, max_iter: int = 2000) -> dict:
    """Supervised admixture: maximize sum_j log P(g_j | q, P) over q on the simplex with superpopulation
    allele frequencies P fixed (1000 Genomes, 2504 unrelated samples) at the Kidd 55 AISNPs. EM updates
    (as in ADMIXTURE's q-step with fixed P), started from the uniform vector, fixed iteration budget."""
    obs = []
    for rs, f in freqs["snps"].items():
        s = panel[rs]
        d, st = gtio.dosage(g, s["chrom"], s[f"pos_{build}"], f["alt"], f["ref"])
        if d is not None:
            obs.append((d, [min(max(f["af"][k], 1e-3), 1 - 1e-3) for k in SUPERPOPS]))
    if len(obs) < 30:
        return {"method": "insufficient AISNPs", "n_snps": len(obs), **{k: None for k in SUPERPOPS}}
    q = estimate_q(obs, max_iter=max_iter)
    res = {k: common.r(v, 3) for k, v in zip(SUPERPOPS, q)}
    res.update({"n_snps": len(obs), "method": "supervised admixture EM, fixed 1000G superpopulation frequencies",
                "panel": "Kidd 55 AISNPs (Kidd et al. 2014 FSI Genet 10:23); frequencies 1000G NYGC 30x, 2504 unrelated"})
    return res


def estimate_q(obs, *, max_iter=2000, tol=1e-10):
    K = len(obs[0][1])
    q = [1.0 / K] * K
    for _ in range(max_iter):
        acc = [0.0] * K
        for d, p in obs:
            sa = sum(qk * pk for qk, pk in zip(q, p))
            sr = sum(qk * (1 - pk) for qk, pk in zip(q, p))
            for k in range(K):
                acc[k] += d * q[k] * p[k] / sa + (2 - d) * q[k] * (1 - p[k]) / sr
        new = [a / (2 * len(obs)) for a in acc]
        if max(abs(a - b) for a, b in zip(new, q)) < tol:
            q = new
            break
        q = new
    return q


def loglik(obs, q):
    ll = 0.0
    for d, p in obs:
        f = sum(qk * pk for qk, pk in zip(q, p))
        ll += math.log(f) * d + math.log(1 - f) * (2 - d)
    return ll
