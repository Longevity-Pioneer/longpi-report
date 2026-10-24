#!/usr/bin/env python3
"""Build data/exercise_library.json and assets/exercises/*.jpg for the training module.

Usage: build_exercise_library.py <skill_dir> [<narrative.json with authored entries>]

Images: Free Exercise DB (github.com/yuhonas/free-exercise-db), The Unlicense (public domain).
Each movement has a start (_0) and end (_1) photo, resized to 460 px wide (macOS `sips`).
Chinese text was written for LongPi: the first 19 entries in a real-case session (2026-10-24),
the beginner / older-adult entries below by hand.
"""
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

SRC = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/{id}/{i}.jpg"
# name in the authored narrative -> (library id, Free Exercise DB id or None, category, equipment)
MAP = {
    "高脚杯深蹲": ("goblet_squat", "Goblet_Squat", "下肢", "哑铃或壶铃"),
    "上斜俯卧撑": ("incline_pushup", "Incline_Push-Up", "上肢推", "桌边或台阶"),
    "标准俯卧撑": ("pushup", "Pushups", "上肢推", "无"),
    "哑铃单臂划船": ("db_row", "One-Arm_Dumbbell_Row", "上肢拉", "哑铃、凳子"),
    "哑铃罗马尼亚硬拉": ("db_rdl", "Stiff-Legged_Dumbbell_Deadlift", "下肢", "哑铃"),
    "平板支撑": ("plank", "Plank", "核心", "垫子"),
    "哑铃分腿蹲": ("split_squat", "Split_Squat_with_Dumbbells", "下肢", "哑铃"),
    "哑铃站姿推举": ("db_press", "Standing_Dumbbell_Press", "上肢推", "哑铃"),
    "高位下拉": ("lat_pulldown", "Full_Range-Of-Motion_Lat_Pulldown", "上肢拉", "健身房器械"),
    "弹力带坐姿划船": ("band_row", "Seated_Cable_Rows", "上肢拉", "弹力带"),
    "臀桥": ("glute_bridge", "Butt_Lift_Bridge", "下肢", "垫子"),
    "侧平板": ("side_plank", "Side_Bridge", "核心", "垫子"),
    "死虫式": ("dead_bug", "Dead_Bug", "核心", "垫子"),
    "靠墙收颌": ("chin_tuck", None, "颈肩", "墙"),
    "颈部等长收缩": ("neck_isometric", "Isometric_Neck_Exercise_-_Front_And_Back", "颈肩", "无"),
    "弹力带拉开": ("band_pull_apart", "Band_Pull_Apart", "颈肩", "弹力带"),
    "俯身哑铃飞鸟": ("reverse_fly", "Reverse_Flyes", "颈肩", "轻哑铃"),
    "侧颈拉伸": ("side_neck_stretch", "Side_Neck_Stretch", "颈肩", "椅子"),
    "猫式伸展": ("cat_stretch", "Cat_Stretch", "柔韧", "垫子"),
}
CLEAN_NAME = {"标准俯卧撑（第 9 周起）": "标准俯卧撑", "高位下拉（器械）": "高位下拉", "弹力带坐姿划船（居家替代）": "弹力带坐姿划船",
              "死虫式（与侧平板交替）": "死虫式"}
FIX = {  # remove plan-specific wording so the entries fit anyone
    ("pushup", "alias"): "比上斜俯卧撑难；能做 3 组 × 10 次上斜俯卧撑后再换",
    ("incline_pushup", "harder"): "降低台面，最后改成地面标准俯卧撑",
    ("band_row", "alias"): "没有器械时代替高位下拉；图里是器械版，姿势一样",
    ("reverse_fly", "default_dose"): "2–3 组 × 12–15 次",
}
NEW = [
    {"id": "chair_squat", "source": "Chair_Squat", "category": "下肢", "equipment": "椅子", "level": "入门",
     "name": "椅子坐站", "alias": "从椅子上站起再坐下，是深蹲的入门版，老年人也适用", "target": "大腿前侧、臀部，起身能力",
     "default_dose": "3 组 × 8–12 次",
     "steps": ["坐在稳固、不带轮子的椅子前半部分，双脚与肩同宽踩实", "双臂交叉抱在胸前，身体稍前倾", "呼气，脚掌发力站直，臀部夹紧",
               "吸气，屁股向后慢慢坐回，轻碰椅面就再站起"],
     "cues": ["起身时不要用手撑膝盖或扶手", "坐下要慢（3 秒），不要“砸”回椅子"], "mistakes": ["膝盖内扣", "身体后仰坐下"],
     "easier": "用手扶着椅子扶手起身，或在椅面加一个垫子坐高一些", "harder": "不碰椅面（悬停 1 秒）再起，或手捧哑铃"},
    {"id": "bodyweight_squat", "source": "Bodyweight_Squat", "category": "下肢", "equipment": "无", "level": "入门",
     "name": "徒手深蹲", "alias": "不拿重量的深蹲", "target": "大腿前侧、臀部", "default_dose": "3 组 × 12–15 次",
     "steps": ["双脚略比肩宽，脚尖稍向外", "双臂向前平举保持平衡", "吸气，屁股向后向下坐，蹲到大腿与地面平行或尽量低", "呼气，全脚掌发力站起"],
     "cues": ["脚跟不离地", "膝盖朝着脚尖方向"], "mistakes": ["弯腰低头", "膝盖内扣"],
     "easier": "改做椅子坐站", "harder": "改做高脚杯深蹲"},
    {"id": "step_up", "source": "Dumbbell_Step_Ups", "category": "下肢", "equipment": "台阶或稳固的矮凳，可加哑铃", "level": "入门",
     "name": "上台阶", "alias": "一只脚踩上台阶，把身体推上去，再慢慢下来", "target": "大腿前侧、臀部、平衡",
     "default_dose": "每侧 3 组 × 8–10 次",
     "steps": ["面对一级台阶或 20–40 cm 高的稳固矮凳站好", "右脚整只脚踩上台阶", "右脚发力把身体推上去，左脚跟上站稳", "左脚先下，右脚再下；做完一侧换腿"],
     "cues": ["用上面那条腿发力，下面的脚不要蹬地借力", "下来时慢慢放"], "mistakes": ["膝盖内扣", "身体前倾太多"],
     "easier": "台阶低一些，或一只手扶墙", "harder": "双手拿哑铃，或台阶加高"},
    {"id": "calf_raise", "source": "Standing_Calf_Raises", "category": "下肢", "equipment": "墙或椅背（扶着）", "level": "入门",
     "name": "站姿提踵", "alias": "踮起脚尖再慢慢放下", "target": "小腿、踝关节稳定，减少跌倒", "default_dose": "3 组 × 15–20 次",
     "steps": ["双脚与髋同宽站直，一只手轻扶墙或椅背", "呼气，脚跟尽量抬高，用前脚掌站", "停 1 秒，吸气，慢慢放下"],
     "cues": ["抬到最高", "放下要慢（3 秒）"], "mistakes": ["身体前后晃", "只做半程"],
     "easier": "双手扶稳", "harder": "单脚做，或站在台阶边缘让脚跟低于台阶"},
    {"id": "farmers_walk", "source": "Farmers_Walk", "category": "全身", "equipment": "一对哑铃或两袋重物", "level": "入门",
     "name": "农夫行走", "alias": "两手各提一份重物，挺胸走路", "target": "握力、肩背、核心", "default_dose": "3 组 × 30–40 米（或 30 秒）",
     "steps": ["两手各提一只哑铃或一袋重物，垂在身体两侧", "挺胸、肩膀下沉，收紧腹部", "用正常步幅向前走，到距离后放下休息"],
     "cues": ["身体不左右歪", "握紧，不让重物晃"], "mistakes": ["耸肩", "弯腰驼背"],
     "easier": "减重，或缩短距离", "harder": "加重，或单手提（练核心抗侧弯）"},
]


def fetch(src_id: str, out_dir: Path) -> list:
    paths = []
    for i in (0, 1):
        dst = out_dir / f"{src_id}_{i}.jpg"
        if not dst.exists():
            urllib.request.urlretrieve(SRC.format(id=src_id, i=i), dst)
            subprocess.run(["sips", "-Z", "460", "-s", "formatOptions", "70", str(dst)], check=True, capture_output=True)
        paths.append(f"assets/exercises/{dst.name}")
    return paths


def main() -> int:
    skill = Path(sys.argv[1])
    img = skill / "assets" / "exercises"
    img.mkdir(parents=True, exist_ok=True)
    lib = []
    if len(sys.argv) > 2:
        n = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        for s in n["training"]["sessions"]:
            for e in s["exercises"]:
                name = CLEAN_NAME.get(e["name"], e["name"])
                lid, src, cat, eq = MAP[name]
                ent = {"id": lid, "source": src, "category": cat, "equipment": eq, "level": "基础", "name": name,
                       "alias": e.get("alias", ""), "target": e.get("target", ""), "default_dose": e.get("dose", ""),
                       "steps": e["steps"], "cues": e.get("cues", []), "mistakes": e.get("mistakes", []),
                       "easier": e.get("easier", ""), "harder": e.get("harder", "")}
                for (fid, key), val in FIX.items():
                    if fid == lid:
                        ent[key] = val
                lib.append(ent)
    else:
        lib = json.loads((skill / "data" / "exercise_library.json").read_text(encoding="utf-8"))["exercises"]
        lib = [e for e in lib if e["id"] not in {x["id"] for x in NEW}]
    lib += NEW
    for e in lib:
        e["images"] = fetch(e["source"], img) if e["source"] else []
    out = {"source": "Free Exercise DB (github.com/yuhonas/free-exercise-db), The Unlicense; Chinese text written for LongPi",
           "credit_zh": "动作照片来自开源动作数据集 Free Exercise DB（github.com/yuhonas/free-exercise-db，公共领域授权）。照片里的器械可以用哑铃、弹力带代替，姿势相同。",
           "exercises": lib}
    (skill / "data" / "exercise_library.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(lib), "exercises;", sum(len(e["images"]) for e in lib), "images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
