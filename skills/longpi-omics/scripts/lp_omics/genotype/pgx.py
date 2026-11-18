"""CPIC-style star-allele calls for SNP-definable pharmacogenes (unphased)."""
from __future__ import annotations

from .. import common
from . import gtio

FUNC_PHENO = {
    # (n_no_function, n_increased) -> phenotype for CYP2C19
    "CYP2C19": {(0, 0): "正常代谢型", (0, 1): "快代谢型", (0, 2): "超快代谢型",
                (1, 0): "中间代谢型", (1, 1): "中间代谢型", (2, 0): "慢代谢型"},
}
NF_PHENO = {0: "正常代谢型", 1: "中间代谢型", 2: "慢代谢型"}


def load_defs() -> dict:
    return common.load_json(common.data_file("pgx_cpic.json"))


def _site(panel, rsid, build):
    s = panel[rsid]
    return s["chrom"], s[f"pos_{build}"], s[f"alleles_{build}"]


def _count(g, panel, rsid, alt, build):
    """Copies of the variant allele `alt` at rsid; None when not genotyped."""
    c, p, alleles = _site(panel, rsid, build)
    other = [a for a in alleles if a != alt]
    ref = other[0] if other else None
    positions = [p]
    if any(len(a) != 1 for a in alleles):
        positions.append(p - 1)  # VCF indel anchor base
    for pos in positions:
        for call in g.at(c, pos):
            if call.alleles is None:
                continue
            if call.ref is not None and len(alt) != 1:
                # indel: compare the length change of each called allele with the panel indel
                d_alt = len(alt) - len(ref or "")
                n = sum((len(a) - len(call.ref)) == d_alt and a != call.ref for a in call.alleles)
                if call.alts and any((len(a) - len(call.ref)) == d_alt for a in call.alts):
                    return n
                continue
            d, st = gtio.dosage(g, c, pos, alt, ref if ref and len(ref) == 1 else None)
            if d is not None:
                return d
    return None


def call_all(g: gtio.Genotypes, build: str, panel: dict) -> list:
    defs = load_defs()
    out = []
    for gene, d in defs["genes"].items():
        rec = {"gene": gene, "rule": "CPIC", "snps": {}, "unphased": True}
        if d["model"] == "genotype":
            n = _count(g, panel, d["rsid"], d["alt"], build)
            rec["snps"][d["rsid"]] = n
            if n is None:
                rec.update({"diplotype": None, "phenotype": None, "called": False})
            else:
                names = d["allele_names"]
                dip = "/".join([names["alt"]] * n + [names["ref"]] * (2 - n))
                rec.update({"diplotype": dip, "phenotype": d["labels"][str(n)], "called": True})
            out.append(rec)
            continue
        counts, missing = {}, []
        for star, a in d["alleles"].items():
            n = _count(g, panel, a["rsid"], a["alt"], build)
            rec["snps"][a["rsid"]] = n
            if n is None:
                missing.append(star)
            else:
                counts[star] = n
        if not counts:
            rec.update({"diplotype": None, "phenotype": None, "called": False,
                        "note": "defining SNPs not genotyped"})
            out.append(rec)
            continue
        # TPMT *3A = *3B + *3C on one haplotype (cis is by far the most common configuration)
        for combo, name in d.get("combine", {}).items():
            a, b = combo.split("+")
            k = min(counts.get(a, 0), counts.get(b, 0))
            if k:
                counts[a] -= k
                counts[b] -= k
                counts[name] = counts.get(name, 0) + k
                rec.setdefault("notes", []).append(f"{a}+{b} assigned to {name} (cis); {a}/{b} trans is rarer")
        stars = []
        for star in sorted(counts, key=lambda s: (_func_rank(d, s), s)):
            stars += [star] * counts[star]
        if len(stars) > 2:
            rec.setdefault("notes", []).append(f"{len(stars)} variant alleles observed; the two lowest-function kept")
            stars = stars[:2]
        dip = sorted(stars + ["*1"] * (2 - len(stars)), key=_star_key)
        rec["diplotype"] = "/".join(dip)
        rec["called"] = True
        rec["phenotype"] = _phenotype(gene, d, dip)
        if missing:
            rec.setdefault("notes", []).append("not genotyped: " + ", ".join(missing))
        out.append(rec)
    return out


def _func_rank(d, star):
    a = d["alleles"].get(star)
    if a is None:  # combined allele, e.g. *3A
        return 0
    if d["model"] == "activity":
        return a["value"]
    return {"no": 0, "decreased": 1, "increased": 3}.get(a["function"], 2)


def _star_key(s):
    head = s.split(" ")[0].lstrip("*")
    num = "".join(ch for ch in head if ch.isdigit())
    return (int(num) if num else 999, s)


def _phenotype(gene, d, dip):
    if d["model"] == "activity":
        score = sum(1.0 if s == "*1" else d["alleles"][s]["value"] for s in dip)
        for thr, label in d["thresholds"]:
            if score >= thr:
                return f"{label}（活性评分 {score:g}）"
    nf = sum(1 for s in dip if s != "*1" and (s not in d["alleles"] or d["alleles"][s]["function"] == "no"))
    inc = sum(1 for s in dip if s in d["alleles"] and d["alleles"][s]["function"] == "increased")
    if gene in FUNC_PHENO:
        return FUNC_PHENO[gene].get((nf, inc), "无法判定")
    if "phenotypes" in d:
        return d["phenotypes"][str(nf)]
    return NF_PHENO[nf]
