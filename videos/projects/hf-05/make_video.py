# -*- coding: utf-8 -*-
"""HyperFrames 教程第 5 集《你的视频代码有没有错，别用眼睛看：check 门控实操》。

靛蓝深＋金网格主题（沿用 hf-01/02/03/04），552.49s，17 幕。教学核心＝
check 六道关（Lint/Runtime/Layout/Motion/Contrast/Snapshots）与
警告/错误之分：警告是「页面成立但有后果」exit 0，错误是「页面不成立」
exit 1，这道闸能直接挂进 CI。全片用七组真机实验展开：删 data-duration
（missing_timing 黄）、彩蛋越界（ends_past_root_duration 黄＋双修法）、
深蓝灰 #1a1f26（Contrast 四✗ 1.14:1 vs 3:1，Try rgb(93,97,102) 递修法）、
同轨重叠全绿＋DOM 对调仍绿（track-index 只是 Studio 元数据）、贴不透明
色块（text_occluded 九采样点全抓）、#sut 拼错（三警告静默失踪）、
page_error 连坐；收尾体检三命令 keyframes(--shot)/inspect/beats 与
echo %ERRORLEVEL% 回显 0。

素材先行：23 段录屏短片（oneoffs/cut_final.py 从 21 条粗切 shorts 二次
精切，片长一一等于成片窗口）＋25 个定格 clip（21 张 take 尾帧＋check-running/
color-bad-full/kf-list/nulltarget-warn-a 过程帧；check-good 全绿帧复用三处）。
录屏/定格作**顶层 clip**（StaticGuard），置 scenes 下层。终端素材 1600x920
缩左到 1120x644（left:54 top:226），右侧 620px 概念卡随六关/规则/修法
口播拍点轮替（STORYBOARD-FRAMEWORK.md 第 5 节定稿）；论述段用全屏概念卡。
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

# 靛蓝深＋金：与 hf-01/02/03/04 同一主题
THEME = replace(
    DARK_GOLD_GH,
    name="indigo-gold-hf",
    bg="#0d1b2a",
    subshade=("linear-gradient(transparent, rgba(13,27,42,.55) 40%, "
              "rgba(13,27,42,.94))"),
)

# ---- GitHub Dark 辅助色（右卡/规则卡与真机终端文案同色）----
PANEL, LINE = "#161b22", "#30363d"
INK, MUTE = "#e6edf3", "#8b949e"
BLUE, BLUE2 = "#1f6feb", "#58a6ff"
GREEN, GREEN2 = "#3fb950", "#7ee787"
RED, RED2 = "#f85149", "#ffa198"
AMBER, GOLD = "#d29922", "#e3b341"

# ---------- 17 幕（边界严格首尾相接；时间＝成片音频秒） ----------
SCENES = [

# S1 开场：承上＋眼睛看不出错＋守门员＋能力边界（全屏）0.00–56.10
Scene("sc-open", 0.00, 56.10, """
          <div class="op-ep" id="op-ep">HyperFrames 教程 · 第 5 集</div>
          <div class="op-title" id="op-title">别用眼睛看</div>
          <div class="op-sub" id="op-sub">HyperFrames check 门控实操</div>

          <div class="stage" id="s1-recap">
            <div class="st-h">上一集，我们让 div 动起来了</div>
            <div class="st-chips">
              <span class="st-chip">暂停的时间轴</span>
              <span class="st-chip">seek 到任意一秒</span>
              <span class="st-chip hot">帧帧可复现</span>
            </div>
          </div>

          <div class="stage" id="s1-q">
            <div class="st-q">一个项目，几百航 HTML、几十条动画</div>
            <div class="st-q-big">写完，怎么知道自己没写错？</div>
          </div>

          <div class="stage" id="s1-eye">
            <div class="st-eye">靠眼睛，从头看一遍？</div>
            <div class="st-eye-sub">我先给你看个东西 ——</div>
          </div>

          <div class="stage" id="s1-hidden">
            <div class="st-h">有个错，明晃晃写在标题的颜色值里</div>
            <div class="st-warn">盯着看了半天，没看出来</div>
          </div>

          <div class="stage" id="s1-checkword">
            <div class="st-h">今天的主角：官方守门员</div>
            <div class="st-check">check</div>
          </div>

          <div class="stage" id="s1-green">
            <div class="st-warnline">先把丑话说前头：它不是万能的</div>
            <div class="cmp">
              <div class="cmp-box bad" id="s1g-box">
                <div class="cmp-h red">setInterval 计数器</div>
                <div class="cmp-l">check 一路<strong>绿灯</strong></div>
              </div>
            </div>
          </div>

          <div class="stage" id="s1-six">
            <div class="st-six-q">六个渲染器，同时问第二秒</div>
            <div class="st-six-a">回来好几个<strong>不同的数</strong></div>
            <div class="st-six-note">动画能不能被定位 —— 这种运行时逻辑，守门员不管</div>
          </div>

          <div class="stage" id="s1-scope">
            <div class="st-scope-h">它管的是另一大类错 —— 光是这一类，就够救你好几回</div>
            <div class="st-chips" id="s1-scope-chips">
              <span class="st-chip">结构写错没</span>
              <span class="st-chip">控制台炸没炸</span>
              <span class="st-chip">布局遮没遮</span>
              <span class="st-chip hot">字看不看得清</span>
            </div>
          </div>"""),

# S2 工程首跑：命令＋六关递进（终端缩左＋右关卡）56.10–112.36
Scene("sc-sixgates", 56.10, 112.36, """
          <div class="kicker" id="g2-k">工程就一个标题、一个副标题，十秒 —— 终端里敲</div>
          <div class="gk">
            <div class="gk-card" id="g2-card">
              <div class="gk-tag">check · 六道关，一段段过</div>
              <div class="gate" id="gate-1"><span class="gate-n">1</span><b>Lint</b><span class="gate-d">不起浏览器，纯读文件</span></div>
              <div class="gate" id="gate-2"><span class="gate-n">2</span><b>Runtime</b><span class="gate-d">无头 Chrome 真跑</span></div>
              <div class="gate" id="gate-3"><span class="gate-n">3</span><b>Layout</b><span class="gate-d">9 个采样点测布局</span></div>
              <div class="gate" id="gate-4"><span class="gate-n">4</span><b>Motion</b><span class="gate-d">查动画写法</span></div>
              <div class="gate" id="gate-5"><span class="gate-n">5</span><b>Contrast</b><span class="gate-d">逐点测对比度</span></div>
              <div class="gate" id="gate-6"><span class="gate-n">6</span><b>Snapshots</b><span class="gate-d">没配就是 disabled</span></div>
              <div class="gk-pass" id="g2-pass">◇ Check passed · 全绿</div>
            </div>
          </div>"""),

# S3 喂错一：删 data-duration（终端＋规则卡轮替）112.36–151.60
Scene("sc-missing", 112.36, 151.60, """
          <div class="kicker" id="g3-k">开始给它喂错 · 第一个</div>
          <div class="gk">
            <div class="gk-card" id="g3-steps">
              <div class="gk-tag">实验 ①</div>
              <div class="steprow"><span class="step-n">1</span>删掉 #title 身上的 <span class="mono gold">data-duration</span></div>
              <div class="steprow"><span class="step-n">2</span>存盘</div>
              <div class="steprow"><span class="step-n">3</span>再 check</div>
            </div>
            <div class="gk-card rule warn" id="g3-rule">
              <div class="rule-head"><span class="rule-mark warn">⚠</span><b>warning</b><span class="rule-exit">exit 0</span></div>
              <div class="rule-name">timeline_element_missing_timing</div>
              <div class="rule-cn">元素在时间轴上，却没有时长 —— 时间轴画不出它在哪儿结束</div>
              <div class="rule-but">可你抬头看：<span class="pass-text">◇ Check passed，绿灯</span></div>
            </div>
            <div class="gk-card rule warn" id="g3-conseq">
              <div class="rule-head"><span class="rule-mark warn">⚠</span><b>只警告，不拦你</b><span class="rule-exit">exit 0</span></div>
              <div class="conseq-h">但后果是真的，黄字写明了：</div>
              <div class="conseq-line">预览 · 海报帧 · 最终渲染</div>
              <div class="conseq-line hot">这个元素都可能被切掉</div>
              <div class="rule-foot">黄字不是凑数的，是给人读的</div>
            </div>
          </div>"""),

# S4 喂错二：彩蛋越界＋root 13 复绿（终端＋时间轴/规则卡）151.60–181.26
Scene("sc-overflow", 151.60, 181.26, """
          <div class="kicker" id="g4-k">再来一个：片尾加个彩蛋</div>
          <div class="gk">
            <div class="gk-card" id="g4-tlcard">
              <div class="gk-tag">彩蛋第八秒进来，停五秒 —— 片子总长只有十秒</div>
              <div class="c4-axis">
                <div class="c4-main"></div>
                <div class="c4-tail"></div>
                <div class="c4-endline"></div>
                <span class="c4-lab-main">0s</span>
                <span class="c4-lab-end">根时长 10s</span>
                <span class="c4-lab-tail">走到 13s ✗</span>
              </div>
            </div>
            <div class="gk-card rule warn" id="g4-rule">
              <div class="rule-head"><span class="rule-mark warn">⚠</span><b>warning</b><span class="rule-exit">exit 0</span></div>
              <div class="rule-name">clip_ends_past_root_duration</div>
              <div class="fix-h">它直接递上两条修法：</div>
              <div class="fixrow"><span class="fix-n">①</span>把根时长延到 13 秒</div>
              <div class="fixrow"><span class="fix-n">②</span>让彩蛋在第 10 秒前结束</div>
            </div>
            <div class="gk-card rule pass" id="g4-law">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>选①：root 改成 13</b><span class="rule-exit pass-text">绿了</span></div>
              <div class="lawrow"><span class="law-w">页面成立、但有后果 → 警告</span></div>
              <div class="lawrow"><span class="law-r">页面不成立 → 错误</span></div>
            </div>
          </div>"""),

# S5 论述：警告 vs 错误＋退出码＋CI（全屏）181.26–202.28
Scene("sc-warnrule", 181.26, 202.28, """
          <div class="kicker" id="g5-k">两条黄字看明白，规律就出来了</div>
          <div class="cmp" id="g5-cmp">
            <div class="cmp-box" id="g5-warn">
              <div class="cmp-h amber-h">⚠ 警告 warning</div>
              <div class="cmp-l">页面<strong>还成立</strong>、能渲染</div>
              <div class="cmp-l dim">但有后果</div>
              <div class="cmp-badge warn-b">退出码 0</div>
            </div>
            <div class="cmp-box bad" id="g5-err">
              <div class="cmp-h red">✗ 错误 error</div>
              <div class="cmp-l">页面<strong>不成立</strong></div>
              <div class="cmp-l dim">真拦你</div>
              <div class="cmp-badge err-b">退出码 1</div>
            </div>
          </div>
          <div class="ci-card" id="g5-ci">
            <span class="mono gold ci-code">exit 0 才放行</span>
            <span class="ci-txt">这道闸，能直接挂进 CI —— 黄字留给人逐条读</span>
          </div>
          <div class="goldword" id="g5-word">绿灯，从来不是免死金牌</div>"""),

# S6 对比度主线（终端＋红/绿规则卡）202.28–253.56
Scene("sc-contrast", 202.28, 253.56, """
          <div class="kicker" id="g6-k">这个错，是让我决定拍这集的原因</div>
          <div class="gk">
            <div class="gk-card" id="g6-code">
              <div class="gk-tag">编辑器里，没觉得有大问题</div>
              <div class="codeblock">
                <div class="cb-line">#title {</div>
                <div class="cb-line">&nbsp;&nbsp;color: <span class="cb-hex">#1a1f26</span>;</div>
                <div class="cb-line">}</div>
              </div>
            </div>
            <div class="gk-card rule err" id="g6-bad">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>Contrast · error</b><span class="rule-exit">exit 1</span></div>
              <div class="ratio-row"><span class="ratio-bad">1.14:1</span><span class="ratio-need">大字门槛 3:1</span></div>
              <div class="samples">#title 四个采样点全红 · t=0.722 / 3.611 / 6.5 / 9.389s</div>
              <div class="tryfix">它还递上修好的颜色：<span class="mono gold">rgb(93,97,102)</span></div>
            </div>
            <div class="gk-card rule pass bigpass" id="g6-good">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>抄上，复跑</b></div>
              <div class="pass-ten">10 / 10</div>
              <div class="pass-ten-note">十个检查点，十分之十，全过 · WCAG AA</div>
            </div>
          </div>"""),

# S7 论述：六道关为什么分三层（全屏）253.56–286.02
Scene("sc-layers", 253.56, 286.02, """
          <div class="kicker" id="g7-k">那问题来了：这种错，第一关 Lint 为什么抓不着？</div>
          <div class="reason-card" id="g7-reason">
            「这个字在画面上到底清不清楚」，<strong>读文本是算不出来的</strong><br>
            <span class="reason-sub">颜色叠上底色 · 透明度 · 动画走到一半的中间态</span>
          </div>
          <div class="layerflow" id="g7-flow">
            <div class="lstep" id="ls-1">
              <div class="ls-tag">① 静态</div>
              <div class="ls-h">读文件能查的</div>
              <div class="ls-go">归 <b>Lint</b></div>
            </div>
            <div class="lstep" id="ls-2">
              <div class="ls-tag">② 真跑</div>
              <div class="ls-h">跑起来才暴露的</div>
              <div class="ls-go">归 <b>Runtime</b></div>
            </div>
            <div class="lstep hot" id="ls-3">
              <div class="ls-tag">③ 渲染后</div>
              <div class="ls-h">量像素才知道的遮挡与对比</div>
              <div class="ls-go">归 <b>Layout · Contrast</b></div>
            </div>
          </div>
          <div class="layer-note" id="g7-note">人眼会累、会脑补；机器的采样点，一个不落</div>"""),

# S8 成见引入：两 div 同轨重叠（全屏示意）286.02–296.00
Scene("sc-trackintro", 286.02, 296.00, """
          <div class="kicker" id="g8-k">下一个实验，考的是成见</div>
          <div class="ti-h" id="g8-h">两个片段，<span class="mono gold">data-track-index</span> 都写 1，时间还重叠</div>
          <div class="ti-trackbox" id="g8-box">
            <div class="ti-row">
              <span class="ti-rail">轨 1</span>
              <div class="ti-bar titlebar" id="ti-title">#title</div>
              <div class="ti-bar subbar" id="ti-sub">#sub</div>
            </div>
            <div class="ti-row">
              <span class="ti-rail dim">轨 2</span>
            </div>
          </div>
          <div class="ti-q" id="g8-q">标题跟副标题，在同一根轨上叠着 —— 同轨撞车，该报错了吧？</div>"""),

# S9 同轨全绿＋DOM 对调＋遮挡红（终端＋右卡三段）296.00–357.80
Scene("sc-track", 296.00, 357.80, """
          <div class="kicker" id="g9-k">check ——</div>
          <div class="gk">
            <div class="gk-card rule pass" id="g9-a1">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>全绿</b></div>
              <div class="g9-line">渲染器眼里，压根没有「轨」这个东西</div>
              <div class="g9-line dim">同轨叠着？不报错</div>
            </div>
            <div class="gk-card" id="g9-a2">
              <div class="gk-tag">track-index 是什么</div>
              <div class="g9-line">只是给官方 Studio 画轨道用的<strong>元数据</strong></div>
              <div class="g9-line">真正决定谁盖谁的：<span class="mono gold">DOM 顺序</span></div>
            </div>
            <div class="gk-card rule pass" id="g9-b">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>把两个 div 前后对调</b></div>
              <div class="g9-line">别的什么都不动 —— 照样全绿</div>
              <div class="g9-line dim">顺序怎么排，是你的设计；它只在后果闯祸时才出手</div>
            </div>
            <div class="gk-card rule err" id="g9-c">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>Layout · error</b><span class="rule-exit">exit 1</span></div>
              <div class="rule-name">text_occluded</div>
              <div class="rule-cn">文字藏在不透明元素底下</div>
              <div class="samples">9 个采样点，0.56s–9.44s，一个不落全抓到</div>
              <div class="rule-foot">它查的从来是画面上的结果，不是你起的名字</div>
            </div>
          </div>"""),

# S10 #sut 三警告静默失踪（终端＋右卡三段）357.80–391.90
Scene("sc-sut", 357.80, 391.90, """
          <div class="kicker" id="g10-k">最后一种错，最阴</div>
          <div class="gk">
            <div class="gk-card" id="g10-code">
              <div class="gk-tag">给副标题补个淡入，选择器一顺手 —— 就这一行</div>
              <div class="codeblock">
                <div class="cb-line dim">tl.fromTo('#sub', {opacity:0},</div>
                <div class="cb-line dim">&nbsp;&nbsp;{opacity:1, duration:1});</div>
                <div class="cb-line bad">tl.fromTo('<span class="cb-bad">#sut</span>', {opacity:0},</div>
                <div class="cb-line bad">&nbsp;&nbsp;{opacity:1, duration:1});</div>
              </div>
            </div>
            <div class="gk-card rule warn" id="g10-warn3">
              <div class="rule-head"><span class="rule-mark warn">⚠</span><b>Runtime · 3 warnings</b><span class="rule-exit pass-text">passed</span></div>
              <div class="w3row" id="w3-1"><span class="w3-mark warn">⚠</span><span class="mono">GSAP target #sut not found</span><span class="w3-t">t=0s</span></div>
              <div class="w3row" id="w3-2"><span class="w3-mark warn">⚠</span><span class="mono">GSAP target "" not found</span><span class="w3-t">t=0s</span></div>
              <div class="w3row" id="w3-3"><span class="w3-mark warn">⚠</span><span class="mono">GSAP target "" not found</span><span class="w3-t">t=1.667s</span></div>
              <div class="w3-note">同一处拼错：起步记两回，走到 1.667 秒，又记一回</div>
            </div>
            <div class="gk-card silent" id="g10-silent">
              <div class="silent-h">副标题的动画，就这么静悄悄地没了</div>
              <div class="silent-chips">
                <span class="si-chip">不报错</span>
                <span class="si-chip">不崩</span>
                <span class="si-chip hot">不提醒你第二遍</span>
              </div>
            </div>
          </div>"""),

# S11 论述：绿灯≠没事＋page_error 连坐（全屏）391.90–412.78
Scene("sc-greenrule", 391.90, 412.78, """
          <div class="kicker" id="g11-k">所以记住这个画面</div>
          <div class="goldword big" id="g11-word">绿灯不代表没事，黄字得逐条读完</div>
          <div class="cmp" id="g11-cmp">
            <div class="cmp-box bad wide" id="g11-pe">
              <div class="cmp-h red">✗ 真调了个不存在的函数</div>
              <div class="cmp-l">控制台直接 <span class="mono gold">page_error</span>，红的</div>
            </div>
          </div>
          <div class="chain-card" id="g11-chain">
            <div class="chain-h">后面的关卡连坐 —— 时间轴压根没跑起来</div>
            <div class="chain-q">这一趟所有的绿，都不可信</div>
          </div>"""),

# S12 体检三命令（终端＋右卡三段）412.78–485.20
Scene("sc-checkup", 412.78, 485.20, """
          <div class="kicker" id="g12-k">check 之外，还有三个体检命令，快速过一遍</div>
          <div class="gk">
            <div class="gk-card" id="g12-kf">
              <div class="gk-tag"><span class="mono gold">keyframes</span> · 把全片动画一条条列出来</div>
              <div class="cu-line">哪个文件 · 哪个元素 · 什么写法 · 第几秒到第几秒</div>
              <div class="cu-line hot">#title visual fromTo/flat @0s&gt;1s，0%→100% opacity</div>
              <div class="cu-shot">加 <span class="mono gold">--shot</span>：真渲染一张洋葱皮图，首帧尾帧叠一块，一眼破案</div>
            </div>
            <div class="gk-card rule warn" id="g12-insp">
              <div class="rule-head"><span class="rule-mark warn">⚠</span><b class="mono">inspect</b><span class="rule-exit">deprecated</span></div>
              <div class="cu-line">还能跑，但终端第一句就劝退：</div>
              <div class="cu-line bad">这命令已经废弃，将来要删 —— 请改用 check</div>
              <div class="cu-line dim">底下照样把布局查一遍：9 采样点，0 问题</div>
            </div>
            <div class="gk-card" id="g12-beats">
              <div class="gk-tag"><span class="mono gold">beats</span> · 给音乐轨数拍子用的</div>
              <div class="cu-line">这片没音乐 → 一行红字：没找到音乐轨</div>
              <div class="cu-line dim">给 &lt;audio&gt; 加 data-timeline-role="music"，或 id 起成 music/bgm/soundtrack</div>
              <div class="cu-note">注意：这行红是它<strong>没活干</strong>，不是片子判了错</div>
            </div>
          </div>"""),

# S13 echo 退出码（终端＋0 卡）485.20–499.90
Scene("sc-echo", 485.20, 499.90, """
          <div class="kicker" id="g13-k">收尾：看过了绿，也看过了红，亲手验证退出码</div>
          <div class="gk">
            <div class="gk-card" id="g13-how">
              <div class="gk-tag">全绿之后，在 cmd 里另起一行</div>
              <div class="codeblock">
                <div class="cb-line">echo <span class="cb-hex">%ERRORLEVEL%</span></div>
              </div>
            </div>
            <div class="gk-card zero-card" id="g13-zero">
              <div class="zero-big">0</div>
              <div class="zero-note">这就是 CI 能认的那个零</div>
            </div>
          </div>"""),

# S14 论述：机器判什么，什么是你的事（全屏）499.90–511.34
Scene("sc-scope", 499.90, 511.34, """
          <div class="kicker" id="g14-k">check 把机器能判的，都替你判了</div>
          <div class="cmp" id="g14-cmp">
            <div class="cmp-box ok" id="g14-machine">
              <div class="cmp-h green-h">机器判</div>
              <div class="cmp-l">结构 · 报错</div>
              <div class="cmp-l">遮挡</div>
              <div class="cmp-l">对比度</div>
            </div>
            <div class="cmp-box" id="g14-yours">
              <div class="cmp-h gold-h">那是你的事</div>
              <div class="cmp-l">片子好不好看</div>
              <div class="cmp-l">节奏对不对</div>
              <div class="cmp-l">包袱响不响</div>
            </div>
          </div>
          <div class="layer-note" id="g14-note">它一句不掺和</div>"""),

# S15 行动三件＋金句（全屏）511.34–536.24
Scene("sc-action", 511.34, 536.24, """
          <div class="kicker" id="g15-k">行动件给你备好了：回去打开你自己的工程，跑一遍 check，看三样</div>
          <div class="acl" id="g15-list">
            <div class="acl-row" id="ac-1"><span class="acl-n">①</span>
              <strong>红色的错误</strong>，照它递的修法改</div>
            <div class="acl-row" id="ac-2"><span class="acl-n">②</span>
              <strong>黄色的警告</strong>，逐条读完再决定放行</div>
            <div class="acl-row" id="ac-3"><span class="acl-n">③</span>
              退出码是 <span class="mono gold">0</span>，再去按渲染</div>
          </div>
          <div class="flow-chip" id="g15-flow">挂进出片流程：每次渲染前，过一道</div>
          <div class="goldword big" id="g15-word">别用眼睛看，让机器先看</div>
          <div class="word-sub" id="g15-sub">让错留在本地，别留到视频发出去以后</div>"""),

# S16 下集预告（全屏）536.24–550.20
Scene("sc-next", 536.24, 550.20, """
          <div class="kicker" id="g16-k">下一集</div>
          <div class="next-card" id="g16-card">给片子加声音、加画面素材</div>
          <div class="nx-then" id="g16-then">今天埋下的扣子，也该兑现了：</div>
          <div class="nx-errs" id="g16-errs">
            <span class="nx-chip">音频文件找不到</span>
            <span class="nx-chip">媒体 id 对不上</span>
          </div>
          <div class="nx-ep" id="g16-ep">这些在 Lint 关就是硬错误，根本别想走到渲染那一步</div>"""),

# S17 道别 550.20–TOTAL
Scene("sc-bye", 550.20, total, """
          <div class="bye" id="bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 顶层录屏/定格 clip（不可嵌套；放 scenes 之前＝下层） ----------
# 终端素材 1600x920 一律缩左 1120x644（left:54 top:226），右 620px 给概念卡。
# video 按二次精切实长（一一等于媒体时长）；img 定格随口播停留。
VIDEOS = """      <!-- S2 56.10–112.36：命令打字 → Checking 陪伴帧 → 全绿 -->
      <video id="rec2-type" class="clip term" data-start="61.00"
             data-duration="5.00" data-track-index="2"
             src="media/shorts/check-good-type.mp4" muted playsinline preload="auto"></video>
      <img id="img2-run" class="clip term" data-start="66.20"
           data-duration="43.50" src="media/freezes/check-running.png" alt="">
      <img id="img2-good" class="clip term" data-start="109.70"
           data-duration="2.66" src="media/freezes/check-good.png" alt="">

      <!-- S3 112.36–151.60：删 duration → 黄字 freeze 长停 -->
      <video id="rec3-edit" class="clip term" data-start="114.90"
             data-duration="2.80" data-track-index="2"
             src="media/shorts/dur-del-act.mp4" muted playsinline preload="auto"></video>
      <img id="img3-edit" class="clip term" data-start="117.70"
           data-duration="0.70" src="media/freezes/dur-del.png" alt="">
      <video id="rec3-run" class="clip term" data-start="118.40"
             data-duration="1.80" data-track-index="2"
             src="media/shorts/dur-run-type.mp4" muted playsinline preload="auto"></video>
      <img id="img3-run" class="clip term" data-start="120.20"
           data-duration="31.40" src="media/freezes/dur-run.png" alt="">

      <!-- S4 151.60–181.26：越界黄字双修法 → root 13 → 复绿 -->
      <video id="rec4-run" class="clip term" data-start="159.30"
             data-duration="1.90" data-track-index="2"
             src="media/shorts/overflow-type.mp4" muted playsinline preload="auto"></video>
      <img id="img4-run" class="clip term" data-start="161.20"
           data-duration="11.30" src="media/freezes/overflow-run.png" alt="">
      <video id="rec4-edit" class="clip term" data-start="172.50"
             data-duration="3.30" data-track-index="2"
             src="media/shorts/root-fix-act.mp4" muted playsinline preload="auto"></video>
      <img id="img4-edit" class="clip term" data-start="175.80"
           data-duration="0.40" src="media/freezes/root-fix-edit.png" alt="">
      <video id="rec4-run2" class="clip term" data-start="176.20"
             data-duration="1.40" data-track-index="2"
             src="media/shorts/root-fix-type.mp4" muted playsinline preload="auto"></video>
      <img id="img4-green" class="clip term" data-start="177.60"
           data-duration="3.66" src="media/freezes/root-fix-run.png" alt="">

      <!-- S6 202.28–253.56：#1a1f26 红四点 → rgb(93,97,102) 10/10 -->
      <img id="img6-idle" class="clip term" data-start="202.50"
           data-duration="5.70" src="media/freezes/check-good.png" alt="">
      <video id="rec6-badedit" class="clip term" data-start="208.20"
             data-duration="2.60" data-track-index="2"
             src="media/shorts/color-bad-act.mp4" muted playsinline preload="auto"></video>
      <img id="img6-badedit" class="clip term" data-start="210.80"
           data-duration="4.50" src="media/freezes/color-bad-edit.png" alt="">
      <video id="rec6-badrun" class="clip term" data-start="215.30"
             data-duration="1.60" data-track-index="2"
             src="media/shorts/color-bad-type.mp4" muted playsinline preload="auto"></video>
      <img id="img6-badrun" class="clip term" data-start="216.90"
           data-duration="29.60" src="media/freezes/color-bad-full.png" alt="">
      <video id="rec6-fixedit" class="clip term" data-start="246.50"
             data-duration="3.20" data-track-index="2"
             src="media/shorts/color-fix-act.mp4" muted playsinline preload="auto"></video>
      <img id="img6-fixedit" class="clip term" data-start="249.70"
           data-duration="0.30" src="media/freezes/color-fix-edit.png" alt="">
      <video id="rec6-fixrun" class="clip term" data-start="250.00"
             data-duration="1.40" data-track-index="2"
             src="media/shorts/color-fix-type.mp4" muted playsinline preload="auto"></video>
      <img id="img6-good" class="clip term" data-start="251.40"
           data-duration="2.16" src="media/freezes/color-fix-run.png" alt="">

      <!-- S9 296.00–357.80：同轨全绿 → 对调仍绿 → 贴块 text_occluded 红 -->
      <video id="rec9-run1" class="clip term" data-start="296.20"
             data-duration="4.20" data-track-index="2"
             src="media/shorts/same-track-type.mp4" muted playsinline preload="auto"></video>
      <img id="img9-green1" class="clip term" data-start="300.40"
           data-duration="16.50" src="media/freezes/same-track-run.png" alt="">
      <video id="rec9-swap" class="clip term" data-start="316.90"
             data-duration="3.60" data-track-index="2"
             src="media/shorts/dom-swap-act.mp4" muted playsinline preload="auto"></video>
      <img id="img9-swap" class="clip term" data-start="320.50"
           data-duration="1.40" src="media/freezes/dom-swap.png" alt="">
      <video id="rec9-run2" class="clip term" data-start="321.90"
             data-duration="1.80" data-track-index="2"
             src="media/shorts/dom-swap-type.mp4" muted playsinline preload="auto"></video>
      <img id="img9-green2" class="clip term" data-start="323.70"
           data-duration="8.90" src="media/freezes/dom-swap-run.png" alt="">
      <video id="rec9-block" class="clip term" data-start="332.60"
             data-duration="4.20" data-track-index="2"
             src="media/shorts/occlude-code-act.mp4" muted playsinline preload="auto"></video>
      <img id="img9-block" class="clip term" data-start="336.80"
           data-duration="0.50" src="media/freezes/occlude-code.png" alt="">
      <video id="rec9-run3" class="clip term" data-start="337.30"
             data-duration="1.60" data-track-index="2"
             src="media/shorts/occlude-type.mp4" muted playsinline preload="auto"></video>
      <img id="img9-red" class="clip term" data-start="338.90"
           data-duration="18.90" src="media/freezes/occlude-run.png" alt="">

      <!-- S10 357.80–391.90：#sut 一行 → 三警告 freeze 长停 -->
      <video id="rec10-code" class="clip term" data-start="359.50"
             data-duration="4.80" data-track-index="2"
             src="media/shorts/nulltarget-code-act.mp4" muted playsinline preload="auto"></video>
      <img id="img10-code" class="clip term" data-start="364.30"
           data-duration="3.30" src="media/freezes/nulltarget-code.png" alt="">
      <video id="rec10-run" class="clip term" data-start="367.60"
             data-duration="1.60" data-track-index="2"
             src="media/shorts/nulltarget-type.mp4" muted playsinline preload="auto"></video>
      <img id="img10-warn" class="clip term" data-start="369.20"
           data-duration="22.70" src="media/freezes/nulltarget-warn-a.png" alt="">

      <!-- S12 412.78–485.20：keyframes/--shot → inspect → beats -->
      <video id="rec12-kfcmd" class="clip term" data-start="415.00"
             data-duration="3.50" data-track-index="2"
             src="media/shorts/kf-cmd.mp4" muted playsinline preload="auto"></video>
      <video id="rec12-kfpop" class="clip term" data-start="418.50"
             data-duration="5.20" data-track-index="2"
             src="media/shorts/kf-list-pop.mp4" muted playsinline preload="auto"></video>
      <img id="img12-kflist" class="clip term" data-start="423.70"
           data-duration="13.70" src="media/freezes/kf-list.png" alt="">
      <video id="rec12-shot" class="clip term" data-start="437.40"
             data-duration="6.00" data-track-index="2"
             src="media/shorts/kf-shotcmd.mp4" muted playsinline preload="auto"></video>
      <img id="img12-shot" class="clip term" data-start="443.40"
           data-duration="4.00" src="media/freezes/kf.png" alt="">
      <video id="rec12-insp" class="clip term" data-start="447.40"
             data-duration="3.60" data-track-index="2"
             src="media/shorts/inspect-type.mp4" muted playsinline preload="auto"></video>
      <img id="img12-insp" class="clip term" data-start="451.00"
           data-duration="11.80" src="media/freezes/inspect-dep.png" alt="">
      <video id="rec12-beats" class="clip term" data-start="462.80"
             data-duration="3.60" data-track-index="2"
             src="media/shorts/beats-type.mp4" muted playsinline preload="auto"></video>
      <img id="img12-beats" class="clip term" data-start="466.40"
           data-duration="18.80" src="media/freezes/beats.png" alt="">

      <!-- S13 485.20–499.90：全绿 → echo %ERRORLEVEL% → 0 -->
      <img id="img13-idle" class="clip term" data-start="486.00"
           data-duration="7.50" src="media/freezes/check-good.png" alt="">
      <video id="rec13-echo" class="clip term" data-start="493.50"
             data-duration="2.30" data-track-index="2"
             src="media/shorts/echo-act.mp4" muted playsinline preload="auto"></video>
      <img id="img13-echo" class="clip term" data-start="495.80"
           data-duration="4.10" src="media/freezes/errlvl-zero.png" alt="">"""

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

      /* 终端录屏/定格：1600x920 缩左 1120x644，右 620px 让给概念卡 */
      #rec2-type, #img2-run, #img2-good,
      #rec3-edit, #img3-edit, #rec3-run, #img3-run,
      #rec4-run, #img4-run, #rec4-edit, #img4-edit, #rec4-run2, #img4-green,
      #img6-idle, #rec6-badedit, #img6-badedit, #rec6-badrun, #img6-badrun,
      #rec6-fixedit, #img6-fixedit, #rec6-fixrun, #img6-good,
      #rec9-run1, #img9-green1, #rec9-swap, #img9-swap, #rec9-run2, #img9-green2,
      #rec9-block, #img9-block, #rec9-run3, #img9-red,
      #rec10-code, #img10-code, #rec10-run, #img10-warn,
      #rec12-kfcmd, #rec12-kfpop, #img12-kflist, #rec12-shot, #img12-shot,
      #rec12-insp, #img12-insp, #rec12-beats, #img12-beats,
      #img13-idle, #rec13-echo, #img13-echo
        { position:absolute;
        left:54px; top:226px; width:1120px; height:644px; object-fit:fill;
        border-radius:10px; box-shadow:0 18px 60px rgba(0,0,0,.55); }

      /* 通用 */
      .kicker { position:absolute; left:0; right:0; top:40px; text-align:center;
        font-size:42px; color:#8b949e; }
      .mono { font-family:'Consolas','Courier New',monospace; color:#e6edf3; }
      .mono.gold { color:#e3b341; }

      /* ===== 右卡（终端幕）：gk 容器固定，gk-card 同位置轮替 ===== */
      .gk { position:absolute; left:1200px; top:128px; width:620px; height:800px; }
      .gk-card { position:absolute; left:0; top:0; width:620px; box-sizing:border-box;
        background:#161b22; border:2px solid #30363d; border-radius:18px;
        padding:32px 36px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      .gk-tag { font-size:34px; color:#58a6ff; line-height:1.5; margin-bottom:20px; }
      .gk-card.rule { padding-top:26px; }
      .rule-head { display:flex; align-items:center; font-size:34px; margin-bottom:18px; }
      .rule-head b { color:#e6edf3; font-weight:600; }
      .rule-mark { display:inline-flex; align-items:center; justify-content:center;
        width:52px; height:52px; border-radius:50%; font-size:34px; margin-right:14px; }
      .rule-mark.warn { background:rgba(210,153,34,.16); color:#d29922; }
      .rule-mark.err { background:rgba(248,81,73,.16); color:#f85149; }
      .rule-mark.pass { background:rgba(63,185,80,.16); color:#3fb950; }
      .rule-exit { margin-left:auto; font-size:28px; color:#8b949e; }
      .rule-exit.pass-text, .pass-text { color:#7ee787; }
      .gk-card.rule.warn { border-color:#5e4a1e; }
      .gk-card.rule.err { border-color:#6e2b2b; }
      .gk-card.rule.pass { border-color:#2b573f; }
      .rule-name { font-family:'Consolas','Courier New',monospace; font-size:30px;
        color:#e3b341; line-height:1.5; margin:6px 0 14px; }
      .rule-cn { font-size:34px; color:#c9d1d9; line-height:1.55; }
      .rule-but { margin-top:18px; font-size:34px; color:#c9d1d9; line-height:1.5; }
      .rule-foot { margin-top:16px; font-size:32px; color:#8b949e; line-height:1.5; }

      /* S2 六关 */
      .gate { display:flex; align-items:center; padding:15px 20px; margin-bottom:12px;
        background:#0d1521; border:2px solid #21262d; border-radius:12px;
        font-size:32px; color:#8b949e; }
      .gate b { font-size:34px; margin:0 16px 0 4px; color:#8b949e; font-weight:600; }
      .gate-n { display:inline-flex; align-items:center; justify-content:center;
        width:44px; height:44px; border-radius:50%; border:2px solid #30363d;
        font-size:26px; color:#8b949e; }
      .gate-d { margin-left:auto; text-align:right; font-size:28px; }
      /* 高亮态由 GSAP 直接补间属性（className:'+=on' 在当前 gsap 版本会
         把类名替换成单独的 on、丢掉 .gate 基础样式；属性补间 seek 也安全） */
      .gk-pass { margin-top:14px; font-size:40px; color:#3fb950; text-align:center; }

      /* S3 步骤/后果 */
      .steprow { display:flex; align-items:center; font-size:38px; color:#e6edf3;
        line-height:1.7; margin:10px 0; }
      .step-n, .fix-n { display:inline-flex; align-items:center; justify-content:center;
        width:48px; height:48px; border-radius:50%; background:#1f6feb; color:#fff;
        font-size:28px; margin-right:18px; flex:none; }
      .conseq-h { font-size:34px; color:#8b949e; margin:8px 0 14px; }
      .conseq-line { font-size:40px; color:#e6edf3; line-height:1.7; }
      .conseq-line.hot { color:#ffa198; }

      /* S4 时间轴示意 */
      .c4-axis { position:relative; height:210px; margin:18px 8px 0; }
      .c4-main { position:absolute; left:0; top:70px; width:318px; height:44px;
        background:rgba(63,185,80,.35); border:2px solid #3fb950; border-radius:8px; }
      .c4-tail { position:absolute; left:318px; top:70px; width:199px; height:44px;
        background:rgba(248,81,73,.28); border:2px dashed #f85149; border-radius:8px; }
      .c4-endline { position:absolute; left:398px; top:36px; height:112px;
        border-left:4px solid #e6edf3; }
      .c4-lab-main { position:absolute; left:0; top:128px; font-size:28px; color:#8b949e; }
      .c4-lab-end { position:absolute; left:330px; top:128px; font-size:28px; color:#e6edf3; }
      .c4-lab-tail { position:absolute; right:0; top:20px; font-size:30px; color:#ffa198; }
      .fix-h { font-size:34px; color:#8b949e; margin:6px 0 12px; }
      .fixrow { display:flex; align-items:center; font-size:34px; color:#e6edf3;
        line-height:1.6; margin:8px 0; }
      .lawrow { margin:10px 0; font-size:36px; line-height:1.5; }
      .law-w { color:#e3b341; } .law-r { color:#ffa198; }

      /* 代码块（右卡） */
      .codeblock { background:#0d1521; border:2px solid #30363d; border-radius:12px;
        padding:20px 24px; }
      .cb-line { font-family:'Consolas','Courier New',monospace; font-size:30px;
        color:#c9d1d9; line-height:1.7; white-space:nowrap; }
      .cb-line.dim { color:#8b949e; margin-top:10px; font-family:inherit; font-size:30px; }
      .cb-line.bad { color:#ffa198; }
      .cb-hex { color:#58a6ff; }
      .cb-bad { color:#ffa198; }

      /* S6 对比度 */
      .ratio-row { display:flex; align-items:baseline; margin:10px 0 6px; }
      .ratio-bad { font-size:88px; color:#f85149; font-weight:700; margin-right:24px; }
      .ratio-need { font-size:36px; color:#c9d1d9; }
      .samples { font-size:29px; color:#ffa198; line-height:1.5; margin:8px 0; }
      .tryfix { margin-top:14px; font-size:33px; color:#c9d1d9; line-height:1.5;
        border-top:2px solid #30363d; padding-top:14px; }
      .bigpass { text-align:center; }
      .pass-ten { font-size:120px; color:#3fb950; font-weight:700; line-height:1.1; }
      .pass-ten-note { font-size:34px; color:#c9d1d9; margin-top:8px; }

      /* S9 */
      .g9-line { font-size:35px; color:#e6edf3; line-height:1.6; margin:8px 0; }
      .g9-line.dim { color:#8b949e; font-size:31px; }

      /* S10 三警告 */
      .w3row { display:flex; align-items:center; background:#0d1521;
        border:2px solid #5e4a1e; border-radius:10px; padding:12px 16px; margin:10px 0; }
      .w3-mark { font-size:28px; margin-right:12px; }
      .w3-mark.warn { color:#d29922; }
      .w3row .mono { font-size:25px; flex:1; color:#e6edf3; }
      .w3-t { font-size:28px; color:#8b949e; margin-left:10px; }
      .w3-note { margin-top:12px; font-size:30px; color:#8b949e; line-height:1.5; }
      .silent-h { font-size:44px; color:#ffa198; line-height:1.5; margin-bottom:24px; }
      .silent-chips { text-align:center; }
      .si-chip { display:inline-block; margin:8px 10px; padding:16px 30px; font-size:36px;
        color:#e6edf3; background:#0d1521; border:2px solid #30363d; border-radius:999px; }
      .si-chip.hot { border-color:#6e2b2b; color:#ffa198; }

      /* S12 体检卡 */
      .cu-line { font-size:33px; color:#e6edf3; line-height:1.6; margin:10px 0; }
      .cu-line.dim { color:#8b949e; font-size:30px; }
      .cu-line.bad { color:#ffa198; }
      .cu-line.hot { color:#7ee787; font-size:31px; }
      .cu-shot { margin-top:14px; padding-top:14px; border-top:2px solid #30363d;
        font-size:33px; color:#c9d1d9; line-height:1.5; }
      .cu-note { margin-top:14px; font-size:32px; color:#e3b341; line-height:1.5; }

      /* S13 零 */
      .zero-card { text-align:center; padding-top:48px; }
      .zero-big { font-size:220px; color:#3fb950; font-weight:700; line-height:1.05; }
      .zero-note { font-size:38px; color:#c9d1d9; margin-top:10px; }

      /* ===== 全屏概念幕 ===== */
      /* S1 开场 */
      .op-ep { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:48px; color:#8b949e; letter-spacing:.3em; }
      .op-title { position:absolute; left:0; right:0; top:382px; text-align:center;
        font-size:140px; color:#e3b341; letter-spacing:.14em; }
      .op-sub { position:absolute; left:0; right:0; top:560px; text-align:center;
        font-size:46px; color:#58a6ff; letter-spacing:.18em; }
      .stage { position:absolute; left:140px; right:140px; top:250px; text-align:center; }
      .st-h { font-size:52px; color:#c9d1d9; line-height:1.6; }
      .st-chips { margin-top:40px; }
      .st-chip { display:inline-block; margin:10px 16px; padding:22px 42px; font-size:44px;
        color:#c9d1d9; background:#161b22; border:2px solid #2b3c57; border-radius:999px; }
      .st-chip.hot { border-color:#e3b341; color:#e3b341; }
      .st-q { font-size:46px; color:#8b949e; }
      .st-q-big { font-size:72px; color:#e6edf3; margin-top:34px; line-height:1.4; }
      .st-eye { font-size:80px; color:#e6edf3; }
      .st-eye-sub { font-size:46px; color:#e3b341; margin-top:36px; }
      .st-warn { font-size:54px; color:#ffa198; margin-top:24px; }
      .st-check { font-family:'Consolas','Courier New',monospace; font-size:170px;
        color:#7ee787; margin-top:30px; letter-spacing:.04em; }
      .st-warnline { font-size:48px; color:#e3b341; margin-bottom:40px; }
      .st-six-q { font-size:50px; color:#8b949e; }
      .st-six-a { font-size:76px; color:#ffa198; margin:24px 0; }
      .st-six-a strong { color:#f85149; }
      .st-six-note { font-size:42px; color:#c9d1d9; margin-top:20px; }
      .st-scope-h { font-size:52px; color:#e6edf3; line-height:1.6; margin-bottom:20px; }

      /* 通用双盒 */
      .cmp { position:absolute; left:0; right:0; text-align:center; }
      .cmp-box { display:inline-block; width:580px; padding:38px 46px; margin:0 26px;
        background:#161b22; border:2px solid #2b3c57;
        box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 10px 30px rgba(0,0,0,.38);
        border-radius:20px; vertical-align:top; }
      .cmp-box.wide { width:760px; }
      .cmp-box.hot { border-color:#1f6feb; }
      .cmp-box.bad { border-color:#6e3b3b; }
      .cmp-box.ok { border-color:#2b573f; }
      .cmp-h { font-size:48px; margin-bottom:22px; }
      .cmp-h.mute { color:#8b949e; } .cmp-h.blue { color:#58a6ff; }
      .cmp-h.red { color:#ffa198; } .cmp-h.amber-h { color:#e3b341; }
      .cmp-h.green-h { color:#7ee787; } .cmp-h.gold-h { color:#e3b341; }
      .cmp-l { font-size:42px; color:#e6edf3; line-height:1.75; }
      .cmp-l.dim { color:#8b949e; font-size:36px; margin-top:8px; }
      .cmp-badge { display:inline-block; margin-top:22px; padding:12px 34px;
        border-radius:999px; font-size:38px; }
      .warn-b { color:#e3b341; background:rgba(210,153,34,.12); border:2px solid #5e4a1e; }
      .err-b { color:#ffa198; background:rgba(248,81,73,.12); border:2px solid #6e2b2b; }

      /* S5 */
      #g5-cmp { top:180px; }
      .ci-card { position:absolute; left:300px; right:300px; top:600px; text-align:center;
        background:#0d1521; border:2px solid #30363d; border-radius:18px; padding:28px 44px; }
      .ci-code { display:block; font-size:60px; margin-bottom:10px; }
      .ci-txt { font-size:40px; color:#c9d1d9; }
      .goldword { position:absolute; left:0; right:0; text-align:center;
        font-size:64px; color:#e3b341; letter-spacing:.04em; }
      .goldword.big { font-size:72px; }
      #g5-word { top:800px; }

      /* S7 三层 */
      .reason-card { position:absolute; left:200px; right:200px; top:170px; text-align:center;
        font-size:52px; color:#e6edf3; line-height:1.7;
        background:#161b22; border:2px solid #2b3c57; border-radius:18px; padding:34px 44px; }
      .reason-sub { font-size:40px; color:#8b949e; }
      .layerflow { position:absolute; left:0; right:0; top:470px; text-align:center; }
      .lstep { display:inline-block; width:460px; padding:36px 26px; margin:0 16px;
        background:#161b22; border:2px solid #2b3c57; border-radius:18px; vertical-align:top; }
      .lstep.hot { border-color:#1f6feb; box-shadow:0 0 40px rgba(31,111,235,.2); }
      .ls-tag { font-size:34px; color:#8b949e; }
      .ls-h { font-size:42px; color:#e6edf3; line-height:1.5; margin:14px 0; }
      .ls-go { font-size:44px; color:#58a6ff; }
      .layer-note { position:absolute; left:0; right:0; bottom:150px; text-align:center;
        font-size:48px; color:#e3b341; }

      /* S8 同轨示意 */
      .ti-h { position:absolute; left:120px; right:120px; top:180px; text-align:center;
        font-size:52px; color:#e6edf3; line-height:1.6; }
      .ti-trackbox { position:absolute; left:300px; right:300px; top:400px; }
      .ti-row { position:relative; height:180px; border-bottom:2px solid #30363d; }
      .ti-rail { position:absolute; left:0; top:50px; font-size:40px; color:#c9d1d9;
        width:150px; }
      .ti-rail.dim { color:#3a4453; }
      .ti-bar { position:absolute; height:64px; border-radius:10px; font-size:36px;
        color:#fff; text-align:center; line-height:64px; }
      .ti-bar.titlebar { left:180px; top:20px; width:560px;
        background:rgba(31,111,235,.55); border:2px solid #58a6ff; }
      .ti-bar.subbar { left:420px; top:96px; width:560px;
        background:rgba(227,179,65,.5); border:2px dashed #e3b341; }
      .ti-q { position:absolute; left:120px; right:120px; bottom:170px; text-align:center;
        font-size:50px; color:#e3b341; line-height:1.6; }

      /* S11 连坐 */
      #g11-word { top:170px; }
      #g11-cmp { top:330px; }
      .chain-card { position:absolute; left:300px; right:300px; top:660px; text-align:center;
        background:rgba(248,81,73,.07); border:2px solid #6e2b2b; border-radius:18px;
        padding:30px 44px; }
      .chain-h { font-size:44px; color:#c9d1d9; }
      .chain-q { font-size:54px; color:#ffa198; margin-top:12px; }

      /* S14 */
      #g14-cmp { top:280px; }
      #g14-note { bottom:200px; }

      /* S15 行动件 */
      .acl { position:absolute; left:150px; right:150px; top:180px; }
      .acl-row { padding:28px 40px; margin-bottom:24px; background:#161b22;
        border:2px solid #2b3c57; border-left:10px solid #1f6feb; border-radius:14px;
        font-size:44px; color:#e6edf3; line-height:1.5; }
      .acl-n { color:#e3b341; font-size:52px; margin-right:20px; }
      .flow-chip { position:absolute; left:0; right:0; top:636px; text-align:center;
        font-size:44px; color:#58a6ff; }
      #g15-word { top:724px; }
      .word-sub { position:absolute; left:0; right:0; top:872px; text-align:center;
        font-size:40px; color:#c9d1d9; }

      /* S16 下集 */
      .next-card { position:absolute; left:160px; right:160px; top:240px; text-align:center;
        font-size:64px; color:#e6edf3; }
      .nx-then { position:absolute; left:0; right:0; top:420px; text-align:center;
        font-size:42px; color:#8b949e; }
      .nx-errs { position:absolute; left:0; right:0; top:530px; text-align:center; }
      .nx-chip { display:inline-block; margin:0 20px; padding:22px 44px; font-size:46px;
        color:#ffa198; background:rgba(248,81,73,.08); border:2px solid #6e2b2b;
        border-radius:999px; }
      .nx-ep { position:absolute; left:180px; right:180px; bottom:250px; text-align:center;
        font-size:44px; color:#e3b341; line-height:1.6; }

      /* S17 道别 */
      .bye { position:absolute; left:0; right:0; top:440px; text-align:center;
        font-size:72px; color:#e6edf3; letter-spacing:.08em; }
"""

# ---------- 场景时间轴（时间显式给秒；拍点锚 cues 实测词戳） ----------
SCENE_JS = """
      /* 六关递进：直接补间属性（seek 安全；当前 gsap 的 className += 会丢基础类） */
      function gateAt(sel, t) {
        tl.to(sel, {backgroundColor:'rgba(31,111,235,.16)', borderColor:'#1f6feb',
                    color:'#e6edf3', duration:.4}, t);
        tl.to(sel+' b, '+sel+' .gate-n', {color:'#58a6ff', borderColor:'#1f6feb',
                    duration:.4}, t);
        tl.to(sel+' .gate-d', {color:'#c9d1d9', duration:.4}, t);
      }

      /* S1 0–56.10：片名 → 承上 → 眼睛 → check → 边界与四类，stage 轮替 */
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#op-ep',{y:18,opacity:0,duration:.6},.2);
      tl.from('#op-title',{scale:.8,opacity:0,duration:.8,ease:'back.out(1.5)'},.5);
      tl.from('#op-sub',{opacity:0,duration:.6},1.0);
      tl.to(['#op-ep','#op-title','#op-sub'],{opacity:0,duration:.35},2.5);
      tl.from('#s1-recap',{y:22,opacity:0,duration:.7},2.9);
      tl.to('#s1-recap',{opacity:0,duration:.3},7.8);
      tl.from('#s1-q',{y:22,opacity:0,duration:.7},8.4);
      tl.to('#s1-q',{opacity:0,duration:.3},15.3);
      tl.from('#s1-eye',{scale:.92,opacity:0,duration:.7,ease:'back.out(1.3)'},15.9);
      tl.to('#s1-eye',{opacity:0,duration:.3},19.2);
      tl.from('#s1-hidden',{y:22,opacity:0,duration:.7},19.5);
      tl.to('#s1-hidden',{opacity:0,duration:.3},25.0);
      tl.from('#s1-checkword',{y:22,opacity:0,duration:.7},25.6);
      tl.to('#s1-checkword',{opacity:0,duration:.3},28.4);
      tl.from('#s1-green',{y:22,opacity:0,duration:.7},28.7);
      tl.from('#s1-green .st-warnline',{y:18,opacity:0,duration:.6},28.95);
      tl.from('#s1g-box',{scale:.92,opacity:0,duration:.7,ease:'back.out(1.3)'},31.9);
      tl.to('#s1-green',{opacity:0,duration:.3},38.0);
      tl.from('#s1-six',{y:22,opacity:0,duration:.7},38.7);
      tl.to('#s1-six',{opacity:0,duration:.3},43.2);
      tl.from('#s1-scope',{y:22,opacity:0,duration:.7},43.8);
      tl.from('#s1-scope-chips .st-chip',{y:16,opacity:0,duration:.5,stagger:.12},45.2);
      tl.to('#sc-open > .scene-inner',{opacity:0,duration:.4},55.70);

      /* S2 56.10–112.36：六关词戳 Lint 70.54/Runtime 78.31/Layout 84.76/
         Motion 90.40/Contrast 103.05/Snapshots 108.22/全绿 110.22/passed 111.0 */
      tl.fromTo('#sc-sixgates > .scene-inner',{opacity:0},{opacity:1,duration:.5},56.10);
      tl.from('#g2-k',{y:18,opacity:0,duration:.6},56.4);
      tl.from('#g2-card',{x:60,opacity:0,duration:.7,ease:'back.out(1.2)'},56.6);
      gateAt('#gate-1',71.0);
      gateAt('#gate-2',78.8);
      gateAt('#gate-3',85.2);
      gateAt('#gate-4',90.9);
      gateAt('#gate-5',103.4);
      gateAt('#gate-6',108.9);
      tl.from('#g2-pass',{scale:.8,opacity:0,duration:.6,ease:'back.out(1.4)'},110.3);
      tl.to('#sc-sixgates > .scene-inner',{opacity:0,duration:.4},111.96);

      /* S3 112.36–151.60：步骤 113.8 → 规则名 120.10 → 只警告 132.50/后果 144.02 */
      tl.fromTo('#sc-missing > .scene-inner',{opacity:0},{opacity:1,duration:.5},112.36);
      tl.from('#g3-k',{y:18,opacity:0,duration:.6},112.6);
      tl.from('#g3-steps',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},113.0);
      tl.to('#g3-steps',{opacity:0,duration:.3},119.9);
      tl.from('#g3-rule',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},120.3);
      tl.to('#g3-rule',{opacity:0,duration:.3},132.3);
      tl.from('#g3-conseq',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},132.7);
      tl.to('#sc-missing > .scene-inner',{opacity:0,duration:.4},151.20);

      /* S4 151.60–181.26：彩蛋 152.86 → check 159.96/规则 160.92 →
         修法 166.20 → root 改 174.48/绿 177.14 → 规律 178.00 */
      tl.fromTo('#sc-overflow > .scene-inner',{opacity:0},{opacity:1,duration:.5},151.60);
      tl.from('#g4-k',{y:18,opacity:0,duration:.6},151.9);
      tl.from('#g4-tlcard',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},152.0);
      tl.from('.c4-tail',{scaleX:0,transformOrigin:'left center',opacity:0,duration:.7},155.6);
      tl.to('#g4-tlcard',{opacity:0,duration:.3},159.6);
      tl.from('#g4-rule',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},160.5);
      tl.to('#g4-rule',{opacity:0,duration:.3},177.8);
      tl.from('#g4-law',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},178.2);
      tl.to('#sc-overflow > .scene-inner',{opacity:0,duration:.4},180.86);

      /* S5 181.26–202.28：定义 181.26/183.36 → CI 192.00 → 金句 200.18 */
      tl.fromTo('#sc-warnrule > .scene-inner',{opacity:0},{opacity:1,duration:.5},181.26);
      tl.from('#g5-k',{y:18,opacity:0,duration:.6},181.5);
      /* 双盒同拍点出现，避免单盒期在页面中线横向跳位 */
      tl.from('#g5-warn',{x:-50,opacity:0,duration:.7,ease:'back.out(1.3)'},181.8);
      tl.from('#g5-err',{x:50,opacity:0,duration:.7,ease:'back.out(1.3)'},181.8);
      tl.from('#g5-ci',{y:26,opacity:0,duration:.7},192.2);
      tl.to(['#g5-warn','#g5-err','#g5-ci'],{opacity:0,duration:.3},199.8);
      tl.from('#g5-word',{scale:.88,opacity:0,duration:.8,ease:'back.out(1.4)'},200.4);
      tl.to('#sc-warnrule > .scene-inner',{opacity:0,duration:.4},201.88);

      /* S6 202.28–253.56：色值 209.66 → 全红 217.24/1.14:1 218.73/3:1 221.34
         → Try rgb 244.58 → 10/10 250.62 */
      tl.fromTo('#sc-contrast > .scene-inner',{opacity:0},{opacity:1,duration:.5},202.28);
      tl.from('#g6-k',{y:18,opacity:0,duration:.6},202.6);
      tl.from('#g6-code',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},211.2);
      tl.to('#g6-code',{opacity:0,duration:.3},216.9);
      tl.from('#g6-bad',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},217.3);
      tl.to('#g6-bad',{opacity:0,duration:.3},250.4);
      tl.from('#g6-good',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},250.8);
      tl.to('#sc-contrast > .scene-inner',{opacity:0,duration:.4},253.16);

      /* S7 253.56–286.02：抓不着 254.50/算不出 259.80 → 三层 269.06 → 尾注 282.14 */
      tl.fromTo('#sc-layers > .scene-inner',{opacity:0},{opacity:1,duration:.5},253.56);
      tl.from('#g7-k',{y:18,opacity:0,duration:.6},253.8);
      tl.from('#g7-reason',{scale:.94,opacity:0,duration:.7,ease:'back.out(1.2)'},256.5);
      tl.to('#g7-reason',{opacity:0,duration:.3},268.6);
      tl.from('.layerflow .lstep',{y:30,opacity:0,duration:.6,stagger:.3},269.3);
      tl.from('#g7-note',{y:22,opacity:0,duration:.7},282.4);
      tl.to('#sc-layers > .scene-inner',{opacity:0,duration:.4},285.62);

      /* S8 286.02–296.00：成见 287.10/两片段 287.98/index 289.42/重叠 291.78 */
      tl.fromTo('#sc-trackintro > .scene-inner',{opacity:0},{opacity:1,duration:.5},286.02);
      tl.from('#g8-k',{y:18,opacity:0,duration:.6},286.3);
      tl.from('#g8-h',{y:22,opacity:0,duration:.7},288.2);
      tl.from('#ti-title',{x:-40,opacity:0,duration:.6,ease:'back.out(1.3)'},289.8);
      tl.from('#ti-sub',{x:-40,opacity:0,duration:.6,ease:'back.out(1.3)'},292.0);
      tl.from('#g8-q',{y:22,opacity:0,duration:.7},294.4);
      tl.to('#sc-trackintro > .scene-inner',{opacity:0,duration:.4},295.60);

      /* S9 296.00–357.80：全绿 300.42 → 元数据 305.32/DOM 311.38 →
         对调仍绿 322.62 → 贴块 332.92 → text_occluded 346.60/退出码 351.72 */
      tl.fromTo('#sc-track > .scene-inner',{opacity:0},{opacity:1,duration:.5},296.00);
      tl.from('#g9-k',{y:18,opacity:0,duration:.6},296.3);
      tl.from('#g9-a1',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},300.6);
      tl.to('#g9-a1',{opacity:0,duration:.3},311.2);
      tl.from('#g9-a2',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},311.6);
      tl.to('#g9-a2',{opacity:0,duration:.3},322.6);
      tl.from('#g9-b',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},323.0);
      tl.to('#g9-b',{opacity:0,duration:.3},340.2);
      tl.from('#g9-c',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},340.6);
      tl.to('#sc-track > .scene-inner',{opacity:0,duration:.4},357.40);

      /* S10 357.80–391.90：拼错 362.20/就这一行 367.14 → passed 368.12 →
         三警告 369.46/#sut 374.02/空名 377.28/1.667s 383.24 → 静默 387.24 */
      tl.fromTo('#sc-sut > .scene-inner',{opacity:0},{opacity:1,duration:.5},357.80);
      tl.from('#g10-k',{y:18,opacity:0,duration:.6},358.1);
      tl.from('#g10-code',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},359.2);
      tl.to('#g10-code',{opacity:0,duration:.3},369.1);
      tl.from('#g10-warn3',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},369.5);
      tl.from('#w3-1',{x:30,opacity:0,duration:.5},372.6);
      tl.from('#w3-2',{x:30,opacity:0,duration:.5},374.3);
      tl.from('#w3-3',{x:30,opacity:0,duration:.5},377.5);
      tl.to('#g10-warn3',{opacity:0,duration:.3},385.7);
      tl.from('#g10-silent',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},386.1);
      tl.to('#sc-sut > .scene-inner',{opacity:0,duration:.4},391.50);

      /* S11 391.90–412.78：金句 394.04 → page_error 401.98/红 403.74 →
         连坐 404.78/不可信 410.94 */
      tl.fromTo('#sc-greenrule > .scene-inner',{opacity:0},{opacity:1,duration:.5},391.90);
      tl.from('#g11-word',{scale:.9,opacity:0,duration:.8,ease:'back.out(1.4)'},392.2);
      tl.to('#g11-word',{opacity:0,duration:.3},399.2);
      tl.from('#g11-pe',{scale:.92,opacity:0,duration:.7,ease:'back.out(1.3)'},400.2);
      tl.from('#g11-chain',{y:26,opacity:0,duration:.7},405.0);
      tl.to('#sc-greenrule > .scene-inner',{opacity:0,duration:.4},412.38);

      /* S12 412.78–485.20：keyframes 416.12/标题条 425.56/--shot 437.04 →
         inspect 447.38/改用 check 453.50 → beats 462.60/没活干 477.96 */
      tl.fromTo('#sc-checkup > .scene-inner',{opacity:0},{opacity:1,duration:.5},412.78);
      tl.from('#g12-k',{y:18,opacity:0,duration:.6},413.1);
      tl.from('#g12-kf',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},414.5);
      tl.to('#g12-kf',{opacity:0,duration:.3},447.2);
      tl.from('#g12-insp',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},447.6);
      tl.to('#g12-insp',{opacity:0,duration:.3},462.6);
      tl.from('#g12-beats',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},463.0);
      tl.to('#sc-checkup > .scene-inner',{opacity:0,duration:.4},484.80);

      /* S13 485.20–499.90：另起一行 491.64/echo 493.90 → 回显零 497.72/CI 的零 497.90 */
      tl.fromTo('#sc-echo > .scene-inner',{opacity:0},{opacity:1,duration:.5},485.20);
      tl.from('#g13-k',{y:18,opacity:0,duration:.6},485.5);
      tl.from('#g13-how',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},486.0);
      tl.to('#g13-how',{opacity:0,duration:.3},497.5);
      tl.from('#g13-zero',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},497.9);
      tl.to('#sc-echo > .scene-inner',{opacity:0,duration:.4},499.50);

      /* S14 499.90–511.34：机器判 502.60/你的事 508.94 */
      tl.fromTo('#sc-scope > .scene-inner',{opacity:0},{opacity:1,duration:.5},499.90);
      tl.from('#g14-k',{y:18,opacity:0,duration:.6},500.2);
      tl.from('#g14-machine',{x:-50,opacity:0,duration:.7,ease:'back.out(1.3)'},502.8);
      tl.from('#g14-yours',{x:50,opacity:0,duration:.7,ease:'back.out(1.3)'},502.8);
      tl.from('#g14-note',{y:20,opacity:0,duration:.6},509.2);
      tl.to('#sc-scope > .scene-inner',{opacity:0,duration:.4},510.94);

      /* S15 511.34–536.24：三样 517.44/518.50/524.76 → 流程 526.00 → 金句 528.20 */
      tl.fromTo('#sc-action > .scene-inner',{opacity:0},{opacity:1,duration:.5},511.34);
      tl.from('#g15-k',{y:18,opacity:0,duration:.6},511.6);
      tl.from('.acl .acl-row',{x:-40,opacity:0,duration:.6,stagger:3.6},517.4);
      tl.from('#g15-flow',{y:20,opacity:0,duration:.6},526.3);
      tl.from('#g15-word',{scale:.9,opacity:0,duration:.8,ease:'back.out(1.4)'},528.5);
      tl.from('#g15-sub',{opacity:0,duration:.6},531.8);
      tl.to('#sc-action > .scene-inner',{opacity:0,duration:.4},535.84);

      /* S16 536.24–550.20：下集 536.24/加声音素材 537.14 → 硬错误 542.62/545.60 */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},536.24);
      tl.from('#g16-k',{y:18,opacity:0,duration:.6},536.5);
      tl.from('#g16-card',{y:24,opacity:0,duration:.7},537.4);
      tl.from('#g16-then',{opacity:0,duration:.6},540.4);
      tl.from('.nx-errs .nx-chip',{y:20,opacity:0,duration:.5,stagger:.25},542.9);
      tl.from('#g16-ep',{y:20,opacity:0,duration:.7},546.2);
      tl.to('#sc-next > .scene-inner',{opacity:0,duration:.4},549.80);

      /* S17 550.20–TOTAL */
      tl.fromTo('#sc-bye > .scene-inner',{opacity:0},{opacity:1,duration:.5},550.20);
      tl.from('#bye',{y:24,opacity:0,duration:.7},550.5);
"""

# ---------- 底部字幕轨道 ----------
# time_offset：faster-whisper 吞句间停顿致字幕整体偏早；hf-01 0.28、
# hf-02 0.37、hf-03 0.29、hf-04 0.30。hf-05 经 oneoffs/measure_offset.py
# 实测 onset 配对中位数 +293.1ms（43/66），取 0.29。
frag = char_track(cues, chars, THEME.accent, time_offset=0.29)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/hf-05-yeyang.wav", total),
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
print("已生成 index.html（%.2f 秒，%d 幕，%d 句，23 段录屏＋25 个定格 clip）"
      % (total, len(SCENES), len(cues)))
