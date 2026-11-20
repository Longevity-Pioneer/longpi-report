#!/usr/bin/env python3
"""Apply the dual-independent-build rule to terms already in the registry (one-off migration, 2026-11-20).

    python3 apply_consensus.py --second <dir with B specs> [--second <dir> ...] [--cache <B builder .cache dir> ...] [--dry-run]

For every counted ext.* term (build A = the registry spec) the second build B is <dir>/<id>.json. B is verified offline
against the fetched texts its builder cached (copied into this skill's .cache first). Then:
  agree (B passes verify and at least one outcome agrees)  -> the term stays counted, restricted to agreeing outcomes,
                                                             with B recorded as evidence.replication
  otherwise (no B, B fails, or nothing agrees)             -> the term becomes qualitative; A and B kept in candidates/
Population neutrality is checked before freezing; nothing is written on failure.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import consensus as CN  # noqa: E402
import term_builder as TB  # noqa: E402

RG = TB.RG


def _date() -> str:
    import datetime as _dt
    return _dt.date.today().isoformat()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--second", action="append", required=True)
    ap.add_argument("--cache", action="append", default=[])
    ap.add_argument("--root", default=str(RG.REG_DIR))
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root)
    cache_dst = HERE.parent / ".cache"
    for c in a.cache:
        if Path(c).is_dir():
            shutil.copytree(c, cache_dst, dirs_exist_ok=True)
    seconds = {}
    for d in a.second:
        for p in Path(d).glob("ext.*.json"):
            seconds[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    report, new_terms, to_qual, cands = [], {}, {}, {}
    for tp in sorted((root / "terms").glob("ext.*.json")):
        A = json.loads(tp.read_text(encoding="utf-8"))
        B = seconds.get(A["id"])
        if B is None:
            why = "第二次独立建项未产出规格"
            to_qual[A["id"]], cands[A["id"]] = (A, why), {"id": A["id"], "a": A, "b": None, "why": why}
            report.append((A["id"], "未计入", why))
            continue
        try:
            rb = TB.verify(B, root, offline=True)
        except Exception as e:  # noqa: BLE001 - a malformed second build is a failed second build
            rb = {"verdict": "invalid", "fail": [f"核对出错：{type(e).__name__}: {e}"]}
        cmp = CN.compare(A, B)
        merged, dropped = CN.merge(A, B, cmp) if rb["verdict"] == "auto_accept" else (None, [])
        rec = {"id": A["id"], "a": A, "b": B, "verify_b": rb["verdict"], "verify_b_fail": rb.get("fail", []), "comparison": cmp}
        if merged is not None:
            merged = TB.expand_reference(merged)      # a reference given as population norms is expanded, as add() does
            merged.setdefault("evidence", {}).update({"numbers_verified": True, "verified_at": _date(), "verifier": TB.VERIFIER + " (add-consensus)"})
            merged["status"] = "active"
            new_terms[A["id"]] = merged
            if dropped:
                cands[A["id"]] = rec
            report.append((A["id"], "计入", "一致：" + "、".join(oc for oc, v in cmp["outcomes"].items() if v["agree"])
                           + ("；未计入：" + "；".join(dropped) if dropped else "")))
        else:
            why = ("第二次建项未通过核对：" + "；".join(rb.get("fail", [])[:2])) if rb["verdict"] != "auto_accept" else \
                  ("两次独立建项不一致：" + "；".join(sum((v.get("why", []) for v in cmp["outcomes"].values()), [])[:3]))
            to_qual[A["id"]], cands[A["id"]] = (A, why), dict(rec, why=why)
            report.append((A["id"], "未计入", why))
    # population check on the would-be registry
    cur = {t["id"]: t for t in TB._all_terms(root) if t["id"] not in to_qual}
    cur.update(new_terms)
    pc = TB.check_population(list(cur.values()), n=20000)
    for r in report:
        print(" | ".join(r))
    print(f"计入 {sum(1 for r in report if r[1] == '计入')}，改为定性 {len(to_qual)}；人群中性检查 {'通过' if pc['ok'] else '未通过'}")
    if not pc["ok"]:
        print("；".join(pc["fails"][:10]))
        return 2
    if a.dry_run:
        return 0
    (root / "candidates").mkdir(exist_ok=True)
    for tid, t in new_terms.items():
        (root / "terms" / f"{tid}.json").write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for tid, (A, why) in to_qual.items():
        q = dict(A, why_qualitative_zh=why, demoted_from_counted="2026-11-20 双次独立建项规则")
        (root / "qualitative" / f"{tid}.json").write_text(json.dumps(q, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        (root / "terms" / f"{tid}.json").unlink()
    for tid, rec in cands.items():
        (root / "candidates" / f"{tid}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    man = RG.freeze(root, TB.bump_version(root))
    print("冻结为", man["version"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
