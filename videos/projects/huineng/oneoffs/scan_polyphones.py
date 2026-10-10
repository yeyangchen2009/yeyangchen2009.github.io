# -*- coding: utf-8 -*-
"""慧能片 · 多音字/非常用字扫描（TTS 前用）。

对正字稿每个汉字查 pypinyin：
- heteronym 返回多个读音  -> 多音字；
- 读音等于原字（pypinyin 不认识）-> 非常用字/生僻字；
输出按字汇总的读音清单与全部语境，供人工按语境定音。
用法: python oneoffs/scan_polyphones.py
"""
import io
import os
import sys

from pypinyin import pinyin, Style

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src", "huineng-src.txt")

text = io.open(SRC, encoding="utf-8").read()
han = [c for c in text if "一" <= c <= "鿿"]

info = {}  # 字 -> (读音set, [语境])
for i, c in enumerate(text):
    if not ("一" <= c <= "鿿"):
        continue
    readings = sorted(set(pinyin(c, heteronym=True, style=Style.NORMAL)[0]))
    rare = readings == [c]
    if len(readings) > 1 or rare:
        a, b = max(0, i - 6), min(len(text), i + 7)
        ctx = text[a:b].replace("\n", " ")
        info.setdefault(c, (readings if not rare else ["??生僻"], []))[1].append(ctx)

print("== 多音字（{} 个）==".format(sum(1 for v in info.values() if v[0][0] != "??生僻")))
for c, (readings, ctxs) in sorted(info.items(), key=lambda kv: -len(kv[1][1])):
    if readings[0] == "??生僻":
        continue
    print("\n【{}】读音: {}   出现 {} 次".format(c, "/".join(readings), len(ctxs)))
    for ctx in ctxs:
        print("   …{}…".format(ctx))

print("\n== 生僻字（pypinyin 不识别，{} 个）==".format(
    sum(1 for v in info.values() if v[0][0] == "??生僻")))
for c, (readings, ctxs) in sorted(info.items(), key=lambda kv: -len(kv[1][1])):
    if readings[0] != "??生僻":
        continue
    print("\n【{}】出现 {} 次".format(c, len(ctxs)))
    for ctx in ctxs:
        print("   …{}…".format(ctx))
