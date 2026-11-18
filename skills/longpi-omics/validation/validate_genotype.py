#!/usr/bin/env python3
"""Genotype-tool validations on public data (needs cached 1000G sites, ClinVar caches, plink2).

V1 prs_score vs plink2 --score on the 504 real 1000G EAS genotypes (Pearson, max abs diff), per score.
V2 AF approximation of the EAS reference mean/SD vs the empirical 504-sample distribution (one score).
V3 ancestry_aisnp: leave-one-out superpopulation assignment of the 2504 1000G samples.
V4 pgx_cpic / apoe_genotype: EAS allele frequencies from our callers vs published 1000G/CPIC values.
V5 clinvar_acmg: >=20 known P/LP (>=2 stars) and >=20 known benign ACMG SF variants, both builds.
Results -> validation/results/<tool_id>.json
"""
from __future__ import annotations

import gzip
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from lp_omics import common  # noqa: E402
from lp_omics.genotype import clinvar, core, gtio, kg, pgx, prs  # noqa: E402

RES = HERE / "results"
RES.mkdir(exist_ok=True)
DATE = "2026-11-18"


def save(tool_id, version, dataset, metric, value, passed, details):
    doc = {"tool_id": tool_id, "version": version, "dataset": dataset, "metric": metric, "value": value,
           "passed": bool(passed), "date": DATE, "details": details}
    (RES / f"{tool_id}.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    print(tool_id, metric, value, "PASS" if passed else "FAIL")


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def sample_genotypes(sites_recs, col):
    """In-memory single-sample Genotypes from cached 1000G records (GRCh38 VCF semantics)."""
    calls = {}
    for (c, p), recs in sites_recs.items():
        for ref, alt, gts in recs:
            a = gts[col].replace("|", "/").split("/")
            al = None if any(x not in "01" for x in a) else tuple(ref if x == "0" else alt for x in a)
            calls.setdefault((c, p), []).append(gtio.Call(c, p, ref, (alt,), al, None))
    return gtio.Genotypes("vcf", "wgs", {}, calls, {}, {"records": 0}, [], 0, [])


# ------------------------------------------------------------------ V1 / V2
def v_prs(pgs_ids):
    plink = shutil.which("plink2")
    eas = kg.eas_samples()
    per = {}
    allp = []
    for pid in pgs_ids:
        sf = prs.fetch_score(pid, "GRCh38")
        ref = prs.load_reference(pid)
        var = [v for v in sf.variants() if v[1]]
        recs = kg.query_sites([(c, p) for _, c, p, *_ in var], eas)
        ours = []
        for k in range(len(eas)):
            g = sample_genotypes(recs, k)
            r = prs.score_person(g, sf, ref, min_coverage=0.0)
            ours.append(r["raw"] if r["raw"] is not None else 0.0)
        # plink2 on the same genotypes: write a VCF of the 504 EAS samples at the score sites
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            vcf = td / "eas.vcf"
            with open(vcf, "w") as fh:
                fh.write("##fileformat=VCFv4.2\n##FORMAT=<ID=GT,Number=1,Type=String,Description=\"GT\">\n")
                fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t" + "\t".join(eas) + "\n")
                seen = set()
                for (c, p) in sorted(recs, key=lambda x: (int(x[0]) if x[0].isdigit() else 99, x[1])):
                    for ref_, alt, gts in recs[(c, p)]:
                        vid = f"{c}:{p}:{ref_}:{alt}"
                        if vid in seen:
                            continue
                        seen.add(vid)
                        fh.write(f"{c}\t{p}\t{vid}\t{ref_}\t{alt}\t.\tPASS\t.\tGT\t" + "\t".join(gts) + "\n")
            sc = td / "score.txt"
            n_rows = 0
            with open(sc, "w") as fh:
                for i, c, p, e, o, w in var:
                    if str(i) not in ref["rows"]:
                        continue
                    for ref_, alt, _ in sorted(recs.get((c, p), []), key=lambda r: not (o and {e, o} == {r[0], r[1]})):
                        if e in (ref_, alt):
                            fh.write(f"{c}:{p}:{ref_}:{alt}\t{e}\t{w!r}\n")
                            n_rows += 1
                            break
            cmd = [plink, "--vcf", str(vcf), "--score", str(sc), "1", "2", "3", "cols=+scoresums",
                   "no-mean-imputation", "--out", str(td / "o"), "--threads", "1"]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(r.stdout[-1500:] + r.stderr[-1500:])
            lines = (td / "o.sscore").read_text().splitlines()
            hdr = lines[0].split()
            j = hdr.index("SCORE1_SUM")
            pl = {ln.split()[0]: float(ln.split()[j]) for ln in lines[1:]}
        theirs = [pl[s] for s in eas]
        rho = pearson(ours, theirs)
        mad = max(abs(a - b) for a, b in zip(ours, theirs))
        # V2: AF approximation vs empirical
        used = [(w, ref["rows"][str(i)]["d"]) for i, c, p, e, o, w in var if str(i) in ref["rows"]]
        m_af, sd_af = prs.af_approximation(used)
        emp = prs._ref_scores([(0, w, d) for w, d in used], ref["n"])
        m_e = sum(emp) / len(emp)
        sd_e = math.sqrt(sum((x - m_e) ** 2 for x in emp) / (len(emp) - 1))
        per[pid] = {"n_weight_variants": len(list(sf.variants())), "n_in_panel": ref["n_in_panel"],
                    "plink2_rows": n_rows, "pearson": round(rho, 8), "max_abs_diff": mad,
                    "af_mean": round(m_af, 6), "emp_mean": round(m_e, 6), "af_sd": round(sd_af, 6),
                    "emp_sd": round(sd_e, 6), "sd_ratio_af_over_emp": round(sd_af / sd_e, 4)}
        allp.append(rho)
        print(pid, per[pid])
    ver = subprocess.run([plink, "--version"], capture_output=True, text=True).stdout.strip()
    save("prs_score", "0.1.0", f"1000 Genomes NYGC 30x GRCh38, 504 EAS unrelated; scores {', '.join(pgs_ids)}",
         "min Pearson vs plink2 --score (sums, no-mean-imputation)", round(min(allp), 8),
         min(allp) >= 0.99 and all(v["max_abs_diff"] < 1e-6 for v in per.values()),
         {"plink2": ver, "per_score": per,
          "af_approximation_note": "the tool uses the empirical 504-sample distribution; AF-only mean/SD reported for comparison"})


# ------------------------------------------------------------------ V3
def v_ancestry():
    panel = core.load_panel()
    freqs = common.load_json(common.data_file("aisnp_1kg_freqs.json"))["snps"]
    samples = kg.sample_panel()
    names = [s for s, *_ in samples]
    sp = {s: p for s, _, p, _ in samples}
    ais = [panel[r] for r in freqs]
    recs = kg.query_sites([(s["chrom"], s["pos_GRCh38"]) for s in ais], names)
    correct, conf = 0, {}
    eas_q = []
    for k, name in enumerate(names):
        obs = []
        for rs, f in freqs.items():
            s = panel[rs]
            cand = [c for c in recs.get((s["chrom"], s["pos_GRCh38"]), []) if c[0] == f["ref"] and c[1] == f["alt"]]
            if not cand:
                continue
            a = cand[0][2][k].replace("|", "/").split("/")
            if any(x not in "01" for x in a):
                continue
            d = sum(x == "1" for x in a)
            # leave-one-out frequencies
            af = []
            for pop in core.SUPERPOPS:
                ac, an = f["ac"][pop], f["an"][pop]
                if pop == sp[name]:
                    ac, an = ac - d, an - 2
                af.append(min(max(ac / an, 1e-3), 1 - 1e-3))
            obs.append((d, af))
        q = core.estimate_q(obs)
        best = core.SUPERPOPS[max(range(5), key=lambda i: q[i])]
        conf.setdefault(sp[name], {}).setdefault(best, 0)
        conf[sp[name]][best] += 1
        correct += best == sp[name]
        if sp[name] == "EAS":
            eas_q.append(q[core.SUPERPOPS.index("EAS")])
    acc = correct / len(names)
    eas_acc = conf["EAS"].get("EAS", 0) / sum(conf["EAS"].values())
    save("ancestry_aisnp", "0.1.0", "1000 Genomes 2504 unrelated (leave-one-out frequencies), Kidd 55 AISNPs",
         "EAS samples assigned to EAS (argmax q)", round(eas_acc, 4), eas_acc >= 0.99,
         {"overall_accuracy": round(acc, 4), "confusion": conf, "mean_q_EAS_in_EAS": round(sum(eas_q) / len(eas_q), 4),
          "note": "AMR and SAS are admixed / close to EUR at 55 SNPs; proportions are coarse, EAS vs non-EAS is reliable"})


# ------------------------------------------------------------------ V4
PUBLISHED_EAS = {  # allele frequencies in East Asians (CPIC frequency tables / gnomAD / 1000G)
    ("CYP2C19", "*2"): 0.29, ("CYP2C19", "*3"): 0.07, ("CYP2C19", "*17"): 0.02,
    ("CYP2C9", "*3"): 0.034, ("CYP3A5", "*3"): 0.71, ("NUDT15", "*3"): 0.09, ("TPMT", "*3C"): 0.016,
    ("VKORC1", "alt"): 0.89, ("SLCO1B1", "alt"): 0.12, ("APOE", "e4"): 0.09, ("APOE", "e2"): 0.08,
}


def v_pgx():
    panel = core.load_panel()
    eas = kg.eas_samples()
    sites = set()
    for s in panel.values():
        if s["group"] in ("pgx", "apoe"):
            sites.add((s["chrom"], s["pos_GRCh38"]))
            if any(len(a) != 1 for a in s["alleles_GRCh38"]):
                sites.add((s["chrom"], s["pos_GRCh38"] - 1))
    recs = kg.query_sites(sorted(sites), eas)
    defs = pgx.load_defs()["genes"]
    counts = {}
    n_called = {}
    e4 = e2 = n_apoe = 0
    for k in range(len(eas)):
        g = sample_genotypes(recs, k)
        for r in pgx.call_all(g, "GRCh38", panel):
            if not r["called"]:
                continue
            n_called[r["gene"]] = n_called.get(r["gene"], 0) + 1
            if defs[r["gene"]]["model"] == "genotype":
                n = next(iter(r["snps"].values()))
                counts[(r["gene"], "alt")] = counts.get((r["gene"], "alt"), 0) + n
            else:
                for star in r["diplotype"].split("/"):
                    if star != "*1":
                        counts[(r["gene"], star)] = counts.get((r["gene"], star), 0) + 1
        a = core.apoe(g, "GRCh38", panel)
        if a:
            n_apoe += 1
            e4 += a["e4_count"]
            e2 += a["genotype"].count("e2")
    rows = {}
    worst = 0.0
    for key, pub in PUBLISHED_EAS.items():
        if key[0] == "APOE":
            obs = (e4 if key[1] == "e4" else e2) / (2 * n_apoe)
        else:
            obs = counts.get(key, 0) / (2 * n_called.get(key[0], 1))
        rows[f"{key[0]} {key[1]}"] = {"observed_1000G_EAS": round(obs, 4), "published_EAS": pub}
        worst = max(worst, abs(obs - pub))
    save("pgx_cpic", "0.1.0", "1000 Genomes NYGC 30x, 504 EAS; CPIC/gnomAD East Asian allele frequencies",
         "max |observed - published| allele frequency", round(worst, 4), worst <= 0.05,
         {"alleles": rows, "n_called": n_called,
          "note": "frequency agreement checks allele orientation and the caller; it is not a per-sample truth set"})
    apo = {k: v for k, v in rows.items() if k.startswith("APOE")}
    save("apoe_genotype", "0.1.0", "1000 Genomes NYGC 30x, 504 EAS", "max |e2/e4 frequency - published EAS|",
         round(max(abs(v["observed_1000G_EAS"] - v["published_EAS"]) for v in apo.values()), 4),
         all(abs(v["observed_1000G_EAS"] - v["published_EAS"]) <= 0.03 for v in apo.values()),
         {"alleles": apo, "n": n_apoe})


# ------------------------------------------------------------------ V5
def v_clinvar(n_each=25, seed=7):
    out = {}
    ok_all = True
    cv38 = clinvar.load_cache("GRCh38")
    cv37 = clinvar.load_cache("GRCh37")
    id37 = {r["id"]: r for r in cv37["records"].values()}
    rnd = random.Random(seed)
    plp = [r for r in cv38["records"].values() if clinvar.reportable(r) and r["id"] in id37
           and clinvar.reportable(id37[r["id"]]) and r["gene"] not in ("HFE",)
           and clinvar.load_genes()["genes"][r["gene"]]["inheritance"] != "AR"]
    ben = [r for r in cv38["records"].values() if (r.get("clnsig") or "") in ("Benign", "Likely_benign", "Benign/Likely_benign")
           and r["id"] in id37 and clinvar.review_stars(r.get("revstat") or "") >= 2]
    vus = [r for r in cv38["records"].values() if (r.get("clnsig") or "") == "Uncertain_significance" and r["id"] in id37]
    rnd.shuffle(plp); rnd.shuffle(ben); rnd.shuffle(vus)
    snv = lambda r: len(r["ref"]) == 1 and len(r["alt"]) == 1
    pick_p = [r for r in plp if snv(r)][:n_each - 5] + [r for r in plp if not snv(r)][:5]
    pick_b = [r for r in ben if snv(r)][:n_each - 5] + [r for r in ben if not snv(r)][:5]
    pick_v = vus[:10]
    for build, cv in (("GRCh38", cv38), ("GRCh37", cv37)):
        res = {"pathogenic_called": 0, "benign_called": 0, "vus_called": 0}
        for group, picks in (("pathogenic", pick_p), ("benign", pick_b), ("vus", pick_v)):
            for r in picks:
                rr = r if build == "GRCh38" else id37[r["id"]]
                g = gtio.Genotypes("vcf", "wgs", {}, {(rr["chrom"], rr["pos"]): [
                    gtio.Call(rr["chrom"], rr["pos"], rr["ref"], (rr["alt"],), (rr["ref"], rr["alt"]), None)]},
                    {}, {"records": 1}, [], 0, [])
                hits = clinvar.annotate(g, build, cv)
                res[f"{group}_called"] += bool(hits and hits[0]["clinvar_id"] == r["id"])
        res["pathogenic_total"], res["benign_total"], res["vus_total"] = len(pick_p), len(pick_b), len(pick_v)
        ok = (res["pathogenic_called"] == len(pick_p) and res["benign_called"] == 0 and res["vus_called"] == 0)
        ok_all &= ok
        out[build] = res
    out["releases"] = {"GRCh38": cv38["release"], "GRCh37": cv37["release"]}
    out["pathogenic_ids"] = [r["id"] for r in pick_p]
    out["benign_ids"] = [r["id"] for r in pick_b]
    out["vus_ids"] = [r["id"] for r in pick_v]
    save("clinvar_acmg", "0.1.0", "ClinVar VCF GRCh38 + GRCh37, ACMG SF v3.2 genes, heterozygous test calls",
         "known P/LP correctly reported AND benign/VUS never reported (both builds)",
         f"{out['GRCh38']['pathogenic_called']}/{len(pick_p)} P/LP, 0/{len(pick_b)} benign, 0/{len(pick_v)} VUS"
         if ok_all else "see details", ok_all, out)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    pgs_ids = ["PGS002262", "PGS003353", "PGS000050", "PGS000070"]
    if which in ("all", "prs"):
        v_prs(pgs_ids)
    if which in ("all", "ancestry"):
        v_ancestry()
    if which in ("all", "pgx"):
        v_pgx()
    if which in ("all", "clinvar"):
        v_clinvar()
