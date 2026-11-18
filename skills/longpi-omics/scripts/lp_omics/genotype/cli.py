"""Genotype (VCF / 23andMe-style chip) -> QC, build, ancestry, PRS, APOE, ClinVar ACMG SF, PGx."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from .. import common
from . import clinvar, core, gtio, pgx, prs

TOOLS = {"geno_qc": "0.1.0", "geno_build": "0.1.0", "ancestry_aisnp": "0.1.0", "prs_score": "0.1.0",
         "apoe_genotype": "0.1.0", "clinvar_acmg": "0.1.0", "pgx_cpic": "0.1.0", "impute_beagle": "0.1.0"}
REGISTRY_TERMS = Path(__file__).resolve().parents[4] / "longpi-report" / "registry" / "terms"


def add_arguments(p):
    p.add_argument("input", help="single-sample VCF(.gz) or 23andMe-style genotype text")
    p.add_argument("--build", default="auto", choices=["auto", "GRCh37", "GRCh38"])
    p.add_argument("--source-type", default=None, choices=["wgs", "wes", "chip"],
                   help="default: chip for text files, wgs for VCF")
    p.add_argument("--sample", default=None, help="sample column for multi-sample VCFs (never written out)")
    p.add_argument("--sex", default=None, choices=["M", "F"], help="declared sex for the sex check")
    p.add_argument("--pgs", action="append", default=[], help="PGS Catalog id (repeatable); registry PGS: terms are added")
    p.add_argument("--registry", default=str(REGISTRY_TERMS), help="registry terms dir scanned for PGS: inputs")
    p.add_argument("--min-coverage", type=float, default=0.8)
    p.add_argument("--confirmed", action="store_true",
                   help="rare P/LP calls in this file were confirmed by a clinical laboratory")
    p.add_argument("--no-clinvar", action="store_true")
    p.add_argument("--clinvar-cache", default=None, help="prebuilt ClinVar ACMG cache (json.gz) for the build")
    p.add_argument("--include-filtered", action="store_true", help="also use non-PASS VCF records")
    p.add_argument("--impute", action="store_true", help="impute with Beagle before scoring (needs --panel)")
    p.add_argument("--panel", default=None, help="directory of per-chromosome reference panels (bref3 or vcf.gz)")
    p.add_argument("--offline", action="store_true", help="never download; fail if reference data is not cached")


def registry_pgs(terms_dir: str) -> dict:
    """{pgs_id: [disease ids]} from registry terms whose input code is PGS:<id>."""
    out = {}
    d = Path(terms_dir)
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.json")):
        try:
            t = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        code = ((t.get("input") or {}).get("code") or "")
        if code.startswith("PGS:"):
            pid = code.split(":", 1)[1]
            out.setdefault(pid, [])
            for k in (t.get("effect") or {}):
                if k != "all_cause" and k not in out[pid]:
                    out[pid].append(k)
    return out


def _peek_contigs(path):
    with gtio._open(path) as fh:
        lens = {}
        for line in fh:
            if not line.startswith("##"):
                break
            if line.startswith("##contig=<"):
                kv = dict(x.split("=", 1) for x in line.strip()[10:-1].split(",") if "=" in x)
                if "ID" in kv and kv.get("length", "").isdigit():
                    lens[gtio.norm_chrom(kv["ID"])] = int(kv["length"])
        return lens


def run(args):
    if args.offline:
        os.environ["LONGPI_OMICS_OFFLINE"] = "1"
    path = Path(args.input)
    panel = core.load_panel()
    freqs = common.load_json(common.data_file("aisnp_1kg_freqs.json"))
    reg = registry_pgs(args.registry)
    pgs_ids = sorted(set(args.pgs) | set(reg))
    for pid in pgs_ids:
        prs.check_id(pid)
    provenance, notes = [], []

    # ---- build detection
    fmt = gtio.sniff_format(path)
    src = args.source_type or ("chip" if fmt == "chip" else "wgs")
    scores = {}
    if args.build != "auto":
        build, bmeta = args.build, {"build": args.build, "method": "declared (--build)", "votes": {}}
    else:
        lens = _peek_contigs(path) if fmt == "vcf" else {}
        if lens.get("1") in core.CHR1_LEN:
            build = core.CHR1_LEN[lens["1"]]
            bmeta = {"build": build, "method": "VCF contig header (chr1 length)", "votes": {}}
        else:
            it = gtio.Interest()
            for s in panel.values():
                it.add_pos(s["chrom"], s["pos_GRCh37"])
                it.add_pos(s["chrom"], s["pos_GRCh38"])
                it.rsids.add(s["rsid"])
            g0 = gtio.read(path, it.finalize(), source_type=src, sample=args.sample,
                           pass_only=not args.include_filtered)
            bmeta = core.detect_build(g0, panel)
            build = bmeta["build"]
    provenance.append({"step": "build", "tool": "geno_build", "version": TOOLS["geno_build"],
                       "params": {"method": bmeta["method"], "votes": bmeta["votes"]}})

    # ---- scores and licences
    refused = []
    for pid in pgs_ids:
        meta_lic = None
        try:
            meta_lic = prs.fetch_metadata(pid).get("license")
        except Exception as e:  # metadata unavailable: the scoring-file header is checked below
            notes.append(f"{pid}: Catalog metadata unavailable ({type(e).__name__})")
        if meta_lic and not prs.license_allowed(meta_lic):
            refused.append({"pgs_id": pid, "license": meta_lic})
            continue
        sf = prs.fetch_score(pid, build)
        if not sf.license_ok():
            refused.append({"pgs_id": pid, "license": sf.license})
            continue
        scores[pid] = sf

    # ---- main read with build-specific sites of interest
    it = gtio.Interest()
    for s in panel.values():
        it.add_pos(s["chrom"], s[f"pos_{build}"])
        if any(len(a) != 1 for a in s[f"alleles_{build}"]):
            it.add_pos(s["chrom"], s[f"pos_{build}"] - 1)
        it.rsids.add(s["rsid"])
    for sf in scores.values():
        for _, c, p, *_ in sf.variants():
            if c:
                it.add_pos(c, p)
    cv = None
    if not args.no_clinvar:
        cpath = Path(args.clinvar_cache) if args.clinvar_cache else clinvar.cache_path(build)
        if not cpath.exists():
            if os.environ.get("LONGPI_OMICS_OFFLINE"):
                raise RuntimeError(f"ClinVar cache for {build} not found ({cpath}); run without --offline once")
            clinvar.build_cache(build)
        cv = clinvar.load_cache(build, cpath)
        if cv["build"] != build:
            raise ValueError(f"ClinVar cache is {cv['build']}, genotypes are {build}")
        for c, p in clinvar.interest_positions(cv):
            it.add_pos(c, p)
    # chrX sites for the sex check are counted while streaming (all records), not stored
    g = gtio.read(path, it.finalize(), source_type=src, sample=args.sample, pass_only=not args.include_filtered)
    if args.impute:
        from . import impute
        g, imp_prov = impute.run(path, g, build, args)
        provenance.append(imp_prov)

    q = core.qc(g, build, args.sex)
    q["notes"] = notes + q["notes"]
    provenance.append({"step": "qc", "tool": "geno_qc", "version": TOOLS["geno_qc"],
                       "params": {"pass_only": not args.include_filtered}})
    anc = core.ancestry(g, build, panel, freqs)
    provenance.append({"step": "ancestry", "tool": "ancestry_aisnp", "version": TOOLS["ancestry_aisnp"],
                       "ref_data": {"panel": anc.get("panel"), "frequencies": freqs.get("source")}})

    observations = []
    common_obs = dict(method="tool", platform=src, specimen=None, source_file=_safe_name(path, args.sample or getattr(g, 'sample_name', None)),
                      datetime=args.date)

    # ---- PRS
    prs_out = []
    for pid, sf in scores.items():
        try:
            if not prs.ref_path(pid).exists():
                if os.environ.get("LONGPI_OMICS_OFFLINE"):
                    raise RuntimeError("EAS reference not cached")
                prs.build_reference(pid)
            ref = prs.load_reference(pid)
            res = prs.score_person(g, sf, ref, min_coverage=args.min_coverage)
        except Exception as e:
            res = {"pgs_id": pid, "scored": False, "reason": f"{type(e).__name__}: {e}", "raw": None, "z": None,
                   "percentile": None, "coverage": None, "min_coverage": args.min_coverage, "license": sf.license}
        res["disease_id"] = (reg.get(pid) or [None])[0]
        res["disease_ids"] = reg.get(pid, [])
        prs_out.append(res)
        if res.get("scored"):
            observations.append(common.make_obs(f"PGS:{pid}", res["z"], unit="z (1000G EAS)", tool="prs_score",
                                                source_locator=f"{pid} hmPOS {build}", **common_obs))
        provenance.append({"step": "prs", "tool": "prs_score", "version": TOOLS["prs_score"], "pgs_id": pid,
                           "ref_data": {"pgs_scoring_file": f"{pid} hmPOS {build} {sf.header.get('HmPOS_date', '')}".strip(),
                                        "scoring_file_sha256": common.sha256_file(sf.path),
                                        "reference_panel": f"{prs.kg.PANEL_NAME}; EAS n=504"},
                           "license": sf.license})
    for r_ in refused:
        prs_out.append({"pgs_id": r_["pgs_id"], "scored": False, "reason": "licence does not permit commercial use",
                        "license": r_["license"], "raw": None, "z": None, "percentile": None, "coverage": None,
                        "min_coverage": args.min_coverage, "disease_id": (reg.get(r_["pgs_id"]) or [None])[0]})
        provenance.append({"step": "prs", "tool": "prs_score", "version": TOOLS["prs_score"],
                           "pgs_id": r_["pgs_id"], "refused": "licence", "license": r_["license"]})

    # ---- APOE
    ap = core.apoe(g, build, panel)
    if ap:
        observations.append(common.make_obs("LP:apoe_e4_count", ap["e4_count"], unit="count", tool="apoe_genotype",
                                            source_locator="rs429358, rs7412", **common_obs))
    provenance.append({"step": "apoe", "tool": "apoe_genotype", "version": TOOLS["apoe_genotype"]})

    # ---- ClinVar
    mono = []
    if cv is not None:
        mono = clinvar.annotate(g, build, cv, confirmed=args.confirmed)
        seen = set()
        for m in mono:
            if m["counts_in_engine"] and m["hgnc"] not in seen:
                seen.add(m["hgnc"])
                observations.append(common.make_obs(f"LP:monogenic:{m['hgnc']}", 1, unit="carrier", tool="clinvar_acmg",
                                                    source_locator=m["spdi"], **common_obs))
        provenance.append({"step": "clinvar", "tool": "clinvar_acmg", "version": TOOLS["clinvar_acmg"],
                           "ref_data": {"clinvar_release": cv.get("release"), "clinvar_source": cv.get("source"),
                                        "clinvar_sha256": cv.get("sha256_full_vcf"),
                                        "gene_list": clinvar.load_genes()["version"]}})

    # ---- PGx
    px = pgx.call_all(g, build, panel)
    provenance.append({"step": "pgx", "tool": "pgx_cpic", "version": TOOLS["pgx_cpic"],
                       "ref_data": {"rules": pgx.load_defs()["source"]}})

    genetics = {"build": build, "source_type": src, "qc": q, "ancestry": anc, "prs": prs_out, "apoe": ap,
                "monogenic": mono, "pgx": px, "pgx_caveat_zh": pgx.load_defs()["caveat_zh"]}
    summary = [f"build {build} ({bmeta['method']}); source {src}; call rate {q['call_rate']}; sex {q['inferred_sex']}",
               "ancestry " + ", ".join(f"{k} {anc.get(k)}" for k in core.SUPERPOPS),
               "APOE " + (ap["genotype"] if ap else "not genotyped")]
    for r_ in prs_out:
        summary.append(f"{r_['pgs_id']}: " + (f"z {r_['z']} pct {r_['percentile']} coverage {r_['coverage']}"
                                             if r_.get("scored") else f"not scored ({r_.get('reason')})"))
    summary.append(f"ACMG SF P/LP: {len(mono)} listed, {sum(m['counts_in_engine'] for m in mono)} counted")
    summary += [f"{x['gene']} {x['diplotype']} {x['phenotype']}" for x in px]
    return {"tool_ids": list(TOOLS), "observations": observations, "provenance": provenance,
            "genetics": genetics, "summary": summary}


def _safe_name(path: Path, sample: str | None) -> str:
    name = path.name
    if sample:
        name = name.replace(sample, "<sample>")
    return re.sub(r"\s+", "_", name)
