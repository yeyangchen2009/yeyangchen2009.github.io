# -*- coding: utf-8 -*-
"""HyperFrames 教程第 7 集《把每一帧看清楚：snapshot 与 seek 管得住的动画》。

GitHub Dark 蓝主色（事实集，区别于 hf-06 声音集的金），559.22s，20 幕。
教学核心＝烤片之前把每一帧看清楚：同一工程同一秒连拍四张，蓝块（GSAP）
纹丝不动、合法 CSS 绿点（WAAPI 在册）钉死相位，红块（setInterval 闭包
自掐表的黑户）四个位置——preview 无痕、check 零 error 也会骗眼睛；
两种动画过两种时间（墙钟 vs 时间轴），慢表边界实验补刀；老契约
timeline paused＋登记 window.__timelines＋seek 要哪帧给哪帧；snapshot
at/frames/接触表、zoom 选择器/像素区（写错硬报错）、拍哪些秒
（接缝/半途/心虚句，只清自己命名的帧）；keyframes 无参体检报告
（GSAP/CSS keyframes/Anime 逐户登记，三个 items）与 --shot 洋葱皮
（#bad 黑户硬报错 nothing animates、读系统时间/requestAnimationFrame
会被 check 立刻拦下、闭包自己记数偏漏网）；compare 多方案对照
（标签逗号小脾气）；grade-compare 选片（CSS filter 串＝inactive/no-op
白烤一遍，真机警告入镜，正确档 adjust 对象）＋present 演讲模式。

素材：9 take 录屏（oneoffs/record_segments.py；cut_shorts.py 粗切，
10 shorts 均 30fps CFR）＋12 终端 freeze＋artifacts 真机产物
（contact4/frame10/contact5/zoom 裁图/onion-good/compare/grade）。
终端素材 1600x920 缩左 1120x644（left:54 top:226），右侧 620px 概念卡
随口播拍点轮替；论述段全屏概念卡。

用法：
  python make_video.py              正式版（须 media/shorts＋freezes＋artifacts）
  python make_video.py --cards-only 仅概念卡（录屏未到位时 check/snapshot 自验）

时点锚 cues.json（559.22s／273 句，2026-10-20 换主角 v2 母带）；
time_offset=0.31（oneoffs/measure_offset.py 实测中位 +315.1ms，53/69）。
"""
import io
import sys
from dataclasses import replace
from pathlib import Path

CARDS_ONLY = "--cards-only" in sys.argv

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

# GitHub Dark 蓝主色：底用原色 #0d1117，字幕逐字高亮换蓝（事实集）
THEME = replace(
    DARK_GOLD_GH,
    name="githubdark-blue-hf07",
    accent="#58a6ff",
)

# ---- GitHub Dark 辅助色 ----
PANEL, LINE = "#161b22", "#30363d"
INK, MUTE = "#e6edf3", "#8b949e"
BLUE, BLUE2 = "#1f6feb", "#58a6ff"
GREEN, GREEN2 = "#3fb950", "#7ee787"
RED, RED2 = "#f85149", "#ffa198"
AMBER, GOLD = "#d29922", "#e3b341"

# ---------- 20 幕（边界严格首尾相接；时间＝成片音频秒，锚 cues 词戳） ----------
SCENES = [

# m01 实验钩子 0.00–1.40
Scene("sc-open", 0.00, 1.40, """
          <div class="lab" id="lab">
            <div class="lab-dots"><i class="b"></i><i class="g"></i><i class="r"></i></div>
            <div class="lab-word">先做一个实验</div>
          </div>"""),

# m02 三元素开演＋preview 无痕 1.40–31.18
Scene("sc-three", 1.40, 31.18, """
          <div class="stage" id="m2-intro">
            <div class="kicker-static">工程里三个元素，同一秒开演</div>
            <div class="three-list">
              <div class="tl-row blue" id="tl-blue">
                <span class="tl-sq blue"></span>
                <div class="tl-body"><b>蓝方块</b>·交给 <span class="mono blue2-t">GSAP</span>，从左滑到右
                  <div class="tl-tag ok">seekable · 登记在册</div></div>
              </div>
              <div class="tl-row green" id="tl-green">
                <span class="tl-sq green"></span>
                <div class="tl-body"><b>绿点</b>·最普通的 <span class="mono green-t">CSS</span> 动画，一亮一暗地喘气
                  <div class="tl-tag ok">WAAPI 接管 · 登记在册</div></div>
              </div>
              <div class="tl-row red" id="tl-red">
                <span class="tl-sq red"></span>
                <div class="tl-body"><b>红方块</b>·也从左滑到右，可不归任何动画库管
                  <div class="tl-tag bad">setInterval · 自己掐表的黑户</div></div>
              </div>
            </div>
          </div>

          <div class="termwrap" id="m2-term">
            <div class="gk rightcard" id="c2-preview">
              <div class="gk-tag">我开 preview</div>
              <div class="pv-rows">
                <div class="pvr" id="pvr-1"><span class="pv-dot blue"></span>蓝的走蓝的</div>
                <div class="pvr" id="pvr-2"><span class="pv-dot green"></span>绿的喘绿的</div>
                <div class="pvr" id="pvr-3"><span class="pv-dot red"></span>红的滑得又顺又稳</div>
              </div>
              <div class="goldword-sm" id="c2-word">三个都没有任何毛病</div>
            </div>
          </div>"""),

# m03 连拍四个第二秒（终端＋右卡）31.18–43.40
Scene("sc-snap4", 31.18, 43.40, """
          <div class="termwrap" id="m3-term">
            <div class="gk rightcard" id="c3-ask">
              <div class="gk-tag">不拖进度条</div>
              <div class="c3-line">让机器在<b class="blue2-t">同一秒钟</b>连拍四张照片</div>
            </div>
            <div class="gk rightcard" id="c3-cmd">
              <div class="gk-tag">命令是 <span class="mono blue2-t">snapshot</span></div>
              <div class="cmdbox">snapshot v1 --at <b class="gold-t">2,2,2,2</b></div>
              <div class="rule-foot">时点写四个一模一样的数字</div>
            </div>
            <div class="gk rightcard" id="c3-four">
              <div class="four2">
                <i>第二秒</i><i>第二秒</i><i>第二秒</i><i>第二秒</i>
              </div>
            </div>
          </div>"""),

# m04 contact4 全屏＋烤片成本 43.40–85.42
Scene("sc-contact4", 43.40, 85.42, """
          <div class="stage" id="m4-sheet">
            <div class="kicker-static">四张照片摆一块儿</div>
            <img class="contactbig" id="contact4-img" src="media/artifacts/contact4.jpg" alt="">
            <div class="verdicts">
              <div class="vd blue" id="vd-b">蓝方块纹丝不动，像素级地稳</div>
              <div class="vd green" id="vd-g">最普通的 CSS 绿点，也钉在同一个相位，一寸没挪</div>
              <div class="vd red" id="vd-r">红方块呢——四张图，四个位置</div>
            </div>
          </div>

          <div class="stage" id="m4-cost">
            <div class="costrows">
              <div class="cost-eq" id="cost-eq">
                <span class="ce-item">一帧，零点几秒</span><span class="ce-x">×</span>
                <span class="ce-item">上万帧</span><span class="ce-x">＝</span>
                <span class="ce-out">烤一次，大几十分钟</span>
              </div>
              <div class="cost-waste" id="cost-waste">烤完才发现某个元素满屏乱飘——这大几十分钟，白等了</div>
              <div class="cost-last" id="cost-last">上集说过：声音画面都齐了，总不能闭着眼等渲染</div>
              <div class="cost-fear" id="cost-fear">视频这东西，最怕的不是丑，是<b class="red2">不确定</b></div>
              <div class="cost-topic" id="cost-topic">烤片之前，怎么把每一帧看清楚</div>
            </div>
          </div>"""),

# m05 两种时间＋墙钟机制 85.42–136.14
Scene("sc-clocks", 85.42, 136.14, """
          <div class="stage" id="m5-ask">
            <div class="ask-q" id="ask-q">问题出在哪？</div>
            <div class="ask-a" id="ask-a">两种动画，过的是<b class="blue2-t">两种时间</b></div>
            <div class="twoclocks">
              <div class="clock-card redside" id="clk-wall">
                <div class="clock-h">墙钟</div>
                <div class="clock-l">浏览器里看不见的钟</div>
                <div class="clock-l">从页面打开那刻起，<b>自己走</b></div>
              </div>
              <div class="clock-vs" id="clk-vs">VS</div>
              <div class="clock-card blueside" id="clk-axis">
                <div class="clock-h">时间轴</div>
                <div class="clock-l">进度条说了算</div>
                <div class="clock-l">拖到第几秒，<b>就停在第几秒</b></div>
              </div>
            </div>
          </div>

          <div class="stage" id="m5-mech">
            <div class="mech-cards">
              <div class="mc registered" id="mc-ok">
                <div class="mc-h"><span class="mc-n green">✓</span>登记在时间轴上</div>
                <div class="mc-l"><span class="sq blue"></span>蓝方块（GSAP）是</div>
                <div class="mc-l"><span class="sq green"></span>绿点那种 CSS 动画也是</div>
                <div class="mc-note" id="mc-waapi">浏览器内部有一套<b class="blue2-t">标准的动画接口</b>，
                  把 CSS 动画一并接管——拖到第十秒，它就停在第十秒的相位</div>
              </div>
              <div class="mc blackhouse" id="mc-bad">
                <div class="mc-h"><span class="mc-n red">✗</span>红方块不这样</div>
                <div class="mc-code mono">setInterval（闭包里揣着自己的计数器）</div>
                <div class="mc-l">一下一下，自己累加</div>
                <div class="mc-badrows" id="mc-badrows">
                  <span>既不登记时间轴</span><span>也不读系统时间</span><span>只认现实里过了几秒</span>
                </div>
              </div>
              <div class="mc result" id="mc-result">
                连拍四个第二秒，四次按下快门的瞬间，它自己的表走得不一样远——
                <b class="red2">红方块就站在四个地方</b>
              </div>
            </div>
          </div>"""),

# m06 慢表边界实验（终端＋frame10）136.14–158.82
Scene("sc-slow", 136.14, 158.82, """
          <div class="termwrap" id="m6-term">
            <div class="gk rightcard" id="c6-exp">
              <div class="gk-tag">边界实验</div>
              <div class="c6-line">把红方块的表调慢——慢到<b class="red2">一分钟才走一圈</b></div>
              <div class="cmdbox">snapshot v3 --at <b class="gold-t">10</b></div>
            </div>
            <div class="gk rightcard" id="c6-read">
              <div class="gk-tag">进度条停在第十秒</div>
              <div class="readrows">
                <div class="readr" id="rd-blue"><span class="sq blue"></span>蓝方块八秒走完全程，<b class="green-t">早在终点等着</b></div>
                <div class="readr" id="rd-red"><span class="sq red"></span>红方块的表才走 <b class="red2">六分之一</b>，人还贴在起点附近</div>
              </div>
              <div class="goldword-sm" id="c6-word">自己掐表的，时间轴一律管不着</div>
            </div>
          </div>"""),

# m07 CSS 平反 158.82–191.80
Scene("sc-css", 158.82, 191.80, """
          <div class="termwrap" id="m7-term">
            <div class="gk rightcard" id="c7-clear">
              <div class="gk-tag">平心而论</div>
              <div class="c7-line">这事真赖不着 <b class="green-t">CSS</b></div>
              <div class="rule-cn">绿点就是 CSS——人家每一帧都<b class="blue2-t">听调度</b></div>
            </div>
          </div>

          <div class="stage" id="m7-who">
            <div class="who-card" id="who-bad">
              <div class="who-h red2">真正的黑户</div>
              <div class="who-l">不登记、自己掐表跑的<b>脚本</b></div>
            </div>
            <div class="who-card" id="who-web">
              <div class="who-h green-t">而做网页的时候</div>
              <div class="who-l">页面本来就是打开给人看的，跟着墙钟走，<b>天经地义</b></div>
              <div class="web-chips">
                <span class="wchip">loading 转圈</span><span class="wchip">按钮 hover</span>
                <span class="wchip">弹窗淡入</span><span class="wchip dim">全是这套</span>
              </div>
            </div>
            <div class="who-card hot" id="who-solve">
              <div class="who-l big">错的是把网页的习惯，直接搬进视频</div>
              <div class="solve-lines">
                <div id="sv-1">烤片不是在「播放页面」</div>
                <div id="sv-2">是在<b class="blue2-t">「求每一帧的解」</b></div>
                <div id="sv-3">同一个第几秒，不管求多少次——<b class="gold-t">答案必须是同一个</b></div>
              </div>
            </div>
          </div>"""),

# m08 老契约＋薛定谔的猫 191.80–216.80
Scene("sc-contract", 191.80, 216.80, """
          <div class="stage" id="m8-pact">
            <div class="kicker-static">GSAP 那套老契约，为什么管用？</div>
            <div class="pact3">
              <div class="pact-card" id="pc-1">
                <div class="pc-n mono">①</div><div class="pc-h mono">timeline</div>
                <div class="pc-l">默认暂停</div>
              </div>
              <div class="pact-card" id="pc-2">
                <div class="pc-n mono">②</div><div class="pc-h mono">__timelines</div>
                <div class="pc-l">每个动作登记到 window 点 __timelines 那张表上</div>
              </div>
              <div class="pact-card" id="pc-3">
                <div class="pc-n mono">③</div><div class="pc-h mono">seek</div>
                <div class="pc-l">渲染器想烤第几帧，直接 seek 到第几帧</div>
              </div>
            </div>
            <div class="pact-word" id="pc-word">要哪帧给哪帧，帧帧确定</div>
          </div>

          <div class="termwrap" id="m8-term">
            <div class="gk rightcard" id="c8-seek">
              <div class="gk-tag">前面有一集说过</div>
              <div class="goldword-sm">灵魂在 seek</div>
            </div>
          </div>

          <div class="stage" id="m8-cat">
            <div class="cat-q" id="cat-q">不能 seek 的动画</div>
            <div class="cat-rows">
              <div class="catr alive" id="catr-1">实时预览里，是<b class="green-t">活的</b></div>
              <div class="catr dead" id="catr-2">进了烤片炉，就是<b class="red2">薛定谔的猫</b></div>
            </div>
          </div>"""),

# m09 preview / snapshot 分工 216.80–228.40
Scene("sc-preview", 216.80, 228.40, """
          <div class="stage" id="m9-job">
            <div class="kicker-static">那实时预览还要不要？要，它干它擅长的</div>
            <div class="job-cards">
              <div class="job-card pv" id="jb-pv">
                <div class="job-h">preview</div>
                <div class="job-l">听声音 · 看节奏</div>
                <div class="job-l">感受整片顺不顺</div>
              </div>
              <div class="job-arrow" id="jb-arrow">但「这一帧对不对」——</div>
              <div class="job-card snap" id="jb-snap">
                <div class="job-h mono">snapshot</div>
                <div class="job-l big">这个问题，永远问它</div>
              </div>
            </div>
          </div>"""),

# m10 跟 check 分工 228.40–258.59
Scene("sc-check", 228.40, 258.59, """
          <div class="stage" id="m10-job">
            <div class="kicker-static">再跟 check 分个工</div>
            <div class="gate-cards">
              <div class="gate-card machine" id="gt-machine">
                <div class="gate-h mono">check</div>
                <div class="gate-sub">机器替你跑体检</div>
                <div class="gate-l">结构非法 · 对比度不够 · 文件缺失</div>
                <div class="gate-l">按规则，一条条查</div>
              </div>
              <div class="gate-card eye" id="gt-eye">
                <div class="gate-h">你的眼睛</div>
                <div class="gate-sub">看照片</div>
                <div class="gate-l">「此刻该不该在这个位置」</div>
                <div class="gate-l">「这个动作看着舒不舒服」——规则管不着</div>
              </div>
            </div>
            <div class="gate-case" id="gt-case">
              就说这个红方块：check 一路绿灯，<b class="green-t">零个 error</b>，眼睛照样被它骗
            </div>
            <div class="gate-word" id="gt-word">
              机器全绿，只说明<b>规矩没破</b>，不说明画面是对的——两道闸，谁也替不了谁
            </div>
          </div>"""),

# m11 snapshot at/frames/接触表（终端）258.59–282.78
Scene("sc-shot1", 258.59, 282.78, """
          <div class="termwrap" id="m11-term">
            <div class="gk rightcard" id="c11-at">
              <div class="gk-tag">时点两种写法 · 心里有数</div>
              <div class="cmdbox">snapshot v1 --at <b class="gold-t">2,4,6.5</b></div>
              <div class="rule-foot">用 at，把秒数一个一个列出来</div>
            </div>
            <div class="gk rightcard" id="c11-frames">
              <div class="gk-tag">只想均匀扫一遍</div>
              <div class="cmdbox">snapshot v1 --frames <b class="gold-t">5</b></div>
              <div class="rule-foot">整片等分，开头结尾自动带上</div>
              <div class="rule-foot dim">每张照片按秒数命名</div>
            </div>
            <div class="gk rightcard" id="c11-sheet">
              <div class="gk-tag">额外还送一张</div>
              <div class="c11-big">接触表</div>
              <div class="rule-foot">所有时刻排在一张图上</div>
              <div class="goldword-sm">等于给整片做了一次体检总览</div>
            </div>
          </div>"""),

# m12 zoom（终端＋裁图＋报错）282.78–296.60
Scene("sc-zoom", 282.78, 296.60, """
          <div class="termwrap" id="m12-term">
            <div class="gk rightcard" id="c12-zoom">
              <div class="gk-tag">想看清局部</div>
              <div class="cmdbox">--zoom <b class="gold-t">"#bad"</b></div>
              <div class="rule-foot">后跟选择器，或直接给一块像素区域</div>
              <div class="rule-foot">把那一块，<b class="blue2-t">高密度裁出来</b></div>
            </div>
            <div class="gk rightcard err" id="c12-err">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>选择器写错、啥也没选中</b></div>
              <div class="rule-cn">它不糊弄你一张全图</div>
              <div class="rule-foot hot">直接报错</div>
            </div>
          </div>"""),

# m13 拍哪些秒＋清扫语义 296.60–325.24
Scene("sc-where", 296.60, 325.24, """
          <div class="stage" id="m13-where">
            <div class="kicker-static">拍哪些秒，也有讲究 · 均匀拍五张是扫雷</div>
            <div class="where3">
              <div class="wh-card" id="wh-1">
                <div class="wh-n">①</div>
                <div class="wh-h">接缝</div>
                <div class="wh-l">每段 clip 的接缝前后各一张——转场最容易穿帮</div>
              </div>
              <div class="wh-card" id="wh-2">
                <div class="wh-n">②</div>
                <div class="wh-h">半途</div>
                <div class="wh-l">动作的中间状态拍一张——起步和落位往往都对，错在半途</div>
              </div>
              <div class="wh-card" id="wh-3">
                <div class="wh-n">③</div>
                <div class="wh-h">心虚句</div>
                <div class="wh-l">你自己写得最没把握的那几句，单独点名</div>
              </div>
            </div>
            <div class="clean-card" id="wh-clean">
              <div class="cl-h">照片拍完，不想要旧的也无妨</div>
              <div class="cl-l">它<b class="blue2-t">只清理自己命名的帧</b>——你搁旁边的别的文件，一律不碰</div>
            </div>
          </div>"""),

# m14 keyframes --shot 洋葱皮＋无参体检报告 325.24–367.98
Scene("sc-keyframes", 325.24, 367.98, """
          <div class="stage" id="m14-onion">
            <div class="kicker-static">有了照片，怎么判断一个动作本身对不对？总不能一格一格去对</div>
            <div class="onion-card">
              <div class="onion-cmd mono" id="on-cmd">keyframes v1 --shot onion.png --selector #good</div>
              <div class="onion-l" id="on-l">把元素在整条时间线上的轨迹，拍成<b class="blue2-t">一张洋葱皮图</b>：
                半透明残影排在线上——第几秒在哪，拐弯没有，停顿没有，一眼看完</div>
              <div class="onion-spec" id="on-spec">
                <span class="os-chip">默认沿线采 <b>9</b> 个点</span>
                <span class="os-chip">疏密用 <span class="mono gold-t">samples</span> 调</span>
                <span class="os-chip">只看某段：<span class="mono gold-t">from / to</span> 掐头去尾</span>
              </div>
            </div>
          </div>

          <div class="termwrap" id="m14-term">
            <div class="gk rightcard" id="c14-report">
              <div class="gk-tag">它还能做体检 · 不加 <span class="mono">--shot</span>，光出报告</div>
              <div class="report-rows">
                <div class="rpr" id="rpr-1"><span class="sq blue"></span>GSAP 动作</div>
                <div class="rpr" id="rpr-2"><span class="sq green"></span>CSS 的 keyframes</div>
                <div class="rpr" id="rpr-3"><span class="sq amber"></span>Anime 的时间线</div>
              </div>
              <div class="report-note">逐户登记 · 我这个工程里——</div>
              <div class="items-big mono" id="rpr-items">3 items</div>
            </div>
          </div>"""),

# m15 #bad 黑户点名＋硬报错＋洋葱皮公道 367.98–421.02
Scene("sc-blackhouse", 367.98, 421.02, """
          <div class="termwrap" id="m15-term">
            <div class="gk rightcard" id="c15-noaccount">
              <div class="gk-tag">再点一下这个红方块的名</div>
              <div class="rule-cn">它在画面里<b class="red2">红得扎眼</b>，可体检报告上压根没有它这一户</div>
              <div class="items-big mono" id="c15-items">3 items · 全是登记在册的</div>
            </div>
            <div class="gk rightcard" id="c15-shotit">
              <div class="gk-tag">我用 --shot 直接点它，想拍出它的轨迹</div>
              <div class="rule-foot">机器反手就是一个<b class="red2">硬报错</b> ↓</div>
            </div>
            <div class="gk rightcard" id="c15-near">
              <div class="gk-tag">它在动，机器却不知道它在动</div>
              <div class="rule-cn">离得最近的，是<b class="blue2-t">蓝块、时钟</b>和那个<b class="green-t">绿点</b></div>
            </div>
          </div>

          <div class="stage" id="m15-sneak">
            <div class="sneak-card">
              <div class="sn-h" id="sn-h">更刁的是</div>
              <div class="sn-l" id="sn-1">这段脚本要是敢<b class="red2">直接读系统时间</b>，
                或者用 <span class="mono red2">requestAnimationFrame</span> 那种逐帧回调——</div>
              <div class="sn-l good" id="sn-2">check <b class="green-t">立刻就拦下来了</b></div>
              <div class="sn-l" id="sn-3">它偏不：关起门，在闭包里<b>自己记数</b>——check 就看不出一点毛病</div>
            </div>
          </div>

          <div class="termwrap" id="m15-onion">
            <div class="gk rightcard" id="c15-fair">
              <div class="gk-tag">洋葱皮图也公道</div>
              <div class="rule-cn">只画<b class="blue2-t">登记过</b>的运动：蓝块九帧轨迹清清楚楚</div>
              <div class="rule-cn hot">红绿两个，连残影都没有</div>
              <div class="goldword-sm big" id="c15-hukou">上了户口，时间轴才管得着你</div>
            </div>
          </div>"""),

# m16 compare（终端＋对照图）421.02–457.36
Scene("sc-compare", 421.02, 457.36, """
          <div class="stage" id="m16-two">
            <div class="kicker-static">再进一步：两个方案摆一块儿挑</div>
            <div class="two-html">
              <div class="th-card a" id="th-a"><span class="th-file mono">v1/index.html</span>方块走 <b class="blue2-t">800</b> 像素</div>
              <div class="th-plus" id="th-plus">＋</div>
              <div class="th-card b" id="th-b"><span class="th-file mono">v2/index.html</span>走 <b class="green-t">500</b>，颜色也换掉</div>
            </div>
            <div class="cmdbox big" id="th-cmd">compare v1 v2 --at 4 --labels 方案A·x800,方案B·x500</div>
          </div>

          <div class="termwrap" id="m16-term">
            <div class="gk rightcard" id="c16-read">
              <div class="gk-tag">一张对照图出来了</div>
              <div class="rule-cn">每格带编号、带标签，同一个时刻两个方案并排站</div>
              <div class="rule-foot">不止两版也可以，它自己排版，一排最多<b class="blue2-t">四个</b></div>
              <div class="rule-foot">改布局、改配色、改动作幅度——不用来回切窗口，<b class="gold-t">一张图投票</b></div>
            </div>
            <div class="gk rightcard warn" id="c16-label">
              <div class="rule-head"><span class="rule-mark warn">!</span><b>标签有个小脾气</b></div>
              <div class="rule-cn">它按<b class="amber-t">逗号</b>分段——标签里自己别写逗号</div>
              <div class="rule-foot hot">写了，就被切成好几截</div>
            </div>
          </div>"""),

# m17 grade-compare＋no-op 坑＋present 457.36–493.06
Scene("sc-grade", 457.36, 493.06, """
          <div class="termwrap" id="m17-term">
            <div class="gk rightcard" id="c17-what">
              <div class="gk-tag">两件小工具，一句话带过</div>
              <div class="rule-cn"><span class="mono gold-t">grade-compare</span>：拿同一帧套几种调色，
                暖色一档、高亮一档，摆一块儿</div>
              <div class="rule-foot hot">选片用的，不是查帧用的</div>
            </div>
            <div class="gk rightcard err" id="c17-pit">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>我自己踩的坑</b></div>
              <div class="rule-cn">图省事，照网页习惯写了一串 <span class="mono red2">CSS filter</span></div>
              <div class="rule-cn">图是出了，<b class="red2">三格却一模一样</b></div>
              <div class="warn-lines">
                <div class="wl" id="wl-1">⚠ 这一档 inactive / no-op</div>
                <div class="wl" id="wl-2">机器倒没瞒着，发了条警告</div>
              </div>
              <div class="rule-foot hot">等于白烤一遍——配置要按它的规矩写</div>
            </div>
          </div>

          <div class="stage" id="m17-present">
            <div class="present-card">
              <div class="pr-h mono" id="pr-h">present</div>
              <div class="pr-l" id="pr-l">把工程当幻灯片、全屏放的<b>演讲模式</b></div>
              <div class="pr-sub" id="pr-sub">也不是日常预览</div>
            </div>
          </div>"""),

# m18 recap 三句话 493.06–520.62
Scene("sc-recap", 493.06, 520.62, """
          <div class="stage" id="m18-recap">
            <div class="kicker-static gold-kicker">今天一集，记住三句话</div>
            <div class="recap-rows">
              <div class="rr-card" id="rr-1">
                <div class="rr-n">①</div>
                <div class="rr-l">实时预览管<b class="blue2-t">感受</b>，snapshot 管<b class="blue2-t">事实</b>——
                  眼睛会骗人，<b class="gold-t">帧不会</b></div>
              </div>
              <div class="rr-card" id="rr-2">
                <div class="rr-n">②</div>
                <div class="rr-l">凡是要烤进片子的动画，必须能被 <span class="mono gold-t">seek</span> 管住；
                  不登记时间轴、自己掐表跑的动画再顺滑——<b class="red2">留给网页，别留给烤片炉</b></div>
              </div>
              <div class="rr-card" id="rr-3">
                <div class="rr-n">③</div>
                <div class="rr-l">拿不准就拍照片：关键帧拍、接缝处拍、开头结尾拍——
                  <b class="gold-t">一张接触表，胜过盯着播放头看半小时</b></div>
              </div>
            </div>
          </div>"""),

# m19 行动件 520.62–544.30
Scene("sc-action", 520.62, 544.30, """
          <div class="stage" id="m19-action">
            <div class="kicker-static">行动件：打开你手上的工程</div>
            <div class="acl">
              <div class="acl-row" id="ac-1"><span class="acl-n">①</span>
                先用 <span class="mono gold-t">frames</span> 拍五张</div>
              <div class="acl-row" id="ac-2"><span class="acl-n">②</span>
                再找一个你最没把握的动作，<span class="mono gold-t">keyframes</span> 加 <span class="mono gold-t">--shot</span>，出一张洋葱皮</div>
              <div class="acl-row" id="ac-3"><span class="acl-n">③</span>
                发现哪个元素是脚本自己掐表、不登记时间轴的——趁早换回 <span class="mono blue2-t">seekable</span> 的写法</div>
            </div>
            <div class="action-ps" id="ac-ps">CSS 动画你放心用，人家有户口；别等整片烤完，才认识那个黑户</div>
          </div>"""),

# m20 render 预告＋道别 544.30–TOTAL
Scene("sc-next", 544.30, total, """
          <div class="stage" id="m20-next">
            <div class="nx-h" id="nx-h">下一集</div>
            <div class="nx-card mono" id="nx-card">render</div>
            <div class="nx-lines">
              <div id="nx-l1">照片都验干净了，就该真烤了——无头浏览器怎样把网页一帧帧烤成 <span class="mono">M P 四</span></div>
              <div id="nx-l2">上万帧要烤多久 · 烤崩了怎么查</div>
            </div>
          </div>
          <div class="bye" id="bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 顶层录屏/真机图 clip（不可嵌套；放 scenes 之前＝下层） ----------
# 终端素材 1600x920 缩左 1120x644（.term fill）；artifacts 非 16:9 真机图
# 同位 contain（.shot）；zoom 504x504 方图（.sq）；contact4 全屏宽图自带类。
# 视频段 data-media-start 取 cut_shorts 源内切点（源＝shorts 自身秒）。
if CARDS_ONLY:
    VIDEOS = "      <!-- --cards-only：录屏/真机图 clip 待媒体到位后填入 -->"
else:
    VIDEOS = """      <!-- m02 1.40–31.18：preview 后台命令 → player 红蓝绿同屏无痕 -->
      <video id="rec-prev" class="clip term" data-start="20.80"
             data-duration="4.00" data-track-index="2"
             src="media/shorts/prev-bg-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-prev" class="clip term" data-start="24.80"
           data-duration="1.00" src="media/freezes/prev-bg-run.png" alt="">
      <video id="rec-player" class="clip term" data-start="25.80"
             data-duration="5.38" data-track-index="2"
             src="media/shorts/player-run.mp4" muted playsinline preload="auto"></video>

      <!-- m03 31.18–43.40：snapshot --at 2,2,2,2 敲字段＋4 frames 列表 -->
      <video id="rec-snap4" class="clip term" data-start="32.00"
             data-duration="6.50" data-track-index="2"
             src="media/shorts/snap4-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-snap4" class="clip term" data-start="38.50"
           data-duration="4.90" src="media/freezes/snap4-run.png" alt="">

      <!-- m06 136.14–158.82：snapshot v3 --at 10 敲字段＋frame10 真机帧 -->
      <video id="rec-slow" class="clip term" data-start="136.80"
             data-duration="7.50" data-track-index="2"
             src="media/shorts/slow10-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-frame10" class="clip shot" data-start="144.30"
           data-duration="14.52" src="media/artifacts/frame10.png" alt="">

      <!-- m07 158.82–191.80：绿点＝CSS 听调度，player 短回切 -->
      <video id="rec-greendot" class="clip term" data-start="160.30"
             data-duration="4.00" data-track-index="2"
             src="media/shorts/player-run.mp4" muted playsinline preload="auto"></video>

      <!-- m08 191.80–216.80：蓝块早在终点，seek 段短回切 -->
      <video id="rec-seek" class="clip term" data-start="205.00"
             data-duration="4.50" data-track-index="2"
             src="media/shorts/player-run.mp4" muted playsinline preload="auto"></video>

      <!-- m11 258.59–282.78：frames 5 敲字段＋列表＋接触表真机图 -->
      <video id="rec-frames5" class="clip term" data-start="261.50"
             data-duration="7.00" data-track-index="2"
             src="media/shorts/frames5-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-frames5" class="clip term" data-start="268.50"
           data-duration="7.60" src="media/freezes/frames5-run.png" alt="">
      <img id="img-contact5" class="clip shot" data-start="276.10"
           data-duration="6.68" src="media/artifacts/contact5.jpg" alt="">

      <!-- m12 282.78–296.60：zoom #bad 敲字段 → 504 裁图 → #nope 硬报错（报错口播 288.66） -->
      <video id="rec-zoom" class="clip term" data-start="283.20"
             data-duration="4.80" data-track-index="2"
             src="media/shorts/zoom-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-zoomcrop" class="clip shot-sq" data-start="288.20"
           data-duration="3.60" src="media/artifacts/zoom-crop.png" alt="">
      <img id="img-zoomerr" class="clip term" data-start="292.00"
           data-duration="4.20" src="media/freezes/zoom-nope-err.png" alt="">

      <!-- m14 325.24–367.98：无参 keyframes 敲命令出报告＋3 items 尾帧 -->
      <video id="rec-kf" class="clip term" data-start="356.30"
             data-duration="8.00" data-track-index="2"
             src="media/shorts/keyframes-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-kfreport" class="clip term" data-start="364.30"
           data-duration="3.68" src="media/freezes/keyframes-run.png" alt="">

      <!-- m15 367.98–421.02：报告回切＋#bad 硬报错＋洋葱皮真机图 -->
      <img id="img-kfreport2" class="clip term" data-start="368.30"
           data-duration="13.50" src="media/freezes/keyframes-run.png" alt="">
      <img id="img-kfbad" class="clip term" data-start="382.00"
           data-duration="9.40" src="media/freezes/kf-bad-err.png" alt="">
      <img id="img-onion" class="clip shot" data-start="408.80"
           data-duration="12.22" src="media/artifacts/onion-good.png" alt="">

      <!-- m16 421.02–457.36：compare 敲字段＋Rendering＋对照真机图（与逗号卡同屏） -->
      <video id="rec-compare" class="clip term" data-start="430.50"
             data-duration="8.00" data-track-index="2"
             src="media/shorts/compare-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-compare" class="clip shot" data-start="438.90"
           data-duration="18.10" src="media/artifacts/compare.png" alt="">

      <!-- m17 457.36–493.06：旧录 CSS filter no-op 警告入镜＋adjust 正确档 -->
      <video id="rec-grade" class="clip term" data-start="467.80"
             data-duration="10.00" data-track-index="2"
             src="media/shorts/grade-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-gradewarn" class="clip term" data-start="477.80"
           data-duration="8.00" src="media/freezes/grade-run.png" alt="">
      <img id="img-gradeok" class="clip shot" data-start="485.80"
           data-duration="1.70" src="media/artifacts/grade.png" alt="">"""

# ---------- 场景专属 CSS ----------
PROJECT_CSS = """
      /* 背景：蓝色细网格＋蓝红光斑（事实集蓝主色，区别 hf-06 金） */
      #bg-grid { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background-image:
          linear-gradient(rgba(88,166,255,.055) 1px, transparent 1px),
          linear-gradient(90deg, rgba(88,166,255,.055) 1px, transparent 1px);
        background-size:80px 80px; }
      #bg-glow { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background:
          radial-gradient(720px 500px at 16% 12%, rgba(31,111,235,.17), transparent 70%),
          radial-gradient(840px 580px at 86% 84%, rgba(248,81,73,.10), transparent 70%); }

      /* 终端录屏/终端 freeze：1600x920 缩左 1120x644，右 620px 让给概念卡 */
      .term { position:absolute; left:54px; top:226px; width:1120px; height:644px;
        object-fit:fill; border-radius:10px;
        box-shadow:0 18px 60px rgba(0,0,0,.55); }
      /* artifacts 真机产物：同机位但保持原比例（1920x1080/宽扁/方形） */
      .shot { position:absolute; left:54px; top:226px; width:1120px; height:644px;
        object-fit:contain; background:#0a0d12; border-radius:10px;
        box-shadow:0 18px 60px rgba(0,0,0,.55); }
      .shot-sq { position:absolute; left:292px; top:226px; width:644px; height:644px;
        object-fit:contain; background:#0a0d12; border-radius:10px;
        box-shadow:0 18px 60px rgba(0,0,0,.55); }

      /* 通用 */
      .kicker { position:absolute; left:0; right:0; top:40px; text-align:center;
        font-size:42px; color:#8b949e; }
      .kicker-static { text-align:center; font-size:44px; color:#8b949e; margin-bottom:34px; }
      .gold-kicker { color:#e3b341; }
      .mono { font-family:'Consolas','Courier New',monospace; color:#e6edf3; }
      .mono.gold, .gold-t { color:#e3b341; }
      .blue2-t { color:#58a6ff; } .green-t { color:#7ee787; }
      .red-t, .red2 { color:#ffa198; } .amber-t { color:#e3b341; }
      .goldword-sm { margin-top:18px; text-align:center; font-size:42px;
        color:#e3b341; letter-spacing:.03em; }
      .goldword-sm.big { font-size:50px; margin-top:24px; }
      .stage { position:absolute; left:120px; right:120px; top:150px; text-align:center; }
      .sq { display:inline-block; width:26px; height:26px; border-radius:7px;
        margin-right:14px; vertical-align:-3px; background:#8b949e; }
      .sq.blue { background:#1f6feb; } .sq.green { background:#3fb950; }
      .sq.red { background:#f85149; } .sq.amber { background:#d29922; }

      /* ===== 右卡（终端幕）：gk 容器固定，gk-card 同位置轮替 ===== */
      .gk { position:absolute; left:1200px; top:128px; width:620px; height:800px; }
      .gk-card { position:absolute; left:0; top:0; width:620px;
        box-sizing:border-box; background:#161b22; border:2px solid #30363d;
        border-radius:18px; padding:30px 34px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      /* 右卡元素同时挂 .gk（left:1200 定位）；这里只给视觉，不给 position/left，
         否则 left:0 会把卡片打回屏幕左上角（hf-07 首轮抽帧实测） */
      .rightcard { box-sizing:border-box; background:#161b22; border:2px solid #30363d;
        border-radius:18px; padding:30px 34px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      .gk-tag { font-size:33px; color:#58a6ff; line-height:1.5; margin-bottom:18px; }
      .gk-card.rule, .rightcard.err, .rightcard.warn { padding-top:24px; }
      .rightcard.err { border-color:#6e2b2b; }
      .rightcard.warn { border-color:#5e4a1e; }
      .rule-head { display:flex; align-items:center; font-size:32px; margin-bottom:16px; }
      .rule-head b { color:#e6edf3; font-weight:600; }
      .rule-mark { display:inline-flex; align-items:center; justify-content:center;
        width:50px; height:50px; border-radius:50%; font-size:32px; margin-right:13px; }
      .rule-mark.warn { background:rgba(210,153,34,.16); color:#d29922; }
      .rule-mark.err { background:rgba(248,81,73,.16); color:#f85149; }
      .rule-mark.pass { background:rgba(63,185,80,.16); color:#3fb950; }
      .rule-cn { font-size:33px; color:#c9d1d9; line-height:1.55; margin:10px 0; }
      .rule-foot { margin-top:14px; font-size:30px; color:#8b949e; line-height:1.5; }
      .rule-foot.hot, .rule-cn.hot { color:#ffa198; }
      .cmdbox { font-family:'Consolas','Courier New',monospace; font-size:30px;
        color:#c9d1d9; background:#0d1521; border:2px solid #30363d; border-radius:12px;
        padding:20px 22px; line-height:1.5; margin:14px 0; }
      .cmdbox.big { font-size:28px; text-align:center; }

      /* m01 实验台 */
      .lab { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .lab-dots { margin-bottom:44px; }
      .lab-dots i { display:inline-block; width:54px; height:54px; border-radius:14px;
        margin:0 26px; }
      .lab-dots i.b { background:#1f6feb; box-shadow:0 0 34px rgba(31,111,235,.6); }
      .lab-dots i.g { background:#3fb950; box-shadow:0 0 34px rgba(63,185,80,.6); }
      .lab-dots i.r { background:#f85149; box-shadow:0 0 34px rgba(248,81,73,.6); }
      .lab-word { font-size:96px; color:#e6edf3; letter-spacing:.12em; }

      /* m02 三元素（全屏） */
      .three-list { width:1500px; margin:0 auto; }
      .tl-row { display:flex; align-items:flex-start; background:#161b22;
        border:2px solid #30363d; border-radius:18px; padding:26px 36px;
        margin:20px 0; text-align:left; }
      .tl-row.blue { border-left:10px solid #1f6feb; }
      .tl-row.green { border-left:10px solid #3fb950; }
      .tl-row.red { border-left:10px solid #f85149; }
      .tl-sq { width:40px; height:40px; border-radius:10px; margin:6px 24px 0 0; flex:none; }
      .tl-sq.blue { background:#1f6feb; } .tl-sq.green { background:#3fb950; }
      .tl-sq.red { background:#f85149; }
      .tl-body { font-size:40px; color:#e6edf3; line-height:1.5; }
      .tl-tag { display:inline-block; margin-top:10px; font-size:30px;
        padding:6px 20px; border-radius:999px; }
      .tl-tag.ok { color:#7ee787; background:rgba(63,185,80,.12); border:2px solid #2b573f; }
      .tl-tag.bad { color:#ffa198; background:rgba(248,81,73,.12);
        border:2px solid #6e2b2b; font-family:'Consolas','Courier New',monospace; }
      .pv-rows { margin:10px 0 6px; }
      .pvr { display:flex; align-items:center; font-size:38px; color:#e6edf3;
        line-height:2.0; }
      .pv-dot { width:24px; height:24px; border-radius:50%; margin-right:18px; }
      .pv-dot.blue { background:#1f6feb; } .pv-dot.green { background:#3fb950; }
      .pv-dot.red { background:#f85149; }

      /* m03 四个第二秒 */
      .c3-line { font-size:38px; color:#e6edf3; line-height:1.7; }
      .four2 { text-align:center; margin:30px 0; }
      .four2 i { display:inline-block; font-style:normal; font-size:40px; color:#58a6ff;
        background:#0d1521; border:2px solid #1f4e8c; border-radius:14px;
        padding:18px 14px; margin:6px; width:120px; }

      /* m04 接触表全屏＋成本 */
      .contactbig { display:block; width:1422px; height:580px; object-fit:fill;
        margin:0 auto; border-radius:12px; box-shadow:0 16px 50px rgba(0,0,0,.5); }
      .verdicts { margin-top:26px; }
      .vd { font-size:38px; line-height:1.5; color:#8b949e; }
      .vd.blue { color:#79c0ff; } .vd.green { color:#7ee787; } .vd.red { color:#ffa198; }
      .costrows { width:1500px; margin:0 auto; }
      .cost-eq { display:flex; align-items:center; justify-content:center;
        font-size:46px; color:#e6edf3; margin:30px 0; }
      .ce-item { background:#161b22; border:2px solid #1f4e8c; border-radius:14px;
        padding:16px 30px; }
      .ce-x { font-size:50px; color:#58a6ff; margin:0 22px; }
      .ce-out { background:rgba(248,81,73,.12); border:2px solid #6e2b2b;
        border-radius:14px; padding:16px 30px; color:#ffa198; }
      .cost-waste { font-size:42px; color:#ffa198; margin:36px 0; }
      .cost-last { font-size:36px; color:#8b949e; margin:34px 0; }
      .cost-fear { font-size:60px; color:#e6edf3; margin:34px 0; }
      .cost-topic { font-size:52px; color:#58a6ff; letter-spacing:.04em; }

      /* m05 双钟＋机制 */
      .ask-q { font-size:52px; color:#8b949e; }
      .ask-a { font-size:64px; color:#e6edf3; margin:18px 0 40px; }
      .twoclocks { display:flex; align-items:center; justify-content:center; }
      .clock-card { width:560px; background:#161b22; border-radius:20px; padding:40px 44px;
        text-align:left; }
      .clock-card.redside { border:2px solid #6e2b2b; }
      .clock-card.blueside { border:2px solid #1f4e8c; }
      .clock-h { font-size:52px; margin-bottom:18px; }
      .redside .clock-h { color:#ffa198; } .blueside .clock-h { color:#58a6ff; }
      .clock-l { font-size:34px; color:#c9d1d9; line-height:1.7; }
      .clock-vs { font-size:40px; color:#8b949e; margin:0 36px; }
      .mech-cards { width:1520px; margin:0 auto; }
      .mc { border-radius:18px; padding:28px 38px; margin:18px 0; text-align:left; }
      .mc.registered { background:#101c14; border:2px solid #2b573f; }
      .mc.blackhouse { background:#1d1212; border:2px solid #6e2b2b; }
      .mc.result { background:#161b22; border:2px solid #30363d; font-size:38px;
        color:#e6edf3; line-height:1.6; text-align:center; padding:30px 40px; }
      .mc-h { font-size:42px; color:#e6edf3; margin-bottom:12px; }
      .mc-n.green { color:#3fb950; margin-right:12px; }
      .mc-n.red { color:#f85149; margin-right:12px; }
      .mc-l { font-size:34px; color:#c9d1d9; line-height:1.7; display:flex;
        align-items:center; }
      .mc-code { font-family:'Consolas','Courier New',monospace; font-size:30px;
        color:#ffa198; background:#0d1521; border:2px solid #6e2b2b; border-radius:12px;
        padding:14px 22px; margin:12px 0; }
      .mc-note { font-size:31px; color:#8b949e; line-height:1.6; margin-top:12px; }
      .mc-badrows { margin-top:10px; }
      .mc-badrows span { display:inline-block; font-size:30px; color:#ffa198;
        background:rgba(248,81,73,.1); border:2px solid #6e2b2b; border-radius:999px;
        padding:8px 22px; margin:6px 10px 6px 0; }

      /* m06 慢表右卡 */
      .c6-line { font-size:36px; color:#e6edf3; line-height:1.65; margin-bottom:18px; }
      .readrows { margin:14px 0; }
      .readr { display:flex; align-items:center; font-size:32px; color:#c9d1d9;
        line-height:1.75; margin:12px 0; text-align:left; }

      /* m07 平反/黑户/确定性 */
      .c7-line { font-size:44px; color:#e6edf3; line-height:1.6; margin:14px 0; }
      .who-card { width:1400px; margin:18px auto; background:#161b22;
        border:2px solid #30363d; border-radius:18px; padding:26px 44px; }
      .who-h { font-size:40px; margin-bottom:10px; }
      .who-l { font-size:36px; color:#e6edf3; line-height:1.6; }
      .who-l.big { font-size:44px; margin-bottom:16px; }
      .who-card.hot { border-color:#1f4e8c; }
      .web-chips { margin-top:14px; }
      .wchip { display:inline-block; font-size:30px; color:#c9d1d9; background:#0d1521;
        border:2px solid #30363d; border-radius:999px; padding:8px 24px; margin:6px 12px; }
      .wchip.dim { color:#8b949e; }
      .solve-lines { font-size:38px; color:#c9d1d9; line-height:1.9; }

      /* m08 契约三件＋猫 */
      .pact3 { display:flex; justify-content:center; margin-top:10px; }
      .pact-card { width:420px; margin:0 22px; background:#161b22; border:2px solid #1f4e8c;
        border-radius:20px; padding:38px 32px; min-height:360px; }
      .pc-n { font-size:48px; color:#58a6ff; }
      .pc-h { font-size:40px; color:#79c0ff; margin:14px 0; }
      .pc-l { font-size:32px; color:#c9d1d9; line-height:1.6; }
      .pact-word { margin-top:38px; font-size:48px; color:#e3b341; }
      .cat-q { font-size:52px; color:#8b949e; margin-bottom:40px; }
      .cat-rows { display:flex; justify-content:center; gap:60px; }
      .catr { font-size:52px; background:#161b22; border:2px solid #30363d;
        border-radius:20px; padding:36px 50px; }
      .catr.alive { border-color:#2b573f; } .catr.dead { border-color:#6e2b2b; }

      /* m09 分工 */
      .job-cards { display:flex; align-items:center; justify-content:center; margin-top:30px; }
      .job-card { width:480px; background:#161b22; border:2px solid #30363d;
        border-radius:20px; padding:44px 38px; }
      .job-card.pv { border-color:#5e4a1e; } .job-card.snap { border-color:#1f4e8c; }
      .job-h { font-size:56px; color:#e3b341; margin-bottom:24px; }
      .job-card.snap .job-h { color:#58a6ff; }
      .job-l { font-size:36px; color:#c9d1d9; line-height:1.8; }
      .job-l.big { font-size:40px; color:#e6edf3; }
      .job-arrow { font-size:34px; color:#8b949e; margin:0 34px; width:300px;
        line-height:1.5; }

      /* m10 两道闸 */
      .gate-cards { display:flex; justify-content:center; gap:44px; margin-top:10px; }
      .gate-card { width:620px; background:#161b22; border:2px solid #30363d;
        border-radius:20px; padding:38px 40px; text-align:left; }
      .gate-card.machine { border-color:#1f4e8c; }
      .gate-card.eye { border-color:#5e4a1e; }
      .gate-h { font-size:50px; color:#58a6ff; margin-bottom:8px; }
      .gate-card.eye .gate-h { color:#e3b341; }
      .gate-sub { font-size:32px; color:#8b949e; margin-bottom:18px; }
      .gate-l { font-size:32px; color:#c9d1d9; line-height:1.75; }
      .gate-case { width:1300px; margin:30px auto 0; font-size:38px; color:#e6edf3;
        background:#1d1212; border:2px solid #6e2b2b; border-radius:16px;
        padding:24px 36px; line-height:1.5; }
      .gate-word { width:1360px; margin:26px auto 0; font-size:40px; color:#e3b341;
        line-height:1.55; }

      /* m11 右卡 */
      .c11-big { font-size:72px; color:#58a6ff; text-align:center; margin:14px 0; }

      /* m13 三处必拍＋清扫 */
      .where3 { display:flex; justify-content:center; }
      .wh-card { width:430px; margin:0 18px; background:#161b22; border:2px solid #1f4e8c;
        border-radius:20px; padding:34px 30px; min-height:380px; text-align:left; }
      .wh-n { font-size:48px; color:#58a6ff; }
      .wh-h { font-size:44px; color:#e6edf3; margin:10px 0 16px; }
      .wh-l { font-size:31px; color:#c9d1d9; line-height:1.65; }
      .clean-card { width:1300px; margin:34px auto 0; background:#0d1521;
        border:2px solid #2b573f; border-radius:16px; padding:24px 40px; text-align:left; }
      .cl-h { font-size:36px; color:#7ee787; margin-bottom:10px; }
      .cl-l { font-size:33px; color:#c9d1d9; line-height:1.5; }

      /* m14 洋葱皮能力＋报告 */
      .onion-card { width:1400px; margin:0 auto; background:#161b22;
        border:2px solid #1f4e8c; border-radius:20px; padding:40px 48px; text-align:left; }
      .onion-cmd { font-size:34px; color:#79c0ff; background:#0d1521;
        border:2px solid #30363d; border-radius:12px; padding:20px 26px; }
      .onion-l { font-size:36px; color:#c9d1d9; line-height:1.7; margin:24px 0; }
      .onion-spec { display:flex; }
      .os-chip { font-size:31px; color:#c9d1d9; background:#0d1521;
        border:2px solid #30363d; border-radius:999px; padding:10px 24px;
        margin-right:20px; }
      .report-rows { margin:14px 0; }
      .rpr { display:flex; align-items:center; font-size:34px; color:#e6edf3;
        line-height:1.9; text-align:left; }
      .report-note { font-size:30px; color:#8b949e; margin-top:12px; }
      .items-big { font-family:'Consolas','Courier New',monospace; font-size:64px;
        color:#7ee787; text-align:center; margin-top:14px;
        text-shadow:0 0 22px rgba(63,185,80,.4); }

      /* m15 黑户 */
      #c15-items { font-size:44px; color:#ffa198; text-shadow:none; margin-top:18px; }
      .sneak-card { width:1300px; margin:0 auto; background:#1d1212;
        border:2px solid #6e2b2b; border-radius:20px; padding:40px 48px; text-align:left; }
      .sn-h { font-size:44px; color:#ffa198; margin-bottom:20px; }
      .sn-l { font-size:37px; color:#c9d1d9; line-height:1.8; margin:12px 0; }
      .sn-l.good { color:#7ee787; }

      /* m16 compare */
      .two-html { display:flex; align-items:center; justify-content:center; margin:20px 0; }
      .th-card { width:480px; background:#161b22; border:2px solid #30363d;
        border-radius:18px; padding:32px 36px; font-size:38px; color:#e6edf3; }
      .th-card.a { border-color:#1f4e8c; } .th-card.b { border-color:#2b573f; }
      .th-file { display:block; font-size:28px; color:#8b949e; margin-bottom:14px; }
      .th-plus { font-size:56px; color:#8b949e; margin:0 34px; }
      #th-cmd { width:1200px; margin:6px auto 0; }

      /* m17 grade/present */
      .warn-lines { margin:16px 0; }
      .wl { font-family:'Consolas','Courier New',monospace; font-size:29px;
        color:#e3b341; background:#0d1521; border:2px solid #5e4a1e; border-radius:10px;
        padding:12px 20px; margin:8px 0; }
      .present-card { width:1100px; margin:0 auto; background:#161b22;
        border:2px solid #2b3c57; border-radius:22px; padding:56px 60px; }
      .pr-h { font-size:88px; color:#58a6ff; margin-bottom:26px; }
      .pr-l { font-size:46px; color:#e6edf3; line-height:1.6; }
      .pr-sub { font-size:36px; color:#8b949e; margin-top:22px; }

      /* m18 recap */
      .recap-rows { width:1560px; margin:0 auto; }
      .rr-card { display:flex; align-items:flex-start; background:#161b22;
        border:2px solid #5e4a1e; border-radius:18px; padding:28px 40px;
        margin:22px 0; text-align:left; }
      .rr-n { font-size:52px; color:#e3b341; margin-right:28px; flex:none; }
      .rr-l { font-size:38px; color:#e6edf3; line-height:1.6; }

      /* m19 行动件 */
      .acl { width:1400px; margin:0 auto; }
      .acl-row { padding:24px 38px; margin-bottom:20px; background:#161b22;
        border:2px solid #2b3c57; border-left:10px solid #1f6feb; border-radius:14px;
        font-size:39px; color:#e6edf3; line-height:1.5; text-align:left; }
      .acl-n { color:#e3b341; font-size:46px; margin-right:20px; }
      .action-ps { width:1300px; margin:26px auto 0; font-size:38px; color:#7ee787;
        line-height:1.5; }

      /* m20 */
      #m20-next { top:200px; }
      .nx-h { font-size:44px; color:#8b949e; letter-spacing:.3em; }
      .nx-card { font-size:96px; color:#58a6ff; margin:26px 0 40px; }
      .nx-lines { font-size:38px; color:#c9d1d9; line-height:1.9; }
      .bye { position:absolute; left:0; right:0; top:760px; text-align:center;
        font-size:72px; color:#e6edf3; letter-spacing:.08em; }
"""

# ---------- 场景时间轴（时间显式给秒；拍点锚 cues 实测词戳） ----------
SCENE_JS = """
      /* 拍点通用：右卡同位置轮替（x:60 滑入），全屏卡 y/淡入。
         gsap className 替换非追加，所有高亮一律属性补间（hf-05 教训）。 */

      /* m01 0–1.40：实验台 */
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.4},0);
      tl.from('.lab-dots i',{y:24,opacity:0,duration:.4,stagger:.12,ease:'back.out(1.6)'},.1);
      tl.from('#lab .lab-word',{y:20,opacity:0,duration:.5},.5);

      /* m02 1.40–31.18：三行 4.56/7.96/13.80 → preview 20.8 起终端，右卡 25.5 */
      tl.fromTo('#sc-three > .scene-inner',{opacity:0},{opacity:1,duration:.5},1.40);
      tl.from('#tl-blue',{x:-50,opacity:0,duration:.55,ease:'back.out(1.2)'},4.2);
      tl.from('#tl-green',{x:-50,opacity:0,duration:.55,ease:'back.out(1.2)'},8.0);
      tl.from('#tl-red',{x:-50,opacity:0,duration:.55,ease:'back.out(1.2)'},14.0);
      tl.to('#m2-intro',{opacity:0,duration:.35},20.3);
      tl.from('#c2-preview',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},24.4);
      tl.from('#pvr-1',{x:20,opacity:0,duration:.4},24.9);
      tl.from('#pvr-2',{x:20,opacity:0,duration:.4},26.0);
      tl.from('#pvr-3',{x:20,opacity:0,duration:.4},27.2);
      tl.from('#c2-word',{scale:.9,opacity:0,duration:.5},29.2);
      tl.to('#sc-three > .scene-inner',{opacity:0,duration:.4},30.78);

      /* m03 31.18–43.40：连拍 33.34 → 命令 36.60 → 四第二秒 40.47 */
      tl.fromTo('#sc-snap4 > .scene-inner',{opacity:0},{opacity:1,duration:.5},31.18);
      tl.from('#c3-ask',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},31.6);
      tl.to('#c3-ask',{opacity:0,duration:.3},36.1);
      tl.from('#c3-cmd',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},36.4);
      tl.to('#c3-cmd',{opacity:0,duration:.3},40.0);
      tl.from('#c3-four',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},40.3);
      tl.from('#c3-four i',{scale:.6,opacity:0,duration:.35,stagger:.18,
                ease:'back.out(1.5)'},40.7);
      tl.to('#sc-snap4 > .scene-inner',{opacity:0,duration:.4},43.00);

      /* m04 43.40–85.42：接触表 43.4 → 三判定 45.68/47.48/52.88 → 成本 57.3 */
      tl.fromTo('#sc-contact4 > .scene-inner',{opacity:0},{opacity:1,duration:.5},43.40);
      tl.from('#contact4-img',{scale:.96,opacity:0,duration:.6},44.0);
      tl.from('#vd-b',{opacity:0,duration:.5},45.8);
      tl.from('#vd-g',{opacity:0,duration:.5},47.6);
      tl.from('#vd-r',{opacity:0,duration:.5},53.0);
      tl.to('#m4-sheet',{opacity:0,duration:.4},56.9);
      tl.from('#cost-eq',{y:24,opacity:0,duration:.6,ease:'back.out(1.15)'},64.5);
      tl.from('#cost-waste',{opacity:0,duration:.6},69.8);
      tl.from('#cost-last',{opacity:0,duration:.6},73.4);
      tl.from('#cost-fear',{scale:.92,opacity:0,duration:.6,ease:'back.out(1.4)'},80.2);
      tl.from('#cost-topic',{opacity:0,duration:.6},83.6);
      tl.to('#sc-contact4 > .scene-inner',{opacity:0,duration:.4},85.02);

      /* m05 85.42–136.14：双钟 → 登记 96.28/WAAPI 107.02 → 红机制 114.96 → 结论 127.86 */
      tl.fromTo('#sc-clocks > .scene-inner',{opacity:0},{opacity:1,duration:.5},85.42);
      tl.from('#ask-q',{y:18,opacity:0,duration:.5},85.9);
      tl.from('#ask-a',{y:18,opacity:0,duration:.6,ease:'back.out(1.3)'},87.4);
      tl.from('#clk-wall',{x:-50,opacity:0,duration:.6,ease:'back.out(1.2)'},93.8);
      tl.from('#clk-vs',{opacity:0,duration:.4},94.6);
      tl.from('#clk-axis',{x:50,opacity:0,duration:.6,ease:'back.out(1.2)'},94.8);
      tl.to('#m5-ask',{opacity:0,duration:.4},96.2);
      tl.from('#mc-ok',{y:30,opacity:0,duration:.6,ease:'back.out(1.15)'},96.6);
      tl.from('#mc-ok .mc-l',{x:24,opacity:0,duration:.45,stagger:.5},98.2);
      tl.from('#mc-waapi',{opacity:0,duration:.6},107.2);
      tl.from('#mc-bad',{y:30,opacity:0,duration:.6,ease:'back.out(1.15)'},115.3);
      tl.from('#mc-bad .mc-code',{opacity:0,duration:.5},116.4);
      tl.from('#mc-badrows span',{opacity:0,duration:.4,stagger:.5},123.0);
      tl.from('#mc-result',{y:24,opacity:0,duration:.6,ease:'back.out(1.15)'},128.2);
      tl.to('#sc-clocks > .scene-inner',{opacity:0,duration:.4},135.74);

      /* m06 136.14–158.82：实验 136.14 → frame10 144.3 → 读数 147.26/151.30 → 收束 155.06 */
      tl.fromTo('#sc-slow > .scene-inner',{opacity:0},{opacity:1,duration:.5},136.14);
      tl.from('#c6-exp',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},136.5);
      tl.to('#c6-exp',{opacity:0,duration:.3},144.0);
      tl.from('#c6-read',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},144.5);
      tl.from('#rd-blue',{opacity:0,duration:.5},147.4);
      tl.from('#rd-red',{opacity:0,duration:.5},151.4);
      tl.from('#c6-word',{scale:.92,opacity:0,duration:.5},155.3);
      tl.to('#sc-slow > .scene-inner',{opacity:0,duration:.4},158.42);

      /* m07 158.82–191.80：平反＋player 回切 160.3 → 黑户 166.7 → 网页 171.3 → 求解 179.84 */
      tl.fromTo('#sc-css > .scene-inner',{opacity:0},{opacity:1,duration:.5},158.82);
      tl.from('#c7-clear',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},159.2);
      tl.to('#m7-term',{opacity:0,duration:.35},166.0);
      tl.from('#who-bad',{y:26,opacity:0,duration:.6,ease:'back.out(1.15)'},167.0);
      tl.from('#who-web',{y:26,opacity:0,duration:.6,ease:'back.out(1.15)'},171.0);
      tl.from('#who-web .wchip',{opacity:0,duration:.4,stagger:.18},175.8);
      tl.from('#who-solve',{y:26,opacity:0,duration:.6,ease:'back.out(1.15)'},180.2);
      tl.from('#sv-1',{opacity:0,duration:.5},180.8);
      tl.from('#sv-2',{opacity:0,duration:.5},183.6);
      tl.from('#sv-3',{opacity:0,duration:.6},187.0);
      tl.to('#sc-css > .scene-inner',{opacity:0,duration:.4},191.40);

      /* m08 191.80–216.80：契约三件 194.22 → seek 回切 200.5 → 猫 208.96/212.88 */
      tl.fromTo('#sc-contract > .scene-inner',{opacity:0},{opacity:1,duration:.5},191.80);
      tl.from('#m8-pact .kicker-static',{y:18,opacity:0,duration:.5},192.3);
      tl.from('#pc-1',{y:30,opacity:0,duration:.55,ease:'back.out(1.15)'},194.4);
      tl.from('#pc-2',{y:30,opacity:0,duration:.55,ease:'back.out(1.15)'},195.8);
      tl.from('#pc-3',{y:30,opacity:0,duration:.55,ease:'back.out(1.15)'},197.4);
      tl.from('#pc-word',{scale:.92,opacity:0,duration:.55},201.8);
      tl.to('#m8-pact',{opacity:0,duration:.35},204.8);
      tl.from('#c8-seek',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},205.3);
      tl.to('#m8-term',{opacity:0,duration:.35},209.8);
      tl.from('#cat-q',{y:22,opacity:0,duration:.6},210.0);
      tl.from('#catr-1',{x:-40,opacity:0,duration:.55,ease:'back.out(1.2)'},212.4);
      tl.from('#catr-2',{x:40,opacity:0,duration:.55,ease:'back.out(1.2)'},214.6);
      tl.to('#sc-contract > .scene-inner',{opacity:0,duration:.4},216.40);

      /* m09 216.80–228.40：preview/snapshot 分工 */
      tl.fromTo('#sc-preview > .scene-inner',{opacity:0},{opacity:1,duration:.5},216.80);
      tl.from('#m9-job .kicker-static',{y:18,opacity:0,duration:.5},217.2);
      tl.from('#jb-pv',{y:28,opacity:0,duration:.6,ease:'back.out(1.15)'},219.2);
      tl.from('#jb-arrow',{opacity:0,duration:.5},223.4);
      tl.from('#jb-snap',{y:28,opacity:0,duration:.6,ease:'back.out(1.15)'},223.8);
      tl.to('#sc-preview > .scene-inner',{opacity:0,duration:.4},228.00);

      /* m10 228.40–258.59：两道闸 → 红块案例 245.62 → 金句 251.64 */
      tl.fromTo('#sc-check > .scene-inner',{opacity:0},{opacity:1,duration:.5},228.40);
      tl.from('#m10-job .kicker-static',{y:18,opacity:0,duration:.5},228.9);
      tl.from('#gt-machine',{x:-40,opacity:0,duration:.6,ease:'back.out(1.15)'},230.0);
      tl.from('#gt-eye',{x:40,opacity:0,duration:.6,ease:'back.out(1.15)'},230.0);
      tl.from('#gt-case',{y:22,opacity:0,duration:.6},245.9);
      tl.from('#gt-word',{scale:.94,opacity:0,duration:.6,ease:'back.out(1.2)'},251.9);
      tl.to('#sc-check > .scene-inner',{opacity:0,duration:.4},258.19);

      /* m11 258.59–282.78：at 264.0 → frames 268.62 → 接触表 276.28 */
      tl.fromTo('#sc-shot1 > .scene-inner',{opacity:0},{opacity:1,duration:.5},258.59);
      tl.from('#c11-at',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},259.0);
      tl.to('#c11-at',{opacity:0,duration:.3},267.8);
      tl.from('#c11-frames',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},268.1);
      tl.to('#c11-frames',{opacity:0,duration:.3},275.6);
      tl.from('#c11-sheet',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},275.9);
      tl.to('#sc-shot1 > .scene-inner',{opacity:0,duration:.4},282.38);

      /* m12 282.78–296.60：zoom 284.72 → 裁图 289.2 → 报错 293.5/295.78 */
      tl.fromTo('#sc-zoom > .scene-inner',{opacity:0},{opacity:1,duration:.5},282.78);
      tl.from('#c12-zoom',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},283.1);
      tl.to('#c12-zoom',{opacity:0,duration:.3},288.3);
      tl.from('#c12-err',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},288.5);
      tl.to('#sc-zoom > .scene-inner',{opacity:0,duration:.4},296.20);

      /* m13 296.60–325.24：三必拍 304.02/306.58/313.14 → 清扫 317.62 */
      tl.fromTo('#sc-where > .scene-inner',{opacity:0},{opacity:1,duration:.5},296.60);
      tl.from('#m13-where .kicker-static',{y:18,opacity:0,duration:.5},297.0);
      tl.from('#wh-1',{y:28,opacity:0,duration:.55,ease:'back.out(1.15)'},304.2);
      tl.from('#wh-2',{y:28,opacity:0,duration:.55,ease:'back.out(1.15)'},306.8);
      tl.from('#wh-3',{y:28,opacity:0,duration:.55,ease:'back.out(1.15)'},313.4);
      tl.from('#wh-clean',{y:22,opacity:0,duration:.6},318.0);
      tl.to('#sc-where > .scene-inner',{opacity:0,duration:.4},324.84);

      /* m14 325.24–367.98：洋葱皮能力 331.32 → 采样 346.26 → 报告终端 356.3/items 365.48 */
      tl.fromTo('#sc-keyframes > .scene-inner',{opacity:0},{opacity:1,duration:.5},325.24);
      tl.from('#m14-onion .kicker-static',{y:18,opacity:0,duration:.5},325.7);
      tl.fromTo('#m14-onion .onion-card',{opacity:0},{opacity:1,duration:.4},331.0);
      tl.from('#on-cmd',{opacity:0,duration:.55},331.6);
      tl.from('#on-l',{opacity:0,duration:.6},334.8);
      tl.from('#on-spec .os-chip',{y:18,opacity:0,duration:.45,stagger:.5},346.6);
      tl.to('#m14-onion',{opacity:0,duration:.4},355.4);
      tl.from('#c14-report',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},355.8);
      tl.from('#rpr-1',{x:20,opacity:0,duration:.4},358.3);
      tl.from('#rpr-2',{x:20,opacity:0,duration:.4},359.1);
      tl.from('#rpr-3',{x:20,opacity:0,duration:.4},359.9);
      tl.from('#rpr-items',{scale:.7,opacity:0,duration:.6,ease:'back.out(1.5)'},365.6);
      tl.to('#sc-keyframes > .scene-inner',{opacity:0,duration:.4},367.58);

      /* m15 367.98–421.02：没户口 370.14 → 硬报错 382.38 → 刁 393.84 → 洋葱公道 408.60 → 户口 418.56 */
      tl.fromTo('#sc-blackhouse > .scene-inner',{opacity:0},{opacity:1,duration:.5},367.98);
      tl.from('#c15-noaccount',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},368.4);
      tl.to('#c15-noaccount',{opacity:0,duration:.3},376.6);
      tl.from('#c15-shotit',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},376.9);
      tl.to('#c15-shotit',{opacity:0,duration:.3},381.7);
      tl.from('#c15-near',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},388.8);
      tl.to('#m15-term',{opacity:0,duration:.4},391.4);
      tl.fromTo('#m15-sneak .sneak-card',{opacity:0},{opacity:1,duration:.4},391.6);
      tl.from('#sn-h',{y:18,opacity:0,duration:.5},391.8);
      tl.from('#sn-1',{opacity:0,duration:.6},392.4);
      tl.from('#sn-2',{opacity:0,duration:.6},398.0);
      tl.from('#sn-3',{opacity:0,duration:.6},404.0);
      tl.to('#m15-sneak',{opacity:0,duration:.4},408.3);
      tl.from('#c15-fair',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},408.7);
      tl.from('#c15-hukou',{scale:.9,opacity:0,duration:.6,ease:'back.out(1.3)'},418.7);
      tl.to('#sc-blackhouse > .scene-inner',{opacity:0,duration:.4},420.62);

      /* m16 421.02–457.36：两方案 422.42 → compare 终端 430.8 → 读图 435.74 → 逗号脾气 450.28 */
      tl.fromTo('#sc-compare > .scene-inner',{opacity:0},{opacity:1,duration:.5},421.02);
      tl.from('#m16-two .kicker-static',{y:18,opacity:0,duration:.5},421.5);
      tl.from('#th-a',{x:-40,opacity:0,duration:.55,ease:'back.out(1.2)'},422.6);
      tl.from('#th-plus',{opacity:0,duration:.4},423.4);
      tl.from('#th-b',{x:40,opacity:0,duration:.55,ease:'back.out(1.2)'},423.8);
      tl.from('#th-cmd',{opacity:0,duration:.55},426.8);
      tl.to('#m16-two',{opacity:0,duration:.4},430.2);
      tl.from('#c16-read',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},435.8);
      tl.to('#c16-read',{opacity:0,duration:.3},449.9);
      tl.from('#c16-label',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},450.2);
      tl.to('#sc-compare > .scene-inner',{opacity:0,duration:.4},456.96);

      /* m17 457.36–493.06：grade 459.76 → 踩坑终端 467.8/警告 481.30 → present 487.66 */
      tl.fromTo('#sc-grade > .scene-inner',{opacity:0},{opacity:1,duration:.5},457.36);
      tl.from('#c17-what',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},458.0);
      tl.to('#c17-what',{opacity:0,duration:.3},467.4);
      tl.from('#c17-pit',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},467.7);
      tl.from('#wl-1',{opacity:0,duration:.5},478.8);
      tl.from('#wl-2',{opacity:0,duration:.5},480.2);
      tl.to('#m17-term',{opacity:0,duration:.4},487.3);
      tl.fromTo('#m17-present .present-card',{opacity:0},{opacity:1,duration:.4},487.8);
      tl.from('#pr-h',{scale:.8,opacity:0,duration:.6,ease:'back.out(1.5)'},488.0);
      tl.from('#pr-l',{y:18,opacity:0,duration:.55},489.6);
      tl.from('#pr-sub',{opacity:0,duration:.5},491.6);
      tl.to('#sc-grade > .scene-inner',{opacity:0,duration:.4},492.66);

      /* m18 493.06–520.62：三句话 495.52/503.34/509.96 */
      tl.fromTo('#sc-recap > .scene-inner',{opacity:0},{opacity:1,duration:.5},493.06);
      tl.from('#m18-recap .kicker-static',{y:18,opacity:0,duration:.5},493.6);
      tl.from('#rr-1',{x:-50,opacity:0,duration:.6,ease:'back.out(1.15)'},495.8);
      tl.from('#rr-2',{x:-50,opacity:0,duration:.6,ease:'back.out(1.15)'},503.6);
      tl.from('#rr-3',{x:-50,opacity:0,duration:.6,ease:'back.out(1.15)'},510.2);
      tl.to('#sc-recap > .scene-inner',{opacity:0,duration:.4},520.22);

      /* m19 520.62–544.30：三行动 523.16/524.94/530.96 → CSS 放心 535.94 */
      tl.fromTo('#sc-action > .scene-inner',{opacity:0},{opacity:1,duration:.5},520.62);
      tl.from('#m19-action .kicker-static',{y:18,opacity:0,duration:.5},521.1);
      tl.from('#ac-1',{x:-40,opacity:0,duration:.55},523.4);
      tl.from('#ac-2',{x:-40,opacity:0,duration:.55},525.2);
      tl.from('#ac-3',{x:-40,opacity:0,duration:.55},531.2);
      tl.from('#ac-ps',{opacity:0,duration:.6},536.2);
      tl.to('#sc-action > .scene-inner',{opacity:0,duration:.4},543.90);

      /* m20 544.30–TOTAL：预告 → render 556.38 → 道别 556.56 */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},544.30);
      tl.from('#nx-h',{y:18,opacity:0,duration:.5},544.8);
      tl.from('#nx-l1',{opacity:0,duration:.6},547.0);
      tl.from('#nx-l2',{opacity:0,duration:.6},550.6);
      tl.from('#nx-card',{scale:.8,opacity:0,duration:.55,ease:'back.out(1.5)'},553.4);
      tl.to('#m20-next',{opacity:0,duration:.35},556.15);
      tl.from('#bye',{y:24,opacity:0,duration:.7},556.5);
"""

# ---------- 底部字幕轨道 ----------
# time_offset：faster-whisper 吞句间停顿致字幕偏早；hf-01..06 实测
# 0.28/0.37/0.29/0.30/0.29/0.31。hf-07 v2 段级重建母带经
# oneoffs/measure_offset.py 实测 onset 配对中位数 +315.1ms（53/69），取 0.31。
frag = char_track(cues, chars, THEME.accent, time_offset=0.31)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/hf-07-yeyang.wav", total),
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
io.open(P.index_html, "w", encoding="utf-8", newline="\n").write(html)
mode = "仅概念卡（--cards-only）" if CARDS_ONLY else "正式版（含录屏 clip）"
print("已生成 index.html（%.2f 秒，%d 幕，%d 句，%s）"
      % (total, len(SCENES), len(cues), mode))
