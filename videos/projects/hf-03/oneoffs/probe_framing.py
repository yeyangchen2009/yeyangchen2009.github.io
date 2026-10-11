# -*- coding: utf-8 -*-
"""hf-03 取景探针：干净 init 样板上验证五段录屏要用的全部 NPP 镜头（zoom=0）。

只发选区消息、不编辑文件。每跑前重置：
  cp /f/_hftest/hf03-clip/index.html /f/_hftest/hf03-npptest/index.html
用法：python probe_framing.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec_automate as r
import npp_ops as n

TEST = r"F:\_hftest\hf03-npptest\index.html"
SHOT = r"F:\_hftest\hf03-rec\probe"


def snap(name, hold=0.4):
    time.sleep(hold)
    r.screenshot(os.path.join(SHOT, name))
    print("shot:", name)


def main():
    n.launch(TEST)
    n.set_zoom(0)
    time.sleep(.3)

    # 0. 全景首屏（caret 归文件头，自动滚回左上）
    s = n.active_scintilla()
    n._senda(s, n.SCI_SETSEL, 0, 0)
    snap("L0-home.png")

    tl = n.line_of('class="clip"')   # L39 title 行
    cdn = n.line_of("cdn.jsdelivr")  # L6

    # 段①拍 A：class / data-start / data-duration 三属性
    n.reveal_in_line(tl, 'class="clip"', 'data-duration="10"')
    snap("L1-attrs-a.png")

    # 段①拍 B：data-track-index + Title（横移）
    n.reveal_in_line(tl, "data-track-index", "</h1>")
    snap("L1-attrs-b.png")

    # 段①CDN：选区到版本号为止，保证 URL 头部在镜内
    n.reveal_in_line(cdn, "<script", "gsap@3.14.2")
    snap("L1-cdn.png")

    # 段④a：#root CSS 规则（先送 caret 到块底 font-family 行，整块入镜）
    n.reveal_in_line(n.line_of("#root {"), "#root {",
                     scroll_anchor=(n.line_of("font-family: Inter"),
                                    "font-family: Inter"))
    snap("L4-root-css.png")

    # 段④b：#title 规则块（先送 caret 到块底 letter-spacing 行）
    n.reveal_in_line(n.line_of("#title {"), "#title {",
                     scroll_anchor=(n.line_of("letter-spacing"),
                                    "letter-spacing"))
    snap("L4-title-css.png")

    # 段④c：body 结构（root/title 元素）
    n.reveal_in_line(tl, "<h1", 'class="clip"')
    snap("L4-body.png")


if __name__ == "__main__":
    main()
