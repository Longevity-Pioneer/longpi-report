"""Polygenic scores from PGS Catalog harmonized scoring files, standardized to 1000 Genomes EAS.

Method
- Scoring file: `<PGS>_hmPOS_<build>.txt.gz` (PGS Catalog harmonized positions for the user's build).
- Person score: sum(weight x effect-allele dosage) over variants the person has a call for AND that
  are present in the reference panel. Missing variants contribute nothing (no mean imputation).
- Coverage = scored variants / weight variants in the file. Below `min_coverage` (default 0.8):
  scored=false and no number is reported.
- Reference: the 504 unrelated EAS samples of 1000 Genomes (NYGC 30x GRCh38 phased panel), scored on
  exactly the same variant subset. z = (raw - mean) / sd; percentile = mid-rank among the 504.
- GRCh37 users: rows of the GRCh37 and GRCh38 harmonized files are the same original rows, so the
  reference dosages built on GRCh38 are joined by row.
- Licence: the scoring-file header / Catalog licence text is checked; non-commercial or
  research-only licences are refused (recorded, never scored).
"""
from __future__ import annotations

import gzip
import json
import math
import re
from pathlib import Path

from .. import common
from . import gtio, kg

PGS_URL = "https://ftp.ebi.ac.uk/pub/databases/spot/pgs/scores/{id}/ScoringFiles/Harmonized/{id}_hmPOS_{build}.txt.gz"
DEFAULT_LICENSE = ("PGS obtained from the Catalog should be cited appropriately, and used in accordance with any "
                   "licensing restrictions set by the authors.")
RESTRICTED = re.compile(r"non[- ]?commercial|\bNC\b|-NC|research (use|purposes) only|academic|not[- ]for[- ]profit|"
                        r"commercial purposes should contact|for research use", re.I)
MAX_REF_VARIANTS = 20000


class ScoreFile:
    def __init__(self, pgs_id: str, build: str, path: Path):
        self.pgs_id, self.build, self.path = pgs_id, build, path
        self.header, self.rows = {}, []
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            cols = None
            for line in fh:
                if line.startswith("#"):
                    if "=" in line:
                        k, v = line[1:].rstrip("\n").split("=", 1)
                        self.header[k.strip()] = v.strip()
                    continue
                f = line.rstrip("\n").split("\t")
                if cols is None:
                    cols = f
                    continue
                self.rows.append(dict(zip(cols, f)))
        self.cols = cols or []
        for bad in ("is_haplotype", "is_diplotype", "is_interaction"):
            if bad in self.cols and any(r.get(bad, "").upper() == "TRUE" for r in self.rows):
                raise ValueError(f"{pgs_id}: haplotype/interaction terms are not supported")
        if "effect_weight" not in self.cols:
            raise ValueError(f"{pgs_id}: no effect_weight column (dosage-specific weights are not supported)")

        self.meta = {}

    @property
    def license(self) -> str:
        return self.header.get("license") or self.meta.get("license") or DEFAULT_LICENSE

    def license_ok(self) -> bool:
        return license_allowed(self.license)

    def variants(self):
        """Yield (row_index, chrom, pos, effect, other, weight); chrom None when not harmonized."""
        for i, r in enumerate(self.rows):
            try:
                w = float(r["effect_weight"])
            except (KeyError, ValueError):
                continue
            chrom = r.get("hm_chr") or None
            pos = r.get("hm_pos") or None
            eff = (r.get("effect_allele") or "").upper()
            oth = (r.get("other_allele") or r.get("hm_inferOtherAllele") or "").upper() or None
            if oth and "/" in oth:
                oth = None  # several possible other alleles: match on the effect allele only
            if chrom and pos and pos.isdigit():
                yield i, gtio.norm_chrom(chrom), int(pos), eff, oth, w
            else:
                yield i, None, None, eff, oth, w


META_URL = "https://www.pgscatalog.org/rest/score/{id}"


def check_id(pgs_id: str) -> str:
    if not re.fullmatch(r"PGS\d{6}", pgs_id or ""):
        raise ValueError(f"bad PGS id {pgs_id!r}")
    return pgs_id


def fetch_metadata(pgs_id: str) -> dict:
    """Catalog metadata (licence, trait, publication). Public, cached."""
    dest = common.ref_dir("pgs", check_id(pgs_id)) / f"{pgs_id}_meta.json"
    common.download(META_URL.format(id=pgs_id), dest)
    return common.load_json(dest)


def license_allowed(text: str) -> bool:
    return not RESTRICTED.search(text or "")


def fetch_score(pgs_id: str, build: str) -> ScoreFile:
    check_id(pgs_id)
    dest = common.ref_dir("pgs", pgs_id) / f"{pgs_id}_hmPOS_{build}.txt.gz"
    common.download(PGS_URL.format(id=pgs_id, build=build), dest)
    sf = ScoreFile(pgs_id, build, dest)
    try:
        sf.meta = fetch_metadata(pgs_id)
    except Exception:  # metadata is optional; header licence or the Catalog default applies
        sf.meta = {}
    return sf


# ------------------------------------------------------------------ EAS reference panel

def ref_path(pgs_id: str) -> Path:
    return common.ref_dir("pgs", pgs_id) / f"{pgs_id}_EAS1kg_ref.json.gz"


def build_reference(pgs_id: str, *, max_variants: int = MAX_REF_VARIANTS) -> Path:
    """Effect-allele dosages of the 504 1000G EAS samples at every harmonized GRCh38 row.

    Only public score positions are sent to the public 1000 Genomes server (htslib range reads).
    """
    out = ref_path(pgs_id)
    if out.exists():
        return out
    sf = fetch_score(pgs_id, "GRCh38")
    var = [v for v in sf.variants() if v[1] is not None]
    if len(var) > max_variants:
        raise RuntimeError(f"{pgs_id}: {len(var)} variants exceeds the remote reference limit {max_variants}")
    samples = kg.eas_samples()
    recs = kg.query_sites([(c, p) for _, c, p, *_ in var], samples)
    rows = {}
    for i, c, p, e, o, w in var:
        cand = recs.get((c, p), [])
        d = None
        for ref, alt, gts in sorted(cand, key=lambda r: not (o and {e, o} == {r[0], r[1]})):
            if e in (ref, alt):  # the record carrying both score alleles first (split multi-allelics)
                d = _dosages(gts, ref, alt, e)
                break
        if d is None and not (o and gtio.comp(e) == o):
            fe = gtio.comp(e)
            for ref, alt, gts in cand:
                if fe in (ref, alt):
                    d = _dosages(gts, ref, alt, fe)
                    break
        if d is not None:
            rows[str(i)] = {"c": c, "p": p, "d": d, "ref": cand[0][0] if cand else None}
    doc = {"pgs_id": pgs_id, "panel": kg.PANEL_NAME, "n": len(samples), "rows": rows,
           "n_weight_variants": len(list(sf.variants())), "n_in_panel": len(rows)}
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        json.dump(doc, fh, sort_keys=True)
    return out


def _dosages(gts: list, ref: str, alt: str, effect: str) -> str:
    out = []
    for g in gts:
        a = g.replace("|", "/").split("/")
        if any(x not in ("0", "1") for x in a):
            out.append(".")
            continue
        n_alt = sum(x == "1" for x in a)
        n = n_alt if effect == alt else len(a) - n_alt
        if len(a) == 1:  # haploid (male X); count as diploid-equivalent
            n *= 2
        out.append(str(n))
    return "".join(out)


def load_reference(pgs_id: str) -> dict:
    with gzip.open(ref_path(pgs_id), "rt", encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ scoring

def score_person(g: gtio.Genotypes, sf: ScoreFile, ref: dict, *, min_coverage: float = 0.8):
    allvar = list(sf.variants())
    n_total = len(allvar)
    used, raw = [], 0.0
    status = {}
    for i, c, p, e, o, w in allvar:
        if c is None:
            status["not_harmonized"] = status.get("not_harmonized", 0) + 1
            continue
        d, st = gtio.dosage(g, c, p, e, o)
        if d is None:
            status[st] = status.get(st, 0) + 1
            continue
        rr = ref["rows"].get(str(i))
        if rr is None:
            status["not_in_reference"] = status.get("not_in_reference", 0) + 1
            continue
        status[st] = status.get(st, 0) + 1
        if c in ("X",) and len(set(_alleles_at(g, c, p))) == 1 and _ploidy(g, c, p) == 1:
            d *= 2
        raw += w * d
        used.append((i, w, rr["d"]))
    coverage = len(used) / n_total if n_total else 0.0
    res = {"pgs_id": sf.pgs_id, "trait": sf.header.get("trait_reported") or sf.header.get("trait_mapped"),
           "n_variants": n_total, "n_scored": len(used), "coverage": common.r(coverage, 4),
           "min_coverage": min_coverage, "match_status": dict(sorted(status.items())),
           "ref": f"1000G EAS (n {ref['n']})", "license": sf.license}
    if coverage < min_coverage or not used:
        res.update({"scored": False, "raw": None, "z": None, "percentile": None,
                    "reason": f"coverage {coverage:.3f} below required {min_coverage}"})
        return res
    refsc = _ref_scores(used, ref["n"])
    vals = [v for v in refsc if v is not None]
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / (len(vals) - 1))
    below = sum(v < raw - 1e-12 for v in vals)
    ties = sum(abs(v - raw) <= 1e-12 for v in vals)
    pct = 100.0 * (below + 0.5 * ties) / len(vals)
    res.update({"scored": True, "raw": common.r(raw, 6), "z": common.r((raw - m) / sd if sd > 0 else 0.0, 4),
                "percentile": common.r(pct, 2), "ref_mean": common.r(m, 6), "ref_sd": common.r(sd, 6),
                "ref_n_used": len(vals)})
    return res


def _alleles_at(g, c, p):
    for call in g.at(c, p):
        if call.alleles:
            return call.alleles
    return ()


def _ploidy(g, c, p):
    return len(_alleles_at(g, c, p)) or 2


def _ref_scores(used, n):
    """Reference scores on the same variants. Reference samples with a missing genotype at a used
    variant get the reference-sample mean dosage for that variant (rare in the 30x panel)."""
    tot = [0.0] * n
    for _, w, d in used:
        called = [int(x) for x in d if x != "."]
        mean = sum(called) / len(called) if called else 0.0
        for k, x in enumerate(d):
            tot[k] += w * (int(x) if x != "." else mean)
    return tot


def af_approximation(used_rows: list):
    """Mean/SD of a score from EAS allele frequencies alone (HWE + linkage equilibrium).

    used_rows: [(weight, dosage_string)]. Used only for validation of the approximation.
    """
    m = v = 0.0
    for w, d in used_rows:
        called = [int(x) for x in d if x != "."]
        p = sum(called) / (2 * len(called))
        m += 2 * p * w
        v += 2 * p * (1 - p) * w * w
    return m, math.sqrt(v)
