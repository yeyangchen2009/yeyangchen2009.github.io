# -*- coding: utf-8 -*-
"""HyperFrames 教程第 1 集《认识 HyperFrames》成片生成器。

暗色 GitHub 主题（DARK_GOLD_GH），234.98s，17 幕。本片独有：17 幕 body、
专属 CSS、场景时间轴。两处嵌入真实终端录屏——doctor 体检（S12）与
--help 命令列表（S13）：录屏作**顶层 clip**（StaticGuard：video 不可嵌套
在另一个 data-start 元素内），播真实时长后由 GSAP 概念卡接续讲解。
页面骨架／主题／字幕／clip 外壳全部复用 videopipe。
"""
import io
import sys
from pathlib import Path

# projects/<name>/make_video.py -> videos/ 在 parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       DARK_GOLD_GH)
from videopipe.config import WHISPER_WORD_LEAD

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars, total = data["cues"], data["chars"], data["duration"]
THEME = DARK_GOLD_GH

# ---- GitHub Dark 辅助色（主题只给 accent/bg，其余在此固定） ----
PANEL, LINE = "#161b22", "#30363d"
INK, MUTE = "#e6edf3", "#8b949e"
BLUE, BLUE2 = "#1f6feb", "#58a6ff"
GREEN, RED, GOLD = "#3fb950", "#f85149", "#e3b341"

# ---------- 17 幕（边界严格首尾相接，交叉淡变） ----------
SCENES = [

# S1 灵魂拷问 0.00–9.20（cue1–5）
Scene("sc-ask", 0.00, 9.20, """
          <div class="kicker" id="ask-k">做视频，一定要 ——</div>
          <svg id="tl-svg" viewBox="0 0 1100 360">
            <rect x="40" y="60" width="1020" height="92" rx="10" id="tl-track"/>
            <rect x="40" y="190" width="1020" height="92" rx="10" id="tl-track2"/>
            <g id="tl-cuts">
              <path d="M220 52 l16 16 l-16 16 l-16 -16 Z" class="keyframe"/>
              <path d="M520 182 l16 16 l-16 16 l-16 -16 Z" class="keyframe"/>
              <path d="M820 52 l16 16 l-16 16 l-16 -16 Z" class="keyframe"/>
            </g>
            <line x1="120" y1="106" x2="980" y2="106" class="clip-line"/>
            <line x1="120" y1="236" x2="980" y2="236" class="clip-line"/>
          </svg>
          <div class="ask-tail" id="ask-tail">打开剪辑软件 · 一帧帧拖轨道 · 打关键帧？</div>"""),

# S2 新工具 9.20–22.62（cue6–11）
Scene("sc-tool", 9.20, 22.62, """
          <div class="kicker" id="tl-k">但现在有个工具 —— 你完全不用碰时间轴</div>
          <div class="flow">
            <div class="flow-box" id="fb-code">
              <div class="fb-h">你只管写</div>
              <div class="fb-c">HTML · CSS</div>
            </div>
            <div class="flow-arrow" id="fb-arrow">→</div>
            <div class="flow-box hot" id="fb-video">
              <div class="fb-h">它负责</div>
              <div class="fb-c">渲染成视频</div>
            </div>
          </div>"""),

# S3 HyperFrames＋九字口号 22.62–31.62（cue12–18）
Scene("sc-name", 22.62, 31.62, """
          <div class="hf-name" id="hf-name">HyperFrames</div>
          <div class="slogan">
            <div class="sl-line" id="sl1"><span class="sl-en">Write HTML</span></div>
            <div class="sl-line" id="sl2"><span class="sl-en">Render video</span></div>
            <div class="sl-line hot" id="sl3"><span class="sl-en">Built for agents</span></div>
          </div>
          <div class="hf-note" id="hf-note">九个英文单词 · 把自己讲得明明白白</div>"""),

# S4 报名 31.62–38.10（cue19–23）
Scene("sc-hi", 31.62, 38.10, """
          <div class="hi-main" id="hi-main">哈喽，我是叶扬</div>
          <div class="hi-sub" id="hi-sub">一个写代码的 · 带你从安装玩到成片</div>"""),

# S5 网页→MP4，渲染不是录屏 38.10–54.88（cue24–33）
Scene("sc-render", 38.10, 54.88, """
          <div class="kicker" id="rd-k">给它一个网页，还你一个 MP4</div>
          <div class="cmp">
            <div class="cmp-box" id="cmp-rec">
              <div class="cmp-h red">录屏</div>
              <div class="cmp-l">你操作一遍</div>
              <div class="cmp-l">它在旁边<strong>实时拍</strong></div>
            </div>
            <div class="cmp-box hot" id="cmp-rd">
              <div class="cmp-h green">渲染</div>
              <div class="cmp-l">像摆拍</div>
              <div class="cmp-l">每帧<strong>精确算出来</strong>再拼</div>
            </div>
          </div>"""),

# S6 Built for agents 54.88–60.78（cue34–37）
Scene("sc-agents", 54.88, 60.78, """
          <div class="kicker" id="ag-k">九个单词里，最后三个 ——</div>
          <div class="big-word" id="ag-big">Built for agents</div>
          <div class="big-sub" id="ag-sub">为 AI 而生</div>"""),

# S7 确定 60.78–66.60（cue38–41）
Scene("sc-key", 60.78, 66.60, """
          <div class="kicker" id="ck-k">凭什么敢说给 AI 用？关键两个字 ——</div>
          <div class="big-word gold" id="ck-big">确定</div>"""),

# S8 逐字节一致 66.60–79.78（cue42–48）
Scene("sc-byte", 66.60, 79.78, """
          <div class="kicker" id="bt-k">同一份网页，渲染多少遍 ——</div>
          <div class="bytes">
            <div class="byte-file" id="bf1">.html<div class="byte-sub">今天</div></div>
            <div class="byte-eq" id="be1">=</div>
            <div class="byte-file" id="bf2">.html<div class="byte-sub">明天</div></div>
            <div class="byte-eq" id="be2">=</div>
            <div class="byte-file" id="bf3">.html<div class="byte-sub">换台机器</div></div>
          </div>
          <div class="byte-out" id="bt-out">MP4 逐字节一模一样 · 同一时间点画面永远相同</div>"""),

# S9 对 AI 是命根子 79.78–97.70（cue49–56）
Scene("sc-life", 79.78, 97.70, """
          <div class="kicker" id="lf-k">对真人锦上添花，对 AI agent ——</div>
          <div class="loop-wrap">
            <svg id="loop-svg" viewBox="0 0 900 300">
              <g id="lp-nodes">
                <rect x="40" y="110" width="180" height="90" rx="14" class="lp-node"/>
                <rect x="360" y="110" width="180" height="90" rx="14" class="lp-node"/>
                <rect x="680" y="110" width="180" height="90" rx="14" class="lp-node"/>
              </g>
              <text x="130" y="165" class="lp-t">自动改</text>
              <text x="450" y="165" class="lp-t">自动渲染</text>
              <text x="770" y="165" class="lp-t">自动核对</text>
              <path d="M225 135 q65 -60 130 0" class="lp-arrow"/>
              <path d="M545 135 q65 -60 130 0" class="lp-arrow"/>
            </svg>
          </div>
          <div class="life-sub" id="lf-sub">还能跳回任意一帧检查 · 没有确定性，根本不敢撒手自己干</div>"""),

# S10 三件套 97.70–110.82（cue57–63）
Scene("sc-stack", 97.70, 110.82, """
          <div class="kicker" id="st-k">要跑起来，机器上得有三样 ——</div>
          <div class="stack">
            <div class="stack-card" id="sc1">
              <div class="stack-name">Node</div>
              <div class="stack-role">跑程序</div>
            </div>
            <div class="stack-card" id="sc2">
              <div class="stack-name">Chrome</div>
              <div class="stack-role">渲染网页</div>
            </div>
            <div class="stack-card" id="sc3">
              <div class="stack-name">FFmpeg</div>
              <div class="stack-role">编码成视频</div>
            </div>
          </div>"""),

# S11 doctor 命令 110.82–123.34（cue64–71）
Scene("sc-doctor-cmd", 110.82, 123.34, """
          <div class="kicker" id="dc-k">装没装、版本对不对，不用挨个查 ——</div>
          <div class="cmd-card" id="dc-card">
            <div class="cmd-line">$ npx hyperframes <span class="cmd-hl">doctor</span></div>
          </div>
          <div class="cmd-desc" id="dc-desc">跑一遍 · 把环境从上到下体检一次</div>"""),

# S12 录屏 doctor 123.34–139.52（cue72–80）
# 概念卡在录屏结束（125.27）后淡入；video 是顶层独立 clip（见 VIDEOS）
Scene("sc-doctor-rec", 123.34, 139.52, """
          <div class="doc-cards" id="doc-cards">
            <div class="doc-verdict" id="doc-v">绿勾 = 这一项过关</div>
            <div class="doc-green" id="doc-g">
              <span class="dg">Node ✓</span>
              <span class="dg">FFmpeg ✓</span>
              <span class="dg">Chrome ✓</span>
            </div>
            <div class="doc-note" id="doc-n">叉 = whisper / docker 可选配件 · 新版本提示 —— 都不挡路</div>
          </div>"""),

# S13 录屏 --help 139.52–164.06（cue81–96）
Scene("sc-help-rec", 139.52, 164.06, """
          <div class="help-cards" id="help-cards">
            <div class="help-verdict" id="help-v">敲一条 <span class="cmd-hl">--help</span> · 命令特别多</div>
            <div class="help-four" id="help-f">
              <span class="hf-cmd">init</span>
              <span class="hf-dot">·</span>
              <span class="hf-cmd">preview</span>
              <span class="hf-dot">·</span>
              <span class="hf-cmd">check</span>
              <span class="hf-dot">·</span>
              <span class="hf-cmd">render</span>
            </div>
            <div class="pipe-flow" id="pipe-flow">
              <span class="pf-step">规划</span><span class="pf-arrow">→</span>
              <span class="pf-step">HTML</span><span class="pf-arrow">→</span>
              <span class="pf-step">动画</span><span class="pf-arrow">→</span>
              <span class="pf-step">媒体</span><span class="pf-arrow">→</span>
              <span class="pf-step">lint</span><span class="pf-arrow">→</span>
              <span class="pf-step">preview</span><span class="pf-arrow">→</span>
              <span class="pf-step final">render</span>
            </div>
            <div class="help-tail" id="help-tail">按官方主流程走一遍 · 一集一个，慢慢来</div>
          </div>"""),

# S14 Remotion 对比 164.06–190.08（cue97–109）
Scene("sc-remotion", 164.06, 190.08, """
          <div class="kicker" id="rm-k">用代码写视频，跟 Remotion 有啥区别？</div>
          <div class="cmp">
            <div class="cmp-box" id="rm-box1">
              <div class="cmp-h mute">Remotion</div>
              <div class="cmp-l">用 <strong>React</strong> 写视频</div>
              <div class="cmp-l">得按 React 那套来</div>
            </div>
            <div class="cmp-box hot" id="rm-box2">
              <div class="cmp-h blue">HyperFrames</div>
              <div class="cmp-l"><strong>不绑框架</strong> · 标准 HTML</div>
              <div class="cmp-l">浏览器直接能打开 · 为「跳到任意一帧」而生</div>
            </div>
          </div>
          <div class="rm-soul" id="rm-soul">跳到任意一帧 —— 它的灵魂，第四集专门讲</div>"""),

# S15 卡中间空白 190.08–208.62（cue110–118）
Scene("sc-gap", 190.08, 208.62, """
          <div class="three">
            <div class="three-card" id="tc1">
              <div class="three-h">剪辑软件</div>
              <div class="three-l">给人手拖</div>
              <div class="three-b red">AI 下不了手</div>
            </div>
            <div class="three-card" id="tc2">
              <div class="three-h">录屏</div>
              <div class="three-l">能自动化</div>
              <div class="three-b red">随机 · 会抖 · 不能复现</div>
            </div>
            <div class="three-card win" id="tc3">
              <div class="three-h">HyperFrames</div>
              <div class="three-l">卡中间这块空白</div>
              <div class="three-b green">既能全自动，又确定</div>
            </div>
          </div>"""),

# S16 升华 208.62–222.02（cue119–124）
Scene("sc-rise", 208.62, 222.02, """
          <div class="rise-lead" id="rs-lead">三十多年的老手艺，突然能直接产出视频</div>
          <div class="rise-words">
            <div class="rise-line" id="rsl1">实时 · 做给人看</div>
            <div class="rise-arrow" id="rs-a">↓</div>
            <div class="rise-line hot" id="rsl2">一帧帧 · 算给机器看</div>
          </div>
          <div class="rise-note" id="rs-note">变的不是网页，是渲染的方式</div>"""),

# S17 预告＋道别 222.02–TOTAL（cue125–133）
Scene("sc-next", 222.02, total, """
          <div class="nx-lead" id="nx-lead">光说不练假把式 ——</div>
          <div class="nx-card" id="nx-card">
            <div class="nx-cmd">下一集 · init 命令</div>
            <div class="nx-sub">三十秒搭好项目 · 看工程骨架长什么样</div>
          </div>
          <div class="nx-bye" id="nx-bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 顶层录屏 clip（不可嵌套；放 scenes 之前＝下层） ----------
VIDEOS = """      <video id="rec-doctor" class="clip" data-start="123.34"
             data-duration="1.93" data-track-index="2"
             src="media/rec-doctor.mp4" muted playsinline preload="auto"></video>
      <video id="rec-help" class="clip" data-start="139.52"
             data-duration="2.80" data-track-index="2"
             src="media/rec-help.mp4" muted playsinline preload="auto"></video>"""

# ---------- 场景专属 CSS ----------
PROJECT_CSS = """
      /* 录屏窗口卡片：1280x672，上移到字幕区上方 */
      #rec-doctor, #rec-help { position:absolute; left:320px; top:128px;
        width:1280px; height:672px; object-fit:fill; }

      /* 通用 kicker / 强调（GitHub Dark 字面量） */
      .kicker { position:absolute; left:0; right:0; top:118px; text-align:center;
        font-size:52px; color:#8b949e; }
      .cmd-hl { color:#e3b341; font-family:'Consolas','Courier New',monospace; }

      /* S1 时间轴 */
      #tl-svg { position:absolute; left:50%; top:250px; margin-left:-550px;
        width:1100px; height:360px; }
      #tl-track, #tl-track2 { fill:#161b22; stroke:#30363d; stroke-width:2; }
      .keyframe { fill:#e3b341; }
      .clip-line { stroke:#8b949e; stroke-width:4; stroke-dasharray:14 12; }
      .ask-tail { position:absolute; left:0; right:0; bottom:278px; text-align:center;
        font-size:60px; color:#e6edf3; letter-spacing:.04em; }

      /* S2 流程 */
      .flow { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .flow-box { display:inline-block; width:440px; padding:48px 30px;
        background:#161b22; border:2px solid #30363d; border-radius:20px; vertical-align:middle; }
      .flow-box.hot { border-color:#1f6feb; }
      .fb-h { font-size:46px; color:#8b949e; margin-bottom:18px; }
      .fb-c { font-size:74px; color:#e6edf3; }
      .flow-arrow { display:inline-block; font-size:96px; color:#8b949e;
        margin:0 40px; vertical-align:middle; }

      /* S3 名称＋口号 */
      .hf-name { position:absolute; left:0; right:0; top:200px; text-align:center;
        font-size:150px; color:#e6edf3; letter-spacing:.06em; }
      .slogan { position:absolute; left:0; right:0; top:430px; text-align:center; }
      .sl-line { display:block; margin:14px 0; }
      .sl-en { font-size:58px; color:#8b949e; letter-spacing:.05em; }
      .sl-line.hot .sl-en { color:#e3b341; }
      .hf-note { position:absolute; left:0; right:0; bottom:268px; text-align:center;
        font-size:46px; color:#8b949e; }

      /* S4 报名 */
      .hi-main { position:absolute; left:0; right:0; top:380px; text-align:center;
        font-size:108px; color:#e6edf3; }
      .hi-sub { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:52px; color:#8b949e; }

      /* S5 / S14 对比 */
      .cmp { position:absolute; left:0; right:0; top:280px; text-align:center; }
      .cmp-box { display:inline-block; width:520px; padding:40px 44px; margin:0 24px;
        background:#161b22; border:2px solid #30363d; border-radius:20px; vertical-align:top; }
      .cmp-box.hot { border-color:#1f6feb; }
      .cmp-h { font-size:60px; margin-bottom:22px; }
      .cmp-h.red { color:#f85149; } .cmp-h.green { color:#3fb950; }
      .cmp-h.blue { color:#58a6ff; } .cmp-h.mute { color:#8b949e; }
      .cmp-l { font-size:48px; color:#e6edf3; line-height:1.7; }
      .rm-soul { position:absolute; left:0; right:0; bottom:262px; text-align:center;
        font-size:52px; color:#e3b341; }

      /* S6/S7 大字 */
      .big-word { position:absolute; left:0; right:0; top:360px; text-align:center;
        font-size:140px; color:#58a6ff; letter-spacing:.04em; }
      .big-word.gold { color:#e3b341; }
      .big-sub { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:64px; color:#8b949e; }

      /* S8 逐字节 */
      .bytes { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .byte-file { display:inline-block; width:200px; padding:40px 0; background:#161b22;
        border:2px solid #30363d; border-radius:16px; font-size:50px; color:#e6edf3; }
      .byte-sub { font-size:36px; color:#8b949e; margin-top:14px; }
      .byte-eq { display:inline-block; font-size:72px; color:#8b949e; margin:0 20px; }
      .byte-out { position:absolute; left:0; right:0; bottom:280px; text-align:center;
        font-size:52px; color:#e3b341; }

      /* S9 循环 */
      #loop-svg { position:absolute; left:50%; top:300px; margin-left:-450px;
        width:900px; height:300px; }
      .lp-node { fill:#161b22; stroke:#30363d; stroke-width:2; }
      .lp-t { fill:#e6edf3; font-size:44px; text-anchor:middle; }
      .lp-arrow { fill:none; stroke:#8b949e; stroke-width:4; }
      .life-sub { position:absolute; left:140px; right:140px; bottom:262px; text-align:center;
        font-size:50px; color:#8b949e; line-height:1.5; }

      /* S10 三件套 */
      .stack { position:absolute; left:0; right:0; top:310px; text-align:center; }
      .stack-card { display:inline-block; width:360px; margin:0 26px; padding:50px 0;
        background:#161b22; border:2px solid #30363d; border-radius:20px; }
      .stack-name { font-size:88px; color:#58a6ff; }
      .stack-role { font-size:48px; color:#8b949e; margin-top:18px; }

      /* S11 doctor 命令 */
      .cmd-card { position:absolute; left:50%; top:340px; margin-left:-480px;
        width:960px; padding:56px 60px; background:#161b22; border:2px solid #30363d;
        border-radius:18px; }
      .cmd-line { font-size:72px; color:#e6edf3; font-family:'Consolas','Courier New',monospace; }
      .cmd-desc { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:54px; color:#8b949e; }

      /* S12 doctor 概念卡（录屏结束后） */
      .doc-cards { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .doc-verdict { font-size:60px; color:#e6edf3; }
      .doc-green { margin:44px 0; }
      .dg { display:inline-block; margin:0 30px; padding:24px 50px;
        background:#161b22; border:2px solid #3fb950; border-radius:16px;
        font-size:76px; color:#3fb950; }
      .doc-note { font-size:48px; color:#8b949e; line-height:1.6; }

      /* S13 help 概念卡 */
      .help-cards { position:absolute; left:0; right:0; top:250px; text-align:center; }
      .help-verdict { font-size:56px; color:#e6edf3; }
      .help-four { margin:34px 0; }
      .hf-cmd { display:inline-block; font-size:84px; color:#e3b341; }
      .hf-dot { display:inline-block; font-size:72px; color:#8b949e; margin:0 22px; }
      .pipe-flow { margin:40px 0; }
      .pf-step { display:inline-block; font-size:48px; color:#8b949e; }
      .pf-step.final { color:#e3b341; }
      .pf-arrow { display:inline-block; font-size:44px; color:#8b949e; margin:0 14px; }
      .help-tail { font-size:46px; color:#8b949e; margin-top:8px; }

      /* S15 三象限 */
      .three { position:absolute; left:0; right:0; top:280px; text-align:center; }
      .three-card { display:inline-block; width:430px; margin:0 22px; padding:40px 36px;
        background:#161b22; border:2px solid #30363d; border-radius:20px; vertical-align:top; }
      .three-card.win { border-color:#3fb950; }
      .three-h { font-size:54px; color:#8b949e; margin-bottom:20px; }
      .three-l { font-size:46px; color:#e6edf3; line-height:1.6; }
      .three-b { margin-top:22px; font-size:50px; line-height:1.4; }
      .three-b.red { color:#f85149; } .three-b.green { color:#3fb950; }

      /* S16 升华 */
      .rise-lead { position:absolute; left:0; right:0; top:200px; text-align:center;
        font-size:62px; color:#8b949e; }
      .rise-words { position:absolute; left:0; right:0; top:380px; text-align:center; }
      .rise-line { display:block; font-size:88px; color:#e6edf3; margin:10px 0; }
      .rise-line.hot { color:#e3b341; }
      .rise-arrow { font-size:64px; color:#8b949e; }
      .rise-note { position:absolute; left:0; right:0; bottom:278px; text-align:center;
        font-size:54px; color:#8b949e; }

      /* S17 预告道别 */
      .nx-lead { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:60px; color:#8b949e; }
      .nx-card { position:absolute; left:50%; top:380px; margin-left:-520px;
        width:1040px; padding:48px 60px; background:#161b22; border:2px solid #30363d;
        border-radius:20px; text-align:center; }
      .nx-cmd { font-size:76px; color:#58a6ff; }
      .nx-sub { font-size:48px; color:#8b949e; margin-top:20px; }
      .nx-bye { position:absolute; left:0; right:0; bottom:280px; text-align:center;
        font-size:64px; color:#e6edf3; }
"""

# ---------- 场景时间轴（时间显式给秒） ----------
SCENE_JS = """
      /* S1 0–9.20 */
      tl.fromTo('#sc-ask > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#ask-k',{y:24,opacity:0,duration:.6},.2);
      tl.from('#tl-track,#tl-track2',{opacity:0,duration:.7},1.0);
      tl.from('.keyframe',{scale:0,opacity:0,duration:.5,ease:'back.out(2)',stagger:.8},2.2);
      tl.from('#ask-tail',{y:24,opacity:0,duration:.6},5.4);
      tl.to('#sc-ask > .scene-inner',{opacity:0,duration:.4},8.8);

      /* S2 9.20–22.62 */
      tl.fromTo('#sc-tool > .scene-inner',{opacity:0},{opacity:1,duration:.5},9.20);
      tl.from('#tl-k',{y:24,opacity:0,duration:.6},9.5);
      tl.from('#fb-code',{x:-50,opacity:0,duration:.7,ease:'back.out(1.4)'},11.2);
      tl.from('#fb-arrow',{opacity:0,duration:.5},13.4);
      tl.from('#fb-video',{x:50,opacity:0,duration:.7,ease:'back.out(1.4)'},14.0);
      tl.to('#sc-tool > .scene-inner',{opacity:0,duration:.4},22.22);

      /* S3 22.62–31.62 */
      tl.fromTo('#sc-name > .scene-inner',{opacity:0},{opacity:1,duration:.5},22.62);
      tl.from('#hf-name',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},23.0);
      tl.from('#sl1,#sl2,#sl3',{y:26,opacity:0,duration:.6,stagger:1.5},25.2);
      tl.from('#hf-note',{y:22,opacity:0,duration:.6},29.6);
      tl.to('#sc-name > .scene-inner',{opacity:0,duration:.4},31.22);

      /* S4 31.62–38.10 */
      tl.fromTo('#sc-hi > .scene-inner',{opacity:0},{opacity:1,duration:.5},31.62);
      tl.from('#hi-main',{y:36,opacity:0,duration:.7,ease:'back.out(1.5)'},31.9);
      tl.from('#hi-sub',{y:22,opacity:0,duration:.6},35.6);
      tl.to('#sc-hi > .scene-inner',{opacity:0,duration:.35},37.7);

      /* S5 38.10–54.88 */
      tl.fromTo('#sc-render > .scene-inner',{opacity:0},{opacity:1,duration:.5},38.10);
      tl.from('#rd-k',{y:24,opacity:0,duration:.6},38.4);
      tl.from('#cmp-rec',{x:-50,opacity:0,duration:.7,ease:'back.out(1.4)'},41.0);
      tl.from('#cmp-rd',{x:50,opacity:0,duration:.7,ease:'back.out(1.4)'},45.6);
      tl.to('#sc-render > .scene-inner',{opacity:0,duration:.4},54.48);

      /* S6 54.88–60.78 */
      tl.fromTo('#sc-agents > .scene-inner',{opacity:0},{opacity:1,duration:.5},54.88);
      tl.from('#ag-k',{y:24,opacity:0,duration:.6},55.1);
      tl.from('#ag-big',{scale:.7,opacity:0,duration:.7,ease:'back.out(1.5)'},56.8);
      tl.from('#ag-sub',{y:22,opacity:0,duration:.6},58.8);
      tl.to('#sc-agents > .scene-inner',{opacity:0,duration:.4},60.38);

      /* S7 60.78–66.60 */
      tl.fromTo('#sc-key > .scene-inner',{opacity:0},{opacity:1,duration:.5},60.78);
      tl.from('#ck-k',{y:24,opacity:0,duration:.6},61.0);
      tl.from('#ck-big',{scale:.6,opacity:0,duration:.7,ease:'back.out(1.8)'},63.4);
      tl.to('#sc-key > .scene-inner',{opacity:0,duration:.4},66.2);

      /* S8 66.60–79.78 */
      tl.fromTo('#sc-byte > .scene-inner',{opacity:0},{opacity:1,duration:.5},66.60);
      tl.from('#bt-k',{y:24,opacity:0,duration:.6},66.9);
      tl.from('#bf1,#bf2,#bf3',{y:34,opacity:0,duration:.6,ease:'back.out(1.4)',stagger:1.2},69.0);
      tl.from('#be1,#be2',{opacity:0,duration:.5,stagger:1.2},70.4);
      tl.from('#bt-out',{y:24,opacity:0,duration:.6},75.6);
      tl.to('#sc-byte > .scene-inner',{opacity:0,duration:.4},79.38);

      /* S9 79.78–97.70 */
      tl.fromTo('#sc-life > .scene-inner',{opacity:0},{opacity:1,duration:.5},79.78);
      tl.from('#lf-k',{y:24,opacity:0,duration:.6},80.0);
      tl.from('.lp-node',{opacity:0,duration:.6,stagger:.8},83.0);
      tl.from('.lp-t',{opacity:0,duration:.5,stagger:.8},83.3);
      tl.from('.lp-arrow',{opacity:0,duration:.5,stagger:.8},85.0);
      tl.from('#lf-sub',{y:22,opacity:0,duration:.7},91.0);
      tl.to('#sc-life > .scene-inner',{opacity:0,duration:.4},97.3);

      /* S10 97.70–110.82 */
      tl.fromTo('#sc-stack > .scene-inner',{opacity:0},{opacity:1,duration:.5},97.70);
      tl.from('#st-k',{y:24,opacity:0,duration:.6},98.0);
      tl.from('#sc1,#sc2,#sc3',{y:40,opacity:0,duration:.7,ease:'back.out(1.4)',stagger:1.6},100.6);
      tl.to('#sc-stack > .scene-inner',{opacity:0,duration:.4},110.42);

      /* S11 110.82–123.34 */
      tl.fromTo('#sc-doctor-cmd > .scene-inner',{opacity:0},{opacity:1,duration:.5},110.82);
      tl.from('#dc-k',{y:24,opacity:0,duration:.6},111.1);
      tl.from('#dc-card',{scale:.8,opacity:0,duration:.7,ease:'back.out(1.4)'},114.0);
      tl.from('#dc-desc',{y:22,opacity:0,duration:.6},119.4);
      tl.to('#sc-doctor-cmd > .scene-inner',{opacity:0,duration:.4},122.94);

      /* S12 123.34–139.52（录屏 123.34–125.27 顶层播放；概念卡 125.4 淡入） */
      tl.fromTo('#sc-doctor-rec > .scene-inner',{opacity:0},{opacity:1,duration:.4},125.4);
      tl.from('#doc-v',{y:24,opacity:0,duration:.6},125.7);
      tl.from('#doc-g',{y:30,opacity:0,duration:.7},127.6);
      tl.from('#doc-n',{y:22,opacity:0,duration:.6},133.6);
      tl.to('#sc-doctor-rec > .scene-inner',{opacity:0,duration:.4},139.12);

      /* S13 139.52–164.06（录屏 139.52–142.32；概念卡 142.5 淡入） */
      tl.fromTo('#sc-help-rec > .scene-inner',{opacity:0},{opacity:1,duration:.4},142.5);
      tl.from('#help-v',{y:22,opacity:0,duration:.6},142.7);
      tl.from('#help-f',{y:26,opacity:0,duration:.7},144.6);
      tl.from('#pipe-flow',{y:26,opacity:0,duration:.7},149.0);
      tl.from('#help-tail',{y:20,opacity:0,duration:.6},160.8);
      tl.to('#sc-help-rec > .scene-inner',{opacity:0,duration:.4},163.66);

      /* S14 164.06–190.08 */
      tl.fromTo('#sc-remotion > .scene-inner',{opacity:0},{opacity:1,duration:.5},164.06);
      tl.from('#rm-k',{y:24,opacity:0,duration:.6},164.3);
      tl.from('#rm-box1',{x:-50,opacity:0,duration:.7,ease:'back.out(1.4)'},167.0);
      tl.from('#rm-box2',{x:50,opacity:0,duration:.7,ease:'back.out(1.4)'},172.0);
      tl.from('#rm-soul',{y:22,opacity:0,duration:.6},184.0);
      tl.to('#sc-remotion > .scene-inner',{opacity:0,duration:.4},189.68);

      /* S15 190.08–208.62 */
      tl.fromTo('#sc-gap > .scene-inner',{opacity:0},{opacity:1,duration:.5},190.08);
      tl.from('#tc1,#tc2,#tc3',{y:40,opacity:0,duration:.7,ease:'back.out(1.4)',stagger:1.8},192.0);
      tl.to('#sc-gap > .scene-inner',{opacity:0,duration:.4},208.22);

      /* S16 208.62–222.02 */
      tl.fromTo('#sc-rise > .scene-inner',{opacity:0},{opacity:1,duration:.5},208.62);
      tl.from('#rs-lead',{y:24,opacity:0,duration:.6},208.9);
      tl.from('#rsl1',{y:26,opacity:0,duration:.6},211.0);
      tl.from('#rs-a',{opacity:0,duration:.5},213.2);
      tl.from('#rsl2',{y:26,opacity:0,duration:.7,ease:'back.out(1.5)'},214.0);
      tl.from('#rs-note',{y:22,opacity:0,duration:.6},218.4);
      tl.to('#sc-rise > .scene-inner',{opacity:0,duration:.4},221.62);

      /* S17 222.02–TOTAL */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},222.02);
      tl.from('#nx-lead',{y:24,opacity:0,duration:.6},222.3);
      tl.from('#nx-card',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},224.4);
      tl.from('#nx-bye',{y:22,opacity:0,duration:.6},231.0);
"""

# ---------- 底部字幕轨道（词时间提前，补偿 whisper 偏晚） ----------
frag = char_track(cues, chars, THEME.accent, word_lead=WHISPER_WORD_LEAD)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/audio.wav", total),
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
print("已生成 index.html（%.2f 秒，%d 幕，%d 句）"
      % (total, len(SCENES), len(cues)))
