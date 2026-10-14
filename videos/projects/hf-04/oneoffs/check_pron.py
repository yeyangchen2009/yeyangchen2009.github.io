# -*- coding: utf-8 -*-
"""hf-04 母带声学判音（whisper base 判不了的，用共振峰/VOT/摩擦段判）。

四类疑点，全部在母带阶段拦下，避免 hf-03 那样成片后做外科补丁：
  A. 行 háng（借「航」3 处）vs xíng（基准 2 处）：韵腹 F1/F2 两簇应相隔 1700Hz
  B. tick（6 处，whisper 全转 check）vs 真 check（守门员段 1 处基准）：
     t 是塞音、tʃ 有长摩擦段——词首 160ms 高频(3–8kHz)能量占比分两簇
  C. 得 děi（4 处）vs 轻声 de（基准 3 处）：韵腹时长＋F2（ěi 走高滑韵）
  D. 涨 zhǎng（借 2 处，目标 zhǎng）vs ch 送气基准「差」：声母 VOT
另打印 seekable(cable)、灵魂在 seek、GSAP/Chrome/薛/paused 等待人耳点的时间戳。

方法同 hf-03 patch 判据：20ms Hann＋预加重 0.97 rfft；F1/F2 取韵腹中段谱峰。
"""
import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RAW = json.loads((ROOT / "build" / "raw.json").read_text(encoding="utf-8"))
SEGS = RAW["segments"]

w = wave.open(str(ROOT / "media" / "hf-04-yeyang.wav"), "rb")
SR = w.getframerate()
PCM = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
w.close()

WIN, HOP, PRE = 0.02, 0.01, 0.97


def all_words():
    for si, s in enumerate(SEGS):
        for wo in s["words"]:
            yield si, wo


def find_words(pred):
    """pred(word_text, seg_text) -> [(t, seg_text, word_dict)]"""
    out = []
    for si, s in enumerate(SEGS):
        for wo in s["words"]:
            if pred(wo["w"], s["t"]):
                out.append((si, s["t"], wo))
    return out


def ctx(si, span=2):
    a, b = max(0, si - span), min(len(SEGS), si + span + 1)
    return "／".join(SEGS[i]["t"] for i in range(a, b))[:46]


def spec_frame(seg_pcm):
    n = len(seg_pcm)
    x = np.append(seg_pcm[0], seg_pcm[1:] - PRE * seg_pcm[:-1])
    x = x * np.hanning(n)
    sp = np.abs(np.fft.rfft(x, n=512)) ** 2
    freqs = np.fft.rfftfreq(512, 1 / SR)
    return freqs, sp


def formants(t0, t1, n_mid=0.34):
    """取字韵腹中段：能量最大的连续元音区，返回 F1/F2 中位数与韵腹秒长。"""
    a, b = int(t0 * SR), int(t1 * SR)
    x = PCM[a:b]
    if len(x) < int(0.05 * SR):
        return None
    fr = int(WIN * SR)
    hop = int(HOP * SR)
    rows, energy = [], []
    for i in range(0, len(x) - fr, hop):
        f, sp = spec_frame(x[i:i + fr])
        e = float(np.sum(sp[(f >= 0.08) & (f <= 5)]))
        rows.append((f, sp))
        energy.append(e)
    energy = np.array(energy)
    if len(energy) < 3:
        return None
    # 韵腹＝能量超过该字 55% 峰值的帧中最长一段（粗取中段比例）
    hi = np.where(energy > 0.55 * energy.max())[0]
    if len(hi) == 0:
        hi = np.argsort(energy)[-max(2, len(energy) // 3):]
    vowel_frames = [rows[i] for i in hi]
    m0 = int(len(vowel_frames) * (0.5 - n_mid / 2))
    m1 = int(len(vowel_frames) * (0.5 + n_mid / 2))
    sel = vowel_frames[m0:m1] or vowel_frames[len(vowel_frames) // 2:][:1]
    f1s, f2s = [], []
    for f, sp in sel:
        m1b = (f >= 250) & (f <= 1100)
        m2b = (f >= 900) & (f <= 3000)
        if sp[m1b].max() > 0:
            f1s.append(f[m1b][np.argmax(sp[m1b])])
        if sp[m2b].max() > 0:
            f2s.append(f[m2b][np.argmax(sp[m2b])])
    dur_v = (hi[-1] - hi[0] + 1) * HOP
    return (round(float(np.median(f1s))) if f1s else -1,
            round(float(np.median(f2s))) if f2s else -1,
            round(dur_v, 2))


def fric_ratio(t0, t1=0.17):
    """词首 0.17s 内 3–8kHz 能量占比；check(tʃ) 高，tick(t) 低。"""
    a = int(t0 * SR)
    x = PCM[a:a + int(t1 * SR)]
    fr = int(WIN * SR)
    hop = int(HOP * SR)
    ratios = []
    for i in range(0, len(x) - fr, hop):
        f, sp = spec_frame(x[i:i + fr])
        hi = np.sum(sp[(f >= 3000) & (f <= 8000)])
        lo = np.sum(sp[(f >= 100) & (f <= 3000)])
        ratios.append(hi / (lo + 1e-9))
    return np.round(np.array(ratios), 2).tolist()


def word_vowel(t0, t1):
    """词内最响元音帧的 F1/F2——tick 的 ɪ(F1≈400/F2≈2200) vs
    check 的 e(F1≈650/F2≈1800)；同时返回词长与首/尾半段高比分。"""
    a, b = int(t0 * SR), int(t1 * SR)
    x = PCM[a:b]
    fr, hop = int(WIN * SR), int(HOP * SR)
    best = None
    rows = []
    for i in range(0, len(x) - fr, hop):
        seg = x[i:i + fr]
        f, sp = spec_frame(seg)
        rms = float(np.sqrt(np.mean(seg ** 2)))
        hi = np.sum(sp[(f >= 3000) & (f <= 8000)])
        lo = np.sum(sp[(f >= 100) & (f <= 3000)])
        ratio = hi / (lo + 1e-9)
        rows.append((rms, ratio, f, sp))
    # 元音：高 RMS、低高比，取最响的一帧
    vow = [r for r in rows if r[1] < 0.6 and r[0] > 0.02]
    if vow:
        _, _, f, sp = max(vow, key=lambda r: r[0])
        m1 = (f >= 250) & (f <= 1100)
        m2 = (f >= 1200) & (f <= 3000)
        f1 = f[m1][np.argmax(sp[m1])]
        f2 = f[m2][np.argmax(sp[m2])]
    else:
        f1 = f2 = -1
    ratios = [r[1] for r in rows]
    n = len(ratios)
    head = float(np.mean(ratios[:max(1, n // 3)]))
    tail = float(np.mean(ratios[-max(1, n // 3):]))
    return round(float(f1)), round(float(f2)), round(t1 - t0, 2), round(head, 2), round(tail, 2)


def vot(t0, t1, limit=0.16):
    """字起点到首个周期浊音帧的距离（秒）：ch 送气长（0.08–0.14s 无 F0），
    zh 不送气短（~0.02s）。用自相关峰强度判周期性，RMS 判有声。"""
    a, b = int(t0 * SR), int(min(t1, t0 + limit) * SR)
    x = PCM[a:b]
    fr = int(WIN * SR)
    hop = int(HOP * SR)
    for i in range(0, len(x) - fr, hop):
        seg = x[i:i + fr] * np.hanning(fr)
        rms = float(np.sqrt(np.mean(seg ** 2)))
        if rms < 0.02:
            continue
        ac = np.correlate(seg, seg, "full")[fr - 1:]
        ac /= ac[0] + 1e-9
        lo, hi2 = int(SR / 400), int(SR / 70)  # F0 70–400Hz
        peak = float(ac[lo:hi2].max()) if hi2 < len(ac) else 0
        if peak > 0.45:
            return round(i / SR, 3)
    return None


print("=" * 78)
print("A. 行 háng 候选（应高 F1/低 F2 簇）vs xíng 基准（F2>2300）")
print("=" * 78)
targets = [
    ("这航", lambda wt, st: wt in ("行", "航") and ("这行是" in st.replace(" ", "") or "这航是" in st or "渲染main" in st.lower())),
    ("一航", lambda wt, st: wt in ("行", "航", "意行") and "tl" in st.lower()),
    ("三航", lambda wt, st: wt in ("行", "航") and ("三行" in st or "三航" in st or "凑齐" in st)),
    ("xíng基准:动画行", lambda wt, st: wt in ("行", "型") and "css动画" in st.lower().replace(" ", "")),
    ("xíng基准:并行", lambda wt, st: wt in ("型", "行") and ("无头" in st or "cron" in st.lower())),
]
for name, pred in targets:
    hits = find_words(pred)
    for si, st, wo in hits[:2]:
        fm = formants(wo["s"], wo["e"])
        print("  %-14s %6.2fs F1=%-5s F2=%-5s 韵腹=%ss | %s"
              % (name, wo["s"], fm[0], fm[1], fm[2], ctx(si, 1)))

print()
print("=" * 78)
print("B. tick 候选 vs 真 check 基准（每帧高频比，>0.25 持续为 tʃ 摩擦特征）")
print("=" * 78)
tick_hits = find_words(lambda wt, st: wt.lower() in ("check", "tick") and ("tick" in st.lower() or "check" in st.lower()))
for si, st, wo in tick_hits:
    is_real_check = "绿的" in st or "连check" in st.lower().replace(" ", "")
    is_check_mention = "门控" in st
    tag = "真check基准" if is_real_check else ("check门控  " if is_check_mention else "tick候选 ")
    f1, f2, dur, head, tail = word_vowel(wo["s"], wo["e"])
    print("  %s %6.2fs 词长=%ss 元音F1=%-5s F2=%-5s 首段高比=%-6s 尾段高比=%-6s | %s"
          % (tag, wo["s"], dur, f1, f2, head, tail, ctx(si, 1)))

print()
print("=" * 78)
print("C. 得 děi 候选（韵腹长＋F2 滑高）vs 轻声 de 基准")
print("=" * 78)
dei_hits = find_words(lambda wt, st: wt == "得")
for si, st, wo in dei_hits:
    fm = formants(wo["s"], wo["e"])
    print("  %6.2fs F1=%-5s F2=%-5s 韵腹=%ss | %s" % (wo["s"], fm[0], fm[1], fm[2], ctx(si, 1)))

print()
print("=" * 78)
print("D. 涨 zhǎng 候选（VOT 应短）vs ch 送气基准「差」（VOT 应长）")
print("=" * 78)
zhang = find_words(lambda wt, st: wt == "长")
for si, st, wo in zhang:
    print("  长(涨候选) %6.2fs VOT=%s | %s" % (wo["s"], vot(wo["s"], wo["e"]), ctx(si, 1)))
cha = find_words(lambda wt, st: wt in ("差",) and ("像素" in st or "只差" in st))
for si, st, wo in cha:
    print("  差(ch基准) %6.2fs VOT=%s | %s" % (wo["s"], vot(wo["s"], wo["e"]), ctx(si, 1)))

print()
print("=" * 78)
print("E. 待人耳核对点时间戳（切片用）")
print("=" * 78)
ear = [
    ("seekable首现", lambda wt, st: "cable" in wt.lower() or "seekable" in wt.lower()),
    ("灵魂在seek", lambda wt, st: "sick" in wt.lower() and "灵魂" in st.replace(" ", "")),
    ("GSAP", lambda wt, st: any(k in wt.lower() for k in ("gsap", "zip", "zapp", "赛不"))),
    ("Chrome", lambda wt, st: ("cron" in wt.lower() or "chrome" in wt.lower()
                               or ("窗户" in wt and "无头" in st.replace(" ", "")))),
    ("薛定谔", lambda wt, st: "薛" in wt or ("确定饿" in st.replace(" ", ""))),
    ("paused=true", lambda wt, st: any(k in wt.lower() for k in ("paused", "post", "poss", "true", "处")) and "暂停" not in wt and ("poss" in wt.lower() or "post" in wt.lower() or "true" in wt.lower() or wt == "处")),
    ("power2.out", lambda wt, st: "power" in wt.lower() or "2.0" in wt),
    ("WAAPI", lambda wt, st: "wap" in wt.lower()),
    ("Lottie", lambda wt, st: wt.lower().startswith("lot")),
    ("fromTo", lambda wt, st: "from" in wt.lower()),
]
seen = set()
for name, pred in ear:
    n = 0
    for si, st, wo in find_words(pred):
        key = (name, round(wo["s"], 1))
        if key in seen:
            continue
        seen.add(key)
        print("  %-12s %6.2f–%6.2fs 「%s」| %s" % (name, wo["s"], wo["e"], wo["w"], ctx(si, 0)))
        n += 1
        if n >= 7:
            break
