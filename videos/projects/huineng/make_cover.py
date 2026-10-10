# -*- coding: utf-8 -*-
"""慧能 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架在 videopipe.cover；本文件只保留慧能独有的：
主视觉「擦镜 vs 空壁」（神秀渐修／慧能本来无一物）、
两偈对比金色制图、文字内容。用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover
from videopipe.cover import RULER_LEFT, BOX_RIGHT

HERE = Path(__file__).resolve().parent

# 本片布局数值（结构同 damo）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="78%", wash_y="50%", wash_alpha=".14",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=165, t2_mtop=14,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=80, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层：两偈对比（渐 vs 顿）为本片独有
BLUEPRINT_SVG = """  <!-- 左框：神秀 · 渐（框 300..500） -->
  <rect class="bp bp-line" x="300" y="746" width="200" height="80"/>
  <g class="bp bp-dim">
    <line x1="286" y1="746" x2="314" y2="746"/>
    <line x1="486" y1="746" x2="514" y2="746"/>
    <line x1="300" y1="732" x2="300" y2="760"/>
    <line x1="500" y1="732" x2="500" y2="760"/>
  </g>
  <circle class="bp-dot" cx="400" cy="786" r="7"/>

  <!-- VS 令箭：左框 → 右框 -->
  <line class="bp bp-line" x1="522" y1="786" x2="758" y2="786"/>
  <path class="bp bp-line" d="M 538 774 L 510 786 L 538 798"/>
  <path class="bp bp-line" d="M 742 774 L 770 786 L 742 798"/>
  <text x="612" y="770" fill="#a97d2b" font-size="26"
        font-family="Consolas,monospace" letter-spacing="2">VS</text>

  <!-- 右框：慧能 · 顿（框 780..980） -->
  <rect class="bp bp-line" x="780" y="746" width="200" height="80"/>
  <g class="bp bp-dim">
    <line x1="766" y1="746" x2="794" y2="746"/>
    <line x1="966" y1="746" x2="994" y2="746"/>
    <line x1="780" y1="732" x2="780" y2="760"/>
    <line x1="980" y1="732" x2="980" y2="760"/>
  </g>
  <circle class="bp-dot" cx="880" cy="786" r="7"/>

  <!-- 标签在框上方 y=716 -->
  <text x="322" y="716" fill="#a97d2b" font-size="26"
        font-family="KaiTi,serif" letter-spacing="2">神秀 · 渐</text>
  <text x="802" y="716" fill="#a97d2b" font-size="26"
        font-family="KaiTi,serif" letter-spacing="2">慧能 · 顿</text>

  <!-- 围绕空壁的 construction 圆弧（右上，中心 1648,400，只画上半与右侧） -->
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

# 素描主视觉 SVG 内层：擦镜 vs 空壁，基点 1430,610
SCENE_SVG = """  <g transform="translate(1430,610)">
  <!-- 地面 -->
  <line x1="-360" y1="176" x2="360" y2="176" class="pencil" stroke-width="2.6"/>
  <g class="pencil hatch">
    <path d="M -330 176 l -14 14"/><path d="M -60 176 l -14 14"/>
    <path d="M 60 176 l -14 14"/><path d="M 330 176 l -14 14"/>
  </g>

  <!-- ===== 左：立架铜镜（神秀 · 擦镜） ===== -->
  <!-- 镜架斜撑＋横座 -->
  <path class="pencil" stroke-width="2.4" d="M -210 32 L -300 176"/>
  <path class="pencil" stroke-width="2.4" d="M -210 32 L -120 176"/>
  <line class="pencil" stroke-width="3" x1="-308" y1="176" x2="-112" y2="176"/>

  <!-- 镜框外圆＋乳钉纹 -->
  <circle cx="-210" cy="-95" r="131" class="pencil" stroke-width="2.6"
          style="fill:#f3ead6"/>
  <g class="pencil hatch">
    <line x1="-210" y1="-242" x2="-210" y2="-228"/>
    <line x1="-210" y1="38" x2="-210" y2="52"/>
    <line x1="-357" y1="-95" x2="-343" y2="-95"/>
    <line x1="-77" y1="-95" x2="-63" y2="-95"/>
    <line x1="-314" y1="-199" x2="-303" y2="-188"/>
    <line x1="-117" y1="2" x2="-106" y2="13"/>
    <line x1="-314" y1="9" x2="-303" y2="-2"/>
    <line x1="-117" y1="-192" x2="-106" y2="-203"/>
  </g>

  <!-- 镜面 -->
  <circle cx="-210" cy="-95" r="116" class="pencil" stroke-width="2"
          style="fill:#faf4e4"/>

  <!-- 镜面擦拭动势痕（三道渐开弧） -->
  <g class="pencil hatch">
    <path d="M -250 -140 A 60 60 0 0 1 -172 -62"/>
    <path d="M -262 -124 A 76 76 0 0 1 -160 -58"/>
    <path d="M -244 -44 A 88 88 0 0 1 -122 -128"/>
  </g>

  <!-- 手臂（从右侧伸入镜面）＋布团 -->
  <path class="pencil" stroke-width="9" stroke-linecap="round" fill="none"
        d="M 40 -28 C -10 -58,-72 -82,-140 -112"/>
  <path class="pencil hatch" d="M 36 -44 C -16 -70,-70 -96,-132 -126"/>
  <!-- 手指 -->
  <g class="pencil" stroke-width="2.2">
    <line x1="-136" y1="-120" x2="-150" y2="-130"/>
    <line x1="-140" y1="-110" x2="-156" y2="-116"/>
    <line x1="-142" y1="-100" x2="-158" y2="-102"/>
  </g>
  <!-- 布团（碎布，边缘不规则） -->
  <path class="pencil" stroke-width="2.2" style="fill:#e7dabb"
        d="M -192 -134 l 14 -8 18 3 10 12 -6 14 -18 5 -16 -7 -6 -12 Z"/>
  <g class="pencil hatch">
    <path d="M -184 -128 l 8 10"/><path d="M -170 -136 l 2 14"/>
    <path d="M -188 -116 l 12 -2"/>
  </g>
  <!-- 动势短线 -->
  <g class="pencil hatch">
    <path d="M -292 -184 l -14 -10"/><path d="M -286 -168 l -18 -4"/>
  </g>

  <!-- ===== 右：空壁（慧能 · 本来无一物） ===== -->
  <rect x="70" y="-250" width="270" height="390" rx="4"
        class="pencil" stroke-width="2.6" style="fill:#ece2cb;fill-opacity:.55"/>
  <!-- 墙头檐线＋三笔瓦弧 -->
  <line class="pencil" stroke-width="2.6" x1="60" y1="-250" x2="350" y2="-250"/>
  <g class="pencil hatch">
    <path d="M 92 -262 q 12 -10 24 0"/><path d="M 196 -262 q 12 -10 24 0"/>
    <path d="M 300 -262 q 12 -10 24 0"/>
  </g>
  <!-- 壁面仅两笔淡裂纹 -->
  <g class="pencil hatch">
    <path d="M 150 -104 l -10 24 l 8 20 l -6 22"/>
    <path d="M 262 36 l 10 18 l -8 22"/>
  </g>

  <!-- 墙根斜靠一枝毛笔 -->
  <line class="pencil" stroke-width="4" x1="118" y1="172" x2="300" y2="42"/>
  <path class="pencil" stroke-width="2.2" style="fill:#e7dabb"
        d="M 110 176 l 20 -4 -2 -14 -18 6 Z"/>
  </g>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="FIELD NOTE · 两首偈 · No.05",
    title1="时时勤拂拭，",
    title2="本来无一物。",
    seal_cols=[["能"]],
    dateline="中国佛教史 · 短视频第 05 篇",
    dateline_en="FIELD NOTE No.05 · TWO GATHAS",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="慧能封面",
    scene_comment="素描主视觉：擦镜（渐修）vs 空壁（本来无一物）",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
