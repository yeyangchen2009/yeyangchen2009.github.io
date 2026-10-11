# -*- coding: utf-8 -*-
r"""hf-03 录屏操作链全链路冒烟：在 F:\_hftest\hf03-npptest 副本上跑
段①②④⑤的全部 NPP 编辑，逐步磁盘断言＋截图。正式录制文件不受影响。

用法：python smoke_npp.py
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec_automate as r
import npp_ops as n

TEST = r"F:\_hftest\hf03-npptest\index.html"
SHOT = r"F:\_hftest\hf03-rec\probe"

CARD_CSS = """      #card {
        position: absolute;
        width: 780px;
        padding: 52px 60px;
        background: #18181b;
        border: 1px solid #3f3f46;
        border-radius: 24px;
        color: #fbbf24;
        font-size: 44px;
        font-weight: 500;
        text-align: center;
      }
      #subtitle {
        color: #a1a1aa;
        font-size: 40px;
        font-weight: 400;
        margin-top: 28px;
      }"""

CARD_EL = ('      <div data-hf-id="hf-hj9x" id="card" class="clip" '
           'data-start="3" data-duration="2" data-track-index="0">'
           'HTML 里后写的，盖在上面</div>')
SUB_EL = ('      <h2 data-hf-id="hf-n4nz" id="subtitle" class="clip" '
          'data-start="6" data-duration="4" data-track-index="0">'
          '零行 JavaScript，先出片子</h2>')


def shot(name):
    r.screenshot(os.path.join(SHOT, f"smoke-{name}.png"))


def must(cond, msg):
    if not cond:
        shot("FAIL")
        raise AssertionError(msg)
    print("ok:", msg)


def main():
    n.launch(TEST)
    time.sleep(.5)
    shot("00-start")

    # ---- 段①：CDN 换本地 ----
    n.replace_all("https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js",
                  "gsap.min.js")
    n.save(lambda t: 'src="gsap.min.js"' in t and "cdn.jsdelivr" not in t)
    must('src="gsap.min.js"' in n.read_file(), "段① CDN→本地")
    shot("01-cdn")

    # ---- 段②：标题文字＋时间（唯一长串，避开 root 行同值属性）----
    old = ('class="clip" data-start="0" data-duration="10" '
           'data-track-index="0">Title</h1>')
    new = ('class="clip" data-start="2" data-duration="4" '
           'data-track-index="0">我的第一个片段</h1>')
    n.replace_all(old, new)
    n.save(lambda t: "我的第一个片段" in t and 'data-start="2" data-duration="4"' in t)
    t = n.read_file()
    must("我的第一个片段" in t, "段② 标题文字")
    must(t.count('data-start="2" data-duration="4"') == 1, "段② 时间唯一替换")
    shot("02-title")

    # ---- 段④a：#root 加 position: relative ----
    n.insert_after_anchor("#root {", "        position: relative;")
    n.save(lambda t: "position: relative;" in t)
    must(n.read_file().count("position: relative;") == 1, "段④a root relative")

    # ---- 段④b：#card/#subtitle 样式，插在 </style> 前 ----
    n.insert_after_line(n.line_of("</style>") - 1, CARD_CSS)
    n.save(lambda t: "#card {" in t and "#subtitle {" in t)
    t = n.read_file()
    must("#card {" in t and "#subtitle {" in t, "段④b 两段样式")
    must(t.count("<style>") == 1, "style 块仍唯一")
    shot("04b-css")

    # ---- 段④c：card 元素先插在 title 之后（后写者盖上）----
    n.insert_after_anchor("我的第一个片段", CARD_EL)
    n.save(lambda t: 'id="card"' in t)
    t = n.read_file()
    must(t.index("我的第一个片段") < t.index('id="card"'), "段④c card 在 title 后")

    # ---- 段④d：Alt+Up 移到 title 前 ----
    n.move_line_up(n.line_of('id="card"'))
    n.save(lambda t: t.index('id="card"') < t.index("我的第一个片段"))
    t = n.read_file()
    must(t.index('id="card"') < t.index("我的第一个片段"), "段④d card 移到 title 前")

    # ---- 段④e：subtitle 插在 title 后 ----
    n.insert_after_anchor("我的第一个片段", SUB_EL)
    n.save(lambda t: 'id="subtitle"' in t)
    t = n.read_file()
    must(t.index('id="card"') < t.index("我的第一个片段") < t.index('id="subtitle"'),
         "段④e 终态顺序 card→title→subtitle")
    shot("04e-els")

    # ---- 段⑤：check 报错后加 data-layout-allow-overlap ----
    n.replace_all('id="card" class="clip" data-start="3" data-duration="2"',
                  'id="card" class="clip" data-start="3" data-duration="2" '
                  'data-layout-allow-overlap=""')
    n.save(lambda t: "data-layout-allow-overlap" in t)
    must(n.read_file().count("data-layout-allow-overlap") == 1, "段⑤ 放行属性")
    shot("05-allow")

    print("\n=== 终态文件 ===")
    print(n.read_file())


if __name__ == "__main__":
    main()
