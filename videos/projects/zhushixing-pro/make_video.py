# -*- coding: utf-8 -*-
"""朱士行 Pro（丝路电影级样板，demo 单幕）成片生成器。

本片独有：
- ★camera tracking：外层 <g id="camera"> 随 walker 西行缓慢 pan + 极轻 zoom，
  起幅洛阳近景、终帧聚焦于阗（电影跟镜），与素版最大差别；
- 精致地形（沙点 pattern / 沙丘弧线 / 祁连山脉 / 于阗河 / 绿洲 / 阳关烽燧）；
- walker = 黑暗大漠里一盏移动的「灯火」（暖光跟随 + 有界呼吸）；
- 地名 SVG clipPath 行级擦入，节点到达光环单次扩散；
- 内联 WebGL cinematic-zoom 起幅（黑场 → 洛阳）；
- 思源宋体 Noto Serif SC / Source Han Serif Heavy；
- vignette 暗角 + CSS 点阵 grain。

只生成丝路一幕（全片时间 68.2–90.3），时间整体偏移 -68.2 归零。
★cues 不另存：跨项目只读 ../zhushixing/cues/cues.json，底部字幕切
cue36–48（cue35「公元二六零年」由 WebGL 标题卡承担）。
页面骨架 / 主题 / 字幕 / clip 外壳全部复用 videopipe。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       SILK_PRO)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

# ---------- demo 窗口参数 ----------
ACT_S, ACT_E = 68.2, 90.3
OFF = ACT_S
TOTAL = round(ACT_E - ACT_S, 3)          # 22.1
THEME = SILK_PRO

# ---------- 跨项目读素版 cues ----------
VIDEOS_DIR = Path(__file__).resolve().parents[2]
src_cues = VIDEOS_DIR / "projects" / "zhushixing" / "cues" / "cues.json"
d = load_cues(src_cues)
cues_all, chars_all = d["cues"], d["chars"]

# 先把全片 cue 顺序消费成字（保留 assert 对齐），记录每 cue 的字列表
cue_chars = []
ci = 0
for cue in cues_all:
    these = []
    for ch in cue["t"]:
        c = chars_all[ci]
        assert c["c"] == ch, (c["c"], ch)
        these.append(c)
        ci += 1
    cue_chars.append((cue, these))
assert ci == len(chars_all)

# 底部字幕范围：cue 36..48
SUB = cue_chars[36:49]
sub_cues = [cue for cue, _ in SUB]
sub_chars = [c for _, these in SUB for c in these]
frag = char_track(sub_cues, sub_chars, THEME.accent,
                  time_offset=-OFF, sub_ids=range(36, 49))

# ---------- 节点（东→西，右→左） ----------
# (id, cx, cy, 地名, text_y, clip_x, arrive_t)
NODES = [
    ("n-luo",  1560, 520, "洛阳", 486, 1483, 4.38),
    ("n-guan", 1280, 470, "关中", 436, 1203, 5.80),
    ("n-he",   1000, 440, "河西", 406,  923, 6.70),
    ("n-yang",  700, 480, "阳关", 446,  623, 7.60),
    ("n-yu",    360, 560, "于阗", 612,  283, 18.20),
]

clip_defs, node_html, node_js = [], [], []
for nid, cx, cy, name, ty, clipx, arr in NODES:
    clip_defs.append(
        '        <clipPath id="clip-%s"><rect id="cr-%s" x="%d" y="%d" width="0" height="48"/></clipPath>'
        % (nid, nid, clipx, ty - 38))
    node_html.append(
        '          <g class="node" id="%s">'
        '<circle class="halo" cx="%d" cy="%d" r="10"/>'
        '<circle cx="%d" cy="%d" r="9"/>'
        '<text x="%d" y="%d" clip-path="url(#clip-%s)">%s</text></g>'
        % (nid, cx, cy, cx, cy, cx, ty, nid, name))
    node_js.append(
        "      tl.to('#cr-%s', { attr: { width: 154 }, duration: .45, ease: 'power2.inOut' }, %.2f);"
        % (nid, arr))
    node_js.append(
        "      tl.fromTo('#%s .halo', { attr: { r: 9 }, opacity: .55 }, { attr: { r: 30 }, opacity: 0, duration: .9, ease: 'power2.out' }, %.2f);"
        % (nid, arr))
    node_js.append(
        "      tl.to('#%s', { opacity: 1, duration: .3 }, %.2f);" % (nid, arr))
CLIP_DEFS = "\n".join(clip_defs)
NODE_HTML = "\n".join(node_html)
NODE_JS = "\n".join(node_js)

# ---------- 丝路地图（含地形，整体在 camera 内） ----------
MAP_HTML = """
        <div class="map-title">公元 260 年 <span class="mt-dot">·</span> 西行路线</div>
        <svg id="map" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice" data-layout-allow-overflow>
          <defs>
            <radialGradient id="lampgrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stop-color="#e3b341" stop-opacity=".26"/>
              <stop offset="55%" stop-color="#e3b341" stop-opacity=".08"/>
              <stop offset="100%" stop-color="#e3b341" stop-opacity="0"/>
            </radialGradient>
            <pattern id="sand" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="7" cy="9" r="1.1" fill="#3a3324"/>
              <circle cx="21" cy="20" r=".9" fill="#322c1f"/>
              <circle cx="14" cy="3" r=".7" fill="#40382a"/>
            </pattern>
__CLIPDEFS__
          </defs>

          <g id="camera">
            <!-- 底色 + 大漠肌理 -->
            <rect x="-400" y="-400" width="2800" height="2000" fill="#100e0a"/>
            <rect x="-400" y="-400" width="2800" height="2000" fill="url(#sand)"/>

            <!-- 祁连 → 天山 山脉（路线北侧） -->
            <path class="mtn" d="M 220,400 L 300,300 L 360,372 L 440,268 L 520,360 L 600,256 L 690,356 L 770,276 L 860,352 L 950,264 L 1040,344 L 1120,300 L 1120,420 L 220,420 Z"/>
            <!-- 黄河河谷（关中方向，右上） -->
            <path class="river" d="M 1280,470 C 1340,400 1300,320 1380,250"/>
            <!-- 于阗河（和田河，向北入大漠） -->
            <path class="river" d="M 360,560 C 352,486 384,430 366,356"/>
            <!-- 沙丘弧线（大漠南缘） -->
            <path class="dune" d="M 120,760 C 420,700 700,800 1000,724 C 1240,672 1460,740 1780,690"/>
            <path class="dune dune2" d="M 80,880 C 380,824 680,920 1000,846 C 1280,792 1520,862 1840,806"/>
            <!-- 绿洲 -->
            <circle class="oasis" cx="1280" cy="470" r="16"/>
            <circle class="oasis" cx="360" cy="560" r="20"/>
            <!-- 阳关 汉代烽燧 -->
            <g class="beacon"><rect x="688" y="452" width="22" height="28"/><path d="M 686,452 L 712,452 L 706,438 L 692,438 Z"/></g>

            <!-- 路：底（暗） -->
            <path class="route-base" d="M1560,520 L1280,470"/>
            <path class="route-base" d="M1280,470 L1000,440"/>
            <path class="route-base" d="M1000,440 L700,480"/>
            <path class="route-base" d="M700,480 C590,556 470,600 360,560"/>
            <!-- 路：亮（分段点亮） -->
            <path class="route-lit" id="seg1" pathLength="100" d="M1560,520 L1280,470"/>
            <path class="route-lit" id="seg2" pathLength="100" d="M1280,470 L1000,440"/>
            <path class="route-lit" id="seg3" pathLength="100" d="M1000,440 L700,480"/>
            <path class="route-lit" id="seg4" pathLength="100" d="M700,480 C590,556 470,600 360,560"/>

            <!-- 节点 -->
__NODES__

            <!-- 行者：一盏移动的灯火 -->
            <g id="walker">
              <circle class="lamp" r="190" fill="url(#lampgrad)"/>
              <circle r="8" fill="#e3b341"/>
              <circle r="16" fill="none" stroke="#e3b341" stroke-opacity=".45" stroke-width="2"/>
            </g>
          </g>
        </svg>
        <div class="map-notes">
          <span class="mn" id="mn1">没有徒弟四人</span>
          <span class="mn" id="mn2">没有白龙马</span>
          <span class="mn" id="mn3">更没有神仙护法</span>
        </div>
        <div class="map-dist" id="map-dist">一万多里 <span class="md-sep">·</span> 每一步都是拿命在赌</div>
"""
MAP_HTML = (MAP_HTML
            .replace("__CLIPDEFS__", CLIP_DEFS)
            .replace("__NODES__", NODE_HTML))

print("字幕 %d 句，逐字高亮 %d 字；节点 %d 个"
      % (len(sub_cues), len(sub_chars), len(NODES)))

# ---------- 场景专属 CSS（地图 / fx / 氛围；通用骨架与字幕由 theme 拼） ----------
ROOT_VARS = """      :root {
        --bg: #0d1117; --panel: #161b22; --line: #30363d;
        --blue: #1f6feb; --blue2: #58a6ff; --blue3: #79c0ff;
        --gold: #e3b341; --red: #f85149; --ink: #e6edf3; --mut: #8b949e;
        --serif: "NotoSerifSC", "Source Han Serif SC", "KaiTi", serif;
        --heavy: "HanSerifHeavy", "Source Han Serif SC", "NotoSerifSC", serif;
        --mono: "Consolas", "Courier New", monospace;
      }
"""

PROJECT_CSS = """

      /* ===== 地图 ===== */
      .map-title { position: absolute; left: 0; right: 0; top: 96px; text-align: center;
        font-family: var(--serif); font-weight: 300;
        font-size: 44px; color: var(--ink); letter-spacing: .22em; text-indent: .22em; }
      .map-title .mt-dot { color: var(--gold); padding: 0 6px; }
      #map { position: absolute; inset: 0; width: 1920px; height: 1080px; }
      .mtn { fill: #152128; stroke: #27414d; stroke-width: 1.5; opacity: .9; }
      .river { fill: none; stroke: #21506e; stroke-width: 3; stroke-linecap: round; opacity: .7; }
      .dune { fill: none; stroke: #2c2517; stroke-width: 2.4; opacity: .65; }
      .dune2 { stroke: #241e13; opacity: .5; }
      .oasis { fill: #2f6b3a; opacity: .4; }
      .beacon rect { fill: #4a3a1c; } .beacon path { fill: #5a4722; }
      .beacon { opacity: .8; }

      .route-base { fill: none; stroke: #21262d; stroke-width: 6; stroke-linecap: round; }
      .route-lit { fill: none; stroke: var(--gold); stroke-width: 6; stroke-linecap: round;
        stroke-dasharray: 100 100; stroke-dashoffset: 100;
        filter: drop-shadow(0 0 7px rgba(227,179,65,.5)); }
      .node circle { fill: #2a2e36; stroke: var(--blue2); stroke-width: 2; }
      .node .halo { fill: none; stroke: var(--gold); stroke-width: 2; opacity: 0; }
      .node text { fill: var(--ink); font-family: var(--heavy); font-weight: 900;
        font-size: 36px; text-anchor: middle; }
      #n-yu circle { stroke: var(--gold); stroke-width: 2.5; }

      .map-notes { position: absolute; left: 0; right: 0; bottom: 300px; text-align: center; }
      .mn { display: inline-block; margin: 0 24px; font-family: var(--serif);
        font-size: 38px; color: var(--mut); letter-spacing: .08em; }
      .map-dist { position: absolute; left: 0; right: 0; bottom: 232px; text-align: center;
        font-family: var(--heavy); font-weight: 900;
        font-size: 42px; color: var(--gold); letter-spacing: .1em;
        text-shadow: 0 0 40px rgba(227,179,65,.35); }
      .map-dist .md-sep { color: var(--mut); padding: 0 8px; }

      /* ===== WebGL fx 起幅 ===== */
      #fx { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;
        z-index: 40; pointer-events: none; display: none; }
      .fx-scene { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px;
        background: var(--bg); display: flex; flex-direction: column;
        align-items: center; justify-content: center; overflow: hidden; }
      .fx-warm { position: absolute; left: 0; top: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 50% 56%, rgba(227,179,65,.14), transparent 60%); }
      .fx-tag { font-family: var(--mono); font-size: 22px; letter-spacing: .5em;
        text-indent: .5em; color: var(--gold); opacity: .8; margin-bottom: 34px; }
      .fx-big { font-family: var(--heavy); font-weight: 900; font-size: 120px;
        color: var(--gold); letter-spacing: .12em; text-indent: .12em;
        text-shadow: 0 0 70px rgba(227,179,65,.4); }
      .fx-big2 { font-size: 200px; }
      .fx-rule { width: 220px; height: 2px; margin-top: 40px;
        background: linear-gradient(90deg, transparent, var(--gold), transparent); }
      .fx-sub { margin-top: 30px; font-family: var(--serif); font-size: 34px;
        color: var(--mut); letter-spacing: .2em; text-indent: .2em; }

      /* ===== 氛围层 ===== */
      #vignette { position: absolute; inset: 0; z-index: 30; pointer-events: none;
        background: radial-gradient(ellipse at center, transparent 52%, rgba(0,0,0,.55) 100%); }
      #grain { position: absolute; inset: 0; z-index: 31; pointer-events: none; opacity: .05;
        background-image:
          radial-gradient(rgba(255,255,255,.5) .5px, transparent .6px),
          radial-gradient(rgba(255,255,255,.35) .5px, transparent .6px);
        background-size: 3px 3px, 7px 7px;
        background-position: 0 0, 1px 2px; }"""

# ---------- 场景时间轴（静态，绝对秒） ----------
SCENE_JS = """
      // ===== camera tracking 运镜（pan + zoom；walker 保持黄金区） =====
      // 世界 P 映射屏幕：P*k + (x,y)。关键帧为 camera 的绝对 x/y/scale。
      tl.set('#camera', { x: -1338, y: -246, scale: 1.55, svgOrigin: '0 0' }, 0);
      tl.to('#camera', { x: -1290, y: -220, scale: 1.50, duration: 4.38, ease: 'sine.inOut' }, 0);
      tl.to('#camera', { x: -708,  y: -90,  scale: 1.35, duration: 1.42, ease: 'power1.inOut' }, 4.38);
      tl.to('#camera', { x: -250,  y: -5,   scale: 1.25, duration: .90, ease: 'power1.inOut' }, 5.80);
      tl.to('#camera', { x: 158,   y: -12,  scale: 1.16, duration: .90, ease: 'power1.inOut' }, 6.70);
      // 阳关短暂停顿 7.6→8.4，随后长段近景匀速 pan（与 seg4/walker 严格同步）；
      // 终点聚焦于阗，洛阳出发后留在身后，不再回画
      tl.to('#camera', { x: 406,   y: -99,  scale: 1.15, duration: 9.80, ease: 'none' }, 8.40);

      // ===== 地图元素初始态（显式 time 0；无 position 的 set 会被追加到时间轴末尾） =====
      tl.set('#seg1,#seg2,#seg3,#seg4', { strokeDashoffset: 100 }, 0);
      tl.set('#walker', { x: 1560, y: 520 }, 0);
      tl.set('.node', { opacity: .32 }, 0);
      tl.set('.map-notes, .map-dist, .map-title', { opacity: 0 }, 0);

      // ===== 标题（极慢淡入） =====
      tl.to('.map-title', { opacity: 1, y: -8, duration: .9, ease: 'power2.out' }, 1.3);

      // ===== 节点：地名 clip 擦入 + 光环 + 点亮 =====
__NODE_JS__

      // ===== 路线 + walker 同步西行 =====
      tl.to('#seg1', { strokeDashoffset: 0, duration: 1.4, ease: 'power1.inOut' }, 4.38);
      tl.to('#walker', { x: 1280, y: 470, duration: 1.4, ease: 'power1.inOut' }, 4.38);
      tl.to('#seg2', { strokeDashoffset: 0, duration: .90, ease: 'power1.inOut' }, 5.80);
      tl.to('#walker', { x: 1000, y: 440, duration: .90, ease: 'power1.inOut' }, 5.80);
      tl.to('#seg3', { strokeDashoffset: 0, duration: .90, ease: 'power1.inOut' }, 6.70);
      tl.to('#walker', { x: 700, y: 480, duration: .90, ease: 'power1.inOut' }, 6.70);
      // 阳关→于阗 大漠长段：匀速 9.8s
      tl.to('#seg4', { strokeDashoffset: 0, duration: 9.80, ease: 'none' }, 8.40);
      tl.to('#walker', { x: 360, y: 560, duration: 9.80, ease: 'none' }, 8.40);
      // 灯火呼吸（有界）
      tl.fromTo('#walker .lamp', { scale: .92 }, { scale: 1.12, duration: 2.6, ease: 'sine.inOut', repeat: 7, yoyo: true }, 2.0);

      // ===== 旁注（随口播） =====
      tl.to('#mn1', { opacity: 1, y: -10, duration: .55, ease: 'power2.out' }, 10.7);
      tl.to('#mn2', { opacity: 1, y: -10, duration: .55, ease: 'power2.out' }, 12.3);
      tl.to('#mn3', { opacity: 1, y: -10, duration: .55, ease: 'power2.out' }, 13.4);
      tl.to('#map-dist', { opacity: 1, duration: .8, ease: 'power2.out' }, 16.8);
"""
SCENE_JS = SCENE_JS.replace("__NODE_JS__", NODE_JS)

# ---------- WebGL cinematic-zoom 起幅（黑场 → 洛阳） ----------
FX_HTML = """
      <canvas id="fx" width="1920" height="1080"></canvas>
      <!-- 烘焙源（简单 div，仅供纹理，初始化后隐藏） -->
      <div id="f1" class="fx-scene">
        <div class="fx-tag">SILK ROAD · 丝 路</div>
        <div class="fx-big">公元二六〇年</div>
        <div class="fx-rule"></div>
      </div>
      <div id="f2" class="fx-scene">
        <div class="fx-warm"></div>
        <div class="fx-tag fx-tag2">起 点</div>
        <div class="fx-big fx-big2">洛阳</div>
        <div class="fx-sub">西行之路 · 由此启程</div>
      </div>
"""

# 主 timeline onUpdate 里驱动 fx（0–1.1s），之后隐藏 canvas
FX_JS = """
      // ===== 内联 WebGL cinematic-zoom 起幅 =====
      var fxCanvas = document.getElementById('fx');
      var gl = fxCanvas.getContext('webgl', { preserveDrawingBuffer: true });
      if (gl) {
        var FW = 1920, FH = 1080;
        fxCanvas.style.display = 'block';
        gl.viewport(0, 0, FW, FH);
        var fxTextures = {};
        function captureScene(sceneId) {
          var scene = document.getElementById(sceneId);
          var c = document.createElement('canvas');
          c.width = FW; c.height = FH;
          var ctx = c.getContext('2d');
          ctx.fillStyle = window.getComputedStyle(scene).backgroundColor;
          ctx.fillRect(0, 0, FW, FH);
          var sr = scene.getBoundingClientRect();
          var els = scene.querySelectorAll('*');
          for (var i = 0; i < els.length; i++) {
            var el = els[i], cs = window.getComputedStyle(el);
            if (cs.display === 'none' || cs.visibility === 'hidden') continue;
            var r = el.getBoundingClientRect();
            if (r.width < 1 || r.height < 1) continue;
            var x = r.left - sr.left, y = r.top - sr.top, w = r.width, h = r.height;
            ctx.save();
            ctx.globalAlpha = parseFloat(cs.opacity) || 1;
            var bg = cs.backgroundColor;
            if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
              ctx.fillStyle = bg; ctx.fillRect(x, y, w, h);
            }
            var hasChild = el.querySelector('div,span');
            var text = '';
            for (var j = 0; j < el.childNodes.length; j++)
              if (el.childNodes[j].nodeType === 3) text += el.childNodes[j].textContent;
            text = text.trim();
            if (text && !hasChild) {
              ctx.font = cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
              ctx.fillStyle = cs.color;
              ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
              ctx.fillText(text, x + w / 2, y + h / 2);
            }
            ctx.restore();
          }
          var tex = gl.createTexture();
          gl.bindTexture(gl.TEXTURE_2D, tex);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
          gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, c);
          fxTextures[sceneId] = tex;
        }
        var vertSrc =
          'attribute vec2 a_pos; varying vec2 v_uv; void main(){' +
          'v_uv=a_pos*0.5+0.5; v_uv.y=1.0-v_uv.y; gl_Position=vec4(a_pos,0,1);}';
        var quadBuf = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
        gl.bufferData(gl.ARRAY_BUFFER,
          new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
        function compileShader(src, type) {
          var s = gl.createShader(type);
          gl.shaderSource(s, src); gl.compileShader(s);
          if (!gl.getShaderParameter(s, gl.COMPILE_STATUS))
            console.error('Shader:', gl.getShaderInfoLog(s));
          return s;
        }
        function mkProg(fragSrc) {
          var p = gl.createProgram();
          gl.attachShader(p, compileShader(vertSrc, gl.VERTEX_SHADER));
          gl.attachShader(p, compileShader(fragSrc, gl.FRAGMENT_SHADER));
          gl.linkProgram(p);
          if (!gl.getProgramParameter(p, gl.LINK_STATUS))
            console.error('Link:', gl.getProgramInfoLog(p));
          return p;
        }
        var H = 'precision mediump float; varying vec2 v_uv;' +
          'uniform sampler2D u_from,u_to; uniform float u_progress; uniform vec2 u_resolution;\\n';
        var progPass = mkProg(H + 'void main(){gl_FragColor=texture2D(u_from,v_uv);}');
        var progTrans = mkProg(H +
          'void main(){vec2 d=v_uv-vec2(.5);float fromS=u_progress*.08;float toS=(1.-u_progress)*.06;' +
          'float fr=0.,fg=0.,fb=0.;for(int i=0;i<12;i++){float f=float(i)/12.;' +
          'fr+=texture2D(u_from,v_uv-d*(fromS*1.06)*f).r;fg+=texture2D(u_from,v_uv-d*fromS*f).g;' +
          'fb+=texture2D(u_from,v_uv-d*(fromS*.94)*f).b;}vec3 fromBl=vec3(fr,fg,fb)/12.;' +
          'float tr=0.,tg=0.,tb=0.;for(int i=0;i<12;i++){float f=float(i)/12.;' +
          'tr+=texture2D(u_to,v_uv+d*(toS*1.06)*f).r;tg+=texture2D(u_to,v_uv+d*toS*f).g;' +
          'tb+=texture2D(u_to,v_uv+d*(toS*.94)*f).b;}vec3 toBl=vec3(tr,tg,tb)/12.;' +
          'gl_FragColor=vec4(mix(fromBl,toBl,u_progress),1.);}');
        function paint(prog, a, b, p) {
          gl.useProgram(prog);
          gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, a);
          gl.uniform1i(gl.getUniformLocation(prog, 'u_from'), 0);
          gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, b);
          gl.uniform1i(gl.getUniformLocation(prog, 'u_to'), 1);
          gl.uniform1f(gl.getUniformLocation(prog, 'u_progress'), p);
          gl.uniform2f(gl.getUniformLocation(prog, 'u_resolution'), FW, FH);
          var pos = gl.getAttribLocation(prog, 'a_pos');
          gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
          gl.enableVertexAttribArray(pos);
          gl.vertexAttribPointer(pos, 2, gl.FLOAT, false, 0, 0);
          gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
        }
        function easeInOut(p){ return p<.5 ? 2*p*p : 1-Math.pow(-2*p+2,2)/2; }
        captureScene('f1'); captureScene('f2');
        document.getElementById('f1').style.display = 'none';
        document.getElementById('f2').style.display = 'none';
        paint(progPass, fxTextures['f1'], fxTextures['f1'], 0);
        tl.eventCallback('onUpdate', function () {
          var t = tl.time();
          console.log('[fxup] t=' + t.toFixed(3) + ' disp=' + fxCanvas.style.display);
          if (t < .45) {
            fxCanvas.style.display = 'block';
            paint(progPass, fxTextures['f1'], fxTextures['f1'], 0);
          } else if (t < 1.05) {
            paint(progTrans, fxTextures['f1'], fxTextures['f2'], easeInOut((t-.45)/.6));
          } else if (t < 1.15) {
            paint(progPass, fxTextures['f2'], fxTextures['f2'], 0);
          } else {
            fxCanvas.style.display = 'none';
          }
        });
        window.__fx = { gl: gl, tex: fxTextures, FW: FW, FH: FH, canvas: fxCanvas,
          progPass: progPass, progTrans: progTrans };
      }
"""

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/map-demo.wav", TOTAL),
    "",
    render_scenes([Scene("sc-map", 0.0, TOTAL, MAP_HTML)]),
    "",
    '      <div id="subshade"></div>',
    '      <div id="subbar">',
    frag.html,
    '      </div>',
    "",
    FX_HTML,
    "",
    '      <div id="vignette"></div>',
    '      <div id="grain"></div>',
])
js = (frag.js + "\n" + SCENE_JS + "\n" + frag.word_js + "\n" + FX_JS)

html = render_page(total=TOTAL,
                   css=assemble_css(THEME, PROJECT_CSS, root_vars=ROOT_VARS),
                   body=body, js=js)
io.open(P.index_html, "w", encoding="utf-8").write(html)
print("已生成 index.html（%.2f 秒，%d 句字幕）" % (TOTAL, len(sub_cues)))
