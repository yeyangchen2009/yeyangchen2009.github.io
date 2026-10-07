# -*- coding: utf-8 -*-
"""封面公共骨架：宏观阿尔法风格（宣纸底＋圆润大字＋铅笔素描＋金色制图）。

深模块：项目只提供——
  1. CoverLayout：标题/印章/晕染等本片布局数值（结构相同、数值不同）；
  2. scene 主视觉 SVG（老僧 / 猪头 …，逐片手写，完全独有）；
  3. blueprint 金色制图 SVG 内层（坐标围绕各自主视觉）；
  4. 文字内容（tag / 标题 / 印章列 / 日期线）。
doctype / reset / body / 通用 CSS / grain 纸纹 / SVG 外层全部本模块固定，
顺序与空白锁定，使新封面能与黄金参考 PNG 做零像素差异比对。

随片增量：先随 wang 验证；zbj 迁移时复用并核对。
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CoverLayout:
    # wash 第一层 radial-gradient（第二、三层两片逐字同，固定在模板）
    wash_rw: int            # ellipse 宽 px（wang 1200 / zbj 1100）
    wash_x: str             # at 横向（'78%' / '80%'）
    wash_y: str             # at 纵向（'38%' / '45%'）
    wash_alpha: str         # 晕染色 alpha（'.14' / '.15'）
    # 标题盒（left 两片同 118，固定）
    title_top: int          # wang 198 / zbj 268
    title_width: int        # wang 1180 / zbj 1120
    t1_size: int            # wang 86 / zbj 84
    t2_size: int            # wang 196 / zbj 200
    t2_mtop: int            # wang 8 / zbj 10
    # 印章＋日期线盒（left 两片同 130，固定）
    subnote_mode: str       # 定位：'top' / 'bottom'
    subnote_pos: int        # wang top:848 / zbj bottom:96
    seal_size: int          # wang 44（四字）/ zbj 62（两字）
    seal_lineheight: Optional[str]   # wang '1.02' / zbj None
    seal_gap: str           # 列间距（wang '6px' / zbj '4px'）
    # 顶部 field note（left 两片同 118，固定）
    tag_top: int            # wang 108 / zbj 150


# blueprint 内两片逐字相同的两段（4 空格缩进，可直接嵌入内层）
RULER_LEFT = """  <!-- 左下竖标尺 -->
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
  </g>"""

BOX_RIGHT = """  <!-- 右下小方框标注 -->
  <g class="bp bp-dim">
    <rect x="1780" y="930" width="96" height="70"/>
    <line x1="1828" y1="916" x2="1828" y2="930"/>
    <line x1="1828" y1="1000" x2="1828" y2="1016"/>
    <circle class="bp-dot" cx="1828" cy="916" r="3"/>
  </g>"""


_CSS_SPACED = """  @font-face {
    font-family: 'MaShanZheng';
    src: url('%(mashan_src)s') format('truetype');
    font-display: block;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1920px; height: 1080px; overflow: hidden; }
  body {
    position: relative;
    background: #f4ecda;
    font-family: 'MaShanZheng', 'KaiTi', serif;
  }
  /* 纸面整体做旧晕染 */
  .wash {
    position: absolute; inset: 0; z-index: 0;
    background:
      radial-gradient(ellipse %(wash_rw)dpx 700px at %(wash_x)s %(wash_y)s, rgba(214,160,80,%(wash_alpha)s), transparent 65%%),
      radial-gradient(ellipse 900px 600px at 12%% 88%%, rgba(120,90,50,.08), transparent 70%%),
      radial-gradient(ellipse 1400px 800px at 50%% 50%%, transparent 60%%, rgba(110,80,40,.10));
  }
  /* 纸纹纤维 */
  .grain { position: absolute; inset: 0; z-index: 1; pointer-events: none; }
  .layer { position: absolute; inset: 0; }

  /* ===== 金色工程制图层 ===== */
  .blueprint { z-index: 2; }
  .bp { fill: none; stroke: #a97d2b; stroke-linecap: round; }
  .bp-dim { stroke-width: 1.6; stroke-opacity: .55; }
  .bp-line { stroke-width: 2; stroke-opacity: .8; }
  .bp-thin { stroke-width: 1.2; stroke-opacity: .4; }
  .bp-dot { fill: #a97d2b; stroke: none; }

  /* ===== 素描主视觉 ===== */
  .scene { z-index: 3; }
  .pencil { fill: none; stroke: #423a2e; stroke-linecap: round; stroke-linejoin: round; }
  .hatch { stroke-width: 1.1; stroke-opacity: .5; }

  /* ===== 标题 ===== */
  .title-wrap {
    position: absolute; z-index: 5;
    left: 118px; top: %(title_top)dpx; width: %(title_width)dpx;
  }
  .t1 {
    font-family: 'LXGW WenKai', 'KaiTi', serif;
    font-weight: 700;
    font-size: %(t1_size)dpx; color: #1b1710;
    letter-spacing: 6px; line-height: 1.15;
    white-space: nowrap;
  }
  .t2 {
    font-family: 'LXGW WenKai', 'KaiTi', serif;
    font-weight: 700;
    font-size: %(t2_size)dpx; color: #141008;
    line-height: 1.08; letter-spacing: 12px;
    margin-top: %(t2_mtop)dpx;
    white-space: nowrap;
  }
  .t2 .redcircle { position: relative; }
  .subnote {
    position: absolute; z-index: 5;
    left: 130px; %(subnote_decl)s;
    display: flex; align-items: center; gap: 26px;
  }
  .seal {
    width: 132px; height: 132px;
    background: #b03426;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    color: #f7ead2; %(seal_font)s;
    letter-spacing: 2px;
    font-family: 'MaShanZheng','KaiTi',serif;
    transform: rotate(-3deg);
    box-shadow: 0 0 0 3px #b03426, 0 0 0 6px rgba(176,52,38,.25);
    filter: url(#sealrough);
  }
  .seal .col { display: flex; flex-direction: column; align-items: center; }
  .dateline { color: #6d5a36; font-size: 34px; letter-spacing: 4px; font-family: 'KaiTi',serif; }
  .dateline .en { display: block; font-size: 19px; letter-spacing: 5px; color: #a97d2b;
                  font-family: 'Consolas', monospace; margin-top:6px; }

  .tag {
    position: absolute; z-index: 5; left: 118px; top: %(tag_top)dpx;
    color: #a97d2b; font-family: 'Consolas', monospace;
    font-size: 21px; letter-spacing: 6px;
    display: flex; align-items: center; gap: 14px;
  }
  .tag .bar { width: 70px; height: 2px; background: #a97d2b; opacity: .8; }"""

# zbj 老封面：从 .wash 起冒号后一律无空格，且无 .t2 .redcircle 行
_CSS_COMPACT = """  @font-face {
    font-family: 'MaShanZheng';
    src: url('%(mashan_src)s') format('truetype');
    font-display: block;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html, body { width: 1920px; height: 1080px; overflow: hidden; }
  body {
    position: relative;
    background: #f4ecda;
    font-family: 'MaShanZheng', 'KaiTi', serif;
  }
  /* 纸面整体做旧晕染 */
  .wash {
    position: absolute; inset:0; z-index:0;
    background:
      radial-gradient(ellipse %(wash_rw)dpx 700px at %(wash_x)s %(wash_y)s, rgba(214,160,80,%(wash_alpha)s), transparent 65%%),
      radial-gradient(ellipse 900px 600px at 12%% 88%%, rgba(120,90,50,.08), transparent 70%%),
      radial-gradient(ellipse 1400px 800px at 50%% 50%%, transparent 60%%, rgba(110,80,40,.10));
  }
  .grain { position:absolute; inset:0; z-index:1; pointer-events:none; }
  .layer { position:absolute; inset:0; }

  /* ===== 金色工程制图层 ===== */
  .blueprint { z-index:2; }
  .bp { fill:none; stroke:#a97d2b; stroke-linecap:round; }
  .bp-dim { stroke-width:1.6; stroke-opacity:.55; }
  .bp-line { stroke-width:2; stroke-opacity:.8; }
  .bp-thin { stroke-width:1.2; stroke-opacity:.4; }
  .bp-dot { fill:#a97d2b; stroke:none; }

  /* ===== 素描主视觉 ===== */
  .scene { z-index:3; }
  .pencil { fill:none; stroke:#423a2e; stroke-linecap:round; stroke-linejoin:round; }
  .hatch { stroke-width:1.1; stroke-opacity:.5; }

  /* ===== 标题 ===== */
  .title-wrap {
    position:absolute; z-index:5;
    left:118px; top:%(title_top)dpx; width:%(title_width)dpx;
  }
  .t1 {
    font-family:'LXGW WenKai','KaiTi',serif;
    font-weight:700;
    font-size:%(t1_size)dpx; color:#1b1710;
    letter-spacing:6px; line-height:1.15;
    white-space:nowrap;
  }
  .t2 {
    font-family:'LXGW WenKai','KaiTi',serif;
    font-weight:700;
    font-size:%(t2_size)dpx; color:#141008;
    line-height:1.08; letter-spacing:12px;
    margin-top:%(t2_mtop)dpx;
    white-space:nowrap;
  }
  .subnote {
    position:absolute; z-index:5;
    left:130px; %(subnote_decl)s;
    display:flex; align-items:center; gap:26px;
  }
  .seal {
    width:132px; height:132px;
    background:#b03426;
    border-radius:6px;
    display:flex; align-items:center; justify-content:center;
    color:#f7ead2; %(seal_font)s;
    letter-spacing:2px;
    font-family:'MaShanZheng','KaiTi',serif;
    transform:rotate(-3deg);
    box-shadow:0 0 0 3px #b03426, 0 0 0 6px rgba(176,52,38,.25);
    filter:url(#sealrough);
  }
  .seal .col { display:flex; flex-direction:column; align-items:center; }
  .dateline { color:#6d5a36; font-size:34px; letter-spacing:4px; font-family:'KaiTi',serif; }
  .dateline .en { display:block; font-size:19px; letter-spacing:5px; color:#a97d2b;
                  font-family:'Consolas',monospace; margin-top:6px; }

  .tag {
    position:absolute; z-index:5; left:118px; top:%(tag_top)dpx;
    color:#a97d2b; font-family:'Consolas',monospace;
    font-size:21px; letter-spacing:6px;
    display:flex; align-items:center; gap:14px;
  }
  .tag .bar { width:70px; height:2px; background:#a97d2b; opacity:.8; }"""

_INKBLEED = """
  <!-- 墨迹微洇滤镜（给标题用） -->
  <filter id="inkbleed" x="-6%" y="-6%" width="112%" height="112%">
    <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="11" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="4.2"/>
  </filter>"""

_GRAIN_SPACED = """<!-- 纸纹纤维：SVG turbulence -->
<svg class="grain" width="1920" height="1080" viewBox="0 0 1920 1080">
  <filter id="paperNoise">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
  <rect width="1920" height="1080" filter="url(#paperNoise)" opacity=".07"/>
  <!-- 几条长纤维 -->
  <g fill="none" stroke="#8a6f42" stroke-opacity=".09">
    <path d="M-40 232 C 500 218, 1100 250, 1960 226" stroke-width="1.2"/>
    <path d="M-40 612 C 600 628, 1200 596, 1960 618" stroke-width="1"/>
    <path d="M-40 942 C 700 926, 1250 960, 1960 940" stroke-width="1.3"/>
  </g>%(inkbleed)s
  <!-- 印章斑驳 -->
  <filter id="sealrough">
    <feTurbulence type="fractalNoise" baseFrequency="0.11" numOctaves="3" seed="5" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="3.2"/>
  </filter>
</svg>"""

# zbj：首注释无「：SVG turbulence」尾注，且无「几条长纤维」注释
_GRAIN_COMPACT = """<!-- 纸纹纤维 -->
<svg class="grain" width="1920" height="1080" viewBox="0 0 1920 1080">
  <filter id="paperNoise">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
  <rect width="1920" height="1080" filter="url(#paperNoise)" opacity=".07"/>
  <g fill="none" stroke="#8a6f42" stroke-opacity=".09">
    <path d="M-40 232 C 500 218, 1100 250, 1960 226" stroke-width="1.2"/>
    <path d="M-40 612 C 600 628, 1200 596, 1960 618" stroke-width="1"/>
    <path d="M-40 942 C 700 926, 1250 960, 1960 940" stroke-width="1.3"/>
  </g>%(inkbleed)s
  <!-- 印章斑驳 -->
  <filter id="sealrough">
    <feTurbulence type="fractalNoise" baseFrequency="0.11" numOctaves="3" seed="5" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="3.2"/>
  </filter>
</svg>"""


def _seal_html(cols, gap) -> str:
    parts = []
    for i, col in enumerate(cols):
        inner = "".join("<span>%s</span>" % c for c in col)
        if i == 0:
            parts.append('    <span class="col">%s</span>' % inner)
        else:
            parts.append('    <span class="col" style="margin-left:%s">%s</span>'
                         % (gap, inner))
    return "\n".join(parts)


def render_cover(*, layout: CoverLayout, tag_text, title1, title2,
                 seal_cols, dateline, dateline_en,
                 blueprint_svg, scene_svg,
                 title="封面", scene_comment="素描主视觉",
                 css_style="spaced",
                 wenkai_href="wenkai/package/lxgwwenkai-bold.css",
                 mashan_src="fonts/MaShanZheng.ttf",
                 has_inkbleed=False) -> str:
    """组装完整封面 HTML（字符串）。字体路径可按环境覆盖。

    css_style：'spaced'（wang，属性冒号后带空格）/ 'compact'（zbj 紧凑）。
    """
    if css_style == "compact":
        subnote_decl = ("%s:%dpx" % (layout.subnote_mode, layout.subnote_pos))
    else:
        subnote_decl = ("%s: %dpx" % (layout.subnote_mode, layout.subnote_pos))
    if css_style == "compact":
        seal_font = "font-size:%dpx" % layout.seal_size
        if layout.seal_lineheight:
            seal_font += ";line-height:%s" % layout.seal_lineheight
        css_tpl, grain_tpl = _CSS_COMPACT, _GRAIN_COMPACT
    else:
        seal_font = "font-size: %dpx" % layout.seal_size
        if layout.seal_lineheight:
            seal_font += "; line-height: %s" % layout.seal_lineheight
        css_tpl, grain_tpl = _CSS_SPACED, _GRAIN_SPACED
    css = css_tpl % {
        "mashan_src": mashan_src,
        "wash_rw": layout.wash_rw, "wash_x": layout.wash_x,
        "wash_y": layout.wash_y, "wash_alpha": layout.wash_alpha,
        "title_top": layout.title_top, "title_width": layout.title_width,
        "t1_size": layout.t1_size,
        "t2_size": layout.t2_size, "t2_mtop": layout.t2_mtop,
        "subnote_decl": subnote_decl,
        "seal_font": seal_font,
        "tag_top": layout.tag_top,
    }
    grain = grain_tpl % {"inkbleed": _INKBLEED if has_inkbleed else ""}
    seal = _seal_html(seal_cols, layout.seal_gap)

    return (
        '<!DOCTYPE html>\n'
        '<html lang="zh-CN">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<title>%s</title>\n'
        '<link rel="stylesheet" href="%s">\n'
        '<style>\n%s\n</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="wash"></div>\n'
        '\n%s\n'
        '\n<!-- ============ 金色工程制图层 ============ -->\n'
        '<svg class="layer blueprint" width="1920" height="1080" '
        'viewBox="0 0 1920 1080">\n%s\n</svg>\n'
        '\n<!-- ============ %s ============ -->\n'
        '<svg class="layer scene" width="1920" height="1080" '
        'viewBox="0 0 1920 1080">\n%s\n</svg>\n'
        '\n<!-- ============ 文字层 ============ -->\n'
        '<div class="tag"><span class="bar"></span>%s</div>\n'
        '<div class="title-wrap">\n'
        '  <div class="t1">%s</div>\n'
        '  <div class="t2">%s</div>\n'
        '</div>\n'
        '<div class="subnote">\n'
        '  <div class="seal">\n%s\n  </div>\n'
        '  <div class="dateline">\n    %s\n'
        '    <span class="en">%s</span>\n  </div>\n'
        '</div>\n'
        '</body>\n</html>\n'
        % (title, wenkai_href, css, grain, blueprint_svg, scene_comment,
           scene_svg, tag_text, title1, title2, seal, dateline,
           dateline_en)
    )
