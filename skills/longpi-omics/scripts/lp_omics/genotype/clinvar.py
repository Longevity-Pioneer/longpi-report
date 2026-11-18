"""ClinVar annotation restricted to ACMG SF v3.2 genes.

Rules
- Source: the official ClinVar VCF for the user's build (downloaded and cached; release = ##fileDate).
- Reportable: CLNSIG Pathogenic, Likely_pathogenic or Pathogenic/Likely_pathogenic (no "Conflicting"),
  review status >= 2 stars. VUS, benign and conflicting are never reported.
- Matching: SNVs by chrom/pos/ref/alt exactly; indels after trimming shared prefix/suffix of REF/ALT
  (no left-alignment without a reference FASTA; users should supply bcftools-normalized VCFs).
- Recessive genes (MUTYH, ATP7B, BTD, GAA, RPE65, HFE C282Y): ACMG SF reports biallelic findings only;
  a single heterozygous P/LP variant is listed as carrier, not as a monogenic finding.
- Chip-derived calls are listed but flagged confirmed_clinical=false and never emitted as observations
  (consumer chips have a very high false-positive rate for rare variants: Weedon et al. 2021 BMJ 372:n214).
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from .. import common
from . import gtio

CLINVAR_URL = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_{build}/clinvar.vcf.gz"
STARS = {
    "practice_guideline": 4,
    "reviewed_by_expert_panel": 3,
    "criteria_provided,_multiple_submitters,_no_conflicts": 2,
    "criteria_provided,_single_submitter": 1,
    "criteria_provided,_conflicting_classifications": 1,
    "criteria_provided,_conflicting_interpretations": 1,
}
PLP = {"Pathogenic", "Likely_pathogenic", "Pathogenic/Likely_pathogenic"}
REFSEQ = {
    "GRCh38": {"1": "NC_000001.11", "2": "NC_000002.12", "3": "NC_000003.12", "4": "NC_000004.12", "5": "NC_000005.10",
               "6": "NC_000006.12", "7": "NC_000007.14", "8": "NC_000008.11", "9": "NC_000009.12", "10": "NC_000010.11",
               "11": "NC_000011.10", "12": "NC_000012.12", "13": "NC_000013.11", "14": "NC_000014.9", "15": "NC_000015.10",
               "16": "NC_000016.10", "17": "NC_000017.11", "18": "NC_000018.10", "19": "NC_000019.10", "20": "NC_000020.11",
               "21": "NC_000021.9", "22": "NC_000022.11", "X": "NC_000023.11", "Y": "NC_000024.10", "MT": "NC_012920.1"},
    "GRCh37": {"1": "NC_000001.10", "2": "NC_000002.11", "3": "NC_000003.11", "4": "NC_000004.11", "5": "NC_000005.9",
               "6": "NC_000006.11", "7": "NC_000007.13", "8": "NC_000008.10", "9": "NC_000009.11", "10": "NC_000010.10",
               "11": "NC_000011.9", "12": "NC_000012.11", "13": "NC_000013.10", "14": "NC_000014.8", "15": "NC_000015.9",
               "16": "NC_000016.9", "17": "NC_000017.10", "18": "NC_000018.9", "19": "NC_000019.9", "20": "NC_000020.10",
               "21": "NC_000021.8", "22": "NC_000022.10", "X": "NC_000023.10", "Y": "NC_000024.9", "MT": "NC_012920.1"},
}


def load_genes() -> dict:
    return common.load_json(common.data_file("acmg_sf_v3.2.json"))


def review_stars(revstat: str) -> int:
    return STARS.get(revstat, 0)


def trim(pos: int, ref: str, alt: str):
    """Trim shared suffix then prefix; returns (pos, ref, alt) with possibly empty alleles."""
    while len(ref) > 0 and len(alt) > 0 and ref[-1] == alt[-1] and (len(ref) > 1 or len(alt) > 1):
        ref, alt = ref[:-1], alt[:-1]
    while len(ref) > 0 and len(alt) > 0 and ref[0] == alt[0]:
        ref, alt, pos = ref[1:], alt[1:], pos + 1
    return pos, ref, alt


def spdi(build: str, chrom: str, pos: int, ref: str, alt: str) -> str:
    p, r, a = trim(pos, ref, alt)
    return f"{REFSEQ[build].get(chrom, chrom)}:{p - 1}:{r}:{a}"


def cache_path(build: str) -> Path:
    return common.ref_dir("clinvar", build) / "clinvar_acmg_sf.json.gz"


def full_vcf(build: str, *, connections: int = 8) -> Path:
    dest = common.ref_dir("clinvar", build) / "clinvar.vcf.gz"
    return common.download_ranged(CLINVAR_URL.format(build=build), dest, connections=connections)


def subset_vcf(build: str, *, pad: int = 5000, workers: int = 4) -> Path:
    """ACMG SF gene regions of the official ClinVar VCF, fetched by tabix range reads (bcftools),
    one gene per request with per-gene caching so an interrupted fetch resumes.

    Only public gene coordinates are sent; the result keeps the ClinVar ##fileDate header.
    """
    import concurrent.futures as cf
    import shutil
    import subprocess
    d = common.ref_dir("clinvar", build)
    dest = d / "clinvar_acmg_regions.vcf.gz"
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    url = CLINVAR_URL.format(build=build)
    common.check_public_url(url)
    common.offline_guard(url)
    common.drop_bad_index(d, url)
    bcf = shutil.which("bcftools") or "/opt/homebrew/bin/bcftools"
    gdir = d / "genes"
    gdir.mkdir(exist_ok=True)

    def fetch(args, out):
        if out.exists():
            return
        err = ""
        for _ in range(4):
            try:
                r = subprocess.run([bcf, "view", *args, url], cwd=d, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=1800)
            except subprocess.TimeoutExpired:
                err = "timeout"
                continue
            if r.returncode == 0:
                tmp = out.with_suffix(".tmp")
                tmp.write_text(r.stdout)
                tmp.replace(out)
                return
            err = r.stderr[-400:]
        raise RuntimeError(f"ClinVar fetch failed ({out.name}): {err}")

    fetch(["-h"], gdir / "_header.vcf")
    jobs = []
    for g, v in sorted(load_genes()["genes"].items()):
        c, a, b = v[f"region_{build}"]
        jobs.append((["-H", "-r", f"{c}:{max(1, a - pad)}-{b + pad}"], gdir / f"{g}.vcf"))
    with cf.ThreadPoolExecutor(workers) as ex:
        list(ex.map(lambda j: fetch(*j), jobs))
    seen = set()
    tmp = d / "clinvar_acmg_regions.part.vcf.gz"
    with gzip.open(tmp, "wt") as fh:
        fh.write((gdir / "_header.vcf").read_text())
        for _, f in jobs:
            for line in open(f):
                key = line.split("\t", 3)[:3]
                k = tuple(key)
                if k not in seen:
                    seen.add(k)
                    fh.write(line)
    tmp.replace(dest)
    return dest


def build_cache(build: str, vcf: Path | None = None, *, full: bool = False) -> Path:
    """Extract ACMG SF gene records from ClinVar (region subset by default, or the full VCF)."""
    out = cache_path(build)
    if out.exists():
        return out
    vcf = Path(vcf) if vcf else (full_vcf(build) if full else subset_vcf(build))
    genes = load_genes()["genes"]
    entrez = {v["entrez"]: k for k, v in genes.items()}
    release, recs = None, {}
    with gzip.open(vcf, "rt", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#"):
                if line.startswith("##fileDate="):
                    release = line.strip().split("=", 1)[1]
                continue
            f = line.rstrip("\n").split("\t", 8)
            info = f[7]
            gi = _info(info, "GENEINFO")
            if not gi:
                continue
            gsyms = [x.split(":") for x in gi.split("|")]
            gene = next((s for s, i in gsyms if s in genes or i in entrez), None)
            if gene is None:
                continue
            gene = gene if gene in genes else entrez.get(dict(gsyms)[gene])
            chrom = gtio.norm_chrom(f[0])
            pos, ref, alt = int(f[1]), f[3].upper(), f[4].upper()
            if alt in (".", "") or "," in alt:
                continue
            tp, tr, ta = trim(pos, ref, alt)
            key = f"{chrom}:{tp}:{tr}:{ta}"
            recs[key] = {"id": f[2], "chrom": chrom, "pos": pos, "ref": ref, "alt": alt, "gene": gene,
                         "clnsig": _info(info, "CLNSIG"), "revstat": _info(info, "CLNREVSTAT"),
                         "condition": (_info(info, "CLNDN") or "").replace("_", " ").split("|")[0]}
    doc = {"build": build, "release": release, "source": CLINVAR_URL.format(build=build),
           "source_subset": "ACMG SF v3.2 gene regions +-5 kb (tabix range reads)" if not full and vcf.name.startswith("clinvar_acmg") else "full VCF",
           "sha256_source_vcf": common.sha256_file(vcf), "n": len(recs), "records": recs}
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        json.dump(doc, fh, sort_keys=True)
    return out


def _info(info: str, key: str):
    for kv in info.split(";"):
        if kv.startswith(key + "="):
            return kv[len(key) + 1:]
    return None


def load_cache(build: str, path: Path | None = None) -> dict:
    with gzip.open(path or cache_path(build), "rt", encoding="utf-8") as fh:
        return json.load(fh)


def reportable(rec: dict) -> bool:
    sig = (rec.get("clnsig") or "").split("|")[0]
    return sig in PLP and review_stars(rec.get("revstat") or "") >= 2


def interest_positions(cache: dict):
    """Positions to retain while reading (all reportable records; VCF and trimmed coordinates)."""
    for key, rec in cache["records"].items():
        if reportable(rec):
            yield rec["chrom"], rec["pos"]
            c, p, *_ = key.split(":")
            yield c, int(p)


def annotate(g: gtio.Genotypes, build: str, cache: dict, *, confirmed: bool = False) -> list:
    genes = load_genes()["genes"]
    found = {}
    for (chrom, pos), calls in sorted(g.calls.items()):
        for call in calls:
            if call.alleles is None:
                continue
            if call.ref is not None:
                cands = [(a, sum(x == a for x in call.alleles)) for a in call.alts if a in call.alleles]
                for alt, n in cands:
                    tp, tr, ta = trim(pos, call.ref, alt)
                    rec = cache["records"].get(f"{chrom}:{tp}:{tr}:{ta}")
                    if rec and reportable(rec):
                        found[rec["id"]] = (rec, n)
            else:  # chip: compare letters with ClinVar SNV alleles at this position
                for rec in _snv_at(cache, chrom, pos):
                    if not reportable(rec):
                        continue
                    n = sum(x == rec["alt"] for x in call.alleles)
                    if n and set(call.alleles) <= {rec["ref"], rec["alt"]}:
                        found[rec["id"]] = (rec, n)
    out = []
    by_gene = {}
    for vid, (rec, n) in sorted(found.items(), key=lambda kv: (kv[1][0]["gene"], kv[1][0]["pos"])):
        by_gene.setdefault(rec["gene"], []).append((rec, n))
    for gene, items in by_gene.items():
        gd = genes[gene]
        biallelic = sum(n for _, n in items) >= 2
        for rec, n in items:
            reportable_finding = True
            note = None
            if gd["inheritance"] == "AR":
                reportable_finding = biallelic
                if not biallelic:
                    note = "隐性遗传基因的单个杂合变异：携带者，不作为次要发现报告"
            if gene == "HFE":
                c282y = gd["only_c282y_homozygous"][build]
                reportable_finding = (n == 2 and int(rec["pos"]) == c282y[1] and rec["alt"] == c282y[3])
                note = None if reportable_finding else "HFE：仅 p.C282Y 纯合按次要发现报告"

            src = g.source_type
            conf = confirmed if src == "chip" else (src in ("wgs", "wes") or confirmed)
            item = {"gene": gene, "hgnc": gd["hgnc"], "spdi": spdi(build, rec["chrom"], rec["pos"], rec["ref"], rec["alt"]),
                    "clinvar_id": rec["id"], "clnsig": rec["clnsig"], "review_status": rec["revstat"],
                    "review_stars": review_stars(rec["revstat"]), "condition": rec["condition"],
                    "zygosity": "hom" if n == 2 else "het", "disease_ids": gd.get("disease_ids", []),
                    "acmg_sf": True, "acmg_sf_reportable": reportable_finding, "inheritance": gd["inheritance"],
                    "source_type": src, "confirmed_clinical": bool(confirmed),
                    "counts_in_engine": bool(reportable_finding and conf),
                    "clinvar_version": cache.get("release"), "disclosure": "counsel"}
            if src == "chip" and not confirmed:
                item["note"] = ("消费级芯片对罕见致病变异的假阳性率很高（Weedon 2021 BMJ 372:n214），"
                                "需临床级检测确认后才计入风险")
            elif note:
                item["note"] = note
            out.append(item)
    return out


def _snv_at(cache, chrom, pos):
    idx = cache.get("_by_pos")
    if idx is None:
        idx = {}
        for rec in cache["records"].values():
            if len(rec["ref"]) == 1 and len(rec["alt"]) == 1:
                idx.setdefault((rec["chrom"], rec["pos"]), []).append(rec)
        cache["_by_pos"] = idx
    return idx.get((chrom, pos), [])
