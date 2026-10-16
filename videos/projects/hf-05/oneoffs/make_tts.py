# -*- coding: utf-8 -*-
"""hf-05 借音稿派生：src/hf-05-src.txt → src/hf-05-tts.txt。

体例沿 hf-03/hf-04（见 ../hf-04/oneoffs/make_tts.py）：
- 正字稿给字幕；借音稿给蝉镜试听 TTS（0 蝉豆，绝不点「立即生成」）。
- 符号口语化：连字符属性改空格、蛇形规则名下划线改空格、@ 念 at、
  井号选择器去符号逐字符、rgb() 去括号、--shot 念「横杠横杠 shot」、
  ERRORLEVEL 拆词防逐字母。
- 多音字处理（依据 ../src/hf-05-zhengyin.md）：
  行 háng 借「航」1 处＋同义/量词改写 8 处；量 liáng→测；数 shǔ→算；
  待 dāi→停；明晃晃→明明白白（huǎng 易误 huàng）。

硬闸（hf-03 曾出 8 处未知污染串句的教训）：
1. 每条替换在 src 中必须恰好出现 expect 次，否则中止；
2. 全部替换后做逆变换，结果必须与 src 逐字相等，一字不等即中止；
3. tts 稿不得残留连字符属性/蛇形命名/@/半角括号/双横杠/井号，
   半角数字只允许出现在版本号 0.8.107；
4. 借音字「航」在 tts 稿中恰 1 次（仅由替换带入）。

重跑幂等：python oneoffs/make_tts.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "hf-05-src.txt"
TTS = ROOT / "src" / "hf-05-tts.txt"

# (原文, 借音/口语化, 预期次数)；先长后短、上下文唯一，避免子串误伤。
# 注意：裸 "track-index" 是 "data-track-index" 的子串，故第二条带足上下文，
# 正/逆替换都不靠子串包含关系。
REPLACES = [
    # —— 符号口语化 ——
    ("npx hyperframes@0.8.107 check", "n p x hyperframes at 0.8.107 check", 1),
    ("timeline_element_missing_timing", "timeline element missing timing", 1),
    ("clip_ends_past_root_duration", "clip ends past root duration", 1),
    ("data-timeline-role", "data timeline role", 1),
    ("data-track-index", "data track index", 1),
    ("track-index 只是给", "track index 只是给", 1),
    ("data-duration", "data duration", 2),
    ("text_occluded", "text occluded", 1),
    ("page_error", "page error", 1),
    # sut 是蝉镜词库外拼写，整词会被纠偏念成熟词 sub（试音＋词尾 F2 双证）；
    # 分字母后蝉镜念字母名 S-U-T（probe-sut 试音验证），与 /sʌb/ 泾渭分明。
    ("井号 sut", "井号 s u t", 2),
    ("index.html", "index 点 html", 1),
    ("井号 1a1f26", "井号一 a 一 f 二六", 1),
    ("rgb(93,97,102)", "r g b 九三，九七，一零二", 1),
    ("--shot", "横杠横杠 shot", 1),
    ("百分号 ERRORLEVEL 百分号", "百分号 error level 百分号", 1),
    # —— 多音字借字/改写（依据 hf-05-zhengyin.md）——
    ("几百行 HTML", "几百航 HTML", 1),
    ("明晃晃", "明明白白", 1),
    ("一个个 seek 过去量布局", "一个个 seek 过去测布局", 1),
    ("每个采样点量文字和底色的对比度", "每个采样点测文字和底色的对比度", 1),
    ("渲染出来才量得出的遮挡和对比", "渲染出来才测得出的遮挡和对比", 1),
    ("进来，待五秒", "进来，停五秒", 1),
    ("数拍子用的", "算节拍用的", 1),
    ("一行黄字", "一条黄字", 1),
    ("就这一行", "就这一处", 1),
    ("躺着三行警告", "躺着三条警告", 1),
    ("一行点了名", "头一条点了名", 1),
    ("还有两行", "还有两条", 1),
    ("它直接一行红字", "它直接蹦出红字", 1),
    ("这行红是它没活干", "这句红是它没活干", 1),
    ("另起一行", "另敲一句", 1),
]

# 借音字仅应由替换带入恰 1 次（正字稿中本无「航」）
BORROW_CHARS = {"航": 1}


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
    for pat in [r"data-[a-z]", r"[A-Za-z]_[A-Za-z]", r"index\.html",
                r"#", r"@", r"[()]", r"--", r"sut"]:
        m = re.search(pat, tts)
        if m:
            leftovers.append("%s -> %r" % (pat, m.group(0)))
    # 半角数字只允许版本号 0.8.107（分词为 0.8 与 107）
    nums = re.findall(r"\d+\.?\d*", tts)
    if nums != ["0.8", "107"]:
        leftovers.append("半角数字非版本号: %r" % nums)
    if leftovers:
        sys.exit("tts 稿残留未口语化符号：\n  " + "\n  ".join(leftovers))

    # 闸 4：借音字计数
    for ch, expect in BORROW_CHARS.items():
        got = tts.count(ch)
        if got != expect:
            sys.exit("借音字 %r 出现 %d 次，预期 %d" % (ch, got, expect))

    TTS.write_text(tts, encoding="utf-8")

    n_han = len(re.findall(r"[一-鿿]", tts))
    print("OK：%s" % TTS.relative_to(ROOT.parent.parent))
    print("替换 %d 组全部命中，逆变换逐字还原通过，残留/借音闸通过"
          % len(REPLACES))
    print("tts 稿汉字数 %d，总长 %d 字符" % (n_han, len(tts)))


if __name__ == "__main__":
    main()
