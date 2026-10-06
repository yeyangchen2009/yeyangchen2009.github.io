# -*- coding: utf-8 -*-
"""猪八戒 · 封面生成器（宏观阿尔法风格，紧凑 CSS 版）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留猪八戒独有的：布局数值、八戒扛耙主视觉 SVG、金色制图 SVG、
文字内容。用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover

HERE = Path(__file__).resolve().parent

# 本片布局数值（结构同两片，数值取自 zbj-cover.html）
LAYOUT = CoverLayout(
    wash_rw=1100, wash_x="80%", wash_y="45%", wash_alpha=".15",
    title_top=268, title_width=1120,
    t1_size=84, t2_size=200, t2_mtop=10,
    subnote_mode="bottom", subnote_pos=96,
    seal_size=62, seal_lineheight=None, seal_gap="4px",
    tag_top=150,
)

# 金色工程制图 SVG 内层（坐标围绕猪头 1530,430）
BLUEPRINT_SVG = """  <!-- 左上十字准星 -->
  <g>
    <line class="bp bp-line" x1="60" y1="192" x2="560" y2="192"/>
    <line class="bp bp-line" x1="240" y1="100" x2="240" y2="460"/>
    <circle class="bp bp-dim" cx="240" cy="192" r="15"/>
    <circle class="bp-dot" cx="240" cy="192" r="3.4"/>
    <g class="bp bp-dim">
      <line x1="100" y1="184" x2="100" y2="200"/><line x1="140" y1="184" x2="140" y2="200"/>
      <line x1="180" y1="186" x2="180" y2="198"/><line x1="300" y1="186" x2="300" y2="198"/>
      <line x1="340" y1="184" x2="340" y2="200"/><line x1="380" y1="184" x2="380" y2="200"/>
      <line x1="232" y1="132" x2="248" y2="132"/><line x1="232" y1="162" x2="248" y2="162"/>
      <line x1="232" y1="222" x2="248" y2="222"/><line x1="232" y1="252" x2="248" y2="252"/>
    </g>
  </g>

  <!-- 围绕猪头的大 construction 圆弧（右上，中心 1530,430） -->
  <g>
    <circle class="bp bp-thin" cx="1530" cy="430" r="262" stroke-dasharray="9 8"/>
    <circle class="bp bp-dim" cx="1530" cy="430" r="330"/>
    <path class="bp bp-line" d="M 1530 66 A 364 364 0 0 1 1876 356"/>
    <g class="bp bp-dim">
      <line x1="1530" y1="56" x2="1530" y2="80"/>
      <line x1="1858" y1="322" x2="1880" y2="338"/>
      <line x1="1640" y1="92" x2="1652" y2="110"/>
      <line x1="1770" y1="152" x2="1782" y2="170"/>
    </g>
    <circle class="bp-dot" cx="1530" cy="430" r="4"/>
    <!-- 水平基准虚线 -->
    <line class="bp bp-thin" x1="560" y1="430" x2="1180" y2="430" stroke-dasharray="10 9"/>
    <line class="bp bp-line" x1="1120" y1="430" x2="1200" y2="430"/>
    <path class="bp bp-line" d="M1188 421 L1206 430 L1188 439"/>
  </g>

  <!-- 左下竖标尺 -->
  <g class="bp bp-dim">
    <line x1="74" y1="760" x2="74" y2="1040"/>
    <line x1="64" y1="790" x2="84" y2="790"/>
    <line x1="68" y1="820" x2="80" y2="820"/>
    <line x1="64" y1="850" x2="84" y2="850"/>
    <line x1="68" y1="880" x2="80" y2="880"/>
    <line x1="64" y1="910" x2="84" y2="910"/>
    <line x1="68" y1="940" x2="80" y2="940"/>
    <line x1="64" y1="970" x2="84" y2="970"/>
    <line x1="68" y1="1000" x2="80" y2="1000"/>
  </g>

  <!-- 右下小方框标注 -->
  <g class="bp bp-dim">
    <rect x="1780" y="930" width="96" height="70"/>
    <line x1="1828" y1="916" x2="1828" y2="930"/>
    <line x1="1828" y1="1000" x2="1828" y2="1016"/>
    <circle class="bp-dot" cx="1828" cy="916" r="3"/>
  </g>

  <!-- 顶部小三角几何 -->
  <g class="bp bp-thin">
    <path d="M 820 80 L 1000 80 L 910 160 Z"/>
    <circle class="bp-dot" cx="820" cy="80" r="3"/><circle class="bp-dot" cx="1000" cy="80" r="3"/>
    <circle class="bp-dot" cx="910" cy="160" r="3"/>
  </g>"""

# 素描主视觉 SVG 内层：猪八戒正面憨笑扛耙
SCENE_SVG = """  <!-- 地面一道 -->
  <path class="pencil" stroke-width="2" opacity=".5"
        d="M 1080 1000 C 1300 976, 1600 980, 1880 968"/>
  <g class="pencil hatch">
    <path d="M1230 992 q 30 12 60 0"/><path d="M1380 984 q 30 10 60 0"/>
    <path d="M1530 980 q 30 9 60 0"/><path d="M1680 974 q 30 8 60 0"/>
  </g>

  <!-- 八戒整体（正面憨笑，扛耙），基点 1530,470 -->
  <g transform="translate(1530,470) scale(1.32)">

    <!-- ===== 九齿钉耙（底层：杆从耙头斜到右肩） ===== -->
    <g>
      <line x1="285" y1="-250" x2="150" y2="196" stroke="#8a5a2b" stroke-width="9" stroke-linecap="round"/>
      <line x1="285" y1="-250" x2="150" y2="196" class="pencil hatch"/>
      <!-- 耙头横杆（垂直于杆方向） -->
      <line x1="226" y1="-258" x2="346" y2="-222" stroke="#8a5a2b" stroke-width="11" stroke-linecap="round"/>
      <!-- 七根齿 -->
      <g stroke="#6e4415" stroke-width="6" stroke-linecap="round">
        <line x1="232" y1="-256" x2="240" y2="-294"/>
        <line x1="250" y1="-251" x2="258" y2="-287"/>
        <line x1="268" y1="-246" x2="276" y2="-280"/>
        <line x1="286" y1="-240" x2="294" y2="-274"/>
        <line x1="304" y1="-235" x2="312" y2="-268"/>
        <line x1="322" y1="-230" x2="330" y2="-262"/>
        <line x1="340" y1="-224" x2="348" y2="-256"/>
      </g>
    </g>

    <!-- ===== 两只大蒲扇耳朵（宽叶下垂，根部被脸遮） ===== -->
    <path class="pencil" stroke-width="2.6" fill="#eccca2" fill-opacity=".55"
          d="M -118 -56
             C -252 -98, -302 16, -272 106
             C -250 170, -164 158, -134 92
             C -112 44, -104 -14, -118 -56 Z"/>
    <path class="pencil" stroke-width="2.6" fill="#eccca2" fill-opacity=".55"
          d="M 118 -56
             C 252 -98, 302 16, 272 106
             C 250 170, 164 158, 134 92
             C 112 44, 104 -14, 118 -56 Z"/>
    <!-- 耳窝：一条短弧＋几笔触（不画长同心弧） -->
    <g class="pencil hatch">
      <path d="M -156 -22 q -48 52 -20 106"/>
      <path d="M -202 44 l -14 10"/><path d="M -214 76 l -12 10"/><path d="M -218 106 l -10 8"/>
      <path d="M 156 -22 q 48 52 20 106"/>
      <path d="M 202 44 l 14 10"/><path d="M 214 76 l 12 10"/><path d="M 218 106 l 10 8"/>
    </g>

    <!-- ===== 脸（大圆胖） ===== -->
    <path class="pencil" stroke-width="2.8" fill="#f0d9b4" fill-opacity=".6"
          d="M -178 -40
             C -188 -152, -112 -208, 0 -202
             C 112 -208, 188 -152, 178 -40
             C 186 82, 122 168, 0 168
             C -122 168, -186 82, -178 -40 Z"/>

    <!-- ===== 僧帽 ===== -->
    <path class="pencil" stroke-width="3" fill="#dcc59a" fill-opacity=".5"
          d="M -116 -182 Q 0 -218 116 -182 Q 108 -156 92 -150 Q 0 -172 -92 -150 Q -108 -156 -116 -182 Z"/>
    <circle cx="0" cy="-226" r="8" fill="#b03426" stroke="#7a2418" stroke-width="1.6"/>

    <!-- 眉毛 -->
    <path class="pencil" stroke-width="3.4" d="M -100 -86 q 26 -10 50 -2"/>
    <path class="pencil" stroke-width="3.4" d="M 50 -88 q 26 -8 50 2"/>

    <!-- 笑眼（弯月） -->
    <path class="pencil" stroke-width="3.2" d="M -96 -56 q 25 16 50 0"/>
    <path class="pencil" stroke-width="3.2" d="M 46 -56 q 25 16 50 0"/>

    <!-- 腮红 -->
    <ellipse cx="-104" cy="64" rx="30" ry="20" fill="#d98a6e" fill-opacity=".32"/>
    <ellipse cx="104" cy="64" rx="30" ry="20" fill="#d98a6e" fill-opacity=".32"/>

    <!-- ===== 大拱嘴 ===== -->
    <ellipse cx="0" cy="38" rx="110" ry="76" class="pencil" stroke-width="2.8" fill="#eccfa0" fill-opacity=".7"/>
    <!-- 鼻孔 -->
    <ellipse cx="-42" cy="34" rx="18" ry="25" fill="#604220" opacity=".8"/>
    <ellipse cx="42" cy="34" rx="18" ry="25" fill="#604220" opacity=".8"/>
    <!-- 鼻吻排线 -->
    <g class="pencil hatch">
      <path d="M -88 8 q -14 40 0 70"/><path d="M 88 8 q 14 40 0 70"/>
      <path d="M -60 96 q 60 18 120 0"/>
    </g>

    <!-- 嘴（憨笑） -->
    <path class="pencil" stroke-width="3" fill="#b06a4e" fill-opacity=".3"
          d="M -58 126 Q 0 168 58 126 Q 0 144 -58 126 Z"/>

    <!-- ===== 身体 ===== -->
    <!-- 外袍 -->
    <path class="pencil" stroke-width="2.8" fill="#c9a86e" fill-opacity=".5"
          d="M -238 224
             C -262 320, -250 424, -202 486
             L 202 486
             C 250 424, 262 320, 238 224
             C 202 172, 112 166, 0 182
             C -112 166, -202 172, -238 224 Z"/>
    <!-- 肚皮 -->
    <ellipse cx="0" cy="372" rx="104" ry="116" class="pencil" stroke-width="2.6" fill="#f2dcb6" fill-opacity=".8"/>
    <!-- 肚脐 -->
    <circle cx="0" cy="392" r="7" class="pencil hatch"/>
    <!-- 交领 -->
    <path class="pencil" stroke-width="2.4" d="M -150 210 Q -60 286 -14 330"/>
    <path class="pencil" stroke-width="2.4" d="M 150 210 Q 60 286 14 330"/>
    <!-- 袍褶 -->
    <g class="pencil hatch">
      <path d="M -190 280 q -10 90 -6 180"/><path d="M 190 280 q 10 90 6 180"/>
      <path d="M -120 470 q 6 -30 4 -60"/><path d="M 120 470 q -6 -30 -4 -60"/>
    </g>
  </g>

  <!-- 脚下投影 -->
  <ellipse cx="1530" cy="1010" rx="230" ry="22" fill="#7a5e30" fill-opacity=".14"/>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="FIELD NOTE · 代码考古 · No.01",
    title1="一身毛病的猪八戒，",
    title2="不是编的。",
    seal_cols=[["八"], ["戒"]],
    dateline="中国佛教史 · 短视频第 01 篇",
    dateline_en="FIELD NOTE No.01 · CODE ARCHAEOLOGY",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="猪八戒封面",
    scene_comment="素描主视觉：猪八戒",
    css_style="compact",
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
