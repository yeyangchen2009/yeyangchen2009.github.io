# -*- coding: utf-8 -*-
"""中系门户 hook（门户＝#72，31 篇路线表唯一进度维护处）。"""
import re

PORTAL_ISSUE = 72

# | 中15 | 标题 | 状态 |
ROW_RE = re.compile(r"^(\| 中)(\d+)( \|.*\| )(.+?)( \|)\s*$")

NEXT = "⏳ 下一篇"
DONE_FMT = "[✅ #{n}](/post/{n}.html)"


def apply(body, series_index, issue_number):
    """返回 (新 body, 说明)。当前 ⏳ 行＝series_index 才能打勾；
    随后的 series_index+1 行若 💤 则转 ⏳。"""
    lines = body.split("\n")
    cur_row = None
    nxt_row = None
    for i, line in enumerate(lines):
        m = ROW_RE.match(line)
        if not m:
            continue
        idx = int(m.group(2))
        if idx == series_index:
            cur_row = i
        elif idx == series_index + 1:
            nxt_row = i

    if cur_row is None:
        raise ValueError("门户表里找不到中{:02d} 行".format(series_index))

    notes = []
    m = ROW_RE.match(lines[cur_row])
    if NEXT in m.group(4):
        lines[cur_row] = "".join(
            [m.group(1), str(series_index), m.group(3),
             DONE_FMT.format(n=issue_number), m.group(5)]
        )
        notes.append("中{:02d} 已勾选 #{}".format(series_index, issue_number))
    elif m.group(4).startswith("[✅"):
        notes.append("中{:02d} 本已勾选，跳过".format(series_index))
    else:
        raise ValueError("中{:02d} 行状态异常：{}".format(series_index, m.group(4)))

    if nxt_row is not None:
        m2 = ROW_RE.match(lines[nxt_row])
        if m2.group(4) == "💤":
            lines[nxt_row] = "".join(
                [m2.group(1), str(series_index + 1), m2.group(3), NEXT, m2.group(5)]
            )
            notes.append("中{:02d} 转为下一篇".format(series_index + 1))
        elif m2.group(4) == NEXT:
            notes.append("中{0:02d} 本就是下一篇，跳过".format(series_index + 1))
    else:
        notes.append("无中{:02d} 行（系列收官？），不转下一篇".format(series_index + 1))

    return "\n".join(lines), "；".join(notes)
