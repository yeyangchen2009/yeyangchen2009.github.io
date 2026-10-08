# -*- coding: utf-8 -*-
"""组句 cue、单调修正、cues.json / SRT 读写。

cues.json 三键 {duration, chars, cues}：是"评审锁定版"对齐结果，
入库并支撑无音频重建；新对齐产物默认只进 build/，覆盖此文件须人工
copy + 评审。
"""
import json

from .align import HAN_RE, LAT_RE


def _group_han(src_text, al, split):
    """纯中文组句（原逻辑，逐字节锁定）。"""
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


def group_cues(src_text, al, split):
    """按原稿标点（split 字符集）把逐字时间切成句 cue。

    纯中文走 _group_han（与历史逐字节一致）；含拉丁片段（技术稿英文术语）
    时，拉丁串整体保留并取 al.latin 的对齐时间，句 t 完整含英文。
    """
    src_text = src_text.strip()
    if not LAT_RE.search(src_text):
        return _group_han(src_text, al, split)

    cues, cur, parts = [], [], []
    hk = lk = 0
    i, n = 0, len(src_text)

    def flush():
        if cur:
            cues.append({"s": round(cur[0][0], 2),
                         "e": round(cur[-1][1], 2),
                         "t": "".join(parts)})

    while i < n:
        ch = src_text[i]
        if HAN_RE.match(ch):
            cur.append((al.ts[hk], al.te[hk])); hk += 1
            parts.append(ch); i += 1
        elif LAT_RE.match(ch):
            m = LAT_RE.match(src_text, i)
            s, e = al.latin[lk]; lk += 1
            # 英文词前补排版空格（不进 cur/时间轴）：避免 Write HTML
            # 被无分隔符扫描粘连成 WriteHTML，也让中英之间留出可读间距。
            if parts and not parts[-1].endswith(" "):
                parts.append(" ")
            cur.append((s, e)); parts.append(m.group(0))
            i = m.end()
        elif ch in split:
            flush(); cur, parts = [], []; i += 1
        else:
            i += 1
    flush()
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
