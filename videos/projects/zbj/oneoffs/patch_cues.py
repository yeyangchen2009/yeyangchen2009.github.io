# -*- coding: utf-8 -*-
"""oneoff · 39 字漏识别区间修补：用片段词级时间戳替换，再按标点重建 cue。

whisper 整段漏识别（时间戳被「儿」吞掉），字形不动——chars 字形仍取
正字稿（…印度原典…严丝合缝…），只替换时间戳；随后按正字稿标点经
公共 group_cues / enforce_monotonic 重建全部 cue。产物写 build/，
与入库 cues/cues.json 完全比对，不覆盖锁定文件。
源自原 Temp/patch-cues.py。
"""
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import (ProjectPaths, load_cues, Alignment, HAN_RE,
                       group_cues, enforce_monotonic, build_cues_json,
                       save_cues, write_srt)
try:
    from pypinyin import lazy_pinyin
except Exception:
    lazy_pinyin = None

P = ProjectPaths.at(Path(__file__).resolve().parents[1])
SRC = P.src_dir / "zbj-src.txt"
GAPW = P.build_dir / "zbj-gap-words.json"
OUT_JSON = P.build_dir / "zbj-cues-patched.json"
OUT_SRT = P.build_dir / "zbj-cues.srt"
SPLIT = "，。：？！"

src_text = io.open(SRC, encoding="utf-8").read().strip()
A = HAN_RE.findall(src_text)

data = load_cues(P.cues_json)
chars = data["chars"]
assert len(chars) == len(A)
for k in range(len(A)):
    assert chars[k]["c"] == A[k], (k, chars[k]["c"], A[k])

# 在正字稿中定位被吞区间
target = "替这位菩萨管车驾车的本身就是一头猪这个设定跟印度原典严丝合缝后来学界也有人考证"
big = "".join(A)
st = big.find(target)
assert st >= 0 and big.find(target, st + 1) < 0, "区间未唯一定位"
ed = st + len(target)
print("被吞区间：正字索引 %d..%d（%d 字），前一字 %r"
      % (st, ed - 1, ed - st, A[st - 1]))
assert A[st - 1] == "儿"

# 展开片段词级时间戳为逐字（多字词在区间内均摊）
gap = json.load(io.open(GAPW, encoding="utf-8"))
exp = []
for wd in gap:
    hz = HAN_RE.findall(wd["w"])
    n = len(hz)
    for i, ch in enumerate(hz):
        s = wd["s"] + (wd["e"] - wd["s"]) * i / n
        e = wd["s"] + (wd["e"] - wd["s"]) * (i + 1) / n
        exp.append((ch, round(s, 3), round(e, 3)))
assert len(exp) == ed - st, (len(exp), ed - st)

# 拼音宽松校验展开序列与正字区间对应（允许 ASR 同音误写：典→点、合→核）
assert lazy_pinyin, "缺少 pypinyin"
AP = lazy_pinyin(target)
EP = lazy_pinyin("".join(x[0] for x in exp))
mism = [(i, target[i], exp[i][0]) for i in range(len(exp)) if AP[i] != EP[i]]
assert not mism, ("拼音不匹配", mism)

# 前一字「儿」收口到区间起点（原为 141.30–150.68 错误长区间）
chars[st - 1]["e"] = round(exp[0][1], 3)
# 替换 39 字时间戳
for i, (ch, s, e) in enumerate(exp):
    chars[st + i]["s"] = s
    chars[st + i]["e"] = e
print("已替换时间戳；区间 %.2f–%.2f，前字「儿」e=%.2f"
      % (exp[0][1], exp[-1][2], chars[st - 1]["e"]))

# 按正字稿标点重建 cue（公共函数）
al = Alignment(chars=A,
               ts=[chars[k]["s"] for k in range(len(A))],
               te=[chars[k]["e"] for k in range(len(A))],
               amap=[], bchars=[], match_rate=0.0)
cues = enforce_monotonic(group_cues(src_text, al, SPLIT))

patched = build_cues_json(data["duration"], al, cues)
save_cues(patched, OUT_JSON)
write_srt(cues, OUT_SRT)
print("重建完成：%d 条 cue" % len(cues))

# 与入库锁定版完全比对
ok = patched == data
print("RESULT", "PASS" if ok else "DIFF")
if not ok:
    print("chars equal:", patched["chars"] == data["chars"])
    print("cues equal:", patched["cues"] == data["cues"])
    sys.exit(1)

# SRT 与历史产物比对
hist_srt = Path(__file__).resolve().parents[4] / "Temp" / "zbj-cues.srt"
if hist_srt.exists():
    srt_ok = io.open(hist_srt, encoding="utf-8").read() == io.open(
        OUT_SRT, encoding="utf-8").read()
    print("SRT", "PASS" if srt_ok else "DIFF")
    if not srt_ok:
        sys.exit(1)
print("report", OUT_JSON)
