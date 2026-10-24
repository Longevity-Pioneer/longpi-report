"""Assemble the report page: engine results + wearable/lab series + Claude's narrative."""
from __future__ import annotations

import base64
import copy
import html
import json
import mimetypes
from pathlib import Path
from typing import Optional

ASSETS = Path(__file__).resolve().parents[2] / "assets"


def _safe_json(obj) -> str:
    # keep "</script>" and HTML comments out of the inline script
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("<!--", "<\\!--")


def methods_cards(res: dict, params: dict, evidence: Optional[dict]) -> dict:
    sc = res["index120"]["scenarios"]
    w = res["index120"]["weights"]
    ev = evidence or {}
    val = ev.get("validation", {})
    mp = params.get("methylation", {})
    g2 = mp.get("clocks", {}).get("GrimAge2", {})
    meth_row = (f"只认 GrimAge2 / GrimAge：在 LongPi 已有的信息之外，GrimAge2 每高 1 个标准差，死亡风险再高 {100 * (g2['hr_per_sd_resid'] - 1):.0f}%"
                "（美国国家健康调查 50 岁以上成人的长期随访）；其他甲基化时钟和器官年龄多分辨得很少，不计入") if g2 else "不计入"
    dv = res.get("data_value")
    cards = [
        {"title": "LongPi Age 是什么", "sub": "死亡风险等效年龄",
         "body": "把你此刻的死亡风险，换算成“同性别的中国人平均要到几岁才有这么高的风险”。"
                 "成年人的死亡风险大约每长 1 岁上升 10%，所以风险高 10%，大约就等于老了 1 岁。它说的是风险相当于几岁，不等于能活多久。",
         "rows": [["每长 1 岁风险上升", f"约 {100 * (2.718281828 ** res['gompertz_b'] - 1):.0f}%（联合国 2024 年中国生命表）"],
                  ["血液年龄怎么算进来", f"血液 PhenoAge 比同龄人每年轻 1 岁，约等于风险年轻 {res['longpi_age']['clock']['years_per_gap_year_central']} 岁（用美国 3.7 万人随访数据校准）"],
                  ["其他指标怎么算进来", "每项都用大规模研究汇总出的关系，再和同龄、同性别的中国人比"],
                  ["甲基化怎么算进来", meth_row],
                  ["没测的项目怎么办", "按同龄人的分布计入：不改变中间值，只让区间变宽。没有血液检测、没有 GrimAge2 时也一样"],
                  ["区间怎么来的", "把研究数据的不确定、设备误差和没测的项目都考虑进去，反复模拟 2000 次"]]},
        {"title": "120 指数是什么", "sub": "100 + 10 × log10（你活到 120 岁的概率 ÷ 同龄人的概率）",
         "body": "100 分 = 和同龄人一样；110 分 = 活到 120 岁的可能性是同龄人的 10 倍；90 分 = 十分之一。"
                 "到了极高龄，人和人之间的风险差别会变小（最脆弱的人已先离开），模型考虑了这一点，所以这个分数主要反映你和同龄人比的位置。",
         "rows": [[sc[k]["name"], f"{sc[k]['desc']}（权重 {w[k]}）"] for k in sc]},
    ]
    if dv:
        hw = lambda x: f"±{x / 2:.1f} 岁"
        cards.append({"title": "区间和数据完整度", "sub": "资料越全，区间越窄",
                      "body": "区间的意思：如果把补测清单里能测的都测了，算出来的 LongPi Age 有八成把握落在这个范围里（研究数据本身的不确定也算在内）。"
                              "没测的项目按同龄人的分布计入，所以资料越少区间越宽。数据完整度不是数项目个数，而是按信息量算："
                              "现在的区间比只知道年龄和性别时缩小了多少，占全部做完能缩小的比例。",
                      "rows": [["只知道年龄和性别", hw(dv["width_none"])], ["现在", hw(dv["width_now"])],
                               ["清单全部做完", hw(dv["width_all"])], ["数据完整度", f"{dv['completeness_pct']}%"]]})
    if val:
        cards.append({"title": "用公共数据检验过吗", "sub": "用美国国家健康调查（NHANES）5 万人、最长 20 年的随访数据检验",
                      "rows": [[k, v] for k, v in val.items()]})
    src = ev.get("sources", [])
    if src:
        cards.append({"title": "主要数据与文献", "sub": "完整清单见方法学白皮书", "body": "；".join(src)})
    return {"cards": cards}


SKILL_DIR = Path(__file__).resolve().parents[2]


def exercise_library() -> dict:
    return json.loads((SKILL_DIR / "data" / "exercise_library.json").read_text(encoding="utf-8"))


def _data_uri(f: Path) -> str:
    mt = mimetypes.guess_type(f.name)[0] or "image/jpeg"
    return f"data:{mt};base64," + base64.b64encode(f.read_bytes()).decode("ascii")


def inline_training_images(narrative: dict, base: Optional[Path]) -> dict:
    """Resolve exercises and embed their pictures as data URIs so the page stays one offline file.

    An exercise may be {"ref": "<library id>", ...overrides}: the entry from data/exercise_library.json is used,
    with the narrative's fields (usually just "dose") on top; library images come from the skill's assets.
    Other images are paths relative to narrative.json."""
    tr = narrative.get("training")
    if not tr:
        return narrative
    narrative = copy.deepcopy(narrative)
    lib = {e["id"]: e for e in exercise_library()["exercises"]}
    used_lib = False
    for sess in narrative["training"].get("sessions", []):
        for i, ex in enumerate(sess.get("exercises", [])):
            roots = [base] if base else []
            if ex.get("ref"):
                entry = lib.get(ex["ref"])
                if entry is None:
                    continue   # reported by schema.check_narrative
                merged = {k: v for k, v in entry.items() if k not in ("id", "source", "default_dose")}
                merged["dose"] = entry.get("default_dose", "")
                merged.update({k: v for k, v in ex.items() if k != "ref"})
                if "images" not in ex:
                    roots = [SKILL_DIR]
                sess["exercises"][i] = ex = merged
                used_lib = True
            imgs = []
            for src in ex.get("images", []):
                if str(src).startswith("data:"):
                    imgs.append(src)
                    continue
                f = next((r / src for r in roots + [SKILL_DIR] if r and (r / src).is_file()), None)
                if f is not None:
                    imgs.append(_data_uri(f))
            ex["images"] = imgs
    if used_lib and not narrative["training"].get("credit"):
        narrative["training"]["credit"] = exercise_library()["credit_zh"]
    return narrative


def render(res: dict, data: dict, narrative: dict, meta: dict, params: dict, evidence: Optional[dict], out: Path,
           base: Optional[Path] = None) -> Path:
    narrative = inline_training_images(narrative, base)
    head = (ASSETS / "report_head.html").read_text(encoding="utf-8")
    body = (ASSETS / "report_body.html").read_text(encoding="utf-8")
    title = meta.get("title") or "LongPi 报告"
    head = head.replace("<title>LongPi Demo</title>", f"<title>{html.escape(title)}</title>")
    payload = {"meta": meta, "res": res, "data": data, "narrative": narrative,
               "methods": methods_cards(res, params, evidence)}
    page = head + body.replace("__LONGPI_DATA__", _safe_json(payload))
    out.write_text(page, encoding="utf-8")
    return out
