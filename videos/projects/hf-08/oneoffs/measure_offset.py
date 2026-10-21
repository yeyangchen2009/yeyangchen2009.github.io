# -*- coding: utf-8 -*-
"""hf-06 time_offset 实测（沿 hf-01/02/03/04 同法）。

每个 onset 配它前面最近的句首（唯一、不争抢），看全片偏移分布。
diff = onset（真实发声）- cue_s（字幕句首）；正=字幕早。
在 whisper 真实输入 build/16k.wav 上测 onset。
前五集实测：hf-01 +0.28 / hf-02 +0.37 / hf-03 +0.29 / hf-04 +0.30 / hf-05 +0.29。
hf-06 v3 母带（491.835s／288 句 cues）实测配对 43/55，中位数 +310.1ms
（均值 +319.3，P25 +282/P75 +350），取 0.31 回填 make_video.py。
（v2 母带曾测 +293.1ms 取 0.29，母带重合成后作废。）

hf-07 母带（440.17s／215 句 cues，2026-10-19）配对 29/50，分布双峰：
中位 +265 / P25 +60 / P75 +320。RMS 包络＋raw 词级戳裁决——
* 软起团 16 句（m/w/sh/zh 等鼻擦声母长起势，如「命/问题/上集」）：
  cue 处已有气息能量、韵腹（响度突增）在 cue+.25~+.44，silencedetect
  标在此处，中位约 +310——与前六片 0.28~0.31 同一物理量（字幕感知
  锚点＝韵腹，hf-04 F2 教训）；
* 硬起团 13 句（塞音/零声母干脆起句，如「蓝方块/有了/无限/行动件」）：
  cue 处静音、声母与韵腹都在 cue+.05~+.10。
whisper 两团都没戳错，差异在 TTS 起声方式；连读句（186/215 无 ≥80ms
停）不可单点测。决策取 **time_offset=0.29**（系列主值；软起句准、
硬起句字幕晚韵腹约 0.2s，在 lag 容忍内；F2 逐句目验兜底）。

★ 2026-10-20 换主角：v2 母带（559.22s／273 句，11 段蝉镜重合成＋11 段
旧母带谷点切窗重排，见 rebuild_audio.py）重测：配对 53/69，中位
+315.1ms／均值 +326.7／P25 +262.1／P75 +400.0／min +50／max +560。
分布回到单峰（段级重排后句首多在 0.34s 段间停顿之后，软起为主），
make_video.py 回填 **time_offset=0.31**（同 hf-06，贴中位）。

hf-08 母带（611.51s／274 句，20 段蝉镜段级取音首录，2026-10-21）配对
64/81，中位 **+291.5ms**／均值 +300.8／P25 +253.6／P75 +365.0／
min +35／max +510，单峰；make_video.py 取 **time_offset=0.29**（系列
主值，贴中位）。
"""
import bisect
import json
import re
import statistics
import subprocess
from pathlib import Path

P = Path(__file__).resolve().parent.parent
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
    j = bisect.bisect_right(cue_s, o) - 1
    if j >= 0 and o - cue_s[j] < 0.6:
        rows.append((cue_s[j], o, o - cue_s[j]))

d = sorted(r[2] for r in rows)
n = len(d)
print("配对 %d/%d" % (n, len(onsets)))
print("中位数 %+.1f ms   均值 %+.1f ms"
      % (1000 * statistics.median(d), 1000 * statistics.mean(d)))
print("min %+.1f  P25 %+.1f  P75 %+.1f  max %+.1f"
      % (1000 * d[0], 1000 * d[n // 4], 1000 * d[3 * n // 4], 1000 * d[-1]))
