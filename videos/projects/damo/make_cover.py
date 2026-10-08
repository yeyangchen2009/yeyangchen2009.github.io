# -*- coding: utf-8 -*-
"""达摩 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留达摩独有的：布局数值、面壁老僧背影＋墙上影子＋一苇主视觉、
建康→长江→嵩山金色行程制图、文字内容。用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover
from videopipe.cover import RULER_LEFT, BOX_RIGHT

HERE = Path(__file__).resolve().parent

# 本片布局数值（结构同 liangwudi，数值沿用，文字数相近）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="78%", wash_y="50%", wash_alpha=".14",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=200, t2_mtop=10,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=80, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层：建康→长江→嵩山行程线为本片独有
BLUEPRINT_SVG = """  <!-- 节点① 皇宫（建康）中心 260,760 -->
  <g>
    <path class="bp bp-line" d="M 226 770 L 260 742 L 294 770"/>
    <line class="bp bp-line" x1="234" y1="776" x2="286" y2="776"/>
    <circle class="bp-dot" cx="260" cy="792" r="7"/>
  </g>

  <!-- 令箭：皇宫 → 长江 → 嵩山（水平） -->
  <line class="bp bp-line" x1="284" y1="786" x2="566" y2="786"/>
  <path class="bp bp-line" d="M 524 774 L 576 786 L 524 798"/>

  <!-- 节点② 长江（江浪两道，节点下方）中心 640,786 -->
  <g class="bp bp-dim">
    <path d="M 608 812 q 11 -12 22 0 q 11 12 22 0"/>
    <path d="M 608 832 q 11 -12 22 0 q 11 12 22 0"/>
  </g>
  <circle class="bp-dot" cx="640" cy="786" r="7"/>

  <line class="bp bp-line" x1="662" y1="786" x2="944" y2="786"/>
  <path class="bp bp-line" d="M 902 774 L 954 786 L 902 798"/>

  <!-- 节点③ 嵩山（三峰）中心 1020,760 -->
  <g>
    <path class="bp bp-line" d="M 982 786 L 1010 738 L 1036 786"/>
    <path class="bp bp-line" d="M 1010 786 L 1036 750 L 1060 786"/>
    <circle class="bp-dot" cx="1020" cy="792" r="7"/>
  </g>

  <!-- 标签统一在节点上方 y=700，避开底部日期线 -->
  <text x="212" y="704" fill="#a97d2b" font-size="26"
        font-family="KaiTi,serif" letter-spacing="2">建康</text>
  <text x="600" y="704" fill="#a97d2b" font-size="26"
        font-family="KaiTi,serif" letter-spacing="2">长江</text>
  <text x="984" y="704" fill="#a97d2b" font-size="26"
        font-family="KaiTi,serif" letter-spacing="2">嵩山</text>

  <!-- 围绕面壁石壁的 construction 圆弧（右上，中心 1648,400，只画上半与右侧） -->
  <g>
    <path class="bp bp-thin" stroke-dasharray="9 8"
          d="M 1360 400 A 288 288 0 0 1 1936 400"/>
    <path class="bp bp-dim"
          d="M 1320 400 A 328 328 0 0 1 1976 400"/>
    <path class="bp bp-line" d="M 1648 108 A 292 292 0 0 1 1932 356"/>
    <g class="bp bp-dim">
      <line x1="1640" y1="124" x2="1656" y2="124"/>
      <line x1="1922" y1="342" x2="1940" y2="356"/>
      <line x1="1760" y1="140" x2="1772" y2="156"/>
    </g>
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

# 素描主视觉 SVG 内层：面壁老僧背影＋墙上影子＋一苇，基点 1430,610
SCENE_SVG = """  <g transform="translate(1430,610)">
  <!-- 石洞拱形洞壁（背景） -->
  <path class="pencil hatch"
        d="M -348 158 L -348 -168 Q -348 -306 -200 -316 L 200 -316 Q 348 -306 348 -168 L 348 158"/>
  <g class="pencil hatch">
    <path d="M -320 -120 l -20 40"/><path d="M 300 -140 l 20 44"/>
    <path d="M -120 -286 l 26 -14"/><path d="M 150 -286 l 26 -14"/>
  </g>

  <!-- 地面 -->
  <line x1="-360" y1="176" x2="360" y2="176" class="pencil" stroke-width="2.6"/>
  <g class="pencil hatch">
    <path d="M -300 176 l -14 14"/><path d="M 60 176 l -14 14"/>
    <path d="M 250 176 l -14 14"/>
  </g>

  <!-- ===== 面壁石壁（右侧竖墙） ===== -->
  <rect x="200" y="-252" width="126" height="428" rx="6"
        class="pencil" stroke-width="2.6" style="fill:#ece2cb;fill-opacity:.55"/>
  <g class="pencil hatch">
    <path d="M 224 -230 l 0 60"/><path d="M 262 -210 l 0 70"/>
    <path d="M 296 -236 l 0 64"/><path d="M 220 60 l 0 70"/>
    <path d="M 280 40 l 0 80"/>
  </g>

  <!-- 老僧投在石壁上的影子（头＋肩背） -->
  <ellipse cx="172" cy="-120" rx="30" ry="36"
           fill="#3a3125" fill-opacity=".07" class="pencil hatch"/>
  <path d="M 126 -44 Q 172 -86 218 -44 L 218 -14 L 126 -14 Z"
        fill="#3a3125" fill-opacity=".07" class="pencil hatch"/>

  <!-- ===== 盘腿老僧背影，身体中线 x=-60，面朝右墙 ===== -->
  <!-- 盘腿底座 -->
  <path class="pencil" stroke-width="2.8" style="fill:#ece2cb"
        d="M -236 158 C -252 92, -150 58, -60 88 C 30 58, 132 92, 116 158 Z"/>
  <g class="pencil hatch">
    <path d="M -180 120 q 60 30 120 8"/><path d="M -20 128 q 60 20 104 -6"/>
  </g>

  <!-- 躯干袈裟（背影） -->
  <path class="pencil" stroke-width="2.8" style="fill:#f3ead6"
        d="M -152 -72
           C -162 -18, -152 62, -118 124
           L -2 124
           C 32 62, 42 -18, 32 -72
           Q -60 -98 -152 -72 Z"/>
  <g class="pencil hatch">
    <path d="M -60 -64 q -10 60 0 120"/><path d="M -120 -40 q -6 70 -6 120"/>
    <path d="M 0 -40 q 6 70 6 120"/>
  </g>

  <!-- 双臂（背影，垂落膝上） -->
  <path class="pencil hatch" d="M -140 -60 C -152 2, -142 62, -108 106"/>
  <path class="pencil hatch" d="M 20 -60 C 32 2, 22 62, -12 106"/>

  <!-- 肩背弧＋光头（后脑勺） -->
  <path class="pencil" stroke-width="2.8" d="M -152 -72 Q -60 -152 32 -72"/>
  <circle cx="-60" cy="-120" r="46" class="pencil" stroke-width="2.8"
          style="fill:#f7f0de"/>

  <!-- ===== 一苇（左后侧斜立） ===== -->
  <line x1="-250" y1="156" x2="-308" y2="-80" class="pencil" stroke-width="3"/>
  <g>
    <ellipse cx="-314" cy="-100" rx="9" ry="26" class="pencil" stroke-width="2"
             style="fill:#ddcfa6" transform="rotate(-12 -314 -100)"/>
    <path class="pencil hatch" d="M -300 -40 q -34 6 -44 -24"/>
    <path class="pencil hatch" d="M -288 10 q -30 10 -46 -14"/>
  </g>
  </g>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="FIELD NOTE · 一次判零 · No.03",
    title1="皇帝攒满分，",
    title2="达摩判零。",
    seal_cols=[["达"]],
    dateline="中国佛教史 · 短视频第 03 篇",
    dateline_en="FIELD NOTE No.03 · SCORE ZERO",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="达摩封面",
    scene_comment="素描主视觉：面壁老僧＋墙上影子＋一苇",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
