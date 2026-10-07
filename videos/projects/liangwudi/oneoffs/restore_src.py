# -*- coding: utf-8 -*-
"""oneoff · 从 TTS 发音稿反向还原正字稿：4 处骗读替换。

音频实际念的是 TTS 稿，故正字稿以 TTS 稿为底，只把骗读字换回正字，
保证与口播逐字对应。产物写 build/，并与入库的 src/liangwudi-src.txt
逐字比对（不覆盖源文件）。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import ProjectPaths

P = ProjectPaths.at(Path(__file__).resolve().parents[1])

TTS = P.root / "src" / "liangwudi-tts.txt"
SRC = P.root / "src" / "liangwudi-src.txt"
OUT = P.build_dir / "liangwudi-src-restored.txt"

text = io.open(TTS, encoding="utf-8").read()

# 顺序无关、彼此不重叠；逐条替换并计数核对
repl = [
    ("祥将", "降将"),    # 降将 xiáng（侯景）
    ("楞茄经", "楞伽经"),  # 楞伽经 qié
    ("当拆", "当差"),    # 当差 dāng chāi
    ("设成", "当成"),    # 当成 dàng
]
for a, b in repl:
    n = text.count(a)
    if n != 1:
        raise SystemExit("替换项 %s 命中 %d 次，应为 1，请人工核对" % (a, n))
    text = text.replace(a, b)

io.open(OUT, "w", encoding="utf-8").write(text)
for kw in ["降将", "楞伽经", "当差", "当成"]:
    print("  [%s] %d 处" % (kw, text.count(kw)))

ok = io.open(SRC, encoding="utf-8").read() == text
print("RESULT", "PASS" if ok else "DIFF")
print("report", OUT)
if not ok:
    sys.exit(1)
