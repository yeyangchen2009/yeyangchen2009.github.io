# -*- coding: utf-8 -*-
"""oneoff · 复核 v2 里「波惹」（般若）是否念 bo re，而非 ban ruo（班弱）。

转录改调 videopipe 公共后端（audioio / whisper_asr），不再裸跑
ffmpeg/wave/faster-whisper；详细报告写 build/，末行用 ASCII 给结论，
便于终端直接判定。源自原 Temp/transcribe-wang-v2.py。
"""
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import (ProjectPaths, to_16k_mono, read_pcm16,
                       probe_duration, transcribe)
try:
    from pypinyin import lazy_pinyin
    def py(s):
        return lazy_pinyin(s)
except Exception:
    def py(s):
        return []

P = ProjectPaths.at(Path(__file__).resolve().parents[1])
SRC = P.media_dir / "zhushixing-wang-yeyang-v2.wav"
A16 = P.build_dir / "zhushixing-wang-v2-16k.wav"
OUT = P.build_dir / "wang-v2-asr.txt"

to_16k_mono(SRC, A16)
pcm = read_pcm16(A16)
total = probe_duration(SRC)
tr = transcribe(pcm, total, model_size="base", beam_size=5)

lines = ["duration %.1f sec, %d segments" % (total, len(tr.segments)), ""]
for g in tr.segments:
    lines.append("[%.2f] %s" % (g.s, g.t))
lines.append("")
lines.append("=== windows [bo/ban][re/ruo/ru] and pinyin ===")

win_re = re.compile(r"[波般班][惹若弱]")
ok = 0
total_win = 0
for g in tr.segments:
    wins = win_re.findall(g.t)
    if not wins:
        continue
    lines.append("[%.2f] %s" % (g.s, g.t))
    for w in wins:
        total_win += 1
        p = py(w)
        good = (len(p) == 2 and p[0] == "bo" and p[1] == "re")
        ok += 1 if good else 0
        lines.append("    %s -> %s  %s"
                     % (w, " ".join(p), "BO_RE" if good else "CHECK"))

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

has_pinyin = bool(py("x"))
print("windows=%d bo_re=%d other=%d" % (total_win, ok, total_win - ok))
if not has_pinyin:
    verdict = "NO_PINYIN"
elif total_win and ok == total_win:
    verdict = "PASS"
else:
    verdict = "CHECK"
print("RESULT", verdict)
print("report", OUT)
