# -*- coding: utf-8 -*-
"""HyperFrames 教程第 6 集《给片子配上声音：媒体进场与一把响度尺》。

靛蓝深＋金网格主题（沿用 hf-01/02/03/04/05），491.835s，17 幕。教学核心＝
媒体三兄弟（img/video/audio）堂堂正正进时间轴：老契约（class=clip＋
data-start/data-duration）不变，新规矩两条——id 是身份证（video/audio
缺 id 硬错误 FROZEN/SILENT，img 仅警告）、muted 是声音立场（不表态即
error）；文件缺失 audio_src_not_found/missing_local_asset 一律真机文案；
人声自己也是一个 audio 标签；BGM 第三轨＋data-timeline-role=music＋beats
拍子地图；音量三件套 data-volume(0–3.98)/fade/media-start；客观响度尺
normalize-audio 量 LUFS（人声实测 -21.8、乐轨 -37.3、+7.5dB、写回
2.371374、幂等 withinTolerance），差距超 +12dB 创作上限拒绝（needs
16.0 dB，噪声底原理＋loudnorm/调小两正路）；id 在命令里写错只喊疼不干活
（Target audio #bgn was not found / Selector did not match: #dem）；
远程素材 autoProxy 与占位 URL 404、media-treatment --analyze 体检画面。

素材：16 take 录屏（oneoffs/record_segments.py；cut_shorts.py 粗切后由
oneoffs/cut_final.py 二次精切，片长一一等于成片窗口）＋尾帧 freeze。
终端素材 1600x920 缩左 1120x644（left:54 top:226），右侧 620px 概念卡
随口播拍点轮替；论述段全屏概念卡。

用法：
  python make_video.py              正式版（须 media/shorts＋freezes 齐备）
  python make_video.py --cards-only 仅概念卡（录屏未到位时 check/snapshot 自验）

VIDEOS 段 data-start 锚 cues 词戳、duration 为预排，代录＋cut_final 后
按实测切点二次对齐（同 hf-05 工艺）。
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

# 靛蓝深＋金：与 hf-01/02/03/04/05 同一主题
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

# ---------- 17 幕（边界严格首尾相接；时间＝成片音频秒，锚 cues 词戳） ----------
SCENES = [

# S1 开场：默片钩子＋muted 灰章＋今日主题（全屏）0.00–25.30
Scene("sc-open", 0.00, 25.30, """
          <div class="op-ep" id="op-ep">HyperFrames 教程 · 第 6 集</div>
          <div class="op-title" id="op-title">给片子配上声音</div>
          <div class="op-sub" id="op-sub">媒体进场与一把响度尺</div>

          <div class="stage" id="s1-silent">
            <div class="st-h">前五集做出来的片子</div>
            <div class="st-q-big">其实全是<strong>默片</strong></div>
          </div>

          <div class="stage" id="s1-have">
            <div class="have-grid">
              <div class="have-item" id="hv-1"><span class="have-ok">✓</span>画面</div>
              <div class="have-item" id="hv-2"><span class="have-ok">✓</span>动画</div>
              <div class="have-item" id="hv-3"><span class="have-ok">✓</span>字幕</div>
              <div class="have-item no" id="hv-4"><span class="have-no">✗</span>声音 · 空空荡荡</div>
            </div>
            <div class="s1-note">每一段录屏的 video 标签上，都写着同一个词</div>
          </div>

          <div class="stage" id="s1-mutedrow">
            <div class="mutedrows" id="mr-box">
              <div class="vtag" id="vt-1">&lt;video <span class="mt-stamp">muted</span> …&gt;</div>
              <div class="vtag" id="vt-2">&lt;video <span class="mt-stamp">muted</span> …&gt;</div>
              <div class="vtag" id="vt-3">&lt;video <span class="mt-stamp">muted</span> …&gt;</div>
            </div>
            <div class="mono-big mute-word" id="mr-word">muted</div>
          </div>

          <div class="stage" id="s1-today">
            <div class="st-h">今天这集，给片子配上声音</div>
            <div class="st-chips">
              <span class="st-chip">图片</span>
              <span class="st-chip">音乐</span>
              <span class="st-chip">视频素材</span>
              <span class="st-chip hot">堂堂正正走进时间轴</span>
            </div>
          </div>"""),

# S2 三兄弟＋老契约（终端缩左 t0 全绿＋右卡）25.30–48.74
Scene("sc-three", 25.30, 48.74, """
          <div class="kicker" id="g2-k">先说媒体三兄弟</div>
          <div class="gk">
            <div class="gk-card" id="c1-tags">
              <div class="gk-tag">三个标签，三种素材</div>
              <div class="tagrow"><span class="tag-chip img">img</span><span class="tag-d">图片</span></div>
              <div class="tagrow"><span class="tag-chip vid">video</span><span class="tag-d">视频</span></div>
              <div class="tagrow"><span class="tag-chip aud">audio</span><span class="tag-d">音频</span></div>
            </div>
            <div class="gk-card" id="c1-contract">
              <div class="gk-tag">进时间轴的老契约，不变</div>
              <div class="contract-line"><span class="mono gold">class="clip"</span></div>
              <div class="contract-line"><span class="mono gold">data-start</span></div>
              <div class="contract-line"><span class="mono gold">data-duration</span></div>
              <div class="contract-note">网页元素的时间，写在属性上——不用去时间轴上拖</div>
            </div>
            <div class="gk-card rule warn" id="c1-idwarn">
              <div class="rule-head"><span class="rule-mark warn">!</span><b>但媒体比 div 多两条新规矩</b></div>
              <div class="idwarn-h">第一条，就很要命：</div>
              <div class="idwarn-big mono">必须有 id</div>
            </div>
          </div>"""),

# S3 删 id：FROZEN/SILENT/img 仅警告（终端＋右卡轮替）48.74–88.06
Scene("sc-id", 48.74, 88.06, """
          <div class="kicker" id="g3-k">不信你看 · 把录屏视频的 id 删掉</div>
          <div class="gk">
            <div class="gk-card" id="g3-steps">
              <div class="gk-tag">实验 ①</div>
              <div class="steprow"><span class="step-n">1</span>删掉 video 身上的 <span class="mono gold">id="demo"</span></div>
              <div class="steprow"><span class="step-n">2</span>存盘，别的什么都不动</div>
              <div class="steprow"><span class="step-n">3</span>跑 check</div>
            </div>
            <div class="gk-card rule err" id="g3-frozen">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>media_missing_id</b><span class="rule-exit">exit 1</span></div>
              <div class="rule-cn">有起始时间，却没有 id —— 渲染器靠 id 把媒体登记进时间轴</div>
              <div class="frozen-big">FROZEN</div>
              <div class="rule-foot">这个视频，在渲染时会冻住</div>
            </div>
            <div class="gk-card rule err" id="g3-silent">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>音频版同款</b><span class="rule-exit">exit 1</span></div>
              <div class="frozen-big silent">SILENT</div>
              <div class="rule-cn">没有 id，渲染出来就是哑巴</div>
            </div>
            <div class="gk-card" id="g3-diff">
              <div class="gk-tag">记住这个差别</div>
              <div class="diffrow"><span class="tag-chip img">img</span><span class="diff-t">不写 id → <b class="amber-t">只是警告</b>，Studio 不好点选</span></div>
              <div class="diffrow"><span class="tag-chip vid">video</span><span class="diff-t">不写 id → <b class="red-t">硬错误</b></span></div>
              <div class="diffrow"><span class="tag-chip aud">audio</span><span class="diff-t">不写 id → <b class="red-t">硬错误</b></span></div>
              <div class="goldword-sm">媒体要进场，先上身份证</div>
            </div>
          </div>"""),

# S4 muted 声音立场（终端＋右卡岔路）88.06–113.40
Scene("sc-muted", 88.06, 113.40, """
          <div class="kicker" id="g4-k">video 还得多回答一个问题：这段素材，到底有没有声音？</div>
          <div class="gk">
            <div class="gk-card" id="g4-q">
              <div class="gk-tag">录屏没开麦克风</div>
              <div class="g4-qline">无声？有声？<strong>必须表个态</strong></div>
            </div>
            <div class="gk-card" id="g4-fork">
              <div class="forkrow" id="fk-mute">
                <span class="fork-n">①</span>
                <div>无声素材，老老实实写<div class="mono gold fork-code">muted</div></div>
              </div>
              <div class="forkrow" id="fk-audio">
                <span class="fork-n">②</span>
                <div>素材自己带声、想保留，写<div class="mono gold fork-code">data-has-audio="true"</div></div>
              </div>
            </div>
            <div class="gk-card rule err" id="g4-error">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>不表态呢？</b><span class="rule-exit">exit 1</span></div>
              <div class="rule-cn">它连一个默认值都不肯替你猜</div>
              <div class="g4-twoline">
                <div class="g4-case">有声没声明 → 声画对不上，<b class="red-t">你的事故</b></div>
                <div class="g4-case">无声不声明 → 它也<b class="red-t">不替你背锅</b></div>
              </div>
            </div>
          </div>"""),

# S5 扣子1：src 改坏字母 → audio_src_not_found（终端＋右卡）113.40–133.48
Scene("sc-missingfile", 113.40, 133.48, """
          <div class="kicker" id="g5-k">上集埋的两个扣子，挨个兑现 · 第一个：文件找不到</div>
          <div class="gk">
            <div class="gk-card" id="g5-step">
              <div class="gk-tag">音频的 src，改坏一个字母</div>
              <div class="codeblock">
                <div class="cb-line dim">src="media/<span class="cb-good">voice</span>.wav"</div>
                <div class="cb-line bad">src="media/<span class="cb-bad">voise</span>.wav"</div>
              </div>
            </div>
            <div class="gk-card rule err" id="g5-err">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>audio_src_not_found</b><span class="rule-exit">exit 1</span></div>
              <div class="rule-cn">音频引用了工程里不存在的文件</div>
              <div class="rule-foot hot">The rendered video <b>will be silent</b>——渲染出来，将会是静音的</div>
            </div>
          </div>"""),

# S6 silently skip＋退出码 CI（终端＋三连谱）133.48–156.46
Scene("sc-skip", 133.48, 156.46, """
          <div class="kicker" id="g6-k">视频和图片版本的报错，更损</div>
          <div class="gk">
            <div class="gk-card rule err" id="g6-skip">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>missing_local_asset</b><span class="rule-exit">exit 1</span></div>
              <div class="rule-cn">渲染器会悄悄跳过它们 —— <span class="mono gold">silently skip</span></div>
              <div class="rule-foot">不跑 check，就拿到一个缺胳膊少腿的片子，还以为一切正常</div>
            </div>
            <div class="gk-card" id="g6-spec">
              <div class="gk-tag">找不到的文件，三种下场</div>
              <div class="specrow aud"><span class="tag-chip aud">audio</span><span>渲染成片 <b class="red-t">静音</b></span></div>
              <div class="specrow vid"><span class="tag-chip vid">video / img</span><span>被悄悄 <b class="red-t">跳过</b></span></div>
              <div class="specrow remote dim"><span class="tag-chip url">https://</span><span>占位网址 → <b class="amber-t">404</b>（后面讲）</span></div>
            </div>
            <div class="gk-card" id="g6-ci">
              <div class="g6-ci-h">路径写错，眼睛扫十遍都漏，机器一次就抓</div>
              <div class="ci-mini"><span class="mono gold">check 退出码 = 1</span><span>→ CI 那关，你过不去</span></div>
            </div>
          </div>"""),

# S7 人声就是一个 audio 标签（全屏 C5）156.46–171.42
Scene("sc-avoice", 156.46, 171.42, """
          <div class="kicker" id="g7-k">音频怎么进场？说个好玩的</div>
          <div class="audiocard" id="c7-card">
            <div class="ac-note">你听了九分钟的、叶扬的这条声音，在工程里就是——</div>
            <div class="ac-tag" id="c7-tag">&lt;audio <span class="ac-hl">id="a-roll-audio"</span>
              <span class="ac-dim">class="clip" data-track-index="2"</span>
              <span class="ac-hl">data-volume="1"</span> src="…"&gt;</div>
            <div class="ac-props">
              <span class="acp" id="acp-1">id：a-roll-audio</span>
              <span class="acp" id="acp-2">待在第二轨</span>
              <span class="acp" id="acp-3">data-volume = 1</span>
            </div>
            <div class="goldword-sm big" id="c7-word">主角自己，也不过是个标签</div>
          </div>"""),

# S8 同轨层叠＋BGM 第三轨（终端＋轨示意）171.42–189.02
Scene("sc-layer", 171.42, 189.02, """
          <div class="kicker" id="g8-k">再加背景音乐，有个新讲究</div>
          <div class="gk">
            <div class="gk-card" id="g8-bad">
              <div class="gk-tag">别跟人声挤在同一条轨上</div>
              <div class="minitracks" id="mt-bad">
                <div class="mt-row"><span class="mt-rail">轨 2</span>
                  <div class="mt-bar voice">voice.wav</div><div class="mt-bar music bad">music.wav</div></div>
                <div class="mt-row dim"><span class="mt-rail">轨 3</span><span class="mt-empty">空着</span></div>
              </div>
            </div>
            <div class="gk-card rule warn" id="g8-warn">
              <div class="rule-head"><span class="rule-mark warn">⚠</span><b>duplicate_audio_track</b><span class="rule-exit pass-text">passed</span></div>
              <div class="rule-cn">两段有声素材时间叠着 → <b class="amber-t">层叠播放</b></div>
              <div class="rule-foot hot">两层声音糊成一团，谁也听不清 · 警告但不拦</div>
            </div>
            <div class="gk-card rule pass" id="g8-good">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>正解：BGM 单独放第三轨</b></div>
              <div class="minitracks" id="mt-good">
                <div class="mt-row"><span class="mt-rail">轨 2</span><div class="mt-bar voice">voice.wav</div></div>
                <div class="mt-row"><span class="mt-rail">轨 3</span><div class="mt-bar music ok">music.wav</div></div>
              </div>
            </div>
          </div>"""),

# S9 music 角色＋beats 拍子地图（终端＋C6）189.02–211.82
Scene("sc-beats", 189.02, 211.82, """
          <div class="kicker" id="g9-k">放好了，再补一个属性</div>
          <div class="gk">
            <div class="gk-card" id="g9-role">
              <div class="gk-tag">眼熟吗？上集 beats 冲我甩过脸子：没找到音乐轨</div>
              <div class="codeblock">
                <div class="cb-line">&lt;audio …&gt;</div>
                <div class="cb-line"><span class="cb-hex">data-timeline-role="music"</span></div>
              </div>
              <div class="rule-foot">今天，音乐轨来了</div>
            </div>
            <div class="gk-card rule pass" id="g9-beats">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>beats 立刻有活干</b></div>
              <div class="rule-cn">把整段音乐的拍子一个个标出来，写进 beats 文件夹</div>
              <div class="beatdots" id="beat-dots"></div>
              <div class="rule-foot gold-t">Wrote 23 beats（bpm 243.9）—— 想做卡点，这就是地图</div>
            </div>
          </div>"""),

# S10 音量三件套（全屏 C7）211.82–239.46
Scene("sc-volume", 211.82, 239.46, """
          <div class="kicker" id="g10-k">音量本身，三个小件</div>
          <div class="vthree">
            <div class="vt-card" id="vtc-1">
              <div class="vt-name mono">data-volume</div>
              <div class="vt-scale"><span class="vts">0</span><span class="vts hot">1 原样</span><span class="vts">3.98</span></div>
              <div class="vt-note">零是静音 · 最大 3.98 ＝ 硬加 <b class="amber-t">+12 dB</b></div>
            </div>
            <div class="vt-card" id="vtc-2">
              <div class="vt-name mono">data-fade-in / -out</div>
              <div class="fade-demo"><span class="fd-up">片头轻轻起来</span><span class="fd-down">片尾慢慢收掉</span></div>
              <div class="vt-note">不砸耳朵</div>
            </div>
            <div class="vt-card" id="vtc-3">
              <div class="vt-name mono">data-media-start</div>
              <div class="vt-note">只想用素材中间一截？告诉它<b>从素材的第几秒开始读</b></div>
              <div class="vt-note dim">clip 有多长用多少，多出来的，不读</div>
            </div>
          </div>"""),

# S11 LUFS 客观尺（终端 norm-dry＋C8 双表）239.46–273.24
Scene("sc-lufs", 239.46, 273.24, """
          <div class="kicker" id="g11-k">人声一轨，音乐一轨 —— 谁响，谁轻？</div>
          <div class="gk">
            <div class="gk-card" id="c11-ear">
              <div class="gk-tag">凭耳朵拖滑块？</div>
              <div class="ear-line">拖三遍，给你<b class="red-t">三个数</b></div>
              <div class="ear-line dim">早上拖和半夜拖，又不一样</div>
            </div>
            <div class="gk-card" id="c11-ruler">
              <div class="gk-tag">HyperFrames 给了一把客观尺</div>
              <div class="mono-big gold" id="norm-cmd">normalize-audio</div>
              <div class="rule-cn">量的不是波形高矮，是 <b class="blue2-t">LUFS</b> 积分响度</div>
              <div class="rule-foot dim">耳朵真正感受到的那一种「这条音有多响」</div>
            </div>
            <div class="gk-card" id="c11-meters">
              <div class="gk-tag">参考轨、目标轨，两条都量 · 本片实测</div>
              <div class="meters">
                <div class="meter voice"><span class="m-who">人声 #voice</span><span class="m-val">-21.8</span><span class="m-u">LUFS</span></div>
                <div class="meter music"><span class="m-who">音乐 #bgm</span><span class="m-val">-37.3</span><span class="m-u">LUFS</span></div>
              </div>
              <div class="rule-foot">差距 +15.5 dB · 建议增益 <span class="mono gold">+7.5 dB</span></div>
            </div>
          </div>"""),

# S12 --write 写回与幂等（终端 norm-write）273.24–287.26
Scene("sc-write", 273.24, 287.26, """
          <div class="kicker" id="g12-k">先空跑，只报数，不碰文件</div>
          <div class="gk">
            <div class="gk-card" id="g12-dry">
              <div class="gk-tag">dry-run · <span class="mono">"wrote": false</span></div>
              <div class="json-lines">
                <div>"referenceLufs": <b>-21.8</b></div>
                <div>"targetLufs": <b>-37.26</b></div>
                <div>"gainDb": <b class="gold-t">7.5</b></div>
              </div>
            </div>
            <div class="gk-card rule pass" id="g12-write">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>加 --write，才写回</b></div>
              <div class="codeblock"><div class="cb-line">data-volume="<span class="cb-hex">2.371374</span>"</div></div>
            </div>
            <div class="gk-card" id="g12-idem">
              <div class="gk-tag">写完再跑第二遍</div>
              <div class="idem-big">withinTolerance: true</div>
              <div class="rule-foot">已经齐了，在容差之内，不动 —— <b class="green-t">幂等的，你敢重复点</b></div>
            </div>
          </div>"""),

# S13 +12dB 天花板＋噪声底＋两正路（终端 ceiling＋C9）287.26–328.90
Scene("sc-ceiling", 287.26, 328.90, """
          <div class="kicker" id="g13-k">但这把尺子，有脾气</div>
          <div class="gk">
            <div class="gk-card rule err" id="g13-refuse">
              <div class="rule-head"><span class="rule-mark err">✗</span><b>故意把音乐压得很轻再去追人声</b><span class="rule-exit">exit 1</span></div>
              <div class="json-lines bad">
                <div>"ok": <b>false</b></div>
                <div>"needs": <b class="red-t">16.0 dB</b></div>
              </div>
              <div class="rule-foot hot">beyond the <b>+12 dB</b> authoring ceiling —— 直接拒绝</div>
            </div>
            <div class="gk-card" id="g13-why">
              <div class="gk-tag">为什么？增益这东西，信号和噪声底一起抬</div>
              <div class="noise-demo">
                <div class="nd-row"><span class="nd-l">原信号</span><span class="nd-bar sig"></span></div>
                <div class="nd-row"><span class="nd-l">噪声底</span><span class="nd-bar floor"></span></div>
                <div class="nd-row up"><span class="nd-l">硬加 16 dB</span><span class="nd-bar sig2"></span><span class="nd-bar floor2"></span></div>
              </div>
              <div class="rule-foot hot">音乐没响，沙沙声先响</div>
            </div>
            <div class="gk-card rule pass" id="g13-paths">
              <div class="rule-head"><span class="rule-mark pass">✓</span><b>它递了两条正路，别在混音台上硬拗</b></div>
              <div class="fixrow"><span class="fix-n">①</span>回源文件做响度归一化，如 ffmpeg 的 <span class="mono gold">loudnorm</span></div>
              <div class="fixrow"><span class="fix-n">②</span>干脆把人声<b>调小</b>，让两边靠近</div>
            </div>
          </div>"""),

# S14 扣子2：命令里写错 id 只喊疼不干活（终端 badid＋C10）328.90–401.26
Scene("sc-badid", 328.90, 401.26, """
          <div class="kicker" id="g14-k">第二个扣子：媒体 id 对不上 —— 真机一验，得拆成两种情况</div>
          <div class="gk">
            <div class="gk-card" id="g14-split">
              <div class="splitrow"><span class="split-a">元素<strong>不写</strong> id</span><span class="split-r red-t">硬错误：冻帧、哑巴</span></div>
              <div class="splitrow"><span class="split-a">命令里把 id <strong>写错</strong></span><span class="split-r gold-t">另一种待遇 ↓</span></div>
            </div>
            <div class="gk-card rule err" id="g14-bgn">
              <div class="rule-head compact"><span class="rule-mark err">✗</span><b>normalize --target <span class="mono">#bgn</span></b><span class="rule-exit">exit 1</span></div>
              <div class="rule-cn mono-sm">Target audio #bgn was not found</div>
              <div class="rule-foot hot">只喊疼，不干活：工程文件一个字节没改，渲染压根没开始</div>
            </div>
            <div class="gk-card rule err" id="g14-trt">
              <div class="rule-head compact"><span class="rule-mark err">✗</span><b>media-treatment --selector <span class="mono">#dem</span></b><span class="rule-exit">exit 1</span></div>
              <div class="rule-cn mono-sm">Selector did not match: #dem —— 一个元素都没匹配到，甩手就走</div>
            </div>
            <div class="gk-card silent" id="g14-law">
              <div class="law-big">命令跑完</div>
              <div class="law-big law-neq">≠ 活干完</div>
              <div class="law-sub">脚本里不查退出码，连个响声都听不见 · 同上集 #sut 鬼故事</div>
              <div class="law-three">
                <span class="l3">退出码要看</span>
                <span class="l3">屏幕上的话要读</span>
                <span class="l3 hot">文件变没变，亲眼确认</span>
              </div>
            </div>
          </div>"""),

# S15 远程素材 autoProxy＋media-treatment（终端 placeholder/treatment）401.26–437.86
Scene("sc-remote", 401.26, 437.86, """
          <div class="kicker" id="g15-k">两件小事，快速带过</div>
          <div class="gk">
            <div class="gk-card" id="g15-proxy">
              <div class="gk-tag">远程素材：src 里直接写网址</div>
              <div class="rule-cn">默认走<b class="blue2-t">自动代理</b>：渲染时本地资源服务器替你把文件取回来</div>
              <div class="rule-foot hot">写个 <span class="mono">example.com</span> 占位网址 → error：它分得清真素材和忘了填的坑</div>
            </div>
            <div class="gk-card" id="g15-treat">
              <div class="gk-tag"><span class="mono gold">media-treatment --analyze</span> · 画面本身也能体检</div>
              <div class="rule-cn">抽几帧量曝光、量对比度 → 开一张调参的方子 → apply 确定性写回工程</div>
              <div class="rule-foot">深色录屏普遍偏暗这种事，它一眼量出来</div>
            </div>
          </div>"""),

# S16 收尾三件事（全屏 C11）437.86–457.44
Scene("sc-recap", 437.86, 457.44, """
          <div class="kicker" id="g16-k">收尾 · 记住三件事</div>
          <div class="recap3">
            <div class="rp-card" id="rp-1">
              <div class="rp-n">①</div>
              <div class="rp-h">素材进工程</div>
              <div class="rp-l"><b>id</b> 是身份证 · <b>muted</b> 是声音立场</div>
              <div class="rp-l hot">文件必须真的在</div>
            </div>
            <div class="rp-card" id="rp-2">
              <div class="rp-n">②</div>
              <div class="rp-h">多轨别叠一块儿</div>
              <div class="rp-l">响度别靠猜</div>
              <div class="rp-l">让 <span class="mono gold">normalize-audio</span> 拿 LUFS 量</div>
            </div>
            <div class="rp-card" id="rp-3">
              <div class="rp-n">③</div>
              <div class="rp-h">跑完 ≠ 干完</div>
              <div class="rp-l">屏幕上每句话都要读</div>
              <div class="rp-l hot">退出码一个都别漏</div>
            </div>
          </div>"""),

# S17 行动件＋hf-07 预告＋道别 457.44–TOTAL
Scene("sc-action", 457.44, total, """
          <div class="stage" id="s17-action">
            <div class="kicker-static">行动件：打开你自己的工程</div>
            <div class="acl">
              <div class="acl-row" id="a17-1"><span class="acl-n">①</span>加一条音轨，配音也行、音乐也行</div>
              <div class="acl-row" id="a17-2"><span class="acl-n">②</span>跑一遍 check，把红色错误清干净</div>
              <div class="acl-row" id="a17-3"><span class="acl-n">③</span>再跑 normalize-audio，亲眼看一眼两条轨差多少 LU</div>
            </div>
          </div>

          <div class="stage" id="s17-next">
            <div class="nx-h">下一集</div>
            <div class="nx-card">把每一帧看清楚</div>
            <div class="nx-lines">
              <div id="nx-l1">声音画面都齐了，可渲染一段要九分钟、全片六七十分钟</div>
              <div id="nx-l2">总不能闭着眼等 —— <b class="blue2-t">preview</b> 实时看，<b class="blue2-t">snapshot</b> 把任意一秒拍成照片</div>
            </div>
          </div>

          <div class="bye" id="bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 顶层录屏/定格 clip（不可嵌套；放 scenes 之前＝下层） ----------
# 终端素材 1600x920 缩左 1120x644，右 620px 给概念卡。
# 预排锚口播词戳；代录＋cut_shorts/cut_final 后按实测切点二次对齐。
if CARDS_ONLY:
    VIDEOS = "      <!-- --cards-only：录屏 clip 待代录后填入 -->"
else:
    VIDEOS = """      <!-- S2 25.30–48.74：好工程 check 全绿（老契约成立） -->
      <video id="rec2-good" class="clip term" data-start="30.80"
             data-duration="17.90" data-track-index="2"
             src="media/shorts/good-run.mp4" muted playsinline preload="auto"></video>

      <!-- S3 48.74–88.06：删 id → FROZEN 长停（SILENT/img 差别由右卡讲） -->
      <video id="rec3-edit" class="clip term" data-start="50.10"
             data-duration="3.20" data-track-index="2"
             src="media/shorts/del-id-edit.mp4" muted playsinline preload="auto"></video>
      <img id="img3-edit" class="clip term" data-start="53.30"
           data-duration="0.70" src="media/freezes/del-id-edit.png" alt="">
      <video id="rec3-run" class="clip term" data-start="54.00"
             data-duration="3.00" data-track-index="2"
             src="media/shorts/noid-run.mp4" muted playsinline preload="auto"></video>
      <img id="img3-run" class="clip term" data-start="57.00"
           data-duration="31.06" src="media/freezes/noid-run.png" alt="">

      <!-- S4 88.06–113.40：删 muted → 不表态 error -->
      <video id="rec4-edit" class="clip term" data-start="88.60"
             data-duration="3.00" data-track-index="2"
             src="media/shorts/del-muted-edit.mp4" muted playsinline preload="auto"></video>
      <img id="img4-edit" class="clip term" data-start="91.60"
           data-duration="0.80" src="media/freezes/del-muted-edit.png" alt="">
      <video id="rec4-run" class="clip term" data-start="101.40"
             data-duration="3.00" data-track-index="2"
             src="media/shorts/nomuted-run.mp4" muted playsinline preload="auto"></video>
      <img id="img4-run" class="clip term" data-start="104.40"
           data-duration="9.00" src="media/freezes/nomuted-run.png" alt="">

      <!-- S5 113.40–133.48：voice→voise → will be silent -->
      <video id="rec5-edit" class="clip term" data-start="120.10"
             data-duration="3.40" data-track-index="2"
             src="media/shorts/bad-src-edit.mp4" muted playsinline preload="auto"></video>
      <img id="img5-edit" class="clip term" data-start="123.50"
           data-duration="0.60" src="media/freezes/bad-src-edit.png" alt="">
      <video id="rec5-run" class="clip term" data-start="124.10"
             data-duration="3.00" data-track-index="2"
             src="media/shorts/badaudio-run.mp4" muted playsinline preload="auto"></video>
      <img id="img5-run" class="clip term" data-start="127.10"
           data-duration="6.38" src="media/freezes/badaudio-run.png" alt="">

      <!-- S6 133.48–156.46：missing_local_asset silently skip -->
      <video id="rec6-run" class="clip term" data-start="135.90"
             data-duration="4.20" data-track-index="2"
             src="media/shorts/missing-run.mp4" muted playsinline preload="auto"></video>
      <img id="img6-run" class="clip term" data-start="140.10"
           data-duration="16.36" src="media/freezes/missing-run.png" alt="">

      <!-- S8 171.42–189.02：同轨层叠 warning 但 passed -->
      <video id="rec8-run" class="clip term" data-start="176.90"
             data-duration="4.20" data-track-index="2"
             src="media/shorts/sametrack-run.mp4" muted playsinline preload="auto"></video>
      <img id="img8-run" class="clip term" data-start="181.10"
           data-duration="7.92" src="media/freezes/sametrack-run.png" alt="">

      <!-- S9 189.02–211.82：beats 23 拍 -->
      <video id="rec9-run" class="clip term" data-start="203.00"
             data-duration="6.40" data-track-index="2"
             src="media/shorts/beats-run.mp4" muted playsinline preload="auto"></video>
      <img id="img9-run" class="clip term" data-start="209.40"
           data-duration="2.42" src="media/freezes/beats-run.png" alt="">

      <!-- S11 239.46–273.24：normalize dry JSON -21.8/-37.3/7.5 -->
      <video id="rec11-run" class="clip term" data-start="263.90"
             data-duration="5.50" data-track-index="2"
             src="media/shorts/norm-dry.mp4" muted playsinline preload="auto"></video>
      <img id="img11-run" class="clip term" data-start="269.40"
           data-duration="3.84" src="media/freezes/norm-dry.png" alt="">

      <!-- S12 273.24–287.26：--write 2.371374 → withinTolerance -->
      <video id="rec12-run" class="clip term" data-start="274.80"
             data-duration="12.46" data-track-index="2"
             src="media/shorts/norm-write.mp4" muted playsinline preload="auto"></video>

      <!-- S13 287.26–328.90：needs 16.0 dB 拒绝长停 -->
      <video id="rec13-run" class="clip term" data-start="291.20"
             data-duration="7.80" data-track-index="2"
             src="media/shorts/ceiling.mp4" muted playsinline preload="auto"></video>
      <img id="img13-run" class="clip term" data-start="299.00"
           data-duration="29.90" src="media/freezes/ceiling.png" alt="">

      <!-- S14 328.90–401.26：#bgn not found → #dem did not match -->
      <video id="rec14-run" class="clip term" data-start="348.80"
             data-duration="9.60" data-track-index="2"
             src="media/shorts/badid.mp4" muted playsinline preload="auto"></video>
      <img id="img14-run" class="clip term" data-start="358.40"
           data-duration="13.80" src="media/freezes/badid-bgn.png" alt="">
      <img id="img14-trt" class="clip term" data-start="372.20"
           data-duration="3.20" src="media/freezes/badid-trt.png" alt="">
      <video id="rec14-trt" class="clip term" data-start="375.40"
             data-duration="3.60" data-track-index="2"
             src="media/shorts/treatment-run.mp4" muted playsinline preload="auto"></video>
      <img id="img14-done" class="clip term" data-start="379.00"
           data-duration="22.26" src="media/freezes/badid-trt.png" alt="">

      <!-- S15 401.26–437.86：example.com 404 → media-treatment analyze -->
      <video id="rec15-url" class="clip term" data-start="408.80"
             data-duration="4.20" data-track-index="2"
             src="media/shorts/placeholder-run.mp4" muted playsinline preload="auto"></video>
      <img id="img15-url" class="clip term" data-start="413.00"
           data-duration="8.80" src="media/freezes/placeholder-run.png" alt="">
      <video id="rec15-treat" class="clip term" data-start="423.90"
             data-duration="11.60" data-track-index="2"
             src="media/shorts/treatment.mp4" muted playsinline preload="auto"></video>
      <img id="img15-treat" class="clip term" data-start="435.50"
           data-duration="2.36" src="media/freezes/treatment.png" alt="">"""

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
      #rec2-good,
      #rec3-edit, #img3-edit, #rec3-run, #img3-run,
      #rec4-edit, #img4-edit, #rec4-run, #img4-run,
      #rec5-edit, #img5-edit, #rec5-run, #img5-run,
      #rec6-run, #img6-run,
      #rec8-run, #img8-run,
      #rec9-run, #img9-run,
      #rec11-run, #img11-run, #rec12-run,
      #rec13-run, #img13-run,
      #rec14-run, #img14-run, #img14-trt, #rec14-trt, #img14-done,
      #rec15-url, #img15-url, #rec15-treat, #img15-treat
        { position:absolute;
        left:54px; top:226px; width:1120px; height:644px; object-fit:fill;
        border-radius:10px; box-shadow:0 18px 60px rgba(0,0,0,.55); }

      /* 通用 */
      .kicker { position:absolute; left:0; right:0; top:40px; text-align:center;
        font-size:42px; color:#8b949e; }
      .kicker-static { text-align:center; font-size:44px; color:#8b949e; margin-bottom:36px; }
      .mono { font-family:'Consolas','Courier New',monospace; color:#e6edf3; }
      .mono.gold, .gold-t { color:#e3b341; }
      .mono-big { font-family:'Consolas','Courier New',monospace; font-size:64px;
        text-align:center; margin:18px 0; }
      .mono-sm { font-family:'Consolas','Courier New',monospace; font-size:28px;
        color:#ffa198; line-height:1.5; margin:8px 0; }
      .red-t { color:#ffa198; } .green-t { color:#7ee787; }
      .amber-t { color:#e3b341; } .blue2-t { color:#58a6ff; }
      .goldword-sm { margin-top:18px; text-align:center; font-size:44px;
        color:#e3b341; letter-spacing:.03em; }
      .goldword-sm.big { font-size:52px; margin-top:26px; }

      /* ===== 右卡（终端幕）：gk 容器固定，gk-card 同位置轮替 ===== */
      .gk { position:absolute; left:1200px; top:128px; width:620px; height:800px; }
      .gk-card { position:absolute; left:0; top:0; width:620px; box-sizing:border-box;
        background:#161b22; border:2px solid #30363d; border-radius:18px;
        padding:30px 34px; box-shadow:0 14px 40px rgba(0,0,0,.45); }
      .gk-tag { font-size:33px; color:#58a6ff; line-height:1.5; margin-bottom:18px; }
      .gk-card.rule { padding-top:24px; }
      .rule-head { display:flex; align-items:center; font-size:32px; margin-bottom:16px; }
      .rule-head b { color:#e6edf3; font-weight:600; }
      .rule-head.compact { font-size:27px; }
      .rule-mark { display:inline-flex; align-items:center; justify-content:center;
        width:50px; height:50px; border-radius:50%; font-size:32px; margin-right:13px; }
      .rule-mark.warn { background:rgba(210,153,34,.16); color:#d29922; }
      .rule-mark.err { background:rgba(248,81,73,.16); color:#f85149; }
      .rule-mark.pass { background:rgba(63,185,80,.16); color:#3fb950; }
      .rule-exit { margin-left:auto; font-size:27px; color:#8b949e; }
      .rule-exit.pass-text, .pass-text { color:#7ee787; }
      .gk-card.rule.warn { border-color:#5e4a1e; }
      .gk-card.rule.err { border-color:#6e2b2b; }
      .gk-card.rule.pass { border-color:#2b573f; }
      .gk-card.silent { border-color:#6e2b2b; background:#1a1416; }
      .rule-cn { font-size:33px; color:#c9d1d9; line-height:1.55; }
      .rule-foot { margin-top:14px; font-size:30px; color:#8b949e; line-height:1.5; }
      .rule-foot.hot { color:#ffa198; }

      /* 步骤/修法行 */
      .steprow, .fixrow { display:flex; align-items:center; font-size:33px; color:#e6edf3;
        line-height:1.6; margin:9px 0; }
      .step-n, .fix-n { display:inline-flex; align-items:center; justify-content:center;
        width:46px; height:46px; border-radius:50%; background:#1f6feb; color:#fff;
        font-size:27px; margin-right:16px; flex:none; }

      /* 代码块 */
      .codeblock { background:#0d1521; border:2px solid #30363d; border-radius:12px;
        padding:18px 22px; }
      .cb-line { font-family:'Consolas','Courier New',monospace; font-size:29px;
        color:#c9d1d9; line-height:1.7; white-space:nowrap; }
      .cb-line.dim { color:#8b949e; }
      .cb-line.bad { color:#ffa198; }
      .cb-hex { color:#58a6ff; }
      .cb-bad { color:#ffa198; }
      .cb-good { color:#7ee787; }

      /* S1 开场 */
      .op-ep { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:48px; color:#8b949e; letter-spacing:.3em; }
      .op-title { position:absolute; left:0; right:0; top:382px; text-align:center;
        font-size:128px; color:#e3b341; letter-spacing:.1em; }
      .op-sub { position:absolute; left:0; right:0; top:556px; text-align:center;
        font-size:46px; color:#58a6ff; letter-spacing:.14em; }
      .stage { position:absolute; left:140px; right:140px; top:240px; text-align:center; }
      .st-h { font-size:54px; color:#c9d1d9; line-height:1.6; }
      .st-q-big { font-size:80px; color:#e6edf3; margin-top:30px; }
      .st-q-big strong { color:#e3b341; }
      .st-chips { margin-top:44px; }
      .st-chip { display:inline-block; margin:10px 14px; padding:20px 38px; font-size:42px;
        color:#c9d1d9; background:#161b22; border:2px solid #2b3c57; border-radius:999px; }
      .st-chip.hot { border-color:#e3b341; color:#e3b341; }
      .have-grid { margin:0 auto; width:1100px; }
      .have-item { display:inline-block; width:480px; margin:14px; padding:34px 0;
        font-size:56px; background:#161b22; border:2px solid #2b573f;
        border-radius:18px; color:#7ee787; }
      .have-item.no { border-color:#6e2b2b; color:#ffa198; width:1000px; font-size:60px; }
      .have-ok { color:#7ee787; margin-right:18px; }
      .have-no { color:#f85149; margin-right:18px; }
      .s1-note { margin-top:40px; font-size:40px; color:#8b949e; }
      .mutedrows { margin-bottom:30px; }
      .vtag { font-family:'Consolas','Courier New',monospace; font-size:54px;
        color:#8b949e; line-height:1.9; }
      .mt-stamp { display:inline-block; margin:0 10px; padding:4px 22px; border-radius:10px;
        background:#30363d; color:#e6edf3; border:2px solid #8b949e; }
      .mute-word { color:#8b949e; letter-spacing:.12em; }

      /* S2 三兄弟/契约 */
      .tagrow { display:flex; align-items:center; margin:14px 0; font-size:38px; }
      .tag-chip { display:inline-flex; align-items:center; justify-content:center;
        min-width:180px; padding:10px 22px; margin-right:24px; border-radius:12px;
        font-family:'Consolas','Courier New',monospace; font-size:38px; font-weight:700; }
      .tag-chip.img { background:rgba(63,185,80,.15); color:#7ee787; border:2px solid #2b573f; }
      .tag-chip.vid { background:rgba(88,166,255,.15); color:#58a6ff; border:2px solid #1f4e8c; }
      .tag-chip.aud { background:rgba(227,179,65,.15); color:#e3b341; border:2px solid #5e4a1e; }
      .tag-chip.url { font-size:28px; min-width:180px; background:#0d1521; color:#c9d1d9;
        border:2px solid #30363d; }
      .tag-d { color:#e6edf3; font-size:36px; }
      .contract-line { font-size:42px; margin:14px 0; }
      .contract-note { margin-top:18px; font-size:30px; color:#8b949e; line-height:1.5; }
      .idwarn-h { font-size:36px; color:#c9d1d9; margin:10px 0; }
      .idwarn-big { font-size:80px; color:#ffa198; text-align:center; margin-top:14px; }

      /* S3 FROZEN/SILENT/diff */
      .frozen-big { font-size:96px; font-weight:800; text-align:center; margin:10px 0;
        color:#79c0ff; letter-spacing:.08em;
        text-shadow:0 0 28px rgba(121,192,255,.55); }
      .frozen-big.silent { color:#ffa198; text-shadow:0 0 28px rgba(248,81,73,.45); }
      .diffrow { display:flex; align-items:center; margin:16px 0; font-size:32px; }
      .diff-t { margin-left:20px; color:#c9d1d9; line-height:1.4; }

      /* S4 岔路 */
      .g4-qline { font-size:46px; color:#e6edf3; line-height:1.6; margin:18px 0; }
      .forkrow { display:flex; align-items:flex-start; background:#0d1521;
        border:2px solid #21262d; border-radius:14px; padding:20px 24px; margin:16px 0;
        font-size:34px; color:#e6edf3; line-height:1.6; }
      .fork-n { display:inline-flex; align-items:center; justify-content:center;
        width:46px; height:46px; border-radius:50%; background:#1f6feb; color:#fff;
        font-size:27px; margin-right:18px; flex:none; }
      .fork-code { display:inline-block; margin-top:8px; font-size:32px; }
      .g4-twoline { margin-top:16px; }
      .g4-case { font-size:31px; color:#c9d1d9; line-height:1.8; }

      /* S6 三连谱 */
      .specrow { display:flex; align-items:center; font-size:33px; color:#e6edf3;
        margin:14px 0; }
      .specrow.dim { opacity:.55; }
      .specrow span:last-child { margin-left:20px; }
      .g6-ci-h { font-size:38px; color:#e6edf3; line-height:1.55; margin-bottom:22px; }
      .ci-mini { display:flex; align-items:center; justify-content:space-around;
        background:#0d1521; border:2px solid #5e4a1e; border-radius:14px; padding:24px;
        font-size:34px; color:#c9d1d9; }
      .ci-mini .mono { font-size:40px; color:#e3b341; }

      /* S7 人声标签（全屏） */
      .audiocard { position:absolute; left:160px; right:160px; top:240px;
        background:#161b22; border:2px solid #2b3c57; border-radius:22px;
        padding:52px 60px; text-align:center;
        box-shadow:inset 0 1px 0 rgba(121,192,255,.14),0 18px 60px rgba(0,0,0,.45); }
      .ac-note { font-size:42px; color:#8b949e; margin-bottom:40px; }
      .ac-tag { font-family:'Consolas','Courier New',monospace; font-size:44px;
        color:#c9d1d9; line-height:1.7; background:#0d1521; border:2px solid #30363d;
        border-radius:14px; padding:30px 24px; }
      .ac-hl { color:#e3b341; }
      .ac-dim { color:#8b949e; }
      .ac-props { margin:40px 0 10px; }
      .acp { display:inline-block; margin:8px 18px; padding:16px 30px; font-size:36px;
        color:#58a6ff; background:#0d1521; border:2px solid #1f4e8c; border-radius:999px; }

      /* S8 轨道迷你示意 */
      .minitracks { margin:10px 0; }
      .mt-row { position:relative; height:86px; border-bottom:2px solid #30363d; }
      .mt-row.dim { opacity:.5; }
      .mt-rail { position:absolute; left:0; top:26px; width:96px; font-size:28px; color:#c9d1d9; }
      .mt-bar { position:absolute; top:18px; height:48px; border-radius:9px;
        font-size:28px; color:#fff; text-align:center; line-height:48px; padding:0 18px; }
      .mt-bar.voice { left:110px; background:rgba(31,111,235,.55); border:2px solid #58a6ff; }
      .mt-bar.music { left:330px; background:rgba(227,179,65,.5); border:2px dashed #e3b341; }
      .mt-bar.music.bad { border-style:solid; border-color:#f85149; box-shadow:0 0 18px rgba(248,81,73,.4); }
      .mt-bar.music.ok { border-style:solid; border-color:#3fb950; }
      .mt-empty { position:absolute; left:120px; top:28px; font-size:28px; color:#5a6472; }

      /* S9 拍点 */
      .beatdots { display:flex; flex-wrap:wrap; gap:9px; margin:18px 8px; }
      .beatdots i { width:22px; height:22px; border-radius:50%; background:#30363d;
        display:inline-block; }
      .beatdots i.on { background:#e3b341; box-shadow:0 0 10px rgba(227,179,65,.7); }

      /* S10 音量三件 */
      .vthree { position:absolute; left:110px; right:110px; top:200px; text-align:center; }
      .vt-card { display:inline-block; width:500px; vertical-align:top; min-height:430px;
        margin:0 20px; padding:42px 38px; background:#161b22; border:2px solid #2b3c57;
        border-radius:20px; text-align:left; }
      .vt-name { font-size:44px; color:#58a6ff; margin-bottom:30px; }
      .vt-scale { display:flex; justify-content:space-between; margin:20px 0; }
      .vts { font-size:40px; color:#8b949e; }
      .vts.hot { color:#e3b341; }
      .vt-note { font-size:33px; color:#c9d1d9; line-height:1.6; margin-top:16px; }
      .vt-note.dim { color:#8b949e; font-size:30px; }
      .fade-demo { margin:24px 0; font-size:34px; line-height:1.9; }
      .fd-up { color:#7ee787; display:block; }
      .fd-down { color:#e3b341; display:block; }

      /* S11 双表 */
      .ear-line { font-size:40px; color:#e6edf3; line-height:1.7; }
      .ear-line.dim { font-size:33px; color:#8b949e; }
      .meters { margin:18px 0; }
      .meter { display:flex; align-items:baseline; background:#0d1521;
        border:2px solid #21262d; border-radius:12px; padding:16px 22px; margin:12px 0; }
      .meter.voice { border-color:#1f4e8c; }
      .meter.music { border-color:#5e4a1e; }
      .m-who { font-size:32px; color:#c9d1d9; margin-right:auto; }
      .m-val { font-family:'Consolas','Courier New',monospace; font-size:72px; font-weight:700; }
      .meter.voice .m-val { color:#7ee787; }
      .meter.music .m-val { color:#e3b341; }
      .m-u { font-size:28px; color:#8b949e; margin-left:14px; }

      /* S12 JSON */
      .json-lines { font-family:'Consolas','Courier New',monospace; font-size:34px;
        color:#c9d1d9; line-height:1.8; }
      .json-lines b { color:#7ee787; }
      .json-lines.bad b { color:#ffa198; }
      .json-lines.bad .gold-t { color:#e3b341; }
      .idem-big { font-family:'Consolas','Courier New',monospace; font-size:44px;
        color:#7ee787; text-align:center; margin:22px 0; }

      /* S13 噪声底 */
      .noise-demo { margin:14px 0; }
      .nd-row { display:flex; align-items:center; margin:10px 0; }
      .nd-l { width:150px; font-size:28px; color:#c9d1d9; }
      .nd-bar { height:26px; border-radius:6px; margin-right:10px; }
      .nd-bar.sig { width:280px; background:#58a6ff; }
      .nd-bar.floor { width:70px; background:#6e7681; }
      .nd-bar.sig2 { width:340px; background:#58a6ff; opacity:.85; }
      .nd-bar.floor2 { width:220px; background:#f85149; box-shadow:0 0 14px rgba(248,81,73,.5); }

      /* S14 金句 */
      .splitrow { display:flex; justify-content:space-between; align-items:center;
        background:#0d1521; border:2px solid #21262d; border-radius:12px;
        padding:18px 22px; margin:12px 0; font-size:31px; color:#e6edf3; }
      .law-big { font-size:62px; color:#ffa198; text-align:center; margin:6px 0;
        letter-spacing:.03em; line-height:1.35; }
      .law-neq { color:#e3b341; margin-bottom:16px; }
      .law-sub { font-size:31px; color:#c9d1d9; text-align:center; line-height:1.55; }
      .law-three { text-align:center; margin-top:24px; }
      .l3 { display:inline-block; margin:8px 12px; padding:14px 26px; font-size:32px;
        color:#c9d1d9; background:#0d1521; border:2px solid #30363d; border-radius:999px; }
      .l3.hot { border-color:#6e2b2b; color:#ffa198; }

      /* S16 三件事 */
      .recap3 { position:absolute; left:90px; right:90px; top:190px; text-align:center; }
      .rp-card { display:inline-block; width:520px; vertical-align:top; min-height:500px;
        margin:0 18px; padding:44px 38px; background:#161b22; border:2px solid #2b3c57;
        border-radius:22px; text-align:left; }
      .rp-n { font-size:54px; color:#e3b341; }
      .rp-h { font-size:46px; color:#e6edf3; margin:14px 0 26px; }
      .rp-l { font-size:34px; color:#c9d1d9; line-height:1.7; }
      .rp-l.hot { color:#ffa198; }

      /* S17 */
      .acl { width:1300px; margin:0 auto; }
      .acl-row { padding:26px 38px; margin-bottom:22px; background:#161b22;
        border:2px solid #2b3c57; border-left:10px solid #1f6feb; border-radius:14px;
        font-size:42px; color:#e6edf3; line-height:1.5; text-align:left; }
      .acl-n { color:#e3b341; font-size:50px; margin-right:20px; }
      #s17-action { top:200px; }
      #s17-next { top:230px; }
      .nx-h { font-size:44px; color:#8b949e; letter-spacing:.3em; }
      .nx-card { font-size:78px; color:#e3b341; margin:22px 0 36px; }
      .nx-lines { font-size:38px; color:#c9d1d9; line-height:1.9; }
      .bye { position:absolute; left:0; right:0; top:440px; text-align:center;
        font-size:72px; color:#e6edf3; letter-spacing:.08em; }
"""

# ---------- 场景时间轴（时间显式给秒；拍点锚 cues 实测词戳） ----------
SCENE_JS = """
      /* 拍点通用：右卡同位置轮替（x:60 滑入），全屏卡 scale/淡入。
         gsap className 替换非追加，所有高亮一律属性补间（hf-05 教训）。 */

      /* S9 拍点：beats 真机输出 23 拍，这里补 23 个圆点，入场后逐拍点亮 */
      (function(){
        const bd = document.getElementById('beat-dots');
        for (let i = 0; i < 23; i++) bd.appendChild(document.createElement('i'));
      })();

      /* S1 0–25.30：片名 → 默片 → 四件家当 → muted 章 → 今日主题 */
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#op-ep',{y:18,opacity:0,duration:.6},.2);
      tl.from('#op-title',{scale:.8,opacity:0,duration:.8,ease:'back.out(1.5)'},.5);
      tl.from('#op-sub',{opacity:0,duration:.6},1.0);
      tl.to(['#op-ep','#op-title','#op-sub'],{opacity:0,duration:.35},2.6);
      tl.from('#s1-silent',{y:22,opacity:0,duration:.7},3.0);
      tl.to('#s1-silent',{opacity:0,duration:.3},6.4);
      tl.from('#s1-have',{y:22,opacity:0,duration:.7},6.8);
      tl.from('#hv-1',{y:18,opacity:0,duration:.45},7.4);
      tl.from('#hv-2',{y:18,opacity:0,duration:.45},8.0);
      tl.from('#hv-3',{y:18,opacity:0,duration:.45},8.6);
      tl.from('#hv-4',{y:24,opacity:0,duration:.6,ease:'back.out(1.3)'},9.6);
      tl.from('#s1-have .s1-note',{opacity:0,duration:.6},13.2);
      tl.to('#s1-have',{opacity:0,duration:.3},14.8);
      tl.from('#s1-mutedrow',{y:22,opacity:0,duration:.7},15.1);
      tl.from('.vtag',{x:-30,opacity:0,duration:.5,stagger:.5},15.6);
      tl.fromTo('.mt-stamp',{backgroundColor:'rgba(48,54,61,0)'},
                {backgroundColor:'rgba(210,153,34,.25)',borderColor:'#d29922',
                 color:'#e3b341',duration:.5,stagger:.5},16.9);
      tl.from('#mr-word',{scale:.85,opacity:0,duration:.6,ease:'back.out(1.4)'},19.6);
      tl.to('#s1-mutedrow',{opacity:0,duration:.3},21.0);
      tl.from('#s1-today',{y:22,opacity:0,duration:.7},21.4);
      tl.from('#s1-today .st-chip',{y:16,opacity:0,duration:.5,stagger:.18},22.4);
      tl.to('#sc-open > .scene-inner',{opacity:0,duration:.4},24.90);

      /* S2 25.30–48.74：三兄弟 27.04 → 老契约 30.60（终端 30.8 进）→ 必须有 id 47.62 */
      tl.fromTo('#sc-three > .scene-inner',{opacity:0},{opacity:1,duration:.5},25.30);
      tl.from('#g2-k',{y:18,opacity:0,duration:.6},25.6);
      tl.from('#c1-tags',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},26.0);
      tl.from('#c1-tags .tagrow',{x:24,opacity:0,duration:.45,stagger:.5},27.2);
      tl.to('#c1-tags',{opacity:0,duration:.3},30.2);
      tl.from('#c1-contract',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},30.5);
      tl.from('#c1-contract .contract-line',{x:24,opacity:0,duration:.45,stagger:.7},33.2);
      tl.to('#c1-contract',{opacity:0,duration:.3},45.4);
      tl.from('#c1-idwarn',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},45.8);
      tl.from('#c1-idwarn .idwarn-big',{scale:.7,opacity:0,duration:.6,ease:'back.out(1.5)'},47.0);
      tl.to('#sc-three > .scene-inner',{opacity:0,duration:.4},48.34);

      /* S3 48.74–88.06：步骤 49.8 → FROZEN 70.90 → SILENT 75.70 → 差别 76.24 */
      tl.fromTo('#sc-id > .scene-inner',{opacity:0},{opacity:1,duration:.5},48.74);
      tl.from('#g3-k',{y:18,opacity:0,duration:.6},49.0);
      tl.from('#g3-steps',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},49.4);
      tl.to('#g3-steps',{opacity:0,duration:.3},65.6);
      tl.from('#g3-frozen',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},66.0);
      tl.from('#g3-frozen .frozen-big',{scale:.6,opacity:0,duration:.7,
                ease:'back.out(1.6)'},70.6);
      tl.to('#g3-frozen',{opacity:0,duration:.3},71.1);
      /* 口播 71.30「音频版同款」、74.26 SILENT、76.24「记住这个差别」 */
      tl.from('#g3-silent',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},71.4);
      tl.from('#g3-silent .frozen-big',{scale:.6,opacity:0,duration:.7,
                ease:'back.out(1.6)'},74.3);
      tl.to('#g3-silent',{opacity:0,duration:.3},75.8);
      tl.from('#g3-diff',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},76.1);
      tl.from('#g3-diff .diffrow',{x:20,opacity:0,duration:.4,stagger:.5},76.5);
      tl.from('#g3-diff .goldword-sm',{scale:.9,opacity:0,duration:.6},86.4);
      tl.to('#sc-id > .scene-inner',{opacity:0,duration:.4},87.66);

      /* S4 88.06–113.40：问题 88 → 两表态 94/98.7 → 不表态 error 101.88 */
      tl.fromTo('#sc-muted > .scene-inner',{opacity:0},{opacity:1,duration:.5},88.06);
      tl.from('#g4-k',{y:18,opacity:0,duration:.6},88.3);
      tl.from('#g4-q',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},88.6);
      tl.to('#g4-q',{opacity:0,duration:.3},93.4);
      tl.from('#g4-fork',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},93.7);
      tl.from('#fk-mute',{x:24,opacity:0,duration:.5},94.2);
      tl.from('#fk-audio',{x:24,opacity:0,duration:.5},98.9);
      tl.to('#g4-fork',{opacity:0,duration:.3},101.3);
      tl.from('#g4-error',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},101.6);
      tl.from('#g4-error .g4-case',{x:20,opacity:0,duration:.5,stagger:.8},106.4);
      tl.to('#sc-muted > .scene-inner',{opacity:0,duration:.4},113.00);

      /* S5 113.40–133.48：扣子 115.96 → 改字母 119.8 → 报错 122.82/静音 132.12 */
      tl.fromTo('#sc-missingfile > .scene-inner',{opacity:0},{opacity:1,duration:.5},113.40);
      tl.from('#g5-k',{y:18,opacity:0,duration:.6},113.7);
      tl.from('#g5-step',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},117.6);
      /* 口播 122.82 报错名、123.32「不存在的文件」、132.12「将会是静音的」 */
      tl.to('#g5-step',{opacity:0,duration:.3},122.4);
      tl.from('#g5-err',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},122.7);
      tl.from('#g5-err .rule-foot',{opacity:0,duration:.6},131.8);
      tl.to('#sc-missingfile > .scene-inner',{opacity:0,duration:.4},133.08);

      /* S6 133.48–156.46：skip 136.34 → 三连谱 → 退出码/CI 152.82 */
      tl.fromTo('#sc-skip > .scene-inner',{opacity:0},{opacity:1,duration:.5},133.48);
      tl.from('#g6-k',{y:18,opacity:0,duration:.6},133.8);
      tl.from('#g6-skip',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},134.2);
      tl.to('#g6-skip',{opacity:0,duration:.3},144.8);
      tl.from('#g6-spec',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},145.1);
      tl.from('#g6-spec .specrow',{x:20,opacity:0,duration:.45,stagger:.5},145.7);
      tl.to('#g6-spec',{opacity:0,duration:.3},152.0);
      tl.from('#g6-ci',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},152.3);
      tl.to('#sc-skip > .scene-inner',{opacity:0,duration:.4},156.06);

      /* S7 156.46–171.42：提问 157.86 → audio 标签 161.68 → 三属性 → 金句 169.94 */
      tl.fromTo('#sc-avoice > .scene-inner',{opacity:0},{opacity:1,duration:.5},156.46);
      tl.from('#g7-k',{y:18,opacity:0,duration:.6},156.8);
      tl.from('#c7-card',{y:30,opacity:0,duration:.8,ease:'back.out(1.2)'},158.6);
      tl.from('#c7-tag',{scale:.92,opacity:0,duration:.7},161.8);
      tl.from('#acp-1',{y:18,opacity:0,duration:.5},165.6);
      tl.from('#acp-2',{y:18,opacity:0,duration:.5},167.2);
      tl.from('#acp-3',{y:18,opacity:0,duration:.5},168.8);
      tl.from('#c7-word',{scale:.9,opacity:0,duration:.7,ease:'back.out(1.4)'},170.0);
      tl.to('#sc-avoice > .scene-inner',{opacity:0,duration:.4},171.02);

      /* S8 171.42–189.02：挤轨 174 → 警告 180.68 → 正解第三轨 187.50 */
      tl.fromTo('#sc-layer > .scene-inner',{opacity:0},{opacity:1,duration:.5},171.42);
      tl.from('#g8-k',{y:18,opacity:0,duration:.6},171.7);
      tl.from('#g8-bad',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},172.0);
      tl.to('#g8-bad',{opacity:0,duration:.3},180.0);
      tl.from('#g8-warn',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},180.3);
      tl.to('#g8-warn',{opacity:0,duration:.3},186.6);
      tl.from('#g8-good',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},186.9);
      tl.to('#sc-layer > .scene-inner',{opacity:0,duration:.4},188.62);

      /* S9 189.02–211.82：role 191.64 → 眼熟/甩脸子 → beats 203.22/23 拍 → 地图 210.60 */
      tl.fromTo('#sc-beats > .scene-inner',{opacity:0},{opacity:1,duration:.5},189.02);
      tl.from('#g9-k',{y:18,opacity:0,duration:.6},189.3);
      tl.from('#g9-role',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},189.6);
      tl.to('#g9-role',{opacity:0,duration:.3},202.4);
      tl.from('#g9-beats',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},202.7);
      /* .beatdots i 初始色在 CSS 里已是 #30363d，这里只补间点亮（逐拍 0.18s） */
      tl.to('.beatdots i',{backgroundColor:'#e3b341',boxShadow:'0 0 10px rgba(227,179,65,.7)',
                duration:.25,stagger:{each:.18}},204.8);
      tl.to('#sc-beats > .scene-inner',{opacity:0,duration:.4},211.42);

      /* S10 211.82–239.46：volume 214.36/3.98 216.90 → fade 221.34 → media-start 231.40 */
      tl.fromTo('#sc-volume > .scene-inner',{opacity:0},{opacity:1,duration:.5},211.82);
      tl.from('#g10-k',{y:18,opacity:0,duration:.6},212.1);
      tl.from('.vthree .vt-card',{y:34,opacity:0,duration:.7,stagger:.8,
                ease:'back.out(1.15)'},213.4);
      tl.from('#vtc-1 .vts',{opacity:0,duration:.4,stagger:.6},215.0);
      tl.from('#vtc-2 .fd-up',{x:-20,opacity:0,duration:.5},223.8);
      tl.from('#vtc-2 .fd-down',{x:20,opacity:0,duration:.5},225.6);
      tl.to('#sc-volume > .scene-inner',{opacity:0,duration:.4},239.06);

      /* S11 239.46–273.24：拖滑块 244.98 → 客观尺 252.45/LUFS 257.84 → 实测 269.66 */
      tl.fromTo('#sc-lufs > .scene-inner',{opacity:0},{opacity:1,duration:.5},239.46);
      tl.from('#g11-k',{y:18,opacity:0,duration:.6},239.8);
      /* 口播 244.98「凭耳朵拖滑块？拖三遍三个数」 */
      tl.from('#c11-ear',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},244.6);
      tl.to('#c11-ear',{opacity:0,duration:.3},251.8);
      tl.from('#c11-ruler',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},252.1);
      tl.from('#norm-cmd',{scale:.9,opacity:0,duration:.6,ease:'back.out(1.4)'},253.2);
      tl.to('#c11-ruler',{opacity:0,duration:.3},268.8);
      tl.from('#c11-meters',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},269.1);
      tl.from('.meter',{x:26,opacity:0,duration:.5,stagger:.8},269.6);
      tl.to('#sc-lufs > .scene-inner',{opacity:0,duration:.4},272.84);

      /* S12 273.24–287.26：空跑 273.24 → write 277.60/2.371374 → 幂等 282.94 */
      tl.fromTo('#sc-write > .scene-inner',{opacity:0},{opacity:1,duration:.5},273.24);
      tl.from('#g12-k',{y:18,opacity:0,duration:.6},273.5);
      tl.from('#g12-dry',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},273.8);
      tl.to('#g12-dry',{opacity:0,duration:.3},277.0);
      tl.from('#g12-write',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},277.3);
      tl.to('#g12-write',{opacity:0,duration:.3},282.2);
      tl.from('#g12-idem',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},282.5);
      tl.from('#g12-idem .idem-big',{scale:.85,opacity:0,duration:.6,ease:'back.out(1.5)'},283.2);
      tl.to('#sc-write > .scene-inner',{opacity:0,duration:.4},286.86);

      /* S13 287.26–328.90：拒绝 295.64/16.0 293.88 → 噪声底 305.10 → 两正路 316.94 */
      tl.fromTo('#sc-ceiling > .scene-inner',{opacity:0},{opacity:1,duration:.5},287.26);
      tl.from('#g13-k',{y:18,opacity:0,duration:.6},287.6);
      tl.from('#g13-refuse',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},289.6);
      /* needs 16.0 在 293.88、ok false 在 295.64，JSON 块整体取中 */
      tl.from('#g13-refuse .json-lines',{opacity:0,duration:.5},294.2);
      tl.to('#g13-refuse',{opacity:0,duration:.3},303.8);
      tl.from('#g13-why',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},304.1);
      tl.from('.nd-row',{x:24,opacity:0,duration:.45,stagger:.5},306.4);
      tl.to('#g13-why',{opacity:0,duration:.3},316.2);
      tl.from('#g13-paths',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},316.5);
      tl.from('#g13-paths .fixrow',{x:20,opacity:0,duration:.5,stagger:1.6},318.6);
      tl.to('#sc-ceiling > .scene-inner',{opacity:0,duration:.4},328.50);

      /* S14 328.90–401.26：拆两情况 335.72 → #bgn 351.2/不干活 358.72 →
         #dem 373.66 → 金句 379.84/三看 394.30 */
      tl.fromTo('#sc-badid > .scene-inner',{opacity:0},{opacity:1,duration:.5},328.90);
      tl.from('#g14-k',{y:18,opacity:0,duration:.6},329.2);
      tl.from('#g14-split',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},332.0);
      tl.to('#g14-split',{opacity:0,duration:.3},347.8);
      tl.from('#g14-bgn',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},348.1);
      tl.to('#g14-bgn',{opacity:0,duration:.3},370.4);
      tl.from('#g14-trt',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},371.8);
      /* 口播 379.84「命令跑完，不等于活干完」 */
      tl.to('#g14-trt',{opacity:0,duration:.3},379.0);
      tl.from('#g14-law',{x:60,opacity:0,duration:.7,ease:'back.out(1.2)'},379.3);
      tl.from('#g14-law .law-big',{scale:.85,opacity:0,duration:.6,stagger:.18,
                ease:'back.out(1.5)'},379.9);
      tl.from('#g14-law .l3',{y:18,opacity:0,duration:.5,stagger:.8},394.4);
      tl.to('#sc-badid > .scene-inner',{opacity:0,duration:.4},400.86);

      /* S15 401.26–437.86：自动代理 406.70/example 408.58 → analyze 424.24 */
      tl.fromTo('#sc-remote > .scene-inner',{opacity:0},{opacity:1,duration:.5},401.26);
      tl.from('#g15-k',{y:18,opacity:0,duration:.6},401.6);
      /* 口播 406.70 自动代理、408.58 example.com、424.24 media-treatment analyze */
      tl.from('#g15-proxy',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},405.8);
      tl.to('#g15-proxy',{opacity:0,duration:.3},423.2);
      tl.from('#g15-treat',{x:60,opacity:0,duration:.6,ease:'back.out(1.2)'},423.6);
      tl.to('#sc-remote > .scene-inner',{opacity:0,duration:.4},437.46);

      /* S16 437.86–457.44：三件事 440.90 起逐张 */
      tl.fromTo('#sc-recap > .scene-inner',{opacity:0},{opacity:1,duration:.5},437.86);
      tl.from('#g16-k',{y:18,opacity:0,duration:.6},438.1);
      tl.from('.recap3 .rp-card',{y:36,opacity:0,duration:.7,stagger:2.0,
                ease:'back.out(1.2)'},441.0);
      tl.to('#sc-recap > .scene-inner',{opacity:0,duration:.4},457.04);

      /* S17 457.44–TOTAL：行动件 459.22 → 预告 472.80 → 道别 489.40 */
      tl.fromTo('#sc-action > .scene-inner',{opacity:0},{opacity:1,duration:.5},457.44);
      tl.from('#s17-action .kicker-static',{y:18,opacity:0,duration:.6},458.0);
      /* 口播 460.72 加音轨、464.54 跑 check、467.02 normalize-audio */
      tl.from('#s17-action .acl-row',{x:-40,opacity:0,duration:.6,stagger:{each:1.0}},460.5);
      tl.to('#s17-action',{opacity:0,duration:.4},471.8);
      tl.from('#s17-next',{y:24,opacity:0,duration:.7},472.2);
      tl.from('#nx-l1',{opacity:0,duration:.6},475.6);
      tl.from('#nx-l2',{opacity:0,duration:.6},480.6);
      tl.to('#s17-next',{opacity:0,duration:.35},488.4);
      tl.from('#bye',{y:24,opacity:0,duration:.7},489.2);
"""

# ---------- 底部字幕轨道 ----------
# time_offset：faster-whisper 吞句间停顿致字幕整体偏早；hf-01 0.28、
# hf-02 0.37、hf-03 0.29、hf-04 0.30、hf-05 0.29。hf-06 v3 母带经
# oneoffs/measure_offset.py 实测 onset 配对中位数 +310.1ms（43/55），取 0.31。
frag = char_track(cues, chars, THEME.accent, time_offset=0.31)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/hf-06-yeyang.wav", total),
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
mode = "仅概念卡（--cards-only）" if CARDS_ONLY else "正式版（含录屏 clip）"
print("已生成 index_html（%.2f 秒，%d 幕，%d 句，%s）"
      % (total, len(SCENES), len(cues), mode))
