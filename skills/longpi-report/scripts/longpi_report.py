#!/usr/bin/env python3
"""LongPi report command line (standard library only, Python 3.9+).

  longpi_report.py check   person.json                  validate inputs, list what is missing
  longpi_report.py compute person.json -o results.json  run the engine (adds chart series)
  longpi_report.py facts   results.json                 compact fact sheet for writing the narrative
  longpi_report.py render  results.json narrative.json -o report.html
  longpi_report.py demo    [-o outdir]                  synthetic example end to end

Paths inside person.json (wearable exports, CGM, BP logs) are relative to the person file.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lp import derive as DV  # noqa: E402
from lp import engine as EN  # noqa: E402
from lp import render as RD  # noqa: E402
from lp import schema as SC  # noqa: E402

SKILL = HERE.parent


def cmd_check(a) -> int:
    person = json.loads(Path(a.person).read_text(encoding="utf-8"))
    rep = SC.check(person, Path(a.person).parent)
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return 0 if not rep["errors"] else 2


def cmd_compute(a) -> int:
    pfile = Path(a.person)
    person = json.loads(pfile.read_text(encoding="utf-8"))
    rep = SC.check(person, pfile.parent)
    if rep["errors"]:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
        return 2
    derived = DV.derive(person, pfile.parent)
    res = EN.run(person, derived, n_draws=a.draws, seed=a.seed)
    out = {"results": res, "data": derived["data"], "wearables": derived["wearables"],
           "person_meta": {"code": person["person"].get("code", ""), "synthetic": bool(person.get("synthetic")),
                           "label": person["person"].get("label", "")},
           "checks": rep}
    Path(a.output).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    la = res["longpi_age"]
    print(f"LongPi Age {la['value']['median']} (80% {la['value']['p10']}-{la['value']['p90']}), "
          f"chrono {la['chrono']}; 120 Index (weighted) {res['index120']['weighted_index']['median']}")
    print(f"wrote {a.output}")
    return 0


def cmd_facts(a) -> int:
    out = json.loads(Path(a.results).read_text(encoding="utf-8"))
    print(SC.fact_sheet(out))
    return 0


def cmd_render(a) -> int:
    out = json.loads(Path(a.results).read_text(encoding="utf-8"))
    ev = out.get("results", {}).get("engine_version")
    if ev != EN.ENGINE_VERSION:
        print(f"results.json 由引擎 {ev} 生成，当前为 {EN.ENGINE_VERSION}：请先重新运行 compute", file=sys.stderr)
        return 2
    narrative = json.loads(Path(a.narrative).read_text(encoding="utf-8")) if a.narrative else {}
    problems = SC.check_narrative(narrative, out)
    if problems:
        print("narrative problems:\n- " + "\n- ".join(problems), file=sys.stderr)
        if a.strict:
            return 2
    params = json.loads((SKILL / "data" / "params.json").read_text(encoding="utf-8"))
    evidence = json.loads((SKILL / "data" / "evidence_summary.json").read_text(encoding="utf-8")) \
        if (SKILL / "data" / "evidence_summary.json").exists() else None
    pm = out.get("person_meta", {})
    meta = {"title": a.title or "LongPi 报告", "person_label": pm.get("label") or pm.get("code", ""),
            "synthetic": pm.get("synthetic", False),
            "banner": narrative.get("banner") or ("⚠ 演示页：全部数值为程序生成的虚构数据，不对应任何真实个人。" if pm.get("synthetic") else ""),
            "footer": narrative.get("footer", "")}
    RD.render(out["results"], dict(out["data"], wearables=out.get("wearables", {})), narrative, meta, params, evidence, Path(a.output),
              base=Path(a.narrative).resolve().parent if a.narrative else None)
    print(f"wrote {a.output}")
    return 0


def cmd_demo(a) -> int:
    outdir = Path(a.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    ex = SKILL / "examples"
    ns = argparse.Namespace(person=str(ex / "demo_person.json"), output=str(outdir / "results.json"), draws=a.draws, seed=20261024)
    if cmd_compute(ns):
        return 2
    nr = ex / "demo_narrative.json"
    return cmd_render(argparse.Namespace(results=str(outdir / "results.json"), narrative=str(nr) if nr.exists() else None,
                                         output=str(outdir / "report.html"), title="LongPi Demo", strict=False))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check"); p.add_argument("person"); p.set_defaults(f=cmd_check)
    p = sub.add_parser("compute"); p.add_argument("person"); p.add_argument("-o", "--output", default="results.json")
    p.add_argument("--draws", type=int, default=2000); p.add_argument("--seed", type=int, default=20261024); p.set_defaults(f=cmd_compute)
    p = sub.add_parser("facts"); p.add_argument("results"); p.set_defaults(f=cmd_facts)
    p = sub.add_parser("render"); p.add_argument("results"); p.add_argument("narrative", nargs="?")
    p.add_argument("-o", "--output", default="report.html"); p.add_argument("--title"); p.add_argument("--strict", action="store_true")
    p.set_defaults(f=cmd_render)
    p = sub.add_parser("demo"); p.add_argument("-o", "--outdir", default="longpi_demo_out"); p.add_argument("--draws", type=int, default=1500)
    p.set_defaults(f=cmd_demo)
    a = ap.parse_args(argv)
    return a.f(a)


if __name__ == "__main__":
    raise SystemExit(main())
