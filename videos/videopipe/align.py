# -*- coding: utf-8 -*-
"""ASR 词时间戳 → 正字稿对齐（Needleman-Wunsch，字形 + 拼音综合打分）。

逻辑逐字提取自 align-zsx.py：多字词时间均摊、NW 全局对齐、未命中字
在相邻命中字之间线性插值。只产逐字时间，不组句（组句在 cues.py）。
"""
import re
from dataclasses import dataclass

import numpy as np
from pypinyin import lazy_pinyin
from pypinyin.style import finals, initials

HAN_RE = re.compile(r"[一-鿿]")


@dataclass(frozen=True)
class Scores:
    glyph: int = 3           # 字形相同
    pinyin: int = 2          # 拼音全同（字形不同）
    initial_final: int = 2   # 声母韵母皆同
    final_only: int = 1      # 仅韵母同
    mismatch: int = -2
    gap: int = -1


@dataclass
class Alignment:
    chars: list          # 原稿汉字 A
    ts: list             # 每字起
    te: list             # 每字止
    amap: list           # 原稿字 i → ASR 字下标（-1 未命中）
    bchars: list         # ASR 汉字 B（报告用）
    match_rate: float


def _pair_score(a, b, ap, bp, sc: Scores) -> int:
    if a == b:
        return sc.glyph
    if ap == bp:
        return sc.pinyin
    try:
        ai, af = initials.to_initial(ap), finals.to_final(ap)
        bi, bf = initials.to_initial(bp), finals.to_final(bp)
        if ai == bi and af == bf:
            return sc.initial_final
        if af == bf and af:
            return sc.final_only
    except Exception:
        pass
    return sc.mismatch


def _unfold(tr):
    """从 Transcript 展开 ASR 汉字及其起/止（多字词均摊）。"""
    B, BS, BE = [], [], []
    for g in tr.segments:
        for wd in g.words:
            hs = HAN_RE.findall(wd.w)
            n = len(hs)
            for i, ch in enumerate(hs):
                B.append(ch)
                BS.append(wd.s + (wd.e - wd.s) * i / n)
                BE.append(wd.s + (wd.e - wd.s) * (i + 1) / n)
    return B, BS, BE


def align(src_text: str, tr, *, sc: Scores = Scores()) -> Alignment:
    src_text = src_text.strip()
    A = HAN_RE.findall(src_text)
    B, BS, BE = _unfold(tr)

    AP = lazy_pinyin("".join(A))
    BP = lazy_pinyin("".join(B))

    na, nb = len(A), len(B)
    M = np.zeros((na + 1, nb + 1), dtype=np.int32)
    for i in range(1, na + 1):
        M[i, 0] = i * sc.gap
    for j in range(1, nb + 1):
        M[0, j] = j * sc.gap
    for i in range(1, na + 1):
        ai, api = A[i - 1], AP[i - 1]
        row, prev = M[i], M[i - 1]
        for j in range(1, nb + 1):
            diag = prev[j - 1] + _pair_score(ai, B[j - 1],
                                             api, BP[j - 1], sc)
            row[j] = max(diag, prev[j] + sc.gap, row[j - 1] + sc.gap)

    amap = [-1] * na
    i, j = na, nb
    while i > 0 or j > 0:
        if (i > 0 and j > 0
                and M[i, j] == M[i - 1, j - 1]
                + _pair_score(A[i - 1], B[j - 1], AP[i - 1], BP[j - 1], sc)):
            amap[i - 1] = j - 1
            i -= 1
            j -= 1
        elif i > 0 and M[i, j] == M[i - 1, j] + sc.gap:
            i -= 1
        else:
            j -= 1

    ts, te = [None] * na, [None] * na
    for k, bj in enumerate(amap):
        if bj >= 0:
            ts[k], te[k] = BS[bj], BE[bj]
    for k in range(na):
        if ts[k] is None:
            lo = k - 1
            while lo >= 0 and ts[lo] is None:
                lo -= 1
            hi = k + 1
            while hi < na and ts[hi] is None:
                hi += 1
            if lo >= 0 and hi < na:
                ts[k] = (te[lo]
                         + (ts[hi] - te[lo]) * (k - lo) / (hi - lo))
                te[k] = ts[k] + 0.12
            elif lo >= 0:
                ts[k] = te[lo] + 0.05
                te[k] = ts[k] + 0.12
            else:
                ts[k] = max(0, ts[hi] - 0.2 * (hi - k))
                te[k] = ts[k] + 0.12

    matched = sum(1 for x in amap if x >= 0)
    rate = 100.0 * matched / na if na else 0.0
    return Alignment(A, ts, te, amap, B, rate)


def check_report(al: Alignment) -> str:
    """逐字核对行（写入 align-check.txt 供人工审）。"""
    lines = []
    for k, bj in enumerate(al.amap):
        if bj >= 0 and al.chars[k] == al.bchars[bj]:
            tag = "OK "
        elif bj >= 0:
            tag = "音 "
        else:
            tag = "GAP"
        shown = al.bchars[bj] if bj >= 0 else "·"
        lines.append("%s %s %s  %.2f-%.2f"
                     % (tag, al.chars[k], shown, al.ts[k], al.te[k]))
    return "\n".join(lines)
