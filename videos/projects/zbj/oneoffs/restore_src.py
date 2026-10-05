# -*- coding: utf-8 -*-
"""oneoff · 从 TTS 发音稿反向还原正字稿：5 处骗读替换。

音频实际念的是 TTS 稿，故正字稿以 TTS 稿为底，只把骗读字换回正字，
保证与口播逐字对应；md 定稿「跟开是一个道理」系漏字，不采用。
产物写 build/，并与入库的 src/zbj-src.txt 逐字比对（不覆盖源文件）。
源自原 Temp/gen-zbj-src.py。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import ProjectPaths

P = ProjectPaths.at(Path(__file__).resolve().parents[1])

TTS = P.root / "src" / "zbj-tts.txt"
SRC = P.root / "src" / "zbj-src.txt"
OUT = P.build_dir / "zbj-src-restored.txt"

text = io.open(TTS, encoding="utf-8").read()

# 顺序无关、彼此不重叠；逐条替换并计数核对
repl = [
    ("可就少了", "得少掉"),    # 取经路上得少掉一半
    ("必须诚实", "得诚实"),    # 我得诚实
    ("于田", "于阗"),          # 去于阗
    ("猪将军", "猪将"),        # 密教里的猪将（御车将军不含“猪将军”，安全）
    ("反倒像", "倒像"),        # 听着倒像
]
for a, b in repl:
    n = text.count(a)
    if n != 1:
        raise SystemExit("替换项 %s 命中 %d 次，应为 1，请人工核对" % (a, n))
    text = text.replace(a, b)

io.open(OUT, "w", encoding="utf-8").write(text)
for kw in ["得少掉", "得诚实", "于阗", "密教里的猪将", "听着倒像", "开源项目"]:
    print("  [%s] %d 处" % (kw, text.count(kw)))

ok = io.open(SRC, encoding="utf-8").read() == text
print("RESULT", "PASS" if ok else "DIFF")
print("report", OUT)
if not ok:
    sys.exit(1)
