# -*- coding: utf-8 -*-
"""梁武帝 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留梁武帝独有的：布局数值、青菜豆腐僧碗主视觉 SVG、
皇宫→碗金色令箭 SVG、文字内容。用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover
from videopipe.cover import RULER_LEFT, BOX_RIGHT

HERE = Path(__file__).resolve().parent

# 本片布局数值（结构同 zbj，数值按本稿视觉调）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="76%", wash_y="52%", wash_alpha=".14",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=200, t2_mtop=10,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=80, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层：皇宫→僧碗令箭为本片独有，标尺/方框复用公共件
BLUEPRINT_SVG = """  <!-- 皇宫节点（建康·同泰寺） -->
  <g>
    <!-- 小宫殿屋顶简形，中心 478,718 -->
    <path class="bp bp-line" d="M 444 728 L 478 700 L 512 728"/>
    <line class="bp bp-line" x1="452" y1="734" x2="504" y2="734"/>
    <line class="bp bp-dim" x1="462" y1="742" x2="462" y2="752"/>
    <line class="bp bp-dim" x1="494" y1="742" x2="494" y2="752"/>
    <circle class="bp-dot" cx="478" cy="758" r="8"/>
  </g>

  <!-- 令箭：皇宫 → 僧碗 -->
  <line class="bp bp-line" x1="500" y1="752" x2="1114" y2="646"/>
  <path class="bp bp-line" d="M 1074 672 L 1128 644 L 1084 622"/>
  <text x="612" y="712" fill="#a97d2b" font-size="30"
        font-family="KaiTi,serif" letter-spacing="3">《断酒肉文》</text>
  <text x="300" y="812" fill="#a97d2b" font-size="26"
        font-family="KaiTi,serif" letter-spacing="2">建康 · 同泰寺</text>

  <!-- 围绕僧碗的 construction 圆弧（右侧，中心 1450,640，只画上半，避开日期线） -->
  <g>
    <path class="bp bp-thin" stroke-dasharray="9 8"
          d="M 1150 640 A 300 300 0 1 1 1750 640"/>
    <path class="bp bp-dim"
          d="M 1098 640 A 352 352 0 1 1 1802 640"/>
    <path class="bp bp-line" d="M 1450 268 A 372 372 0 0 1 1812 566"/>
    <g class="bp bp-dim">
      <line x1="1442" y1="284" x2="1458" y2="284"/>
      <line x1="1796" y1="552" x2="1812" y2="562"/>
      <line x1="1560" y1="300" x2="1570" y2="316"/>
      <line x1="1700" y1="392" x2="1712" y2="408"/>
    </g>
  </g>

  <!-- 左上十字准星 -->
  <g>
    <line class="bp bp-line" x1="1230" y1="110" x2="1730" y2="110"/>
    <line class="bp bp-line" x1="1480" y1="60" x2="1480" y2="170"/>
    <circle class="bp bp-dim" cx="1480" cy="110" r="14"/>
    <circle class="bp-dot" cx="1480" cy="110" r="3.2"/>
  </g>

%s

%s""" % (RULER_LEFT, BOX_RIGHT)

# 素描主视觉 SVG 内层：青菜豆腐僧碗＋木筷，碗心 1450,640
SCENE_SVG = """  <!-- 碗下投影 -->
  <ellipse cx="1450" cy="852" rx="318" ry="24" fill="#7a5e30" fill-opacity=".14"/>

  <!-- ===== 僧碗整体，基点 1450,640 ===== -->
  <g transform="translate(1450,640)">

    <!-- 碗腹（白釉淡彩） -->
    <path class="pencil" stroke-width="2.8" style="fill:#f0e7d2;fill-opacity:.9"
          d="M -330 -100
             C -342 60, -262 172, 0 184
             C 262 172, 342 60, 330 -100"/>
    <!-- 碗腹两侧排线（瓷弧质感） -->
    <g class="pencil hatch">
      <path d="M -300 -52 q -20 96 24 158"/>
      <path d="M 300 -52 q 20 96 -24 158"/>
      <path d="M -250 30 q -6 70 30 118"/>
      <path d="M 250 30 q 6 70 -30 118"/>
    </g>
    <!-- 圈足 -->
    <path class="pencil" stroke-width="2.4" d="M -86 168 Q 0 196 86 168"/>
    <line class="pencil" stroke-width="2.4" x1="-70" y1="176" x2="70" y2="176"/>

    <!-- ===== 碗内食物（口沿以内） ===== -->
    <!-- 豆腐两块（再加大、填色明确） -->
    <rect x="-300" y="-162" width="132" height="86" rx="10"
          class="pencil" stroke-width="2.6" style="fill:#faf5e5"/>
    <rect x="174" y="-154" width="126" height="80" rx="10"
          class="pencil" stroke-width="2.6" style="fill:#faf5e5"/>
    <g class="pencil hatch">
      <path d="M -278 -138 l 30 -12"/><path d="M 196 -130 l 28 -11"/>
    </g>
    <!-- 青菜三丛（大叶片铺满碗口、绿色加深） -->
    <g class="pencil" stroke-width="2.8" style="fill:#6f9b34;fill-opacity:.95">
      <path d="M -170 -92
               q -52 -40 -16 -88 q 48 6 64 50 q 12 38 -20 58 Z"/>
      <path d="M -30 -100
               q -48 -54 12 -92 q 54 12 54 62 q -2 42 -34 54 Z"/>
      <path d="M 96 -90
               q -40 -38 4 -78 q 40 16 34 60 q -6 34 -34 38 Z"/>
    </g>
    <g class="pencil hatch">
      <path d="M -146 -122 q 14 30 -6 54"/>
      <path d="M 18 -134 q 4 32 -16 54"/>
      <path d="M 112 -118 q -2 24 -18 36"/>
    </g>

    <!-- 碗口椭圆（口沿，不填色以免淡化食物） -->
    <ellipse cx="0" cy="-100" rx="330" ry="58"
             class="pencil" stroke-width="2.8" fill="none"/>
    <!-- 近侧口沿加深一道，遮住食物底边 -->
    <path class="pencil" stroke-width="3.2" d="M -330 -100 Q 0 -38 330 -100"/>

    <!-- ===== 木筷（斜搭右上碗口） ===== -->
    <g>
      <line x1="210" y1="-330" x2="-40" y2="-86" stroke="#8a5a2b" stroke-width="8" stroke-linecap="round"/>
      <line x1="228" y1="-322" x2="-22" y2="-78" stroke="#8a5a2b" stroke-width="8" stroke-linecap="round"/>
      <line x1="210" y1="-330" x2="-40" y2="-86" class="pencil hatch"/>
      <line x1="228" y1="-322" x2="-22" y2="-78" class="pencil hatch"/>
    </g>

    <!-- 热气三道（碗口左上） -->
    <g class="pencil hatch">
      <path d="M -180 -180 q 18 -24 0 -48 q -14 -20 2 -42"/>
      <path d="M -120 -172 q 16 -22 0 -44 q -12 -18 2 -38"/>
    </g>
  </g>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="FIELD NOTE · 全局配置变更 · No.02",
    title1="让和尚吃素的，",
    title2="不是佛祖。",
    seal_cols=[["梁"]],
    dateline="中国佛教史 · 短视频第 02 篇",
    dateline_en="FIELD NOTE No.02 · GLOBAL CONFIG CHANGE",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="梁武帝封面",
    scene_comment="素描主视觉：青菜豆腐僧碗",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
