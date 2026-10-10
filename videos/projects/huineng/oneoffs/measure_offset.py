# -*- coding: utf-8 -*-
"""每个 onset 配它前面最近的句首（唯一、不争抢），看全片偏移分布。

diff = onset（真实发声）- cue_s（字幕句首）；正=字幕早。
在 whisper 真实输入 build/16k.wav 上测 onset。
用法（在 videos/ 目录下）: python projects/huineng/oneoffs/measure_offset.py
"""
import json
import re
import statistics
import subprocess
import bisect
from pathlib import Path

P = Path(__file__).resolve().parents[1]
cue_s = [c["s"] for c in
         json.load(open(P / "cues/cues.json", encoding="utf-8"))["cues"]]

cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i",
       str(P / "build/16k.wav"),
       "-af", "silencedetect=n=-48dB:d=0.08", "-f", "null", "-"]
out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                     text=True).stdout
onsets = [float(m) for m in re.findall(r"silence_end: ([\d.]+)", out)]

rows = []
for o in onsets:
    j = bisect.bisect_right(cue_s, o) - 1   # 最大的 <= o
    if j >= 0 and o - cue_s[j] < 0.6:
        rows.append((cue_s[j], o, o - cue_s[j]))

d = sorted(r[2] for r in rows)
n = len(d)
print("配对 %d/%d" % (n, len(onsets)))
print("中位数 %+.1f ms   均值 %+.1f ms"
      % (1000 * statistics.median(d), 1000 * statistics.mean(d)))
print("min %+.1f  P25 %+.1f  P75 %+.1f  max %+.1f"
      % (1000 * d[0], 1000 * d[n // 4], 1000 * d[3 * n // 4], 1000 * d[-1]))
for cs, o, dd in rows:
    print("%7.2f  %7.2f  %+6.1f" % (cs, o, 1000 * dd))
