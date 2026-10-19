# -*- coding: utf-8 -*-
"""hf-07 借音稿派生：src/hf-07-src.txt → src/hf-07-tts.txt。

体例沿 hf-03/04/05/06（见 ../../hf-06/oneoffs/make_tts.py）：
- 正字稿给字幕；借音稿给蝉镜试听 TTS（0 蝉豆，绝不点「立即生成」）。
- 本集轻工艺档：英文命令/参数名整词保留（有字幕兜底），只做三处机械
  口语化：--shot 念「横杠横杠 shot」（hf-05 惯例）；grade-compare 拆
  空格；MP4 系列口播首现，拆「M P 四」（逐字母＋中文，同 WCAG 体例）。
- 多音字在写稿阶段已全部清掉硬伤：「那几行」改「那几句」、「也行」改
  「也可以」、「得靠」改「要靠」、「一条条量」改「一条条查」。剩下的
  行/得/还/长/数全单一读音，计数闸锁死防后续改稿引入污染。
- window 点 __timelines 沿 hf-04 体例原样（蝉镜试听通过、成片 F2 过）。

硬闸（hf-03 曾出 8 处未知污染串句的教训）：
1. 每条替换在 src 中必须恰好出现 expect 次，否则中止；
2. 全部替换后做逆变换，结果必须与 src 逐字相等，一字不等即中止；
3. tts 稿不得残留连字符词/data- 前缀/双横杠/井号/半角括号/蛇形命名/
   true/false，不得出现任何半角数字（MP4 已拆 M P 四）；
4. 替换后多音字词计数：行 1（仅行动件，xíng）、得 8（全 de 补语）、
   还 8（全 hái）、地 4、数 6（全 shù）。

重跑幂等：python oneoffs/make_tts.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "hf-07-src.txt"
TTS = ROOT / "src" / "hf-07-tts.txt"

# (原文, 借音/口语化, 预期次数)
REPLACES = [
    ("--shot", "横杠横杠 shot", 3),
    ("grade-compare", "grade compare", 1),
    ("MP4", "M P 四", 1),
]

# 多音/高频字计数（值＝替换后 tts 稿中的预期总次数）
# 行＝仅「行动件」xíng（háng/xíng 硬伤写稿时已改写避音）；
# 得＝滑得/走得/写得最心虚/查得出来/查得出/写得清清楚楚/驱得动/管得住，全 de；
# 还＝我还/还停/还要/还送/还有/还能用/还能/还是，全 hái；
# 地＝像素级地(de)＋四个地方(dì)＋天经地义(dì)＋三个地方(dì)；
# 数＝数字/有数/秒数(列出来)/给个数/秒数命名/参数/同一个秒数，全 shù。
COUNT_EXPECT = {"行": 1, "得": 8, "还": 8, "地": 4, "数": 7}


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

    # 闸 2：逆变换逐字还原（反序还原，双保险）
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
