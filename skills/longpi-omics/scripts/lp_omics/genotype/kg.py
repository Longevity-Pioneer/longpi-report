"""1000 Genomes reference access (public data, remote tabix range reads via bcftools).

Panel: NYGC 30x high-coverage phased panel, GRCh38 (3202 samples; the 2504 unrelated phase-3 samples
are used, EAS n=504). Only public score/panel positions are requested; no personal data is sent.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import os
import shutil
import subprocess
from pathlib import Path

from .. import common

PANEL_NAME = "1000 Genomes NYGC 30x phased panel GRCh38 (20220422), 2504 unrelated samples"
BASE = ("https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/1000G_2504_high_coverage/working/"
        "20220422_3202_phased_SNV_INDEL_SV/")
SAMPLE_PANEL_URL = ("https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"
                    "integrated_call_samples_v3.20130502.ALL.panel")


def vcf_url(chrom: str) -> str:
    if chrom == "X":
        return BASE + "1kGP_high_coverage_Illumina.chrX.filtered.SNV_INDEL_SV_phased_panel.v2.vcf.gz"
    return BASE + f"1kGP_high_coverage_Illumina.chr{chrom}.filtered.SNV_INDEL_SV_phased_panel.vcf.gz"


def bcftools() -> str:
    b = shutil.which("bcftools") or "/opt/homebrew/bin/bcftools"
    if not Path(b).exists():
        raise RuntimeError("bcftools is required to build 1000 Genomes reference data")
    return b


def sample_panel() -> list[tuple[str, str, str, str]]:
    p = common.download(SAMPLE_PANEL_URL, common.ref_dir("1kg") / "integrated_call_samples_v3.20130502.ALL.panel")
    out = []
    for line in open(p):
        f = line.split()
        if len(f) >= 4 and f[0] != "sample":
            out.append((f[0], f[1], f[2], f[3]))  # sample pop super_pop gender
    return sorted(out)


def eas_samples() -> list[str]:
    return [s for s, _, sp, _ in sample_panel() if sp == "EAS"]


def unrelated_samples() -> list[str]:
    return [s for s, *_ in sample_panel()]


def _run_query(c, cdir, sfile, lines):
    common.drop_bad_index(cdir, vcf_url(c))
    reg = cdir / f"regions_{os.getpid()}_{abs(hash(sfile)) % 1000}.txt"
    reg.write_text("".join(lines))
    cmd = [bcftools(), "query", "-R", str(reg), "-S", str(sfile), "--force-samples",
           "-f", "%CHROM\t%POS\t%REF\t%ALT[\t%GT]\n", vcf_url(c)]
    for _ in range(3):
        r = subprocess.run(cmd, cwd=cdir, capture_output=True, text=True)
        if r.returncode == 0:
            break
    else:
        raise RuntimeError(f"bcftools query chr{c} failed: {r.stderr[-500:]}")
    reg.unlink(missing_ok=True)
    return r.stdout.splitlines()


def query_sites(sites, samples, *, regions=None, workers: int = 12):
    """Return {(chrom, pos): [(ref, alt, [gt per requested sample])]} for GRCh38 sites.

    Exact sites are fetched once for all 2504 unrelated samples and cached locally
    (`tabix_cache/chr*/sites.tsv`), so later scores or panels reuse them without network.
    `regions` (chrom, start, end) are fetched directly for the requested samples (fixture building).
    """
    allsamp = unrelated_samples()
    col = {s: i for i, s in enumerate(allsamp)}
    missing = [s for s in samples if s not in col]
    if missing and not regions:
        raise ValueError(f"{len(missing)} requested samples are not in the 2504 unrelated set")
    work = common.ref_dir("1kg", "tabix_cache")
    s_all = work / "samples_2504.txt"
    s_all.write_text("\n".join(allsamp) + "\n")
    s_req = work / ("samples_" + hashlib.sha1("\n".join(samples).encode()).hexdigest()[:12] + ".txt")
    s_req.write_text("\n".join(samples) + "\n")
    by_chr, iv_chr = {}, {}
    for c, p in sites:
        by_chr.setdefault(c, set()).add(int(p))
    for c, s, e in regions or ():
        iv_chr.setdefault(c, set()).add((int(s), int(e)))

    def run(c):
        cdir = work / f"chr{c}"
        cdir.mkdir(exist_ok=True)
        cache, done = cdir / "sites.tsv", cdir / "queried.txt"
        have = set(int(x) for x in done.read_text().split()) if done.exists() else set()
        need = sorted(by_chr.get(c, set()) - have)
        if need:
            common.offline_guard(vcf_url(c))
            lines = _run_query(c, cdir, s_all, [f"chr{c}\t{p}\t{p}\n" for p in need])
            needset = set(need)
            with open(cache, "a") as fh:
                for ln in lines:
                    if int(ln.split("\t", 2)[1]) in needset:
                        fh.write(ln + "\n")
            with open(done, "a") as fh:
                fh.write("".join(f"{p}\n" for p in need))
        out = {}
        want = by_chr.get(c, set())
        if want and cache.exists():
            idx = [col[s] for s in samples]
            for ln in open(cache):
                f = ln.rstrip("\n").split("\t")
                p = int(f[1])
                if p in want:
                    g = f[4:]
                    rec = (f[2], f[3], [g[i] for i in idx])
                    if rec not in out.get((c, p), []):
                        out.setdefault((c, p), []).append(rec)
        if c in iv_chr:
            common.offline_guard(vcf_url(c))
            lines = _run_query(c, cdir, s_req, [f"chr{c}\t{s}\t{e}\n" for s, e in sorted(iv_chr[c])])
            for ln in lines:
                f = ln.split("\t")
                rec = (f[2], f[3], f[4:])
                if rec not in out.get((c, int(f[1])), []):
                    out.setdefault((c, int(f[1])), []).append(rec)
        return out

    res = {}
    chroms = sorted(set(by_chr) | set(iv_chr))
    with cf.ThreadPoolExecutor(min(workers, len(chroms) or 1)) as ex:
        for d in ex.map(run, chroms):
            res.update(d)
    return res
