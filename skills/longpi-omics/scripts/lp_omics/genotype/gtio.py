"""Genotype readers: single-sample VCF (plain or gz) and 23andMe-style chip text.

The reader streams the file once. It keeps QC counters for every record but only stores
records that fall on "sites of interest" (panel SNPs, PRS variants, ACMG gene intervals for
either build), so whole-genome VCFs do not have to fit in memory.
"""
from __future__ import annotations

import bisect
import gzip
from dataclasses import dataclass, field
from pathlib import Path

COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}

# Pseudo-autosomal regions (1-based, inclusive)
PAR = {
    "GRCh38": [(10001, 2781479), (155701383, 156030895)],
    "GRCh37": [(60001, 2699520), (154931044, 155260560)],
}


def norm_chrom(c: str) -> str:
    c = c.strip()
    if c.lower().startswith("chr"):
        c = c[3:]
    c = c.upper()
    return {"23": "X", "24": "Y", "25": "X", "26": "MT", "M": "MT", "XY": "X"}.get(c, c)


def comp(a: str) -> str:
    return "".join(COMP.get(x, "N") for x in a[::-1]) if len(a) > 1 else COMP.get(a, "N")


@dataclass
class Call:
    chrom: str
    pos: int
    ref: str | None          # None for chip data (no reference allele in the file)
    alts: tuple              # () for chip data
    alleles: tuple | None    # called alleles as strings; None = missing
    rsid: str | None = None


@dataclass
class Interest:
    """Sites to retain while streaming: exact positions and intervals, keyed by chromosome."""
    positions: dict = field(default_factory=dict)   # chrom -> set(pos)
    intervals: dict = field(default_factory=dict)   # chrom -> sorted list of (start, end)
    rsids: set = field(default_factory=set)

    def add_pos(self, chrom, pos):
        self.positions.setdefault(norm_chrom(str(chrom)), set()).add(int(pos))

    def add_interval(self, chrom, start, end):
        self.intervals.setdefault(norm_chrom(str(chrom)), []).append((int(start), int(end)))

    def finalize(self):
        for c, iv in self.intervals.items():
            iv.sort()
            merged = []
            for s, e in iv:
                if merged and s <= merged[-1][1] + 1:
                    merged[-1] = (merged[-1][0], max(merged[-1][1], e))
                else:
                    merged.append((s, e))
            self.intervals[c] = merged
        self._starts = {c: [s for s, _ in iv] for c, iv in self.intervals.items()}
        return self

    def wants(self, chrom, pos, rsid=None):
        if rsid and rsid in self.rsids:
            return True
        if pos in self.positions.get(chrom, ()):
            return True
        iv = self.intervals.get(chrom)
        if iv:
            i = bisect.bisect_right(self._starts[chrom], pos) - 1
            if i >= 0 and iv[i][0] <= pos <= iv[i][1]:
                return True
        return False


@dataclass
class Genotypes:
    fmt: str                         # "vcf" | "chip"
    source_type: str                 # wgs | wes | chip
    contig_lengths: dict
    calls: dict                      # (chrom, pos) -> [Call]
    by_rsid: dict                    # rsid -> (chrom, pos)
    counters: dict                   # raw counters for QC (build-independent)
    xcalls: list                     # (pos, is_het, ploidy) for chrX calls, for the sex check
    n_y_called: int
    notes: list

    def at(self, chrom, pos):
        return self.calls.get((chrom, int(pos)), [])


def _open(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return open(path, "rt", encoding="utf-8", errors="replace")


def sniff_format(path: Path) -> str:
    with _open(path) as fh:
        for i, line in enumerate(fh):
            if line.startswith("##fileformat=VCF"):
                return "vcf"
            if line.startswith("#CHROM"):
                return "vcf"
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) in (4, 5) and (parts[0].startswith("rs") or parts[0].startswith("i")):
                return "chip"
            if i > 200:
                break
    raise ValueError(f"{path}: not a VCF or a 23andMe-style genotype file")


def read(path: Path, interest: Interest, *, source_type: str | None = None, sample: str | None = None,
         pass_only: bool = True) -> Genotypes:
    fmt = sniff_format(path)
    if fmt == "vcf":
        return _read_vcf(path, interest, source_type or "wgs", sample, pass_only)
    if source_type and source_type != "chip":
        raise ValueError("a 23andMe-style text file is chip data; --source-type must be chip")
    return _read_chip(path, interest)


def _new_counters():
    return {"records": 0, "called": 0, "auto_called": 0, "auto_het": 0, "filtered": 0, "multisample": 0}


def _note_x(xcalls, chrom, pos, alleles, ref=None):
    if chrom == "X" and alleles is not None:
        nonref = True if ref is None else any(a != ref for a in alleles)
        xcalls.append((pos, len(set(alleles)) > 1, len(alleles), nonref))


def _read_vcf(path, interest, source_type, sample, pass_only):
    contigs, calls, by_rsid, xcalls, notes = {}, {}, {}, [], []
    ctr = _new_counters()
    n_y = 0
    si = None
    with _open(path) as fh:
        for line in fh:
            if line.startswith("##"):
                if line.startswith("##contig=<"):
                    body = line.strip()[10:-1]
                    kv = dict(p.split("=", 1) for p in body.split(",") if "=" in p)
                    if "ID" in kv and "length" in kv:
                        try:
                            contigs[norm_chrom(kv["ID"])] = int(kv["length"])
                        except ValueError:
                            pass
                continue
            if line.startswith("#CHROM"):
                cols = line.rstrip("\n").split("\t")
                samples = cols[9:]
                if not samples:
                    raise ValueError("VCF has no sample column")
                if sample is not None:
                    if sample not in samples:
                        raise ValueError("requested --sample is not in the VCF")
                    si = 9 + samples.index(sample)
                elif len(samples) == 1:
                    si = 9
                else:
                    raise ValueError(f"VCF has {len(samples)} samples; pass --sample")
                continue
            if si is None:
                raise ValueError("VCF data line before #CHROM header")
            f = line.rstrip("\n").split("\t")
            if len(f) <= si:
                continue
            chrom = norm_chrom(f[0])
            try:
                pos = int(f[1])
            except ValueError:
                continue
            ctr["records"] += 1
            if pass_only and f[6] not in ("PASS", ".", ""):
                ctr["filtered"] += 1
                continue
            ref = f[3].upper()
            alts = tuple(a.upper() for a in f[4].split(",")) if f[4] not in (".", "") else ()
            fmtk = f[8].split(":")
            try:
                gi = fmtk.index("GT")
            except ValueError:
                continue
            gts = f[si].split(":")
            gt = gts[gi] if gi < len(gts) else "."
            idx = gt.replace("|", "/").split("/")
            alleles = None
            if all(x not in (".", "") for x in idx):
                all_alleles = (ref,) + alts
                try:
                    alleles = tuple(all_alleles[int(x)] for x in idx)
                except (ValueError, IndexError):
                    alleles = None
            if alleles is not None:
                ctr["called"] += 1
                if chrom not in ("X", "Y", "MT"):
                    ctr["auto_called"] += 1
                    if len(set(alleles)) > 1:
                        ctr["auto_het"] += 1
                if chrom == "Y" and any(a != ref for a in alleles):
                    n_y += 1
            _note_x(xcalls, chrom, pos, alleles, ref)
            rsid = f[2] if f[2].startswith("rs") else None
            if interest.wants(chrom, pos, rsid):
                calls.setdefault((chrom, pos), []).append(Call(chrom, pos, ref, alts, alleles, rsid))
                if rsid:
                    by_rsid[rsid] = (chrom, pos)
    if ctr["filtered"]:
        notes.append(f"{ctr['filtered']} records with FILTER other than PASS were ignored")
    g = Genotypes("vcf", source_type, contigs, calls, by_rsid, ctr, xcalls, n_y, notes)
    g.sample_name = samples[si - 9] if si is not None else None  # used only to redact; never written out
    return g


def _read_chip(path, interest):
    calls, by_rsid, xcalls, notes = {}, {}, [], []
    ctr = _new_counters()
    n_y = 0
    with _open(path) as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            f = line.rstrip("\n").replace(",", "\t").split("\t")
            if f[0].lower() in ("rsid", "snp", "name"):
                continue
            if len(f) == 5:  # AncestryDNA style: rsid chrom pos allele1 allele2
                f = [f[0], f[1], f[2], (f[3] + f[4])]
            if len(f) < 4:
                continue
            rsid, chrom, pos, g = f[0], norm_chrom(f[1]), f[2], f[3].strip().upper()
            try:
                pos = int(pos)
            except ValueError:
                continue
            ctr["records"] += 1
            if g in ("--", "00", "", "NC") or any(ch not in "ACGT" for ch in g):
                alleles = None  # no call, or indel codes D/I which cannot be matched to alleles
            else:
                alleles = tuple(g)
            if alleles is not None:
                ctr["called"] += 1
                if chrom not in ("X", "Y", "MT"):
                    ctr["auto_called"] += 1
                    if len(set(alleles)) > 1:
                        ctr["auto_het"] += 1
                if chrom == "Y":
                    n_y += 1
            _note_x(xcalls, chrom, pos, alleles)
            rs = rsid if rsid.startswith("rs") else None
            if interest.wants(chrom, pos, rs):
                calls.setdefault((chrom, pos), []).append(Call(chrom, pos, None, (), alleles, rs))
                if rs:
                    by_rsid[rs] = (chrom, pos)
    return Genotypes("chip", "chip", {}, calls, by_rsid, ctr, xcalls, n_y, notes)


def dosage(g: Genotypes, chrom: str, pos: int, effect: str, other: str | None):
    """Copies of `effect` carried at a site, aligned to the score's alleles.

    Returns (dosage | None, status) with status in
    ok | flipped | missing | absent | mismatch | ambiguous.
    """
    effect = effect.upper()
    other = other.upper() if other else None
    recs = g.at(chrom, pos)
    if not recs:
        return None, "absent"
    pal = other is not None and comp(effect) == other
    for c in recs:
        if c.ref is not None:  # VCF: alleles are on the + strand of the reference
            s = {c.ref, *c.alts}
            if effect in s or (other and other in s):
                if c.alleles is None:
                    return None, "missing"
                return sum(a == effect for a in c.alleles), "ok"
        else:  # chip letters
            if c.alleles is None:
                return None, "missing"
            p = set(c.alleles)
            pair = {effect} | ({other} if other else set())
            if other and p <= pair:
                return sum(a == effect for a in c.alleles), "ok"
            if other is None and effect in p:
                return sum(a == effect for a in c.alleles), "ok"
    # try strand flip (never for palindromic A/T, C/G pairs)
    if pal:
        return None, "ambiguous"
    fe = comp(effect)
    fo = comp(other) if other else None
    for c in recs:
        if c.ref is not None:
            s = {c.ref, *c.alts}
            if fe in s or (fo and fo in s):
                if c.alleles is None:
                    return None, "missing"
                return sum(a == fe for a in c.alleles), "flipped"
        else:
            if c.alleles is None:
                return None, "missing"
            p = set(c.alleles)
            if fo and p <= {fe, fo}:
                return sum(a == fe for a in c.alleles), "flipped"
    # chip, no other allele known and effect absent: the person carries 0 copies only if
    # the observed letters are not explainable by a flip; treat as mismatch to stay safe
    return None, "mismatch"
