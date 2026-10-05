# -*- coding: utf-8 -*-
"""oneoff · 转录被漏识别的 9.4s 片段（全局起点 141.30s）。

从 media 主 wav 用 ffmpeg input seeking 切出 141.30–150.70 转 16k，
再经 videopipe 公共后端（whisper_asr）词级转录：独立片段无 condition
前文、开 VAD；时间戳加 141.30 偏移。词表写 build/zbj-gap-words.json，
并与历史产物 Temp/zbj-gap-words.json 逐字比对。
源自原 Temp/transcribe-gap.py。
"""
import io
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import ProjectPaths, read_pcm16, transcribe

P = ProjectPaths.at(Path(__file__).resolve().parents[1])
SRC = P.media_dir / "zbj-yeyang.wav"
GAP16 = P.build_dir / "zbj-gap-16k.wav"
OUT = P.build_dir / "zbj-gap-words.json"

OFFSET, GAP_LEN = 141.30, 9.4

# input seeking（-ss 在 -i 前）：与历史 _zbj-gap-16k.wav 字节一致
subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error",
     "-ss", str(OFFSET), "-t", str(GAP_LEN), "-i", str(SRC),
     "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(GAP16)],
    check=True)

pcm = read_pcm16(GAP16)
print("片段 %.1f 秒" % (len(pcm) / 16000))

tr = transcribe(pcm, GAP_LEN, model_size="base", beam_size=5,
                vad_filter=True, condition_on_previous_text=False,
                time_offset=OFFSET)

words = []
for seg in tr.segments:
    print("SEG %.2f-%.2f %s" % (seg.s, seg.e, seg.t))
    for w in seg.words:
        words.append({"w": w.w, "s": w.s, "e": w.e})

with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(words, f, ensure_ascii=False, indent=1)
print("词数", len(words))

hist_path = Path(__file__).resolve().parents[4] / "Temp" / "zbj-gap-words.json"
if hist_path.exists():
    hist = json.load(io.open(hist_path, encoding="utf-8"))
    ok = hist == words
    print("RESULT", "PASS" if ok else "DIFF")
    if not ok:
        print("hist", hist)
        sys.exit(1)
else:
    print("历史产物缺失，跳过比对")
print("report", OUT)
