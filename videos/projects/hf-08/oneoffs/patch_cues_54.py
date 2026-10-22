# -*- coding: utf-8 -*-
"""hf-08 cues.json 句级补丁：与 patch_audio_54.py 成对（2026-10-22）。

音频窗 267.240–271.120 整句替换后，窗外时间轴逐样本不动，仅窗内 17 个
汉字时间戳与两条组句需按新音回填。字时间来源：patched 母带切窗
whisper base 词级（build/patch/check-54.wav），数字 token「54」
（267.82–268.36）按三字等分给五/十/四；组句界保持全片首尾相接体例，
逗号停顿（秒止 268.62 → 编起 268.94）从中点 268.78 分两句，下句尾界
271.02 不动（接窗外「小工程…」）。

只改 chars 17 字＋cues 2 条，其余 2421 字/291 条断言不动。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CUES = ROOT / "cues" / "cues.json"

# 字 → (s, e)，母带轴
NEW_CHARS = [
    ("硬", 267.36, 267.50), ("件", 267.50, 267.64),
    ("路", 267.64, 267.82),
    ("五", 267.82, 268.00), ("十", 268.00, 268.18),
    ("四", 268.18, 268.36), ("秒", 268.36, 268.62),
    ("编", 268.94, 269.06), ("码", 269.06, 269.18),
    ("和", 269.18, 269.42), ("抓", 269.42, 269.58),
    ("帧", 269.58, 269.80),
    ("重", 269.80, 270.08), ("叠", 270.08, 270.30),
    ("在", 270.30, 270.46),
    ("一", 270.46, 270.62), ("起", 270.62, 270.78),
]
OLD_TEXT = "硬件路五十二秒编码和抓帧重叠在一起"
NEW_TEXT = "".join(c for c, _, _ in NEW_CHARS)

# 组句：t 文本替换＋界回填
NEW_CUES = [
    ("硬件路五十四秒", 267.26, 268.78),
    ("编码和抓帧重叠在一起", 268.78, 271.02),
]
OLD_CUES = ["硬件路五十二秒", "编码和抓帧重叠在一起"]


def main():
    data = json.loads(CUES.read_text(encoding="utf-8"))
    chars, cues = data["chars"], data["cues"]

    # 定位 chars 窗：全文唯一匹配旧句
    joined = "".join(c["c"] for c in chars)
    assert joined.count(OLD_TEXT) == 1, "旧句匹配不唯一/缺失"
    i0 = joined.index(OLD_TEXT)
    old_chars = json.loads(json.dumps(chars[i0:i0 + len(NEW_CHARS)]))

    assert [c["c"] for c in chars[i0:i0 + len(NEW_CHARS)]] == list(OLD_TEXT)
    for k, (ch, s, e) in enumerate(NEW_CHARS):
        chars[i0 + k]["c"], chars[i0 + k]["s"], chars[i0 + k]["e"] = ch, s, e
    assert "".join(c["c"] for c in chars[i0:i0 + len(NEW_CHARS)]) == NEW_TEXT

    # 定位两条 cues（按旧文本＋旧时间双重断言）
    hit = 0
    for cue in cues:
        if cue["t"] in OLD_CUES:
            j = OLD_CUES.index(cue["t"])
            t, s, e = NEW_CUES[j]
            assert cue["s"] == (267.26 if j == 0 else 268.88), cue
            assert cue["e"] == (268.88 if j == 0 else 271.02), cue
            cue["t"], cue["s"], cue["e"] = t, s, e
            hit += 1
    assert hit == 2, "cues 命中数 %d" % hit

    # 单调性自检：全片既有 4 处字级起时倒挂（599/819/1139/1939，NW 插值
    # 允许相邻字小重叠，入库时评审接受），补丁不得新增坏点。
    bad = [k for k in range(1, len(chars))
           if chars[k]["s"] + 1e-9 < chars[k - 1]["s"]]
    assert bad == [599, 819, 1139, 1939], "非单调点集合变化: %s" % bad

    CUES.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print("chars[%d:%d] 17 字回填：%s" % (i0, i0 + 17,
          " ".join("%s%.2f-%.2f" % (c, s, e) for c, s, e in NEW_CHARS)))
    print("旧首字 %s → 新 %s" % (old_chars[0], chars[i0]))
    print("cues 2 条：", NEW_CUES)
    print("→", CUES.relative_to(ROOT))


if __name__ == "__main__":
    main()
