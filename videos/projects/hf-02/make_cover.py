# -*- coding: utf-8 -*-
"""hf-02 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留本集独有的：布局数值、终端(init)→项目目录树 铅笔素描主视觉、
INIT→FILES→RULES 金色制图、文字内容。用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover
from videopipe.cover import RULER_LEFT, BOX_RIGHT

HERE = Path(__file__).resolve().parent

# 本集布局数值（结构同 hf-01，文字数相近）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="78%", wash_y="50%", wash_alpha=".14",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=200, t2_mtop=10,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=80, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层（全局坐标）：INIT→FILES→RULES 为本集独有
BLUEPRINT_SVG = """  <!-- 主流程金线 y=835：1040 init → 1330 files → 1600 rules -->
  <line class="bp bp-line" x1="1052" y1="835" x2="1317" y2="835"/>
  <line class="bp bp-line" x1="1343" y1="835" x2="1587" y2="835"/>
  <path class="bp bp-line" d="M 1301 823 L 1327 835 L 1301 847"/>
  <path class="bp bp-line" d="M 1571 823 L 1597 835 L 1571 847"/>
  <circle class="bp-dot" cx="1040" cy="835" r="6"/>
  <circle class="bp-dot" cx="1330" cy="835" r="6"/>
  <circle class="bp-dot" cx="1600" cy="835" r="6"/>

  <!-- 节点标签（上方 y=798） -->
  <text x="1040" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">INIT</text>
  <text x="1330" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">FILES</text>
  <text x="1600" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">RULES</text>

  <!-- 罩在文件夹上方的 construction 虚线半圆弧（中心 1570,380，半宽 250） -->
  <path class="bp bp-thin" stroke-dasharray="9 8"
        d="M 1320 380 A 250 250 0 0 1 1820 380"/>
  <path class="bp bp-dim" d="M 1304 380 A 266 266 0 0 1 1836 380"/>
  <g class="bp bp-dim">
    <line x1="1401" y1="175" x2="1413" y2="165"/>
    <line x1="1727" y1="165" x2="1739" y2="175"/>
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

# 素描主视觉 SVG 内层：终端 init → 项目目录树，基点 1010,600
SCENE_SVG = """  <g transform="translate(1010,600)">
  <!-- ===== 终端窗口 x=-150..210，y=-220..80 ===== -->
  <rect x="-150" y="-220" width="360" height="300" rx="12" class="pencil"
        stroke-width="2.8" style="fill:#fbf6ea"/>
  <!-- 标题栏三圆点 -->
  <circle cx="-124" cy="-199" r="6" class="pencil" stroke-width="1.6"
          style="fill:#d98b7a;fill-opacity:.55"/>
  <circle cx="-100" cy="-199" r="6" class="pencil" stroke-width="1.6"
          style="fill:#dcc07a;fill-opacity:.55"/>
  <circle cx="-76" cy="-199" r="6" class="pencil" stroke-width="1.6"
          style="fill:#8fb083;fill-opacity:.55"/>
  <text x="186" y="-192" text-anchor="end" font-family="Consolas,monospace"
        font-size="15" fill="#8a7d64">zsh</text>
  <line x1="-150" y1="-178" x2="210" y2="-178" class="pencil hatch"/>

  <!-- 终端文字 -->
  <text x="-122" y="-140" font-family="Consolas,monospace" font-size="19"
        fill="#5a4f3c">$ hyperframes init demo</text>
  <g font-family="Consolas,monospace" font-size="16" fill="#7a6f58"
     class="pencil hatch">
    <text x="-122" y="-102">&gt; scaffolding...</text>
    <text x="-122" y="-70">&gt; 6 files created</text>
    <text x="-122" y="-38">&gt; ready</text>
  </g>
  <!-- 光标 -->
  <line x1="-122" y1="-6" x2="-104" y2="-6" class="pencil" stroke-width="2"/>

  <!-- ===== 令箭：终端 → 文件夹 ===== -->
  <line x1="222" y1="-70" x2="298" y2="-70" class="pencil" stroke-width="2.6"/>
  <path class="pencil" stroke-width="2.6" d="M 280 -86 L 310 -70 L 280 -54"/>

  <!-- ===== 文件夹 + 目录树 x=310..810，y=-208..100 ===== -->
  <!-- 文件夹耳 -->
  <path class="pencil" stroke-width="2.4" style="fill:#ecd9b0"
        d="M 310 -180 L 310 -208 L 392 -208 L 410 -180 Z"/>
  <!-- 文件夹主体 -->
  <rect x="310" y="-180" width="500" height="280" rx="8" class="pencil"
        stroke-width="2.8" style="fill:#f3ead8"/>

  <!-- 目录树 -->
  <text x="342" y="-140" font-family="Consolas,monospace" font-size="21"
        fill="#5a4f3c">demo/</text>
  <g font-family="Consolas,monospace" font-size="19" fill="#74694f"
     class="pencil hatch">
    <text x="342" y="-104">|-- package.json</text>
    <text x="342" y="-68">|-- meta.json</text>
    <text x="342" y="-32">|-- hyperframes.json</text>
    <text x="342" y="4">|-- CLAUDE.md</text>
    <text x="342" y="40">|-- AGENTS.md</text>
  </g>
  <!-- 主角 index.html：深色＋下划线 -->
  <text x="342" y="76" font-family="Consolas,monospace" font-size="19"
        fill="#423a2e">\\-- index.html</text>
  <line x1="386" y1="86" x2="512" y2="86" class="pencil" stroke-width="1.8"/>
  </g>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="BUILT FOR AGENTS · No.02",
    title1="一条命令，",
    title2="立规矩。",
    seal_cols=[["构"]],
    dateline="HyperFrames 教程 · 第 02 集",
    dateline_en="INIT IN 30 SECONDS",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="hf-02 封面",
    scene_comment="素描主视觉：终端 init → 项目目录树",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
