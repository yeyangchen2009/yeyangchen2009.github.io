# -*- coding: utf-8 -*-
"""oneoff · 梁武帝全片 TTS 转录（词级，供多音字核对与后续 NW 对齐）。

media wav → ffmpeg 转 16k 单声道 → videopipe.whisper_asr（base/cpu/int8）。
产物：
  build/liangwudi-16k.wav        转码音频
  build/liangwudi-raw.json       词级原始转录（save_raw 格式）
  build/_transcript.txt          识别全文（目检多音字）
TTS 音频干净连续：不开 VAD、保留上文条件。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import (ProjectPaths, to_16k_mono, read_pcm16,
                       probe_duration, transcribe, save_raw)

P = ProjectPaths.at(Path(__file__).resolve().parents[1])
SRC = P.media_dir / "liangwudi-yeyang.wav"
WAV16 = P.build_dir / "liangwudi-16k.wav"
RAW = P.build_dir / "liangwudi-raw.json"
TXT = P.build_dir / "_transcript.txt"

to_16k_mono(SRC, WAV16)
dur = probe_duration(SRC)
pcm = read_pcm16(WAV16)
print("时长 %.2f 秒" % dur)

tr = transcribe(pcm, dur, model_size="base", beam_size=5,
                vad_filter=False, condition_on_previous_text=True)

save_raw(tr, RAW)

lines = []
for seg in tr.segments:
    print("SEG %.2f-%.2f %s" % (seg.s, seg.e, seg.t))
    lines.append(seg.t)
io.open(TXT, "w", encoding="utf-8").write("\n".join(lines))
print("词数", sum(len(g.words) for g in tr.segments))
print("report", RAW)
