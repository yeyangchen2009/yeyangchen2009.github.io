# -*- coding: utf-8 -*-
"""朱士行王版 · 封面生成器（宏观阿尔法风格）。

新流程第①步：先做封面——锁死「一句话主张＋主视觉」，再进 TTS 与成片。
公共骨架（doctype/reset/通用 CSS/纸纹/SVG 外层）在 videopipe.cover；
本文件只保留朱士行独有的：布局数值、老僧西行主视觉 SVG、金色制图 SVG、
文字内容。用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from videopipe import CoverLayout, render_cover

HERE = Path(__file__).resolve().parent

# 本片布局数值（结构同两片，数值取自 cover.html）
LAYOUT = CoverLayout(
    wash_rw=1200, wash_x="78%", wash_y="38%", wash_alpha=".14",
    title_top=198, title_width=1180,
    t1_size=86, t2_size=196, t2_mtop=8,
    subnote_mode="top", subnote_pos=848,
    seal_size=44, seal_lineheight="1.02", seal_gap="6px",
    tag_top=108,
)

# 金色工程制图 SVG 内层（坐标围绕落日 1606,318 与老僧）
BLUEPRINT_SVG = """  <!-- 左上十字准星 -->
  <g>
    <line class="bp bp-line" x1="60" y1="150" x2="560" y2="150"/>
    <line class="bp bp-line" x1="240" y1="60" x2="240" y2="420"/>
    <circle class="bp bp-dim" cx="240" cy="150" r="15"/>
    <circle class="bp-dot" cx="240" cy="150" r="3.4"/>
    <!-- 刻度 -->
    <g class="bp bp-dim">
      <line x1="100" y1="142" x2="100" y2="158"/><line x1="140" y1="142" x2="140" y2="158"/>
      <line x1="180" y1="144" x2="180" y2="156"/><line x1="300" y1="144" x2="300" y2="156"/>
      <line x1="340" y1="142" x2="340" y2="158"/><line x1="380" y1="142" x2="380" y2="158"/>
      <line x1="232" y1="90" x2="248" y2="90"/><line x1="232" y1="120" x2="248" y2="120"/>
      <line x1="232" y1="180" x2="248" y2="180"/><line x1="232" y1="210" x2="248" y2="210"/>
    </g>
  </g>

  <!-- 落日为圆心的大 construction 圆弧（右上） -->
  <g>
    <circle class="bp bp-thin" cx="1606" cy="318" r="150" stroke-dasharray="9 8"/>
    <circle class="bp bp-dim" cx="1606" cy="318" r="238"/>
    <path class="bp bp-line" d="M 1606 40 A 278 278 0 0 1 1872 230"/>
    <!-- 径向放射刻度 -->
    <g class="bp bp-dim">
      <line x1="1606" y1="32" x2="1606" y2="52"/>
      <line x1="1858" y1="192" x2="1874" y2="204"/>
      <line x1="1700" y1="58" x2="1712" y2="74"/>
      <line x1="1794" y1="104" x2="1804" y2="122"/>
    </g>
    <circle class="bp-dot" cx="1606" cy="318" r="4"/>
    <circle class="bp-dot" cx="1858" cy="192" r="3.2"/>
    <!-- 水平基准虚线穿画面 -->
    <line class="bp bp-thin" x1="560" y1="318" x2="1340" y2="318" stroke-dasharray="10 9"/>
    <line class="bp bp-line" x1="1248" y1="318" x2="1330" y2="318"/>
    <path class="bp bp-line" d="M1318 309 L1336 318 L1318 327"/>
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

  <!-- 标题下方虚线＋箭头＋点（右下方向） -->
  <g>
    <line class="bp bp-thin" x1="560" y1="800" x2="1080" y2="800" stroke-dasharray="3 10"/>
    <circle class="bp-dot" cx="610" cy="800" r="3"/><circle class="bp-dot" cx="760" cy="800" r="3"/>
    <circle class="bp-dot" cx="910" cy="800" r="3"/><circle class="bp-dot" cx="1060" cy="800" r="3"/>
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
    <path d="M 820 70 L 1000 70 L 910 150 Z"/>
    <circle class="bp-dot" cx="820" cy="70" r="3"/><circle class="bp-dot" cx="1000" cy="70" r="3"/>
    <circle class="bp-dot" cx="910" cy="150" r="3"/>
  </g>"""

# 素描主视觉 SVG 内层：老僧拄杖西行背影、落日、沙丘、脚印、远驼队
SCENE_SVG = """  <!-- 远沙脊 -->
  <path class="pencil" stroke-width="2" opacity=".55"
        d="M 880 806 C 1080 760, 1240 772, 1400 746 C 1560 722, 1740 736, 1940 712"/>
  <!-- 远沙脊排线 -->
  <g class="pencil hatch">
    <path d="M960 800 q 26 14 52 0"/><path d="M1060 786 q 26 13 52 0"/>
    <path d="M1180 772 q 26 12 52 0"/><path d="M1300 758 q 24 12 48 0"/>
    <path d="M1500 736 q 24 11 48 0"/><path d="M1640 728 q 26 11 52 0"/>
    <path d="M1780 720 q 26 10 52 0"/>
  </g>

  <!-- 远处小驼队剪影 -->
  <g class="pencil" stroke-width="1.6" opacity=".6">
    <path d="M1108 772 c 2 -14 6 -22 10 -22 c 3 0 3 8 5 8 c 2 -6 5 -10 8 -8 c 3 4 4 12 6 22"/>
    <circle cx="1112" cy="748" r="2.6"/>
    <path d="M1152 766 c 2 -12 5 -19 9 -19 c 2 0 3 7 4 7 c 2 -5 4 -9 7 -7 c 2 3 3 10 5 19"/>
  </g>

  <!-- 落日 -->
  <circle cx="1606" cy="318" r="92" fill="#e3a35c" fill-opacity=".3"
          stroke="#c07f36" stroke-width="2.2" stroke-opacity=".75"/>
  <circle cx="1606" cy="318" r="92" fill="none" class="pencil hatch"/>
  <!-- 落日里的几道云气 -->
  <path class="pencil hatch" d="M1536 326 q 35 -14 70 0 q 35 13 70 0"/>
  <path class="pencil hatch" d="M1552 350 q 27 -10 54 0 q 27 9 54 0"/>

  <!-- 近沙丘 -->
  <path class="pencil" stroke-width="2.6"
        d="M 820 1080 C 900 930, 1080 872, 1260 852 C 1460 830, 1620 868, 1760 930 C 1840 966, 1890 1020, 1920 1080 Z"
        fill="#e8d5ac" fill-opacity=".55"/>
  <path class="pencil" stroke-width="2.4"
        d="M 820 1080 C 900 930, 1080 872, 1260 852 C 1460 830, 1620 868, 1760 930 C 1840 966, 1890 1020, 1920 1080"/>
  <!-- 沙纹排线 -->
  <g class="pencil hatch">
    <path d="M980 1000 q 40 -16 80 0"/><path d="M1070 970 q 36 -14 72 0"/>
    <path d="M1160 940 q 40 -15 80 0"/><path d="M1260 912 q 38 -14 76 0"/>
    <path d="M1370 892 q 42 -13 84 0"/><path d="M1490 888 q 40 -10 80 0"/>
    <path d="M1590 912 q 36 -8 72 0"/><path d="M1680 952 q 34 -6 68 0"/>
    <path d="M1020 1050 q 44 -14 88 0"/><path d="M1200 1040 q 44 -10 88 0"/>
    <path d="M1400 1030 q 44 -8 88 0"/><path d="M1600 1024 q 40 -6 80 0"/>
    <path d="M1780 1020 q 30 -4 60 0"/>
    <!-- 沙脊亮边短触 -->
    <path d="M1230 858 l 18 -4"/><path d="M1280 854 l 18 -3"/><path d="M1330 851 l 18 -3"/>
    <path d="M1380 850 l 18 -2"/><path d="M1430 851 l 18 -2"/>
  </g>

  <!-- 一串脚印（从画面右下走向老僧） -->
  <g class="pencil hatch">
    <ellipse cx="1196" cy="1018" rx="7" ry="3.4" transform="rotate(-12 1196 1018)"/>
    <ellipse cx="1226" cy="1000" rx="7" ry="3.4" transform="rotate(-10 1226 1000)"/>
    <ellipse cx="1252" cy="982" rx="6.5" ry="3.2" transform="rotate(-9 1252 982)"/>
    <ellipse cx="1278" cy="964" rx="6.5" ry="3.2" transform="rotate(-8 1278 964)"/>
    <ellipse cx="1304" cy="932" rx="6.2" ry="3.1" transform="rotate(-8 1304 932)"/>
    <ellipse cx="1328" cy="896" rx="6" ry="3" transform="rotate(-7 1328 896)"/>
    <ellipse cx="1350" cy="850" rx="5.8" ry="2.9" transform="rotate(-6 1350 850)"/>
    <ellipse cx="1370" cy="800" rx="5.5" ry="2.8" transform="rotate(-5 1370 800)"/>
    <ellipse cx="1386" cy="746" rx="5.2" ry="2.7" transform="rotate(-4 1386 746)"/>
    <ellipse cx="1394" cy="712" rx="5" ry="2.6" transform="rotate(-3 1394 712)"/>
  </g>

  <!-- ====== 老僧（拄杖西行背影）基点 1500,300，整体 1.1 倍 ====== -->
  <g transform="translate(1500,300) scale(1.1)">
    <!-- 头（光后脑勺） -->
    <path class="pencil" stroke-width="2.6"
          d="M -40 6 Q -44 -38 2 -46 Q 46 -44 44 6 Q 42 26 30 36 Q 14 46 -4 44 Q -30 40 -38 24 Q -42 16 -40 6 Z"/>
    <!-- 耳朵 -->
    <path class="pencil" stroke-width="2" d="M -40 6 q -12 4 -10 18 q 2 10 12 8"/>
    <!-- 头部排线（暗部） -->
    <g class="pencil hatch">
      <path d="M 26 -30 q 10 8 10 22"/><path d="M 30 -14 q 7 8 6 20"/>
      <path d="M 22 -38 q 14 6 18 18"/><path d="M -34 18 q 8 6 18 6"/>
    </g>
    <!-- 后颈 -->
    <path class="pencil" stroke-width="2" d="M -14 44 q -2 18 -10 30 M 16 44 q 4 16 12 26"/>

    <!-- 僧袍主体：肩→腰→下摆 -->
    <path class="pencil" stroke-width="2.8" fill="#cdb283" fill-opacity=".38"
          d="M -78 86
             Q -104 120 -108 190
             Q -116 280 -146 356
             Q -120 374 -86 366
             Q -40 352 -8 348
             Q 30 350 62 366
             Q 104 378 132 358
             Q 108 272 104 196
             Q 102 122 74 88
             Q 40 66 2 68
             Q -44 66 -78 86 Z"/>
    <!-- 外轮廓再勾一遍（保证闭合线清晰） -->
    <path class="pencil" stroke-width="2.6"
          d="M -78 86
             Q -104 120 -108 190
             Q -116 280 -146 356
             Q -120 374 -86 366
             Q -40 352 -8 348
             Q 30 350 62 366
             Q 104 378 132 358
             Q 108 272 104 196
             Q 102 122 74 88
             Q 40 66 2 68
             Q -44 66 -78 86 Z"/>

    <!-- 袍褶长线 -->
    <g class="pencil" stroke-width="1.8" opacity=".72">
      <path d="M -58 104 q -18 110 -52 244"/>
      <path d="M -24 96 q -8 120 -20 250"/>
      <path d="M 10 86 q 4 130 2 258"/>
      <path d="M 44 96 q 14 110 34 250"/>
      <path d="M 72 110 q 20 100 44 238"/>
    </g>
    <!-- 腰带 -->
    <path class="pencil" stroke-width="2.2" d="M -96 236 Q -2 258 96 232"/>
    <path class="pencil hatch" d="M -80 240 q 78 16 158 -4"/>

    <!-- 背上圆包袱（外层，盖在袍上） -->
    <g>
      <!-- 口袋主体 -->
      <path class="pencil" stroke-width="2.4" fill="#d8c190" fill-opacity=".55"
            d="M 30 110
               Q 28 84 62 82
               Q 98 84 100 116
               Q 108 154 92 186
               Q 76 212 50 206
               Q 22 198 16 166
               Q 12 134 30 110 Z"/>
      <!-- 包袱口扎绳结 -->
      <path class="pencil" stroke-width="2" d="M 50 82 q -6 -12 4 -18 M 64 80 q 8 -12 0 -18"/>
      <circle class="pencil" stroke-width="2" cx="58" cy="84" r="4"/>
      <!-- 包袱里露出的卷轴轴头 -->
      <line class="pencil" stroke-width="2" x1="40" y1="98" x2="86" y2="96"/>
      <ellipse class="pencil" stroke-width="1.8" cx="38" cy="98" rx="5" ry="8"/>
      <ellipse class="pencil" stroke-width="1.8" cx="88" cy="96" rx="5" ry="8"/>
      <!-- 斜挎绑带 -->
      <path class="pencil hatch" d="M 22 88 q 26 44 52 84"/>
      <!-- 包袱布纹排线 -->
      <g class="pencil hatch">
        <path d="M 34 130 q 14 8 28 2"/><path d="M 40 156 q 16 8 32 0"/>
        <path d="M 44 182 q 14 6 28 -2"/><path d="M 86 128 q 8 16 4 34"/>
      </g>
    </g>

    <!-- 前侧左臂（弯曲持杖） -->
    <path class="pencil" stroke-width="2.4"
          d="M -78 96 Q -104 150 -84 196 Q -66 224 -42 214"/>
    <!-- 宽袖口 -->
    <path class="pencil" stroke-width="2.2" d="M -52 200 q -14 14 -8 30 q 10 8 22 0"/>
    <!-- 手 -->
    <ellipse class="pencil" stroke-width="2" cx="-40" cy="214" rx="10" ry="8"/>

    <!-- 禅杖：从手斜插到沙 -->
    <line class="pencil" stroke-width="2.6" x1="-42" y1="212" x2="-108" y2="402"/>
    <path class="pencil hatch" d="M -48 236 l -6 3 M -62 282 l -6 3 M -80 332 l -6 3"/>
    <!-- 杖头小环 -->
    <circle class="pencil" stroke-width="1.8" cx="-36" cy="196" r="7"/>

    <!-- 后侧右袖（垂下） -->
    <path class="pencil" stroke-width="2.4"
          d="M 74 92 Q 104 150 96 214 Q 92 240 76 246"/>
    <path class="pencil hatch" d="M 84 130 q 8 40 2 86"/>

    <!-- 袍子暗部排线（右侧背光面密排） -->
    <g class="pencil hatch">
      <path d="M 86 150 l 16 12"/><path d="M 90 172 l 17 12"/><path d="M 92 196 l 16 11"/>
      <path d="M 92 222 l 15 11"/><path d="M 90 248 l 15 12"/><path d="M 86 274 l 14 12"/>
      <path d="M 82 300 l 13 12"/><path d="M 76 326 l 12 11"/>
      <path d="M 62 348 l 11 10"/>
      <!-- 左肩少量 -->
      <path d="M -84 120 l -13 12"/><path d="M -92 150 l -12 11"/><path d="M -96 180 l -11 11"/>
    </g>

    <!-- 下摆波浪边 -->
    <path class="pencil" stroke-width="2"
          d="M -146 356 q 14 8 30 2 q 16 -7 30 2 q 16 8 30 0 q 16 -8 30 0 q 16 8 30 0 q 16 -8 30 2 q 16 9 30 0 q 16 -8 28 4"/>

    <!-- 脚（一前一后，向西＝左） -->
    <path class="pencil" stroke-width="2.2" d="M -96 358 q -24 4 -34 16 q -4 8 10 8 q 22 2 34 -6"/>
    <path class="pencil" stroke-width="2.2" d="M 40 360 q -14 4 -20 14 q -2 8 10 8 q 18 2 28 -6"/>
  </g>

  <!-- 老僧脚下投影 -->
  <ellipse cx="1470" cy="704" rx="165" ry="21" fill="#7a5e30" fill-opacity=".13"/>"""

html = render_cover(
    layout=LAYOUT,
    tag_text="FIELD NOTE · 西行求法 · No.260",
    title1="第一个西行取经的中国和尚，",
    title2="不是玄奘。",
    seal_cols=[["西", "行"], ["求", "法"]],
    dateline="公元 260 年 · 从长安出发，西渡流沙",
    dateline_en="CHANG'AN → KHOTAN · 11,000 LI",
    blueprint_svg=BLUEPRINT_SVG,
    scene_svg=SCENE_SVG,
    title="朱士行封面",
    has_inkbleed=True,
    mashan_src="../../assets/fonts/MaShanZheng.ttf",
    wenkai_href="../../assets/wenkai/lxgwwenkai-bold.css",
)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
