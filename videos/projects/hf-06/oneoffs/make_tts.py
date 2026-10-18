# -*- coding: utf-8 -*-
"""hf-06 借音稿派生：src/hf-06-src.txt → src/hf-06-tts.txt。

体例沿 hf-03/04/05（见 ../../hf-05/oneoffs/make_tts.py）：
- 正字稿给字幕；借音稿给蝉镜试听 TTS（0 蝉豆，绝不点「立即生成」）。
- 本集轻工艺档（用户 2026-10-18 拍板）：英文词整词还是分字母不纠缠，
  有字幕兜底，只把连字符属性/命令名机械拆空格（沿用 hf-05 成熟惯例），
  true/false 借「真/假」，--write 念「横杠横杠 write」，sut 沿上集分字母。
- 多音字只处理硬伤：3 处 děi 改写为「要」；6 处动词 liáng「量」借「测」；
  1 处 háng「一行字」改写。「音量/响度」的 liàng 保留。

硬闸（hf-03 曾出 8 处未知污染串句的教训）：
1. 每条替换在 src 中必须恰好出现 expect 次，否则中止；
2. 全部替换后做逆变换，结果必须与 src 逐字相等，一字不等即中止；
3. tts 稿不得残留连字符词/data- 前缀/双横杠/井号/半角括号/下划线/
   sut 连写/true/false，不得出现任何半角数字（本集口播无版本号）；
4. 替换后计数：「测」7（实测原 1＋6 处 liáng 借入），「量」1（仅音量；
   「响度」从度字），「行」3（行动件＋也行×2），「得」3（压得/轻得/分得清）。

重跑幂等：python oneoffs/make_tts.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "hf-06-src.txt"
TTS = ROOT / "src" / "hf-06-tts.txt"

# (原文, 借音/口语化, 预期次数)；先长后短、上下文唯一，避免子串误伤。
REPLACES = [
    # —— 符号口语化（机械拆连字符，沿 hf-05）——
    ("data-timeline-role", "data timeline role", 2),
    ("data-media-start", "data media start", 1),
    ("data-has-audio", "data has audio", 1),
    ("data-fade-in", "data fade in", 1),
    ("data-fade-out", "data fade out", 1),
    ("data-duration", "data duration", 1),
    ("data-start", "data start", 1),
    ("data-volume", "data volume", 3),
    ("normalize-audio", "normalize audio", 4),
    ("media-treatment", "media treatment", 2),
    ("a-roll-audio", "a roll audio", 1),
    ("audio_src_not_found", "audio src not found", 1),
    ("--write", "横杠横杠 write", 1),
    ("井号 sut", "井号 s u t", 1),
    ("等于 true", "等于真", 1),
    ("ok 是 false", "ok 是假", 1),
    # bgn 不是词，整串蝉镜必乱念；id 全片默认念法不拆（一致性）
    ("id，bgn。", "id，b g n。", 1),
    # —— 多音字：děi 改写 ——
    ("还得多回答", "还要多回答", 1),
    ("得拆成两种情况", "要拆成两种情况", 1),
    # —— 多音字：动词 liáng「量」借「测」（hf-05 成熟借法）——
    ("它量的不是", "它测的不是", 1),
    ("它两条都量", "它两条都测", 1),
    ("量曝光、量对比度", "测曝光、测对比度", 1),
    ("一眼就量出来了", "一眼就测出来了", 1),
    ("拿 LUFS 量", "拿 LUFS 测", 1),
    # —— 多音字：háng ——
    ("一行字都不用", "一个字都不用", 1),
]

# 借义/借音字计数（值＝替换后 tts 稿中的预期总次数）
# 测＝「实测」原 1＋6 处 liáng 借入；量＝仅剩「音量」1（「响度」从字，不算）；
# 行＝行动件 1＋也行 2（háng 那处已改写）；得＝压得/轻得/分得清三处 de。
COUNT_EXPECT = {"测": 7, "量": 1, "行": 3, "得": 3}


def main():
    src = SRC.read_text(encoding="utf-8")

    # 闸 1：预期次数
    for old, _new, expect in REPLACES:
        got = src.count(old)
        if got != expect:
            sys.exit("替换项次数不符：%r 预期 %d 实得 %d" % (old, expect, got))

    tts = src
    for old, new, _ in REPLACES:
        tts = tts.replace(old, new)

    # 闸 2：逆变换逐字还原（反序还原，双保险；各 new 串上下文已保证无子串嵌套）
    restored = tts
    for old, new, _ in reversed(REPLACES):
        restored = restored.replace(new, old)
    if restored != src:
        for i, (a, b) in enumerate(zip(restored, src)):
            if a != b:
                ctx = slice(max(0, i - 20), i + 20)
                sys.exit("逆变换对不上，首处偏移 %d：tts 侧 %r vs src 侧 %r"
                         % (i, restored[ctx], src[ctx]))
        sys.exit("逆变换长度不符：%d vs %d" % (len(restored), len(src)))

    # 闸 3：残留符号扫描
    leftovers = []
    for pat, label in [
        (r"data-[a-z]", "data- 前缀"),
        (r"[a-z]+-[a-z]+", "连字符词"),
        (r"--", "双横杠"),
        (r"#", "井号符"),
        (r"[()]", "半角括号"),
        (r"[A-Za-z]_[A-Za-z]", "蛇形命名"),
        (r"sut", "sut 连写"),
        (r"true|false", "true/false"),
    ]:
        m = re.search(pat, tts)
        if m:
            leftovers.append("%s: %r" % (label, m.group(0)))
    nums = re.findall(r"\d+\.?\d*", tts)
    if nums:
        leftovers.append("半角数字: %r" % nums)
    if leftovers:
        sys.exit("tts 稿残留未口语化符号：\n  " + "\n  ".join(leftovers))

    # 闸 4：多音字词计数
    for ch, expect in COUNT_EXPECT.items():
        got = tts.count(ch)
        if got != expect:
            sys.exit("字 %r 出现 %d 次，预期 %d" % (ch, got, expect))

    TTS.write_text(tts, encoding="utf-8")

    n_han = len(re.findall(r"[一-鿿]", tts))
    print("OK：%s" % TTS.relative_to(ROOT.parent.parent))
    print("替换 %d 组全部命中，逆变换逐字还原通过，残留/计数闸通过"
          % len(REPLACES))
    print("tts 稿汉字数 %d，总长 %d 字符" % (n_han, len(tts)))


if __name__ == "__main__":
    main()
