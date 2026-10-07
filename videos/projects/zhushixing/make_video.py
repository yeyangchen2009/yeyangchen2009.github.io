# -*- coding: utf-8 -*-
"""朱士行（素版）成片生成器。

本片独有：11 幕 body、S1…S11 专属 CSS、场景时间轴（含 S5 丝路地图
stroke-dashoffset 点亮）。页面骨架 / 主题 / 字幕 / clip 外壳全部复用
videopipe。★残卷 blur 是设计语言，忠实保留不去掉。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       DARK_GOLD_GH)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars, TOTAL = data["cues"], data["chars"], data["duration"]
THEME = DARK_GOLD_GH

# ---------- 11 幕 ----------
SCENES = [

# S1 玄奘钩子 0–11.6
Scene("sc-hook", 0.0, 11.6, """
        <div class="hook-xuan">玄奘</div>
        <div class="hook-sub">《西游记》 · 唐僧师徒 · 九九八十一难</div>
        <div class="hook-ring r1"></div>
        <div class="hook-ring r2"></div>
"""),

# S2 翻转 11.4–22.4
Scene("sc-flip", 11.4, 22.4, """
        <div class="flip-lead">第一个西行求法的中国和尚</div>
        <div class="flip-big"><span class="flip-300">300</span><span class="flip-unit">年</span></div>
        <div class="flip-pre">比玄奘，早了整整三百多年</div>
        <div class="flip-note">——而且他这一辈子，连印度都没走到</div>
"""),

# S3 人物名片 22.3–39.6
Scene("sc-card", 22.3, 39.6, """
        <div class="idcard">
          <div class="id-name">朱士行</div>
          <div class="id-era">三国 · 魏　颍川人</div>
          <div class="id-badge">中国第一位依照羯磨正式受戒出家的汉僧</div>
          <div class="id-divider"></div>
          <div class="id-old">在那以前：剃个头、披件袈裟<span class="id-dim">，没有完整受戒仪式</span></div>
          <div class="id-old id-old2">算不上真正的比丘</div>
        </div>
"""),

# S4 残卷梗阻 39.5–68.4
Scene("sc-scroll", 39.5, 68.4, """
        <div class="scroll-card">
          <div class="scroll-title">《道行般若经》</div>
          <div class="scroll-text">
            <span class="ln">识　性　□　游　□　竺</span>
            <span class="ln blur1">萨　芸　若　波　罗</span>
            <span class="ln">道　□　行　□　无　所</span>
            <span class="ln blur2">从　法　□　意　□</span>
            <span class="ln">生　□　□　断……</span>
          </div>
        </div>
        <div class="scroll-words">
          <div class="sw1">译人对中文生疏 · 又硬又涩</div>
          <div class="sw2">许多地方前后不接、道理不通</div>
          <div class="sw3">删节了？还是手里只是个简略抄本？</div>
          <div class="sw4">传闻：西域或有一部更完整的全本</div>
        </div>
"""),

# S5 ★丝路地图 68.2–90.3
# 节点（东→西，右→左）：洛阳1560,520 关中1280,470 河西1000,440 阳关700,480 于阗360,560
Scene("sc-map", 68.2, 90.3, """
        <div class="map-title">公元 260 年 · 西行路线</div>
        <svg id="map" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid meet">
          <!-- 大漠底纹（沙漠边缘） -->
          <path id="desert" d="M700,520 C600,600 470,640 360,620" fill="none"
                stroke="#30363d" stroke-width="2" stroke-dasharray="4 14"/>
          <!-- 路：底（暗） -->
          <path class="route-base" d="M1560,520 L1280,470" />
          <path class="route-base" d="M1280,470 L1000,440" />
          <path class="route-base" d="M1000,440 L700,480" />
          <path class="route-base" d="M700,480 C590,560 470,600 360,560" />
          <!-- 路：亮（分段点亮） -->
          <path class="route-lit" id="seg1" pathLength="100" d="M1560,520 L1280,470" />
          <path class="route-lit" id="seg2" pathLength="100" d="M1280,470 L1000,440" />
          <path class="route-lit" id="seg3" pathLength="100" d="M1000,440 L700,480" />
          <path class="route-lit" id="seg4" pathLength="100" d="M700,480 C590,560 470,600 360,560" />
          <!-- 节点 -->
          <g class="node" id="n-luo"><circle cx="1560" cy="520" r="9"/><text x="1560" y="486">洛阳</text></g>
          <g class="node" id="n-guan"><circle cx="1280" cy="470" r="9"/><text x="1280" y="436">关中</text></g>
          <g class="node" id="n-he"><circle cx="1000" cy="440" r="9"/><text x="1000" y="406">河西</text></g>
          <g class="node" id="n-yang"><circle cx="700" cy="480" r="9"/><text x="700" y="446">阳关</text></g>
          <g class="node" id="n-yu"><circle cx="360" cy="560" r="10"/><text x="360" y="612">于阗</text></g>
          <!-- 行者：基点放不动画外层 g，内层 #walker 交 GSAP -->
          <g transform="translate(1560,520)">
            <g id="walker">
              <circle r="9" fill="#f85149"/>
              <circle r="17" fill="none" stroke="#e3b341" stroke-opacity=".55" stroke-width="2"/>
            </g>
          </g>
        </svg>
        <div class="map-notes">
          <span class="mn" id="mn1">没有徒弟四人</span>
          <span class="mn" id="mn2">没有白龙马</span>
          <span class="mn" id="mn3">更没有神仙护法</span>
        </div>
        <div class="map-dist" id="map-dist">一万多里 · 每一步都是拿命在赌</div>
"""),

# S6 于阗得经 90.1–103.8
Scene("sc-sutra", 90.1, 103.8, """
        <div class="sutra-glow"></div>
        <div class="sutra-place">于阗 · 得梵本</div>
        <div class="sutra-data">
          <div class="sd" id="sd1"><div class="sd-n">大品</div><div class="sd-l">般若经</div></div>
          <div class="sd" id="sd2"><div class="sd-n">九十</div><div class="sd-l">章</div></div>
          <div class="sd" id="sd3"><div class="sd-n">25000</div><div class="sd-l">颂</div></div>
        </div>
        <div class="sutra-note">当地有一派僧人，不愿经本外传</div>
"""),

# S7 投火 103.6–113.0
Scene("sc-fire", 103.6, 113.0, """
        <div class="fire-wrap">
          <div class="flame f1"></div>
          <div class="flame f2"></div>
          <div class="flame f3"></div>
          <div class="sutra-book">梵本</div>
        </div>
        <div class="fire-text">投之火中，火即自灭</div>
        <div class="fire-note">灵不灵验另说 —— 但可以想见当年这趟事有多难</div>
"""),

# S8 老殁 112.9–130.7
Scene("sc-death", 112.9, 130.7, """
        <svg class="death-map" viewBox="0 0 1920 1080">
          <path class="droute" d="M1560,520 L1280,470 L1000,440 L700,480 C590,560 470,600 360,560"/>
          <circle class="dn dim" cx="1560" cy="520" r="8"/>
          <circle class="dn dim" cx="1280" cy="470" r="8"/>
          <circle class="dn dim" cx="1000" cy="440" r="8"/>
          <circle class="dn dim" cx="700" cy="480" r="8"/>
          <circle class="dn hot" id="d-yu" cx="360" cy="560" r="11"/>
        </svg>
        <div class="death-main">殁于于阗<span class="death-age">年八十</span></div>
        <div class="death-sub">弟子护送梵本东归 · 自己再没走回洛阳</div>
        <div class="death-sub2">他到死，都没能亲眼看见这部经被翻成中文</div>
"""),

# S9 放光流通 128.9–146.6
Scene("sc-spread", 128.9, 146.6, """
        <div class="spread-center">
          <div class="ripple" id="rp1"></div>
          <div class="ripple" id="rp2"></div>
          <div class="ripple" id="rp3"></div>
          <div class="ripple" id="rp4"></div>
          <div class="spread-dot"></div>
          <div class="spread-name">洛阳</div>
        </div>
        <div class="spread-title">《放光般若经》</div>
        <div class="spread-lines">
          <div class="sl" id="sl1">译本一出 · 立刻风行全国</div>
          <div class="sl" id="sl2">鸠摩罗什来华之前，中国最流通的佛经</div>
          <div class="sl" id="sl3">高僧道安，晚年几乎每年都要讲一遍</div>
        </div>
"""),

# S10 程序员接口文档 146.5–175.8
Scene("sc-code", 146.5, 175.8, """
        <div class="code-bridge">他取回来的东西，滋养了往后一两百年的中国思想</div>
        <div class="terminal" id="terminal">
          <div class="term-bar"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
            <span class="term-file">prajna-api.md</span><span class="term-tag">auto-generated · 疑似截断</span></div>
          <pre class="term-body"><span class="c-cmd">GET /api/prajna/dao-xing</span>
<span class="c-punc">{</span>
  <span class="c-key">"五阴"</span>: <span class="c-bad">??,</span>        <span class="c-com">// 字缺</span>
  <span class="c-key">"本无"</span>: <span class="c-bad">██,</span>      <span class="c-com">// 前后不接</span>
  <span class="c-key">"道行"</span>: <span class="c-bad">~~又硬又涩~~</span>
  <span class="c-trunc">"...（内容疑似被截断）</span>
<span class="c-punc">}</span></pre>
        </div>
        <div class="code-actions">
          <span class="ca" id="ca1">买一张单程票</span>
          <span class="ca" id="ca2">飞一趟总部</span>
          <span class="ca" id="ca3">把最原始资料亲手抄回</span>
        </div>
        <div class="code-cost">这趟出差有一万多里 · 最后，他把命留在了那儿</div>
"""),

# S11 格言＋抛问 175.7–186.73
Scene("sc-end", 175.7, TOTAL, """
        <div class="end-saying" id="end-saying">有些人种树<br/>从一开始，就不是为了自己乘凉</div>
        <div class="end-ask" id="end-ask">
          <div class="ea-lead">所以我想问你一句 ——</div>
          <div class="ea-q">如果一件事，你明知道自己等不到结果的那一天，</div>
          <div class="ea-q ea-q2">你，还会选择出发吗？</div>
        </div>
"""),
]

# ---------- 场景专属 CSS（S1…S11；通用骨架/字幕由 theme 拼） ----------
PROJECT_CSS = """

      /* ===== S1 玄奘 ===== */
      .hook-xuan {
        position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:150px; color:#e6edf3; letter-spacing:.2em; text-indent:.2em;
        text-shadow:0 0 60px rgba(139,148,158,.35);
      }
      .hook-sub {
        position:absolute; left:0; right:0; top:520px; text-align:center;
        font-size:40px; color:#8b949e; letter-spacing:.28em; text-indent:.28em;
      }
      .hook-ring {
        position:absolute; left:50%; top:375px; width:340px; height:340px;
        margin-left:-170px; margin-top:-0px; border:1px solid rgba(88,166,255,.35);
        border-radius:50%;
      }
      .hook-ring.r2 { width:480px; height:480px; margin-left:-240px; border-color:rgba(88,166,255,.18); }

      /* ===== S2 翻转 ===== */
      .flip-lead { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:52px; color:#c9d1d9; letter-spacing:.12em; }
      .flip-big { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .flip-300 { font-size:300px; color:#e3b341; font-family:"Mono",monospace;
        text-shadow:0 0 80px rgba(227,179,65,.4); line-height:1; }
      .flip-unit { font-size:120px; color:#e3b341; margin-left:10px; }
      .flip-pre { position:absolute; left:0; right:0; top:690px; text-align:center;
        font-size:50px; color:#e6edf3; letter-spacing:.1em; }
      .flip-note { position:absolute; left:0; right:0; top:780px; text-align:center;
        font-size:38px; color:#8b949e; letter-spacing:.08em; }

      /* ===== S3 名片 ===== */
      .idcard { position:absolute; left:50%; top:170px; transform:translateX(-50%);
        width:1080px; padding:60px 70px 56px; background:#161b22;
        border:1px solid #30363d; border-radius:18px; text-align:center; }
      .id-name { font-size:96px; color:#e6edf3; letter-spacing:.3em; text-indent:.3em; }
      .id-era { margin-top:14px; font-size:34px; color:#8b949e; letter-spacing:.2em; }
      .id-badge { margin:36px auto 0; padding:22px 20px; background:rgba(31,111,235,.14);
        border:1px solid rgba(88,166,255,.4); border-radius:12px;
        font-size:42px; color:#79c0ff; letter-spacing:.06em; }
      .id-divider { margin:40px auto 30px; width:120px; border-top:1px solid #30363d; }
      .id-old { font-size:38px; color:#c9d1d9; letter-spacing:.05em; }
      .id-dim { color:#8b949e; }
      .id-old2 { margin-top:16px; color:#e3b341; font-size:40px; }

      /* ===== S4 残卷 ===== */
      .scroll-card { position:absolute; left:200px; top:200px; width:520px;
        padding:44px 40px; background:#161b22; border:1px solid #30363d; border-radius:14px; }
      .scroll-title { text-align:center; font-size:42px; color:#e3b341;
        letter-spacing:.2em; text-indent:.2em; margin-bottom:30px; }
      .scroll-text .ln { display:block; font-size:40px; color:#c9d1d9;
        letter-spacing:.32em; line-height:1.5; text-align:center; }
      .scroll-text .blur1 { filter:blur(1.6px); color:#8b949e; }
      .scroll-text .blur2 { filter:blur(2.4px); color:#8b949e; }
      .scroll-words { position:absolute; left:800px; top:230px; right:200px; }
      .scroll-words > div { font-size:42px; color:#e6edf3; line-height:1.9; letter-spacing:.05em; }
      .sw2 { color:#d2a8a8; }
      .sw3 { color:#e3b341; }
      .sw4 { color:#79c0ff; }

      /* ===== S5 地图 ===== */
      .map-title { position:absolute; left:0; right:0; top:110px; text-align:center;
        font-size:46px; color:#e6edf3; letter-spacing:.2em; text-indent:.2em; }
      #map { position:absolute; inset:0; width:1920px; height:1080px; }
      .route-base { fill:none; stroke:#21262d; stroke-width:6; stroke-linecap:round; }
      .route-lit { fill:none; stroke:#e3b341; stroke-width:6; stroke-linecap:round;
        stroke-dasharray:100 100; stroke-dashoffset:100; }
      .node circle { fill:#30363d; stroke:#58a6ff; stroke-width:2; }
      .node text { fill:#e6edf3; font-size:34px; text-anchor:middle; }
      #n-yu circle { fill:#30363d; stroke:#e3b341; stroke-width:2.5; }
      .map-notes { position:absolute; left:0; right:0; bottom:300px; text-align:center; }
      .mn { display:inline-block; margin:0 22px; font-size:36px; color:#8b949e; }
      .map-dist { position:absolute; left:0; right:0; bottom:235px; text-align:center;
        font-size:40px; color:#e3b341; letter-spacing:.1em; }

      /* ===== S6 得经 ===== */
      .sutra-glow { position:absolute; left:50%; top:430px; transform:translate(-50%,-50%);
        width:560px; height:560px; border-radius:50%;
        background:radial-gradient(circle, rgba(227,179,65,.28), transparent 65%); }
      .sutra-place { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:48px; color:#e6edf3; letter-spacing:.2em; text-indent:.2em; }
      .sutra-data { position:absolute; left:0; right:0; top:380px; text-align:center; }
      .sd { display:inline-block; width:300px; margin:0 18px; padding:34px 10px;
        background:#161b22; border:1px solid rgba(227,179,65,.45); border-radius:14px; }
      .sd-n { font-size:56px; color:#e3b341; font-family:"Mono",monospace; }
      .sd-l { margin-top:8px; font-size:34px; color:#c9d1d9; }
      .sutra-note { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:36px; color:#8b949e; }

      /* ===== S7 投火 ===== */
      .fire-wrap { position:absolute; left:50%; top:340px; transform:translateX(-50%);
        width:240px; height:300px; }
      .flame { position:absolute; bottom:30px; left:50%; width:120px; height:200px;
        margin-left:-60px; border-radius:60% 60% 55% 55%; transform-origin:center bottom;
        background:radial-gradient(ellipse at 50% 80%, #ffd166 0%, #ef6c00 55%, rgba(180,40,0,.0) 80%);
        opacity:.85;
      }
      .flame.f2 { width:90px; height:160px; margin-left:-45px; opacity:.7; }
      .flame.f3 { width:64px; height:120px; margin-left:-32px;
        background:radial-gradient(ellipse at 50% 80%, #fff3c4 0%, #ffb703 60%, rgba(255,150,0,0) 85%); }
      .sutra-book { position:absolute; bottom:0; left:50%; transform:translateX(-50%);
        width:120px; height:46px; line-height:46px; text-align:center;
        background:#21262d; border:1px solid #58a6ff; border-radius:6px;
        font-size:30px; color:#c9d1d9; }
      .fire-text { position:absolute; left:0; right:0; top:670px; text-align:center;
        font-size:52px; color:#e6edf3; letter-spacing:.15em; }
      .fire-note { position:absolute; left:0; right:0; top:760px; text-align:center;
        font-size:36px; color:#8b949e; }

      /* ===== S8 老殁 ===== */
      .death-map { position:absolute; inset:0; width:1920px; height:1080px; opacity:.8; }
      .droute { fill:none; stroke:#30363d; stroke-width:5; stroke-linecap:round; }
      .dn.dim { fill:#30363d; stroke:#484f58; stroke-width:2; }
      .dn.hot { fill:#6e3a3a; stroke:#f85149; stroke-width:2.5; }
      .death-main { position:absolute; left:0; right:0; top:330px; text-align:center;
        font-size:130px; color:#e6edf3; letter-spacing:.15em; }
      .death-age { font-size:80px; color:#8b949e; margin-left:40px; }
      .death-sub { position:absolute; left:0; right:0; top:560px; text-align:center;
        font-size:42px; color:#c9d1d9; }
      .death-sub2 { position:absolute; left:0; right:0; top:640px; text-align:center;
        font-size:40px; color:#f85149; }

      /* ===== S9 流通 ===== */
      .spread-center { position:absolute; left:50%; top:400px; transform:translate(-50%,-50%);
        width:20px; height:20px; }
      .ripple { position:absolute; left:50%; top:50%; width:300px; height:300px;
        margin:-150px 0 0 -150px; border:2px solid rgba(227,179,65,.6); border-radius:50%; }
      .spread-dot { position:absolute; left:50%; top:50%; width:22px; height:22px;
        margin:-11px 0 0 -11px; background:#e3b341; border-radius:50%; }
      .spread-name { position:absolute; left:50%; top:50%; margin:24px 0 0 -40px;
        width:80px; text-align:center; font-size:32px; color:#e6edf3; }
      .spread-title { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:72px; color:#e3b341; letter-spacing:.2em; text-indent:.2em; }
      .spread-lines { position:absolute; left:0; right:0; top:560px; text-align:center; }
      .spread-lines .sl { font-size:40px; color:#e6edf3; line-height:1.8; }

      /* ===== S10 代码 ===== */
      .code-bridge { position:absolute; left:0; right:0; top:200px; text-align:center;
        font-size:42px; color:#8b949e; }
      .terminal { position:absolute; left:50%; top:250px; transform:translateX(-50%);
        width:1180px; background:#0d1117; border:1px solid #30363d; border-radius:12px;
        box-shadow:0 30px 80px rgba(0,0,0,.5); overflow:hidden; }
      .term-bar { padding:16px 22px; background:#161b22; border-bottom:1px solid #30363d; }
      .dot { display:inline-block; width:14px; height:14px; border-radius:50%; margin-right:8px; }
      .dot.red{background:#f85149;} .dot.yellow{background:#d29922;} .dot.green{background:#3fb950;}
      .term-file { margin-left:18px; color:#c9d1d9; font-size:28px; font-family:"Mono",monospace; }
      .term-tag { float:right; color:#8b949e; font-size:24px; font-family:"Mono",monospace; }
      .term-body { padding:30px 34px 34px; font-family:"Mono",monospace; font-size:34px;
        line-height:1.7; color:#c9d1d9; }
      .c-cmd { color:#79c0ff; }
      .c-key { color:#79c0ff; }
      .c-punc { color:#8b949e; }
      .c-bad { color:#f85149; }
      .c-com { color:#6e7681; }
      .c-trunc { color:#f85149; }
      .code-actions { position:absolute; left:0; right:0; top:730px; text-align:center; }
      .ca { display:inline-block; margin:0 16px; padding:16px 30px;
        background:rgba(31,111,235,.14); border:1px solid rgba(88,166,255,.4);
        border-radius:10px; font-size:36px; color:#79c0ff; }
      .code-cost { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:38px; color:#e3b341; }

      /* ===== S11 结尾 ===== */
      .end-saying { position:absolute; left:0; right:0; top:330px; text-align:center;
        font-size:78px; color:#e3b341; line-height:1.5; letter-spacing:.08em; }
      .end-ask { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .ea-lead { font-size:42px; color:#8b949e; margin-bottom:40px; }
      .ea-q { font-size:58px; color:#e6edf3; line-height:1.6; letter-spacing:.04em; }
      .ea-q2 { color:#e3b341; font-size:66px; margin-top:18px; }"""

# ---------- 场景时间轴（静态，绝对秒） ----------
SCENE_JS = """
      // ===== 场景统一：入场淡入 / 出场淡出（交叠期交叉淡化）=====
      tl.fromTo('#sc-hook > .scene-inner',   {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 0.0);
      tl.to('#sc-hook > .scene-inner',   {opacity:0,duration:.45,ease:'power1.in'}, 11.15);

      // ===== S1 玄奘：环呼吸 =====
      tl.from('.hook-xuan', {opacity:0, scale:.92, duration:1.2, ease:'power2.out'}, .3);
      tl.from('.hook-sub', {opacity:0, y:24, duration:1.0, ease:'power2.out'}, 1.4);
      tl.fromTo('.hook-ring', {scale:.6, opacity:.0}, {scale:1, opacity:.55, duration:3.2, ease:'power2.out', repeat:1, yoyo:true}, .8);

      // ===== S2 翻转 =====
      tl.fromTo('#sc-flip > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 11.4);
      tl.to('#sc-flip > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 21.95);
      tl.from('.flip-lead', {opacity:0, y:30, duration:.8, ease:'power2.out'}, 11.9);
      tl.from('.flip-big', {opacity:0, scale:.7, duration:.9, ease:'back.out(1.6)'}, 13.0);
      tl.from('.flip-pre', {opacity:0, y:20, duration:.7, ease:'power2.out'}, 14.6);
      tl.from('.flip-note', {opacity:0, y:18, duration:.7, ease:'power2.out'}, 18.6);

      // ===== S3 名片 =====
      tl.fromTo('#sc-card > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 22.3);
      tl.to('#sc-card > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 39.15);
      tl.from('.idcard', {opacity:0, y:40, duration:.9, ease:'power2.out'}, 22.8);
      tl.from('.id-badge', {opacity:0, duration:.8, ease:'power2.out'}, 26.0);
      tl.from('.id-old', {opacity:0, y:14, duration:.6, ease:'power2.out'}, 32.0);
      tl.from('.id-old2', {opacity:0, duration:.6, ease:'power2.out'}, 37.9);

      // ===== S4 残卷 =====
      tl.fromTo('#sc-scroll > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 39.5);
      tl.to('#sc-scroll > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 67.95);
      tl.from('.scroll-card', {opacity:0, x:-40, duration:.9, ease:'power2.out'}, 40.0);
      tl.from('.sw1', {opacity:0, y:16, duration:.6}, 49.3);
      tl.to('.sw1', {autoAlpha:0, duration:.4}, 52.6);
      tl.from('.sw2', {opacity:0, y:16, duration:.6}, 52.9);
      tl.to('.sw2', {autoAlpha:0, duration:.4}, 56.0);
      tl.from('.sw3', {opacity:0, y:16, duration:.6}, 56.3);
      tl.to('.sw3', {autoAlpha:0, duration:.4}, 62.0);
      tl.from('.sw4', {opacity:0, y:16, duration:.7}, 63.2);

      // ===== S5 丝路地图 =====
      tl.fromTo('#sc-map > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 68.2);
      tl.to('#sc-map > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 89.85);
      tl.from('.map-title', {opacity:0, y:-20, duration:.7}, 68.7);
      // 路线分段初始隐藏
      tl.set('#seg1,#seg2,#seg3,#seg4', {strokeDashoffset:100});
      tl.set('#walker', {x:0, y:0});
      // 节点初始暗
      tl.set('.node', {opacity:.35});
      // 洛阳 72.58
      tl.to('#n-luo', {opacity:1, duration:.3}, 72.58);
      tl.to('#seg1', {strokeDashoffset:0, duration:1.4, ease:'power1.inOut'}, 72.58);
      tl.to('#walker', {x:-280, y:-50, duration:1.4, ease:'power1.inOut'}, 72.58);
      // 过关中 74.0
      tl.to('#n-guan', {opacity:1, duration:.25}, 74.0);
      tl.to('#seg2', {strokeDashoffset:0, duration:.85, ease:'power1.inOut'}, 74.0);
      tl.to('#walker', {x:-560, y:-80, duration:.85, ease:'power1.inOut'}, 74.0);
      // 走河西 74.9
      tl.to('#n-he', {opacity:1, duration:.25}, 74.9);
      tl.to('#seg3', {strokeDashoffset:0, duration:.85, ease:'power1.inOut'}, 74.9);
      tl.to('#walker', {x:-860, y:-40, duration:.85, ease:'power1.inOut'}, 74.9);
      // 出阳关 75.8
      tl.to('#n-yang', {opacity:1, duration:.25}, 75.8);
      // 大漠段缓慢 76.6 → 86.4
      tl.to('#seg4', {strokeDashoffset:0, duration:9.6, ease:'none'}, 76.6);
      tl.to('#walker', {x:-1200, y:40, duration:9.6, ease:'none'}, 76.6);
      // 到于阗 86.4
      tl.fromTo('#n-yu', {scale:.8}, {scale:1.25, duration:.5, yoyo:true, repeat:1}, 86.4);
      tl.to('#n-yu', {opacity:1, duration:.3}, 86.4);
      // 旁注
      tl.from('#mn1', {opacity:0, y:12, duration:.5}, 78.9);
      tl.from('#mn2', {opacity:0, y:12, duration:.5}, 80.5);
      tl.from('#mn3', {opacity:0, y:12, duration:.5}, 81.6);
      tl.from('#map-dist', {opacity:0, duration:.7}, 85.0);

      // ===== S6 得经 =====
      tl.fromTo('#sc-sutra > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 90.1);
      tl.to('#sc-sutra > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 103.35);
      tl.from('.sutra-place', {opacity:0, y:-16, duration:.7}, 90.6);
      tl.fromTo('.sutra-glow', {opacity:0, scale:.6}, {opacity:.9, scale:1, duration:1.2, ease:'power2.out'}, 90.8);
      tl.from('#sd1', {opacity:0, y:30, scale:.8, duration:.7, ease:'back.out(1.5)'}, 92.6);
      tl.from('#sd2', {opacity:0, y:30, scale:.8, duration:.6, ease:'back.out(1.5)'}, 94.3);
      tl.from('#sd3', {opacity:0, y:30, scale:.8, duration:.6, ease:'back.out(1.5)'}, 95.3);
      tl.from('.sutra-note', {opacity:0, duration:.7}, 98.2);

      // ===== S7 投火 =====
      tl.fromTo('#sc-fire > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 103.6);
      tl.to('#sc-fire > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 112.55);
      tl.from('.fire-text', {opacity:0, duration:.7}, 104.0);
      tl.from('.fire-note', {opacity:0, duration:.7}, 108.6);
      tl.fromTo('.flame', {scaleY:.8, scaleX:.9, opacity:.75}, {scaleY:1.12, scaleX:1.05, opacity:1, duration:.55, ease:'sine.inOut', repeat:-1, yoyo:true}, 103.8);
      tl.from('.sutra-book', {opacity:0, y:14, duration:.6}, 104.2);

      // ===== S8 老殁 =====
      tl.fromTo('#sc-death > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 112.9);
      tl.to('#sc-death > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 128.55);
      tl.from('.death-map', {opacity:0, duration:1.0}, 113.3);
      tl.from('.death-main', {opacity:0, y:26, duration:.9, ease:'power2.out'}, 115.0);
      tl.to('.death-main', {autoAlpha:0, duration:.5, ease:'power1.in'}, 127.9);
      tl.from('.death-sub', {opacity:0, duration:.7}, 117.0);
      tl.from('.death-sub2', {opacity:0, duration:.8}, 123.0);
      tl.to('#d-yu', {attr:{r:16}, duration:.8, yoyo:true, repeat:3}, 114.0);

      // ===== S9 流通 =====
      tl.fromTo('#sc-spread > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 128.9);
      tl.to('#sc-spread > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 146.15);
      tl.from('.spread-title', {opacity:0, y:-18, duration:.8}, 132.6);
      tl.fromTo('#rp1', {scale:.1, opacity:.6}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 129.2);
      tl.fromTo('#rp2', {scale:.1, opacity:.55}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 130.3);
      tl.fromTo('#rp3', {scale:.1, opacity:.5}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 131.4);
      tl.fromTo('#rp4', {scale:.1, opacity:.45}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 132.5);
      tl.from('.spread-dot', {scale:0, duration:.6, ease:'back.out(2)'}, 129.2);
      tl.from('.spread-name', {opacity:0, duration:.6}, 129.8);
      tl.from('#sl1', {opacity:0, y:16, duration:.6}, 135.2);
      tl.from('#sl2', {opacity:0, y:16, duration:.6}, 138.8);
      tl.from('#sl3', {opacity:0, y:16, duration:.6}, 141.1);

      // ===== S10 代码 =====
      tl.fromTo('#sc-code > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 146.5);
      tl.to('#sc-code > .scene-inner', {opacity:0,duration:.45,ease:'power1.in'}, 175.35);
      tl.from('.code-bridge', {opacity:0, duration:.8}, 146.9);
      tl.to('.code-bridge', {autoAlpha:0, duration:.4}, 151.0);
      tl.from('#terminal', {opacity:0, y:40, scale:.96, duration:.8, ease:'power2.out'}, 151.4);
      tl.from('#ca1', {opacity:0, y:18, duration:.5}, 164.0);
      tl.from('#ca2', {opacity:0, y:18, duration:.5}, 166.5);
      tl.from('#ca3', {opacity:0, y:18, duration:.5}, 167.7);
      tl.to('#ca1,#ca2,#ca3', {autoAlpha:0, y:-14, duration:.4, ease:'power1.in'}, 171.0);
      tl.from('.code-cost', {opacity:0, duration:.8}, 171.4);

      // ===== S11 结尾 =====
      tl.fromTo('#sc-end > .scene-inner', {opacity:0}, {opacity:1,duration:.6,ease:'power1.out'}, 175.7);
      tl.from('#end-saying', {opacity:0, y:30, duration:1.1, ease:'power2.out'}, 176.2);
      tl.to('#end-saying', {autoAlpha:0, y:-30, duration:.6, ease:'power1.in'}, 178.9);
      tl.from('.ea-lead', {opacity:0, duration:.7}, 179.3);
      tl.from('.ea-q', {opacity:0, y:20, duration:.8}, 181.0);
      tl.from('.ea-q2', {opacity:0, y:20, duration:.9}, 184.6);
"""

# ---------- 底部字幕轨道 ----------
frag = char_track(cues, chars, THEME.accent)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/zhushixing-yeyang.wav", TOTAL),
    "",
    render_scenes(SCENES),
    "",
    '      <div id="subshade"></div>',
    '      <div id="subbar">',
    frag.html,
    '      </div>',
])
js = frag.js + "\n" + SCENE_JS + "\n" + frag.word_js

html = render_page(total=TOTAL,
                   css=assemble_css(THEME, PROJECT_CSS),
                   body=body, js=js)
io.open(P.index_html, "w", encoding="utf-8").write(html)
print("已生成 index.html（%.2f 秒，%d 幕，%d 句）"
      % (TOTAL, len(SCENES), len(cues)))
