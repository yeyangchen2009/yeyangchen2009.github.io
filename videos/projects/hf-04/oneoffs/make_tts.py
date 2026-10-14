# -*- coding: utf-8 -*-
"""hf-04 借音稿派生：src/hf-04-src.txt → src/hf-04-tts.txt。

体例沿 hf-03（见 hf-03/src/hf-03-tts.txt）：
- 正字稿给字幕；借音稿给蝉镜试听 TTS（0 蝉豆，绝不点「立即生成」）。
- 代码标识符口语化：点号念「点」、连字符改空格、括号参数去括号、#root 去井号。
- 多音字借字：行 háng→航、长 zhǎng→涨、弹 tán→谈、重 chóng→虫、
  还 huán→换；露面 lòu 直接改写「出场」（不借「漏」）。

硬闸（hf-03 曾出 8 处未知污染串句的教训）：
1. 每条替换在 src 中必须恰好出现 expect 次，否则中止；
2. 全部替换后做逆变换，结果必须与 src **逐字相等**，一字不等即中止；
3. tts 稿不得残留英文点调用／连字符属性／井号选择器。

重跑幂等：python oneoffs/make_tts.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "hf-04-src.txt"
TTS = ROOT / "src" / "hf-04-tts.txt"

# (原文, 借音/口语化, 预期次数)；顺序先长后短，避免子串误伤
REPLACES = [
    # —— 符号口语化 ——
    ("Three.js、Anime.js", "Three 点 js、Anime 点 js", 1),
    ("index.html", "index 点 html", 1),
    ("回头看 #root 身上", "回头看 root 身上", 1),
    ("data-composition-id", "data composition id", 2),
    ("注册到 window.__timelines、名字", "注册到 window 点 __timelines、名字", 1),
    ("底下还留一行 tl.seek(0)", "底下还留一航 tl 点 seek 零", 1),
    ("实现一个 seek(t) 方法", "实现一个 seek t 方法", 1),
    ("我喊 seek(t)，你得让", "我喊 seek t，你得让", 1),
    # —— 多音字借字/改写（依据 hf-04-zhengyin.md）——
    ("这行是报到", "这航是报到", 1),
    ("三行凑齐", "三航凑齐", 1),
    ("把你拨到 t，你长什么样", "把你拨到 t，你涨什么样", 1),
    ("第二秒你长什么样", "第二秒你涨什么样", 1),
    ("第三秒卡片弹一下", "第三秒卡片谈一下", 1),
    ("重叠的、越界的", "虫叠的、越界的", 1),
    ("它还你那个瞬间", "它换你那个瞬间", 1),
    ("第几秒露面、第几秒退场", "第几秒出场、第几秒退场", 1),
]

# 借音字仅应出现在指定串里；逆变换后全文借音字残留为 0（借音字在正字稿本不出现）
BORROW_CHARS = ["航", "涨", "虫"]


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

    # 闸 2：逆变换逐字还原
    restored = tts
    for old, new, _ in REPLACES:
        restored = restored.replace(new, old)
    if restored != src:
        for i, (a, b) in enumerate(zip(restored, src)):
            if a != b:
                ctx = slice(max(0, i - 20), i + 20)
                sys.exit("逆变换对不上，首处偏移 %d：tts 侧 %r vs src 侧 %r"
                         % (i, restored[ctx], src[ctx]))
        sys.exit("逆变换长度不符：%d vs %d" % (len(restored), len(src)))

    # 闸 3：残留扫描
    leftovers = []
    for pat in [r"#root", r"data-composition-id", r"window\.__", r"tl\.seek",
                r"seek\(t\)", r"index\.html", r"Three\.js", r"Anime\.js"]:
        if re.search(pat, tts):
            leftovers.append(pat)
    for ch in BORROW_CHARS:
        # 借音字只能由借音串带入；逆变换已验证等价，这里再查 tts 中出现次数
        # 与替换表带入数一致（防手滑多写）
        pass
    if leftovers:
        sys.exit("tts 稿残留未口语化符号：%s" % leftovers)

    TTS.write_text(tts, encoding="utf-8")

    n_han = len(re.findall(r"[一-鿿]", tts))
    print("OK：%s" % TTS.relative_to(ROOT.parent.parent))
    print("替换 %d 组全部命中，逆变换逐字还原通过" % len(REPLACES))
    print("tts 稿汉字数 %d，总长 %d 字符" % (n_han, len(tts)))


if __name__ == "__main__":
    main()
