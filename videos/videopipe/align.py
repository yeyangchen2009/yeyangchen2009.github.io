# -*- coding: utf-8 -*-
"""ASR 词时间戳 → 正字稿对齐（Needleman-Wunsch，字形 + 拼音综合打分）。

逻辑逐字提取自 align-zsx.py：多字词时间均摊、NW 全局对齐、未命中字
在相邻命中字之间线性插值。只产逐字时间，不组句（组句在 cues.py）。
"""
import bisect
import difflib
import re
from dataclasses import dataclass, field

import numpy as np
from pypinyin import lazy_pinyin
from pypinyin.style import finals, initials

HAN_RE = re.compile(r"[一-鿿]")
# 连续拉丁字母 / 数字串：技术教程里的 HyperFrames、HTML、MP4、0.8 等
LAT_RE = re.compile(r"[A-Za-z0-9]+")


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
    latin: list = field(default_factory=list)  # 每拉丁片段 (s,e)，见 align_latin


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


def _latin_norm(s: str) -> str:
    return "".join(c.lower() for c in s if c.isalnum())


def _fill_latin_gaps(out) -> None:
    """没对上的拉丁片段 (None,None)，在相邻命中片段间线性插值（原地）。"""
    n = len(out)
    for k in range(n):
        if out[k][0] is not None:
            continue
        lo = k - 1
        while lo >= 0 and out[lo][0] is None:
            lo -= 1
        hi = k + 1
        while hi < n and out[hi][0] is None:
            hi += 1
        if lo >= 0 and hi < n:
            s = (out[lo][1]
                 + (out[hi][0] - out[lo][1]) * (k - lo) / (hi - lo))
        elif lo >= 0:
            s = out[lo][1] + 0.05
        else:
            s = max(0.0, out[hi][0] - 0.2) if hi < n else 0.0
        out[k] = (s, s + 0.12)


def align_latin(src_text: str, tr):
    """src 拉丁片段 ↔ ASR 拉丁词 顺序对齐，返回每片段 (s,e)。

    纯中文（无拉丁）返回 []，不进主流程。ASR 在 language=zh 下常把一个
    英文词拆成多个子词（HyperFrames→Hy/per/Fr/ames），故按归一化字符
    序列做 SequenceMatcher 对齐，再回映到 ASR 词的时间区间。
    """
    src_segs = LAT_RE.findall(src_text)
    if not src_segs:
        return []
    aw = [wd for g in tr.segments for wd in g.words
          if LAT_RE.search(wd.w)]
    if not aw:
        return [(None, None)] * len(src_segs)

    S = [_latin_norm(x) for x in src_segs]
    T = [_latin_norm(wd.w) for wd in aw]
    Sj, Tj = "".join(S), "".join(T)

    # src 归一化字符 → asr 归一化字符
    mp = [-1] * len(Sj)
    sm = difflib.SequenceMatcher(None, Sj, Tj, autojunk=False)
    for i1, i2, nn in sm.get_matching_blocks():
        for k in range(nn):
            mp[i1 + k] = i2 + k

    tail = np.cumsum([len(x) for x in T])   # 每个 ASR 词结尾(exclusive)

    def word_at(pos):
        return int(min(bisect.bisect_right(tail, pos), len(aw) - 1))

    sb = np.cumsum([0] + [len(x) for x in S])
    out = []
    for k in range(len(src_segs)):
        a, b = int(sb[k]), int(sb[k + 1])
        words = {word_at(mp[p]) for p in range(a, b) if mp[p] >= 0}
        if words:
            lo, hi = min(words), max(words)
            out.append((aw[lo].s, aw[hi].e))
        else:
            out.append((None, None))
    _fill_latin_gaps(out)
    return out


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
    latin = align_latin(src_text, tr)
    return Alignment(A, ts, te, amap, B, rate, latin=latin)


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
