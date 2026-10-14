# -*- coding: utf-8 -*-
"""hf-04 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留本集独有的：布局数值、控制台卡 → 时间轴播放头（2.4）＋
倒着播回头弧的铅笔素描主视觉、CONSOLE→seek(2.4)→TIMELINE 金色制图、
文字内容。
用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover
from videopipe.cover import RULER_LEFT, BOX_RIGHT

HERE = Path(__file__).resolve().parent

# 本集布局数值（结构同 hf-01/02/03；t2 拉丁字母偏窄，宽度仍取 1120）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="78%", wash_y="50%", wash_alpha=".14",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=200, t2_mtop=10,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=80, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层（全局坐标）：CONSOLE 命令 → seek(2.4) → TIMELINE
BLUEPRINT_SVG = """  <!-- 主流程金线 y=835：1052 控制台 → 1330 seek → 1604 时间轴 -->
  <line class="bp bp-line" x1="1092" y1="835" x2="1317" y2="835"/>
  <line class="bp bp-line" x1="1343" y1="835" x2="1591" y2="835"/>
  <path class="bp bp-line" d="M 1301 823 L 1327 835 L 1301 847"/>
  <path class="bp bp-line" d="M 1575 823 L 1601 835 L 1575 847"/>
  <circle class="bp-dot" cx="1080" cy="835" r="6"/>
  <circle class="bp-dot" cx="1330" cy="835" r="6"/>
  <circle class="bp-dot" cx="1614" cy="835" r="6"/>

  <!-- 节点标签（上方 y=798） -->
  <text x="1080" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">CONSOLE</text>
  <text x="1330" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">seek(2.4)</text>
  <text x="1614" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">TIMELINE</text>

  <!-- 罩在时间轴上方的 construction 虚线半圆弧（中心 1630,360，半宽 210） -->
  <path class="bp bp-thin" stroke-dasharray="9 8"
        d="M 1420 360 A 210 210 0 0 1 1840 360"/>
  <path class="bp bp-dim" d="M 1404 360 A 226 226 0 0 1 1856 360"/>
  <g class="bp bp-dim">
    <line x1="1500" y1="182" x2="1512" y2="194"/>
    <line x1="1754" y1="194" x2="1766" y2="182"/>
  </g>

  <!-- 左上十字准星 -->
  <g>
    <line class="bp bp-line" x1="180" y1="118" x2="640" y2="118"/>
    <line class="bp bp-line" x1="410" y1="66" x2="410" y2="172"/>
    <circle class="bp bp-dim" cx="410" cy="118" r="14"/>
    <circle class="bp-dot" cx="410" cy="118" r="3.2"/>
  </g>

%s

%s""" % (RULER_LEFT, BOX_RIGHT)

# 素描主视觉 SVG 内层：DevTools 控制台卡 seek(2.4) → 时间轴播放头，
# 轴上刻点 0 / 2.4 / 3 / 6.3 / 9 / 10，9 跳回 2.4 的回头弧＝倒着播。
# 基点 1010,430（t2 含拉丁词 seek 比纯中文宽，主视觉整体上移避开大字行）
SCENE_SVG = """  <g transform="translate(1010,430)">
  <!-- ===== 控制台卡 x=-170..210，y=-250..-100 ===== -->
  <rect x="-170" y="-250" width="380" height="150" rx="12" class="pencil"
        stroke-width="2.8" style="fill:#fbf6ea"/>
  <!-- 标题栏三圆点 -->
  <circle cx="-144" cy="-229" r="6" class="pencil" stroke-width="1.6"
          style="fill:#d98b7a;fill-opacity:.55"/>
  <circle cx="-120" cy="-229" r="6" class="pencil" stroke-width="1.6"
          style="fill:#dcc07a;fill-opacity:.55"/>
  <circle cx="-96" cy="-229" r="6" class="pencil" stroke-width="1.6"
          style="fill:#8fb083;fill-opacity:.55"/>
  <text x="186" y="-222" text-anchor="end" font-family="Consolas,monospace"
        font-size="14" fill="#8a7d64">DevTools · Console</text>
  <line x1="-170" y1="-208" x2="210" y2="-208" class="pencil hatch"/>

  <!-- 命令行：seek 五拍 -->
  <text x="-142" y="-172" font-family="Consolas,monospace" font-size="18"
        fill="#423a2e">&gt; window.__player.seek(2.4)</text>
  <line x1="-142" y1="-160" x2="166" y2="-160" class="pencil" stroke-width="1.8"/>
  <text x="-142" y="-128" font-family="Consolas,monospace" font-size="16"
        fill="#7a6f58" class="pencil hatch">&gt; seek(3) · 6.3 · 9 · 0</text>

  <!-- ===== 令箭：卡片 → 播放头三角（斜下） ===== -->
  <line x1="216" y1="-170" x2="352" y2="14" class="pencil" stroke-width="2.6"/>
  <path class="pencil" stroke-width="2.6" d="M 350 4 L 378 26 L 352 36"/>

  <!-- ===== 时间轴 x=260..820，轴线 y=60 ===== -->
  <line x1="260" y1="60" x2="820" y2="60" class="pencil" stroke-width="2.6"/>
  <!-- 端帽 0 / 10 -->
  <line x1="260" y1="46" x2="260" y2="74" class="pencil" stroke-width="2.2"/>
  <line x1="820" y1="46" x2="820" y2="74" class="pencil" stroke-width="2.2"/>
  <!-- 刻点 3 / 6.3 / 9 -->
  <line x1="428" y1="50" x2="428" y2="70" class="pencil hatch"/>
  <line x1="613" y1="50" x2="613" y2="70" class="pencil hatch"/>
  <line x1="764" y1="50" x2="764" y2="70" class="pencil hatch"/>
  <!-- 2.4 播放头：竖杆＋三角，淡金填充 -->
  <line x1="394" y1="28" x2="394" y2="92" class="pencil" stroke-width="2.4"/>
  <path class="pencil" stroke-width="2.4" style="fill:#d8b865;fill-opacity:.30"
        d="M 394 22 L 382 42 L 406 42 Z"/>
  <!-- 刻度数字 -->
  <g font-family="Consolas,monospace" font-size="16" fill="#7a6f58"
     class="pencil hatch" text-anchor="middle">
    <text x="260" y="102">0</text>
    <text x="394" y="102" font-family="Consolas,monospace" font-size="16"
          fill="#423a2e" text-anchor="middle">2.4</text>
    <text x="428" y="102">3</text>
    <text x="613" y="102">6.3</text>
    <text x="764" y="102">9</text>
    <text x="820" y="102">10</text>
  </g>

  <!-- ===== 回头弧：9 跳回 2.4，倒着播 ===== -->
  <path class="pencil" stroke-width="2.2" stroke-dasharray="7 6"
        d="M 764 46 A 185 78 0 0 0 394 46"/>
  <path class="pencil" stroke-width="2.2" d="M 408 56 L 388 44 L 406 34"/>
  <text x="579" y="-48" text-anchor="middle" font-family="KaiTi,serif"
        font-size="18" fill="#5a4f3c">倒着播 · 来回播</text>
  </g>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="BUILT FOR AGENTS · No.04",
    title1="灵魂在哪？",
    title2="seek 里。",
    seal_cols=[["寻"]],
    dateline="HyperFrames 教程 · 第 04 集",
    dateline_en="THE SOUL IS IN SEEK",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="hf-04 封面",
    scene_comment="素描主视觉：控制台 seek(2.4) 令箭 → 时间轴播放头，9 跳回 2.4 回头弧",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
