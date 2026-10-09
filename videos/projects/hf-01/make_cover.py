# -*- coding: utf-8 -*-
"""hf-01 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留本集独有的：布局数值、浏览器窗口(HTML)→胶片(视频)主视觉、
HTML→SEEK→MP4 金色确定性流水线、文字内容。用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover
from videopipe.cover import RULER_LEFT, BOX_RIGHT

HERE = Path(__file__).resolve().parent

# 本集布局数值（结构同 damo，数值沿用，文字数相近）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="78%", wash_y="50%", wash_alpha=".14",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=200, t2_mtop=10,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=80, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层（全局坐标）：HTML→SEEK→MP4 确定性流水线为本集独有
BLUEPRINT_SVG = """  <!-- 主流程金线：浏览器中心 1080 → 胶片中心 1630，y=835 -->
  <line class="bp bp-line" x1="1092" y1="835" x2="1343" y2="835"/>
  <line class="bp bp-line" x1="1367" y1="835" x2="1618" y2="835"/>
  <path class="bp bp-line" d="M 1329 823 L 1355 835 L 1329 847"/>
  <path class="bp bp-line" d="M 1604 823 L 1630 835 L 1604 847"/>
  <circle class="bp-dot" cx="1080" cy="835" r="6"/>
  <circle class="bp-dot" cx="1355" cy="835" r="6"/>
  <circle class="bp-dot" cx="1630" cy="835" r="6"/>

  <!-- 节点标签（上方 y=800） -->
  <text x="1080" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">HTML</text>
  <text x="1355" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">SEEK</text>
  <text x="1630" y="798" fill="#a97d2b" font-size="20" text-anchor="middle"
        font-family="Consolas,monospace" letter-spacing="2">MP4</text>

  <!-- 罩在胶片上方的 construction 虚线半圆弧（中心 1630,360） -->
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

# 素描主视觉 SVG 内层：浏览器窗口(HTML) → 胶片(视频)，基点 1010,600
SCENE_SVG = """  <g transform="translate(1010,600)">
  <!-- ===== 浏览器窗口（HTML） x=-120..260，y=-230..110 ===== -->
  <rect x="-120" y="-230" width="380" height="340" rx="14" class="pencil"
        stroke-width="2.8" style="fill:#fbf6ea"/>
  <!-- 顶栏三圆点 -->
  <circle cx="-90" cy="-207" r="8" class="pencil" stroke-width="1.8"
          style="fill:#d98b7a;fill-opacity:.55"/>
  <circle cx="-58" cy="-207" r="8" class="pencil" stroke-width="1.8"
          style="fill:#dcc07a;fill-opacity:.55"/>
  <circle cx="-26" cy="-207" r="8" class="pencil" stroke-width="1.8"
          style="fill:#8fb083;fill-opacity:.55"/>
  <!-- 地址栏 -->
  <rect x="8" y="-222" width="226" height="28" rx="6" class="pencil hatch"
        style="fill:#efe7d4"/>
  <line x1="-120" y1="-182" x2="260" y2="-182" class="pencil hatch"/>

  <!-- 代码内容 -->
  <text x="-92" y="-138" font-family="Consolas,monospace" font-size="21"
        fill="#5a4f3c">&lt;/&gt; index.html</text>
  <g class="pencil hatch">
    <line x1="-92" y1="-106" x2="118" y2="-106"/>
    <line x1="-60" y1="-70" x2="180" y2="-70"/>
    <line x1="-60" y1="-34" x2="72" y2="-34"/>
    <line x1="-92" y1="2" x2="150" y2="2"/>
    <line x1="-60" y1="38" x2="104" y2="38"/>
    <line x1="-92" y1="74" x2="58" y2="74"/>
  </g>

  <!-- ===== 令箭：浏览器 → 胶片 ===== -->
  <line x1="272" y1="-60" x2="392" y2="-60" class="pencil" stroke-width="2.6"/>
  <path class="pencil" stroke-width="2.6" d="M 372 -78 L 402 -60 L 372 -42"/>

  <!-- ===== 胶片框（视频） x=420..820，y=-210..90 ===== -->
  <rect x="420" y="-210" width="400" height="300" rx="10" class="pencil"
        stroke-width="2.8" style="fill:#f3ead8"/>
  <!-- 上下齿孔各 7 个 -->
  <g class="pencil hatch" style="fill:#e7dcc2">
    <rect x="440" y="-196" width="22" height="18" rx="3"/>
    <rect x="494" y="-196" width="22" height="18" rx="3"/>
    <rect x="548" y="-196" width="22" height="18" rx="3"/>
    <rect x="602" y="-196" width="22" height="18" rx="3"/>
    <rect x="656" y="-196" width="22" height="18" rx="3"/>
    <rect x="710" y="-196" width="22" height="18" rx="3"/>
    <rect x="764" y="-196" width="22" height="18" rx="3"/>
    <rect x="440" y="58" width="22" height="18" rx="3"/>
    <rect x="494" y="58" width="22" height="18" rx="3"/>
    <rect x="548" y="58" width="22" height="18" rx="3"/>
    <rect x="602" y="58" width="22" height="18" rx="3"/>
    <rect x="656" y="58" width="22" height="18" rx="3"/>
    <rect x="710" y="58" width="22" height="18" rx="3"/>
    <rect x="764" y="58" width="22" height="18" rx="3"/>
  </g>
  <!-- 播放三角 -->
  <path d="M 598 -96 L 598 -24 L 668 -60 Z" class="pencil" stroke-width="2.4"
        style="fill:#423a2e;fill-opacity:.14"/>
  </g>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="BUILT FOR AGENTS · No.01",
    title1="写 HTML，",
    title2="出视频。",
    seal_cols=[["码"]],
    dateline="HyperFrames 教程 · 第 01 集",
    dateline_en="WRITE HTML · RENDER VIDEO",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="hf-01 封面",
    scene_comment="素描主视觉：浏览器(HTML)→胶片(视频)",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
