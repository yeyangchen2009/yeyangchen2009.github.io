# -*- coding: utf-8 -*-
"""hf-03 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留本集独有的：布局数值、带 data-start/data-duration 的 HTML 标签卡
→ 时间轴 2–6 高亮段 铅笔素描主视觉、TAG→2–6→PLAY 金色制图、文字内容。
用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover
from videopipe.cover import RULER_LEFT, BOX_RIGHT

HERE = Path(__file__).resolve().parent

# 本集布局数值（结构同 hf-01/02，文字数相近）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="78%", wash_y="50%", wash_alpha=".14",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=200, t2_mtop=10,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=80, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层（全局坐标）：TAG→2–6→PLAY 为本集独有
BLUEPRINT_SVG = """  <!-- 主流程金线 y=835：1052 标签 → 1330 时间段 → 1604 播放 -->
  <line class="bp bp-line" x1="1092" y1="835" x2="1317" y2="835"/>
  <line class="bp bp-line" x1="1343" y1="835" x2="1591" y2="835"/>
  <path class="bp bp-line" d="M 1301 823 L 1327 835 L 1301 847"/>
  <path class="bp bp-line" d="M 1575 823 L 1601 835 L 1575 847"/>
  <circle class="bp-dot" cx="1080" cy="835" r="6"/>
  <circle class="bp-dot" cx="1330" cy="835" r="6"/>
  <circle class="bp-dot" cx="1614" cy="835" r="6"/>

  <!-- 节点标签（上方 y=798） -->
  <text x="1080" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">TAG</text>
  <text x="1330" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">2–6</text>
  <text x="1614" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">PLAY</text>

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

# 素描主视觉 SVG 内层：HTML 标签卡（data-start/data-duration）→ 时间轴 2–6，
# 基点 1010,600
SCENE_SVG = """  <g transform="translate(1010,600)">
  <!-- ===== 标签卡 index.html x=-150..300，y=-220..60 ===== -->
  <rect x="-150" y="-220" width="450" height="280" rx="12" class="pencil"
        stroke-width="2.8" style="fill:#fbf6ea"/>
  <!-- 标题栏三圆点 -->
  <circle cx="-124" cy="-199" r="6" class="pencil" stroke-width="1.6"
          style="fill:#d98b7a;fill-opacity:.55"/>
  <circle cx="-100" cy="-199" r="6" class="pencil" stroke-width="1.6"
          style="fill:#dcc07a;fill-opacity:.55"/>
  <circle cx="-76" cy="-199" r="6" class="pencil" stroke-width="1.6"
          style="fill:#8fb083;fill-opacity:.55"/>
  <text x="276" y="-192" text-anchor="end" font-family="Consolas,monospace"
        font-size="15" fill="#8a7d64">index.html</text>
  <line x1="-150" y1="-178" x2="300" y2="-178" class="pencil hatch"/>

  <!-- 代码：一个章、两个数字 -->
  <text x="-118" y="-140" font-family="Consolas,monospace" font-size="19"
        fill="#5a4f3c">&lt;h1 class="clip"&gt;</text>
  <text x="-96" y="-106" font-family="Consolas,monospace" font-size="19"
        fill="#423a2e">data-start="2"</text>
  <line x1="-96" y1="-94" x2="92" y2="-94" class="pencil" stroke-width="1.8"/>
  <text x="-96" y="-70" font-family="Consolas,monospace" font-size="19"
        fill="#423a2e">data-duration="4"</text>
  <line x1="-96" y1="-58" x2="114" y2="-58" class="pencil" stroke-width="1.8"/>
  <text x="-118" y="-30" font-family="Consolas,monospace" font-size="19"
        fill="#7a6f58" class="pencil hatch">我的第一个片段&lt;/h1&gt;</text>

  <!-- ===== 令箭：标签 → 时间轴 ===== -->
  <line x1="312" y1="-60" x2="392" y2="-60" class="pencil" stroke-width="2.6"/>
  <path class="pencil" stroke-width="2.6" d="M 372 -78 L 402 -60 L 372 -42"/>

  <!-- ===== 时间轴 x=420..820，轴线 y=-60 ===== -->
  <line x1="420" y1="-60" x2="820" y2="-60" class="pencil" stroke-width="2.6"/>
  <!-- 端帽 0 / 10 -->
  <line x1="420" y1="-74" x2="420" y2="-46" class="pencil" stroke-width="2.2"/>
  <line x1="820" y1="-74" x2="820" y2="-46" class="pencil" stroke-width="2.2"/>
  <!-- 2–6 高亮段：第二秒进来，第六秒走 -->
  <rect x="520" y="-72" width="180" height="24" rx="5" class="pencil"
        stroke-width="2.2" style="fill:#d8b865;fill-opacity:.22"/>
  <line x1="520" y1="-80" x2="520" y2="-40" class="pencil" stroke-width="2.2"/>
  <line x1="700" y1="-80" x2="700" y2="-40" class="pencil" stroke-width="2.2"/>
  <text x="610" y="-92" text-anchor="middle" font-family="KaiTi,serif"
        font-size="18" fill="#5a4f3c">第二秒进 · 第六秒走</text>
  <!-- 刻度数字 -->
  <g font-family="Consolas,monospace" font-size="16" fill="#7a6f58"
     class="pencil hatch" text-anchor="middle">
    <text x="420" y="-26">0</text>
    <text x="520" y="-26">2</text>
    <text x="700" y="-26">6</text>
    <text x="820" y="-26">10</text>
  </g>
  </g>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="BUILT FOR AGENTS · No.03",
    title1="时间写在哪？",
    title2="标签上。",
    seal_cols=[["时"]],
    dateline="HyperFrames 教程 · 第 03 集",
    dateline_en="WRITE TIME ON TAGS",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="hf-03 封面",
    scene_comment="素描主视觉：带 data-start/data-duration 的标签卡 → 时间轴 2–6 段",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
