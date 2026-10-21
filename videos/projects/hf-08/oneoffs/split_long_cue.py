# -*- coding: utf-8 -*-
"""hf-08 唯一超长 cue 拆句（cards-only check 抓出的字幕溢出）。

现象：check layout 报 t=305.75s 字幕 canvas_overflow bottom 13px，22 个
逐字 span——cues 里一条 51 字长句（四笔账被 whisper 连成一句）折三行
出底。前三集基线最长 36–43 字（两行内）。

处置：按 raw.json 词级时间戳把该句拆成四条（四笔账各一条），时间边界
严格首尾相接；四句 t 的汉字序列拼接与原句逐字一致（char_track 顺序
消费 chars 并 assert），只切不增删字。改 cues/cues.json（lockfile 评审
修订）并重导 build/cues.srt；不动 chars、不动音频。

原句：299.66–309.60
  CPU核数减二 | 总内存的一半除以每个 worker一千五百三十六兆的预算
  | 总帧数除以三十 | 再给内存堆留一笔账
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parents[1]))
from videopipe.cues import to_srt  # noqa: E402

CUES = ROOT / "cues" / "cues.json"
SRT = ROOT / "build" / "cues.srt"

OLD_S, OLD_E = 299.66, 309.6
NEW = [
    (299.66, 300.94, "CPU核数减二"),
    (300.94, 305.66, "总内存的一半除以每个 worker一千五百三十六兆的预算"),
    (305.66, 307.48, "总帧数除以三十"),
    (307.48, 309.60, "再给内存堆留一笔账"),
]

data = json.loads(CUES.read_text(encoding="utf-8"))
cues = data["cues"]

i = next(k for k, c in enumerate(cues) if abs(c["s"] - OLD_S) < 0.01
         and abs(c["e"] - OLD_E) < 0.01)
old = cues[i]
assert old["t"].replace(" ", "") == "".join(t for _, _, t in NEW).replace(" ", ""), \
    "拆句文本与原句不一致：%r" % old["t"]

cues[i:i + 1] = [{"s": s, "e": e, "t": t} for s, e, t in NEW]

# 局部复核：新四条彼此首尾相接、不与前后旧句倒挂（全表允许句间间隙）
for a, b in zip(NEW, NEW[1:]):
    assert a[1] == b[0], (a, b)
prev_e = cues[i - 1]["e"] if i > 0 else 0.0
next_s = cues[i + 4]["s"] if i + 4 < len(cues) else float("inf")
assert prev_e <= NEW[0][0] and NEW[-1][1] <= next_s, (prev_e, next_s)

data["cues"] = cues
CUES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8")
SRT.parent.mkdir(exist_ok=True)
SRT.write_text(to_srt(cues), encoding="utf-8")
print("已拆句：%d → %d 条；最长句 %d 字；SRT 重导 %s"
      % (len(cues) - 3, len(cues), max(len(c["t"]) for c in cues), SRT.name))
