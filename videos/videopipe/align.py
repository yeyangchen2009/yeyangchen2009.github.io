# -*- coding: utf-8 -*-
"""ASR 词时间戳 → 正字稿对齐（字形 + 拼音综合打分）。

2026-10 改：原实现把「汉字」(NW) 与「拉丁词」(align_latin) 拆成两条互不相通
的对齐，各取各的时间。但技术教程口播里蝉镜常把 src 的符号/数字念成中文：
「.」念「点」、「0」念「零」、「10」念「十」（whisper 常写成谐音「时」）。
这造成两类错位：
  · src 拉丁/标点变成 ASR 汉字，混进汉字 NW，把正字稿汉字挤错位；
  · align_latin 独立找拉丁词，时间与汉字时间轴脱节，一个拉丁片段可能被定位
    到其后汉字的更晚处，组句时句尾(拉丁)晚于下句首(汉字)，经单调修正后
    反而出现句内 s>e 倒挂（hf-02 实测 5 处）。

修法：src 与 ASR 都切成「汉字 / 拉丁串」混合 token 流，做一次统一 NW——
汉字↔汉字（字形/拼音）、拉丁↔拉丁（归一化）、拉丁数字↔中文数字（0↔零、
10↔十/时）。汉字配对与拉丁配对来自同一条对齐路径、共用同一时间轴，从根上
消除跨类型错位。命中汉字时间仍取 _unfold 均摊；命中拉丁取配对 ASR token 的
真实时间；未命中在相邻命中间线性插值。
"""
import difflib
import re
from dataclasses import dataclass, field

import numpy as np
from pypinyin import lazy_pinyin
from pypinyin.style import finals, initials

HAN_RE = re.compile(r"[一-鿿]")
# 连续拉丁字母 / 数字串：技术教程里的 HyperFrames、HTML、MP4、0.8 等
LAT_RE = re.compile(r"[A-Za-z0-9]+")
_TOKEN_RE = re.compile(r"[一-鿿]|[A-Za-z0-9]+")


@dataclass(frozen=True)
class Scores:
    glyph: int = 3           # 字形相同
    pinyin: int = 2          # 拼音全同（字形不同）
    initial_final: int = 2   # 声母韵母皆同
    final_only: int = 1      # 仅韵母同
    translit: int = 0        # 拉丁词 ↔ 汉字音译（json→省），仅靠顺序，弱配
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
    latin: list = field(default_factory=list)  # 每拉丁片段 (s,e)


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
    """从 Transcript 展开 ASR 汉字及其起/止（word 时长在词内汉字间均分）。"""
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


# 蝉镜念阿拉伯数字 → whisper 中文：单字数字（含 whisper 把「十」误写「时」）
_CN_NUM = {'零': '0', '〇': '0', '一': '1', '二': '2', '两': '2',
           '三': '3', '四': '4', '五': '5', '六': '6', '七': '7',
           '八': '8', '九': '9', '十': '10', '时': '10'}


def _lat_match(x: str, y: str) -> int:
    nx, ny = _latin_norm(x), _latin_norm(y)
    if not nx or not ny:
        return -2
    if nx == ny:
        return 3
    if nx in ny or ny in nx:
        return 2
    r = difflib.SequenceMatcher(None, nx, ny, autojunk=False).ratio()
    if r > .6:
        return 1
    # whisper 漏/吞音节（paused→post，ratio .4）：首字母同则仍认同词
    if r >= .4 and nx[0] == ny[0]:
        return 1
    return -2


def _number_hit(a_lat: str, b_han: str) -> bool:
    return a_lat.isdigit() and _CN_NUM.get(b_han) == a_lat


def _tok_score(a, b, AP, BP, sc: Scores) -> int:
    """混合 token 对打分。
    a=src [kind,text,序号]；b=asr [kind,text,s,e,汉字bidx(-1)]。"""
    ak, bk = a[0], b[0]
    if ak == 'h' and bk == 'h':
        return _pair_score(a[1], b[1], AP[a[2]], BP[b[4]], sc)
    if ak == 'l' and bk == 'l':
        return _lat_match(a[1], b[1])
    if ak == 'l' and bk == 'h':
        if _number_hit(a[1], b[1]):
            return sc.glyph
        return sc.translit   # 音译（json→省）：靠 NW 顺序，弱于真匹配
    return sc.mismatch


def _trust_lat(a, b) -> bool:
    """src 拉丁 token 与 b 的配对是否可信（可信才取其时间，否则插值）。"""
    if b[0] == 'l':
        return _lat_match(a[1], b[1]) >= 1
    if b[0] == 'h':
        # 调用处 a 必为拉丁 token：数字精确对应或普通词的汉字音译都取其时间
        return True
    return False


def align(src_text: str, tr, *, sc: Scores = Scores()) -> Alignment:
    src_text = src_text.strip()
    A = HAN_RE.findall(src_text)
    B, BS, BE = _unfold(tr)
    AP = lazy_pinyin("".join(A))
    BP = lazy_pinyin("".join(B))

    # src 混合 token：['h',t,汉字序号] / ['l',t,拉丁序号]
    ST, hk, lk = [], 0, 0
    for m in _TOKEN_RE.finditer(src_text):
        t = m.group(0)
        if HAN_RE.match(t):
            ST.append(['h', t, hk]); hk += 1
        else:
            ST.append(['l', t, lk]); lk += 1

    # asr 混合 token：['h',t,s,e,汉字bidx] / ['l',t,s,e,-1]
    AT, bidx = [], 0
    for g in tr.segments:
        for wd in g.words:
            n = len(wd.w)
            for m in _TOKEN_RE.finditer(wd.w):
                t = m.group(0)
                s = wd.s + (wd.e - wd.s) * m.start() / n
                e = wd.s + (wd.e - wd.s) * m.end() / n
                if HAN_RE.match(t):
                    AT.append(['h', t, s, e, bidx]); bidx += 1
                else:
                    AT.append(['l', t, s, e, -1])

    ns, nt = len(ST), len(AT)
    M = np.zeros((ns + 1, nt + 1), dtype=np.int32)
    for i in range(1, ns + 1):
        M[i, 0] = i * sc.gap
    for j in range(1, nt + 1):
        M[0, j] = j * sc.gap
    for i in range(1, ns + 1):
        a, row, prev = ST[i - 1], M[i], M[i - 1]
        for j in range(1, nt + 1):
            b = AT[j - 1]
            row[j] = max(prev[j - 1] + _tok_score(a, b, AP, BP, sc),
                         prev[j] + sc.gap, row[j - 1] + sc.gap)

    amap = [-1] * hk
    latin = [(None, None)] * lk
    i, j = ns, nt
    while i > 0 or j > 0:
        a = ST[i - 1] if i > 0 else None
        b = AT[j - 1] if j > 0 else None
        if (i > 0 and j > 0
                and M[i, j] == M[i - 1, j - 1]
                + _tok_score(a, b, AP, BP, sc)):
            if a[0] == 'h' and b[0] == 'h':
                amap[a[2]] = b[4]
            elif a[0] == 'l' and _trust_lat(a, b):
                latin[a[2]] = (b[2], b[3])
            i -= 1; j -= 1
        elif i > 0 and M[i, j] == M[i - 1, j] + sc.gap:
            i -= 1
        else:
            j -= 1

    # 汉字时间：命中取 _unfold，未命中在相邻命中汉字间线性插值
    ts, te = [None] * hk, [None] * hk
    for k, bj in enumerate(amap):
        if bj >= 0:
            ts[k], te[k] = BS[bj], BE[bj]
    for k in range(hk):
        if ts[k] is None:
            lo = k - 1
            while lo >= 0 and ts[lo] is None:
                lo -= 1
            hi = k + 1
            while hi < hk and ts[hi] is None:
                hi += 1
            if lo >= 0 and hi < hk:
                ts[k] = te[lo] + (ts[hi] - te[lo]) * (k - lo) / (hi - lo)
            elif lo >= 0:
                ts[k] = te[lo] + 0.05
            else:
                ts[k] = max(0, ts[hi] - 0.2 * (hi - k)) if hi < hk else 0.0
            te[k] = ts[k] + 0.12

    # 拉丁缺口在相邻命中片段间线性插值
    _fill_latin_gaps(latin)

    matched = sum(1 for x in amap if x >= 0)
    rate = 100.0 * matched / hk if hk else 0.0
    return Alignment(A, ts, te, amap, B, rate, latin=latin)


def _fill_latin_gaps(out) -> None:
    """未取到时间的拉丁片段 (None,None)，在相邻命中片段间线性插值（原地）。"""
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
            s = out[lo][1] + (out[hi][0] - out[lo][1]) * (k - lo) / (hi - lo)
        elif lo >= 0:
            s = out[lo][1] + 0.05
        else:
            s = max(0.0, out[hi][0] - 0.2) if hi < n else 0.0
        out[k] = (s, s + 0.12)


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
