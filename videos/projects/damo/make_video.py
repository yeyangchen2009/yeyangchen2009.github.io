# -*- coding: utf-8 -*-
"""达摩成片生成器（宣纸主题 XUANZHI，388.18s，21 幕）。

承接梁武帝视觉。本片独有：21 幕 body 与场景时间轴。混用 PPT 式卡片——
四问统一问答卡（S5/S7/S8/S9）、人天小果判语（S6）、追影子（S10）、
攥水漏因（S11）、八字真功德（S12）、圣凡（S13/14）、史料考据（S15）、
一苇渡江（S16）、面壁勿扰（S17）、生前死后反差（S18）、谁赢了（S19）、
真传抛问（S20）、慧可慧能预告（S21）。页面骨架／主题／字幕／clip 外壳
全部复用 videopipe。
"""
import io
import sys
from pathlib import Path

# projects/<name>/make_video.py -> videos/ 在 parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       XUANZHI)
from videopipe.config import WHISPER_WORD_LEAD

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars, total = data["cues"], data["chars"], data["duration"]
THEME = XUANZHI
RED, GOLD, INK, MUTE = "#b03120", "#8a6418", "#2b2620", "#5f574c"

# ---------- 21 幕（边界严格首尾相接，交叉淡变） ----------
SCENES = [

# S1 遗问 0.00–15.02（cue1–9）
Scene("sc-recap", 0.00, 15.02, """
          <div class="rp-lead" id="rp-lead">上一集，我们讲到 ——</div>
          <div class="rp-name" id="rp-name">梁武帝</div>
          <div class="rp-q" id="rp-q">他到死，心里都憋着一个问题</div>
          <div class="rp-hint" id="rp-hint">有个印度和尚，其实当面回答过他</div>"""),

# S2 达摩登场 15.02–21.70（cue10–13）
Scene("sc-damo", 15.02, 21.70, """
          <div class="dn-note" id="dn-note">这场对话，后来成了中国佛教史上最有名的一次</div>
          <div class="dn-name" id="dn-name">菩提达摩</div>
          <div class="dn-sub" id="dn-sub">印度来的和尚 · 禅宗初祖</div>"""),

# S3 报名 21.70–25.38（cue14–16）
Scene("sc-hi", 21.70, 25.38, """
          <div class="hi-main" id="hi-main">哈喽大家好，我是叶扬</div>
          <div class="hi-sub" id="hi-sub">先说，那天是怎么回事</div>"""),

# S4 成绩单 25.38–38.62（cue17–24）
Scene("sc-score", 25.38, 38.62, """
          <div class="sc-lead" id="sc-lead">俩人一见面，皇帝先亮出了成绩单</div>
          <div class="sc-card" id="sc-card">
            <div class="sc-row" id="scr1"><span class="sc-k">壹</span><span class="sc-t">盖寺庙</span></div>
            <div class="sc-row" id="scr2"><span class="sc-k">贰</span><span class="sc-t">抄佛经</span></div>
            <div class="sc-row" id="scr3"><span class="sc-k">叁</span><span class="sc-t">劝人出家</span></div>
          </div>
          <div class="sc-ask" id="sc-ask">这些功德，大不大？</div>"""),

# S5 一问·并无功德 38.62–46.62（cue25–30）
Scene("sc-q1", 38.62, 46.62, """
          <div class="qa-q" id="q1q">朕干了这么多 —— 功德，大不大？</div>
          <div class="qa-big" id="q1b">并无功德</div>
          <div class="qa-tail" id="q1t">他本来，是等着听一句夸奖</div>"""),

# S6 人天小果·有漏之因 46.62–53.48（cue30–35）
Scene("sc-verdict", 46.62, 53.48, """
          <div class="vd-q" id="vd-q">怎么会没有呢？</div>
          <div class="vd-card" id="vd-card">
            <div class="vd-l" id="vdl1">人天小果</div>
            <div class="vd-l" id="vdl2">有漏之因</div>
          </div>"""),

# S7 二问·净智妙圆 53.48–59.38（cue35–40）
Scene("sc-q2", 53.48, 59.38, """
          <div class="qa-q" id="q2q">那到底什么，才算真功德？</div>
          <div class="qa-words" id="q2b"><span id="q2w1">净智妙圆</span><span class="qa-dot">·</span><span id="q2w2">体自空寂</span></div>"""),

# S8 三问·廓然无圣 59.38–74.34（cue41–49）
Scene("sc-q3", 59.38, 74.34, """
          <div class="qa-q" id="q3q">佛法里最究竟的第一义谛，是什么？</div>
          <div class="qa-big" id="q3b">廓然无圣</div>
          <div class="qa-tail" id="q3t">空空荡荡的，压根就没有什么圣人</div>"""),

# S9 四问·不认识 74.34–82.80（cue50–57）
Scene("sc-q4", 74.34, 82.80, """
          <div class="qa-q" id="q4q">那站在我对面的，到底是谁啊？</div>
          <div class="qa-big" id="q4b">不认识</div>
          <div class="qa-tail" id="q4t">天，就这么聊死了</div>"""),

# S10 追影子（含路标）82.80–105.02（cue58–71）
Scene("sc-shadow", 82.80, 105.02, """
          <div class="sh-note" id="sh-note">你可能听到这儿也有点懵 —— 我用件简单事说</div>
          <svg id="sh-svg" viewBox="0 0 1000 520">
            <circle cx="870" cy="96" r="52" id="sh-sun"/>
            <line x1="60" y1="430" x2="940" y2="430" id="sh-ground"/>
            <g id="sh-shadow"><ellipse cx="250" cy="428" rx="120" ry="16"/>
              <path d="M150 430 q100 -70 210 0"/></g>
            <g transform="translate(560,310)"><g id="sh-kid">
              <circle cx="0" cy="-150" r="34" id="sh-head"/>
              <path d="M-44 -30 Q0 -120 44 -30 L44 40 L-44 40 Z"/>
              <line x1="38" y1="-70" x2="96" y2="-110" id="sh-arm"/>
              <line x1="-18" y1="40" x2="-26" y2="120" class="sh-leg"/>
              <line x1="18" y1="40" x2="26" y2="120" class="sh-leg"/>
            </g></g>
          </svg>
          <div class="sh-drop" id="sh-drop">梁武帝追了一辈子的功德 —— 追的是个影子</div>"""),

# S11 有漏·攥水 105.02–134.20（cue72–88）
Scene("sc-leak", 105.02, 134.20, """
          <div class="lk-note" id="lk-note">达摩不是说那些好事白做了 —— 是你在追一个抓不住的东西</div>
          <svg id="lk-svg" viewBox="0 0 1000 480">
            <g id="lk-hand">
              <path d="M250 150 Q300 96 380 120 Q470 96 520 150 L520 270 Q385 320 250 270 Z" id="lk-palm"/>
              <line x1="320" y1="150" x2="320" y2="250" class="lk-finger"/>
              <line x1="385" y1="140" x2="385" y2="252" class="lk-finger"/>
              <line x1="450" y1="150" x2="450" y2="250" class="lk-finger"/>
            </g>
            <g id="lk-drops">
              <ellipse cx="330" cy="330" rx="9" ry="15" class="lk-drop"/>
              <ellipse cx="385" cy="372" rx="9" ry="15" class="lk-drop"/>
              <ellipse cx="440" cy="330" rx="9" ry="15" class="lk-drop"/>
              <ellipse cx="385" cy="420" rx="9" ry="15" class="lk-drop"/>
            </g>
          </svg>
          <div class="lk-words">
            <span class="lk-tag" id="lk-tag1">有漏之因 · 存不住</span>
            <span class="lk-tag" id="lk-tag2">虽有非实</span>
          </div>"""),

# S12 真功德·亮一下 134.20–150.08（cue89–97）
Scene("sc-real", 134.20, 150.08, """
          <div class="rl-lead" id="rl-lead">那真功德，就是那八个字 ——</div>
          <div class="rl-words" id="rl-words"><span id="rlw1">净智妙圆</span><span class="rl-dot">·</span><span id="rlw2">体自空寂</span></div>
          <svg id="rl-svg" viewBox="0 0 200 200"><g id="rl-glow">
            <circle cx="100" cy="100" r="26" id="rl-core"/>
            <line x1="100" y1="30" x2="100" y2="60" class="rl-ray"/>
            <line x1="100" y1="140" x2="100" y2="170" class="rl-ray"/>
            <line x1="30" y1="100" x2="60" y2="100" class="rl-ray"/>
            <line x1="140" y1="100" x2="170" y2="100" class="rl-ray"/>
          </g></svg>
          <div class="rl-sub" id="rl-sub">心里真正亮堂了一下 · 清净了一下 —— 不在外头，不以世求</div>"""),

# S13 圣凡 150.08–175.26（cue98–112）
Scene("sc-holy", 150.08, 175.26, """
          <div class="hy-lead" id="hy-lead">「廓然无圣」，拿走了他最后一个念想</div>
          <div class="hy-cols">
            <div class="hy-col" id="hyc1">谁是圣人 · 谁是凡人</div>
            <div class="hy-col" id="hyc2">谁功德大 · 谁功德小</div>
          </div>
          <div class="hy-note" id="hy-note">他一辈子比来比去，总想够着那个高高在上的「圣」</div>
          <div class="hy-end" id="hy-end">结果达摩说 —— 没有那个东西</div>"""),

# S14 凡圣同心 175.26–189.86（cue113–120）
Scene("sc-sameheart", 175.26, 189.86, """
          <div class="sh2-big" id="sh2-big">凡人和圣人，用的是同一颗心</div>
          <div class="sh2-note" id="sh2-note">哪儿来一个远在天边的圣人，等你攒够了分去换？</div>
          <div class="sh2-tail" id="sh2-tail">名字一给，就又落到那个框框里去了</div>"""),

# S15 史料诚实 189.86–209.94（cue121–129）
Scene("sc-history", 189.86, 209.94, """
          <div class="hi2-lead" id="hi2-lead">得交代一句 ——</div>
          <div class="hi2-card" id="hi2-card">
            <div class="hi2-l" id="hi2l1">这段对话，最早见于宋代灯录</div>
            <div class="hi2-l dim" id="hi2l2">已经是好几百年以后 · 见没见上面，都不一定</div>
          </div>
          <div class="hi2-end" id="hi2-end">但它流传一千多年 —— 把两种活法，说得太透了</div>"""),

# S16 一苇渡江 209.94–224.88（cue130–138）
Scene("sc-river", 209.94, 224.88, """
          <div class="rv-note" id="rv-note">接不住这话，达摩转身就走，一路往北</div>
          <svg id="rv-svg" viewBox="0 0 1000 460">
            <path d="M40 300 q60 -40 120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0" id="rv-wave1"/>
            <path d="M0 360 q60 -40 120 0 t120 0 t120 0 t120 0 t120 0 t120 0 t120 0" id="rv-wave2"/>
            <g transform="translate(150,0)"><g id="rv-man">
              <line x1="0" y1="250" x2="0" y2="150" class="rv-reed"/>
              <ellipse cx="0" cy="252" rx="120" ry="12" class="rv-reed2"/>
              <circle cx="0" cy="110" r="26" class="rv-head"/>
              <path d="M-34 180 Q0 120 34 180 L34 250 L-34 250 Z" class="vr2-robe"/>
            </g></g>
          </svg>
          <div class="rv-name" id="rv-name">一苇渡江</div>"""),

# S17 面壁·壁观·勿扰 224.88–260.44（cue139–161）
Scene("sc-wall", 224.88, 260.44, """
          <div class="wl-lead" id="wl-lead">嵩山少林寺 · 钻进后山石洞，对墙一坐 —— 整整九年</div>
          <div class="wl-name" id="wl-name">壁观婆罗门</div>
          <svg id="wl-phone" viewBox="0 0 240 400">
            <rect x="20" y="16" width="200" height="368" rx="34" id="wl-body2"/>
            <circle cx="120" cy="48" r="5" id="wl-cam"/>
            <path d="M120 130 a34 34 0 1 0 26 56 a44 44 0 1 1 -26 -56 Z" id="wl-moon"/>
            <rect x="80" y="250" width="80" height="10" rx="5" id="wl-bar1"/>
            <rect x="60" y="278" width="120" height="10" rx="5" id="wl-bar2"/>
          </svg>
          <div class="wl-sub" id="wl-sub">就像手机开了「勿扰模式」 —— 世界清净了，手机还在好好运行</div>
          <div class="wl-tail" id="wl-tail">心像一堵墙，安安静静的，可啥都清楚</div>"""),

# S18 生前死后·反差 260.44–298.02（cue162–180）
Scene("sc-contrast", 260.44, 298.02, """
          <div class="ct-lead" id="ct-lead">最有意思的，是这前后的反差</div>
          <div class="ct-cards">
            <div class="ct-card before" id="ctc-before">
              <div class="ct-h">他活着的时候</div>
              <div class="ct-l" id="ctb1">没有自己的庙</div>
              <div class="ct-l" id="ctb2">没什么声势</div>
              <div class="ct-l" id="ctb3">身边就几个徒弟</div>
              <div class="ct-endline" id="ctb4">挺不起眼的一个人</div>
            </div>
            <div class="ct-arrow" id="ct-arrow">拨两百年 →</div>
            <div class="ct-card after" id="ctc-after">
              <div class="ct-h">两百年以后</div>
              <div class="ct-l" id="cta1">禅宗成了最大的一派</div>
              <div class="ct-l" id="cta2">十有七八自称达摩后人</div>
              <div class="ct-l" id="cta3">少林寺被认作祖庭</div>
              <div class="ct-endline hot" id="cta4">面壁的洞，也成了圣地</div>
            </div>
          </div>
          <div class="ct-final" id="ct-final">活着冷冷清清，走了以后，反倒开出一座大山</div>"""),

# S19 谁赢了 298.02–324.34（cue181–195）
Scene("sc-who", 298.02, 324.34, """
          <div class="wo-q" id="wo-q">绕回开头 —— 梁武帝和达摩，到底谁赢了？</div>
          <div class="wo-cards">
            <div class="wo-card emperor" id="woc-emp">
              <div class="wo-h">皇帝</div>
              <div class="wo-l" id="woe1">调动整个国家，指标刷到顶</div>
              <div class="wo-res" id="woe2">可大梁江山，没多久就没了</div>
            </div>
            <div class="wo-card master" id="woc-mas">
              <div class="wo-h">达摩</div>
              <div class="wo-l" id="wom1">啥也没有，就几句话、一个背影</div>
              <div class="wo-res hot" id="wom2">偏偏撑起一千五百年的大宗</div>
            </div>
          </div>"""),

# S20 真传·抛问 324.34–350.28（cue196–209）
Scene("sc-pass", 324.34, 350.28, """
          <div class="pa-lead" id="pa-lead">真正能传下去的，不是数字堆得有多高</div>
          <div class="pa-big" id="pa-big">而是你在心里，是不是真点亮了什么</div>
          <div class="pa-q" id="pa-q">你天天拼命在攒的这些 —— 是会一路漏光的福报，还是真能留下来的东西？</div>
          <div class="pa-tail" id="pa-tail">答案，你自己心里有数就好</div>"""),

# S21 慧可慧能·道别 350.28–387.90（cue210–230）
Scene("sc-next", 350.28, total, """
          <div class="nx-cards">
            <div class="nx-card" id="nxc1">
              <div class="nx-h">二祖慧可</div>
              <div class="nx-l" id="nx1l">大雪里站到天亮 · 为求法砍了一条胳膊</div>
              <div class="nx-l" id="nx1l2">达摩把衣钵和《楞伽经》传给了他</div>
            </div>
            <div class="nx-card" id="nxc2">
              <div class="nx-h">砍柴人 · 慧能</div>
              <div class="nx-l" id="nx2l">大字不识，对着神秀那首偈也题了一首</div>
              <div class="nx-l hot" id="nx2l2">短短二十个字 —— 「本来无一物」</div>
            </div>
          </div>
          <div class="nx-next" id="nx-next">下一期，咱们讲慧能</div>
          <div class="nx-bye" id="nx-bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 场景专属 CSS ----------
PROJECT_CSS = """
      /* ===== S1 遗问 ===== */
      .rp-lead { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:52px; color:#5f574c; }
      .rp-name { position:absolute; left:0; right:0; top:262px; text-align:center;
        font-size:180px; color:#2b2620; letter-spacing:.12em; text-indent:.12em; }
      .rp-q { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:58px; color:#2b2620; }
      .rp-hint { position:absolute; left:0; right:0; bottom:232px; text-align:center;
        font-size:54px; color:#b03120; }

      /* ===== S2 达摩登场 ===== */
      .dn-note { position:absolute; left:120px; right:120px; top:210px; text-align:center;
        font-size:54px; color:#5f574c; line-height:1.5; }
      .dn-name { position:absolute; left:0; right:0; top:392px; text-align:center;
        font-size:190px; color:#2b2620; letter-spacing:.14em; text-indent:.14em; }
      .dn-sub { position:absolute; left:0; right:0; bottom:248px; text-align:center;
        font-size:52px; color:#8a6418; letter-spacing:.08em; }

      /* ===== S3 报名 ===== */
      .hi-main { position:absolute; left:0; right:0; top:380px; text-align:center;
        font-size:108px; color:#2b2620; letter-spacing:.06em; }
      .hi-sub { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:54px; color:#8a6418; }

      /* ===== S4 成绩单 ===== */
      .sc-lead { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:52px; color:#5f574c; }
      .sc-card { position:absolute; left:50%; top:268px; transform:translateX(-50%);
        width:760px; background:#fdfaf2; border:3px solid #d8cfb8; border-radius:18px;
        padding:26px 44px; }
      .sc-row { display:flex; align-items:center; padding:18px 0;
        border-bottom:2px dashed #d8cfb8; }
      .sc-row:last-child { border-bottom:none; }
      .sc-k { font-size:52px; color:#b03120; width:90px; }
      .sc-t { font-size:64px; color:#2b2620; letter-spacing:.06em; }
      .sc-ask { position:absolute; left:0; right:0; bottom:208px; text-align:center;
        font-size:72px; color:#b03120; }

      /* ===== 四问统一问答卡（S5/S7/S8/S9） ===== */
      .qa-q { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:56px; color:#5f574c; }
      .qa-big { position:absolute; left:0; right:0; top:350px; text-align:center;
        font-size:186px; color:#b03120; letter-spacing:.16em; text-indent:.16em;
        line-height:1.1; }
      .qa-words { position:absolute; left:0; right:0; top:400px; text-align:center;
        font-size:120px; color:#b03120; letter-spacing:.06em; }
      .qa-words span { display:inline-block; }
      .qa-dot { color:#8a6418; margin:0 24px; }
      .qa-tail { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:56px; color:#2b2620; }

      /* ===== S6 人天小果 ===== */
      .vd-q { position:absolute; left:0; right:0; top:230px; text-align:center;
        font-size:60px; color:#5f574c; }
      .vd-card { position:absolute; left:0; right:0; top:370px; text-align:center; }
      .vd-l { display:inline-block; margin:0 30px; padding:24px 50px;
        background:#fdfaf2; border:3px solid #b7a079; border-radius:16px;
        font-size:86px; color:#b03120; letter-spacing:.08em; }

      /* ===== S10 追影子 ===== */
      .sh-note { position:absolute; left:120px; right:120px; top:120px; text-align:center;
        font-size:48px; color:#5f574c; }
      #sh-svg { position:absolute; left:50%; top:210px; transform:translateX(-50%);
        width:780px; height:406px; }
      #sh-sun { fill:#8a6418; }
      #sh-ground { stroke:#2b2620; stroke-width:5; }
      #sh-shadow ellipse { fill:rgba(43,38,32,.18); }
      #sh-shadow path { fill:rgba(43,38,32,.10); }
      #sh-head { fill:#fdfaf2; stroke:#2b2620; stroke-width:5; }
      #sh-kid path { fill:rgba(176,49,32,.08); stroke:#b03120; stroke-width:5;
        stroke-linejoin:round; }
      #sh-arm { stroke:#2b2620; stroke-width:6; stroke-linecap:round; }
      .sh-leg { stroke:#2b2620; stroke-width:6; stroke-linecap:round; }
      .sh-drop { position:absolute; left:120px; right:120px; bottom:150px; text-align:center;
        font-size:58px; color:#b03120; }

      /* ===== S11 攥水 ===== */
      .lk-note { position:absolute; left:120px; right:120px; top:132px; text-align:center;
        font-size:46px; color:#5f574c; line-height:1.5; }
      #lk-svg { position:absolute; left:50%; top:250px; transform:translateX(-50%);
        width:560px; height:300px; }
      #lk-palm { fill:#f3ead6; stroke:#2b2620; stroke-width:5; stroke-linejoin:round; }
      .lk-finger { stroke:#2b2620; stroke-width:5; }
      .lk-drop { fill:#3d6ea5; }
      .lk-words { position:absolute; left:0; right:0; bottom:150px; text-align:center; }
      .lk-tag { display:inline-block; margin:0 22px; padding:16px 38px;
        background:#fdfaf2; border:3px solid #b7a079; border-radius:14px;
        font-size:58px; color:#b03120; }

      /* ===== S12 真功德 ===== */
      .rl-lead { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:54px; color:#5f574c; }
      .rl-words { position:absolute; left:0; right:0; top:268px; text-align:center;
        font-size:104px; color:#b03120; }
      .rl-words span { display:inline-block; }
      .rl-dot { color:#8a6418; margin:0 20px; }
      #rl-svg { position:absolute; right:250px; top:250px; width:150px; height:150px; }
      #rl-core { fill:#8a6418; }
      .rl-ray { stroke:#8a6418; stroke-width:8; stroke-linecap:round; }
      .rl-sub { position:absolute; left:140px; right:140px; bottom:220px; text-align:center;
        font-size:50px; color:#2b2620; line-height:1.5; }

      /* ===== S13 圣凡 ===== */
      .hy-lead { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:58px; color:#b03120; }
      .hy-cols { position:absolute; left:0; right:0; top:330px; text-align:center; }
      .hy-col { display:inline-block; margin:0 28px; padding:30px 44px;
        background:#fdfaf2; border:3px solid #d8cfb8; border-radius:16px;
        font-size:64px; color:#2b2620; }
      .hy-note { position:absolute; left:160px; right:160px; top:560px; text-align:center;
        font-size:50px; color:#5f574c; }
      .hy-end { position:absolute; left:0; right:0; bottom:232px; text-align:center;
        font-size:74px; color:#b03120; }

      /* ===== S14 凡圣同心 ===== */
      .sh2-big { position:absolute; left:120px; right:120px; top:270px; text-align:center;
        font-size:104px; color:#2b2620; line-height:1.35; }
      .sh2-note { position:absolute; left:160px; right:160px; top:520px; text-align:center;
        font-size:54px; color:#5f574c; }
      .sh2-tail { position:absolute; left:0; right:0; bottom:240px; text-align:center;
        font-size:56px; color:#b03120; }

      /* ===== S15 史料 ===== */
      .hi2-lead { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:56px; color:#5f574c; }
      .hi2-card { position:absolute; left:160px; right:160px; top:300px;
        background:#fdfaf2; border:3px solid #d8cfb8; border-radius:18px; padding:34px 44px; }
      .hi2-l { font-size:60px; color:#2b2620; line-height:1.5; }
      .hi2-l.dim { font-size:50px; color:#5f574c; }
      .hi2-end { position:absolute; left:140px; right:140px; bottom:232px; text-align:center;
        font-size:54px; color:#b03120; line-height:1.5; }

      /* ===== S16 一苇渡江 ===== */
      .rv-note { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:50px; color:#5f574c; }
      #rv-svg { position:absolute; left:50%; top:240px; transform:translateX(-50%);
        width:820px; height:380px; }
      #rv-wave1, #rv-wave2 { fill:none; stroke:#8a6418; stroke-width:5;
        stroke-linecap:round; }
      #rv-wave2 { stroke:#b7a079; }
      .rv-reed { stroke:#2b2620; stroke-width:6; }
      .rv-reed2 { fill:rgba(138,100,24,.18); stroke:#2b2620; stroke-width:4; }
      .rv-head { fill:#fdfaf2; stroke:#2b2620; stroke-width:5; }
      .vr2-robe { fill:rgba(176,49,32,.08); stroke:#b03120; stroke-width:5;
        stroke-linejoin:round; }
      .rv-name { position:absolute; left:0; right:0; bottom:220px; text-align:center;
        font-size:88px; color:#b03120; letter-spacing:.3em; text-indent:.3em; }

      /* ===== S17 面壁勿扰 ===== */
      .wl-lead { position:absolute; left:140px; right:140px; top:130px; text-align:center;
        font-size:50px; color:#2b2620; line-height:1.5; }
      .wl-name { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:96px; color:#b03120; letter-spacing:.2em; text-indent:.2em; }
      #wl-phone { position:absolute; right:230px; top:250px; width:200px; height:330px; }
      #wl-body2 { fill:#fdfaf2; stroke:#2b2620; stroke-width:6; }
      #wl-cam { fill:#5f574c; }
      #wl-moon { fill:#8a6418; }
      #wl-bar1, #wl-bar2 { fill:#5f574c; }
      .wl-sub { position:absolute; left:140px; width:820px; top:600px;
        font-size:48px; color:#5f574c; line-height:1.5; }
      .wl-tail { position:absolute; left:140px; right:140px; bottom:200px; text-align:center;
        font-size:58px; color:#b03120; }

      /* ===== S18 反差 ===== */
      .ct-lead { position:absolute; left:0; right:0; top:118px; text-align:center;
        font-size:52px; color:#5f574c; }
      .ct-cards { position:absolute; left:120px; right:120px; top:230px;
        display:flex; align-items:stretch; justify-content:center; }
      .ct-card { width:560px; padding:26px 36px; background:#fdfaf2;
        border:3px solid #d8cfb8; border-radius:18px; }
      .ct-card.after { border-color:#4d7c2f; background:#f3f8ec; }
      .ct-h { font-size:48px; color:#8a6418; margin-bottom:14px; }
      .ct-l { font-size:46px; color:#2b2620; line-height:1.7; }
      .ct-endline { margin-top:14px; font-size:50px; color:#2b2620; }
      .ct-endline.hot { color:#b03120; }
      .ct-arrow { display:flex; align-items:center; padding:0 30px;
        font-size:52px; color:#8a6418; }
      .ct-final { position:absolute; left:120px; right:120px; bottom:130px; text-align:center;
        font-size:54px; color:#b03120; }

      /* ===== S19 谁赢了 ===== */
      .wo-q { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:64px; color:#2b2620; }
      .wo-cards { position:absolute; left:160px; right:160px; top:310px;
        display:flex; justify-content:center; gap:60px; }
      .wo-card { width:680px; padding:30px 38px; background:#fdfaf2;
        border:3px solid #d8cfb8; border-radius:18px; }
      .wo-card.master { border-color:#4d7c2f; }
      .wo-h { font-size:54px; color:#8a6418; margin-bottom:14px; }
      .wo-l { font-size:48px; color:#2b2620; line-height:1.5; }
      .wo-res { margin-top:16px; font-size:54px; color:#5f574c; line-height:1.4; }
      .wo-res.hot { color:#b03120; }

      /* ===== S20 真传抛问 ===== */
      .pa-lead { position:absolute; left:140px; right:140px; top:180px; text-align:center;
        font-size:60px; color:#5f574c; }
      .pa-big { position:absolute; left:140px; right:140px; top:330px; text-align:center;
        font-size:86px; color:#b03120; line-height:1.4; }
      .pa-q { position:absolute; left:160px; right:160px; top:540px; text-align:center;
        font-size:50px; color:#2b2620; line-height:1.5; }
      .pa-tail { position:absolute; left:0; right:0; bottom:232px; text-align:center;
        font-size:58px; color:#8a6418; }

      /* ===== S21 慧可慧能道别 ===== */
      .nx-cards { position:absolute; left:140px; right:140px; top:180px;
        display:flex; justify-content:center; gap:56px; }
      .nx-card { width:720px; padding:30px 38px; background:#fdfaf2;
        border:3px solid #d8cfb8; border-radius:18px; }
      #nxc2 { border-color:#4d7c2f; }
      .nx-h { font-size:56px; color:#8a6418; margin-bottom:14px; }
      .nx-l { font-size:46px; color:#2b2620; line-height:1.55; }
      .nx-l.hot { color:#b03120; }
      .nx-next { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:72px; color:#b03120; }
      .nx-bye { position:absolute; left:0; right:0; bottom:232px; text-align:center;
        font-size:62px; color:#2b2620; letter-spacing:.06em; }
"""

# ---------- 场景时间轴（时间显式给秒） ----------
SCENE_JS = """
      /* S1 遗问 0–15.02 */
      tl.fromTo('#sc-recap > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#rp-lead',{y:30,opacity:0,duration:.6},.2);
      tl.from('#rp-name',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},2.0);
      tl.from('#rp-q',{y:26,opacity:0,duration:.6},3.6);
      tl.from('#rp-hint',{y:26,opacity:0,duration:.6},5.7);
      tl.to('#sc-recap > .scene-inner',{opacity:0,duration:.4},14.62);

      /* S2 达摩 15.02–21.70 */
      tl.fromTo('#sc-damo > .scene-inner',{opacity:0},{opacity:1,duration:.5},15.02);
      tl.from('#dn-note',{y:26,opacity:0,duration:.7},15.3);
      tl.from('#dn-name',{scale:.72,opacity:0,duration:.8,ease:'back.out(1.5)'},16.8);
      tl.from('#dn-sub',{y:22,opacity:0,duration:.6},19.8);
      tl.to('#sc-damo > .scene-inner',{opacity:0,duration:.4},21.3);

      /* S3 报名 21.70–25.38 */
      tl.fromTo('#sc-hi > .scene-inner',{opacity:0},{opacity:1,duration:.5},21.70);
      tl.from('#hi-main',{y:40,opacity:0,duration:.7,ease:'back.out(1.5)'},21.9);
      tl.from('#hi-sub',{y:22,opacity:0,duration:.6},24.2);
      tl.to('#sc-hi > .scene-inner',{opacity:0,duration:.35},25.0);

      /* S4 成绩单 25.38–38.62 */
      tl.fromTo('#sc-score > .scene-inner',{opacity:0},{opacity:1,duration:.5},25.38);
      tl.from('#sc-lead',{y:24,opacity:0,duration:.6},25.6);
      tl.from('#sc-card',{y:46,opacity:0,duration:.8,ease:'back.out(1.4)'},27.4);
      tl.from('#scr1,#scr2,#scr3',{x:-40,opacity:0,duration:.55,stagger:1.0},28.4);
      tl.from('#sc-ask',{scale:.7,opacity:0,duration:.7,ease:'back.out(1.7)'},35.6);
      tl.to('#sc-score > .scene-inner',{opacity:0,duration:.4},38.22);

      /* S5 一问 38.62–46.62 */
      tl.fromTo('#sc-q1 > .scene-inner',{opacity:0},{opacity:1,duration:.5},38.62);
      tl.from('#q1q',{y:24,opacity:0,duration:.6},38.9);
      tl.from('#q1b',{scale:.6,opacity:0,duration:.7,ease:'back.out(1.7)'},41.9);
      tl.from('#q1t',{y:22,opacity:0,duration:.6},43.9);
      tl.to('#sc-q1 > .scene-inner',{opacity:0,duration:.4},46.22);

      /* S6 人天小果 46.62–53.48 */
      tl.fromTo('#sc-verdict > .scene-inner',{opacity:0},{opacity:1,duration:.5},46.62);
      tl.from('#vd-q',{y:22,opacity:0,duration:.6},46.9);
      tl.from('#vdl1,#vdl2',{y:40,opacity:0,duration:.6,ease:'back.out(1.6)',stagger:.9},49.0);
      tl.to('#sc-verdict > .scene-inner',{opacity:0,duration:.4},53.08);

      /* S7 二问 53.48–59.38 */
      tl.fromTo('#sc-q2 > .scene-inner',{opacity:0},{opacity:1,duration:.5},53.48);
      tl.from('#q2q',{y:24,opacity:0,duration:.6},53.7);
      tl.from('#q2w1',{y:30,opacity:0,duration:.6,ease:'back.out(1.5)'},55.2);
      tl.from('#q2w2',{y:30,opacity:0,duration:.6,ease:'back.out(1.5)'},57.6);
      tl.to('#sc-q2 > .scene-inner',{opacity:0,duration:.4},58.98);

      /* S8 三问 59.38–74.34 */
      tl.fromTo('#sc-q3 > .scene-inner',{opacity:0},{opacity:1,duration:.5},59.38);
      tl.from('#q3q',{y:24,opacity:0,duration:.6},59.7);
      tl.from('#q3b',{scale:.6,opacity:0,duration:.7,ease:'back.out(1.7)'},68.0);
      tl.from('#q3t',{y:22,opacity:0,duration:.6},70.3);
      tl.to('#sc-q3 > .scene-inner',{opacity:0,duration:.4},73.94);

      /* S9 四问 74.34–82.80 */
      tl.fromTo('#sc-q4 > .scene-inner',{opacity:0},{opacity:1,duration:.5},74.34);
      tl.from('#q4q',{y:24,opacity:0,duration:.6},76.6);
      tl.from('#q4b',{scale:.6,opacity:0,duration:.7,ease:'back.out(1.7)'},80.2);
      tl.from('#q4t',{y:22,opacity:0,duration:.6},81.6);
      tl.to('#sc-q4 > .scene-inner',{opacity:0,duration:.4},82.4);

      /* S10 追影子 82.80–105.02 */
      tl.fromTo('#sc-shadow > .scene-inner',{opacity:0},{opacity:1,duration:.5},82.80);
      tl.from('#sh-note',{y:22,opacity:0,duration:.6},83.0);
      tl.from('#sh-sun',{scale:0,opacity:0,duration:.6,ease:'back.out(2)'},85.6);
      tl.from('#sh-kid',{opacity:0,duration:.5},88.4);
      tl.to('#sh-kid',{x:150,duration:2.2,ease:'sine.inOut',yoyo:true,repeat:3},89.0);
      tl.to('#sh-shadow',{x:150,duration:2.2,ease:'sine.inOut',yoyo:true,repeat:3},89.0);
      tl.to('#sh-arm',{rotation:14,transformOrigin:'left center',duration:.5,
        ease:'sine.inOut',yoyo:true,repeat:5},92);
      tl.from('#sh-drop',{y:26,opacity:0,duration:.7},99.6);
      tl.to('#sc-shadow > .scene-inner',{opacity:0,duration:.4},104.62);

      /* S11 攥水 105.02–134.20 */
      tl.fromTo('#sc-leak > .scene-inner',{opacity:0},{opacity:1,duration:.5},105.02);
      tl.from('#lk-note',{y:24,opacity:0,duration:.7},105.3);
      tl.from('#lk-hand',{y:40,opacity:0,duration:.8,ease:'back.out(1.4)'},110.0);
      tl.from('#lk-drops',{opacity:0,duration:.4},118.2);
      tl.to('.lk-drop',{y:60,opacity:.25,duration:1.6,ease:'sine.in',stagger:.4,repeat:3},118.6);
      tl.from('#lk-tag1',{y:26,opacity:0,duration:.6},125.0);
      tl.from('#lk-tag2',{scale:.6,opacity:0,duration:.7,ease:'back.out(1.8)'},128.0);
      tl.to('#sc-leak > .scene-inner',{opacity:0,duration:.4},133.8);

      /* S12 真功德 134.20–150.08 */
      tl.fromTo('#sc-real > .scene-inner',{opacity:0},{opacity:1,duration:.5},134.20);
      tl.from('#rl-lead',{y:24,opacity:0,duration:.6},134.5);
      tl.from('#rlw1,#rlw2',{y:28,opacity:0,duration:.6,ease:'back.out(1.5)',stagger:.7},135.8);
      tl.from('#rl-glow',{scale:.4,opacity:0,duration:.7,ease:'back.out(1.8)'},139.6);
      tl.to('#rl-core',{scale:1.15,transformOrigin:'center',duration:1.1,
        ease:'sine.inOut',yoyo:true,repeat:-1},140.4);
      tl.from('#rl-sub',{y:24,opacity:0,duration:.7},143.4);
      tl.to('#sc-real > .scene-inner',{opacity:0,duration:.4},149.68);

      /* S13 圣凡 150.08–175.26 */
      tl.fromTo('#sc-holy > .scene-inner',{opacity:0},{opacity:1,duration:.5},150.08);
      tl.from('#hy-lead',{y:24,opacity:0,duration:.6},153.4);
      tl.from('#hyc1,#hyc2',{y:34,opacity:0,duration:.6,ease:'back.out(1.5)',stagger:1.0},159.2);
      tl.from('#hy-note',{y:22,opacity:0,duration:.6},165.6);
      tl.from('#hy-end',{scale:.7,opacity:0,duration:.7,ease:'back.out(1.7)'},168.6);
      tl.to('#sc-holy > .scene-inner',{opacity:0,duration:.4},174.86);

      /* S14 凡圣同心 175.26–189.86 */
      tl.fromTo('#sc-sameheart > .scene-inner',{opacity:0},{opacity:1,duration:.5},175.26);
      tl.from('#sh2-big',{y:34,opacity:0,duration:.8,ease:'back.out(1.4)'},177.0);
      tl.from('#sh2-note',{y:22,opacity:0,duration:.6},181.4);
      tl.from('#sh2-tail',{y:22,opacity:0,duration:.6},186.8);
      tl.to('#sc-sameheart > .scene-inner',{opacity:0,duration:.4},189.46);

      /* S15 史料 189.86–209.94 */
      tl.fromTo('#sc-history > .scene-inner',{opacity:0},{opacity:1,duration:.5},189.86);
      tl.from('#hi2-lead',{y:22,opacity:0,duration:.6},190.1);
      tl.from('#hi2-card',{y:40,opacity:0,duration:.8,ease:'back.out(1.4)'},192.6);
      tl.from('#hi2-end',{y:24,opacity:0,duration:.7},205.0);
      tl.to('#sc-history > .scene-inner',{opacity:0,duration:.4},209.54);

      /* S16 一苇渡江 209.94–224.88 */
      tl.fromTo('#sc-river > .scene-inner',{opacity:0},{opacity:1,duration:.5},209.94);
      tl.from('#rv-note',{y:22,opacity:0,duration:.6},210.2);
      tl.from('#rv-wave1,#rv-wave2',{opacity:0,duration:.8,stagger:.2},213.2);
      tl.from('#rv-man',{opacity:0,duration:.5},214.0);
      tl.to('#rv-man',{x:720,duration:8.6,ease:'none'},214.4);
      tl.from('#rv-name',{scale:.6,opacity:0,duration:.8,ease:'back.out(1.8)'},220.0);
      tl.to('#sc-river > .scene-inner',{opacity:0,duration:.4},224.48);

      /* S17 面壁勿扰 224.88–260.44 */
      tl.fromTo('#sc-wall > .scene-inner',{opacity:0},{opacity:1,duration:.5},224.88);
      tl.from('#wl-lead',{y:24,opacity:0,duration:.7},225.1);
      tl.from('#wl-name',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.6)'},233.8);
      tl.from('#wl-phone',{x:60,opacity:0,duration:.8,ease:'back.out(1.5)'},238.8);
      tl.to('#wl-moon',{scale:1.12,transformOrigin:'center',duration:1.2,
        ease:'sine.inOut',yoyo:true,repeat:-1},242);
      tl.from('#wl-sub',{y:24,opacity:0,duration:.7},241.2);
      tl.from('#wl-tail',{y:22,opacity:0,duration:.6},254.2);
      tl.to('#sc-wall > .scene-inner',{opacity:0,duration:.4},260.04);

      /* S18 反差 260.44–298.02 */
      tl.fromTo('#sc-contrast > .scene-inner',{opacity:0},{opacity:1,duration:.5},260.44);
      tl.from('#ct-lead',{y:22,opacity:0,duration:.6},260.7);
      tl.from('#ctc-before',{x:-50,opacity:0,duration:.7,ease:'back.out(1.4)'},263.0);
      tl.from('#ct-arrow',{opacity:0,duration:.5},273.0);
      tl.from('#ctc-after',{x:50,opacity:0,duration:.7,ease:'back.out(1.4)'},274.0);
      tl.from('#ct-final',{y:24,opacity:0,duration:.7},290.0);
      tl.to('#sc-contrast > .scene-inner',{opacity:0,duration:.4},297.62);

      /* S19 谁赢了 298.02–324.34 */
      tl.fromTo('#sc-who > .scene-inner',{opacity:0},{opacity:1,duration:.5},298.02);
      tl.from('#wo-q',{y:26,opacity:0,duration:.7},298.3);
      tl.from('#woc-emp',{y:40,opacity:0,duration:.7,ease:'back.out(1.4)'},303.4);
      tl.from('#woc-mas',{y:40,opacity:0,duration:.7,ease:'back.out(1.4)'},311.0);
      tl.to('#wom2',{scale:1.05,transformOrigin:'center',duration:1.0,
        ease:'sine.inOut',yoyo:true,repeat:-1},316);
      tl.to('#sc-who > .scene-inner',{opacity:0,duration:.4},323.94);

      /* S20 真传抛问 324.34–350.28 */
      tl.fromTo('#sc-pass > .scene-inner',{opacity:0},{opacity:1,duration:.5},324.34);
      tl.from('#pa-lead',{y:24,opacity:0,duration:.6},325.0);
      tl.from('#pa-big',{scale:.72,opacity:0,duration:.8,ease:'back.out(1.6)'},327.2);
      tl.from('#pa-q',{y:24,opacity:0,duration:.7},337.0);
      tl.from('#pa-tail',{y:22,opacity:0,duration:.6},347.6);
      tl.to('#sc-pass > .scene-inner',{opacity:0,duration:.4},349.88);

      /* S21 慧可慧能 350.28–TOTAL */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},350.28);
      tl.from('#nxc1',{y:40,opacity:0,duration:.7,ease:'back.out(1.4)'},351.2);
      tl.from('#nxc2',{y:40,opacity:0,duration:.7,ease:'back.out(1.4)'},368.8);
      tl.from('#nx-next',{scale:.7,opacity:0,duration:.7,ease:'back.out(1.8)'},383.0);
      tl.from('#nx-bye',{y:22,opacity:0,duration:.6},386.4);
"""

# ---------- 底部字幕轨道 ----------
# 逐字高亮提前 WHISPER_WORD_LEAD，补偿 whisper 词时间戳偏晚（声音先、字幕迟）
frag = char_track(cues, chars, THEME.accent, word_lead=WHISPER_WORD_LEAD)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/damo-yeyang.wav", total),
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
