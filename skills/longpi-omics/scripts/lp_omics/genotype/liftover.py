"""Minimal UCSC chain-file liftover for point positions (used to build GRCh37 test fixtures)."""
from __future__ import annotations

import bisect
import gzip

from . import gtio


class Chain:
    def __init__(self, path):
        self.blocks = {}  # chrom -> sorted list of (t_start, t_end, q_chrom, q_start, strand, q_size)
        with gzip.open(path, "rt") as fh:
            cur = None
            for line in fh:
                f = line.split()
                if not f:
                    continue
                if f[0] == "chain":
                    t_chr, t_start = gtio.norm_chrom(f[2]), int(f[5])
                    q_chr, q_size, q_strand, q_start = gtio.norm_chrom(f[7]), int(f[8]), f[9], int(f[10])
                    cur = [t_chr, t_start, q_chr, q_start, q_strand, q_size]
                    continue
                size = int(f[0])
                t_chr, ts, q_chr, qs, strand, qsize = cur
                self.blocks.setdefault(t_chr, []).append((ts, ts + size, q_chr, qs, strand, qsize))
                if len(f) == 3:
                    cur[1] = ts + size + int(f[1])
                    cur[3] = qs + size + int(f[2])
        for c in self.blocks:
            self.blocks[c].sort()
        self.starts = {c: [b[0] for b in v] for c, v in self.blocks.items()}

    def convert(self, chrom: str, pos1: int):
        """1-based position -> (chrom, pos1, strand) or None if unmapped."""
        chrom = gtio.norm_chrom(chrom)
        v = self.blocks.get(chrom)
        if not v:
            return None
        p0 = pos1 - 1
        i = bisect.bisect_right(self.starts[chrom], p0) - 1
        hits = []
        # chains can overlap on the target; scan back a little for alternatives
        for j in range(max(0, i - 3), min(len(v), i + 1)):
            ts, te, qc, qs, strand, qsize = v[j]
            if ts <= p0 < te:
                q = qs + (p0 - ts)
                if strand == "-":
                    q = qsize - q - 1
                hits.append((qc, q + 1, strand))
        if len(hits) != 1:
            return None
        return hits[0]
