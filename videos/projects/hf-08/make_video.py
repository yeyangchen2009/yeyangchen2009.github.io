# -*- coding: utf-8 -*-
"""hf-08《render：无头 Chrome 怎样把网页烤成 MP4》分镜生成器。

20 幕严格首尾相接（611.51s 母带，293 句 cues），GitHub Dark 蓝主色
事实集（与 hf-07 同视觉系，金＝指纹/金句）。每幕拍点锚 cues 实测词戳。
真机素材 18 个文件、19 个 clip 引用（4 段录屏母带切 6 short＋13 张
freeze 回放帧＋1 张 contact 拼图）。正式版已过 check（0 error，基线
22 warning）；唯一缺位 sw-render.mp4 是冷态 t0（开机首 render），
两 clip 自动降级注释占位，正式 render 前归位重生成即可。

音频用 media/hf-08-yeyang-patched.wav（oneoffs/patch_audio_54.py：
入镜尾报 54.2s，句级补丁把「五十二秒」换成「五十四秒」，窗外不动）。

真机素材位（#609 代录清单，拍法见 oneoffs/RECORD-NOTES.md）：
  media/shorts/hash6-run.mp4    m02 Get-FileHash 六连
  media/freezes/hash6-run.png   m02 六连尾帧 freeze
  media/freezes/frames-dir.png  m04 captured-frames 390 JPG
  media/freezes/debug-tree.png  m06 --debug 目录树
  media/freezes/perf-ledger.png m06/m16 perf-summary 阶段账本
  media/freezes/pngseq-dir.png  m07 png-sequence 产物
  media/shorts/sw-render.mp4    m09 软件路真机 68s 全跑（★冷态 t0 待录）
  media/freezes/gate-multi.png  m09 multi_worker streaming gate 关
  media/shorts/hw-render.mp4    m09 硬件路真机 54.2s 全跑（头尾各取一段）
  media/freezes/gate-stream.png m09 capture_streaming + drawelement
  media/freezes/hf07-timing.png m10 hf-07 长片 Timing（16777/41m43）
  media/freezes/worker-sizing.png m11 workerSizing 日志字段
  media/freezes/src-blackbar.png m12 源码黑条注释＋24GB 地板
  media/shorts/badlint-run.mp4  m14 坏工程 lint 2 error 照烤
  media/artifacts/redblock-30-150.png m14 第30/150帧红块位置 contact
  media/freezes/strict-abort.png m14 --strict exit 1
  media/freezes/missing-audio.png m15 缺音轨拦截
  media/freezes/no-timeline-warn.png m15 45s 轮询 warning

用法：
  python make_video.py --cards-only   # 仅概念卡，先过 check
  python make_video.py                # 正式版（含录屏 clip）
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
    name="githubdark-blue-hf08",
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

# m01 实验钩子 0.00–1.24
Scene("sc-open", 0.00, 1.24, """
          <div class="lab" id="lab">
            <div class="lab-dots"><i class="b"></i><i class="g"></i><i class="r"></i></div>
            <div class="lab-word">先做一个实验</div>
          </div>"""),

# m02 六连烤指纹 1.24–29.42
Scene("sc-sixhash", 1.24, 29.42, """
          <div class="stage" id="m2-table">
            <div class="kicker-static">同一份工程，烤六次 —— 十三秒，黑底上五道白闪</div>
            <div class="ht">
              <div class="ht-row ht-head"><span>产物</span><span>烤法</span><span>sha256</span><span></span></div>
              <div class="ht-row" id="ht-1"><span class="fname">soft-a.mp4</span><span class="ftag">软件 GPU</span><span class="fhash">2057d037…c6c5a83</span><span class="ftick">✓</span></div>
              <div class="ht-row" id="ht-2"><span class="fname">soft-b.mp4</span><span class="ftag">软件 GPU</span><span class="fhash">2057d037…c6c5a83</span><span class="ftick">✓</span></div>
              <div class="ht-row" id="ht-old"><span class="fname">1015-old.mp4</span><span class="ftag amber-t">六天前旧档</span><span class="fhash">2057d037…c6c5a83</span><span class="ftick">✓</span></div>
              <div class="ht-row" id="ht-w1"><span class="fname">w1.mp4</span><span class="ftag">软件单 worker</span><span class="fhash">2057d037…c6c5a83</span><span class="ftick">✓</span></div>
              <div class="ht-row" id="ht-hwa"><span class="fname">hw-a.mp4</span><span class="ftag blue2-t">硬件 GPU 单 worker</span><span class="fhash">2057d037…c6c5a83</span><span class="ftick">✓</span></div>
              <div class="ht-row" id="ht-hwb"><span class="fname">hw-b.mp4</span><span class="ftag blue2-t">硬件 GPU 单 worker</span><span class="fhash">2057d037…c6c5a83</span><span class="ftick">✓</span></div>
            </div>
            <div class="goldword-sm" id="m2-word">六个指纹，同一个文件</div>
          </div>

          <div class="termwrap" id="m2-term">
            <div class="gk rightcard" id="c2-same">
              <div class="gk-tag">烤两遍，摆一块儿算指纹</div>
              <div class="cmdbox">Get-FileHash run-a.mp4, run-b.mp4</div>
              <div class="rule-foot">两个哈希，逐字符一模一样</div>
            </div>
            <div class="gk rightcard" id="c2-old">
              <div class="gk-tag">把六天前的旧文件翻出来</div>
              <div class="rule-cn">再比一次 —— 还是<b class="gold-t">同一个指纹</b></div>
              <div class="rule-foot">跨六天，容器层不写时间戳</div>
            </div>
          </div>"""),

# m03 渲染的名声＋本集三问 29.42–56.86
Scene("sc-fame", 29.42, 56.86, """
          <div class="stage" id="m3-fame">
            <div class="kicker-static" id="m3-k">「渲染」这两个字，名声不太好</div>
            <div class="fame-rows">
              <div class="fame-in" id="fame-in">同一份工程</div>
              <div class="fame-outs" id="fame-outs">
                <span class="fo" id="fo-1">今天烤<em>?</em></span>
                <span class="fo" id="fo-2">明天烤<em>?</em></span>
                <span class="fo" id="fo-3">这台机器<em>?</em></span>
                <span class="fo" id="fo-4">那台机器<em>?</em></span>
              </div>
            </div>
            <div class="fame-but" id="fame-but">而这里 —— 软件 GPU 和硬件 GPU，两条完全不同的路<br><b class="gold-t">烤出来逐字节相同</b></div>
          </div>

          <div class="termwrap" id="m3-term">
            <div class="gk rightcard" id="c3-q1">
              <div class="gk-tag">这一集，真烤</div>
              <div class="rule-cn">无头 Chrome 怎样把网页烤成 <span class="mono gold-t">MP4</span></div>
            </div>
            <div class="gk rightcard" id="c3-q2">
              <div class="gk-tag">上万帧</div>
              <div class="rule-cn">要烤多久？</div>
            </div>
            <div class="gk rightcard" id="c3-q3">
              <div class="gk-tag">烤崩了</div>
              <div class="rule-cn">又怎么查？</div>
            </div>
          </div>"""),

# m04 不是录屏，是逐格求解 56.86–106.86
Scene("sc-solve", 56.86, 106.86, """
          <div class="stage" id="m4-record">
            <div class="kicker-static">先说清楚一件事</div>
            <div class="rec-cmp">
              <div class="rec-card" id="rec-bad">
                <div class="rec-h red-t">播放页面，顺手录屏</div>
                <div class="rec-l">录屏是<b>墙钟</b>的生意：播放一遍，就老老实实花十三秒</div>
                <div class="rec-l">机器卡一下、后台忙一下 —— 录进来的全是<b class="red-t">现场实况</b></div>
              </div>
              <div class="rec-vs" id="rec-vs">render 不认这个</div>
            </div>
          </div>

          <div class="stage" id="m4-math">
            <div class="kicker-static">它把时间轴当成一道数学题</div>
            <div class="eq-row" id="eq-row">
              <span class="eq-i">每秒 30 格</span><span class="eq-x">×</span>
              <span class="eq-i">13 秒</span><span class="eq-x">＝</span>
              <span class="eq-out">390 格</span>
            </div>
            <div class="solve-steps">
              <div class="ss" id="ss-1"><b>seek</b> 到这个时刻</div>
              <div class="ss-arrow">→</div>
              <div class="ss" id="ss-2">等浏览器把画面画稳</div>
              <div class="ss-arrow">→</div>
              <div class="ss" id="ss-3">截一张图</div>
            </div>
            <div class="solve-frames" id="solve-frames">
              <span class="sf" id="sf-1">#1</span>
              <span class="sf" id="sf-100">#100</span>
              <span class="sf" id="sf-390">#390</span>
            </div>
            <div class="solve-note" id="solve-note">谁先求谁后求无所谓，求多少次，答案都一样</div>
          </div>

          <div class="stage" id="m4-two">
            <div class="twopaths">
              <div class="tp" id="tp-v">
                <div class="tp-h blue2-t">390 张静态图</div>
                <div class="tp-l">交给编码器，压成视频流</div>
              </div>
              <div class="tp-plus">＋</div>
              <div class="tp" id="tp-a">
                <div class="tp-h green-t">声音</div>
                <div class="tp-l">走另一条路<br>单独处理、按时长归一</div>
              </div>
            </div>
            <div class="eq-out" id="tp-out">两路合成一个 <span class="mono gold-t">MP4</span></div>
          </div>"""),

# m05 确定性的根 106.86–124.60
Scene("sc-root", 106.86, 124.60, """
          <div class="stage" id="m5-root">
            <div class="kicker-static">视频最怕的不是丑，是<b class="red-t">不确定</b></div>
            <div class="root-fn">
              <div class="fn-machine" id="fn-machine">
                <span class="fn-in">时间码</span>
                <span class="fn-arrow">→</span>
                <span class="fn-box">f()</span>
                <span class="fn-arrow">→</span>
                <span class="fn-out">这一帧的画面</span>
              </div>
              <div class="fn-rule" id="fn-rule">每一帧的画面，只由时间码决定</div>
            </div>
            <div class="root-clock" id="root-clock">
              <span class="clk-banned">墙钟</span>
              <span class="clk-note">被彻底关在<b class="gold-t">烤炉外面</b></span>
            </div>
            <div class="goldword-sm big" id="m5-word">所以同一份工程，才敢烤六次，六个指纹完全相同</div>
          </div>"""),

# m06 --debug 流水线 124.60–170.70
Scene("sc-pipe", 124.60, 170.70, """
          <div class="termwrap" id="m6-term">
            <div class="gk rightcard" id="c6-debug">
              <div class="gk-tag">烤一次经过几道手？</div>
              <div class="cmdbox">hyperframes render . <b class="blue2-t">--debug</b></div>
              <div class="rule-foot">开关一开，中间产物一件不扔</div>
            </div>
            <div class="gk rightcard" id="c6-compile">
              <div class="gk-tag">① 编译</div>
              <div class="rule-cn">工程＋动画运行时，打包成一个自足的页面</div>
              <div class="rule-foot">附一份媒体清单 summary.json</div>
            </div>
            <div class="gk rightcard" id="c6-probe">
              <div class="gk-tag">② 无头 Chrome 探路</div>
              <div class="rule-cn">看这台机器的硬件 GPU 能不能用</div>
            </div>
            <div class="gk rightcard" id="c6-calib">
              <div class="gk-tag">③ 校准：真截五帧</div>
              <div class="cmdbox" style="font-size:26px">frame 0 / 97 / 195 / 292 / 389</div>
              <div class="rule-foot">量 p95 截一帧多久，给派活提供依据</div>
            </div>
            <div class="gk rightcard" id="c6-workers">
              <div class="gk-tag">④ 派活：每个 worker 领一段帧号</div>
              <div class="rule-cn">各开一个无头 Chrome，逐帧 seek、截图，图片落盘</div>
            </div>
            <div class="gk rightcard" id="c6-encode">
              <div class="gk-tag">⑤ 编码与合成</div>
              <div class="rule-cn">390 张图先压成无声视频，再跟声音合到一起</div>
            </div>
          </div>"""),

# m07 源视频抽帧缓存＋png-sequence 170.70–201.08
Scene("sc-cache", 170.70, 201.08, """
          <div class="stage" id="m7-extract">
            <div class="kicker-static">工程里还嵌了视频素材？</div>
            <div class="ex-rows">
              <div class="ex-card" id="ex-1">
                <div class="ex-h blue2-t">烤之前多一道抽帧</div>
                <div class="ex-l">把素材也变成一张张图</div>
              </div>
              <div class="ex-card" id="ex-2">
                <div class="ex-h green-t">按内容做缓存</div>
                <div class="ex-l">同一份素材抽过一次，下回直接用，不重复劳动</div>
                <div class="cmdbox" style="font-size:26px;margin-top:14px">--frames-cache-dir</div>
                <div class="rule-foot">缓存能挪出系统盘，盘紧张的用得上</div>
              </div>
            </div>
          </div>

          <div class="stage" id="m7-png">
            <div class="kicker-static">更彻底的一步：停在烤炉的原始产品</div>
            <div class="cmdbox big" id="png-cmd">--format png-sequence</div>
            <div class="png-rows">
              <span class="pkg" id="png-390">390 张 PNG</span>
              <span class="pkg-plus">＋</span>
              <span class="pkg" id="png-audio">audio.m4a</span>
              <span class="pkg-eq" id="png-size">共 3.2 MB</span>
            </div>
            <div class="solve-note" id="png-note">不想要 MP4、只要图 —— 一眼看见三百九十张原始帧</div>
          </div>"""),

# m08 两条路桥段 201.08–205.16
Scene("sc-fork", 201.08, 205.16, """
          <div class="stage" id="m8-fork">
            <div class="fork-q" id="fork-q">那三百九十张图，是怎么截出来的？</div>
            <div class="fork-rows">
              <div class="fork-card soft" id="fork-soft"><b>第一条</b>截图法<br>软件 GPU</div>
              <div class="fork-card hard" id="fork-hard"><b>第二条</b>硬件路</div>
            </div>
          </div>"""),

# m09 两条捕获路径 205.16–254.82
Scene("sc-paths", 205.16, 254.82, """
          <div class="stage" id="m9-soft-intro">
            <div class="path-intro soft">
              <div class="pi-h" id="pi-soft-h">第一条：截图法，软件 GPU 上场</div>
              <div class="pi-l" id="pi-soft-1">无头 Chrome 用 CPU <b>模拟一块显卡</b>，名字叫 <span class="mono gold-t">SwiftShader</span></div>
              <div class="pi-l" id="pi-soft-2">每个时刻，用浏览器自带的截图命令把画面截下来</div>
            </div>
          </div>

          <div class="termwrap" id="m9-term-soft">
            <div class="gk rightcard" id="c9-sw-par">
              <div class="gk-tag">可以多个 worker 并行</div>
              <div class="rule-cn">三个无头 Chrome 同时开工，各领一段帧号</div>
            </div>
            <div class="gk rightcard" id="c9-sw-disk">
              <div class="gk-tag">图先全部存到盘上</div>
              <div class="rule-cn">等三家都交活，再统一编码</div>
              <div class="rule-foot hot">并行截图，不能边截边编</div>
            </div>
            <div class="gk rightcard" id="c9-hw-probe">
              <div class="gk-tag">第二条：硬件路</div>
              <div class="rule-cn">先探一次硬件 GPU —— 集显探活成功</div>
            </div>
            <div class="gk rightcard" id="c9-hw-de">
              <div class="gk-tag">换一套捕获方式</div>
              <div class="rule-cn">不让浏览器「截图」，让 <span class="mono gold-t">Chrome 合成器</span>直接把画面交出来</div>
              <div class="cmdbox" style="font-size:25px">captureMode = drawElement</div>
            </div>
            <div class="gk rightcard" id="c9-hw-1">
              <div class="gk-tag">这条路，本机永远是一个 worker</div>
              <div class="rule-cn">好处：<b class="green-t">边抓边编码，抓完也编完了</b></div>
            </div>
          </div>"""),

# m10 时间账 254.82–292.22
Scene("sc-time", 254.82, 292.22, """
          <div class="stage" id="m10-small">
            <div class="kicker-static">十三秒的小工程，时间账报一下</div>
            <div class="time-rows">
              <div class="tr" id="tr-1"><span class="tr-name">软件路 · 首跑</span><span class="tr-val red-t">68 秒</span><span class="tr-note">光开浏览器、试截几帧就花掉 16 秒</span></div>
              <div class="tr" id="tr-2"><span class="tr-name">软件路 · 第二回</span><span class="tr-val amber-t">56 秒以内</span><span class="tr-note">浏览器热了</span></div>
              <div class="tr" id="tr-3"><span class="tr-name">硬件路</span><span class="tr-val green-t">52 秒</span><span class="tr-note">编码和抓帧重叠在一起</span></div>
            </div>
            <div class="solve-note" id="tr-note">小工程谁也快不到哪去，启动成本摊不开 —— 长片才见真章</div>
          </div>

          <div class="stage" id="m10-long">
            <div class="kicker-static">我上一个片子（hf-07）</div>
            <div class="long-stats">
              <div class="ls" id="ls-frames"><b>16,777</b>帧</div>
              <div class="ls" id="ls-cap"><b>39</b>分钟抓帧</div>
              <div class="ls" id="ls-total"><b>41 分 43 秒</b>全程</div>
              <div class="ls" id="ls-fps"><b>≈ 7.1</b>帧/秒</div>
            </div>
            <div class="goldword-sm" id="m10-word">硬件路单 worker —— 开烤之前，心里就有钟</div>
          </div>"""),

# m11 worker 是算出来的 292.22–330.90
Scene("sc-sizing", 292.22, 330.90, """
          <div class="stage" id="m11-calc">
            <div class="kicker-static">worker 的数量不是拍脑袋，是算出来的 —— 源码里的四笔账</div>
            <div class="calc-rows">
              <div class="cr" id="cr-1"><span class="cr-expr">CPU 核数 − 2</span><span class="cr-eq">= 6</span></div>
              <div class="cr" id="cr-2"><span class="cr-expr">总内存一半 ÷ 每 worker 1536 兆</span><span class="cr-eq">= 5</span></div>
              <div class="cr" id="cr-3"><span class="cr-expr">总帧数 ÷ 30</span><span class="cr-eq">= 13</span></div>
              <div class="cr" id="cr-4"><span class="cr-expr">再给内存堆留一笔账</span><span class="cr-eq">= 5</span></div>
            </div>
            <div class="calc-min" id="calc-min">四笔取最小，大工程还要再被一道系数压一压</div>
          </div>

          <div class="stage" id="m11-mine">
            <div class="kicker-static">八核、十六 G 内存的机器，实测日志</div>
            <div class="mine-rows">
              <div class="mr" id="mr-cpu">CPU 给 <b class="blue2-t">6</b></div>
              <div class="mr" id="mr-mem">内存给 <b class="blue2-t">5</b></div>
              <div class="mr" id="mr-frame">帧数给 <b class="blue2-t">13</b></div>
              <div class="mr" id="mr-final">最后压到 <b class="gold-t">3</b></div>
            </div>
            <div class="solve-note" id="mr-note">和烤的时候日志里报的数，一模一样</div>
            <div class="calc-min" id="mr-few">帧太少也不并行：不到 60 帧，直接一个 worker</div>
          </div>"""),

# m12 硬件路为什么钉死一个＋黑条事故 330.90–381.64
Scene("sc-why1", 330.90, 381.64, """
          <div class="stage" id="m12-layers">
            <div class="kicker-static">硬件路为什么偏偏钉死一个？这里有三层</div>
            <div class="ly-rows">
              <div class="ly" id="ly-1"><span class="ly-n">①</span><span>短工程帧少，并行连启动成本都赚不回来</span></div>
              <div class="ly" id="ly-2"><span class="ly-n">②</span><span>超过 <b class="gold-t">900 帧</b>，单 worker 边抓边编实测全面更快 —— 它主动把多 worker <b>反转</b>成一个</span></div>
              <div class="ly" id="ly-3"><span class="ly-n">③</span><span>三个硬件 Chrome 一起抓？功能真有 —— 门槛是 <b class="red-t">24 G 内存</b></span></div>
            </div>
          </div>

          <div class="termwrap" id="m12-term">
            <div class="gk rightcard" id="c12-why">
              <div class="gk-tag">为什么定这么高？</div>
              <div class="rule-cn">代码注释里留着<b class="gold-t">事故档案</b></div>
            </div>
            <div class="gk rightcard err" id="c12-bar">
              <div class="rule-head"><span class="rule-mark err">✕</span><b>竖直黑条</b></div>
              <div class="rule-cn hot">老版本在 16 G 机器上<br>开三个硬件实例</div>
              <div class="rule-cn">合成器的画面瓷砖被内存压力挤掉</div>
              <div class="rule-foot">抽检验证，又恰好漏看了那几格</div>
            </div>
            <div class="gk rightcard" id="c12-floor">
              <div class="gk-tag">打这以后</div>
              <div class="rule-cn">24 G 地板以下，只开单 worker</div>
              <div class="rule-foot">我这台 16 G，正好在线外</div>
            </div>
          </div>"""),

# m13 校准不是摆设 381.64–397.50
Scene("sc-calib", 381.64, 397.50, """
          <div class="stage" id="m13-calib">
            <div class="kicker-static">开烤前「挑五帧测一测」，不是摆设</div>
            <div class="calib-rows">
              <div class="clb" id="clb-rule">构图越贵，截一帧越慢</div>
              <div class="clb-costs">
                <span class="cc" id="cc-1">着色器转场 <em>×2</em></span>
                <span class="cc" id="cc-2">requestAnimationFrame <em>×1</em></span>
                <span class="cc" id="cc-3">iframe <em>+0.5</em></span>
              </div>
              <div class="clb-feedback" id="clb-feedback">实测耗时反过来调整 worker 数<br><b class="gold-t">防止浏览器合成器被活活饿死</b></div>
            </div>
          </div>"""),

# m14 lint 门控＋坏工程实验 397.50–448.12
Scene("sc-gate", 397.50, 448.12, """
          <div class="stage" id="m14-intro">
            <div class="kicker-static">再说门控：render 开烤前会自己先跑一遍 <span class="mono blue2-t">lint</span></div>
            <div class="gate-default">
              <div class="gd" id="gd-note">但注意 —— 默认设置下，lint 有 error，它<b class="red-t">并不拦</b></div>
            </div>
          </div>

          <div class="termwrap" id="m14-term">
            <div class="gk rightcard" id="c14-bad">
              <div class="gk-tag">我故意烤了一个坏工程</div>
              <div class="rule-cn">红方块用 <span class="mono" style="color:#ffa198">requestAnimationFrame</span><br>自己掐着表跑</div>
              <div class="rule-foot">上一集说过的墙钟黑户</div>
            </div>
            <div class="gk rightcard" id="c14-cont">
              <div class="gk-tag">lint 报了两个 error</div>
              <div class="rule-cn"><b class="gold-t">render 照样出片</b></div>
            </div>
            <div class="gk rightcard" id="c14-read1">
              <div class="gk-tag">拆开成片看帧</div>
              <div class="rule-cn">第一秒：红方块刚离开起点一点</div>
            </div>
            <div class="gk rightcard" id="c14-read2">
              <div class="gk-tag">第五秒</div>
              <div class="rule-cn">正好走到屏幕<b class="gold-t">正中</b> —— 匀速十秒一个来回，恰好在半程</div>
            </div>
            <div class="gk rightcard err" id="c14-strict">
              <div class="rule-head"><span class="rule-mark err">✕</span><b>想让它拦？</b></div>
              <div class="cmdbox">hyperframes render . <b class="blue2-t">--strict</b></div>
              <div class="rule-cn hot">lint 不过直接中止，一片不出</div>
            </div>
          </div>

          <div class="stage" id="m14-lock">
            <div class="lock-word" id="lock-word">墙钟动画真真切切烤进了 MP4，好坏照烤</div>
            <div class="goldword-sm big" id="lock-word2">check 零 error 是流程纪律 —— 是你给自己上的锁</div>
          </div>"""),

# m15 缺音轨拦截＋45s 坑 448.12–487.28
Scene("sc-block", 448.12, 487.28, """
          <div class="termwrap" id="m15-term">
            <div class="gk rightcard" id="c15-but">
              <div class="gk-tag">但「默认宽容」不等于什么都放</div>
              <div class="rule-cn">又试一个工程：音频文件根本不存在</div>
            </div>
            <div class="gk rightcard err" id="c15-block">
              <div class="rule-head"><span class="rule-mark err">✕</span><b>这一回它没客气</b></div>
              <div class="rule-cn">画面一路烤完，临到合成 —— 声音的源头是空的</div>
              <div class="cmdbox" style="font-size:25px;border-color:#6e2b2b;color:#ffa198">Render blocked: audio_processing_failed</div>
              <div class="rule-cn hot">输出会变成哑巴片 —— exit 1</div>
            </div>
            <div class="gk rightcard warn" id="c15-pit">
              <div class="rule-head"><span class="rule-mark warn">!</span><b>还有个小坑</b></div>
              <div class="rule-cn">没注册时间轴，又忘了贴 <span class="mono amber-t">data-no-timeline</span></div>
              <div class="rule-cn">render 死等时间轴注册，<b class="gold-t">最多等 45 秒</b>才放弃</div>
            </div>
            <div class="gk rightcard" id="c15-fix">
              <div class="gk-tag">纯静态页面</div>
              <div class="rule-cn">记得贴标记 —— 每烤一次<b class="green-t">省 45 秒</b></div>
            </div>
          </div>

          <div class="stage" id="m15-word">
            <div class="antithesis">
              <div class="at-line" id="at-1">宽容的是「画面有嫌疑」</div>
              <div class="at-line red-t" id="at-2">不宽容的是「少一条轨道」</div>
            </div>
          </div>"""),

# m16 烤崩三招＋超时参数 487.28–538.48
Scene("sc-crash", 487.28, 538.48, """
          <div class="stage" id="m16-three">
            <div class="kicker-static">真崩了怎么办？记住三样东西</div>
            <div class="crash3">
              <div class="cz" id="cz-1">
                <div class="cz-n">1</div>
                <div class="cz-h gold-t">--debug 目录</div>
                <div class="cz-l">第一现场：编译产物、<br>每帧的图、无声视频、<br>音频、<b>阶段账本</b>全在里面<br>—— 先看时间死在哪一段</div>
              </div>
              <div class="cz" id="cz-2">
                <div class="cz-n">2</div>
                <div class="cz-h blue2-t">worker 静默退出</div>
                <div class="cz-l">八成是内存问题<br>—— 它自己都会建议你<br><span class="mono">横杠 w</span> 降到一个 worker<br>隔离重烤</div>
              </div>
              <div class="cz" id="cz-3">
                <div class="cz-n">3</div>
                <div class="cz-h green-t">断点续烤</div>
                <div class="cz-l">长片烤到一半崩了<br>不必从头哭：分段捕获的<br>结果可以保留，加参数<br>接着烤</div>
              </div>
            </div>
          </div>

          <div class="stage" id="m16-timeouts">
            <div class="kicker-static">三道超时，各有各的开关，慢机器自己放宽</div>
            <div class="to-rows">
              <div class="to" id="to-1"><span class="to-name">浏览器开页面</span><span class="to-val">60 秒</span></div>
              <div class="to" id="to-2"><span class="to-name">协议通话</span><span class="to-val">300 秒</span></div>
              <div class="to" id="to-3"><span class="to-name">等就绪</span><span class="to-val">45 秒</span></div>
            </div>
            <div class="to-quality" id="to-q">画质分三等、格式有六种 —— 都在参数表里，留给发布前那一道</div>
          </div>"""),

# m17 八集闭环＋承诺验收 538.48–575.44
Scene("sc-loop", 538.48, 575.44, """
          <div class="stage" id="m17-chain">
            <div class="kicker-static">到这里，八集一条线闭环了</div>
            <div class="chain">
              <span class="ch" id="ch-2"><b>02</b>init 搭骨架</span>
              <span class="ch" id="ch-3"><b>03</b>网页摆上时间轴</span>
              <span class="ch" id="ch-4"><b>04</b>灵魂交给 seek</span>
              <span class="ch" id="ch-6"><b>06</b>配上声音</span>
              <span class="ch" id="ch-5"><b>05</b>check 把门</span>
              <span class="ch" id="ch-7"><b>07</b>每一帧看清楚</span>
              <span class="ch hot" id="ch-8"><b>08</b>render 出炉</span>
            </div>
            <div class="chain-note" id="chain-note">从一份 HTML 到一个 MP4 —— 没有黑箱，每一步都能看、能验、能复算</div>
          </div>

          <div class="stage" id="m17-promise">
            <div class="promise">
              <div class="pr-said" id="pr-said">第一集我就说，这东西最硬的承诺是确定性</div>
              <div class="pr-formula" id="pr-formula">同输入 · 同版本 <b class="gold-t">→</b> 同输出</div>
              <div class="pr-stamp" id="pr-stamp">六个指纹完全相同 —— 这就是那张承诺的验收单</div>
            </div>
          </div>"""),

# m18 行动件 575.44–590.98
Scene("sc-action", 575.44, 590.98, """
          <div class="stage" id="m18-action">
            <div class="kicker-static">行动件</div>
            <div class="acl">
              <div class="acl-row" id="ac-1"><span class="acl-n">①</span>挑一个你手上的短工程，真刀真枪 render 一回</div>
              <div class="acl-row" id="ac-2"><span class="acl-n">②</span>加上 <span class="mono gold-t">--debug</span>，打开那个目录，看看属于你的几百张图</div>
              <div class="acl-row" id="ac-3"><span class="acl-n">③</span>再烤一遍，自己算一次指纹，看它是不是一模一样</div>
            </div>
          </div>"""),

# m19 季终云端预告 590.98–608.90
Scene("sc-cloud", 590.98, 608.90, """
          <div class="stage" id="m19-cloud">
            <div class="nx-h" id="nx-h">第一季到此完结</div>
            <div class="cloud-idea" id="cloud-idea">HTML 能在本机烤，就能在<b class="gold-t">云端</b>烤</div>
            <div class="cloud-cmds" id="cloud-cmds">
              <span class="ccmd">cloud</span>
              <span class="ccmd">lambda</span>
              <span class="ccmd">cloud run</span>
            </div>
            <div class="cloud-l" id="cloud-l">把烤炉搬进机房，多台机器一起烤 —— 还有 benchmark 帮你挑配置</div>
            <div class="nx-card" id="nx-card">第二季：去云里烤片</div>
          </div>"""),

# m20 道别 608.90–611.51
Scene("sc-bye", 608.90, 611.51, """
          <div id="m20-bye">
            <div class="bye" id="bye">我是叶扬，我们下期见</div>
            <div class="finale-tag" id="finale-tag">SEASON 1 FINALE</div>
          </div>"""),
]

# ---------- 顶层录屏/真机图 clip（不可嵌套；放 scenes 之前＝下层） ----------
# 终端素材 1600x920 缩左 1120x644（.term fill）；artifacts 真机产物图
# 同位 contain（.shot）。视频段 data-media-start 取源内切点（源内秒）。
if CARDS_ONLY:
    VIDEOS = "      <!-- --cards-only：录屏/真机图 clip 待媒体到位后填入 -->"
else:
    VIDEOS = """      <!-- m02 1.24–29.42：Get-FileHash 六连真机 10.6–18.5，freeze 到 24.0。
           源内 16.0–23.9：PS 空提示→打字→21.8s 六行表全出（2026-10-22 母带） -->
      <video id="rec-hash6" class="clip term" data-start="10.60"
             data-duration="7.90" data-track-index="2" data-media-start="16.0"
             src="media/shorts/hash6-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-hash6" class="clip term" data-start="18.50"
           data-duration="5.50" src="media/freezes/hash6-run.png" alt="">

      <!-- m04 95.58–103.5：captured-frames 390 JPG 真机目录 -->
      <img id="img-frames" class="clip term" data-start="95.80"
           data-duration="7.70" src="media/freezes/frames-dir.png" alt="">

      <!-- m06 132–166：--debug 目录树＋perf-summary 阶段账本 -->
      <img id="img-debugtree" class="clip term" data-start="133.50"
           data-duration="15.00" src="media/freezes/debug-tree.png" alt="">
      <img id="img-perf" class="clip term" data-start="148.50"
           data-duration="17.80" src="media/freezes/perf-ledger.png" alt="">

      <!-- m07 193.5–200.2：png-sequence 产物目录 -->
      <img id="img-pngseq" class="clip term" data-start="193.50"
           data-duration="6.70" src="media/freezes/pngseq-dir.png" alt="">

      <!-- m09 软件路：启动行 216.8–222；Timing 226.2–231。
           2026-10-23 热态演录 sheet 回填：sw1 源内 6.8–12.0（打字实测
           6.5–11s，--no-browser-gpu 命令可读）；sw2 源内 153.8–158.6
           （workerCount:3→streaming-encode gate enabled:false multi_worker
           →forceScreenshot/useStreamingEncode:false→0/3 ready→swiftshader
           launched→三个 page.goto）。热态母带 160s 停录时正式 capture
           未开始，尾报秒数天然不入镜；冷态 68.1s 口径以探针彩排台账为准 -->
      <video id="rec-sw1" class="clip term" data-start="216.80"
             data-duration="5.20" data-track-index="2" data-media-start="6.8"
             src="media/shorts/sw-render.mp4" muted playsinline preload="auto"></video>
      <img id="img-gate-multi" class="clip term" data-start="222.00"
           data-duration="4.20" src="media/freezes/gate-multi.png" alt="">
      <video id="rec-sw2" class="clip term" data-start="226.20"
             data-duration="4.80" data-track-index="2" data-media-start="153.8"
             src="media/shorts/sw-render.mp4" muted playsinline preload="auto"></video>

      <!-- m09 硬件路：probe 行 238.2–243（源内 8–12.8 打字）；streaming
           244.8–251.6（源内 73–79.8＝52%→92% Streaming 245→357/390） -->
      <video id="rec-hw1" class="clip term" data-start="238.20"
             data-duration="4.80" data-track-index="2" data-media-start="8.0"
             src="media/shorts/hw-render.mp4" muted playsinline preload="auto"></video>
      <video id="rec-hw2" class="clip term" data-start="244.80"
             data-duration="6.80" data-track-index="2" data-media-start="73.0"
             src="media/shorts/hw-render.mp4" muted playsinline preload="auto"></video>

      <!-- m10 278.3–291.2：hf-07 长片 Timing 真机日志 -->
      <img id="img-hf07timing" class="clip term" data-start="278.30"
           data-duration="12.90" src="media/freezes/hf07-timing.png" alt="">

      <!-- m11 314.0–328.2：workerSizing 真机日志（算账口播同步） -->
      <img id="img-sizing" class="clip term" data-start="314.20"
           data-duration="14.00" src="media/freezes/worker-sizing.png" alt="">

      <!-- m12 365.4–376.9：源码黑条事故注释＋24GB 地板 -->
      <img id="img-blackbar" class="clip term" data-start="365.40"
           data-duration="11.50" src="media/freezes/src-blackbar.png" alt="">

      <!-- m14 坏工程：lint 照烤录屏 406.2–414.5（源内 18.5–26.8＝命令→横幅→
           Lint 2 error 1 warning＋Continuing→25% capture）；双帧 contact
           419.5–429.5；strict 437–441.5 -->
      <video id="rec-badlint" class="clip term" data-start="406.20"
             data-duration="8.30" data-track-index="2" data-media-start="18.5"
             src="media/shorts/badlint-run.mp4" muted playsinline preload="auto"></video>
      <img id="img-redblock" class="clip shot" data-start="419.50"
           data-duration="10.00" src="media/artifacts/redblock-30-150.png" alt="">
      <img id="img-strict" class="clip term" data-start="436.90"
           data-duration="4.60" src="media/freezes/strict-abort.png" alt="">

      <!-- m15 缺音轨拦截 455–469；45s warning 476.5–485 -->
      <img id="img-missing" class="clip term" data-start="455.00"
           data-duration="14.00" src="media/freezes/missing-audio.png" alt="">
      <img id="img-notimeline" class="clip term" data-start="476.50"
           data-duration="8.70" src="media/freezes/no-timeline-warn.png" alt="">"""

# ---------- 场景专属 CSS ----------
PROJECT_CSS = """
      /* 背景：蓝色细网格＋金蓝光斑（事实集蓝主色，金留给指纹） */
      #bg-grid { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background-image:
          linear-gradient(rgba(88,166,255,.055) 1px, transparent 1px),
          linear-gradient(90deg, rgba(88,166,255,.055) 1px, transparent 1px);
        background-size:80px 80px; }
      #bg-glow { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background:
          radial-gradient(720px 500px at 14% 14%, rgba(227,179,65,.10), transparent 70%),
          radial-gradient(880px 620px at 86% 84%, rgba(31,111,235,.14), transparent 70%); }

      /* 终端录屏/终端 freeze：1600x920 缩左 1120x644，右 620px 让给概念卡 */
      .term { position:absolute; left:54px; top:226px; width:1120px; height:644px;
        object-fit:fill; border-radius:10px;
        box-shadow:0 18px 60px rgba(0,0,0,.55); }
      /* artifacts 真机产物：同机位但保持原比例 */
      .shot { position:absolute; left:54px; top:226px; width:1120px; height:644px;
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
      .goldword-sm.big { font-size:50px; margin-top:30px; }
      .stage { position:absolute; left:120px; right:120px; top:150px; text-align:center; }

      /* ===== 右卡（终端幕）：gk 容器固定，rightcard 同位置轮替 ===== */
      .gk { position:absolute; left:1200px; top:128px; width:620px; height:800px; }
      .rightcard { box-sizing:border-box; background:#161b22; border:2px solid #30363d;
        border-radius:18px; padding:30px 34px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      .rightcard.err { border-color:#6e2b2b; }
      .rightcard.warn { border-color:#5e4a1e; }
      .gk-tag { font-size:33px; color:#58a6ff; line-height:1.5; margin-bottom:18px; }
      .rule-head { display:flex; align-items:center; font-size:32px; margin-bottom:16px; }
      .rule-head b { color:#e6edf3; font-weight:600; }
      .rule-mark { display:inline-flex; align-items:center; justify-content:center;
        width:50px; height:50px; border-radius:50%; font-size:32px; margin-right:13px; }
      .rule-mark.warn { background:rgba(210,153,34,.16); color:#d29922; }
      .rule-mark.err { background:rgba(248,81,73,.16); color:#f85149; }
      .rule-cn { font-size:33px; color:#c9d1d9; line-height:1.55; margin:10px 0; }
      .rule-foot { margin-top:14px; font-size:29px; color:#8b949e; line-height:1.5; }
      .rule-foot.hot, .rule-cn.hot { color:#ffa198; }
      .cmdbox { font-family:'Consolas','Courier New',monospace; font-size:30px;
        color:#c9d1d9; background:#0d1521; border:2px solid #30363d; border-radius:12px;
        padding:20px 22px; line-height:1.5; margin:14px 0; }
      .cmdbox.big { font-size:40px; text-align:center; }

      /* m01 实验台 */
      .lab { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .lab-dots { margin-bottom:44px; }
      .lab-dots i { display:inline-block; width:54px; height:54px; border-radius:14px;
        margin:0 26px; }
      .lab-dots i.b { background:#1f6feb; box-shadow:0 0 34px rgba(31,111,235,.6); }
      .lab-dots i.g { background:#3fb950; box-shadow:0 0 34px rgba(63,185,80,.6); }
      .lab-dots i.r { background:#f85149; box-shadow:0 0 34px rgba(248,81,73,.6); }
      .lab-word { font-size:96px; color:#e6edf3; letter-spacing:.12em; }

      /* m02 指纹表 */
      .ht { width:1300px; margin:6px auto 0; background:#161b22; border:2px solid #30363d;
        border-radius:16px; padding:14px 26px; }
      .ht-row { display:grid; grid-template-columns:230px 280px 1fr 60px;
        align-items:center; height:74px; font-family:'Consolas','Courier New',monospace;
        font-size:28px; border-bottom:1px solid #21262d; }
      .ht-row:last-child { border-bottom:none; }
      .ht-head { height:46px; font-size:18px; color:#484f58; letter-spacing:.2em;
        border-bottom:2px solid #30363d; }
      .fname { color:#7ee787; text-align:left; }
      .ftag { font-size:26px;
        color:#c9d1d9; text-align:left; }
      .fhash { color:#e3b341; letter-spacing:.02em;
        text-shadow:0 0 14px rgba(227,179,65,.22); }
      .ftick { color:#3fb950; font-size:30px; }

      /* m03 渲染名声 */
      .fame-rows { margin:26px 0; }
      .fame-in { display:inline-block; font-size:44px; color:#c9d1d9;
        background:#161b22; border:2px solid #30363d; border-radius:14px;
        padding:18px 40px; margin-bottom:30px; }
      .fame-outs { font-size:0; }
      .fo { display:inline-block; font-size:38px; color:#ffa198; background:#1d1212;
        border:2px solid #6e2b2b; border-radius:14px; padding:20px 30px; margin:10px;
        font-style:normal; }
      .fo em { font-style:normal; color:#f85149; font-weight:bold; margin-left:8px; }
      .fame-but { font-size:42px; color:#c9d1d9; line-height:1.7; margin-top:30px; }

      /* m04 录屏 vs 求解 */
      .rec-cmp { width:1300px; margin:0 auto; }
      .rec-card { background:#1d1212; border:2px solid #6e2b2b; border-radius:18px;
        padding:34px 44px; text-align:left; }
      .rec-h { font-size:48px; margin-bottom:18px; }
      .rec-l { font-size:36px; color:#c9d1d9; line-height:1.8; }
      .rec-vs { margin-top:30px; font-size:44px; color:#e3b341; letter-spacing:.08em; }
      .eq-row { display:flex; align-items:center; justify-content:center; margin:30px 0; }
      .eq-i { font-size:52px; color:#c9d1d9; background:#161b22;
        border:2px solid #1f4e8c; border-radius:14px; padding:16px 34px; }
      .eq-x { font-size:54px; color:#58a6ff; margin:0 26px; }
      .eq-out { font-size:64px; color:#e3b341;
        text-shadow:0 0 24px rgba(227,179,65,.35); }
      .solve-steps { display:flex; align-items:center; justify-content:center; margin:36px 0 22px; }
      .ss { font-size:38px; color:#e6edf3; background:#161b22; border:2px solid #30363d;
        border-radius:14px; padding:20px 30px; }
      .ss b { color:#7ee787; font-family:'Consolas',monospace; margin-right:6px; }
      .ss-arrow { font-size:40px; color:#58a6ff; margin:0 20px; }
      .solve-frames { margin:18px 0; }
      .sf { display:inline-block; font-family:'Consolas',monospace; font-style:normal;
        font-size:40px; color:#79c0ff; background:#0d1521; border:2px solid #1f4e8c;
        border-radius:12px; padding:14px 30px; margin:0 26px; }
      .solve-note { margin-top:28px; font-size:36px; color:#8b949e; line-height:1.6; }
      .twopaths { display:flex; align-items:center; justify-content:center; margin:20px 0; }
      .tp { width:480px; background:#161b22; border:2px solid #30363d; border-radius:18px;
        padding:34px 38px; }
      .tp-h { font-size:48px; margin-bottom:12px; }
      .tp-l { font-size:33px; color:#c9d1d9; line-height:1.6; }
      .tp-plus { font-size:56px; color:#8b949e; margin:0 32px; }

      /* m05 确定性根 */
      .root-fn { margin:36px 0 30px; }
      .fn-machine { display:flex; align-items:center; justify-content:center; }
      .fn-in, .fn-out { font-size:44px; color:#c9d1d9; }
      .fn-box { font-family:'Consolas',monospace; font-size:72px; color:#e3b341;
        border:4px solid #e3b341; border-radius:20px; padding:6px 44px; margin:0 26px;
        text-shadow:0 0 24px rgba(227,179,65,.3); }
      .fn-arrow { font-size:52px; color:#58a6ff; margin:0 18px; }
      .fn-rule { margin-top:30px; font-size:44px; color:#e6edf3; }
      .root-clock { margin:34px 0 10px; font-size:40px; }
      .clk-banned { display:inline-block; color:#ffa198; background:#1d1212;
        border:2px solid #6e2b2b; border-radius:12px; padding:10px 30px; margin-right:22px;
        text-decoration:line-through; }
      .clk-note { color:#c9d1d9; }

      /* m07 抽帧缓存 */
      .ex-rows { display:flex; justify-content:center; gap:44px; margin-top:20px; }
      .ex-card { width:620px; background:#161b22; border:2px solid #30363d;
        border-radius:18px; padding:36px 40px; text-align:left; }
      .ex-h { font-size:42px; margin-bottom:14px; }
      .ex-l { font-size:33px; color:#c9d1d9; line-height:1.65; }
      .png-rows { display:flex; align-items:center; justify-content:center; margin:34px 0; }
      .pkg { font-size:46px; color:#79c0ff; background:#0d1521; border:2px solid #1f4e8c;
        border-radius:14px; padding:18px 34px; font-family:'Consolas',monospace; }
      .pkg-plus { font-size:50px; color:#8b949e; margin:0 26px; }
      .pkg-eq { margin-left:40px; font-size:46px; color:#e3b341; }

      /* m08 分叉 */
      .fork-q { font-size:52px; color:#e6edf3; margin-bottom:50px; }
      .fork-rows { display:flex; justify-content:center; gap:60px; }
      .fork-card { width:520px; font-size:44px; line-height:1.7; color:#c9d1d9;
        background:#161b22; border:2px solid #30363d; border-radius:20px; padding:40px; }
      .fork-card b { display:block; font-size:34px; color:#8b949e; margin-bottom:10px; }
      .fork-card.soft { border-color:#1f4e8c; }
      .fork-card.hard { border-color:#5e4a1e; }

      /* m09 路径介绍 */
      .path-intro { width:1400px; margin:0 auto; text-align:left;
        background:#161b22; border:2px solid #1f4e8c; border-radius:18px; padding:36px 44px; }
      .path-intro.soft { border-color:#1f4e8c; }
      .pi-h { font-size:46px; color:#58a6ff; margin-bottom:20px; }
      .pi-l { font-size:37px; color:#c9d1d9; line-height:1.9; }

      /* m10 时间账 */
      .time-rows { width:1300px; margin:10px auto 0; }
      .tr { display:grid; grid-template-columns:300px 220px 1fr; align-items:center;
        background:#161b22; border:2px solid #30363d; border-radius:14px;
        padding:22px 32px; margin:18px 0; text-align:left; }
      .tr-name { font-size:36px; color:#e6edf3; }
      .tr-val { font-family:'Consolas',monospace; font-size:48px; }
      .tr-note { font-size:29px; color:#8b949e; }
      .long-stats { display:flex; flex-wrap:wrap; justify-content:center; gap:26px;
        margin:30px 0; }
      .ls { width:560px; background:#161b22; border:2px solid #30363d; border-radius:16px;
        padding:30px; font-size:36px; color:#c9d1d9; }
      .ls b { display:block; font-family:'Consolas',monospace; font-size:58px;
        color:#e3b341; margin-bottom:6px; }

      /* m11 算账 */
      .calc-rows { width:1200px; margin:8px auto 0; }
      .cr { display:flex; align-items:center; justify-content:space-between;
        background:#161b22; border:2px solid #1f4e8c; border-radius:14px;
        padding:20px 40px; margin:16px 0; }
      .cr-expr { font-size:36px; color:#c9d1d9; text-align:left; }
      .cr-eq { font-family:'Consolas',monospace; font-size:48px; color:#58a6ff; }
      .calc-min { margin-top:30px; font-size:38px; color:#8b949e; }
      .mine-rows { display:flex; justify-content:center; flex-wrap:wrap; gap:22px;
        margin:24px 0; }
      .mr { width:280px; background:#0d1521; border:2px solid #1f4e8c; border-radius:16px;
        padding:26px 10px; font-size:33px; color:#c9d1d9; }
      .mr b { font-family:'Consolas',monospace; font-size:56px; }

      /* m12 三层 */
      .ly-rows { width:1420px; margin:10px auto 0; }
      .ly { display:flex; align-items:flex-start; background:#161b22;
        border:2px solid #30363d; border-left:10px solid #1f6feb; border-radius:14px;
        padding:24px 36px; margin:20px 0; text-align:left; font-size:37px;
        color:#c9d1d9; line-height:1.55; }
      .ly-n { color:#58a6ff; font-size:44px; margin-right:26px; flex:none; }

      /* m13 校准 */
      .calib-rows { width:1300px; margin:0 auto; }
      .clb-rule { font-size:46px; color:#e6edf3; margin:24px 0; }
      .clb-costs { margin:30px 0; }
      .cc { display:inline-block; font-size:34px; color:#c9d1d9; background:#0d1521;
        border:2px solid #5e4a1e; border-radius:999px; padding:14px 34px; margin:10px 14px; }
      .cc em { font-style:normal; color:#e3b341; font-family:'Consolas',monospace;
        margin-left:8px; }
      .clb-feedback { margin-top:34px; font-size:42px; color:#c9d1d9; line-height:1.7; }

      /* m14 门控 */
      .gate-default { width:1200px; margin:30px auto 0; }
      .gd { font-size:48px; color:#c9d1d9; background:#1d1212; border:2px solid #6e2b2b;
        border-radius:16px; padding:30px 40px; line-height:1.6; }
      .lock-word { font-size:52px; color:#ffa198; margin:30px 0 20px; line-height:1.6; }

      /* m15 对仗 */
      .antithesis { margin-top:60px; }
      .at-line { font-size:60px; line-height:1.9; color:#c9d1d9; }

      /* m16 三宝＋超时 */
      .crash3 { display:flex; justify-content:center; gap:26px; margin-top:14px; }
      .cz { width:440px; background:#161b22; border:2px solid #30363d; border-radius:18px;
        padding:32px 30px; text-align:left; min-height:430px; }
      .cz-n { font-family:'Consolas',monospace; font-size:46px; color:#e3b341; }
      .cz-h { font-size:39px; margin:12px 0 16px; }
      .cz-l { font-size:30px; color:#c9d1d9; line-height:1.7; }
      .to-rows { display:flex; justify-content:center; gap:30px; margin:36px 0; }
      .to { width:400px; background:#161b22; border:2px solid #1f4e8c; border-radius:16px;
        padding:28px 20px; }
      .to-name { display:block; font-size:34px; color:#8b949e; margin-bottom:12px; }
      .to-val { font-family:'Consolas',monospace; font-size:52px; color:#58a6ff; }
      .to-quality { margin-top:34px; font-size:40px; color:#c9d1d9; }

      /* m17 闭环链＋承诺 */
      .chain { display:flex; flex-wrap:wrap; justify-content:center; gap:16px;
        margin:26px 0; }
      .ch { font-size:30px; color:#c9d1d9; background:#161b22; border:2px solid #1f4e8c;
        border-radius:12px; padding:18px 22px; }
      .ch b { font-family:'Consolas',monospace; color:#58a6ff; margin-right:8px; }
      .ch.hot { border-color:#e3b341; }
      .ch.hot b { color:#e3b341; }
      .chain-note { margin-top:28px; font-size:38px; color:#8b949e; line-height:1.6; }
      .pr-said { font-size:42px; color:#8b949e; margin-bottom:34px; }
      .pr-formula { font-family:'Consolas',monospace; font-size:64px; color:#e6edf3;
        margin:20px 0; }
      .pr-stamp { font-size:46px; color:#e3b341; line-height:1.7; margin-top:30px; }

      /* m18 行动件 */
      .acl { width:1400px; margin:0 auto; }
      .acl-row { padding:24px 38px; margin-bottom:20px; background:#161b22;
        border:2px solid #2b3c57; border-left:10px solid #1f6feb; border-radius:14px;
        font-size:37px; color:#e6edf3; line-height:1.5; text-align:left; }
      .acl-n { color:#e3b341; font-size:42px; margin-right:20px; }

      /* m19 云端预告 */
      .nx-h { font-size:40px; color:#8b949e; letter-spacing:.3em; margin-bottom:40px; }
      .cloud-idea { font-size:56px; color:#e6edf3; margin-bottom:34px; }
      .cloud-cmds { margin:26px 0; }
      .ccmd { display:inline-block; font-family:'Consolas',monospace; font-size:40px;
        color:#79c0ff; background:#0d1521; border:2px solid #1f4e8c; border-radius:999px;
        padding:12px 38px; margin:0 14px; }
      .cloud-l { font-size:37px; color:#c9d1d9; line-height:1.8; margin-top:26px; }
      .nx-card { margin-top:44px; font-size:78px; color:#58a6ff; letter-spacing:.04em;
        text-shadow:0 0 30px rgba(88,166,255,.3); }

      /* m20 道别 */
      #m20-bye { position:absolute; inset:0; }
      .bye { position:absolute; left:0; right:0; top:430px; text-align:center;
        font-size:80px; color:#e6edf3; letter-spacing:.08em; }
      .finale-tag { position:absolute; left:0; right:0; top:600px; text-align:center;
        font-family:'Consolas',monospace; font-size:30px; color:#e3b341;
        letter-spacing:.5em; }
"""

# ---------- 场景时间轴（时间显式给秒；拍点锚 cues 实测词戳） ----------
SCENE_JS = """
      /* 拍点通用：右卡同位置轮替（x:60 滑入），全屏卡 y/淡入。
         gsap className 替换非追加，所有高亮一律属性补间（hf-05 教训）。 */

      /* m01 0–1.24：实验台 */
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.4},0);
      tl.from('.lab-dots i',{y:24,opacity:0,duration:.4,stagger:.12,ease:'back.out(1.6)'},.1);
      tl.from('#lab .lab-word',{y:20,opacity:0,duration:.5},.5);

      /* m02 1.24–29.42：表行 9.32/10.38 → 真机 10.6 → 旧档 14.6 → 三烤法 19.2/21 → 金句 28.03 */
      tl.fromTo('#sc-sixhash > .scene-inner',{opacity:0},{opacity:1,duration:.5},1.24);
      tl.from('#m2-table .kicker-static',{y:18,opacity:0,duration:.5},1.6);
      /* 右卡容器幕首隐藏（卡片自身 from 已置 0，容器再兜一道） */
      tl.set('#m2-term',{opacity:0},1.24);
      tl.from('#ht-1',{x:-40,opacity:0,duration:.4},9.32);
      tl.from('#ht-2',{x:-40,opacity:0,duration:.4},10.38);
      tl.to('#m2-table',{opacity:0,duration:.3},10.55);
      tl.to('#m2-term',{opacity:1,duration:.3},10.6);
      tl.from('#c2-same',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},10.7);
      tl.to('#c2-same',{opacity:0,duration:.3},14.2);
      tl.from('#c2-old',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},14.5);
      tl.to('#c2-old',{opacity:0,duration:.3},18.4);
      /* 容器状态机：from 会 immediateRender 把表格在幕首置 0（前 18 秒不可见），
         回收必须用 to 显式点亮 */
      tl.to('#m2-term',{opacity:0,duration:.3},18.4);
      tl.to('#m2-table',{opacity:1,duration:.4},18.6);
      tl.from('#ht-old',{x:-40,opacity:0,duration:.4},14.7);
      tl.from('#ht-w1',{x:-40,opacity:0,duration:.4},19.5);
      tl.from('#ht-hwa',{x:-40,opacity:0,duration:.4},21.4);
      tl.from('#ht-hwb',{x:-40,opacity:0,duration:.4},22.6);
      tl.from('#m2-word',{scale:.92,opacity:0,duration:.55,ease:'back.out(1.3)'},27.6);
      tl.to('#sc-sixhash > .scene-inner',{opacity:0,duration:.4},29.02);

      /* m03 29.42–56.86：名声 31.18 → 今天/明天 34.76 → 逐字节 45.16 → 三问 49.5/53.7/55.4 */
      tl.fromTo('#sc-fame > .scene-inner',{opacity:0},{opacity:1,duration:.5},29.42);
      tl.from('#m3-k',{y:18,opacity:0,duration:.5},29.9);
      tl.from('#fame-in',{scale:.9,opacity:0,duration:.5},31.4);
      tl.from('#fo-1',{y:24,opacity:0,duration:.4,ease:'back.out(1.3)'},34.9);
      tl.from('#fo-2',{y:24,opacity:0,duration:.4,ease:'back.out(1.3)'},35.9);
      tl.from('#fo-3',{y:24,opacity:0,duration:.4,ease:'back.out(1.3)'},38.4);
      tl.from('#fo-4',{y:24,opacity:0,duration:.4,ease:'back.out(1.3)'},39.6);
      tl.from('#fame-but',{y:24,opacity:0,duration:.6,ease:'back.out(1.2)'},44.6);
      tl.to('#m3-fame',{opacity:0,duration:.35},49.0);
      tl.from('#c3-q1',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},49.6);
      tl.to('#c3-q1',{opacity:0,duration:.3},53.2);
      tl.from('#c3-q2',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},53.5);
      tl.to('#c3-q2',{opacity:0,duration:.3},54.9);
      tl.from('#c3-q3',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},55.2);
      tl.to('#sc-fame > .scene-inner',{opacity:0,duration:.4},56.46);

      /* m04 56.86–106.86：录屏 60.7 → 数学题 72.62 → 30格75.34/390 77.78 →
         三步 78.8 → 帧号 87.34 → 两路 95.58/97.98 → 合成 104.4 */
      tl.fromTo('#sc-solve > .scene-inner',{opacity:0},{opacity:1,duration:.5},56.86);
      /* 三个全屏舞台状态机：后两个幕首置 0（含无动画的箭头/加号，
         否则几何盒子与前台文字重叠触 content_overlap） */
      tl.set('#m4-math',{opacity:0},56.86);
      tl.set('#m4-two',{opacity:0},56.86);
      tl.from('#m4-record .kicker-static',{y:18,opacity:0,duration:.5},57.3);
      tl.from('#rec-bad',{y:30,opacity:0,duration:.6,ease:'back.out(1.15)'},60.9);
      tl.from('#rec-vs',{opacity:0,duration:.6},70.0);
      tl.to('#m4-record',{opacity:0,duration:.35},72.1);
      tl.to('#m4-math',{opacity:1,duration:.35},72.1);
      tl.from('#m4-math .kicker-static',{y:18,opacity:0,duration:.5},72.62);
      tl.from('#eq-row > *',{y:24,opacity:0,duration:.4,stagger:.14},75.4);
      tl.from('#ss-1',{y:24,opacity:0,duration:.5},78.9);
      tl.from('.solve-steps > div:nth-child(2)',{y:24,opacity:0,duration:.5},81.4);
      tl.from('#ss-2',{y:24,opacity:0,duration:.5},81.4);
      tl.from('.solve-steps > div:nth-child(4)',{y:24,opacity:0,duration:.5},83.8);
      tl.from('#ss-3',{y:24,opacity:0,duration:.5},83.8);
      tl.from('#sf-1',{scale:.6,opacity:0,duration:.4,ease:'back.out(1.5)'},87.5);
      tl.from('#sf-100',{scale:.6,opacity:0,duration:.4,ease:'back.out(1.5)'},88.7);
      tl.from('#sf-390',{scale:.6,opacity:0,duration:.4,ease:'back.out(1.5)'},89.9);
      tl.from('#solve-note',{opacity:0,duration:.6},91.8);
      tl.to('#m4-math',{opacity:0,duration:.35},95.0);
      tl.to('#m4-two',{opacity:1,duration:.35},95.0);
      tl.from('#tp-v',{x:-50,opacity:0,duration:.6,ease:'back.out(1.15)'},95.7);
      tl.from('.tp-plus',{y:18,opacity:0,duration:.5},98.4);
      tl.from('#tp-a',{x:50,opacity:0,duration:.6,ease:'back.out(1.15)'},98.4);
      tl.from('#tp-out',{scale:.9,opacity:0,duration:.6,ease:'back.out(1.3)'},103.8);
      tl.to('#sc-solve > .scene-inner',{opacity:0,duration:.4},106.46);

      /* m05 106.86–124.60：不确定 109.88 → 时间码 113.78 → 墙钟在外 116.46 → 金句 120.36 */
      tl.fromTo('#sc-root > .scene-inner',{opacity:0},{opacity:1,duration:.5},106.86);
      tl.from('#m5-root .kicker-static',{y:18,opacity:0,duration:.5},107.2);
      tl.from('#fn-machine > *',{y:22,opacity:0,duration:.4,stagger:.13},113.2);
      tl.from('#fn-rule',{opacity:0,duration:.6},115.2);
      tl.from('#root-clock',{y:24,opacity:0,duration:.6,ease:'back.out(1.2)'},116.8);
      tl.from('#m5-word',{scale:.94,opacity:0,duration:.6,ease:'back.out(1.2)'},120.0);
      tl.to('#sc-root > .scene-inner',{opacity:0,duration:.4},124.20);

      /* m06 124.60–170.70：debug 127.38 → 编译 134.9 → 探路 140.34 → 五帧 144.12 →
         worker 157.24 → 落盘 163.18 → 无声 166.14 → 合 169.02 */
      tl.fromTo('#sc-pipe > .scene-inner',{opacity:0},{opacity:1,duration:.5},124.60);
      tl.from('#c6-debug',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},125.0);
      tl.to('#c6-debug',{opacity:0,duration:.3},133.9);
      tl.from('#c6-compile',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},134.2);
      tl.to('#c6-compile',{opacity:0,duration:.3},139.8);
      tl.from('#c6-probe',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},140.1);
      tl.to('#c6-probe',{opacity:0,duration:.3},143.6);
      tl.from('#c6-calib',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},143.9);
      tl.to('#c6-calib',{opacity:0,duration:.3},155.8);
      tl.from('#c6-workers',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},156.1);
      tl.to('#c6-workers',{opacity:0,duration:.3},165.6);
      tl.from('#c6-encode',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},165.9);
      tl.to('#sc-pipe > .scene-inner',{opacity:0,duration:.4},170.30);

      /* m07 170.70–201.08：抽帧 173.58 → 缓存 177.98 → 系统盘 184.40 →
         PNG 193.26 → 3.2兆 197.82 → 原始产品 198.70 */
      tl.fromTo('#sc-cache > .scene-inner',{opacity:0},{opacity:1,duration:.5},170.70);
      tl.from('#m7-extract .kicker-static',{y:18,opacity:0,duration:.5},171.1);
      tl.from('#ex-1',{x:-50,opacity:0,duration:.6,ease:'back.out(1.15)'},173.4);
      tl.from('#ex-2',{x:50,opacity:0,duration:.6,ease:'back.out(1.15)'},177.4);
      tl.to('#m7-extract',{opacity:0,duration:.35},191.0);
      tl.from('#m7-png .kicker-static',{y:18,opacity:0,duration:.5},191.3);
      tl.from('#png-cmd',{scale:.92,opacity:0,duration:.55,ease:'back.out(1.3)'},193.4);
      tl.from('#png-390',{y:24,opacity:0,duration:.5},195.2);
      tl.from('.pkg-plus',{y:24,opacity:0,duration:.5},196.4);
      tl.from('#png-audio',{y:24,opacity:0,duration:.5},196.4);
      tl.from('#png-size',{x:30,opacity:0,duration:.55,ease:'back.out(1.3)'},197.9);
      tl.from('#png-note',{opacity:0,duration:.6},198.9);
      tl.to('#sc-cache > .scene-inner',{opacity:0,duration:.4},200.68);

      /* m08 201.08–205.16：两条路 204.08 */
      tl.fromTo('#sc-fork > .scene-inner',{opacity:0},{opacity:1,duration:.4},201.08);
      tl.from('#fork-q',{y:22,opacity:0,duration:.5},201.4);
      tl.from('#fork-soft',{x:-60,opacity:0,duration:.55,ease:'back.out(1.3)'},203.2);
      tl.from('#fork-hard',{x:60,opacity:0,duration:.55,ease:'back.out(1.3)'},203.6);
      tl.to('#sc-fork > .scene-inner',{opacity:0,duration:.4},204.76);

      /* m09 205.16–254.82：软件介绍 208.7/211.64/213.36 → 并行 220.2 → 统一编 225.84 →
         门控 231.26 → 集显 237.76 → 合成器 244.32 → 1 worker 247.98 → 边抓边编 251.66 */
      tl.fromTo('#sc-paths > .scene-inner',{opacity:0},{opacity:1,duration:.5},205.16);
      tl.from('#pi-soft-h',{y:18,opacity:0,duration:.5},205.6);
      tl.from('#pi-soft-1',{opacity:0,duration:.6},208.4);
      tl.from('#pi-soft-2',{opacity:0,duration:.6},213.0);
      tl.to('#m9-soft-intro',{opacity:0,duration:.35},216.3);
      tl.from('#c9-sw-par',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},216.6);
      tl.to('#c9-sw-par',{opacity:0,duration:.3},224.9);
      tl.from('#c9-sw-disk',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},225.2);
      tl.to('#c9-sw-disk',{opacity:0,duration:.3},233.0);
      tl.from('#c9-hw-probe',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},233.3);
      tl.to('#c9-hw-probe',{opacity:0,duration:.3},243.4);
      tl.from('#c9-hw-de',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},243.7);
      tl.to('#c9-hw-de',{opacity:0,duration:.3},247.4);
      tl.from('#c9-hw-1',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},247.7);
      tl.to('#sc-paths > .scene-inner',{opacity:0,duration:.4},254.42);

      /* m10 254.82–292.22：68 258/16秒 260.12/56 265.97/52 267.26 →
         长片 275.12 → 16777 278.31/39分 281.94/41分 284.04/7帧 286.32 */
      tl.fromTo('#sc-time > .scene-inner',{opacity:0},{opacity:1,duration:.5},254.82);
      tl.from('#m10-small .kicker-static',{y:18,opacity:0,duration:.5},255.2);
      tl.from('#tr-1',{x:-50,opacity:0,duration:.55,ease:'back.out(1.15)'},257.6);
      tl.from('#tr-2',{x:-50,opacity:0,duration:.55,ease:'back.out(1.15)'},264.2);
      tl.from('#tr-3',{x:-50,opacity:0,duration:.55,ease:'back.out(1.15)'},266.8);
      tl.from('#tr-note',{opacity:0,duration:.6},271.0);
      tl.to('#m10-small',{opacity:0,duration:.35},274.6);
      tl.from('#m10-long .kicker-static',{y:18,opacity:0,duration:.5},275.2);
      tl.from('#ls-frames',{y:26,opacity:0,duration:.55,ease:'back.out(1.2)'},277.8);
      tl.from('#ls-cap',{y:26,opacity:0,duration:.55,ease:'back.out(1.2)'},281.4);
      tl.from('#ls-total',{y:26,opacity:0,duration:.55,ease:'back.out(1.2)'},283.6);
      tl.from('#ls-fps',{y:26,opacity:0,duration:.55,ease:'back.out(1.2)'},286.0);
      tl.from('#m10-word',{scale:.94,opacity:0,duration:.6,ease:'back.out(1.2)'},288.6);
      tl.to('#sc-time > .scene-inner',{opacity:0,duration:.4},291.82);

      /* m11 292.22–330.90：算出 294.1/源码 295.42 → 四笔 299.66 → min 309.9 →
         我这台 314 → 压到三 321.66 → 60帧 328.2 */
      tl.fromTo('#sc-sizing > .scene-inner',{opacity:0},{opacity:1,duration:.5},292.22);
      tl.from('#m11-calc .kicker-static',{y:18,opacity:0,duration:.5},292.6);
      tl.from('#cr-1',{x:-46,opacity:0,duration:.5,ease:'back.out(1.15)'},298.0);
      tl.from('#cr-2',{x:-46,opacity:0,duration:.5,ease:'back.out(1.15)'},301.4);
      tl.from('#cr-3',{x:-46,opacity:0,duration:.5,ease:'back.out(1.15)'},304.8);
      tl.from('#cr-4',{x:-46,opacity:0,duration:.5,ease:'back.out(1.15)'},307.6);
      tl.from('#calc-min',{opacity:0,duration:.6},310.1);
      tl.to('#m11-calc',{opacity:0,duration:.35},313.6);
      tl.from('#m11-mine .kicker-static',{y:18,opacity:0,duration:.5},313.9);
      tl.from('#mr-cpu',{y:24,opacity:0,duration:.45},315.0);
      tl.from('#mr-mem',{y:24,opacity:0,duration:.45},316.4);
      tl.from('#mr-frame',{y:24,opacity:0,duration:.45},317.8);
      tl.from('#mr-final',{scale:.85,opacity:0,duration:.55,ease:'back.out(1.5)'},321.7);
      tl.from('#mr-note',{opacity:0,duration:.55},324.6);
      tl.from('#mr-few',{opacity:0,duration:.6},328.0);
      tl.to('#sc-sizing > .scene-inner',{opacity:0,duration:.4},330.50);

      /* m12 330.90–381.64：三层 333.44 → 900帧 341.22/反转 346.28 →
         3并发 355.26/门槛 356.12 → 黑条 365.44/挤掉 370.34/漏看 372.8 →
         地板 376.92/线外 380.34 */
      tl.fromTo('#sc-why1 > .scene-inner',{opacity:0},{opacity:1,duration:.5},330.90);
      tl.from('#m12-layers .kicker-static',{y:18,opacity:0,duration:.5},331.3);
      tl.from('#ly-1',{x:-50,opacity:0,duration:.55,ease:'back.out(1.15)'},334.0);
      tl.from('#ly-2',{x:-50,opacity:0,duration:.55,ease:'back.out(1.15)'},340.2);
      tl.from('#ly-3',{x:-50,opacity:0,duration:.55,ease:'back.out(1.15)'},353.2);
      tl.to('#m12-layers',{opacity:0,duration:.35},360.8);
      tl.from('#c12-why',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},361.1);
      tl.to('#c12-why',{opacity:0,duration:.3},365.0);
      tl.from('#c12-bar',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},365.3);
      tl.to('#c12-bar',{opacity:0,duration:.3},374.6);
      tl.from('#c12-floor',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},374.9);
      tl.to('#sc-why1 > .scene-inner',{opacity:0,duration:.4},381.24);

      /* m13 381.64–397.50：摆设 381.64 → 着色器/iframe 387.30 → 反调 391.14 → 饿死 394.44 */
      tl.fromTo('#sc-calib > .scene-inner',{opacity:0},{opacity:1,duration:.5},381.64);
      tl.from('#clb-rule',{y:20,opacity:0,duration:.55},382.0);
      tl.from('#cc-1',{y:22,opacity:0,duration:.45},386.2);
      tl.from('#cc-2',{y:22,opacity:0,duration:.45},387.4);
      tl.from('#cc-3',{y:22,opacity:0,duration:.45},388.6);
      tl.from('#clb-feedback',{y:26,opacity:0,duration:.6,ease:'back.out(1.2)'},391.0);
      tl.to('#sc-calib > .scene-inner',{opacity:0,duration:.4},397.10);

      /* m14 397.50–448.12：lint 399.18/不拦 404.34 → 坏工程 405.86/掐表 408 →
         照样 416.36 → 第一秒 419.52/第五秒 420.44/正中 423.66 → 真切 430.06 →
         strict 436.88/中止 439.26 → 纪律 441.74/锁 444.38 */
      tl.fromTo('#sc-gate > .scene-inner',{opacity:0},{opacity:1,duration:.5},397.50);
      tl.from('#m14-intro .kicker-static',{y:18,opacity:0,duration:.5},397.9);
      tl.from('#gd-note',{y:26,opacity:0,duration:.6,ease:'back.out(1.15)'},404.0);
      tl.to('#m14-intro',{opacity:0,duration:.35},405.8);
      tl.from('#c14-bad',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},405.9);
      tl.to('#c14-bad',{opacity:0,duration:.3},414.2);
      tl.from('#c14-cont',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},414.5);
      tl.to('#c14-cont',{opacity:0,duration:.3},419.0);
      tl.from('#c14-read1',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},419.2);
      tl.to('#c14-read1',{opacity:0,duration:.3},420.2);
      tl.from('#c14-read2',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},420.5);
      tl.to('#c14-read2',{opacity:0,duration:.3},429.6);
      tl.to('#m14-term',{opacity:0,duration:.35},429.8);
      tl.from('#lock-word',{scale:.94,opacity:0,duration:.6,ease:'back.out(1.2)'},430.0);
      tl.to('#m14-lock',{opacity:0,duration:.3},435.8);
      tl.to('#m14-term',{opacity:1,duration:0},436.6);
      tl.from('#c14-strict',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},436.7);
      tl.to('#c14-strict',{opacity:0,duration:.3},441.2);
      tl.to('#m14-term',{opacity:0,duration:0},441.4);
      tl.from('#m14-lock',{opacity:0,duration:0},441.4);
      tl.from('#lock-word2',{scale:.94,opacity:0,duration:.6,ease:'back.out(1.2)'},441.7);
      tl.to('#sc-gate > .scene-inner',{opacity:0,duration:.4},447.72);

      /* m15 448.12–487.28：不存在 452.42/没客气 454.54 → 哑巴/正确性 460.50 →
         对仗 470.38 → 标记 475.52/死等 478.48/45秒 480.36/省45 485.10 */
      tl.fromTo('#sc-block > .scene-inner',{opacity:0},{opacity:1,duration:.5},448.12);
      tl.from('#c15-but',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},448.5);
      tl.to('#c15-but',{opacity:0,duration:.3},454.2);
      tl.from('#c15-block',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},454.5);
      tl.to('#c15-block',{opacity:0,duration:.3},469.4);
      tl.to('#m15-term',{opacity:0,duration:.3},469.6);
      tl.from('#at-1',{y:24,opacity:0,duration:.6},469.9);
      tl.from('#at-2',{y:24,opacity:0,duration:.6,ease:'back.out(1.2)'},470.6);
      tl.to('#m15-word',{opacity:0,duration:.35},474.8);
      tl.to('#m15-term',{opacity:1,duration:0},475.0);
      tl.from('#c15-pit',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},475.2);
      tl.to('#c15-pit',{opacity:0,duration:.3},482.8);
      tl.from('#c15-fix',{x:60,opacity:0,duration:.55,ease:'back.out(1.2)'},483.1);
      tl.to('#sc-block > .scene-inner',{opacity:0,duration:.4},486.88);

      /* m16 487.28–538.48：三样 488.70 → 第一现场 491.44/账本 493.80 →
         静默退出 505.52 → 续烤 520.44 → 60/300/45 522.70 → 画质 532.46 */
      tl.fromTo('#sc-crash > .scene-inner',{opacity:0},{opacity:1,duration:.5},487.28);
      tl.from('#m16-three .kicker-static',{y:18,opacity:0,duration:.5},487.7);
      tl.from('#cz-1',{y:34,opacity:0,duration:.55,ease:'back.out(1.15)'},489.6);
      tl.from('#cz-2',{y:34,opacity:0,duration:.55,ease:'back.out(1.15)'},498.0);
      tl.from('#cz-3',{y:34,opacity:0,duration:.55,ease:'back.out(1.15)'},514.2);
      tl.to('#m16-three',{opacity:0,duration:.35},521.6);
      tl.from('#m16-timeouts .kicker-static',{y:18,opacity:0,duration:.5},521.9);
      tl.from('#to-1',{y:24,opacity:0,duration:.45},522.9);
      tl.from('#to-2',{y:24,opacity:0,duration:.45},524.3);
      tl.from('#to-3',{y:24,opacity:0,duration:.45},525.7);
      tl.from('#to-q',{opacity:0,duration:.6},532.2);
      tl.to('#sc-crash > .scene-inner',{opacity:0,duration:.4},538.08);

      /* m17 538.48–575.44：闭环 539.57 → 二/三/四/六/五/上集 541.5–551.86 →
         黑箱 559.66 → 确定性 565.14/同输入 567.78/验收单 573.42 */
      tl.fromTo('#sc-loop > .scene-inner',{opacity:0},{opacity:1,duration:.5},538.48);
      tl.from('#m17-chain .kicker-static',{y:18,opacity:0,duration:.5},538.9);
      tl.from('#ch-2',{y:20,opacity:0,duration:.4},541.6);
      tl.from('#ch-3',{y:20,opacity:0,duration:.4},543.4);
      tl.from('#ch-4',{y:20,opacity:0,duration:.4},546.0);
      tl.from('#ch-6',{y:20,opacity:0,duration:.4},548.3);
      tl.from('#ch-5',{y:20,opacity:0,duration:.4},550.0);
      tl.from('#ch-7',{y:20,opacity:0,duration:.4},551.7);
      tl.from('#ch-8',{scale:.85,opacity:0,duration:.55,ease:'back.out(1.5)'},553.8);
      tl.from('#chain-note',{opacity:0,duration:.6},558.2);
      tl.to('#m17-chain',{opacity:0,duration:.35},563.0);
      tl.from('#pr-said',{y:22,opacity:0,duration:.55},563.3);
      tl.from('#pr-formula',{scale:.92,opacity:0,duration:.6,ease:'back.out(1.2)'},566.2);
      tl.from('#pr-stamp',{scale:.94,opacity:0,duration:.6,ease:'back.out(1.2)'},572.0);
      tl.to('#sc-loop > .scene-inner',{opacity:0,duration:.4},575.04);

      /* m18 575.44–590.98：行动件 575.44/真刀真枪 578.66/几百张 584.08/自己算 587.68 */
      tl.fromTo('#sc-action > .scene-inner',{opacity:0},{opacity:1,duration:.5},575.44);
      tl.from('#m18-action .kicker-static',{y:18,opacity:0,duration:.5},575.8);
      tl.from('#ac-1',{x:-44,opacity:0,duration:.55},577.4);
      tl.from('#ac-2',{x:-44,opacity:0,duration:.55},580.4);
      tl.from('#ac-3',{x:-44,opacity:0,duration:.55},586.0);
      tl.to('#sc-action > .scene-inner',{opacity:0,duration:.4},590.58);

      /* m19 590.98–608.90：完结 590.98/云端 594.84/机房 600/benchmark 603.30/第二季 605.62 */
      tl.fromTo('#sc-cloud > .scene-inner',{opacity:0},{opacity:1,duration:.5},590.98);
      tl.from('#nx-h',{y:18,opacity:0,duration:.5},591.4);
      tl.from('#cloud-idea',{y:24,opacity:0,duration:.6},594.6);
      tl.from('.ccmd',{y:22,opacity:0,duration:.45,stagger:.18},595.6);
      tl.from('#cloud-l',{opacity:0,duration:.6},600.2);
      tl.from('#nx-card',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},605.0);
      tl.to('#sc-cloud > .scene-inner',{opacity:0,duration:.4},608.50);

      /* m20 608.90–TOTAL：道别 */
      tl.fromTo('#sc-bye > .scene-inner',{opacity:0},{opacity:1,duration:.5},608.90);
      tl.from('#bye',{y:24,opacity:0,duration:.7},609.1);
      tl.from('#finale-tag',{opacity:0,duration:.8},609.9);
"""

# ---------- 底部字幕轨道 ----------
# time_offset：faster-whisper 吞句间停顿致字幕偏早；hf-01..07 实测
# 0.28/0.37/0.29/0.30/0.29/0.31/0.31。hf-08 20 段蝉镜段级首录母带经
# oneoffs/measure_offset.py 实测 onset 配对中位数 +291.5ms（64/81），取 0.29。
frag = char_track(cues, chars, THEME.accent, time_offset=0.29)

# ---------- 组装 ----------
body = "\n".join([
    # patched 母带：oneoffs/patch_audio_54.py 句级替换「五十二→五十四秒」
    # （入镜母带尾报 54.2s），窗外逐样本不动，total/offset 不变。
    audio_tag("media/hf-08-yeyang-patched.wav", total),
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
