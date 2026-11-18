"""Small table readers shared by the non-genome omics modules (offline, deterministic)."""
from __future__ import annotations

import csv
import math
from pathlib import Path

from . import common

MAX_BYTES = 2_000_000_000  # refuse absurdly large inputs early


def _sniff_delim(first_line: str) -> str:
    if "\t" in first_line:
        return "\t"
    if first_line.count(";") > first_line.count(","):
        return ";"
    return ","


def read_table(path: Path | str, comment: str = "#") -> tuple[list[str], list[list[str]]]:
    """Return (header, rows). Lines starting with `comment` before the header are skipped."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f"{path}: file larger than {MAX_BYTES} bytes")
    with common.open_text(path) as fh:
        lines = [ln for ln in fh]
    body = []
    header_seen = False
    for ln in lines:
        s = ln.rstrip("\r\n")
        if not header_seen and (not s.strip() or (comment and s.startswith(comment) and not s.startswith("#clade_name")
                                                    and not s.startswith("#SampleID"))):
            continue
        header_seen = True
        if s.strip():
            body.append(s)
    if not body:
        raise ValueError(f"{path}: empty table")
    if body[0].startswith("#"):
        body[0] = body[0][1:]
    delim = _sniff_delim(body[0])
    rdr = csv.reader(body, delimiter=delim)
    rows = [[c.strip().lstrip("﻿") for c in row] for row in rdr]
    header, rows = rows[0], rows[1:]
    width = len(header)
    for i, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"{path}: row {i + 2} has {len(row)} fields, header has {width}")
    return header, rows


NA = {"", "na", "nan", "null", "none", "."}


def num(s: str) -> float | None:
    if s is None or s.strip().lower() in NA:
        return None
    v = float(s)
    if math.isnan(v) or math.isinf(v):
        return None
    return v


def pick_column(header: list[str], sample: str | None, *, skip: int = 1, what: str = "sample") -> int:
    """Index of the single data column to use. Sample names never leave this function."""
    cols = list(range(skip, len(header)))
    if sample is not None:
        if sample not in header[skip:]:
            raise ValueError(f"--sample not found among {len(cols)} {what} columns")
        return header.index(sample, skip)
    if len(cols) != 1:
        raise ValueError(f"input has {len(cols)} {what} columns; pass --sample to choose one")
    return cols[0]
