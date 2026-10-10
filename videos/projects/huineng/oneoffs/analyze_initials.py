# -*- coding: utf-8 -*-
"""擦音声母频谱裁决：翘舌(sh/ch/zh) vs 平舌(s/c)。

whisper 两个模型对「韶关」「曹溪」转写不一，改看物理信号：
平舌擦音能量集中在 4kHz 以上，翘舌集中在 1.5–3.8kHz。
用片内已知正确读音的字做参照。用法: python oneoffs/analyze_initials.py
"""
import json
import wave

import numpy as np

WAV = "media/huineng-yeyang.wav"
RAW = "build/raw.json"

# (标签, 绝对起, 绝对止)；韶/曹的擦音段由词时间人工细取
TARGETS = [
    ("韶(sh?)", 336.115, 336.270),
    ("曹(c?)", 336.585, 336.685),
]

# 参照字：从 raw.json 按出现顺序取
REFS = [("神=sh", "神"), ("四=s", "四"), ("禅=ch", "禅"), ("此=c", "此"),
        ("三=s", "三"), ("山=sh", "山")]


def band_ratio(pcm, sr, t0, t1):
    """擦音段高频能量占比：Eh/(El+Eh)。平舌→大，翘舌→小。"""
    a, b = int(t0 * sr), int(t1 * sr)
    seg = pcm[a:b].astype(np.float64)
    seg *= np.hanning(len(seg))
    sp = np.abs(np.fft.rfft(seg))
    fr = np.fft.rfftfreq(len(seg), 1.0 / sr)
    el = sp[(fr >= 1500) & (fr <= 3800)].sum()
    eh = sp[(fr >= 4200) & (fr <= min(7500, sr / 2 - 100))].sum()
    return eh / (el + eh + 1e-9)


def find_word(raw, char, nth=0):
    count = 0
    for g in raw["segments"]:
        for w in g.get("words", []):
            if w["w"] == char:
                if count == nth:
                    return w["s"], w["e"]
                count += 1
    return None


wf = wave.open(WAV, "rb")
sr, ch = wf.getframerate(), wf.getnchannels()
pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
if ch > 1:
    pcm = pcm.reshape(-1, ch)[:, 0]
raw = json.load(open(RAW, encoding="utf-8"))

print("采样率 %d；Eh/(El+Eh)：平舌大、翘舌小" % sr)
for label, t0, t1 in TARGETS:
    print("  %-8s %.3f" % (label, band_ratio(pcm, sr, t0, t1)))
print("-- 参照 --")
for label, ch in REFS:
    span = find_word(raw, ch)
    if span:
        # 声母取词首 35%–60%（跳过声调过渡，取擦音主体）
        t0 = span[0] + (span[1] - span[0]) * 0.12
        t1 = span[0] + (span[1] - span[0]) * 0.55
        print("  %-7s %.3f   (%.2f-%.2f)" %
              (label, band_ratio(pcm, sr, t0, t1), t0, t1))
    else:
        print("  %-7s 未找到" % label)
