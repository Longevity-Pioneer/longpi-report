"""Optional genotype imputation with Beagle 5.x (Browning et al. 2018 AJHG; Beagle is GPLv3, run as an
external program, not linked).

Panel directory layout (user supplied; this tool never downloads whole-genome panels):
  <panel>/chr<N>.vcf.gz (or .bref3)   phased reference panel, same build as the input
  <panel>/plink.chr<N>.<build>.map    optional PLINK genetic map
  <panel>/beagle.jar                  Beagle jar (or env LONGPI_BEAGLE_JAR)
Java: env LONGPI_JAVA or `java` on PATH (e.g. Homebrew openjdk).

Chip input is converted to VCF using the panel's REF/ALT at matching positions (strand-consistent
sites only; palindromic A/T, C/G sites are dropped). Imputed calls with Beagle DR2 >= min_dr2 are added
to the genotype set; genotyped calls are never overwritten. Seed and thread count are fixed for
reproducibility.
"""
from __future__ import annotations

import gzip
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import gtio

SEED = 20261118


def _java():
    j = os.environ.get("LONGPI_JAVA") or shutil.which("java") or "/opt/homebrew/opt/openjdk/bin/java"
    r = subprocess.run([j, "-version"], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("Java runtime not found; install OpenJDK (e.g. brew install openjdk) or set LONGPI_JAVA")
    return j


def _panel_files(panel: Path):
    out = {}
    for f in sorted(panel.iterdir()):
        n = f.name
        for suf in (".bref3", ".vcf.gz"):
            if n.startswith("chr") and n.endswith(suf):
                out[gtio.norm_chrom(n[3:-len(suf)])] = f
    return out


def _panel_sites(vcf: Path):
    sites = {}
    with gzip.open(vcf, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.split("\t", 6)
            if "," in f[4]:
                continue
            sites[int(f[1])] = (f[0], f[3], f[4])
    return sites


def to_vcf(g: gtio.Genotypes, chrom: str, panel_vcf: Path, out: Path) -> int:
    """Write the person's calls on one chromosome as a single-sample VCF aligned to the panel alleles."""
    sites = _panel_sites(panel_vcf)
    n = 0
    with gzip.open(out, "wt") as fh:
        fh.write("##fileformat=VCFv4.2\n##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">\n")
        fh.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tS1\n")
        for (c, p), calls in sorted(g.calls.items(), key=lambda kv: kv[0][1]):
            if c != chrom or p not in sites:
                continue
            pc, ref, alt = sites[p]
            if gtio.comp(ref) == alt:
                continue
            for call in calls:
                if call.alleles is None or len(call.alleles) != 2:
                    continue
                al = list(call.alleles)
                if not set(al) <= {ref, alt}:
                    fl = [gtio.comp(a) for a in al]
                    if set(fl) <= {ref, alt}:
                        al = fl
                    else:
                        continue
                gt = "/".join("0" if a == ref else "1" for a in al)
                fh.write(f"{pc}\t{p}\t.\t{ref}\t{alt}\t.\tPASS\t.\tGT\t{gt}\n")
                n += 1
                break
    return n


def run(path: Path, g: gtio.Genotypes, build: str, args, *, min_dr2: float = 0.8, nthreads: int = 1):
    if not args.panel:
        raise ValueError("--impute needs --panel <dir>")
    panel = Path(args.panel)
    jar = Path(os.environ.get("LONGPI_BEAGLE_JAR") or panel / "beagle.jar")
    if not jar.exists():
        raise RuntimeError(f"Beagle jar not found at {jar}")
    java = _java()
    files = _panel_files(panel)
    if not files:
        raise RuntimeError(f"no chr*.vcf.gz / chr*.bref3 panels in {panel}")
    it = gtio.Interest()
    for chrom in files:
        it.add_interval(chrom, 1, 400_000_000)
    g_full = gtio.read(path, it.finalize(), source_type=g.source_type, sample=getattr(args, "sample", None),
                       pass_only=not getattr(args, "include_filtered", False))
    added, per_chr = 0, {}
    with tempfile.TemporaryDirectory(prefix="lp_impute_") as td:
        td = Path(td)
        for chrom, pf in files.items():
            gt_vcf = td / f"in.chr{chrom}.vcf.gz"
            n_in = to_vcf(g_full, chrom, pf if pf.suffix == ".gz" else pf.with_suffix(".vcf.gz"), gt_vcf)
            if n_in == 0:
                continue
            cmd = [java, "-Xmx4g", "-jar", str(jar), f"gt={gt_vcf}", f"ref={pf}", f"out={td}/out.chr{chrom}",
                   f"seed={SEED}", f"nthreads={nthreads}", "impute=true", "gp=false"]
            mp = sorted(panel.glob(f"plink.chr{chrom}.*.map"))
            if mp:
                cmd.append(f"map={mp[0]}")
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError(f"Beagle failed on chr{chrom}: {r.stderr[-800:]}")
            n_add = 0
            with gzip.open(td / f"out.chr{chrom}.vcf.gz", "rt") as fh:
                for line in fh:
                    if line.startswith("#"):
                        continue
                    f = line.rstrip("\n").split("\t")
                    info = dict(kv.split("=", 1) for kv in f[7].split(";") if "=" in kv)
                    if "IMP" not in f[7].split(";"):
                        continue
                    if float(info.get("DR2", "0")) < min_dr2:
                        continue
                    c, p = gtio.norm_chrom(f[0]), int(f[1])
                    if g.calls.get((c, p)):
                        continue
                    idx = f[9].split(":")[0].replace("|", "/").split("/")
                    al = (f[3], f[4])
                    g.calls[(c, p)] = [gtio.Call(c, p, f[3], (f[4],), tuple(al[int(i)] for i in idx), None)]
                    n_add += 1
            per_chr[chrom] = {"input_sites": n_in, "imputed_added": n_add}
            added += n_add
    g.notes.append(f"Beagle imputation added {added} calls with DR2 >= {min_dr2}")
    return g, {"step": "impute", "tool": "impute_beagle", "version": "0.1.0",
               "params": {"seed": SEED, "nthreads": nthreads, "min_dr2": min_dr2, "per_chrom": per_chr},
               "ref_data": {"panel_dir": panel.name, "beagle_jar": jar.name}}
