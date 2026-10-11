# -*- coding: utf-8 -*-
"""HyperFrames 教程第 3 集《第一个 clip》成片生成器。

靛蓝深＋金网格主题（沿用 hf-01/02），329.37s，24 幕。教学核心＝一次真
实操：把样板标题换成自己的片段，讲清 clip 的「一个章（class="clip"）、
两个数字（data-start/data-duration）」、层叠靠标签顺序（Alt+Up）、零行
JS 纯静态即可渲染，以及 npm run check 红（content_overlap）→ Fix →
data-layout-allow-overlap → 绿的守门员弧光；结尾把「动」扣给 hf-04
（paused timeline 登记 window.__timelines，灵魂在 seek）。

素材先行：13 段录屏短片（media/shorts/，从 7 个长 take 精切，见
oneoffs/cut_shorts.py 与 REC-NOTES.md）＋13 张干净定格帧
（media/freezes/）。录屏作**顶层 clip**（StaticGuard：video 不可嵌套
在另一个 data-start 元素内），先按真实时长播放，随后定格帧全屏停留；
实拍时关键代码已自带选中高亮，概念信息靠顶栏 kicker／底栏注解随口播
轮替，不做缩窗（代码字缩小即不可读）。概念幕用居中卡片。
"""
import io
import sys
from dataclasses import replace
from pathlib import Path

# projects/<name>/make_video.py -> videos/ 在 parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       stage_gsap, DARK_GOLD_GH)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()
stage_gsap(P)  # 引擎本地副本入项目根（CDN 实测 11s、卡 check 导航超时）

data = load_cues(P.cues_json)
cues, chars, total = data["cues"], data["chars"], data["duration"]

# 靛蓝深＋金：与 hf-01/02 同一主题
THEME = replace(
    DARK_GOLD_GH,
    name="indigo-gold-hf",
    bg="#0d1b2a",
    subshade=("linear-gradient(transparent, rgba(13,27,42,.55) 40%, "
              "rgba(13,27,42,.94))"),
)

# ---- GitHub Dark 辅助色 ----
PANEL, LINE = "#161b22", "#30363d"
INK, MUTE = "#e6edf3", "#8b949e"
BLUE, BLUE2 = "#1f6feb", "#58a6ff"
GREEN, RED, GOLD = "#3fb950", "#f85149", "#e3b341"
AMBER = "#fbbf24"

# ---------- 24 幕（边界严格首尾相接；时间＝成片音频秒） ----------
SCENES = [

# S1 报名＋承上＋样板钩子 0.00–10.78（cue0–6）
Scene("sc-open", 0.00, 10.78, """
          <div class="op-title" id="op-title">第一个 clip</div>
          <div class="op-prev" id="op-prev">上一集，台子搭好了。</div>
          <div class="op-sample" id="op-sample">
            可舞台中间，还摆着那行样板 ——<span class="op-code">Hello HyperFrames</span>
          </div>"""),

# S2 本集任务 10.78–15.82（cue7–10）
Scene("sc-mission", 10.78, 15.82, """
          <div class="ms-kicker" id="ms-k">这一集</div>
          <div class="ms-main" id="ms-main">把样板请下去</div>
          <div class="ms-sub" id="ms-sub">做头一个真正属于你自己的片段</div>"""),

# S3 重构：拖时间轴 → 标签上写时间 15.82–31.04（cue10–14）
Scene("sc-concept", 15.82, 31.04, """
          <div class="kicker" id="cx-k">动手前，先掰一个观念</div>
          <div class="cmp">
            <div class="cmp-box" id="cx-edit">
              <div class="cmp-h mute">剪辑软件里</div>
              <div class="cmp-l">片段是鼠标按住</div>
              <div class="cmp-l"><strong>往时间轴上拖出来的</strong></div>
            </div>
            <div class="cmp-box hot" id="cx-hf">
              <div class="cmp-h blue">HyperFrames 里</div>
              <div class="cmp-l">没有这回事 ——</div>
              <div class="cmp-l"><strong>时间，是写在 HTML 标签上的</strong></div>
            </div>
          </div>
          <div class="cx-key" id="cx-key">拿键盘，一个数字一个数字地写</div>"""),

# S4 一个章两个数字（录屏 attrs-a 37.10–41.30，freeze 至 69.70）31.04–69.90
Scene("sc-attrs", 31.04, 69.90, """
          <div class="kicker" id="at-k">打开 index.html，盯住标题身上的属性</div>
          <div class="recnote" id="at-n1">盖了 <span class="mono">class="clip"</span> 的章，渲染器才认它是片段</div>
          <div class="recnote red" id="at-n2">没盖章：字写得再大、再艳，也进不了成片</div>
          <div class="recnote" id="at-n3"><span class="mono">data-start</span> ＝几点上场 ·
            <span class="mono">data-duration</span> ＝待几秒</div>"""),

# S5 track-index 脸熟 69.90–81.76（cue38–42；freeze 76.20 退出后纯卡）
Scene("sc-track", 69.90, 81.76, """
          <div class="kicker" id="tk-k">旁边还跟着一个，先混个脸熟</div>
          <div class="tk-chip" id="tk-chip"><span class="tk-attr">data-track-index</span>=<span class="tk-str">"0"</span></div>
          <div class="tk-use" id="tk-use">只给 Studio 的时间轴分轨道、排显示</div>
          <div class="tk-truth" id="tk-truth">渲染成片时，程序根本不读它 —— 别拿它当开关</div>"""),

# S6 CDN 换本地（录屏 attrs-b 83.46–92.03，freeze 至 98.40）81.76–98.72
Scene("sc-cdn", 81.76, 98.72, """
          <div class="kicker" id="cdn-k">动手前还有件事：把库请回本地</div>
          <div class="cdn-flow" id="cdn-flow">
            <span class="cdn-old" id="cdn-old">网上的 CDN：jsdelivr 上的 GSAP</span>
            <span class="cdn-arrow" id="cdn-arrow">→</span>
            <span class="cdn-new" id="cdn-new">本地一个 <span class="mono gold">gsap.min.js</span></span>
          </div>
          <div class="recnote" id="cdn-n1">断网也能渲染</div>
          <div class="recnote" id="cdn-n2">版本钉死在本机，上游怎么变都带不跑你</div>"""),

# S7 改 2/4＋换标题（录屏 title-a 103.30–106.37，freeze 至 111.60）98.72–111.98
Scene("sc-title", 98.72, 111.98, """
          <div class="kicker" id="tt-k">玩点真的：第二秒进来，第六秒走</div>
          <div class="axis" id="tt-axis">
            <span class="ax-n">0</span><span class="ax-seg" id="ax-seg">2 – 6</span>
            <span class="ax-n">10</span>
          </div>
          <div class="tt-math" id="tt-math"><span class="mono gold">data-start="2"</span>
            ＋ <span class="mono gold">data-duration="4"</span> ＝ 第 6 秒走</div>"""),

# S8 刷新点 Play（录屏 play 115.60–122.77，freeze 至 126.40）111.98–126.72
Scene("sc-play", 111.98, 126.72, """
          <div class="kicker" id="pl-k">回到浏览器，刷新，点 Preview 中间那个 Play</div>
          <div class="recnote" id="pl-n">没有鼠标拖动，就改了两个数字</div>"""),

# S9 relative 锚＋两张脸（录屏 a 131.30 / b 138.60，freeze 至 145.00）126.72–145.24
Scene("sc-anchor", 126.72, 145.24, """
          <div class="kicker" id="an-k">一个片段不过瘾，再加两个</div>
          <div class="recnote" id="an-n1">定位先给个锚：<span class="mono">#root { position: relative; }</span></div>
          <div class="recnote" id="an-n2">两张「脸」先画进样式：卡片 · 副标题 —— 都是普通 CSS</div>"""),

# S10 卡片 3/2（录屏 stack-c 146.80–149.57，freeze 延长到 163.30）145.24–153.90
Scene("sc-card", 145.24, 153.90, """
          <div class="kicker" id="cd-k">先加卡片，故意跟标题撞个满怀</div>
          <div class="recnote" id="cd-n">标题 2–6，卡片 <span class="mono gold">data-start="3" data-duration="2"</span> ＝ 3–5</div>"""),

# S11 后写盖上（录屏 stack-d 163.30–164.70，freeze 至 170.40）153.90–170.70
Scene("sc-stack", 153.90, 170.70, """
          <div class="kicker" id="st-k">注意它写在哪儿：标题标签的后一行</div>
          <div class="st-rule" id="st-rule">HTML 里后写的，盖在上面</div>"""),

# S12 Alt+Up 翻转（录屏 stack-e 175.00–176.97，freeze 至 183.80）170.70–184.10
Scene("sc-flip", 170.70, 184.10, """
          <div class="kicker" id="fl-k">想反过来？不用跟 z-index 较劲</div>
          <div class="fl-keys" id="fl-keys">
            <span class="app">Notepad++</span><span class="keycap">Alt</span><span class="keyplus">＋</span><span class="keycap">↑</span>
          </div>
          <div class="fl-note" id="fl-note">光标一点，整行提走 · 标签顺序一换，上下立刻翻转</div>"""),

# S13 副标题 6/4＋心得（录屏 stack-f 185.70–189.07，freeze 至 202.30）184.10–202.66
Scene("sc-sub", 184.10, 202.66, """
          <div class="kicker" id="sb-k">再放副标题：标题前脚走，它后脚来</div>
          <div class="recnote" id="sb-n"><span class="mono gold">data-start="6" data-duration="4"</span>
            —— 6 到 10，互不打架</div>"""),

# S14 纯静态即视频 202.66–219.88（cue112–119）
Scene("sc-static", 202.66, 219.88, """
          <div class="kicker" id="ss-k">颜色、位置、谁盖谁、几点进出 —— 全是写网页的老手艺</div>
          <div class="ss-zero" id="ss-zero">零行 JavaScript</div>
          <div class="ss-is" id="ss-is">这么一个纯静态页面，已经是一条有精确起止、随时能渲染的视频</div>
          <div class="ss-motto" id="ss-motto">先学会摆，再学会动</div>"""),

# S15 npm run check 与三个坑 219.88–237.90（cue118–126）
Scene("sc-check-intro", 219.88, 237.90, """
          <div class="kicker" id="ci-k">摆完别急着渲染，先让机器替你看一眼</div>
          <div class="cmd-card" id="ci-card"><div class="cmd-line">$ npm run <span class="cmd-hl">check</span></div></div>
          <div class="ci-pits" id="ci-pits">
            <span class="pit">忘盖章的</span>
            <span class="pit">时间写出界的</span>
            <span class="pit">把秒当帧、抬手填个 90 的</span>
          </div>
          <div class="ci-tail" id="ci-tail">新手常栽的坑，它都替你盯着 —— 咱们这页，也跑一下</div>"""),

# S16 红：content_overlap（录屏 fail 238.30–241.47，freeze 至 247.20）237.90–247.52
Scene("sc-fail", 237.90, 247.52, """
          <div class="kicker red" id="fa-k">红了 · 布局一项</div>
          <div class="recnote red" id="fa-n"><span class="mono">content_overlap</span>
            —— 卡片和标题撞在一起，两块文字重叠，可能没法读</div>"""),

# S17 Fix 行：两个选择 247.52–260.66（cue134–139）
Scene("sc-fix", 247.52, 260.66, """
          <div class="kicker" id="fx-k">别急着辩解，看它下面这行 Fix</div>
          <div class="fx-opts" id="fx-opts">
            <div class="fx-opt" id="fx-1"><span class="fx-n">①</span>
              给每块文字各自的地盘</div>
            <div class="fx-or" id="fx-or">或者</div>
            <div class="fx-opt hot" id="fx-2"><span class="fx-n">②</span>
              故意的层叠，就盖个章声明 ——
              <span class="mono gold">data-layout-allow-overlap</span></div>
          </div>"""),

# S18 加属性（录屏 allow 264.30–266.47，freeze 至 268.90）260.66–269.10
Scene("sc-allow", 260.66, 269.10, """
          <div class="kicker" id="ao-k">这次重叠，本来就是我设计的</div>
          <div class="recnote" id="ao-n">那就按它说的，在卡片标签上盖这个章</div>"""),

# S19 绿：四项全过（录屏 pass 269.40–272.60，freeze 至 278.70）269.10–278.98
Scene("sc-pass", 269.10, 278.98, """
          <div class="kicker green" id="pa-k">绿了 · Check passed</div>
          <div class="recnote green" id="pa-n">运行时零错误 · 布局零问题 · 动态零错误 · 对比度全过 WCAG AA</div>"""),

# S20 守门员 278.98–291.28（cue149–154）
Scene("sc-keeper", 278.98, 291.28, """
          <div class="kicker" id="kp-k">看懂这个流程没有</div>
          <div class="kp-pair" id="kp-pair">
            <span class="kp-bad" id="kp-bad">不是拦路虎</span>
            <span class="kp-is" id="kp-is">是守门员</span>
          </div>
          <div class="kp-rule" id="kp-rule">它不反对重叠，它反对的是「没打招呼」的重叠</div>"""),

# S21 Preview 肉眼验收 291.28–298.62（cue155–158）
Scene("sc-eyeball", 291.28, 298.62, """
          <div class="kicker" id="eb-k">过了 check，再肉眼走一遍</div>
          <div class="eb-list" id="eb-list">
            <span class="eb-i" id="eb-1">几点出现 ✓</span>
            <span class="eb-i" id="eb-2">几点消失 ✓</span>
            <span class="eb-i" id="eb-3">都对得上 —— 齐活</span>
          </div>"""),

# S22 还活不起来 298.62–306.68（cue159–163）
Scene("sc-teaser", 298.62, 306.68, """
          <div class="kicker" id="ts-k">不过你也看出来了，现在的画面还「活」不起来</div>
          <div class="ts-list" id="ts-list">
            <span class="ts-i" id="ts-1">标题不会飞进来</span>
            <span class="ts-i" id="ts-2">字不会一个个点亮</span>
            <span class="ts-i" id="ts-3">卡片也不会翻</span>
          </div>"""),

# S23 下一集：seek 306.68–326.92（cue164–173）
Scene("sc-next", 306.68, 326.92, """
          <div class="kicker" id="nx-k">是谁管这些？下一集，整个系列最核心的一集</div>
          <div class="code-card" id="nx-card">
            <div class="code-line"><span class="ln">1</span><span class="tk-kw">const</span> tl = gsap.timeline({ <span class="tk-attr">paused</span>: <span class="tk-kw">true</span> })</div>
            <div class="code-line" id="nx-l2"><span class="ln">2</span>window.<span class="tk-attr">__timelines</span>[<span class="tk-str">"main"</span>] = tl</div>
          </div>
          <div class="nx-why" id="nx-why">时间轴先暂停住、上报到一张表 —— 渲染器才能跳到任意一秒，画面立刻就位</div>
          <div class="nx-soul" id="nx-soul">灵魂，在 seek</div>
          <div class="nx-ep" id="nx-ep">hf-04，我们接着来</div>"""),

# S24 道别 326.92–TOTAL（cue174–175）
Scene("sc-bye", 326.92, total, """
          <div class="bye" id="bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 顶层录屏＋定格 clip（不可嵌套；放 scenes 之前＝下层） ----------
# video 按精切实长播放；紧接 <img> 干净定格。实拍关键代码自带选中高亮。
#   起/止＝成片音频秒（与口播拍点对齐，切点依据见 oneoffs/REC-NOTES.md）
VIDEOS = """      <video id="rec-attrs-a" class="clip" data-start="37.10"
             data-duration="4.20" data-track-index="2"
             src="media/shorts/s-attrs-a.mp4" muted playsinline preload="auto"></video>
      <img id="fz-attrs-a" class="clip" data-start="41.30"
             data-duration="28.40" src="media/freezes/s-attrs-a.png" alt="">
      <video id="rec-attrs-b" class="clip" data-start="83.46"
             data-duration="8.57" data-track-index="2"
             src="media/shorts/s-attrs-b.mp4" muted playsinline preload="auto"></video>
      <img id="fz-attrs-b" class="clip" data-start="92.03"
             data-duration="6.37" src="media/freezes/s-attrs-b.png" alt="">
      <video id="rec-title-a" class="clip" data-start="103.30"
             data-duration="3.07" data-track-index="2"
             src="media/shorts/s-title-a.mp4" muted playsinline preload="auto"></video>
      <img id="fz-title-a" class="clip" data-start="106.37"
             data-duration="5.23" src="media/freezes/s-title-a.png" alt="">
      <video id="rec-play" class="clip" data-start="115.60"
             data-duration="7.17" data-track-index="2"
             src="media/shorts/s-play.mp4" muted playsinline preload="auto"></video>
      <img id="fz-play" class="clip" data-start="122.77"
             data-duration="3.63" src="media/freezes/s-play.png" alt="">
      <video id="rec-stack-a" class="clip" data-start="131.30"
             data-duration="3.37" data-track-index="2"
             src="media/shorts/s-stack-a.mp4" muted playsinline preload="auto"></video>
      <img id="fz-stack-a" class="clip" data-start="134.67"
             data-duration="3.93" src="media/freezes/s-stack-a.png" alt="">
      <video id="rec-stack-b" class="clip" data-start="138.60"
             data-duration="4.07" data-track-index="2"
             src="media/shorts/s-stack-b.mp4" muted playsinline preload="auto"></video>
      <img id="fz-stack-b" class="clip" data-start="142.67"
             data-duration="2.33" src="media/freezes/s-stack-b.png" alt="">
      <video id="rec-stack-c" class="clip" data-start="146.80"
             data-duration="2.77" data-track-index="2"
             src="media/shorts/s-stack-c.mp4" muted playsinline preload="auto"></video>
      <img id="fz-stack-c" class="clip" data-start="149.57"
             data-duration="13.73" src="media/freezes/s-stack-c.png" alt="">
      <video id="rec-stack-d" class="clip" data-start="163.30"
             data-duration="1.40" data-track-index="2"
             src="media/shorts/s-stack-d.mp4" muted playsinline preload="auto"></video>
      <img id="fz-stack-d" class="clip" data-start="164.70"
             data-duration="5.70" src="media/freezes/s-stack-d.png" alt="">
      <video id="rec-stack-e" class="clip" data-start="175.00"
             data-duration="1.97" data-track-index="2"
             src="media/shorts/s-stack-e.mp4" muted playsinline preload="auto"></video>
      <img id="fz-stack-e" class="clip" data-start="176.97"
             data-duration="6.83" src="media/freezes/s-stack-e.png" alt="">
      <video id="rec-stack-f" class="clip" data-start="185.70"
             data-duration="3.37" data-track-index="2"
             src="media/shorts/s-stack-f.mp4" muted playsinline preload="auto"></video>
      <img id="fz-stack-f" class="clip" data-start="189.07"
             data-duration="13.23" src="media/freezes/s-stack-f.png" alt="">
      <video id="rec-fail" class="clip" data-start="238.30"
             data-duration="3.17" data-track-index="2"
             src="media/shorts/s-fail.mp4" muted playsinline preload="auto"></video>
      <img id="fz-fail" class="clip" data-start="241.47"
             data-duration="5.73" src="media/freezes/s-fail.png" alt="">
      <video id="rec-allow" class="clip" data-start="264.30"
             data-duration="2.17" data-track-index="2"
             src="media/shorts/s-allow.mp4" muted playsinline preload="auto"></video>
      <img id="fz-allow" class="clip" data-start="266.47"
             data-duration="2.43" src="media/freezes/s-allow.png" alt="">
      <video id="rec-pass" class="clip" data-start="269.40"
             data-duration="3.20" data-track-index="2"
             src="media/shorts/s-pass.mp4" muted playsinline preload="auto"></video>
      <img id="fz-pass" class="clip" data-start="272.60"
             data-duration="6.10" src="media/freezes/s-pass.png" alt="">"""

# ---------- 场景专属 CSS ----------
PROJECT_CSS = """
      /* 背景：金色细网格＋蓝金光斑 */
      #bg-grid { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background-image:
          linear-gradient(rgba(227,179,65,.055) 1px, transparent 1px),
          linear-gradient(90deg, rgba(227,179,65,.055) 1px, transparent 1px);
        background-size:80px 80px; }
      #bg-glow { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background:
          radial-gradient(720px 500px at 16% 12%, rgba(31,111,235,.17), transparent 70%),
          radial-gradient(840px 580px at 86% 84%, rgba(227,179,65,.12), transparent 70%); }

      /* 录屏窗口/定格：素材 1600x920 等比 1240x713，上移给顶栏/底注/字幕让位 */
      #rec-attrs-a, #rec-attrs-b, #rec-title-a, #rec-play,
      #rec-stack-a, #rec-stack-b, #rec-stack-c, #rec-stack-d, #rec-stack-e, #rec-stack-f,
      #rec-fail, #rec-allow, #rec-pass,
      #fz-attrs-a, #fz-attrs-b, #fz-title-a, #fz-play,
      #fz-stack-a, #fz-stack-b, #fz-stack-c, #fz-stack-d, #fz-stack-e, #fz-stack-f,
      #fz-fail, #fz-allow, #fz-pass { position:absolute;
        left:340px; top:104px; width:1240px; height:713px; object-fit:fill;
        border-radius:10px; box-shadow:0 18px 60px rgba(0,0,0,.55); }

      /* 通用 */
      .kicker { position:absolute; left:0; right:0; top:34px; text-align:center;
        font-size:44px; color:#8b949e; }
      .kicker.red { color:#f85149; } .kicker.green { color:#3fb950; }
      .mono { font-family:'Consolas','Courier New',monospace; color:#e6edf3; }
      .mono.gold { color:#e3b341; }
      /* 注意：tl.from 动画的元素 CSS 里不可写 opacity:0——from 的 immediateRender
         会把样式表的 0 缓存成「自然终值」，动画 0→0 永不显示（hf-03 CDP 实证）。
         需要 CSS 初隐的只用于 tl.to/fromTo 显式驱动的元素（cdn-flow/axis/tt-math）。 */
      .recnote { position:absolute; left:120px; right:120px; bottom:132px; z-index:5;
        text-align:center; font-size:42px; color:#c9d1d9; }
      .recnote.red { color:#ffa198; } .recnote.green { color:#7ee787; }

      /* S1 */
      .op-title { position:absolute; left:0; right:0; top:360px; text-align:center;
        font-size:130px; color:#e3b341; letter-spacing:.12em; }
      .op-prev { position:absolute; left:0; right:0; top:330px; text-align:center;
        font-size:60px; color:#e6edf3; }
      .op-sample { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:48px; color:#8b949e; }
      .op-code { font-family:'Consolas','Courier New',monospace; color:#58a6ff; }

      /* S2 */
      .ms-kicker { position:absolute; left:0; right:0; top:290px; text-align:center;
        font-size:52px; color:#8b949e; }
      .ms-main { position:absolute; left:0; right:0; top:380px; text-align:center;
        font-size:110px; color:#e3b341; }
      .ms-sub { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:56px; color:#e6edf3; }

      /* S3 对比 */
      .cmp { position:absolute; left:0; right:0; top:250px; text-align:center; }
      .cmp-box { display:inline-block; width:580px; padding:44px 48px; margin:0 28px;
        background:#161b22; border:2px solid #2b3c57;
        box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 10px 30px rgba(0,0,0,.38);
        border-radius:20px; vertical-align:top; }
      .cmp-box.hot { border-color:#1f6feb; }
      .cmp-h { font-size:50px; margin-bottom:24px; }
      .cmp-h.mute { color:#8b949e; } .cmp-h.blue { color:#58a6ff; }
      .cmp-l { font-size:44px; color:#e6edf3; line-height:1.8; }
      .cx-key { position:absolute; left:0; right:0; bottom:270px; text-align:center;
        font-size:52px; color:#e3b341; }

      /* S5 track chip */
      .tk-chip { position:absolute; left:50%; top:250px; margin-left:-430px;
        width:860px; padding:30px 44px; text-align:center; background:#0d1521;
        border:2px solid #30363d; border-radius:16px;
        font-family:'Consolas','Courier New',monospace; font-size:52px; }
      .tk-attr { color:#58a6ff; } .tk-str { color:#e3b341; }
      .tk-use { position:absolute; left:0; right:0; top:470px; text-align:center;
        font-size:48px; color:#c9d1d9; }
      .tk-truth { position:absolute; left:120px; right:120px; bottom:280px; text-align:center;
        font-size:46px; color:#e3b341; line-height:1.5; }

      /* S6 CDN */
      .cdn-flow { position:absolute; left:0; right:0; top:300px; text-align:center;
        opacity:0; }
      .cdn-old, .cdn-new { display:inline-block; width:520px; padding:38px 30px;
        font-size:40px; border-radius:18px; vertical-align:middle; }
      .cdn-old { background:#161b22; border:2px solid #6e3b3b; color:#f08d85; }
      .cdn-new { background:#161b22; border:2px solid #2b573f; color:#7ee787; }
      .cdn-arrow { display:inline-block; font-size:70px; color:#8b949e; margin:0 26px; }

      /* S7 时间轴 */
      .axis { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-family:'Consolas','Courier New',monospace; opacity:0; }
      .ax-n { display:inline-block; width:120px; font-size:40px; color:#8b949e;
        vertical-align:middle; }
      .ax-seg { display:inline-block; width:560px; padding:24px 0; margin:0 18px;
        font-size:64px; color:#0d1b2a; background:#e3b341; border-radius:14px;
        vertical-align:middle; }
      .tt-math { position:absolute; left:0; right:0; top:480px; text-align:center;
        font-size:48px; color:#c9d1d9; opacity:0; }

      /* S11 层叠金句 */
      .st-rule { position:absolute; left:0; right:0; bottom:132px; z-index:5; text-align:center;
        font-size:56px; color:#e3b341; text-shadow:0 2px 18px rgba(0,0,0,.8); }

      /* S12 键位 */
      .fl-keys { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .app { display:inline-block; font-size:52px; color:#8b949e;
        vertical-align:middle; margin-right:34px; }
      .keycap { display:inline-block; min-width:110px; padding:18px 30px;
        background:#161b22; border:2px solid #58a6ff; border-bottom-width:6px;
        border-radius:16px; font-size:58px; color:#e6edf3;
        font-family:'Consolas','Courier New',monospace; vertical-align:middle; }
      .keyplus { display:inline-block; font-size:48px; color:#8b949e;
        margin:0 18px; vertical-align:middle; }
      .fl-note { position:absolute; left:120px; right:120px; bottom:132px; z-index:5; text-align:center;
        font-size:46px; color:#c9d1d9; text-shadow:0 2px 18px rgba(0,0,0,.85); }

      /* S14 纯静态 */
      .ss-zero { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:130px; color:#e3b341; letter-spacing:.04em; }
      .ss-is { position:absolute; left:160px; right:160px; top:470px; text-align:center;
        font-size:48px; color:#e6edf3; line-height:1.6; }
      .ss-motto { position:absolute; left:0; right:0; bottom:282px; text-align:center;
        font-size:64px; color:#58a6ff; letter-spacing:.1em; }

      /* 命令卡（S15） */
      .cmd-card { position:absolute; left:50%; top:250px; margin-left:-460px;
        width:920px; padding:46px 56px; background:#161b22; border:2px solid #2b3c57;
        box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 10px 30px rgba(0,0,0,.38);
        border-radius:18px; }
      .cmd-line { font-size:64px; color:#e6edf3; font-family:'Consolas','Courier New',monospace; }
      .cmd-hl { color:#e3b341; }
      .ci-pits { position:absolute; left:0; right:0; top:480px; text-align:center; }
      .pit { display:inline-block; margin:0 18px; padding:20px 34px; font-size:40px;
        color:#c9d1d9; background:rgba(248,81,73,.08); border:2px solid #5e2b2b;
        border-radius:999px; }
      .ci-tail { position:absolute; left:120px; right:120px; bottom:270px; text-align:center;
        font-size:46px; color:#8b949e; }

      /* S17 Fix 两选项 */
      .fx-opts { position:absolute; left:160px; right:160px; top:250px; text-align:center; }
      .fx-opt { display:inline-block; width:1180px; padding:38px 48px; margin-bottom:26px;
        background:#161b22; border:2px solid #2b3c57; border-radius:18px;
        font-size:46px; color:#c9d1d9; text-align:left; }
      .fx-opt.hot { border-color:#e3b341; background:rgba(227,179,65,.08); color:#e6edf3; }
      .fx-n { color:#e3b341; font-size:52px; margin-right:20px; }
      .fx-or { font-size:38px; color:#8b949e; margin:6px 0 18px; }

      /* S20 守门员 */
      .kp-pair { position:absolute; left:0; right:0; top:310px; text-align:center; }
      .kp-bad, .kp-is { display:inline-block; width:480px; padding:42px 0; margin:0 24px;
        font-size:76px; border-radius:22px; vertical-align:middle; }
      .kp-bad { background:#161b22; border:2px solid #5e2b2b; color:#f08d85;
        text-decoration:line-through; text-decoration-color:#f85149; }
      .kp-is { background:rgba(63,185,80,.10); border:2px solid #3fb950; color:#7ee787; }
      .kp-rule { position:absolute; left:140px; right:140px; bottom:278px; text-align:center;
        font-size:52px; color:#e3b341; line-height:1.5; }

      /* S21 肉眼验收 */
      .eb-list { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .eb-i { display:block; font-size:56px; color:#e6edf3; line-height:2.0; }

      /* S22 活不起来 */
      .ts-list { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .ts-i { display:block; font-size:54px; color:#6e7681; line-height:2.0; }

      /* 代码卡（S23） */
      .code-card { position:absolute; left:50%; top:250px; margin-left:-660px;
        width:1320px; padding:34px 44px; background:#0d1521; border:2px solid #30363d;
        border-radius:16px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      .code-line { position:relative; font-family:'Consolas','Courier New',monospace;
        font-size:46px; line-height:1.72; color:#8b949e; white-space:nowrap; }
      .ln { display:inline-block; width:60px; color:#6e7681; text-align:right;
        margin-right:28px; }
      .tk-attr { color:#58a6ff; } .tk-str { color:#e3b341; } .tk-kw { color:#ff7b72; }
      .nx-why { position:absolute; left:140px; right:140px; top:520px; text-align:center;
        font-size:44px; color:#c9d1d9; line-height:1.5; }
      .nx-soul { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:92px; color:#e3b341; letter-spacing:.12em; }
      .nx-ep { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:52px; color:#58a6ff; font-family:'Consolas','Courier New',monospace; }

      /* S24 道别 */
      .bye { position:absolute; left:0; right:0; top:440px; text-align:center;
        font-size:72px; color:#e6edf3; letter-spacing:.08em; }
"""

# ---------- 场景时间轴（时间显式给秒） ----------
SCENE_JS = """
      /* S1 0–10.78：片名为首屏（报名声落在此），随后承上、样板钩子 */
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#op-title',{scale:.8,opacity:0,duration:.8,ease:'back.out(1.5)'},.2);
      tl.to('#op-title',{opacity:0,duration:.4},1.7);
      tl.from('#op-prev',{y:20,opacity:0,duration:.6},1.9);
      tl.from('#op-sample',{y:24,opacity:0,duration:.7},4.0);
      tl.to('#sc-open > .scene-inner',{opacity:0,duration:.4},10.38);

      /* S2 10.78–15.82 */
      tl.fromTo('#sc-mission > .scene-inner',{opacity:0},{opacity:1,duration:.5},10.78);
      tl.from('#ms-k',{y:20,opacity:0,duration:.6},11.0);
      tl.from('#ms-main',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},12.0);
      tl.from('#ms-sub',{y:24,opacity:0,duration:.7},13.4);
      tl.to('#sc-mission > .scene-inner',{opacity:0,duration:.4},15.42);

      /* S3 15.82–31.04 */
      tl.fromTo('#sc-concept > .scene-inner',{opacity:0},{opacity:1,duration:.5},15.82);
      tl.from('#cx-k',{y:20,opacity:0,duration:.6},16.1);
      tl.from('#cx-edit',{x:-50,opacity:0,duration:.7,ease:'back.out(1.4)'},18.2);
      tl.from('#cx-hf',{x:50,opacity:0,duration:.7,ease:'back.out(1.4)'},25.6);
      tl.from('#cx-key',{y:22,opacity:0,duration:.6},27.6);
      tl.to('#sc-concept > .scene-inner',{opacity:0,duration:.4},30.64);

      /* S4 31.04–69.90：录屏 37.10–41.30、freeze 至 76.20；底注按口播轮替 */
      tl.fromTo('#sc-attrs > .scene-inner',{opacity:0},{opacity:1,duration:.5},31.04);
      tl.from('#at-k',{y:18,opacity:0,duration:.6},31.3);
      tl.from('#at-n1',{opacity:0,duration:.5},47.6);
      tl.to('#at-n1',{opacity:0,duration:.4},53.2);
      tl.from('#at-n2',{opacity:0,duration:.5},53.6);
      tl.to('#at-n2',{opacity:0,duration:.4},59.0);
      tl.from('#at-n3',{opacity:0,duration:.5},61.4);
      tl.to('#sc-attrs > .scene-inner',{opacity:0,duration:.4},69.5);

      /* S5 69.90–81.76 */
      tl.fromTo('#sc-track > .scene-inner',{opacity:0},{opacity:1,duration:.5},69.90);
      tl.from('#tk-k',{y:18,opacity:0,duration:.6},70.2);
      tl.from('#tk-chip',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},71.0);
      tl.from('#tk-use',{y:20,opacity:0,duration:.6},74.0);
      tl.from('#tk-truth',{y:22,opacity:0,duration:.7},77.7);
      tl.to('#sc-track > .scene-inner',{opacity:0,duration:.4},81.36);

      /* S6 81.76–98.72：录屏 83.46–92.03、freeze 至 98.40 */
      tl.fromTo('#sc-cdn > .scene-inner',{opacity:0},{opacity:1,duration:.5},81.76);
      tl.from('#cdn-k',{y:18,opacity:0,duration:.6},82.0);
      tl.to('#cdn-flow',{opacity:1,duration:.7},82.3);
      tl.from('#cdn-old',{x:-30,opacity:0,duration:.5},82.4);
      tl.from('#cdn-arrow',{opacity:0,duration:.4},83.0);
      tl.from('#cdn-new',{x:30,opacity:0,duration:.5},83.1);
      tl.to('#cdn-flow',{opacity:0,duration:.4},83.1);   /* 83.46 录屏起，先净场 */
      tl.from('#cdn-n1',{opacity:0,duration:.5},92.2);
      tl.to('#cdn-n1',{opacity:0,duration:.4},94.0);
      tl.from('#cdn-n2',{opacity:0,duration:.5},94.4);
      tl.to('#sc-cdn > .scene-inner',{opacity:0,duration:.4},98.32);

      /* S7 98.72–111.98：录屏 103.30–106.37、freeze 至 111.60 */
      tl.fromTo('#sc-title > .scene-inner',{opacity:0},{opacity:1,duration:.5},98.72);
      tl.from('#tt-k',{y:18,opacity:0,duration:.6},99.0);
      tl.to('#tt-axis',{opacity:1,duration:.6},99.6);
      tl.from('#ax-seg',{scale:.7,opacity:0,duration:.6,ease:'back.out(1.5)'},100.3);
      /* tt-math 由 fromTo 显式驱动（CSS opacity:0 初隐），抢在 103.30 录屏前讲完 */
      tl.fromTo('#tt-math',{opacity:0,y:20},{opacity:1,y:0,duration:.5},100.6);
      tl.to('#tt-axis',{opacity:0,duration:.35},103.1);
      tl.to('#tt-math',{opacity:0,duration:.35},103.1);
      tl.to('#sc-title > .scene-inner',{opacity:0,duration:.4},111.58);

      /* S8 111.98–126.72：录屏 115.60–122.77、freeze 至 126.40 */
      tl.fromTo('#sc-play > .scene-inner',{opacity:0},{opacity:1,duration:.5},111.98);
      tl.from('#pl-k',{y:18,opacity:0,duration:.6},112.2);
      tl.from('#pl-n',{opacity:0,duration:.5},123.8);
      tl.to('#sc-play > .scene-inner',{opacity:0,duration:.4},126.32);

      /* S9 126.72–145.24：录屏 a 131.30 / b 138.60，freeze 至 145.00 */
      tl.fromTo('#sc-anchor > .scene-inner',{opacity:0},{opacity:1,duration:.5},126.72);
      tl.from('#an-k',{y:18,opacity:0,duration:.6},127.0);
      tl.from('#an-n1',{opacity:0,duration:.5},131.7);
      tl.to('#an-n1',{opacity:0,duration:.4},138.2);
      tl.from('#an-n2',{opacity:0,duration:.5},139.0);
      tl.to('#sc-anchor > .scene-inner',{opacity:0,duration:.4},144.84);

      /* S10 145.24–153.90：录屏 c 146.80–149.57，其 freeze 延长到 163.30 */
      tl.fromTo('#sc-card > .scene-inner',{opacity:0},{opacity:1,duration:.5},145.24);
      tl.from('#cd-k',{y:18,opacity:0,duration:.6},145.5);
      tl.from('#cd-n',{opacity:0,duration:.5},150.0);
      tl.to('#sc-card > .scene-inner',{opacity:0,duration:.4},153.5);

      /* S11 153.90–170.70：freeze(c) 承前；录屏 d 163.30–164.70、freeze 至 170.40 */
      tl.fromTo('#sc-stack > .scene-inner',{opacity:0},{opacity:1,duration:.5},153.90);
      tl.from('#st-k',{y:18,opacity:0,duration:.6},154.2);
      tl.from('#st-rule',{y:20,opacity:0,duration:.7},167.2);
      tl.to('#sc-stack > .scene-inner',{opacity:0,duration:.4},170.3);

      /* S12 170.70–184.10：录屏 e 175.00–176.97、freeze 至 183.80 */
      tl.fromTo('#sc-flip > .scene-inner',{opacity:0},{opacity:1,duration:.5},170.70);
      tl.from('#fl-k',{y:18,opacity:0,duration:.6},171.0);
      tl.from('#fl-keys',{scale:.8,opacity:0,duration:.7,ease:'back.out(1.4)'},171.8);
      tl.to('#fl-keys',{opacity:0,duration:.4},174.6);
      tl.from('#fl-note',{y:22,opacity:0,duration:.7},177.2);
      tl.to('#sc-flip > .scene-inner',{opacity:0,duration:.4},183.7);

      /* S13 184.10–202.66：录屏 f 185.70–189.07、freeze 至 202.30 */
      tl.fromTo('#sc-sub > .scene-inner',{opacity:0},{opacity:1,duration:.5},184.10);
      tl.from('#sb-k',{y:18,opacity:0,duration:.6},184.4);
      tl.from('#sb-n',{opacity:0,duration:.5},192.0);
      tl.to('#sc-sub > .scene-inner',{opacity:0,duration:.4},202.26);

      /* S14 202.66–219.88 */
      tl.fromTo('#sc-static > .scene-inner',{opacity:0},{opacity:1,duration:.5},202.66);
      tl.from('#ss-k',{y:18,opacity:0,duration:.6},202.96);
      tl.from('#ss-zero',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},206.0);
      tl.from('#ss-is',{y:24,opacity:0,duration:.7},213.4);
      tl.from('#ss-motto',{y:26,opacity:0,duration:.7},216.0);
      tl.to('#sc-static > .scene-inner',{opacity:0,duration:.4},219.48);

      /* S15 219.88–237.90 */
      tl.fromTo('#sc-check-intro > .scene-inner',{opacity:0},{opacity:1,duration:.5},219.88);
      tl.from('#ci-k',{y:18,opacity:0,duration:.6},220.18);
      tl.from('#ci-card',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},226.2);
      tl.from('.ci-pits .pit',{y:26,opacity:0,duration:.5,stagger:.25},227.6);
      tl.from('#ci-tail',{y:22,opacity:0,duration:.6},236.0);
      tl.to('#sc-check-intro > .scene-inner',{opacity:0,duration:.4},237.5);

      /* S16 237.90–247.52：录屏 fail 238.30–241.47、freeze 至 247.20 */
      tl.fromTo('#sc-fail > .scene-inner',{opacity:0},{opacity:1,duration:.5},237.90);
      tl.from('#fa-k',{y:18,opacity:0,duration:.5},237.95);
      tl.from('#fa-n',{opacity:0,duration:.5},245.0);
      tl.to('#sc-fail > .scene-inner',{opacity:0,duration:.4},247.12);

      /* S17 247.52–260.66 */
      tl.fromTo('#sc-fix > .scene-inner',{opacity:0},{opacity:1,duration:.5},247.52);
      tl.from('#fx-k',{y:18,opacity:0,duration:.6},247.82);
      tl.from('#fx-1',{x:-40,opacity:0,duration:.6},252.4);
      tl.from('#fx-or',{opacity:0,duration:.4},254.6);
      tl.from('#fx-2',{x:40,opacity:0,duration:.6,ease:'back.out(1.2)'},255.8);
      tl.to('#sc-fix > .scene-inner',{opacity:0,duration:.4},260.26);

      /* S18 260.66–269.10：录屏 allow 264.30–266.47、freeze 至 268.90 */
      tl.fromTo('#sc-allow > .scene-inner',{opacity:0},{opacity:1,duration:.5},260.66);
      tl.from('#ao-k',{y:18,opacity:0,duration:.6},260.96);
      tl.from('#ao-n',{opacity:0,duration:.5},261.2);
      tl.to('#sc-allow > .scene-inner',{opacity:0,duration:.4},268.7);

      /* S19 269.10–278.98：录屏 pass 269.40–272.60、freeze 至 278.70 */
      tl.fromTo('#sc-pass > .scene-inner',{opacity:0},{opacity:1,duration:.5},269.10);
      tl.from('#pa-k',{y:18,opacity:0,duration:.5},269.3);
      tl.from('#pa-n',{opacity:0,duration:.5},273.0);
      tl.to('#sc-pass > .scene-inner',{opacity:0,duration:.4},278.58);

      /* S20 278.98–291.28 */
      tl.fromTo('#sc-keeper > .scene-inner',{opacity:0},{opacity:1,duration:.5},278.98);
      tl.from('#kp-k',{y:18,opacity:0,duration:.6},279.28);
      tl.from('#kp-bad',{x:-40,opacity:0,duration:.6},280.8);
      tl.from('#kp-is',{x:40,opacity:0,duration:.6,ease:'back.out(1.3)'},282.4);
      tl.from('#kp-rule',{y:24,opacity:0,duration:.7},285.0);
      tl.to('#sc-keeper > .scene-inner',{opacity:0,duration:.4},290.88);

      /* S21 291.28–298.62 */
      tl.fromTo('#sc-eyeball > .scene-inner',{opacity:0},{opacity:1,duration:.5},291.28);
      tl.from('#eb-k',{y:18,opacity:0,duration:.6},291.58);
      tl.from('.eb-list .eb-i',{y:24,opacity:0,duration:.5,stagger:.3},292.6);
      tl.to('#sc-eyeball > .scene-inner',{opacity:0,duration:.4},298.22);

      /* S22 298.62–306.68 */
      tl.fromTo('#sc-teaser > .scene-inner',{opacity:0},{opacity:1,duration:.5},298.62);
      tl.from('#ts-k',{y:18,opacity:0,duration:.6},298.92);
      tl.from('.ts-list .ts-i',{y:24,opacity:0,duration:.55,stagger:.32},300.4);
      tl.to('#sc-teaser > .scene-inner',{opacity:0,duration:.4},306.28);

      /* S23 306.68–326.92 */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},306.68);
      tl.from('#nx-k',{y:18,opacity:0,duration:.6},306.98);
      tl.from('#nx-card .code-line',{y:20,opacity:0,duration:.55,stagger:.25},312.4);
      tl.from('#nx-why',{y:22,opacity:0,duration:.6},315.6);
      tl.from('#nx-soul',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},323.0);
      tl.from('#nx-ep',{y:20,opacity:0,duration:.6},324.6);
      tl.to('#sc-next > .scene-inner',{opacity:0,duration:.4},326.52);

      /* S24 326.92–TOTAL */
      tl.fromTo('#sc-bye > .scene-inner',{opacity:0},{opacity:1,duration:.5},326.92);
      tl.from('#bye',{y:24,opacity:0,duration:.7},327.1);
"""

# ---------- 底部字幕轨道 ----------
# time_offset：faster-whisper 吞句间停顿致字幕整体偏早；hf-01 实测 0.28、
# hf-02 实测 0.37。hf-03 经 build/measure_offset.py 实测：33 对 onset 配对
# 中位 +295ms／均值 +294ms（区间 180–390ms，无一处声音早）→ 取 0.29。
frag = char_track(cues, chars, THEME.accent, time_offset=0.29)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/hf-03-yeyang.wav", total),
    "",
    '      <div id="bg-grid"></div>',
    '      <div id="bg-glow"></div>',
    "",
    VIDEOS,
    "",
    render_scenes(SCENES),
    "",
    '      <div id="subshade"></div>',
    '      <div id="subbar">',
    frag.html,
    '      </div>',
])
js = "\n".join([frag.js, SCENE_JS, frag.word_js])

html = render_page(total=total,
                   css=assemble_css(THEME, PROJECT_CSS),
                   body=body, js=js)
io.open(P.index_html, "w", encoding="utf-8").write(html)
print("已生成 index.html（%.2f 秒，%d 幕，%d 句，13 段录屏）"
      % (total, len(SCENES), len(cues)))
