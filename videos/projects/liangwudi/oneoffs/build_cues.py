# -*- coding: utf-8 -*-
"""oneoff · 梁武帝片 NW 对齐＋组句（产物只进 build/，不覆盖 cues/cues.json）。

以 src/liangwudi-src.txt（正字稿＝TTS 稿还原，restore PASS）对齐
build/liangwudi-raw.json 词级转录，按全标点切句、单调修正，输出：
  build/liangwudi-cues.json     {duration,chars,cues}
  build/liangwudi-cues.srt      评审用字幕
  build/align-check.txt         匹配率与未命中字
评审通过后人工 copy 为 cues/cues.json。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import (ProjectPaths, load_raw, align, check_report,
                       group_cues, enforce_monotonic, build_cues_json,
                       save_cues, to_srt)
from videopipe.config import SPLIT_FULL

P = ProjectPaths.at(Path(__file__).resolve().parents[1])
SRC_TXT = P.root / "src" / "liangwudi-src.txt"
RAW = P.build_dir / "liangwudi-raw.json"
OUT_JSON = P.build_dir / "liangwudi-cues.json"
OUT_SRT = P.build_dir / "liangwudi-cues.srt"
OUT_CHK = P.build_dir / "align-check.txt"

src_text = io.open(SRC_TXT, encoding="utf-8").read()
tr = load_raw(RAW)

al = align(src_text, tr)
report = check_report(al)
print(report)

cues = enforce_monotonic(group_cues(src_text, al, SPLIT_FULL))
data = build_cues_json(tr.duration, al, cues)
save_cues(data, OUT_JSON)
io.open(OUT_SRT, "w", encoding="utf-8").write(to_srt(cues))

buf = [report, "", "句数 %d，字數 %d" % (len(cues), len(al.chars)), ""]
for q in cues:
    buf.append("%.2f-%.2f  %s" % (q["s"], q["e"], q["t"]))
io.open(OUT_CHK, "w", encoding="utf-8").write("\n".join(buf))
print("句数", len(cues))
print("report", OUT_JSON)
