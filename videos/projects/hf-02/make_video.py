# -*- coding: utf-8 -*-
"""HyperFrames 教程第 2 集《init 三十秒：一个项目长什么样》成片生成器。

靛蓝深＋金网格主题（沿用 hf-01：自 DARK_GOLD_GH 派生，底 #0d1b2a、金质细
网格、蓝金光斑），312.15s，17 幕。教学核心＝讲清 hyperframes init 生成的
六个文件骨架与「合成契约」：stage(#root) / clip / data-start / data-duration
/ data-track-index / GSAP paused timeline 登记 __timelines 靠 seek 跳帧。

三处嵌入真实录屏——init 生成（S2 后）、dir 六文件列表（S3）、npm run dev
预览（S15）：录屏作**顶层 clip**（StaticGuard：video 不可嵌套在另一个
data-start 元素内），先按真实时长播放，随后定格帧全屏停留数秒；dir 与
preview 两段再由 GSAP 把定格缩到屏幕左侧，右侧概念卡同屏讲解（init 段不
缩——紧接的 dir 录屏自然盖入）。页面骨架／主题／字幕／clip 外壳全部复用
videopipe。
"""
import io
import sys
from dataclasses import replace
from pathlib import Path

# projects/<name>/make_video.py -> videos/ 在 parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       DARK_GOLD_GH)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars, total = data["cues"], data["chars"], data["duration"]

# 靛蓝深＋金：与 hf-01 同一主题（底色/底部渐隐；金色 accent、字幕尺寸不变）
THEME = replace(
    DARK_GOLD_GH,
    name="indigo-gold-hf",
    bg="#0d1b2a",
    subshade=("linear-gradient(transparent, rgba(13,27,42,.55) 40%, "
              "rgba(13,27,42,.94))"),
)

# ---- GitHub Dark 辅助色（主题只给 accent/bg，其余在此固定） ----
PANEL, LINE = "#161b22", "#30363d"
INK, MUTE = "#e6edf3", "#8b949e"
BLUE, BLUE2 = "#1f6feb", "#58a6ff"
GREEN, RED, GOLD = "#3fb950", "#f85149", "#e3b341"

# ---------- 17 幕（边界严格首尾相接，交叉淡变） ----------
SCENES = [

# S1 承上＋先搭架子 0.00–13.58（cue1–9）
Scene("sc-open", 0.00, 13.58, """
          <div class="kicker" id="op-k">上一集：写一个网页，渲染成视频 · 这一集 ——</div>
          <div class="op-go" id="op-go">动手</div>
          <div class="op-wait" id="op-wait">不过，先别急着写代码</div>
          <div class="op-shelf" id="op-shelf">做任何项目，头一件事 ——<span class="op-hl">先把架子搭起来</span></div>"""),

# S2 init 命令 13.58–29.00（cue10–21）
Scene("sc-initcmd", 13.58, 29.00, """
          <div class="kicker" id="ic-k">HyperFrames 早替你想到了 —— 一条命令，三十秒</div>
          <div class="cmd-card big" id="ic-card">
            <div class="cmd-line">$ npx hyperframes <span class="ic-init" id="ic-init">init</span> <span class="ic-demo" id="ic-demo">demo</span></div>
          </div>
          <div class="ic-eq" id="ic-eq">init = initialize · 初始化</div>
          <div class="ic-tail" id="ic-tail">空格跟上项目名 · 我建一个叫 demo —— 跑给你看</div>"""),

# S3 dir 录屏＋六文件逐个认脸 35.30–86.66（cue27–53）
# scene-inner 在定格缩小时（41.92）才淡入；此前播放 dir 录屏。右侧六行
# 先全列出（暗），口播讲到哪个，哪个点亮（index 主角带金星）。
Scene("sc-files", 35.30, 86.66, """
          <div class="files-kicker" id="fl-k">满打满算六个文件 · 没一个是凑数的</div>
          <div class="flist" id="flist">
            <div class="frow lead" id="fr-index">
              <span class="fstar">★</span><span class="fname">index.html</span>
              <span class="fdesc">绝对主角 · 视频就是这一个网页</span></div>
            <div class="frow" id="fr-package">
              <span class="fdot"></span><span class="fname">package.json</span>
              <span class="fdesc">里头藏着四条快捷命令</span></div>
            <div class="frow" id="fr-meta">
              <span class="fdot"></span><span class="fname">meta.json</span>
              <span class="fdesc">项目身份证 · 名字和出生时间</span></div>
            <div class="frow" id="fr-hf">
              <span class="fdot"></span><span class="fname">hyperframes.json</span>
              <span class="fdesc">工程配置 · 素材、代理</span></div>
            <div class="frow twin" id="fr-claude">
              <span class="fdot"></span><span class="fname">CLAUDE.md</span>
              <span class="fdesc">写给 AI 助手的说明书</span></div>
            <div class="frow twin" id="fr-agents">
              <span class="fdot"></span><span class="fname">AGENTS.md</span>
              <span class="fdesc">AI 助手进门，先读这个</span></div>
          </div>"""),

# S4 打开 index · 时间写在标签上 86.66–106.58（cue54–64）
Scene("sc-time", 86.66, 106.58, """
          <div class="kicker" id="tm-k">脸认完了 · 打开主角 index.html —— 真正的门道在这儿</div>
          <div class="cmp">
            <div class="cmp-box" id="tm-edit">
              <div class="cmp-h mute">剪辑软件里</div>
              <div class="cmp-l">拿鼠标把片段</div>
              <div class="cmp-l"><strong>拖到时间轴某一秒</strong></div>
            </div>
            <div class="cmp-box hot" id="tm-hf">
              <div class="cmp-h blue">HyperFrames 这儿</div>
              <div class="cmp-l">时间不是拖出来的</div>
              <div class="cmp-l"><strong>直接写在 HTML 标签上</strong></div>
            </div>
          </div>"""),

# S5 stage #root 与关键属性 106.58–130.44（cue65–77）
Scene("sc-stage", 106.58, 130.44, """
          <div class="kicker" id="sg-k">最外层这个 div · id="root" —— 整个项目的舞台 stage</div>
          <div class="code-card" id="sg-card">
            <div class="code-line"><span class="ln">1</span><span class="tk-tag">&lt;div</span> <span class="tk-attr">id</span>=<span class="tk-str">"root"</span><span class="tk-tag">&gt;</span></div>
            <div class="code-line rel"><span class="cline-glow" id="gl-comp"></span><span class="ln">2</span>     <span class="tk-attr">data-composition-id</span>=<span class="tk-str">"main"</span></div>
            <div class="code-line rel"><span class="cline-glow" id="gl-wh"></span><span class="ln">3</span>     <span class="tk-attr">data-width</span>=<span class="tk-str">"1920"</span></div>
            <div class="code-line rel"><span class="cline-glow" id="gl-wh2"></span><span class="ln">4</span>     <span class="tk-attr">data-height</span>=<span class="tk-str">"1080"</span></div>
            <div class="code-line rel"><span class="cline-glow" id="gl-dur"></span><span class="ln">5</span>     <span class="tk-attr">data-duration</span>=<span class="tk-str">"10"</span><span class="tk-tag">&gt;</span></div>
          </div>
          <div class="sg-notes">
            <span class="sgn" id="sgn-comp">main ＝ 给整段合成起名</span>
            <span class="sgn" id="sgn-wh">1920 × 1080 ＝ 画布</span>
            <span class="sgn" id="sgn-dur">10 ＝ 总共十秒</span>
          </div>"""),

# S6 clip h1 与 start/duration 130.44–148.78（cue78–89）
Scene("sc-clip", 130.44, 148.78, """
          <div class="kicker" id="cp-k">舞台搭好 · 里头上场的，是一个个片段 clip</div>
          <div class="code-card" id="cp-card">
            <div class="code-line rel"><span class="cline-glow" id="gl-clip"></span><span class="ln">1</span><span class="tk-tag">&lt;h1</span> <span class="tk-attr">class</span>=<span class="tk-str">"clip"</span><span class="tk-tag">&gt;</span></div>
            <div class="code-line rel"><span class="cline-glow" id="gl-start"></span><span class="ln">2</span>  <span class="tk-attr">data-start</span>=<span class="tk-str">"0"</span></div>
            <div class="code-line rel"><span class="cline-glow" id="gl-cdur"></span><span class="ln">3</span>  <span class="tk-attr">data-duration</span>=<span class="tk-str">"10"</span><span class="tk-tag">&gt;</span></div>
            <div class="code-line"><span class="ln">4</span>  Title<span class="tk-tag">&lt;/h1&gt;</span></div>
          </div>
          <div class="cp-human" id="cp-human">从零秒开始上场 · 一直待到第十秒</div>"""),

# S7 时间是 DOM 的属性 148.78–158.70（cue90–94）
Scene("sc-dom", 148.78, 158.70, """
          <div class="kicker" id="dm-k">什么时候出现、待多久，全是标签上的一个数字</div>
          <div class="dom-eq">
            <span class="dom-time" id="dm-time">时间</span>
            <span class="dom-is" id="dm-is">＝</span>
            <span class="dom-attr" id="dm-attr">DOM 的属性</span>
          </div>
          <div class="dm-note" id="dm-note">这就是它最不一样的地方</div>"""),

# S8 data-track-index 轨道 158.70–188.16（cue95–110）
Scene("sc-track", 158.70, 188.16, """
          <div class="kicker" id="tk-k">旁边还有一个 ——</div>
          <div class="tk-chip" id="tk-chip"><span class="tk-attr">data-track-index</span>=<span class="tk-str">"0"</span></div>
          <div class="layers" id="layers">
            <div class="layer" id="lay2"><span class="lay-n">track 2</span></div>
            <div class="layer" id="lay1"><span class="lay-n">track 1</span></div>
            <div class="layer" id="lay0"><span class="lay-n">track 0</span></div>
          </div>
          <div class="tk-rule" id="tk-rule">数字大的盖在小的上面 · 撞一块谁在前，就看它</div>
          <div class="tk-truth" id="tk-truth">说实话：渲染时程序压根不读它 · 只给可视化编辑界面排位置</div>"""),

# S9 GSAP timeline paused 188.16–203.94（cue111–120）
Scene("sc-paused", 188.16, 203.94, """
          <div class="kicker" id="ps-k">静态位置和时间都有了 · 动画谁管？看最底下脚本</div>
          <div class="code-card narrow" id="ps-card">
            <div class="code-line"><span class="ln">1</span><span class="tk-kw">const</span> tl = gsap.timeline({</div>
            <div class="code-line rel"><span class="cline-glow" id="gl-paused"></span><span class="ln">2</span>  <span class="tk-attr">paused</span>: <span class="tk-kw">true</span></div>
            <div class="code-line"><span class="ln">3</span>})</div>
          </div>
          <div class="ps-note" id="ps-note">重点盯 paused · 这条时间轴刚建出来，先暂停住</div>"""),

# S10 登记 __timelines ＋ seek 203.94–225.26（cue121–133）
Scene("sc-seek", 203.94, 225.26, """
          <div class="kicker" id="sk-k">紧接着，把暂停的时间轴登记到一张表里</div>
          <div class="code-card" id="sk-card">
            <div class="code-line rel"><span class="cline-glow" id="gl-reg"></span><span class="ln">1</span>window.<span class="tk-attr">__timelines</span>[<span class="tk-str">"main"</span>] = tl</div>
            <div class="code-line"><span class="ln">2</span>&nbsp;</div>
            <div class="code-line rel"><span class="cline-glow" id="gl-seek"></span><span class="ln">3</span>tl.<span class="tk-attr">seek</span>(t) <span class="tk-com">// 跳到那一秒，画面立刻就位</span></div>
          </div>
          <div class="sk-why" id="sk-why">渲染器想知道第几秒 · 不用从头播放，直接 seek 跳过去</div>"""),

# S11 灵魂扣子＋第四集 225.26–235.26（cue134–139）
Scene("sc-soul", 225.26, 235.26, """
          <div class="soul-lead" id="sl-lead">上一集的扣子 ——「跳到任意一帧」是它的灵魂</div>
          <div class="soul-now" id="sl-now">你现在，大概摸到一点边了</div>
          <div class="soul-next" id="sl-next">具体怎么做到的 · 第四集专门讲</div>"""),

# S12 回 package.json · 四条命令 235.26–253.80（cue140–148）
Scene("sc-four", 235.26, 253.80, """
          <div class="kicker" id="fr4-k">index.html 看完 · 回到 package.json，四条命令不用死记</div>
          <div class="cmd4">
            <div class="c4" id="c4-dev"><div class="c4-name">dev</div><div class="c4-run">npm run dev</div><div class="c4-act">启动预览</div></div>
            <div class="c4" id="c4-check"><div class="c4-name">check</div><div class="c4-run">npm run check</div><div class="c4-act">自动检查</div></div>
            <div class="c4" id="c4-render"><div class="c4-name">render</div><div class="c4-run">npm run render</div><div class="c4-act">渲染成片</div></div>
            <div class="c4" id="c4-publish"><div class="c4-name">publish</div><div class="c4-run">npm run publish</div><div class="c4-act">发布出去</div></div>
          </div>"""),

# S13 官方主流程＋版本钉死 253.80–267.04（cue149–155）
Scene("sc-pin", 253.80, 267.04, """
          <div class="kicker" id="pn-k">这四步，正好就是官方主流程</div>
          <div class="pn-flow" id="pn-flow">
            <span class="pn-step">dev</span><span class="pn-arrow">→</span>
            <span class="pn-step">check</span><span class="pn-arrow">→</span>
            <span class="pn-step">render</span><span class="pn-arrow">→</span>
            <span class="pn-step">publish</span>
          </div>
          <div class="pin-ver" id="pin-ver">0.8.107</div>
          <div class="pin-note" id="pin-note">每一条都把版本钉死 · 跟整个系列一模一样，绝不偷偷升级</div>"""),

# S14 跑头一条 npm run dev 267.04–271.56（cue156–158）
Scene("sc-rundev", 267.04, 271.56, """
          <div class="kicker" id="rd-k2">光说不看也不行 · 跑头一条 ——</div>
          <div class="cmd-card" id="rd-card">
            <div class="cmd-line">$ npm run <span class="cmd-hl">dev</span></div>
          </div>"""),

# S15 preview 录屏＋货真价实 271.56–289.12（cue159–166）
# scene-inner 在定格缩小时（282.5）才淡入；此前播放 preview 录屏。
Scene("sc-preview", 271.56, 289.12, """
          <div class="pv-kicker" id="pv-k">别嫌它朴素 ——</div>
          <div class="pv-cards">
            <div class="pv-card" id="pv10"><span class="pv-big">10 秒</span><span class="pv-sub">货真价实的一条视频</span></div>
            <div class="pv-card" id="pvmp4"><span class="pv-big">MP4</span><span class="pv-sub">随时能渲染出来</span></div>
          </div>"""),

# S16 升华 init 立规矩 289.12–303.02（cue167–171）
Scene("sc-rise", 289.12, 303.02, """
          <div class="rise-lead" id="rs2-lead">回头看 init 这三十秒 —— 不是扔一个空文件夹让你抓瞎</div>
          <div class="rs2-rule">
            <span class="r2" id="r2-stage">舞台</span>
            <span class="r2" id="r2-clip">片段</span>
            <span class="r2" id="r2-track">轨道</span>
            <span class="r2" id="r2-tl">时间轴</span>
          </div>
          <div class="rs2-sample" id="rs2-sample">＋ 一个真能跑起来的样板 · 一口气，全给你立好了</div>"""),

# S17 预告＋道别 303.02–TOTAL（cue172–177）
Scene("sc-next", 303.02, total, """
          <div class="nx-lead" id="nx2-lead">台子既然搭好 ——</div>
          <div class="nx-card" id="nx2-card">
            <div class="nx-cmd">下一集 · 往舞台上摆片段</div>
            <div class="nx-sub">头一个真正属于你自己的片段</div>
          </div>
          <div class="nx-bye" id="nx2-bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 顶层录屏＋定格 clip（不可嵌套；放 scenes 之前＝下层） ----------
# video 按真实时长播放；紧接的 <img> 是干净定格帧。init 段定格不缩（dir
# 录屏自然盖入）；dir／preview 定格全屏停留后由 GSAP 缩到屏幕左侧。
#   rec-init  29.00 +2.40 =31.40；freeze 31.40→35.30
#   rec-dir   35.30 +1.733=37.03；freeze 37.03→86.66（41.92 缩左）
#   rec-preview 271.56+3.867=275.43；freeze 275.43→289.12（282.5 缩左）
VIDEOS = """      <video id="rec-init" class="clip" data-start="29.00"
             data-duration="2.40" data-track-index="2"
             src="media/rec-init.mp4" muted playsinline preload="auto"></video>
      <img id="freeze-init" class="clip" data-start="31.40"
             data-duration="3.90" src="media/freeze-init.png" alt="">
      <video id="rec-dir" class="clip" data-start="35.30"
             data-duration="1.73" data-track-index="2"
             src="media/rec-dir.mp4" muted playsinline preload="auto"></video>
      <img id="freeze-dir" class="clip" data-start="37.03"
             data-duration="49.63" src="media/freeze-dir.png" alt="">
      <video id="rec-preview" class="clip" data-start="271.56"
             data-duration="3.87" data-track-index="2"
             src="media/rec-preview.mp4" muted playsinline preload="auto"></video>
      <img id="freeze-preview" class="clip" data-start="275.43"
             data-duration="13.69" src="media/freeze-preview.png" alt="">"""

# ---------- 场景专属 CSS ----------
PROJECT_CSS = """
      /* 背景：金色细网格＋蓝金光斑（铺满，置于终端/卡片之下＝下层） */
      #bg-grid { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background-image:
          linear-gradient(rgba(227,179,65,.055) 1px, transparent 1px),
          linear-gradient(90deg, rgba(227,179,65,.055) 1px, transparent 1px);
        background-size:80px 80px; }
      #bg-glow { position:absolute; left:0; top:0; width:1920px; height:1080px;
        background:
          radial-gradient(720px 500px at 16% 12%, rgba(31,111,235,.17), transparent 70%),
          radial-gradient(840px 580px at 86% 84%, rgba(227,179,65,.12), transparent 70%); }

      /* 录屏窗口与定格帧：1280x672，上移到字幕区上方；定格从左上角缩放 */
      #rec-init, #rec-dir, #rec-preview,
      #freeze-init, #freeze-dir, #freeze-preview { position:absolute;
        left:320px; top:128px; width:1280px; height:672px; object-fit:fill; }
      #freeze-dir, #freeze-preview { transform-origin:0 0; }

      /* 通用 kicker / 强调（GitHub Dark 字面量） */
      .kicker { position:absolute; left:0; right:0; top:104px; text-align:center;
        font-size:48px; color:#8b949e; }
      .cmd-hl { color:#e3b341; font-family:'Consolas','Courier New',monospace; }

      /* S1 承上 */
      .op-go { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:150px; color:#e3b341; letter-spacing:.08em; }
      .op-wait { position:absolute; left:0; right:0; top:360px; text-align:center;
        font-size:66px; color:#8b949e; }
      .op-shelf { position:absolute; left:0; right:0; bottom:296px; text-align:center;
        font-size:64px; color:#e6edf3; }
      .op-hl { color:#58a6ff; }

      /* S2 init 命令 */
      .cmd-card { position:absolute; left:50%; top:330px; margin-left:-480px;
        width:960px; padding:52px 60px; background:#161b22; border:2px solid #2b3c57; box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 10px 30px rgba(0,0,0,.38);
        border-radius:18px; }
      .cmd-card.big { margin-left:-560px; width:1120px; }
      .cmd-line { font-size:66px; color:#e6edf3; font-family:'Consolas','Courier New',monospace; }
      .ic-init { color:#8b949e; } .ic-demo { color:#8b949e; }
      .ic-init.lit { color:#e3b341; text-shadow:0 0 26px rgba(227,179,65,.5); }
      .ic-demo.lit { color:#58a6ff; text-shadow:0 0 26px rgba(88,166,255,.5); }
      .ic-eq { position:absolute; left:0; right:0; top:560px; text-align:center;
        font-size:48px; color:#e3b341; }
      .ic-tail { position:absolute; left:0; right:0; bottom:286px; text-align:center;
        font-size:46px; color:#8b949e; }

      /* S3 六文件：定格缩到左上后，右侧清单（left 876＝缩后小窗右缘858之外） */
      .files-kicker { position:absolute; left:876px; top:124px; width:1020px;
        text-align:center; font-size:42px; color:#8b949e; }
      .flist { position:absolute; left:876px; top:206px; width:1020px; }
      .frow { position:relative; height:88px; border:2px solid #263042;
        border-radius:14px; margin-bottom:8px; padding:0 26px;
        background:rgba(22,27,34,.6); white-space:nowrap; }
      .fstar { display:inline-block; width:42px; font-size:40px; color:#3a3320;
        vertical-align:middle; }
      .fdot { display:inline-block; width:42px; vertical-align:middle; }
      .fname { display:inline-block; width:384px; font-size:40px; color:#6e7681;
        font-family:'Consolas','Courier New',monospace; vertical-align:middle; }
      .fdesc { display:inline-block; font-size:33px; color:#586069;
        vertical-align:middle; }
      .frow.lit { border-color:#e3b341; background:rgba(227,179,65,.10); }
      .frow.lit .fname { color:#e6edf3; }
      .frow.lit .fdesc { color:#c9d1d9; }
      .frow.lit.lead .fstar { color:#e3b341; text-shadow:0 0 18px rgba(227,179,65,.7); }
      .frow.twin.lit { border-color:#58a6ff; background:rgba(88,166,255,.10); }

      /* S4 对比 */
      .cmp { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .cmp-box { display:inline-block; width:560px; padding:44px 48px; margin:0 28px;
        background:#161b22; border:2px solid #2b3c57; box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 10px 30px rgba(0,0,0,.38); border-radius:20px; vertical-align:top; }
      .cmp-box.hot { border-color:#1f6feb; }
      .cmp-h { font-size:54px; margin-bottom:24px; }
      .cmp-h.red { color:#f85149; } .cmp-h.green { color:#3fb950; }
      .cmp-h.blue { color:#58a6ff; } .cmp-h.mute { color:#8b949e; }
      .cmp-l { font-size:48px; color:#e6edf3; line-height:1.8; }

      /* 代码卡（S5/S6/S9/S10 通用）：加宽到 1200，容纳 seek 行中文注释不溢出 */
      .code-card { position:absolute; left:50%; top:240px; margin-left:-600px;
        width:1200px; padding:34px 44px; background:#0d1521; border:2px solid #30363d;
        border-radius:16px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      .code-card.narrow { margin-left:-480px; width:960px; }
      .code-line { position:relative; font-family:'Consolas','Courier New',monospace;
        font-size:46px; line-height:1.72; color:#8b949e; white-space:nowrap; }
      .code-line.rel {}
      .ln { display:inline-block; width:60px; color:#3d4450; text-align:right;
        margin-right:28px; }
      .tk-tag { color:#7ee787; } .tk-attr { color:#58a6ff; }
      .tk-str { color:#e3b341; } .tk-kw { color:#ff7b72; } .tk-com { color:#8b949e; }
      .cline-glow { position:absolute; left:-16px; right:-16px; top:6px; bottom:6px;
        background:rgba(227,179,65,.13); border-left:5px solid #e3b341;
        border-radius:6px; opacity:0; }

      /* S5 属性小注 */
      .sg-notes { position:absolute; left:0; right:0; bottom:252px; text-align:center; }
      .sgn { display:inline-block; margin:0 26px; font-size:40px; color:#6e7681; }
      .sgn.lit { color:#e3b341; }

      /* S6 clip 人话 */
      .cp-human { position:absolute; left:0; right:0; bottom:282px; text-align:center;
        font-size:52px; color:#e3b341; }

      /* S7 时间＝DOM 属性 */
      .dom-eq { position:absolute; left:0; right:0; top:360px; text-align:center; }
      .dom-time { display:inline-block; font-size:120px; color:#e6edf3; vertical-align:middle; }
      .dom-is { display:inline-block; font-size:100px; color:#8b949e; margin:0 34px; vertical-align:middle; }
      .dom-attr { display:inline-block; font-size:110px; color:#e3b341; vertical-align:middle; }
      .dm-note { position:absolute; left:0; right:0; bottom:296px; text-align:center;
        font-size:52px; color:#8b949e; }

      /* S8 track-index */
      .tk-chip { position:absolute; left:50%; top:230px; margin-left:-420px;
        width:840px; padding:30px 44px; text-align:center; background:#0d1521;
        border:2px solid #30363d; border-radius:16px;
        font-family:'Consolas','Courier New',monospace; font-size:54px; }
      .layers { position:absolute; left:50%; top:420px; margin-left:-300px;
        width:600px; height:300px; }
      .layer { position:absolute; left:0; width:420px; height:96px;
        background:#161b22; border:2px solid #2b3c57; border-radius:14px; }
      #lay0 { top:170px; left:120px; z-index:0; }
      #lay1 { top:92px; left:60px; z-index:1; border-color:#1f6feb; }
      #lay2 { top:14px; left:0; z-index:2; border-color:#e3b341; }
      .lay-n { display:block; text-align:center; line-height:96px; font-size:44px;
        color:#c9d1d9; font-family:'Consolas','Courier New',monospace; }
      .tk-rule { position:absolute; left:0; right:0; top:770px; text-align:center;
        font-size:42px; color:#8b949e; }
      .tk-truth { position:absolute; left:120px; right:120px; bottom:250px; text-align:center;
        font-size:44px; color:#e3b341; line-height:1.5; }

      /* S9 paused */
      .ps-note { position:absolute; left:0; right:0; bottom:282px; text-align:center;
        font-size:50px; color:#8b949e; }

      /* S10 seek */
      .sk-why { position:absolute; left:0; right:0; bottom:280px; text-align:center;
        font-size:46px; color:#e3b341; }

      /* S11 灵魂 */
      .soul-lead { position:absolute; left:0; right:0; top:280px; text-align:center;
        font-size:56px; color:#8b949e; }
      .soul-now { position:absolute; left:0; right:0; top:430px; text-align:center;
        font-size:72px; color:#e6edf3; }
      .soul-next { position:absolute; left:0; right:0; bottom:296px; text-align:center;
        font-size:58px; color:#e3b341; }

      /* S12 四条命令 */
      .cmd4 { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .c4 { display:inline-block; width:380px; margin:0 22px; padding:40px 0;
        background:#161b22; border:2px solid #263042; border-radius:20px;
        vertical-align:top; }
      .c4-name { font-size:74px; color:#6e7681; font-family:'Consolas','Courier New',monospace; }
      .c4-run { font-size:34px; color:#586069; margin-top:16px; }
      .c4-act { font-size:42px; color:#6e7681; margin-top:18px; }
      .c4.lit { border-color:#1f6feb; box-shadow:0 0 30px rgba(31,111,235,.25); }
      .c4.lit .c4-name { color:#58a6ff; }
      .c4.lit .c4-act { color:#e6edf3; }

      /* S13 主流程＋版本 */
      .pn-flow { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .pn-step { display:inline-block; font-size:72px; color:#e6edf3;
        font-family:'Consolas','Courier New',monospace; }
      .pn-arrow { display:inline-block; font-size:56px; color:#8b949e; margin:0 24px; }
      .pin-ver { position:absolute; left:0; right:0; top:480px; text-align:center;
        font-size:120px; color:#e3b341; letter-spacing:.05em;
        font-family:'Consolas','Courier New',monospace; }
      .pin-note { position:absolute; left:0; right:0; bottom:282px; text-align:center;
        font-size:46px; color:#8b949e; }

      /* S15 preview 概念卡（定格缩左后居右） */
      .pv-kicker { position:absolute; left:884px; top:236px; width:976px;
        text-align:center; font-size:52px; color:#8b949e; }
      .pv-cards { position:absolute; left:884px; top:360px; width:976px;
        text-align:center; }
      .pv-card { display:block; margin:0 auto 40px; width:640px; padding:36px 0;
        background:#161b22; border:2px solid #2b3c57; border-radius:20px; }
      .pv-big { display:block; font-size:96px; color:#58a6ff;
        font-family:'Consolas','Courier New',monospace; }
      .pv-sub { display:block; font-size:42px; color:#8b949e; margin-top:12px; }

      /* S16 升华 */
      .rise-lead { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:54px; color:#8b949e; }
      .rs2-rule { position:absolute; left:0; right:0; top:380px; text-align:center; }
      .r2 { display:inline-block; width:280px; margin:0 20px; padding:54px 0;
        background:#161b22; border:2px solid #2b3c57; border-radius:20px;
        font-size:72px; color:#6e7681; }
      .r2.lit { color:#e3b341; border-color:#e3b341;
        box-shadow:0 0 30px rgba(227,179,65,.25); }
      .rs2-sample { position:absolute; left:0; right:0; bottom:286px; text-align:center;
        font-size:50px; color:#e6edf3; }

      /* S17 预告道别 */
      .nx-lead { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:58px; color:#8b949e; }
      .nx-card { position:absolute; left:50%; top:380px; margin-left:-520px;
        width:1040px; padding:46px 60px; background:#161b22; border:2px solid #2b3c57; box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 10px 30px rgba(0,0,0,.38);
        border-radius:20px; text-align:center; }
      .nx-cmd { font-size:72px; color:#58a6ff; }
      .nx-sub { font-size:46px; color:#8b949e; margin-top:18px; }
      .nx-bye { position:absolute; left:0; right:0; bottom:282px; text-align:center;
        font-size:62px; color:#e6edf3; }
"""

# ---------- 场景时间轴（时间显式给秒） ----------
SCENE_JS = """
      /* 点亮 helper：直接 set CSS（非 addClass），渲染器逐帧 seek 时任意时刻
         状态都能由 GSAP 正确还原。行点亮＝金；twin 行点亮＝蓝。 */
      function litRow(id,t){
        tl.set('#'+id,{borderColor:'#e3b341',backgroundColor:'rgba(227,179,65,.10)'},t);
        tl.set('#'+id+' .fname',{color:'#e6edf3'},t);
        tl.set('#'+id+' .fdesc',{color:'#c9d1d9'},t);
      }
      function litTwin(id,t){
        tl.set('#'+id,{borderColor:'#58a6ff',backgroundColor:'rgba(88,166,255,.10)'},t);
        tl.set('#'+id+' .fname',{color:'#e6edf3'},t);
        tl.set('#'+id+' .fdesc',{color:'#c9d1d9'},t);
      }
      function lit4(id,t){
        tl.set('#'+id,{borderColor:'#1f6feb'},t);
        tl.set('#'+id+' .c4-name',{color:'#58a6ff'},t);
        tl.set('#'+id+' .c4-act',{color:'#e6edf3'},t);
      }

      /* S1 0–13.58：op-wait 出现时 op-go 上移淡出，避免文字重叠 */
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#op-k',{y:22,opacity:0,duration:.6},.2);
      tl.from('#op-go',{scale:.6,opacity:0,duration:.8,ease:'back.out(1.6)'},1.6);
      tl.to('#op-go',{y:-40,opacity:0,duration:.5},6.5);
      tl.from('#op-wait',{y:24,opacity:0,duration:.7},6.7);
      tl.from('#op-shelf',{y:26,opacity:0,duration:.7},9.6);
      tl.to('#sc-open > .scene-inner',{opacity:0,duration:.4},13.18);

      /* S2 13.58–29.00：命令卡先出；init 19.66 亮、demo 26.26 亮 */
      tl.fromTo('#sc-initcmd > .scene-inner',{opacity:0},{opacity:1,duration:.5},13.58);
      tl.from('#ic-k',{y:22,opacity:0,duration:.6},13.9);
      tl.from('#ic-card',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},15.4);
      tl.set('#ic-init',{color:'#e3b341'},19.9);
      tl.from('#ic-eq',{y:18,opacity:0,duration:.6},22.4);
      tl.set('#ic-demo',{color:'#58a6ff'},26.4);
      tl.from('#ic-tail',{y:20,opacity:0,duration:.6},27.3);
      tl.to('#sc-initcmd > .scene-inner',{opacity:0,duration:.35},28.6);

      /* S3 35.30–86.66：dir video 35.30–37.03；定格全屏到 41.92，随后缩左，
         右侧清单同时淡入，六行先列暗、按口播逐个点亮 */
      tl.to('#freeze-dir',{x:-256,y:122,scale:.62,duration:.9,
        ease:'power2.inOut'},41.92);
      tl.fromTo('#sc-files > .scene-inner',{opacity:0},{opacity:1,duration:.4},41.92);
      tl.from('#fl-k',{y:20,opacity:0,duration:.6},42.0);
      tl.from('#flist .frow',{x:40,opacity:0,duration:.5,ease:'power1.out',
        stagger:.12},42.4);
      litRow('fr-index',44.3);
      tl.set('#fr-index .fstar',{color:'#e3b341'},44.3);
      litRow('fr-package',53.7);
      litRow('fr-meta',58.1);
      litRow('fr-hf',63.7);
      litTwin('fr-claude',68.1);
      litTwin('fr-agents',72.0);
      tl.to('#sc-files > .scene-inner',{opacity:0,duration:.4},86.26);

      /* S4 86.66–106.58 */
      tl.fromTo('#sc-time > .scene-inner',{opacity:0},{opacity:1,duration:.5},86.66);
      tl.from('#tm-k',{y:22,opacity:0,duration:.6},86.96);
      tl.from('#tm-edit',{x:-50,opacity:0,duration:.7,ease:'back.out(1.4)'},93.0);
      tl.from('#tm-hf',{x:50,opacity:0,duration:.7,ease:'back.out(1.4)'},102.2);
      tl.to('#sc-time > .scene-inner',{opacity:0,duration:.4},106.18);

      /* S5 106.58–130.44：代码卡；三行 glow＋小注贴合语音 */
      tl.fromTo('#sc-stage > .scene-inner',{opacity:0},{opacity:1,duration:.5},106.58);
      tl.from('#sg-k',{y:22,opacity:0,duration:.6},106.9);
      tl.from('#sg-card .code-line',{y:20,opacity:0,duration:.5,stagger:.3},108.4);
      tl.to('#gl-comp',{opacity:1,duration:.35},116.3);
      tl.set('#sgn-comp',{color:'#e3b341'},117.4);
      tl.to('#gl-wh,#gl-wh2',{opacity:1,duration:.35},122.9);
      tl.set('#sgn-wh',{color:'#e3b341'},124.9);
      tl.to('#gl-dur',{opacity:1,duration:.35},128.2);
      tl.set('#sgn-dur',{color:'#e3b341'},129.2);
      tl.to('#sc-stage > .scene-inner',{opacity:0,duration:.4},130.04);

      /* S6 130.44–148.78：clip 三行 glow；145.8 出「人话」条 */
      tl.fromTo('#sc-clip > .scene-inner',{opacity:0},{opacity:1,duration:.5},130.44);
      tl.from('#cp-k',{y:22,opacity:0,duration:.6},130.78);
      tl.from('#cp-card .code-line',{y:20,opacity:0,duration:.5,stagger:.28},132.2);
      tl.to('#gl-clip',{opacity:1,duration:.3},138.0);
      tl.to('#gl-start',{opacity:1,duration:.3},140.3);
      tl.to('#gl-cdur',{opacity:1,duration:.3},141.9);
      tl.from('#cp-human',{y:22,opacity:0,duration:.6},145.4);
      tl.to('#sc-clip > .scene-inner',{opacity:0,duration:.4},148.38);

      /* S7 148.78–158.70 */
      tl.fromTo('#sc-dom > .scene-inner',{opacity:0},{opacity:1,duration:.5},148.78);
      tl.from('#dm-k',{y:22,opacity:0,duration:.6},149.06);
      tl.from('#dm-time',{scale:.7,opacity:0,duration:.7,ease:'back.out(1.5)'},152.0);
      tl.from('#dm-is',{opacity:0,duration:.5},153.6);
      tl.from('#dm-attr',{scale:.7,opacity:0,duration:.7,ease:'back.out(1.5)'},156.0);
      tl.from('#dm-note',{y:20,opacity:0,duration:.6},156.9);
      tl.to('#sc-dom > .scene-inner',{opacity:0,duration:.4},158.3);

      /* S8 158.70–188.16：chip、三层堆叠、177.8 出「渲染不读」实话 */
      tl.fromTo('#sc-track > .scene-inner',{opacity:0},{opacity:1,duration:.5},158.70);
      tl.from('#tk-k',{y:22,opacity:0,duration:.6},159.0);
      tl.from('#tk-chip',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},160.6);
      tl.from('#layers .layer',{y:30,opacity:0,duration:.6,ease:'back.out(1.3)',
        stagger:.4},164.4);
      tl.from('#tk-rule',{y:20,opacity:0,duration:.6},169.0);
      tl.to('#tk-rule',{opacity:0,duration:.4},177.6);
      tl.from('#tk-truth',{y:24,opacity:0,duration:.7},177.8);
      tl.to('#sc-track > .scene-inner',{opacity:0,duration:.4},187.76);

      /* S9 188.16–203.94 */
      tl.fromTo('#sc-paused > .scene-inner',{opacity:0},{opacity:1,duration:.5},188.16);
      tl.from('#ps-k',{y:22,opacity:0,duration:.6},188.5);
      tl.from('#ps-card .code-line',{y:20,opacity:0,duration:.5,stagger:.3},193.0);
      tl.to('#gl-paused',{opacity:1,duration:.35},198.7);
      tl.from('#ps-note',{y:20,opacity:0,duration:.6},200.9);
      tl.to('#sc-paused > .scene-inner',{opacity:0,duration:.4},203.54);

      /* S10 203.94–225.26：登记行 glow 207、seek 行 glow 220.4 */
      tl.fromTo('#sc-seek > .scene-inner',{opacity:0},{opacity:1,duration:.5},203.94);
      tl.from('#sk-k',{y:22,opacity:0,duration:.6},204.28);
      tl.from('#sk-card .code-line',{y:20,opacity:0,duration:.5,stagger:.28},205.6);
      tl.to('#gl-reg',{opacity:1,duration:.35},207.0);
      tl.to('#gl-seek',{opacity:1,duration:.35},220.4);
      tl.from('#sk-why',{y:20,opacity:0,duration:.6},218.6);
      tl.to('#sc-seek > .scene-inner',{opacity:0,duration:.4},224.86);

      /* S11 225.26–235.26 */
      tl.fromTo('#sc-soul > .scene-inner',{opacity:0},{opacity:1,duration:.5},225.26);
      tl.from('#sl-lead',{y:22,opacity:0,duration:.6},225.6);
      tl.from('#sl-now',{scale:.8,opacity:0,duration:.7,ease:'back.out(1.5)'},228.6);
      tl.from('#sl-next',{y:20,opacity:0,duration:.6},231.8);
      tl.to('#sc-soul > .scene-inner',{opacity:0,duration:.4},234.86);

      /* S12 235.26–253.80：四卡按命令时刻依次点亮 */
      tl.fromTo('#sc-four > .scene-inner',{opacity:0},{opacity:1,duration:.5},235.26);
      tl.from('#fr4-k',{y:22,opacity:0,duration:.6},235.6);
      tl.from('.cmd4 .c4',{y:36,opacity:0,duration:.6,ease:'back.out(1.3)',
        stagger:.15},237.4);
      lit4('c4-dev',241.7);
      lit4('c4-check',245.2);
      lit4('c4-render',247.6);
      lit4('c4-publish',250.2);
      tl.to('#sc-four > .scene-inner',{opacity:0,duration:.4},253.4);

      /* S13 253.80–267.04 */
      tl.fromTo('#sc-pin > .scene-inner',{opacity:0},{opacity:1,duration:.5},253.80);
      tl.from('#pn-k',{y:22,opacity:0,duration:.6},254.14);
      tl.from('#pn-flow .pn-step',{y:20,opacity:0,duration:.5,stagger:.3},255.8);
      tl.from('#pn-flow .pn-arrow',{opacity:0,duration:.4,stagger:.3},256.2);
      tl.from('#pin-ver',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},260.6);
      tl.from('#pin-note',{y:20,opacity:0,duration:.6},263.6);
      tl.to('#sc-pin > .scene-inner',{opacity:0,duration:.4},266.64);

      /* S14 267.04–271.56 */
      tl.fromTo('#sc-rundev > .scene-inner',{opacity:0},{opacity:1,duration:.5},267.04);
      tl.from('#rd-k2',{y:22,opacity:0,duration:.6},267.38);
      tl.from('#rd-card',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},269.0);
      tl.to('#sc-rundev > .scene-inner',{opacity:0,duration:.3},271.16);

      /* S15 271.56–289.12：preview video 271.56–275.43；定格全屏到 282.5，
         随后缩左，右侧「10 秒 / MP4」卡同时淡入 */
      tl.to('#freeze-preview',{x:-256,y:122,scale:.62,duration:.9,
        ease:'power2.inOut'},282.5);
      tl.fromTo('#sc-preview > .scene-inner',{opacity:0},{opacity:1,duration:.4},282.5);
      tl.from('#pv-k',{y:20,opacity:0,duration:.6},282.8);
      tl.from('#pvmp4',{y:30,opacity:0,duration:.6},284.0);
      tl.from('#pv10',{y:30,opacity:0,duration:.7},286.2);
      tl.to('#sc-preview > .scene-inner',{opacity:0,duration:.4},288.72);

      /* S16 289.12–303.02 */
      tl.fromTo('#sc-rise > .scene-inner',{opacity:0},{opacity:1,duration:.5},289.12);
      tl.from('#rs2-lead',{y:22,opacity:0,duration:.6},289.46);
      tl.from('.rs2-rule .r2',{y:30,opacity:0,duration:.6,ease:'back.out(1.3)',
        stagger:.22},294.8);
      tl.set('.rs2-rule .r2',{color:'#e3b341',borderColor:'#e3b341'},295.4);
      tl.from('#rs2-sample',{y:22,opacity:0,duration:.7},300.0);
      tl.to('#sc-rise > .scene-inner',{opacity:0,duration:.4},302.62);

      /* S17 303.02–TOTAL */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},303.02);
      tl.from('#nx2-lead',{y:22,opacity:0,duration:.6},303.36);
      tl.from('#nx2-card',{scale:.85,opacity:0,duration:.7,ease:'back.out(1.4)'},305.0);
      tl.from('#nx2-bye',{y:22,opacity:0,duration:.6},309.9);
"""

# ---------- 底部字幕轨道（整体延后 0.37s） ----------
# faster-whisper 把句间停顿「吞」进后段开头，hf-02 实测 46 个停顿点字幕早于
# 真实发声，中位数 0.373s（hf-01 为 0.28）。time_offset 把整句淡入与逐字
# 变色一起平移到真实发声点。
frag = char_track(cues, chars, THEME.accent, time_offset=0.37)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/audio.wav", total),
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
print("已生成 index.html（%.2f 秒，%d 幕，%d 句）"
      % (total, len(SCENES), len(cues)))
