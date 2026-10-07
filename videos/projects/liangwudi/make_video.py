# -*- coding: utf-8 -*-
"""梁武帝成片生成器（宣纸主题，245.41s，16 幕）。

本片独有：16 幕 body 与场景时间轴。混用 PPT 式卡片——三净肉
checklist（S6）、南传地图（S7）、左右对比（S8）、四次舍身数据卡
（S10）、《断酒肉文》卷轴＋版本升级（S12）、终端配置卡（S13）、
结局时间轴（S14）。页面骨架／主题／字幕／clip 外壳全部复用 videopipe。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       XUANZHI)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars, TOTAL = data["cues"], data["chars"], data["duration"]
THEME = XUANZHI

# ---------- 16 幕 ----------
SCENES = [

# S1 承题·回闪八戒 0.00–16.76（cue1–6）
Scene("sc-recap", 0.00, 16.76, """
          <div class="rp-lead" id="rp-lead">上一集，我们把三个字拆开 ——</div>
          <div class="rp-chars" id="rp-chars"><span class="rp-c" id="rc1">猪</span><span class="rp-c" id="rc2">八</span><span class="rp-c" id="rc3">戒</span></div>
          <div class="rp-stamp" id="rp-stamp">「八戒」本是佛教戒律术语</div>
          <div class="rp-q" id="rp-q">可出家人还有一条更出名的规矩 ——</div>
          <div class="rp-veg" id="rp-veg">吃 素</div>"""),

# S2 青菜豆腐·花和尚 16.76–30.48（cue7–14）
Scene("sc-drama", 16.76, 30.48, """
          <div class="dr-note" id="dr-note">影视剧里，你熟得不能再熟的画面</div>
          <div class="dr-frame" id="dr-frame">
            <svg viewBox="0 0 900 430">
              <circle cx="300" cy="150" r="50" class="dr-head"/>
              <path d="M225 390 Q300 250 375 390" class="dr-robe"/>
              <ellipse cx="540" cy="300" rx="125" ry="26" class="dr-bowl"/>
              <path d="M415 300 Q540 365 665 300" class="dr-bowl"/>
              <path d="M430 292 q110 -26 220 0" class="dr-food"/>
              <g id="dr-meat"><line x1="728" y1="106" x2="624" y2="272" class="dr-chop"/>
                <path d="M588 262 q26 -18 52 2 q8 24 -22 32 q-32 6 -38 -18 Z" class="dr-pork"/></g>
            </svg>
          </div>
          <div class="dr-bad" id="dr-bad">花和尚 · 接下来准没好事</div>"""),

# S3 断言·揭晓 30.48–47.68（cue15–23）
Scene("sc-claim", 30.48, 47.68, """
          <div class="cl-lead" id="cl-lead">吃素，仿佛是和尚的出厂设置</div>
          <div class="cl-big" id="cl-big">但今天，先把结论拍在这儿：</div>
          <div class="cl-not" id="cl-not">不是佛祖亲口定的规矩</div>
          <div class="cl-yes" id="cl-yes">是一个皇帝，用行政命令推行的</div>
          <div class="cl-namewrap" id="cl-namewrap"><span class="cl-crown">♛</span><span class="cl-name" id="cl-name">梁武帝 · 萧衍</span></div>"""),

# S4 报名 47.68–52.54（cue24–27）
Scene("sc-hi", 47.68, 52.54, """
          <div class="hi-main" id="hi-main">哈喽大家好，我是叶扬</div>
          <div class="hi-sub" id="hi-sub">先来看看，佛教原本的规矩</div>"""),

# S5 托钵乞食 52.54–64.26（cue28–33）
Scene("sc-patra", 52.54, 64.26, """
          <svg id="pt-svg" viewBox="0 0 1920 1080">
            <g class="pt-house"><path d="M250 560 L320 500 L390 560"/><rect x="262" y="560" width="116" height="100"/></g>
            <g class="pt-house"><path d="M560 560 L630 500 L700 560"/><rect x="572" y="560" width="116" height="100"/></g>
            <g transform="translate(1500,500)"><g id="walker">
              <circle cx="0" cy="0" r="42" class="pt-head"/>
              <path d="M-52 150 Q0 45 52 150" class="pt-robe"/>
              <ellipse cx="0" cy="118" rx="66" ry="17" class="pt-bowl"/>
            </g></g>
          </svg>
          <div class="pt-note" id="pt-note">托钵乞食 · 施主给什么吃什么 —— 不能挑三拣四</div>"""),

# S6 三净肉 checklist（PPT 卡）64.26–75.28（cue34–39）
Scene("sc-three", 64.26, 75.28, """
          <div class="t3-title" id="t3-title">早期戒律：可以吃「三净肉」</div>
          <div class="t3-list">
            <div class="t3-row" id="r1"><span class="t3-box" id="b1">✓</span><span class="t3-t">不是为你杀的</span></div>
            <div class="t3-row" id="r2"><span class="t3-box" id="b2">✓</span><span class="t3-t">你没亲眼看见杀</span></div>
            <div class="t3-row" id="r3"><span class="t3-box" id="b3">✓</span><span class="t3-t">也没听见杀的声音</span></div>
          </div>
          <div class="t3-ok" id="t3-ok">三条满足，就不犯戒</div>"""),

# S7 南传地图 75.28–82.62（cue40–42）
Scene("sc-south", 75.28, 82.62, """
          <div class="sm-title" id="sm-title">这个传统，南传佛教一直保留到今天</div>
          <svg id="sm-map" viewBox="0 0 1000 440">
            <path d="M180 200 Q270 120 340 220 Q410 320 350 380" class="sm-land"/>
            <circle cx="310" cy="245" r="13" class="sm-dot" id="smd1"/>
            <text x="430" y="258" class="sm-tx">泰国</text>
            <circle cx="255" cy="325" r="13" class="sm-dot" id="smd2"/>
            <text x="370" y="338" class="sm-tx">斯里兰卡</text>
          </svg>
          <div class="sm-note" id="sm-note">僧人并不一律素食</div>"""),

# S8 左右对比·转场 82.62–88.28（cue43–45）
Scene("sc-turn", 82.62, 88.28, """
          <div class="tn-q" id="tn-q">那汉传这一支，怎么就全面吃素了？</div>
          <div class="tn-bowls">
            <div class="tn-b" id="tnb1"><div class="tn-emoji">🍲</div><div class="tn-lab">有荤有素</div></div>
            <div class="tn-arrow" id="tn-arrow">→</div>
            <div class="tn-b green" id="tnb2"><div class="tn-emoji">🥬</div><div class="tn-lab">全面吃素</div></div>
          </div>
          <div class="tn-ptr" id="tn-ptr">答案，在一个皇帝身上 ↓</div>"""),

# S9 萧衍其人 88.28–100.68（cue46–53）
Scene("sc-xiao", 88.28, 100.68, """
          <div class="xw-name" id="xw-name">萧 衍</div>
          <div class="xw-cards">
            <div class="xw-card" id="xc1"><span class="xw-k">文</span><span class="xw-d">才学过人</span></div>
            <div class="xw-card" id="xc2"><span class="xw-k">武</span><span class="xw-d">战功赫赫</span></div>
            <div class="xw-card" id="xc3"><span class="xw-k">帝</span><span class="xw-d">开国皇帝</span></div>
          </div>
          <div class="xw-turn" id="xw-turn">可到了晚年 —— 信佛信得极其投入</div>"""),

# S10 四次舍身·数据卡 100.68–117.62（cue54–62）
Scene("sc-shenshen", 100.68, 117.62, """
          <div class="ss-lead" id="ss-lead">他四次「舍身」同泰寺</div>
          <div class="ss-data"><span id="ss-num">4</span><span class="ss-unit">次</span></div>
          <div class="ss-change"><span id="ss-longpao">脱龙袍</span><span class="ss-arrow">→</span><span id="ss-jiasha">换袈裟</span></div>
          <div class="ss-ransom" id="ss-ransom">大臣凑了 <span class="ss-money">几亿钱</span>，才把皇帝赎回来</div>"""),

# S11 二手平台比喻 117.62–125.10（cue63–66）
Scene("sc-boss", 117.62, 125.10, """
          <div class="bs-note" id="bs-note">放到今天看，这行为艺术就像 ——</div>
          <div class="bs-card" id="bs-card">
            <div class="bs-url">二手交易平台</div>
            <div class="bs-item">
              <div class="bs-tag" id="bs-tag">在售 · 可议价</div>
              <div class="bs-who" id="bs-who">老板本人（九五成新）</div>
            </div>
          </div>
          <div class="bs-ransom" id="bs-ransom">让全公司凑钱，把他赎回去</div>"""),

# S12 断酒肉文·版本升级 125.10–149.46（cue67–76）
Scene("sc-edict", 125.10, 149.46, """
          <div class="ed-lead" id="ed-lead">但他不只做样子，要改一件真规矩 —— 全国僧人彻底断肉</div>
          <div class="ed-scrollwrap" id="ed-scrollwrap">
            <div class="ed-scroll" id="ed-scroll">
              <div class="ed-title">断 酒 肉 文</div>
              <div class="ed-bars"><span></span><span></span><span></span></div>
            </div>
          </div>
          <div class="ed-sutras" id="ed-sutras"><span id="es1">《涅槃经》</span><span id="es2">《楞伽经》</span></div>
          <div class="ed-debate" id="ed-debate">召集僧人开会辩论 · 不执行就处分</div>
          <div class="ed-version" id="ed-version">素食 v1.0 <span class="ed-v-arrow">→</span> <span class="ed-v2">v2.0 必须升级</span></div>"""),

# S13 终端配置卡·1500 年 149.46–166.68（cue77–85）
Scene("sc-config", 149.46, 166.68, """
          <div class="cf-term" id="cf-term">用我们做工程的话说 ——</div>
          <div class="cf-window" id="cf-window">
            <div class="cf-bar"><span></span><span></span><span></span></div>
            <div class="cf-code"><span id="cf-l1">$ sudo —— 动了最高权限</span><span id="cf-l2">$ set 全局默认配置 = 吃素</span></div>
          </div>
          <div class="cf-time" id="cf-time">人会死，朝会亡 —— 这个配置原样保留，跑了 <span class="cf-1500">1500 年</span></div>"""),

# S14 转折·台城·结局时间轴 166.68–190.66（cue86–98）
Scene("sc-fall", 166.68, 190.66, """
          <div class="fl-turn" id="fl-turn">但有趣的是 ——</div>
          <div class="fl-pair">
            <div class="fl-p ok" id="fp1">改得了<span>僧人的餐桌</span> ✓</div>
            <div class="fl-p no" id="fp2">守不住<span>自己的江山</span> ✗</div>
          </div>
          <div class="fl-war" id="fl-war">晚年收留降将侯景 · 侯景叛乱 · 攻破建康</div>
          <div class="fl-timeline">
            <span class="fl-n" id="fn1">86 岁</span><span class="fl-n" id="fn2">围困台城</span><span class="fl-n" id="fn3">病倒</span><span class="fl-n hot" id="fn4">饿死</span>
          </div>
          <div class="fl-end" id="fl-end">号令天下不吃肉的皇帝 —— 断粮而死</div>"""),

# S15 权力之问 190.66–207.08（cue99–106）
Scene("sc-power", 190.66, 207.08, """
          <div class="pw-q" id="pw-q">权力，到底能不能改变人心？</div>
          <div class="pw-cards">
            <div class="pw-c ok" id="pwc1"><div class="pw-lab">让几千万人戒荤吃素</div><div class="pw-res">他做到了 ✓</div></div>
            <div class="pw-c no" id="pwc2"><div class="pw-lab">用佛教慈悲换太平天下</div><div class="pw-res">到死没办到 ✗</div></div>
          </div>"""),

# S16 达摩预告·抛问·道别 207.08–TOTAL（cue107–130）
Scene("sc-damo", 207.08, TOTAL, """
          <div class="dm-note" id="dm-note">而他，并不是没有得到过提示 ——</div>
          <svg id="dm-sea" viewBox="0 0 1920 1080">
            <g transform="translate(360,560)"><g id="dm-boat"><path d="M0 0 l150 0 l-26 60 l-98 0 Z" class="dm-hull"/><line x1="75" y1="0" x2="75" y2="-130" class="dm-mast"/></g></g>
            <path class="dm-wave" d="M180 700 q50 -30 100 0 t100 0 t100 0"/>
          </svg>
          <div class="dm-meet" id="dm-meet">一位从海路远道而来的印度和尚，与他面对面坐着</div>
          <div class="dm-list" id="dm-list"><span>造寺</span><span>写经</span><span>度僧</span><span>四次舍身</span></div>
          <div class="dm-ask" id="dm-ask">这些，有没有功德？</div>
          <div class="dm-cold" id="dm-cold">对方的回答，冷得像一盆冰水 ❄</div>
          <div class="dm-go" id="dm-go">他听完没有懂 —— 和尚转身北上，一苇渡江</div>
          <div class="dm-next" id="dm-next">下一集，我们讲这位和尚：达摩</div>
          <div class="dm-finalq" id="dm-finalq">改变行为，和改变人心，中间到底隔着什么？</div>
          <div class="dm-cmt" id="dm-cmt">评论区告诉我</div>
          <div class="dm-bye" id="dm-bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 场景专属 CSS（占位，随后展开） ----------
PROJECT_CSS = """
      /* ===== S1 承题·八戒回闪 ===== */
      .rp-lead { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:52px; color:#2b2620; }
      .rp-chars { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .rp-c { display:inline-block; font-size:190px; color:#2b2620; width:270px;
        letter-spacing:0; }
      .rp-stamp { position:absolute; left:0; right:0; top:540px; text-align:center;
        font-size:46px; color:#b03120; letter-spacing:.05em; }
      .rp-q { position:absolute; left:0; right:0; bottom:440px; text-align:center;
        font-size:50px; color:#5f574c; }
      .rp-veg { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:128px; color:#b03120; letter-spacing:.22em; text-indent:.22em; }

      /* ===== S2 青菜豆腐·花和尚 ===== */
      .dr-note { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:50px; color:#2b2620; }
      .dr-frame { position:absolute; left:50%; top:250px; transform:translateX(-50%);
        width:780px; padding:24px 30px; background:#fdfaf2;
        border:2px solid #d8cfb8; border-radius:18px; }
      .dr-head { fill:none; stroke:#2b2620; stroke-width:5; }
      .dr-robe { fill:none; stroke:#2b2620; stroke-width:5; stroke-linecap:round; }
      .dr-bowl { fill:none; stroke:#8a6418; stroke-width:5; }
      .dr-food { fill:none; stroke:#4d7c2f; stroke-width:6; stroke-linecap:round; }
      .dr-chop { stroke:#2b2620; stroke-width:6; stroke-linecap:round; }
      .dr-pork { fill:#b03120; stroke:#7d2418; stroke-width:2; }
      .dr-bad { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:66px; color:#b03120; letter-spacing:.06em; }

      /* ===== S3 断言·揭晓 ===== */
      .cl-lead { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:50px; color:#2b2620; }
      .cl-big { position:absolute; left:0; right:0; top:270px; text-align:center;
        font-size:60px; color:#5f574c; }
      .cl-not { position:absolute; left:0; right:0; top:400px; text-align:center;
        font-size:88px; color:#2b2620; letter-spacing:.06em; }
      .cl-yes { position:absolute; left:0; right:0; top:550px; text-align:center;
        font-size:64px; color:#2b2620; }
      .cl-yes::first-letter { color:#b03120; }
      .cl-namewrap { position:absolute; left:0; right:0; bottom:240px; text-align:center; }
      .cl-crown { font-size:92px; color:#8a6418; margin-right:26px; vertical-align:middle; }
      .cl-name { font-size:96px; color:#b03120; letter-spacing:.08em; vertical-align:middle; }

      /* ===== S4 报名 ===== */
      .hi-main { position:absolute; left:0; right:0; top:380px; text-align:center;
        font-size:110px; color:#2b2620; letter-spacing:.08em; }
      .hi-sub { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:56px; color:#8a6418; letter-spacing:.06em; }

      /* ===== S5 托钵乞食 ===== */
      #pt-svg { position:absolute; inset:0; width:1920px; height:1080px; }
      .pt-house path { fill:none; stroke:#8a6418; stroke-width:6; stroke-linecap:round; }
      .pt-house rect { fill:none; stroke:#8a6418; stroke-width:6; }
      .pt-head { fill:none; stroke:#b03120; stroke-width:6; }
      .pt-robe { fill:rgba(176,49,32,.06); stroke:#b03120; stroke-width:6;
        stroke-linejoin:round; }
      .pt-bowl { fill:none; stroke:#2b2620; stroke-width:6; }
      .pt-note { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:52px; color:#2b2620; letter-spacing:.04em; }

      /* ===== S6 三净肉 checklist（PPT 卡） ===== */
      .t3-title { position:absolute; left:0; right:0; top:160px; text-align:center;
        font-size:76px; color:#2b2620; letter-spacing:.06em; }
      .t3-list { position:absolute; left:430px; right:430px; top:320px; }
      .t3-row { display:flex; align-items:center; margin-bottom:26px;
        padding:22px 40px; background:#fdfaf2; border:2px solid #d8cfb8;
        border-radius:14px; }
      .t3-box { display:inline-flex; align-items:center; justify-content:center;
        width:60px; height:60px; margin-right:36px; border-radius:12px;
        font-size:42px; border:3px solid #b7a079; color:transparent; }
      .t3-t { font-size:56px; color:#2b2620; }
      .t3-ok { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:60px; color:#b03120; letter-spacing:.1em; }

      /* ===== S7 南传地图 ===== */
      .sm-title { position:absolute; left:0; right:0; top:180px; text-align:center;
        font-size:56px; color:#2b2620; }
      #sm-map { position:absolute; left:50%; top:290px; transform:translateX(-50%);
        width:720px; height:320px; }
      .sm-land { fill:rgba(138,100,24,.08); stroke:#8a6418; stroke-width:5;
        stroke-linejoin:round; }
      .sm-dot { fill:#b03120; }
      .sm-tx { fill:#2b2620; font-size:44px; }
      .sm-note { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:60px; color:#b03120; letter-spacing:.08em; }

      /* ===== S8 左右对比·转场 ===== */
      .tn-q { position:absolute; left:0; right:0; top:180px; text-align:center;
        font-size:64px; color:#2b2620; }
      .tn-bowls { position:absolute; left:0; right:0; top:350px; display:flex;
        align-items:center; justify-content:center; }
      .tn-b { width:300px; padding:34px 20px; text-align:center; background:#fdfaf2;
        border:3px solid #d8cfb8; border-radius:18px; }
      .tn-emoji { font-size:120px; line-height:1.2; }
      .tn-lab { font-size:48px; color:#2b2620; }
      .tn-b.green { border-color:#4d7c2f; background:#f3f8ec; }
      .tn-b.green .tn-lab { color:#3f6625; }
      .tn-arrow { font-size:100px; color:#8a6418; margin:0 56px; }
      .tn-ptr { position:absolute; left:0; right:0; bottom:240px; text-align:center;
        font-size:52px; color:#8a6418; }

      /* ===== S9 萧衍其人 ===== */
      .xw-name { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:120px; color:#2b2620; letter-spacing:.2em; text-indent:.2em; }
      .xw-cards { position:absolute; left:0; right:0; top:370px; display:flex;
        justify-content:center; gap:44px; }
      .xw-card { width:280px; padding:34px 10px; text-align:center; background:#fdfaf2;
        border:2px solid #d8cfb8; border-radius:16px; }
      .xw-k { display:block; font-size:76px; color:#b03120; line-height:1.1; }
      .xw-d { display:block; margin-top:10px; font-size:44px; color:#5f574c; }
      .xw-turn { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:54px; color:#2b2620; }

      /* ===== S10 四次舍身·数据卡 ===== */
      .ss-lead { position:absolute; left:0; right:0; top:180px; text-align:center;
        font-size:60px; color:#2b2620; }
      .ss-data { position:absolute; left:0; right:0; top:290px; text-align:center; }
      #ss-num { font-size:210px; color:#b03120; line-height:1; vertical-align:middle; }
      .ss-unit { font-size:72px; color:#5f574c; margin-left:10px; vertical-align:middle; }
      .ss-change { position:absolute; left:0; right:0; top:580px; text-align:center;
        font-size:62px; color:#2b2620; }
      .ss-arrow { color:#8a6418; margin:0 18px; }
      #ss-jiasha { color:#b03120; }
      .ss-ransom { position:absolute; left:0; right:0; bottom:240px; text-align:center;
        font-size:52px; color:#2b2620; }
      .ss-money { color:#8a6418; font-size:64px; letter-spacing:.06em; }

      /* ===== S11 二手平台比喻 ===== */
      .bs-note { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:50px; color:#2b2620; }
      .bs-card { position:absolute; left:50%; top:280px; transform:translateX(-50%);
        width:880px; background:#fdfaf2; border:2px solid #d8cfb8;
        border-radius:16px; overflow:hidden; }
      .bs-url { padding:18px 30px; background:#e9e2d0; font-size:40px; color:#5f574c;
        border-bottom:2px solid #d8cfb8; }
      .bs-item { padding:44px 30px; text-align:center; }
      .bs-tag { display:inline-block; padding:10px 28px; border-radius:30px;
        background:#b03120; color:#fff; font-size:40px; }
      .bs-who { margin-top:28px; font-size:72px; color:#2b2620; }
      .bs-ransom { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:56px; color:#b03120; }

      /* ===== S12 断酒肉文·版本升级 ===== */
      .ed-lead { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:46px; color:#2b2620; }
      .ed-scrollwrap { position:absolute; left:0; right:0; top:230px; text-align:center; }
      .ed-scroll { display:inline-block; min-width:580px; padding:30px 56px;
        background:#fbf6e8; border:3px solid #8a6418; border-radius:12px;
        box-shadow:0 10px 30px rgba(138,100,24,.18); }
      .ed-title { font-size:80px; color:#b03120; letter-spacing:.12em;
        text-indent:.12em; text-align:center; }
      .ed-bars { margin-top:22px; }
      .ed-bars span { display:block; height:8px; margin-bottom:12px;
        background:#c9b78e; border-radius:4px; }
      .ed-sutras { position:absolute; left:0; right:0; top:600px; text-align:center; }
      .ed-sutras span { display:inline-block; margin:0 24px; padding:14px 34px;
        background:#fdfaf2; border:2px solid #b7a079; border-radius:12px;
        font-size:46px; color:#8a6418; }
      .ed-debate { position:absolute; left:0; right:0; top:710px; text-align:center;
        font-size:46px; color:#5f574c; }
      .ed-version { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:58px; color:#5f574c; }
      .ed-v-arrow { color:#8a6418; margin:0 8px; }
      .ed-v2 { color:#b03120; font-size:68px; letter-spacing:.06em; }

      /* ===== S13 终端配置卡·1500 年 ===== */
      .cf-term { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:52px; color:#2b2620; }
      .cf-window { position:absolute; left:50%; top:280px; transform:translateX(-50%);
        width:1080px; background:#fbf7ec; border:2px solid #b7a079;
        border-radius:14px; overflow:hidden; }
      .cf-bar { padding:16px 26px; background:#e9e2d0; border-bottom:2px solid #d8cfb8; }
      .cf-bar span { display:inline-block; width:22px; height:22px; margin-right:14px;
        border-radius:50%; background:#c9b78e; }
      .cf-code { padding:38px 44px; font-family:Consolas,"Courier New",monospace; }
      .cf-code span { display:block; font-size:46px; color:#2b2620; line-height:1.7; }
      .cf-time { position:absolute; left:0; right:0; bottom:240px; text-align:center;
        font-size:52px; color:#2b2620; }
      .cf-1500 { color:#8a6418; font-size:76px; letter-spacing:.06em; }

      /* ===== S14 转折·台城·结局时间轴 ===== */
      .fl-turn { position:absolute; left:0; right:0; top:140px; text-align:center;
        font-size:50px; color:#5f574c; }
      .fl-pair { position:absolute; left:0; right:0; top:230px; display:flex;
        justify-content:center; gap:60px; }
      .fl-p { width:520px; padding:30px 20px; text-align:center; border-radius:16px;
        font-size:58px; background:#fdfaf2; border:3px solid #d8cfb8; color:#2b2620; }
      .fl-p span { display:block; margin-top:8px; font-size:44px; color:#5f574c; }
      .fl-p.ok { border-color:#4d7c2f; }
      .fl-p.no { border-color:#b03120; }
      .fl-war { position:absolute; left:0; right:0; top:470px; text-align:center;
        font-size:48px; color:#2b2620; }
      .fl-timeline { position:absolute; left:160px; right:160px; top:590px;
        display:flex; justify-content:space-between; }
      .fl-n { padding:20px 34px; background:#fdfaf2; border:3px solid #b7a079;
        border-radius:12px; font-size:48px; color:#2b2620; }
      .fl-n.hot { border-color:#b03120; color:#b03120; }
      .fl-end { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:62px; color:#b03120; letter-spacing:.06em; }

      /* ===== S15 权力之问 ===== */
      .pw-q { position:absolute; left:0; right:0; top:220px; text-align:center;
        font-size:92px; color:#2b2620; letter-spacing:.06em; }
      .pw-cards { position:absolute; left:0; right:0; top:440px; display:flex;
        justify-content:center; gap:70px; }
      .pw-c { width:560px; padding:36px 24px; text-align:center; border-radius:18px;
        background:#fdfaf2; border:3px solid #d8cfb8; }
      .pw-lab { font-size:50px; color:#5f574c; }
      .pw-res { margin-top:18px; font-size:72px; color:#2b2620; }
      .pw-c.ok { border-color:#4d7c2f; }
      .pw-c.no { border-color:#b03120; }
      .pw-c.no .pw-res { color:#b03120; }

      /* ===== S16 达摩预告·抛问·道别 ===== */
      .dm-note { position:absolute; left:0; right:0; top:110px; text-align:center;
        font-size:46px; color:#2b2620; }
      #dm-sea { position:absolute; inset:0; width:1920px; height:1080px; }
      .dm-hull { fill:rgba(138,100,24,.14); stroke:#8a6418; stroke-width:5;
        stroke-linejoin:round; }
      .dm-mast { stroke:#8a6418; stroke-width:6; stroke-linecap:round; }
      .dm-wave { fill:none; stroke:#b7a079; stroke-width:5; stroke-linecap:round; }
      .dm-meet { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:54px; color:#2b2620; }
      .dm-list { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .dm-list span { display:inline-block; margin:0 16px; padding:12px 30px;
        background:#fdfaf2; border:2px solid #d8cfb8; border-radius:10px;
        font-size:44px; color:#2b2620; }
      .dm-ask { position:absolute; left:0; right:0; top:410px; text-align:center;
        font-size:84px; color:#b03120; letter-spacing:.08em; }
      .dm-cold { position:absolute; left:0; right:0; top:550px; text-align:center;
        font-size:52px; color:#3d6ea5; }
      .dm-go { position:absolute; left:0; right:0; bottom:350px; text-align:center;
        font-size:50px; color:#5f574c; }
      .dm-next { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:80px; color:#b03120; letter-spacing:.1em; }
      .dm-finalq { position:absolute; left:120px; right:120px; top:250px; text-align:center;
        font-size:76px; color:#2b2620; line-height:1.4; }
      .dm-cmt { position:absolute; left:0; right:0; bottom:350px; text-align:center;
        font-size:64px; color:#b03120; }
      .dm-bye { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:62px; color:#2b2620; letter-spacing:.08em; }
"""

# ---------- 场景时间轴（占位，随后展开） ----------
SCENE_JS = """
      /* ===== S1 承题·八戒回闪 0–16.76 ===== */
      tl.fromTo('#sc-recap > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},0);
      tl.from('#rc1,#rc2,#rc3',{y:70,opacity:0,duration:.7,ease:'back.out(1.6)',stagger:.55},.6);
      tl.to('#rc2,#rc3',{color:'#b03120',duration:.5,ease:'none'},3.2);
      tl.from('#rp-stamp',{y:24,opacity:0,duration:.6,ease:'power2.out'},4.9);
      tl.from('#rp-q',{y:24,opacity:0,duration:.6,ease:'power2.out'},10.1);
      tl.from('#rp-veg',{scale:.55,opacity:0,duration:.7,ease:'back.out(1.8)'},12.2);
      tl.to('#rp-veg',{scale:1.05,duration:1.1,ease:'sine.inOut',yoyo:true,repeat:-1},13);
      tl.to('#sc-recap > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},16.36);

      /* ===== S2 青菜豆腐·花和尚 16.76–30.48 ===== */
      tl.fromTo('#sc-drama > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},16.76);
      tl.from('#dr-note',{y:24,opacity:0,duration:.6,ease:'power2.out'},16.9);
      tl.from('#dr-frame',{y:50,opacity:0,duration:.7,ease:'back.out(1.5)'},19.7);
      tl.from('#dr-meat',{x:130,y:-90,opacity:0,duration:.6,ease:'power2.in'},23.8);
      tl.to('#dr-meat',{x:0,y:0,duration:.5,ease:'bounce.out'},24.4);
      tl.from('#dr-bad',{scale:.5,rotate:-8,opacity:0,duration:.6,ease:'back.out(2)'},27.5);
      tl.to('#sc-drama > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},30.08);

      /* ===== S3 断言·揭晓 30.48–47.68 ===== */
      tl.fromTo('#sc-claim > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},30.48);
      tl.from('#cl-lead',{y:24,opacity:0,duration:.6,ease:'power2.out'},31.7);
      tl.from('#cl-big',{y:24,opacity:0,duration:.6,ease:'power2.out'},34.9);
      tl.from('#cl-not',{scale:.8,opacity:0,duration:.6,ease:'back.out(1.6)'},37.8);
      tl.from('#cl-yes',{y:30,opacity:0,duration:.6,ease:'power2.out'},41.6);
      tl.from('#cl-namewrap',{y:40,scale:.8,opacity:0,duration:.7,ease:'back.out(1.7)'},44.9);
      tl.to('#cl-name',{textShadow:'0 0 26px rgba(176,49,32,.45)',duration:1.2,ease:'sine.inOut',yoyo:true,repeat:-1},45.8);
      tl.to('#sc-claim > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},47.28);

      /* ===== S4 报名 47.68–52.54 ===== */
      tl.fromTo('#sc-hi > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},47.68);
      tl.from('#hi-main',{y:40,opacity:0,duration:.6,ease:'back.out(1.6)'},47.9);
      tl.from('#hi-sub',{y:24,opacity:0,duration:.6,ease:'power2.out'},50.6);
      tl.to('#sc-hi > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},52.18);

      /* ===== S5 托钵乞食 52.54–64.26 ===== */
      tl.fromTo('#sc-patra > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},52.54);
      tl.from('.pt-house',{opacity:0,duration:.7,ease:'power2.out',stagger:.3},53.2);
      tl.from('#walker',{opacity:0,duration:.5},54.2);
      tl.to('#walker',{x:-680,duration:9.2,ease:'none'},54.4);
      tl.to('#walker',{y:-10,duration:.55,ease:'sine.inOut',yoyo:true,repeat:-1},54.4);
      tl.from('#pt-note',{y:24,opacity:0,duration:.6,ease:'power2.out'},55.8);
      tl.to('#sc-patra > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},63.9);

      /* ===== S6 三净肉 checklist 64.26–75.28 ===== */
      tl.fromTo('#sc-three > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},64.26);
      tl.from('#t3-title',{y:26,opacity:0,duration:.6,ease:'power2.out'},64.5);
      tl.from('#r1',{x:-60,opacity:0,duration:.55,ease:'back.out(1.5)'},67.1);
      tl.to('#b1',{backgroundColor:'#b03120',color:'#fff',duration:.35},67.7);
      tl.from('#r2',{x:-60,opacity:0,duration:.55,ease:'back.out(1.5)'},69.4);
      tl.to('#b2',{backgroundColor:'#b03120',color:'#fff',duration:.35},70);
      tl.from('#r3',{x:-60,opacity:0,duration:.55,ease:'back.out(1.5)'},71.3);
      tl.to('#b3',{backgroundColor:'#b03120',color:'#fff',duration:.35},71.9);
      tl.to('#b1,#b2,#b3',{scale:1.12,duration:.6,ease:'sine.inOut',yoyo:true,repeat:-1,stagger:.2},72.2);
      tl.from('#t3-ok',{scale:.7,opacity:0,duration:.6,ease:'back.out(1.8)'},73.1);
      tl.to('#sc-three > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},74.9);

      /* ===== S7 南传地图 75.28–82.62 ===== */
      tl.fromTo('#sc-south > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},75.28);
      tl.from('#sm-title',{y:24,opacity:0,duration:.6,ease:'power2.out'},75.4);
      tl.from('#sm-map',{scale:.85,opacity:0,duration:.6,ease:'back.out(1.5)'},77.6);
      tl.from('#smd1',{scale:0,duration:.4,ease:'back.out(2)'},79.4);
      tl.from('#smd2',{scale:0,duration:.4,ease:'back.out(2)'},80.2);
      tl.from('#sm-note',{y:24,opacity:0,duration:.6,ease:'power2.out'},81.3);
      tl.to('#smd1,#smd2',{scale:1.35,duration:.8,ease:'sine.inOut',yoyo:true,repeat:-1,stagger:.25},81);
      tl.to('#sc-south > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},82.22);

      /* ===== S8 左右对比·转场 82.62–88.28 ===== */
      tl.fromTo('#sc-turn > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},82.62);
      tl.from('#tn-q',{y:24,opacity:0,duration:.6,ease:'power2.out'},82.8);
      tl.from('#tnb1',{y:40,opacity:0,duration:.6,ease:'back.out(1.5)'},84.5);
      tl.from('#tn-arrow',{opacity:0,x:-20,duration:.5},85.2);
      tl.from('#tnb2',{y:40,opacity:0,duration:.6,ease:'back.out(1.5)'},85.6);
      tl.from('#tn-ptr',{y:24,opacity:0,duration:.6,ease:'power2.out'},86.2);
      tl.to('#tnb2',{y:-14,duration:1,ease:'sine.inOut',yoyo:true,repeat:-1},86.4);
      tl.to('#sc-turn > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},87.9);

      /* ===== S9 萧衍其人 88.28–100.68 ===== */
      tl.fromTo('#sc-xiao > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},88.28);
      tl.from('#xw-name',{y:30,opacity:0,duration:.6,ease:'power2.out'},88.4);
      tl.from('#xc1',{y:40,opacity:0,duration:.55,ease:'back.out(1.6)'},89.3);
      tl.from('#xc2',{y:40,opacity:0,duration:.55,ease:'back.out(1.6)'},90.9);
      tl.from('#xc3',{y:40,opacity:0,duration:.55,ease:'back.out(1.6)'},92.5);
      tl.from('#xw-turn',{y:24,opacity:0,duration:.6,ease:'power2.out'},97.2);
      tl.to('#xc3',{y:-10,duration:.9,ease:'sine.inOut',yoyo:true,repeat:-1},93.4);
      tl.to('#sc-xiao > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},100.3);

      /* ===== S10 四次舍身·数据卡 100.68–117.62 ===== */
      tl.fromTo('#sc-shenshen > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},100.68);
      tl.from('#ss-lead',{y:24,opacity:0,duration:.6,ease:'power2.out'},100.8);
      tl.from('.ss-data',{scale:.5,opacity:0,duration:.7,ease:'back.out(2)'},101.9);
      tl.from('.ss-change',{y:24,opacity:0,duration:.6,ease:'power2.out'},103.4);
      tl.to('#ss-jiasha',{color:'#b03120',duration:.5},104.2);
      tl.from('#ss-ransom',{y:24,opacity:0,duration:.6,ease:'power2.out'},113);
      tl.to('#ss-num',{scale:1.06,duration:1,ease:'sine.inOut',yoyo:true,repeat:-1},103);
      tl.to('#sc-shenshen > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},117.2);

      /* ===== S11 二手平台比喻 117.62–125.10 ===== */
      tl.fromTo('#sc-boss > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},117.62);
      tl.from('#bs-note',{y:24,opacity:0,duration:.6,ease:'power2.out'},117.8);
      tl.from('#bs-card',{y:46,opacity:0,duration:.7,ease:'back.out(1.5)'},119.1);
      tl.from('#bs-tag',{scale:0,duration:.5,ease:'back.out(2)'},120.3);
      tl.from('#bs-who',{y:20,opacity:0,duration:.6,ease:'power2.out'},121);
      tl.from('#bs-ransom',{y:24,opacity:0,duration:.6,ease:'power2.out'},123.2);
      tl.to('#bs-tag',{scale:1.1,duration:.9,ease:'sine.inOut',yoyo:true,repeat:-1},121);
      tl.to('#sc-boss > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},124.7);

      /* ===== S12 断酒肉文·版本升级 125.10–149.46 ===== */
      tl.fromTo('#sc-edict > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},125.1);
      tl.from('#ed-lead',{y:22,opacity:0,duration:.6,ease:'power2.out'},125.3);
      tl.from('#ed-scroll',{scaleY:.1,opacity:0,duration:.7,ease:'back.out(1.5)'},127.4);
      tl.from('#es1',{y:30,opacity:0,duration:.55,ease:'back.out(1.6)'},133.8);
      tl.from('#es2',{y:30,opacity:0,duration:.55,ease:'back.out(1.6)'},134.6);
      tl.from('#ed-debate',{y:24,opacity:0,duration:.6,ease:'power2.out'},138.5);
      tl.from('#ed-version',{y:24,opacity:0,duration:.6,ease:'power2.out'},143.4);
      tl.from('.ed-v2',{scale:.6,opacity:0,duration:.6,ease:'back.out(2)'},145.2);
      tl.to('.ed-v2',{scale:1.07,duration:.9,ease:'sine.inOut',yoyo:true,repeat:-1},146);
      tl.to('#sc-edict > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},149);

      /* ===== S13 终端配置卡·1500 年 149.46–166.68 ===== */
      tl.fromTo('#sc-config > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},149.46);
      tl.from('#cf-term',{y:24,opacity:0,duration:.6,ease:'power2.out'},153.3);
      tl.from('#cf-window',{y:44,opacity:0,duration:.7,ease:'back.out(1.5)'},155.3);
      tl.from('#cf-l1',{opacity:0,duration:.5},156);
      tl.from('#cf-l2',{opacity:0,duration:.5},157.8);
      tl.from('#cf-time',{y:24,opacity:0,duration:.6,ease:'power2.out'},162);
      tl.from('.cf-1500',{scale:.5,opacity:0,duration:.7,ease:'back.out(2)'},165);
      tl.to('.cf-1500',{scale:1.08,duration:1,ease:'sine.inOut',yoyo:true,repeat:-1},165.9);
      tl.to('#sc-config > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},166.3);

      /* ===== S14 转折·台城·结局时间轴 166.68–190.66 ===== */
      tl.fromTo('#sc-fall > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},166.68);
      tl.from('#fl-turn',{y:20,opacity:0,duration:.5,ease:'power2.out'},166.9);
      tl.from('#fp1',{x:-60,opacity:0,duration:.6,ease:'back.out(1.5)'},167.9);
      tl.from('#fp2',{x:60,opacity:0,duration:.6,ease:'back.out(1.5)'},170.7);
      tl.from('#fl-war',{opacity:0,duration:.6},172.6);
      tl.from('#fn1',{y:30,opacity:0,duration:.5,ease:'back.out(1.6)'},179.8);
      tl.from('#fn2',{y:30,opacity:0,duration:.5,ease:'back.out(1.6)'},181.4);
      tl.from('#fn3',{y:30,opacity:0,duration:.5,ease:'back.out(1.6)'},183.2);
      tl.from('#fn4',{y:30,opacity:0,duration:.55,ease:'back.out(1.8)'},184.2);
      tl.from('#fl-end',{scale:.8,opacity:0,duration:.7,ease:'power2.out'},187.9);
      tl.to('#fn4',{scale:1.1,duration:.7,ease:'sine.inOut',yoyo:true,repeat:-1},185);
      tl.to('#sc-fall > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},190.2);

      /* ===== S15 权力之问 190.66–207.08 ===== */
      tl.fromTo('#sc-power > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},190.66);
      tl.from('#pw-q',{y:30,opacity:0,duration:.7,ease:'power2.out'},191.6);
      tl.from('#pwc1',{y:46,opacity:0,duration:.7,ease:'back.out(1.5)'},195.9);
      tl.from('#pwc2',{y:46,opacity:0,duration:.7,ease:'back.out(1.5)'},200.9);
      tl.to('#pwc1',{y:-12,duration:1.1,ease:'sine.inOut',yoyo:true,repeat:-1},197);
      tl.to('#sc-power > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},206.7);

      /* ===== S16 达摩预告·抛问·道别 207.08–TOTAL ===== */
      tl.fromTo('#sc-damo > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},207.08);
      tl.from('#dm-note',{y:22,opacity:0,duration:.6,ease:'power2.out'},207.2);
      tl.from('#dm-boat',{opacity:0,duration:.5},209);
      tl.to('#dm-boat',{x:980,duration:5.2,ease:'power1.inOut'},209.2);
      tl.to('#dm-boat',{opacity:0,duration:.6,ease:'power1.out'},215.6);
      tl.from('#dm-meet',{y:24,opacity:0,duration:.6,ease:'power2.out'},214.1);
      tl.from('#dm-list span',{y:26,opacity:0,duration:.5,ease:'back.out(1.6)',stagger:.22},216);
      tl.from('#dm-ask',{scale:.7,opacity:0,duration:.6,ease:'back.out(1.7)'},222.2);
      tl.from('#dm-cold',{y:24,opacity:0,duration:.6,ease:'power2.out'},224.1);
      tl.from('#dm-go',{y:24,opacity:0,duration:.6,ease:'power2.out'},228.4);
      tl.from('#dm-next',{scale:.6,opacity:0,duration:.7,ease:'back.out(2)'},231.7);
      tl.to('#dm-note,#dm-sea,#dm-meet,#dm-list,#dm-ask,#dm-cold,#dm-go,#dm-next',{opacity:0,duration:.5,ease:'power1.inOut'},235.2);
      tl.from('#dm-finalq',{y:34,opacity:0,duration:.7,ease:'power2.out'},236);
      tl.from('#dm-cmt',{y:24,opacity:0,duration:.6,ease:'power2.out'},241.8);
      tl.from('#dm-bye',{y:24,opacity:0,duration:.6,ease:'power2.out'},243.2);
      tl.to('#sc-damo > .scene-inner',{opacity:0,duration:.35,ease:'power1.in'},245.05);
"""

# ---------- 底部字幕轨道 ----------
frag = char_track(cues, chars, THEME.accent)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/liangwudi-yeyang.wav", TOTAL),
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
