# -*- coding: utf-8 -*-
"""hf-08 宽字幕 cue 批量拆句（check 字幕单行盒穿帮收口）。

背景：DARK_GOLD_GH 字幕是单行盒（bottom 只容一行，40px 楷体实测容量
约 23.5 字宽单位）。cards-only check 只在 t=305.75 采样抓到一条折行
（51 字长句，已由 split_long_cue.py 先拆四刀）；全片扫描又发现 13 条
≥21 单位的漏网句（check 采样时刻没覆盖）。本脚本按语义断点一次拆齐。

方法（零猜测）：
- 断点文本手工给定（严格原子串，含原排版空格），脚本校验拼接逐字不变；
- 切点时间取 cues.json 自带的逐字 chars 对齐戳（断点最后一个汉字的 e），
  不碰音频、不碰 chars；首条 s＝原 s、末条 e＝原 e。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parents[1]))
from videopipe.cues import to_srt  # noqa: E402

CUES = ROOT / "cues" / "cues.json"

HAN = re.compile(r"[一-鿿]")

# 原句 s → 拆分文本（拼接须与原 t 逐字一致，空格照原串）
SPLITS = {
    144.12: ["看这台机器的硬件 GPU能不能用", "接着在三百九十帧里挑五帧真截一遍"],
    594.84: ["就能在云端烤", "官方还留着 cloud lambda cloudrun", "一路命令"],
    260.12: ["其中光开浏览器试截几帧就花掉十六秒", "第二回浏览器热了"],
    300.94: ["总内存的一半", "除以每个 worker一千五百三十六兆的预算"],
    225.84: ["等三家都交活再统一编码", "并行截图的时候没法边截边编"],
    522.70: ["浏览器开页面六十秒", "协议通话三百秒", "等就绪四十五秒"],
    493.80: ["编译产物每一帧的图无声视频音频", "阶段账本全在里面"],
    408.00: ["红方块用 requestAnimationFrame", "自己掐着表跑"],
    78.80: ["每一格都是一次独立求解", "把时间轴 seek到这个时刻"],
    509.92: ["它自己都会建议你用-w", "降到一个 worker隔离重烤"],
    365.44: ["烤出来的片子出现了竖直黑条", "三个硬件实例抢内存"],
    321.66: ["最后被压到三个", "和烤的时候日志里报的数一模一样"],
    40.48: ["而这里连软件 GPU和硬件 GPU", "两条完全不同的路"],
    193.26: ["有一种格式直接输出三百九十张 PNG", "加一条声音"],
}

data = json.loads(CUES.read_text(encoding="utf-8"))
cues, chars = data["cues"], data["chars"]

# 重放 char_track 的汉字消费序，记每条 cue 的 chars 起始下标
char_idx = 0
bases = []
for c in cues:
    bases.append(char_idx)
    char_idx += len(HAN.findall(c["t"]))
assert char_idx == len(chars), "cue 汉字数与 chars 不符 %d/%d" % (char_idx, len(chars))

by_s = {round(c["s"], 2): (k, c) for k, c in enumerate(cues)}
out = []
applied = 0
for i, c in enumerate(cues):
    spec = SPLITS.get(round(c["s"], 2))
    if not spec:
        out.append(c)
        continue
    assert "".join(spec) == c["t"], (c["s"], c["t"], spec)
    base = bases[i]
    hacc, s0 = 0, c["s"]
    for j, t in enumerate(spec):
        hn = len(HAN.findall(t))
        if j == len(spec) - 1:
            e1 = c["e"]
        else:
            e1 = chars[base + hacc + hn - 1]["e"]
        assert s0 < e1, (c["s"], j, s0, e1)
        out.append({"s": round(s0, 2), "e": round(e1, 2), "t": t})
        s0 = e1
        hacc += hn
    applied += 1

# 全表单调（允许间隙，不许倒挂）
for a, b in zip(out, out[1:]):
    assert a["e"] <= b["s"] + 1e-9, (a, b)

data["cues"] = out
CUES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
(ROOT / "build" / "cues.srt").write_text(to_srt(out), encoding="utf-8")
print("拆 %d 条 → 总 %d 句" % (applied, len(out)))
