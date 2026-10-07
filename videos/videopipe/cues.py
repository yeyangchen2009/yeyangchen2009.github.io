# -*- coding: utf-8 -*-
"""组句 cue、单调修正、cues.json / SRT 读写。

cues.json 三键 {duration, chars, cues}：是"评审锁定版"对齐结果，
入库并支撑无音频重建；新对齐产物默认只进 build/，覆盖此文件须人工
copy + 评审。
"""
import json

from .align import HAN_RE


def group_cues(src_text, al, split):
    """按原稿标点（split 字符集）把逐字时间切成句 cue。"""
    src_text = src_text.strip()
    cues, cur, ki = [], [], 0
    for ch in src_text:
        if HAN_RE.match(ch):
            cur.append(ki)
            ki += 1
        elif ch in split:
            if cur:
                cues.append({
                    "s": round(al.ts[cur[0]], 2),
                    "e": round(al.te[cur[-1]], 2),
                    "t": "".join(al.chars[x] for x in cur)})
                cur = []
    if cur:
        cues.append({
            "s": round(al.ts[cur[0]], 2),
            "e": round(al.te[cur[-1]], 2),
            "t": "".join(al.chars[x] for x in cur)})
    return cues


def enforce_monotonic(cues, gap=0.02):
    """后句早于前句结束时，把后句起点顶到前句末 + gap（原地）。"""
    for i in range(1, len(cues)):
        if cues[i]["s"] < cues[i - 1]["e"]:
            cues[i]["s"] = round(cues[i - 1]["e"] + gap, 2)
    return cues


def build_cues_json(duration, al, cues) -> dict:
    return {
        "duration": duration,
        "chars": [{"c": al.chars[k], "s": round(al.ts[k], 3),
                   "e": round(al.te[k], 3)}
                  for k in range(len(al.chars))],
        "cues": cues,
    }


def save_cues(data: dict, path) -> None:
    with open(str(path), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def load_cues(path) -> dict:
    return json.load(open(str(path), encoding="utf-8"))


def _hms(t) -> str:
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return "%02d:%02d:%02d,%03d" % (h, m, int(s), round((s - int(s)) * 1000))


def to_srt(cues) -> str:
    return "\n".join(
        "%d\n%s --> %s\n%s\n" % (i, _hms(c["s"]), _hms(c["e"]), c["t"])
        for i, c in enumerate(cues, 1))


def write_srt(cues, path) -> None:
    with open(str(path), "w", encoding="utf-8") as f:
        f.write(to_srt(cues))
