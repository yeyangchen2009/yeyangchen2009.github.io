# -*- coding: utf-8 -*-
"""HyperFrames 教程第 4 集《灵魂在 seek》成片生成器。

靛蓝深＋金网格主题（沿用 hf-01/02/03），606.475s，26 幕。教学核心＝
seekable（可定位）：渲染器不是从头播网页架摄像机，而是随机跳帧问页面
「把你播到 t，你长什么样」。CSS 动画三时刻截帧逐字节一致（运行时接管
时钟），setInterval 计数器排队 2 种/一窝蜂 3 种（只认墙钟、不可定位），
check 全绿也查不出；解法＝GSAP paused 时间轴＋fromTo 挂时刻＋注册
window.__timelines，亲手用 window.__player.seek 拨给你看，最后捅破
渲染内核（无头 Chrome＝人肉 seek）与适配器约定（只要实现 seek(t)）。

素材先行：33 段录屏短片（media/shorts/，从 12 个 take 精切，切点依据见
oneoffs/cut_shorts.py 与 oneoffs/RECORD-NOTES.md）＋9 张定格帧
（media/freezes/）＋12 张渲染器真截帧（media/shots/：CSS 三时刻 3 张、
排队 ser-1..3、并发 tk-1..6）。录屏作**顶层 clip**（StaticGuard：video
不可嵌套），先按真实时长播放，随后定格帧全屏停留；CSS 三时刻真帧本身
1920x1080 作全屏 clip，race 九真帧作场景内证据墙浮层。概念信息靠顶栏
kicker／底栏注解随口播轮替，不缩窗（代码字缩小即不可读）。
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

# 靛蓝深＋金：与 hf-01/02/03 同一主题
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

# ---------- 26 幕（边界严格首尾相接；时间＝成片音频秒） ----------
SCENES = [

# S1 报名＋承上静态（录屏 play-static）0.00–14.42
Scene("sc-open", 0.00, 14.42, """
          <div class="op-ep" id="op-ep">HyperFrames 教程 · 第 4 集</div>
          <div class="op-title" id="op-title">灵魂在 seek</div>
          <div class="kicker" id="op-k">先把上一集的成果，打开看一眼 —— 第二秒，标题「抨」地处在那</div>
          <div class="recnote" id="op-n">静态页面嘛：只会出现和消失，不会动</div>"""),

# S2 本集任务＋核心集＋规矩不一样 14.42–30.50
Scene("sc-fly", 14.42, 30.50, """
          <div class="kicker" id="fy-k">今天这集，就让它飞进来</div>
          <div class="core-badge" id="fy-badge">整个系列 · 最核心的一集</div>
          <div class="cmp">
            <div class="cmp-box" id="fy-old">
              <div class="cmp-h mute">在普通网页里写动画</div>
              <div class="cmp-l">页面一加载</div>
              <div class="cmp-l">动画就<strong>自顾自播</strong></div>
            </div>
            <div class="cmp-box hot" id="fy-hf">
              <div class="cmp-h blue">在 HyperFrames 里写动画</div>
              <div class="cmp-l">每一帧</div>
              <div class="cmp-l">都是<strong>问出来的</strong></div>
            </div>
          </div>
          <div class="cx-key" id="fy-key">规矩不一样 —— 不一样不在语法，在这东西的播放方式</div>"""),

# S3 CSS keyframes 实操＋播放（录屏 mid/done/play-css）30.50–52.50
Scene("sc-css-kf", 30.50, 52.50, """
          <div class="kicker" id="kf-k">按老习惯：CSS 写个 @keyframes，就够了</div>
          <div class="recnote" id="kf-n1">起手透明 → 往下挪 60 像素 → 0.8 秒归位，保存</div>
          <div class="recnote" id="kf-n2">回到浏览器，点播放</div>
          <div class="recnote" id="kf-n3">哎？标题确实飞进来了</div>
          <div class="recnote" id="kf-n4">挺正常 —— 可别急着下结论</div>"""),

# S4 渲染器原理（概念）52.50–74.98
Scene("sc-render-how", 52.50, 74.98, """
          <div class="kicker" id="rw-k">渲染器出一条 30 帧每秒的视频，到底是怎么干活的？</div>
          <div class="wrong-card" id="rw-wrong">
            <span class="wrong-s">✗</span> 从头把网页播一遍，在旁边架个摄像机录
          </div>
          <div class="pflow" id="rw-flow">
            <span class="pstep" id="rw-s1">要第几帧？<br><b>算出秒数 t</b></span>
            <span class="parrow">→</span>
            <span class="pstep" id="rw-s2">问页面<br><b>把你播到 t</b></span>
            <span class="parrow">→</span>
            <span class="pstep hot" id="rw-s3">摆好<br><b>截图</b></span>
            <span class="parrow">→</span>
            <span class="pstep" id="rw-s4">下一帧</span>
          </div>
          <div class="rand-note" id="rw-rand">问帧的顺序是随机的：这一秒还在问第 2 秒，下一秒可能直接问第 7 秒 —— 不会从头等你 7 秒</div>"""),

# S5 seekable（概念）74.98–99.30
Scene("sc-seekable", 74.98, 99.30, """
          <div class="kicker" id="sk-k">页面上每一样会动的东西，都得回答同一个问题</div>
          <div class="q-card" id="sk-card">
            给你任意一个秒数 <span class="mono gold">t</span> ——<br>
            你能不能<strong>立刻摆出那个瞬间的样子</strong>？
          </div>
          <div class="seek-sub" id="sk-sub">不用等 · 也不依赖之前发生过什么</div>
          <div class="seek-word" id="sk-word">seekable</div>
          <div class="seek-cn" id="sk-cn">可 定 位</div>
          <div class="seek-notes">
            <span class="seek-note" id="sk-n1">这类工具的命根子</span>
            <span class="seek-note" id="sk-n2">也是它敢说自己「为 agent 而生」的底气</span>
          </div>"""),

# S6 snapshot 截帧三时刻＋逐字节一致（录屏 cmd/run/eq＋真帧全屏）99.30–129.74
Scene("sc-snap-css", 99.30, 129.74, """
          <div class="kicker" id="sn-k">那刚才这段 CSS 动画，能不能被定位？我不猜 —— 截帧看</div>
          <div class="recnote" id="sn-n1">snapshot --at 2.1, 2.5, 2.9 —— 同一个动画，截三张</div>
          <div class="recnote" id="sn-n21">2.1s：淡淡的影子，刚冒头</div>
          <div class="recnote" id="sn-n25">2.5s：半透明，停在半路</div>
          <div class="recnote" id="sn-n29">2.9s：白了，归位了</div>
          <div class="recnote" id="sn-n2">不放心，同样三个时刻再截一轮 —— 逐字节一模一样，一个像素都不带差的</div>"""),

# S7 运行时接管时钟（概念）129.74–149.96
Scene("sc-runtime", 129.74, 149.96, """
          <div class="kicker" id="rt-k">原来 HyperFrames 的运行时，偷偷替你做了一件事</div>
          <div class="rt-flow">
            <div class="rt-box old" id="rt-old">
              <div class="rt-h">页面一加载</div>
              <div class="rt-b">CSS 动画<strong>自顾自播</strong></div>
            </div>
            <span class="rt-arrow" id="rt-arrow">接管 →</span>
            <div class="rt-box hot" id="rt-new">
              <div class="rt-h">绑到片段自己的时间轴上</div>
              <div class="rt-b">标题第 2 秒进场，动画<strong>就在第 2 秒开始</strong></div>
            </div>
          </div>
          <div class="rt-note" id="rt-note">运行时替你播 —— 所以怎么截，帧帧都对</div>"""),

# S8 过渡＋setInterval 计数器（录屏 mid/done/play-timer）149.96–167.08
Scene("sc-timer", 149.96, 167.08, """
          <div class="hurry" id="tm-hurry">那还学什么？CSS 全搞定了？<span class="hurry-em">—— 别急，再试一样东西</span></div>
          <div class="kicker" id="tm-k">在页面上加个计数器：最普通的 setInterval，每半秒 +1</div>
          <div class="recnote" id="tm-n">浏览器里看，数字跳得欢着呢 —— 一点毛病没有</div>"""),

# S9 race 第一轮：排队（录屏 q-cmd/q-run）167.08–198.00
Scene("sc-race-q", 167.08, 198.00, """
          <div class="kicker" id="rq-k">还是不猜，分两轮看 —— 第一轮：排队，一个一个问第 2 秒</div>
          <div class="recnote" id="rq-n1">同一个第 2 秒，连截三张，结果你自己看</div>
          <div class="shot-strip" id="rq-shots">
            <div class="shot-cell"><img src="media/shots/ser-1.png" alt=""><span class="shot-tag">ser-1 · tick 3</span></div>
            <div class="shot-cell"><img src="media/shots/ser-2.png" alt=""><span class="shot-tag">ser-2 · tick 3</span></div>
            <div class="shot-cell hot"><img src="media/shots/ser-3.png" alt=""><span class="shot-tag">ser-3 · tick 4（独一份）</span></div>
          </div>
          <div class="recnote" id="rq-n3">连排队，都给不出唯一答案 —— 进程启动走过的一两秒，就是分水岭</div>"""),

# S10 race 第二轮：一窝蜂（录屏 q-done/f-start/f-done＋六真帧墙）198.00–228.84
Scene("sc-race-f", 198.00, 228.84, """
          <div class="kicker" id="rf-k">第二轮：喊 6 个渲染器同时开工，全问第 2 秒，谁也不许等谁</div>
          <div class="recnote" id="rf-n1">排队问：2 种</div>
          <div class="recnote" id="rf-n2">无头 Chrome 一起开工，几块 CPU 抢着用</div>
          <div class="shot-grid6" id="rf-shots">
            <div class="shot-cell"><img src="media/shots/tk-1.png" alt=""><span class="shot-tag">tk-1 · tick 6</span></div>
            <div class="shot-cell"><img src="media/shots/tk-2.png" alt=""><span class="shot-tag">tk-2 · tick 6</span></div>
            <div class="shot-cell"><img src="media/shots/tk-3.png" alt=""><span class="shot-tag">tk-3 · tick 7</span></div>
            <div class="shot-cell hot"><img src="media/shots/tk-4.png" alt=""><span class="shot-tag">tk-4 · tick 4（独一份）</span></div>
            <div class="shot-cell"><img src="media/shots/tk-5.png" alt=""><span class="shot-tag">tk-5 · tick 6</span></div>
            <div class="shot-cell"><img src="media/shots/tk-6.png" alt=""><span class="shot-tag">tk-6 · tick 7</span></div>
          </div>
          <div class="recnote" id="rf-n3">一窝蜂：3 种 —— 同一个第 2 秒，答案唯不唯一，取决于问法</div>"""),

# S11 定时器为什么不行＋check 全绿（录屏 check-run/pass）228.84–264.52
Scene("sc-check-green", 228.84, 264.52, """
          <div class="kicker" id="cg-k">为什么 CSS 动画行，定时器不行？</div>
          <div class="cmp">
            <div class="cmp-box" id="cg-css">
              <div class="cmp-h blue">CSS 动画</div>
              <div class="cmp-l">时钟被运行时<strong>绑上了片段的轴</strong></div>
            </div>
            <div class="cmp-box bad" id="cg-timer">
              <div class="cmp-h red">setInterval</div>
              <div class="cmp-l">只认<strong>墙上的钟</strong>：页面打开后真实过了几秒，它就跳几下</div>
            </div>
          </div>
          <div class="qa-card" id="cg-qa">
            <div class="qa-q">渲染器问它：第 2 秒，你长什么样？</div>
            <div class="qa-a">它答不上来 —— 只会告诉你「<strong>我现在</strong>是什么样」；CPU 被挤狠了，轮到截图时计数器已多跳了两三下</div>
          </div>
          <div class="recnote green" id="cg-n1">你看 —— 连 check 都是绿的，零错误</div>
          <div class="recnote" id="cg-n2">守门员能查布局、查对比度，但查不出你这个动画根本没法定位 —— 这一刻只能自己懂</div>"""),

# S12 薛定谔规矩＋GSAP 正道引入（概念）264.52–289.62
Scene("sc-schrodinger", 264.52, 289.62, """
          <div class="kicker" id="sd-k">所以规矩是 —— 凡是跟着真实时间自己往前跑的</div>
          <div class="black-chips" id="sd-chips">
            <span class="chip-bad">setInterval</span>
            <span class="chip-bad">setTimeout</span>
            <span class="chip-bad">requestAnimationFrame</span>
            <span class="chip-bad">里手改样式</span>
          </div>
          <div class="sd-verdict" id="sd-verdict">在视频里，都是「薛定谔」的画面</div>
          <div class="axis-gold" id="sd-axis">
            <span class="axis-label">动画的时间，必须交给一根</span>
            <span class="axis-line"><i id="sd-dot"></i></span>
            <span class="axis-name">能来回播的轴</span>
          </div>
          <div class="sd-gsap" id="sd-gsap">
            官方给的正道：<span class="mono gold">gsap.timeline</span> —— 页面骨架底部，位置早就替你留好了。三件事
          </div>"""),

# S13 第一件 paused（录屏 gsap-paused＋freeze）289.62–306.46
Scene("sc-gsap-1", 289.62, 306.46, """
          <div class="kicker" id="g1-k">第一件：建时间轴的时候，加一个参数</div>
          <div class="code-card small" id="g1-card">
            <div class="code-line"><span class="ln">1</span><span class="tk-kw">const</span> tl = gsap.timeline({ <span class="tk-attr">paused</span>: <span class="tk-kw">true</span> })</div>
          </div>
          <div class="recnote" id="g1-n1">这条轴生下来就是暂停的，一秒钟都不自己走</div>
          <div class="recnote" id="g1-n2">它不是一段会播放的动画，更像一个函数</div>
          <div class="recnote" id="g1-n3">你给它时间 t，它还你那个瞬间，每个元素该有的样子</div>"""),

# S14 第二件 fromTo 挂时刻（录屏 gsap-fromto＋freeze）306.46–332.96
Scene("sc-gsap-2", 306.46, 332.96, """
          <div class="kicker" id="g2-k">第二件：动画照写 —— 但是往这条暂停的轴上挂</div>
          <div class="recnote" id="g2-n1">tl.fromTo：开头透明、往下偏 60 像素，1.4 秒浮上来，缓动 power2.out</div>
          <div class="recnote" id="g2-n2">最后一个参数写 2 —— 这是挂在时间轴上的位置</div>
          <div class="recnote" id="g2-n3">标题第 2 秒、卡片第 3 秒、副标题第 6 秒 —— 暂停着没关系，它全记得住</div>"""),

# S15 第三件 注册 window.__timelines（录屏 register/html＋register freeze）332.96–357.36
Scene("sc-gsap-3", 332.96, 357.36, """
          <div class="kicker" id="g3-k">第三件，最容易忘：注册到表上</div>
          <div class="recnote" id="g3-n1">window.__timelines[&quot;main&quot;] = 这条轴</div>
          <div class="recnote" id="g3-n2">main 是谁？回头看 #root 身上的 data-composition-id —— 就是 main</div>
          <div class="recnote" id="g3-n3">这行是报到：渲染器渲染 main 的时候，按名字来这张表取轴</div>
          <div class="recnote" id="g3-n4">底下还留一行 tl.seek(0)：页面一加载先定位第 0 秒，省得开头闪一下</div>"""),

# S16 代理猜中 vs 显式保证（概念）357.36–389.34
Scene("sc-agent", 357.36, 389.34, """
          <div class="kicker" id="ag-k">有人发现了：我刚才偷懒不注册，写全局 GSAP，运行时好像也能兜住？</div>
          <div class="guess-grid">
            <div class="guess-box" id="ag-guess">
              <div class="guess-h mute">那是它 <b>猜中了</b></div>
              <div class="guess-l">眼下版本，运行时会好心帮你代理简单的全局动画，截帧看着也对</div>
              <div class="guess-l dim">一条轴几十个动画：相对位置、嵌套、瞬间跳变 —— 代理拆不过来</div>
            </div>
            <div class="guess-box hot" id="ag-sure">
              <div class="guess-h blue">这才是它 <b>保证了</b></div>
              <div class="guess-l">显式注册，才是写进合同里的规矩</div>
            </div>
          </div>
          <div class="ag-rule" id="ag-rule">写能被保证的代码，别写指望别人聪明的代码</div>"""),

# S17 三行凑齐回浏览器播放（录屏 play-final＋freeze）389.34–407.94
Scene("sc-play-final", 389.34, 407.94, """
          <div class="kicker" id="pf-k">三行凑齐：暂停的轴 · 挂在轴上的动画 · 注册到表里 —— 回浏览器，播放</div>
          <div class="recnote" id="pf-n1">第 2 秒标题浮上来，第 3 秒卡片弹一下，第 6 秒副标题进场</div>
          <div class="recnote" id="pf-n2">光这样还不过瘾 —— 打开开发者工具，在控制台亲手播给你看</div>"""),

# S18 __player seek 矩阵（录屏 cs 八段无缝）407.94–436.20
Scene("sc-matrix", 407.94, 436.20, """
          <div class="kicker" id="mx-k">页面上有个现成的播放器对象 window.__player —— 它身上就有 seek</div>
          <div class="matnote" id="mn-player">window.__player</div>
          <div class="matnote" id="mn-24">seek(2.4)：半透明，浮在半路</div>
          <div class="matnote" id="mn-3">seek(3)：标题就位</div>
          <div class="matnote" id="mn-63">seek(6.3)：副标题在半路</div>
          <div class="matnote" id="mn-9">seek(9)：全在</div>
          <div class="matnote" id="mn-0">seek(0)：空舞台</div>
          <div class="matnote" id="mn-five">连着五回 seek 同一个 2.4，五回画面一模一样 —— 时间在这儿能倒着播、来回播</div>"""),

# S19 直接拨轴不行（概念）436.20–462.96
Scene("sc-direct-axis", 436.20, 462.96, """
          <div class="kicker" id="da-k">那我直接调那条轴的 seek，不就行了？—— 还真不行</div>
          <div class="cmp">
            <div class="cmp-box" id="da-axis">
              <div class="cmp-h mute">轴管的是</div>
              <div class="cmp-l"><strong>动画值</strong></div>
              <div class="cmp-l dim">位移 · 缩放 · 透明度</div>
            </div>
            <div class="cmp-box hot" id="da-player">
              <div class="cmp-h blue">播放器管的是</div>
              <div class="cmp-l">一个片段<strong>第几秒出场、第几秒退场</strong></div>
            </div>
          </div>
          <div class="da-ghost" id="da-ghost">你直接播轴：数值播回去了，人还藏着 —— 第 9 秒标题透明度是 1，画面上却没有它</div>
          <div class="da-rule" id="da-rule">亲手播，找 __player：它一声令下，轴和片段一起就位</div>"""),

# S20 两个管家坑（概念）462.96–489.10
Scene("sc-butlers", 462.96, 489.10, """
          <div class="kicker" id="bl-k">顺手送你一条踩过的坑：交给时间轴的动画，只让它一个人管</div>
          <div class="butler-flow">
            <div class="butler-attr" id="bl-attr">transform · opacity</div>
            <div class="butler-hands">
              <span class="butler" id="bl-b1">GSAP 时间轴</span>
              <span class="butler-vs" id="bl-vs">✋</span>
              <span class="butler bad" id="bl-b2">CSS transition</span>
            </div>
          </div>
          <div class="bl-note" id="bl-note">渲染器瞬间设置，过渡想从头补间 —— 同一秒截两回，可能就是两张脸</div>
          <div class="bl-rule" id="bl-rule">一个属性，一个管家</div>"""),

# S21 渲染内核窗户纸＋render 实播（概念头＋录屏 cmd/run/done）489.10–522.94
Scene("sc-render-inner", 489.10, 522.94, """
          <div class="kicker" id="ri-k">到这，可以把渲染内核的窗户纸捅破了</div>
          <div class="pflow compact" id="ri-flow">
            <span class="pstep sm">帧号算出 t</span>
            <span class="parrow">→</span>
            <span class="pstep sm hot">调一声 seek</span>
            <span class="parrow">→</span>
            <span class="pstep sm">全部元素摆到位</span>
            <span class="parrow">→</span>
            <span class="pstep sm">算完样式 · 截图</span>
          </div>
          <div class="recnote" id="ri-n1">无头浏览器干的，跟你刚才在控制台里干的一模一样</div>
          <div class="recnote" id="ri-n2">一帧一帧 seek，一帧一帧截 —— 10 秒 300 帧，它实打实干了 39 秒</div>
          <div class="recnote green" id="ri-n3">绿了：253.9 KB · rendered in 39.0s —— 再交给 FFmpeg 烤成 MP4</div>
          <div class="recnote" id="ri-n4">你在控制台里手播，等于人肉当了一回渲染器</div>"""),

# S22 适配器模式（概念）522.94–554.06
Scene("sc-adapter", 522.94, 554.06, """
          <div class="kicker" id="ad-k">也正因为如此 —— GSAP 不是唯一选择，它只是样板里替你接好的一种</div>
          <div class="adapter">
            <div class="engines" id="ad-engines">
              <span class="eng">CSS 动画</span>
              <span class="eng">WAAPI</span>
              <span class="eng">Lottie</span>
              <span class="eng">Three.js</span>
              <span class="eng">Anime.js</span>
              <span class="eng">自研对象</span>
            </div>
            <div class="plug" id="ad-plug">
              <span class="mono gold plug-code">seek(t)</span>
              <span class="plug-sub">我喊 seek(t)，你得让画面立刻就位</span>
            </div>
          </div>
          <div class="ad-note" id="ad-note">渲染器不在乎你手里攥的是什么，它只认这一个约定 —— 适配器模式，老程序员一看就懂</div>"""),

# S23 行动三条清单（概念）554.06–580.12
Scene("sc-action3", 554.06, 580.12, """
          <div class="kicker" id="ac-k">回去打开你自己的 index.html，查三条</div>
          <div class="acl">
            <div class="acl-row" id="ac-1"><span class="acl-n">①</span>
              动画的时间，是不是交给了一根<strong>能来回播的轴</strong>，而不是跟着墙钟自己跑</div>
            <div class="acl-row" id="ac-2"><span class="acl-n">②</span>
              GSAP 时间轴，是不是 <span class="mono gold">paused = true</span></div>
            <div class="acl-row" id="ac-3"><span class="acl-n">③</span>
              动画都带时刻挂在轴上，注册到 <span class="mono gold">window.__timelines</span>，名字跟
              <span class="mono gold">data-composition-id</span> 对得上</div>
          </div>
          <div class="ac-tail" id="ac-tail">三条齐 —— 你的动画，才是能被渲染的动画</div>"""),

# S24 收尾＋灵魂在 seek 580.12–591.98
Scene("sc-wrap", 580.12, 591.98, """
          <div class="kicker" id="wr-k">今天，从一段看着没问题的计数器，讲到了整类工具最底层的约定</div>
          <div class="wr-main" id="wr-main">不是让画面动起来 ——<br>是让<strong>任意一秒的画面，随叫随到</strong></div>
          <div class="soul-big" id="wr-soul">灵魂，在 seek</div>"""),

# S25 下集预告 check 591.98–604.38
Scene("sc-next", 591.98, 604.38, """
          <div class="kicker" id="nx-k">下一集</div>
          <div class="next-card" id="nx-card">动画挂多了，手滑写错怎么办？</div>
          <div class="nx-list" id="nx-list">
            <span class="nx-i">重叠的</span>
            <span class="nx-i">越界的</span>
            <span class="nx-i">对比度不够的</span>
            <span class="nx-go">让机器先替你挑一遍错</span>
          </div>
          <div class="nx-ep" id="nx-ep">check 门控 · 三层体检，我们一条条过</div>"""),

# S26 道别 604.38–TOTAL
Scene("sc-bye", 604.38, total, """
          <div class="bye" id="bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 顶层录屏/定格/真帧 clip（不可嵌套；放 scenes 之前＝下层） ----------
# video 按精切实长播放；连续动作段无缝相接，需要延长处跟 <img> 定格。
#   起/止＝成片音频秒（与口播拍点对齐，切点依据见 oneoffs/REC-NOTES.md）
VIDEOS = """      <video id="rec-play-static" class="clip" data-start="1.92"
             data-duration="12.50" data-track-index="2"
             src="media/shorts/play-static.mp4" muted playsinline preload="auto"></video>

      <video id="rec-css-kf-mid" class="clip" data-start="30.70"
             data-duration="5.50" data-track-index="2"
             src="media/shorts/css-kf-mid.mp4" muted playsinline preload="auto"></video>
      <video id="rec-css-kf-done" class="clip" data-start="36.40"
             data-duration="4.20" data-track-index="2"
             src="media/shorts/css-kf-done.mp4" muted playsinline preload="auto"></video>
      <video id="rec-play-css" class="clip" data-start="40.60"
             data-duration="11.90" data-track-index="2"
             src="media/shorts/play-css.mp4" muted playsinline preload="auto"></video>

      <video id="rec-snap-css-cmd" class="clip" data-start="100.20"
             data-duration="10.00" data-track-index="2"
             src="media/shorts/snap-css-cmd.mp4" muted playsinline preload="auto"></video>
      <video id="rec-snap-css-run" class="clip" data-start="110.20"
             data-duration="4.10" data-track-index="2"
             src="media/shorts/snap-css-run.mp4" muted playsinline preload="auto"></video>
      <!-- 三真帧二轮：起点整体前移 0.8–1s，帧切换赶在念出下一数字前
           （「二点五」约 115.9、「二点九」约 119.2、「白了」119.86）；
           eq 提前到 120.00 并拉长，尾点 128.94 不变。 -->
      <img id="shot-css-21" class="clip" data-start="114.30"
             data-duration="1.70" src="media/shots/css-2.1.png" alt="">
      <img id="shot-css-25" class="clip" data-start="116.00"
             data-duration="2.60" src="media/shots/css-2.5.png" alt="">
      <img id="shot-css-29" class="clip" data-start="118.60"
             data-duration="1.40" src="media/shots/css-2.9.png" alt="">
      <video id="rec-snap-css-eq" class="clip" data-start="120.00"
             data-duration="8.94" data-track-index="2"
             src="media/shorts/snap-css-eq.mp4" muted playsinline preload="auto"></video>
      <img id="fz-snap-css-eq" class="clip" data-start="128.94"
             data-duration="0.80" src="media/freezes/snap-css-eq.png" alt="">

      <video id="rec-timer-mid" class="clip" data-start="154.80"
             data-duration="4.60" data-track-index="2"
             src="media/shorts/timer-code-mid.mp4" muted playsinline preload="auto"></video>
      <video id="rec-timer-done" class="clip" data-start="159.40"
             data-duration="3.00" data-track-index="2"
             src="media/shorts/timer-code-done.mp4" muted playsinline preload="auto"></video>
      <video id="rec-play-timer" class="clip" data-start="162.40"
             data-duration="4.68" data-track-index="2"
             src="media/shorts/play-timer.mp4" muted playsinline preload="auto"></video>

      <video id="rec-race-q-cmd" class="clip" data-start="168.00"
             data-duration="7.00" data-track-index="2"
             src="media/shorts/race-q-cmd.mp4" muted playsinline preload="auto"></video>
      <video id="rec-race-q-run" class="clip" data-start="175.00"
             data-duration="23.00" data-track-index="2"
             src="media/shorts/race-q-run.mp4" muted playsinline preload="auto"></video>
      <video id="rec-race-q-done" class="clip" data-start="198.00"
             data-duration="4.00" data-track-index="2"
             src="media/shorts/race-q-done.mp4" muted playsinline preload="auto"></video>
      <video id="rec-race-f-start" class="clip" data-start="202.00"
             data-duration="14.00" data-track-index="2"
             src="media/shorts/race-f-start.mp4" muted playsinline preload="auto"></video>
      <video id="rec-race-f-done" class="clip" data-start="216.00"
             data-duration="12.54" data-track-index="2"
             src="media/shorts/race-f-done.mp4" muted playsinline preload="auto"></video>
      <img id="fz-race-f-done" class="clip" data-start="228.54"
             data-duration="0.30" src="media/freezes/race-f-done.png" alt="">

      <video id="rec-check-run" class="clip" data-start="250.20"
             data-duration="8.00" data-track-index="2"
             src="media/shorts/check-run.mp4" muted playsinline preload="auto"></video>
      <video id="rec-check-pass" class="clip" data-start="258.20"
             data-duration="6.00" data-track-index="2"
             src="media/shorts/check-pass.mp4" muted playsinline preload="auto"></video>
      <img id="fz-check-pass" class="clip" data-start="264.20"
             data-duration="0.32" src="media/freezes/check-pass.png" alt="">

      <video id="rec-gsap-paused" class="clip" data-start="290.20"
             data-duration="6.00" data-track-index="2"
             src="media/shorts/gsap-paused.mp4" muted playsinline preload="auto"></video>
      <img id="fz-gsap-paused" class="clip" data-start="296.20"
             data-duration="10.26" src="media/freezes/gsap-paused.png" alt="">

      <video id="rec-gsap-fromto" class="clip" data-start="307.00"
             data-duration="8.50" data-track-index="2"
             src="media/shorts/gsap-fromto.mp4" muted playsinline preload="auto"></video>
      <img id="fz-gsap-fromto" class="clip" data-start="315.50"
             data-duration="17.46" src="media/freezes/gsap-fromto.png" alt="">

      <video id="rec-gsap-register" class="clip" data-start="333.40"
             data-duration="5.80" data-track-index="2"
             src="media/shorts/gsap-register.mp4" muted playsinline preload="auto"></video>
      <video id="rec-gsap-html" class="clip" data-start="339.20"
             data-duration="5.50" data-track-index="2"
             src="media/shorts/gsap-html.mp4" muted playsinline preload="auto"></video>
      <img id="fz-gsap-register" class="clip" data-start="344.70"
             data-duration="12.66" src="media/freezes/gsap-register.png" alt="">

      <video id="rec-play-final" class="clip" data-start="390.00"
             data-duration="12.40" data-track-index="2"
             src="media/shorts/play-final.mp4" muted playsinline preload="auto"></video>
      <img id="fz-play-final" class="clip" data-start="402.40"
             data-duration="5.54" src="media/freezes/play-final.png" alt="">

      <!-- S18 二轮：八段窗口按源时间轴实证重切后首尾相接，408.00–436.20
           恰好铺满；每段敲命令动作略先于念词，结果帧卡念词。 -->
      <video id="rec-cs-open" class="clip" data-start="408.00"
             data-duration="2.20" data-track-index="2"
             src="media/shorts/cs-open.mp4" muted playsinline preload="auto"></video>
      <video id="rec-cs-player" class="clip" data-start="410.20"
             data-duration="1.60" data-track-index="2"
             src="media/shorts/cs-player.mp4" muted playsinline preload="auto"></video>
      <video id="rec-cs-s24" class="clip" data-start="411.80"
             data-duration="2.80" data-track-index="2"
             src="media/shorts/cs-s24.mp4" muted playsinline preload="auto"></video>
      <video id="rec-cs-s3" class="clip" data-start="414.60"
             data-duration="3.20" data-track-index="2"
             src="media/shorts/cs-s3.mp4" muted playsinline preload="auto"></video>
      <video id="rec-cs-s63" class="clip" data-start="417.80"
             data-duration="3.40" data-track-index="2"
             src="media/shorts/cs-s63.mp4" muted playsinline preload="auto"></video>
      <video id="rec-cs-s9" class="clip" data-start="421.20"
             data-duration="2.40" data-track-index="2"
             src="media/shorts/cs-s9.mp4" muted playsinline preload="auto"></video>
      <video id="rec-cs-s0" class="clip" data-start="423.60"
             data-duration="3.40" data-track-index="2"
             src="media/shorts/cs-s0.mp4" muted playsinline preload="auto"></video>
      <video id="rec-cs-five" class="clip" data-start="427.00"
             data-duration="7.60" data-track-index="2"
             src="media/shorts/cs-five.mp4" muted playsinline preload="auto"></video>
      <img id="fz-cs-five" class="clip" data-start="434.60"
             data-duration="1.60" src="media/freezes/cs-five.png" alt="">

      <video id="rec-render-cmd" class="clip" data-start="493.20"
             data-duration="8.00" data-track-index="2"
             src="media/shorts/render-cmd.mp4" muted playsinline preload="auto"></video>
      <video id="rec-render-run" class="clip" data-start="501.20"
             data-duration="18.00" data-track-index="2"
             src="media/shorts/render-run.mp4" muted playsinline preload="auto"></video>
      <video id="rec-render-done" class="clip" data-start="519.20"
             data-duration="3.34" data-track-index="2"
             src="media/shorts/render-done.mp4" muted playsinline preload="auto"></video>
      <img id="fz-render-done" class="clip" data-start="522.54"
             data-duration="0.40" src="media/freezes/render-done.png" alt="">"""

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
      #rec-play-static,
      #rec-css-kf-mid, #rec-css-kf-done, #rec-play-css,
      #rec-snap-css-cmd, #rec-snap-css-run, #rec-snap-css-eq, #fz-snap-css-eq,
      #rec-timer-mid, #rec-timer-done, #rec-play-timer,
      #rec-race-q-cmd, #rec-race-q-run, #rec-race-q-done,
      #rec-race-f-start, #rec-race-f-done, #fz-race-f-done,
      #rec-check-run, #rec-check-pass, #fz-check-pass,
      #rec-gsap-paused, #fz-gsap-paused, #rec-gsap-fromto, #fz-gsap-fromto,
      #rec-gsap-register, #rec-gsap-html, #fz-gsap-register,
      #rec-play-final, #fz-play-final,
      #rec-cs-open, #rec-cs-player, #rec-cs-s24, #rec-cs-s3, #rec-cs-s63,
      #rec-cs-s9, #rec-cs-s0, #rec-cs-five, #fz-cs-five,
      #rec-render-cmd, #rec-render-run, #rec-render-done, #fz-render-done
        { position:absolute;
        left:340px; top:104px; width:1240px; height:713px; object-fit:fill;
        border-radius:10px; box-shadow:0 18px 60px rgba(0,0,0,.55); }

      /* 渲染器真截帧：1920x1080 全屏（画面本体居中，上下自带黑区） */
      #shot-css-21, #shot-css-25, #shot-css-29
        { position:absolute; left:0; top:0; width:1920px; height:1080px;
        object-fit:fill; }

      /* 通用 */
      .kicker { position:absolute; left:0; right:0; top:34px; text-align:center;
        font-size:44px; color:#8b949e; }
      .kicker.red { color:#f85149; } .kicker.green { color:#3fb950; }
      .mono { font-family:'Consolas','Courier New',monospace; color:#e6edf3; }
      .mono.gold { color:#e3b341; }
      /* 同 hf-03：tl.from 元素 CSS 不写 opacity:0（immediateRender 缓存坑）。 */
      .recnote { position:absolute; left:120px; right:120px; bottom:132px; z-index:5;
        text-align:center; font-size:42px; color:#c9d1d9;
        text-shadow:0 2px 18px rgba(0,0,0,.85); }
      .recnote.red { color:#ffa198; } .recnote.green { color:#7ee787; }
      .matnote { position:absolute; left:120px; right:120px; bottom:132px; z-index:6;
        text-align:center; font-size:40px; color:#e3b341;
        text-shadow:0 2px 18px rgba(0,0,0,.9); }

      /* S1 */
      .op-ep { position:absolute; left:0; right:0; top:330px; text-align:center;
        font-size:48px; color:#8b949e; letter-spacing:.3em; }
      .op-title { position:absolute; left:0; right:0; top:420px; text-align:center;
        font-size:140px; color:#e3b341; letter-spacing:.14em; }

      /* S2 */
      .core-badge { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:54px; color:#58a6ff; letter-spacing:.12em; }
      .cmp { position:absolute; left:0; right:0; top:268px; text-align:center; }
      .cmp-box { display:inline-block; width:580px; padding:40px 48px; margin:0 28px;
        background:#161b22; border:2px solid #2b3c57;
        box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 10px 30px rgba(0,0,0,.38);
        border-radius:20px; vertical-align:top; }
      .cmp-box.hot { border-color:#1f6feb; }
      .cmp-box.bad { border-color:#6e3b3b; }
      .cmp-h { font-size:48px; margin-bottom:22px; }
      .cmp-h.mute { color:#8b949e; } .cmp-h.blue { color:#58a6ff; } .cmp-h.red { color:#ffa198; }
      .cmp-l { font-size:42px; color:#e6edf3; line-height:1.75; }
      .cmp-l.dim { color:#8b949e; font-size:36px; margin-top:10px; }
      .cx-key { position:absolute; left:120px; right:120px; bottom:250px; text-align:center;
        font-size:54px; color:#e3b341; line-height:1.5; }

      /* S4 渲染器流程 */
      .wrong-card { position:absolute; left:50%; top:170px; margin-left:-520px;
        width:1040px; padding:28px 40px; text-align:center; font-size:44px;
        color:#f08d85; background:#161b22; border:2px solid #5e2b2b; border-radius:16px; }
      .wrong-s { color:#f85149; font-size:50px; margin-right:16px; }
      .pflow { position:absolute; left:0; right:0; top:360px; text-align:center; }
      .pstep { display:inline-block; width:300px; padding:34px 20px; margin:0 6px;
        background:#161b22; border:2px solid #2b3c57; border-radius:18px;
        font-size:40px; color:#8b949e; line-height:1.5; vertical-align:middle; }
      .pstep b { color:#e6edf3; font-weight:600; }
      .pstep.hot { border-color:#e3b341; background:rgba(227,179,65,.08); }
      .pstep.sm { width:auto; padding:24px 30px; font-size:38px; }
      .pstep.sm b { color:#58a6ff; }
      .parrow { display:inline-block; font-size:56px; color:#8b949e; margin:0 10px;
        vertical-align:middle; }
      .rand-note { position:absolute; left:180px; right:180px; bottom:240px; text-align:center;
        font-size:44px; color:#c9d1d9; line-height:1.6; }

      /* S5 seekable */
      .q-card { position:absolute; left:160px; right:160px; top:165px; text-align:center;
        font-size:62px; color:#e6edf3; line-height:1.7; }
      .seek-sub { position:absolute; left:0; right:0; top:392px; text-align:center;
        font-size:44px; color:#8b949e; letter-spacing:.1em; }
      .seek-word { position:absolute; left:0; right:0; top:462px; text-align:center;
        font-family:'Consolas','Courier New',monospace; font-size:150px;
        color:#e3b341; letter-spacing:.06em; line-height:1.02; }
      .seek-cn { position:absolute; left:0; right:0; top:636px; text-align:center;
        font-size:52px; color:#58a6ff; letter-spacing:.6em; line-height:1.1; }
      .seek-notes { position:absolute; left:0; right:0; bottom:160px; text-align:center; }
      .seek-note { display:block; font-size:42px; color:#c9d1d9; line-height:1.9; }

      /* S7 运行时接管 */
      .rt-flow { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .rt-box { display:inline-block; width:560px; padding:42px 44px; margin:0 24px;
        background:#161b22; border:2px solid #2b3c57; border-radius:20px;
        vertical-align:middle; }
      .rt-box.old { border-color:#6e3b3b; } .rt-box.hot { border-color:#1f6feb; }
      .rt-h { font-size:44px; color:#8b949e; margin-bottom:20px; }
      .rt-b { font-size:46px; color:#e6edf3; line-height:1.6; }
      .rt-arrow { display:inline-block; font-size:52px; color:#e3b341; margin:0 10px;
        vertical-align:middle; }
      .rt-note { position:absolute; left:160px; right:160px; bottom:270px; text-align:center;
        font-size:50px; color:#e3b341; }

      /* S8 */
      .hurry { position:absolute; left:120px; right:120px; top:330px; text-align:center;
        font-size:58px; color:#8b949e; line-height:1.7; }
      .hurry-em { color:#e3b341; }

      /* S9/S10 真帧证据墙（场景内普通 img，随场景 JS 显隐） */
      .shot-strip { position:absolute; left:60px; right:60px; top:210px; z-index:6;
        text-align:center; }
      .shot-cell { display:inline-block; width:560px; margin:0 14px; vertical-align:top;
        background:#0d1521; border:2px solid #30363d; border-radius:12px; padding:10px 10px 0; }
      .shot-cell.hot { border-color:#e3b341; box-shadow:0 0 36px rgba(227,179,65,.25); }
      .shot-cell img { display:block; width:540px; height:304px; object-fit:fill;
        border-radius:6px; }
      .shot-tag { display:block; padding:14px 0; font-size:34px; color:#c9d1d9; }
      .shot-cell.hot .shot-tag { color:#e3b341; }
      .shot-grid6 { position:absolute; left:80px; right:80px; top:170px; z-index:6;
        text-align:center; }
      .shot-grid6 .shot-cell { width:540px; margin:6px 12px; }
      .shot-grid6 .shot-cell img { width:520px; height:293px; }

      /* S11 问答 */
      .qa-card { position:absolute; left:200px; right:200px; top:560px;
        background:#0d1521; border:2px solid #30363d; border-radius:18px; padding:28px 44px; }
      .qa-q { font-size:44px; color:#58a6ff; line-height:1.6; }
      .qa-a { font-size:40px; color:#c9d1d9; line-height:1.6; margin-top:12px; }

      /* S12 薛定谔 */
      .black-chips { position:absolute; left:0; right:0; top:180px; text-align:center; }
      .chip-bad { display:inline-block; margin:0 16px; padding:20px 38px; font-size:44px;
        font-family:'Consolas','Courier New',monospace; color:#ffa198;
        background:rgba(248,81,73,.08); border:2px solid #5e2b2b; border-radius:999px; }
      .sd-verdict { position:absolute; left:0; right:0; top:320px; text-align:center;
        font-size:64px; color:#f08d85; }
      .axis-gold { position:absolute; left:200px; right:200px; top:500px; text-align:center; }
      .axis-label { display:block; font-size:44px; color:#c9d1d9; margin-bottom:26px; }
      .axis-line { display:block; position:relative; height:8px; margin:0 120px;
        background:linear-gradient(90deg,#8a6a1e,#e3b341,#8a6a1e); border-radius:4px; }
      .axis-line i { position:absolute; left:50%; top:-16px; width:40px; height:40px;
        margin-left:-20px; background:#e3b341; border-radius:50%;
        box-shadow:0 0 30px rgba(227,179,65,.7); }
      .axis-name { display:block; font-size:56px; color:#e3b341; margin-top:30px; }
      .sd-gsap { position:absolute; left:160px; right:160px; bottom:230px; text-align:center;
        font-size:48px; color:#e6edf3; line-height:1.6; }

      /* S13 代码卡 */
      .code-card { position:absolute; left:50%; top:200px; margin-left:-620px;
        width:1240px; padding:34px 44px; background:#0d1521; border:2px solid #30363d;
        border-radius:16px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      .code-card.small { top:180px; margin-left:-560px; width:1120px; }
      .code-line { position:relative; font-family:'Consolas','Courier New',monospace;
        font-size:46px; line-height:1.72; color:#8b949e; white-space:nowrap; }
      .ln { display:inline-block; width:60px; color:#6e7681; text-align:right;
        margin-right:28px; }
      .tk-attr { color:#58a6ff; } .tk-str { color:#e3b341; } .tk-kw { color:#ff7b72; }

      /* S16 猜中/保证 */
      .guess-grid { position:absolute; left:0; right:0; top:250px; text-align:center; }
      .guess-box { display:inline-block; width:620px; padding:42px 46px; margin:0 26px;
        background:#161b22; border:2px solid #2b3c57; border-radius:20px;
        vertical-align:top; text-align:left; }
      .guess-box.hot { border-color:#3fb950; background:rgba(63,185,80,.07); }
      .guess-h { font-size:52px; margin-bottom:24px; }
      .guess-h.mute { color:#f08d85; } .guess-h.blue { color:#7ee787; }
      .guess-l { font-size:42px; color:#e6edf3; line-height:1.7; margin-bottom:16px; }
      .guess-l.dim { color:#8b949e; font-size:36px; }
      .ag-rule { position:absolute; left:120px; right:120px; bottom:250px; text-align:center;
        font-size:58px; color:#e3b341; }

      /* S19 直接拨轴 */
      .da-ghost { position:absolute; left:180px; right:180px; top:560px; text-align:center;
        font-size:46px; color:#ffa198; background:rgba(248,81,73,.07);
        border:2px solid #5e2b2b; border-radius:16px; padding:28px 40px; line-height:1.6; }
      .da-rule { position:absolute; left:120px; right:120px; bottom:260px; text-align:center;
        font-size:54px; color:#7ee787; }

      /* S20 两个管家 */
      .butler-flow { position:absolute; left:0; right:0; top:280px; text-align:center; }
      .butler-attr { display:inline-block; padding:24px 56px; font-size:54px;
        font-family:'Consolas','Courier New',monospace; color:#58a6ff;
        background:#0d1521; border:2px solid #30363d; border-radius:16px; margin-bottom:44px; }
      .butler-hands { font-size:0; }
      .butler { display:inline-block; padding:30px 50px; margin:0 24px; font-size:48px;
        border-radius:18px; background:#161b22; border:2px solid #2b573f; color:#7ee787; }
      .butler.bad { border-color:#6e3b3b; color:#f08d85; }
      .butler-vs { display:inline-block; font-size:56px; color:#e3b341; margin:0 8px; }
      .bl-note { position:absolute; left:180px; right:180px; top:600px; text-align:center;
        font-size:44px; color:#c9d1d9; line-height:1.6; }
      .bl-rule { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:68px; color:#e3b341; letter-spacing:.08em; }

      /* S22 适配器 */
      .adapter { position:absolute; left:0; right:0; top:240px; text-align:center; }
      .engines { margin-bottom:56px; }
      .eng { display:inline-block; margin:10px 14px; padding:22px 40px; font-size:44px;
        color:#c9d1d9; background:#161b22; border:2px solid #2b3c57; border-radius:999px; }
      .plug { display:inline-block; padding:40px 80px; background:rgba(227,179,65,.1);
        border:3px solid #e3b341; border-radius:22px; }
      .plug-code { display:block; font-size:96px; letter-spacing:.04em; }
      .plug-sub { display:block; font-size:42px; color:#c9d1d9; margin-top:14px; }
      .ad-note { position:absolute; left:140px; right:140px; bottom:240px; text-align:center;
        font-size:48px; color:#8b949e; line-height:1.6; }

      /* S23 三条清单 */
      .acl { position:absolute; left:140px; right:140px; top:200px; }
      .acl-row { padding:30px 40px; margin-bottom:26px; background:#161b22;
        border:2px solid #2b3c57; border-left:10px solid #1f6feb; border-radius:14px;
        font-size:44px; color:#e6edf3; line-height:1.55; }
      .acl-n { color:#e3b341; font-size:52px; margin-right:20px; }
      .ac-tail { position:absolute; left:0; right:0; bottom:240px; text-align:center;
        font-size:56px; color:#7ee787; }

      /* S24 收尾 */
      .wr-main { position:absolute; left:120px; right:120px; top:330px; text-align:center;
        font-size:62px; color:#e6edf3; line-height:1.7; }
      .soul-big { position:absolute; left:0; right:0; bottom:230px; text-align:center;
        font-size:120px; color:#e3b341; letter-spacing:.16em; }

      /* S25 下集 */
      .next-card { position:absolute; left:160px; right:160px; top:250px; text-align:center;
        font-size:64px; color:#e6edf3; }
      .nx-list { position:absolute; left:0; right:0; top:430px; text-align:center; }
      .nx-i { display:inline-block; margin:0 18px; padding:18px 38px; font-size:44px;
        color:#ffa198; background:rgba(248,81,73,.08); border:2px solid #5e2b2b;
        border-radius:999px; }
      .nx-go { display:block; margin-top:36px; font-size:52px; color:#c9d1d9; }
      .nx-ep { position:absolute; left:0; right:0; bottom:280px; text-align:center;
        font-size:50px; color:#58a6ff; letter-spacing:.08em; }

      /* S26 道别 */
      .bye { position:absolute; left:0; right:0; top:440px; text-align:center;
        font-size:72px; color:#e6edf3; letter-spacing:.08em; }
"""

# ---------- 场景时间轴（时间显式给秒） ----------
SCENE_JS = """
      /* S1 0–14.42：片名 0.2–1.8，随后承上录屏 play-static 1.92 起 */
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#op-ep',{y:18,opacity:0,duration:.6},.2);
      tl.from('#op-title',{scale:.8,opacity:0,duration:.8,ease:'back.out(1.5)'},.5);
      tl.to('#op-ep',{opacity:0,duration:.3},1.55);
      tl.to('#op-title',{opacity:0,duration:.3},1.55);
      tl.from('#op-k',{y:18,opacity:0,duration:.6},2.1);
      tl.from('#op-n',{opacity:0,duration:.5},8.4);
      tl.to('#sc-open > .scene-inner',{opacity:0,duration:.4},14.02);

      /* S2 14.42–30.50 */
      tl.fromTo('#sc-fly > .scene-inner',{opacity:0},{opacity:1,duration:.5},14.42);
      tl.from('#fy-k',{y:18,opacity:0,duration:.6},14.7);
      tl.from('#fy-badge',{scale:.8,opacity:0,duration:.7,ease:'back.out(1.4)'},16.2);
      tl.from('#fy-old',{x:-50,opacity:0,duration:.7,ease:'back.out(1.4)'},18.0);
      tl.from('#fy-hf',{x:50,opacity:0,duration:.7,ease:'back.out(1.4)'},22.6);
      tl.from('#fy-key',{y:22,opacity:0,duration:.7},26.8);
      tl.to('#sc-fly > .scene-inner',{opacity:0,duration:.4},30.10);

      /* S3 30.50–52.50：mid 30.7 / done 36.4 / play-css 40.6，底注轮替 */
      tl.fromTo('#sc-css-kf > .scene-inner',{opacity:0},{opacity:1,duration:.5},30.50);
      tl.from('#kf-k',{y:18,opacity:0,duration:.6},30.8);
      tl.from('#kf-n1',{opacity:0,duration:.5},31.1);
      tl.to('#kf-n1',{opacity:0,duration:.3},36.2);
      tl.from('#kf-n2',{opacity:0,duration:.5},40.8);
      tl.to('#kf-n2',{opacity:0,duration:.3},43.4);
      tl.from('#kf-n3',{opacity:0,duration:.5},43.8);
      tl.to('#kf-n3',{opacity:0,duration:.3},47.2);
      tl.from('#kf-n4',{opacity:0,duration:.5},47.6);
      tl.to('#sc-css-kf > .scene-inner',{opacity:0,duration:.4},52.10);

      /* S4 52.50–74.98 */
      tl.fromTo('#sc-render-how > .scene-inner',{opacity:0},{opacity:1,duration:.5},52.50);
      tl.from('#rw-k',{y:18,opacity:0,duration:.6},52.8);
      tl.from('#rw-wrong',{scale:.9,opacity:0,duration:.6},54.6);
      tl.from('.pflow#rw-flow .pstep',{y:30,opacity:0,duration:.5,stagger:.28},58.4);
      tl.from('#rw-rand',{y:22,opacity:0,duration:.7},66.2);
      tl.to('#sc-render-how > .scene-inner',{opacity:0,duration:.4},74.58);

      /* S5 74.98–99.30：seekable 词戳 89.04、agent 94.10（raw.json 实测） */
      tl.fromTo('#sc-seekable > .scene-inner',{opacity:0},{opacity:1,duration:.5},74.98);
      tl.from('#sk-k',{y:18,opacity:0,duration:.6},75.3);
      tl.from('#sk-card',{scale:.92,opacity:0,duration:.7,ease:'back.out(1.3)'},78.6);
      tl.from('#sk-sub',{opacity:0,duration:.6},84.8);
      tl.from('#sk-word',{scale:.6,opacity:0,duration:.8,ease:'back.out(1.5)'},88.4);
      tl.from('#sk-cn',{y:18,opacity:0,duration:.6},91.6);
      tl.from('.seek-notes .seek-note',{y:20,opacity:0,duration:.6,stagger:.5},93.4);
      tl.to('#sc-seekable > .scene-inner',{opacity:0,duration:.4},98.90);

      /* S6 99.30–129.74：cmd 100.2 / run 110.2 / 三真帧 115.2/117.3/119.4 / eq 121.0 */
      tl.fromTo('#sc-snap-css > .scene-inner',{opacity:0},{opacity:1,duration:.5},99.30);
      tl.from('#sn-k',{y:18,opacity:0,duration:.6},99.6);
      tl.from('#sn-n1',{opacity:0,duration:.5},100.4);
      tl.to('#sn-n1',{opacity:0,duration:.3},114.1);
      tl.from('#sn-n21',{opacity:0,duration:.4},114.35);
      tl.to('#sn-n21',{opacity:0,duration:.3},115.95);
      tl.from('#sn-n25',{opacity:0,duration:.4},116.05);
      tl.to('#sn-n25',{opacity:0,duration:.3},118.55);
      tl.from('#sn-n29',{opacity:0,duration:.4},118.65);
      tl.to('#sn-n29',{opacity:0,duration:.3},119.95);
      tl.from('#sn-n2',{opacity:0,duration:.6},122.4);
      tl.to('#sc-snap-css > .scene-inner',{opacity:0,duration:.4},129.34);

      /* S7 129.74–149.96 */
      tl.fromTo('#sc-runtime > .scene-inner',{opacity:0},{opacity:1,duration:.5},129.74);
      tl.from('#rt-k',{y:18,opacity:0,duration:.6},130.0);
      tl.from('#rt-old',{x:-46,opacity:0,duration:.7,ease:'back.out(1.3)'},133.0);
      tl.from('#rt-arrow',{opacity:0,duration:.5},138.6);
      tl.from('#rt-new',{x:46,opacity:0,duration:.7,ease:'back.out(1.3)'},139.4);
      tl.from('#rt-note',{y:22,opacity:0,duration:.7},144.6);
      tl.to('#sc-runtime > .scene-inner',{opacity:0,duration:.4},149.56);

      /* S8 149.96–167.08：过渡 4.4s，timer 代码 154.8 起，播放 162.4 */
      tl.fromTo('#sc-timer > .scene-inner',{opacity:0},{opacity:1,duration:.5},149.96);
      tl.from('#tm-hurry',{scale:.9,opacity:0,duration:.7,ease:'back.out(1.3)'},150.3);
      tl.to('#tm-hurry',{opacity:0,duration:.35},154.3);
      tl.from('#tm-k',{y:18,opacity:0,duration:.6},154.9);
      tl.from('#tm-n',{opacity:0,duration:.5},162.8);
      tl.to('#sc-timer > .scene-inner',{opacity:0,duration:.4},166.68);

      /* S9 167.08–198.00：cmd 168 / run 175；ser 三真帧 185–192 */
      tl.fromTo('#sc-race-q > .scene-inner',{opacity:0},{opacity:1,duration:.5},167.08);
      tl.from('#rq-k',{y:18,opacity:0,duration:.6},167.4);
      tl.from('#rq-n1',{opacity:0,duration:.5},168.6);
      tl.to('#rq-n1',{opacity:0,duration:.3},184.4);
      tl.from('#rq-shots',{y:40,opacity:0,duration:.7,ease:'back.out(1.3)'},185.0);
      tl.to('#rq-shots',{opacity:0,duration:.4},192.2);
      tl.from('#rq-n3',{opacity:0,duration:.6},192.6);
      tl.to('#sc-race-q > .scene-inner',{opacity:0,duration:.4},197.60);

      /* S10 198.00–228.84：q-done 198 / f-start 202 / f-done 216；tk 六真帧 219.5–223.5 */
      tl.fromTo('#sc-race-f > .scene-inner',{opacity:0},{opacity:1,duration:.5},198.00);
      tl.from('#rf-k',{y:18,opacity:0,duration:.6},198.3);
      tl.from('#rf-n1',{opacity:0,duration:.5},198.6);
      tl.to('#rf-n1',{opacity:0,duration:.3},201.8);
      tl.from('#rf-n2',{opacity:0,duration:.5},202.4);
      tl.to('#rf-n2',{opacity:0,duration:.3},219.2);
      tl.from('#rf-shots',{scale:.92,opacity:0,duration:.6,ease:'back.out(1.2)'},219.5);
      tl.to('#rf-shots',{opacity:0,duration:.4},223.5);
      tl.from('#rf-n3',{opacity:0,duration:.6},224.0);
      tl.to('#sc-race-f > .scene-inner',{opacity:0,duration:.4},228.44);

      /* S11 228.84–264.52：概念至 250.2，check-run/pass 250.2/258.2 */
      tl.fromTo('#sc-check-green > .scene-inner',{opacity:0},{opacity:1,duration:.5},228.84);
      tl.from('#cg-k',{y:18,opacity:0,duration:.6},229.1);
      tl.from('#cg-css',{x:-46,opacity:0,duration:.6,ease:'back.out(1.3)'},231.4);
      tl.from('#cg-timer',{x:46,opacity:0,duration:.6,ease:'back.out(1.3)'},235.4);
      tl.from('#cg-qa',{y:26,opacity:0,duration:.7},240.6);
      tl.to('#cg-k',{opacity:0,duration:.3},249.8);
      tl.to('#cg-css',{opacity:0,duration:.3},249.8);
      tl.to('#cg-timer',{opacity:0,duration:.3},249.8);
      tl.to('#cg-qa',{opacity:0,duration:.3},249.8);
      tl.from('#cg-n1',{opacity:0,duration:.5},252.4);
      tl.to('#cg-n1',{opacity:0,duration:.3},259.0);
      tl.from('#cg-n2',{opacity:0,duration:.6},259.4);
      tl.to('#sc-check-green > .scene-inner',{opacity:0,duration:.4},264.12);

      /* S12 264.52–289.62 */
      tl.fromTo('#sc-schrodinger > .scene-inner',{opacity:0},{opacity:1,duration:.5},264.52);
      tl.from('#sd-k',{y:18,opacity:0,duration:.6},264.8);
      tl.from('.black-chips .chip-bad',{y:24,opacity:0,duration:.5,stagger:.18},267.6);
      tl.from('#sd-verdict',{scale:.9,opacity:0,duration:.7,ease:'back.out(1.3)'},272.0);
      tl.from('#sd-axis',{y:26,opacity:0,duration:.7},276.4);
      tl.from('#sd-gsap',{y:22,opacity:0,duration:.7},283.4);
      tl.to('#sc-schrodinger > .scene-inner',{opacity:0,duration:.4},289.22);

      /* S13 289.62–306.46：录屏 paused 290.2–296.2，freeze 至 306.46 */
      tl.fromTo('#sc-gsap-1 > .scene-inner',{opacity:0},{opacity:1,duration:.5},289.62);
      tl.from('#g1-k',{y:18,opacity:0,duration:.6},289.9);
      tl.from('#g1-card',{scale:.9,opacity:0,duration:.6,ease:'back.out(1.3)'},290.6);
      tl.to('#g1-card',{opacity:0,duration:.35},296.0);
      tl.from('#g1-n1',{opacity:0,duration:.5},296.6);
      tl.to('#g1-n1',{opacity:0,duration:.3},300.0);
      tl.from('#g1-n2',{opacity:0,duration:.5},300.4);
      tl.to('#g1-n2',{opacity:0,duration:.3},303.0);
      tl.from('#g1-n3',{opacity:0,duration:.5},303.3);
      tl.to('#sc-gsap-1 > .scene-inner',{opacity:0,duration:.4},306.06);

      /* S14 306.46–332.96：录屏 fromTo 307–315.5，freeze 至 332.96 */
      tl.fromTo('#sc-gsap-2 > .scene-inner',{opacity:0},{opacity:1,duration:.5},306.46);
      tl.from('#g2-k',{y:18,opacity:0,duration:.6},306.8);
      tl.from('#g2-n1',{opacity:0,duration:.5},315.9);
      tl.to('#g2-n1',{opacity:0,duration:.3},320.6);
      tl.from('#g2-n2',{opacity:0,duration:.5},321.0);
      tl.to('#g2-n2',{opacity:0,duration:.3},325.8);
      tl.from('#g2-n3',{opacity:0,duration:.6},326.2);
      tl.to('#sc-gsap-2 > .scene-inner',{opacity:0,duration:.4},332.56);

      /* S15 332.96–357.36：register 333.4 / html 343.7 / register freeze 349.2 */
      tl.fromTo('#sc-gsap-3 > .scene-inner',{opacity:0},{opacity:1,duration:.5},332.96);
      tl.from('#g3-k',{y:18,opacity:0,duration:.6},333.2);
      tl.from('#g3-n1',{opacity:0,duration:.5},334.0);
      tl.to('#g3-n1',{opacity:0,duration:.3},339.1);
      tl.from('#g3-n2',{opacity:0,duration:.5},339.5);
      tl.to('#g3-n2',{opacity:0,duration:.3},344.6);
      tl.from('#g3-n3',{opacity:0,duration:.5},344.9);
      tl.to('#g3-n3',{opacity:0,duration:.3},349.5);
      tl.from('#g3-n4',{opacity:0,duration:.5},349.7);
      tl.to('#sc-gsap-3 > .scene-inner',{opacity:0,duration:.4},356.96);

      /* S16 357.36–389.34 */
      tl.fromTo('#sc-agent > .scene-inner',{opacity:0},{opacity:1,duration:.5},357.36);
      tl.from('#ag-k',{y:18,opacity:0,duration:.6},357.7);
      tl.from('#ag-guess',{x:-50,opacity:0,duration:.7,ease:'back.out(1.3)'},363.0);
      tl.from('#ag-sure',{x:50,opacity:0,duration:.7,ease:'back.out(1.3)'},370.0);
      tl.from('#ag-rule',{scale:.9,opacity:0,duration:.8,ease:'back.out(1.4)'},379.0);
      tl.to('#sc-agent > .scene-inner',{opacity:0,duration:.4},388.94);

      /* S17 389.34–407.94：录屏 play-final 390–402.4，freeze 至 407.94 */
      tl.fromTo('#sc-play-final > .scene-inner',{opacity:0},{opacity:1,duration:.5},389.34);
      tl.from('#pf-k',{y:18,opacity:0,duration:.6},389.6);
      tl.from('#pf-n1',{opacity:0,duration:.5},392.2);
      tl.to('#pf-n1',{opacity:0,duration:.3},402.2);
      tl.from('#pf-n2',{opacity:0,duration:.6},402.8);
      tl.to('#sc-play-final > .scene-inner',{opacity:0,duration:.4},407.54);

      /* S18 407.94–436.20：cs 八段 408.2 起无缝，注解跟拍 */
      tl.fromTo('#sc-matrix > .scene-inner',{opacity:0},{opacity:1,duration:.5},407.94);
      tl.from('#mx-k',{y:18,opacity:0,duration:.6},408.3);
      tl.from('#mn-player',{opacity:0,duration:.4},410.30);
      tl.to('#mn-player',{opacity:0,duration:.25},411.75);
      tl.from('#mn-24',{opacity:0,duration:.4},411.90);
      tl.to('#mn-24',{opacity:0,duration:.25},414.55);
      tl.from('#mn-3',{opacity:0,duration:.4},414.70);
      tl.to('#mn-3',{opacity:0,duration:.25},417.75);
      tl.from('#mn-63',{opacity:0,duration:.4},417.90);
      tl.to('#mn-63',{opacity:0,duration:.25},421.15);
      tl.from('#mn-9',{opacity:0,duration:.4},421.30);
      tl.to('#mn-9',{opacity:0,duration:.25},423.55);
      tl.from('#mn-0',{opacity:0,duration:.4},423.70);
      tl.to('#mn-0',{opacity:0,duration:.25},426.90);
      tl.from('#mn-five',{opacity:0,duration:.5},427.10);
      tl.to('#sc-matrix > .scene-inner',{opacity:0,duration:.4},435.80);

      /* S19 436.20–462.96 */
      tl.fromTo('#sc-direct-axis > .scene-inner',{opacity:0},{opacity:1,duration:.5},436.20);
      tl.from('#da-k',{y:18,opacity:0,duration:.6},436.5);
      tl.from('#da-axis',{x:-46,opacity:0,duration:.6,ease:'back.out(1.3)'},440.0);
      tl.from('#da-player',{x:46,opacity:0,duration:.6,ease:'back.out(1.3)'},445.0);
      tl.from('#da-ghost',{y:24,opacity:0,duration:.7},450.4);
      tl.from('#da-rule',{y:22,opacity:0,duration:.7},456.0);
      tl.to('#sc-direct-axis > .scene-inner',{opacity:0,duration:.4},462.56);

      /* S20 462.96–489.10 */
      tl.fromTo('#sc-butlers > .scene-inner',{opacity:0},{opacity:1,duration:.5},462.96);
      tl.from('#bl-k',{y:18,opacity:0,duration:.6},463.3);
      tl.from('#bl-attr',{scale:.9,opacity:0,duration:.6},466.6);
      tl.from('#bl-b1',{x:-30,opacity:0,duration:.5},470.4);
      tl.from('#bl-vs',{opacity:0,duration:.4},472.0);
      tl.from('#bl-b2',{x:30,opacity:0,duration:.5},472.6);
      tl.from('#bl-note',{y:22,opacity:0,duration:.6},476.4);
      tl.from('#bl-rule',{scale:.85,opacity:0,duration:.8,ease:'back.out(1.5)'},482.0);
      tl.to('#sc-butlers > .scene-inner',{opacity:0,duration:.4},488.70);

      /* S21 489.10–522.94：概念头 4s，cmd 493.2 / run 501.2 / done 519.2 */
      tl.fromTo('#sc-render-inner > .scene-inner',{opacity:0},{opacity:1,duration:.5},489.10);
      tl.from('#ri-k',{y:18,opacity:0,duration:.6},489.4);
      tl.from('#ri-flow .pstep',{y:20,opacity:0,duration:.4,stagger:.18},490.0);
      tl.from('#ri-n1',{opacity:0,duration:.5},491.0);
      tl.to('#ri-flow',{opacity:0,duration:.3},493.0);
      tl.to('#ri-n1',{opacity:0,duration:.3},495.0);
      tl.from('#ri-n2',{opacity:0,duration:.6},502.0);
      tl.to('#ri-n2',{opacity:0,duration:.3},519.6);
      tl.from('#ri-n3',{opacity:0,duration:.5},519.8);
      tl.to('#ri-n3',{opacity:0,duration:.3},521.2);
      tl.from('#ri-n4',{opacity:0,duration:.5},521.4);
      tl.to('#sc-render-inner > .scene-inner',{opacity:0,duration:.4},522.54);

      /* S22 522.94–554.06 */
      tl.fromTo('#sc-adapter > .scene-inner',{opacity:0},{opacity:1,duration:.5},522.94);
      tl.from('#ad-k',{y:18,opacity:0,duration:.6},523.2);
      tl.from('.engines .eng',{y:24,opacity:0,duration:.45,stagger:.12},526.0);
      tl.from('#ad-plug',{scale:.8,opacity:0,duration:.8,ease:'back.out(1.4)'},532.0);
      tl.from('#ad-note',{y:22,opacity:0,duration:.7},544.0);
      tl.to('#sc-adapter > .scene-inner',{opacity:0,duration:.4},553.66);

      /* S23 554.06–580.12 */
      tl.fromTo('#sc-action3 > .scene-inner',{opacity:0},{opacity:1,duration:.5},554.06);
      tl.from('#ac-k',{y:18,opacity:0,duration:.6},554.4);
      tl.from('.acl .acl-row',{x:-40,opacity:0,duration:.6,stagger:1.9},556.4);
      tl.from('#ac-tail',{scale:.9,opacity:0,duration:.8,ease:'back.out(1.4)'},573.0);
      tl.to('#sc-action3 > .scene-inner',{opacity:0,duration:.4},579.72);

      /* S24 580.12–591.98 */
      tl.fromTo('#sc-wrap > .scene-inner',{opacity:0},{opacity:1,duration:.5},580.12);
      tl.from('#wr-k',{y:18,opacity:0,duration:.6},580.4);
      tl.from('#wr-main',{y:26,opacity:0,duration:.8},583.4);
      tl.from('#wr-soul',{scale:.65,opacity:0,duration:.9,ease:'back.out(1.5)'},589.2);
      tl.to('#sc-wrap > .scene-inner',{opacity:0,duration:.4},591.58);

      /* S25 591.98–604.38 */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},591.98);
      tl.from('#nx-k',{y:18,opacity:0,duration:.6},592.3);
      tl.from('#nx-card',{y:24,opacity:0,duration:.7},593.4);
      tl.from('.nx-list .nx-i',{y:20,opacity:0,duration:.5,stagger:.22},596.4);
      tl.from('.nx-list .nx-go',{opacity:0,duration:.6},598.4);
      tl.from('#nx-ep',{y:20,opacity:0,duration:.6},600.8);
      tl.to('#sc-next > .scene-inner',{opacity:0,duration:.4},603.98);

      /* S26 604.38–TOTAL */
      tl.fromTo('#sc-bye > .scene-inner',{opacity:0},{opacity:1,duration:.5},604.38);
      tl.from('#bye',{y:24,opacity:0,duration:.7},604.6);
"""

# ---------- 底部字幕轨道 ----------
# time_offset：faster-whisper 吞句间停顿致字幕整体偏早；hf-01 实测 0.28、
# hf-02 0.37、hf-03 0.29。hf-04 经 oneoffs/measure_offset.py 实测：
# 58/71 onset 配对，中位 +300.1ms／均值 +301.5ms（195–525ms）→ 取 0.30。
frag = char_track(cues, chars, THEME.accent, time_offset=0.30)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/hf-04-yeyang.wav", total),
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
print("已生成 index.html（%.2f 秒，%d 幕，%d 句，33 段录屏＋12 张渲染器真帧）"
      % (total, len(SCENES), len(cues)))
