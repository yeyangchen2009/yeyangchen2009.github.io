# -*- coding: utf-8 -*-
"""慧能片 · 从 src 正字稿派生 tts 借音稿。

只做字形替换（见 oneoffs/huineng-pronunciation.md），语义与断句不变；
派生后自动逐字核对：两稿有差异的位置必须恰好等于「借字映射」，防止手滑改字。
用法: python oneoffs/make_tts.py
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src", "huineng-src.txt")
TTS = os.path.join(HERE, "..", "src", "huineng-tts.txt")

# 长串替换优先（大庾岭 中的 庾 不单独列）
REPLACES = [
    ("大庾岭", "大宇岭"),  # 庾 yǔ
    ("偈", "记"),          # 偈 jì，全稿 12 处
]

src = io.open(SRC, encoding="utf-8").read()
tts = src
for a, b in REPLACES:
    n = tts.count(a)
    tts = tts.replace(a, b)
    print("替换 {} -> {}：{} 处".format(a, b, n))

io.open(TTS, "w", encoding="utf-8", newline="\n").write(tts)

# 逐字核对：差异只允许出现在借字上
assert len(src) == len(tts), "两稿长度不一致，替换必须等长！"
bad = [(i, a, b) for i, (a, b) in enumerate(zip(src, tts)) if a != b]
allowed = {c for pair in REPLACES for s in pair for c in s}
wrong = [x for x in bad if x[1] not in allowed]
print("差异位置 {} 个，全部为借字映射: {}".format(len(bad), not wrong))
if wrong:
    for i, a, b in wrong[:10]:
        print("  异常差异 @{}: {} -> {}".format(i, a, b))
    raise SystemExit(1)
print("已写出:", TTS)
