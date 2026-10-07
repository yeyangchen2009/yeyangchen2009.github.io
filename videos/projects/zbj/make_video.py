# -*- coding: utf-8 -*-
"""猪八戒成片生成器（考古工作台主题，225.01s）。

本片独有：15 幕 body、S1…S15 宣纸米·墨字·朱砂批注 CSS、场景时间轴
（含 S7 丝路行者双层 g、S13 四分支 stroke-dashoffset 点亮 merge 成
猪八戒——全片高潮）。页面骨架 / 主题 / 字幕 / clip 外壳全部复用
videopipe。零 blur，渲染走 drawElement streaming 快路径。
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

# ---------- 15 幕 ----------
SCENES = [

# S1 古书·拿掉猪八戒 0.00–5.70（cue0–1）
Scene("sc-hook", 0.00, 5.70, """
          <div class="hk-book">《西游记》</div>
          <div class="hk-name" id="hk-name">猪八戒</div>
          <div class="hk-slot" id="hk-slot"></div>
          <div class="hk-laugh" id="hk-laugh">取经路上，得少掉一半笑声</div>"""),

# S2 毛病＋最亲 5.70–17.60（cue2–7）
Scene("sc-flaw", 5.70, 17.60, """
          <div class="flaw-grid">
            <div class="flaw-card" id="fc1"><span class="fc-k">贪吃</span></div>
            <div class="flaw-card" id="fc2"><span class="fc-k">偷懒</span></div>
            <div class="flaw-card" id="fc3"><span class="fc-k">见着姑娘走不动道</span></div>
            <div class="flaw-card" id="fc4"><span class="fc-k">喊散伙 · 要回高老庄</span></div>
          </div>
          <div class="flaw-turn" id="flaw-turn">可这么一身毛病的角色</div>
          <div class="flaw-dear" id="flaw-dear">偏偏是读者最亲的一个</div>"""),

# S3 断言 17.60–29.20（cue8–12）
Scene("sc-claim", 17.60, 29.20, """
          <div class="cl-lead" id="cl-lead">但今天，先把结论拍在这儿 ——</div>
          <div class="cl-big" id="cl-big"><span class="cl-no">不是</span>吴承恩凭空编出来的</div>
          <div class="cl-from" id="cl-from">在历史和佛经里，真能找到来路</div>
          <div class="cl-more" id="cl-more">而且，不止一条</div>"""),

# S4 报名·代码考古·拆字 29.20–37.40（cue13–17）
Scene("sc-arch", 29.20, 37.40, """
          <div class="ar-hi" id="ar-hi">哈喽大家好，我是叶扬</div>
          <div class="ar-do" id="ar-do">今天，我们来一次代码考古</div>
          <div class="ar-charwrap" id="ar-charwrap">
            <span class="ar-char" id="ac1">猪</span><span class="ar-char" id="ac2">八</span><span class="ar-char" id="ac3">戒</span>
          </div>
          <svg class="ar-main" id="ar-main" viewBox="0 0 1400 80"><line x1="20" y1="40" x2="1380" y2="40" class="ar-line"/><circle cx="700" cy="40" r="13" class="ar-node"/></svg>
          <div class="ar-tip" id="ar-tip">看它，是从哪些分支合并上来的</div>"""),

# S5 八关斋戒 37.40–57.70（cue18–24）
Scene("sc-jie", 37.40, 57.70, """
          <div class="j5-title" id="j5-title">八戒 ＝ <span class="j5-full">八关斋戒</span></div>
          <div class="j5-sub" id="j5-sub">在家信徒 · 特定日子 · 一日一夜受持</div>
          <div class="j5-grid">
            <div class="j5-item" id="ji1">不杀生</div><div class="j5-item" id="ji2">不偷盗</div>
            <div class="j5-item" id="ji3">不淫欲</div><div class="j5-item" id="ji4">不妄语</div>
            <div class="j5-item" id="ji5">不饮酒</div><div class="j5-item" id="ji6">不坐高广大床</div>
            <div class="j5-item" id="ji7">不歌舞打扮</div><div class="j5-item" id="ji8">过午不食</div>
          </div>"""),

# S6 戒字盖章 57.70–68.85（cue25–31）
Scene("sc-seal", 57.70, 68.85, """
          <div class="se-lead" id="se-lead">小说里给二徒弟起这名，是有寓意的</div>
          <div class="se-desire" id="se-desire">一身的欲望</div>
          <div class="seal" id="seal"><span>戒</span></div>
          <div class="se-when" id="se-when">偏给你安一个「戒」字当头</div>
          <div class="se-rev" id="se-rev">名字和人设，从第一天起就是反着来的</div>"""),

# S7 朱士行·丝路 68.85–92.25（cue32–40）
Scene("sc-zhushi", 68.85, 92.25, """
          <div class="zs-tag" id="zs-tag">再说「姓猪」 · 头一个候选人</div>
          <div class="zs-name" id="zs-name">三国时代高僧 · 朱士行</div>
          <div class="zs-first" id="zs-first">中国历史上第一个正式受戒出家的汉族和尚</div>
          <svg id="silk" viewBox="0 0 1920 1080">
            <path id="silk-base" class="silk-base" d="M1400 680 C 1080 540, 720 520, 420 640"/>
            <path id="silk-lit" class="silk-lit" d="M1400 680 C 1080 540, 720 520, 420 640"/>
            <text x="900" y="475" class="silk-dist">西渡流沙一万多里</text>
            <g id="n-luo"><circle cx="1400" cy="680" r="17" class="silk-node"/><text x="1400" y="735" class="silk-tx">洛阳</text></g>
            <g id="n-yu2"><circle cx="420" cy="640" r="17" class="silk-node hot"/><text x="420" y="695" class="silk-tx">于阗</text></g>
            <g transform="translate(1400,680)"><g id="sw-inner"><circle r="12" class="silk-walker"/></g></g>
          </svg>
          <div class="zs-age" id="zs-age">快六十岁出发 · 去于阗求取更完整的佛经原典</div>"""),

# S8 趣称·民间虚线 92.25–115.50（cue41–51）
Scene("sc-folk", 92.25, 115.50, """
          <div class="fk-note" id="fk-note">民间给他安过一个听着特别耳熟的趣称 ——</div>
          <div class="fk-big" id="fk-big">朱八戒</div>
          <div class="fk-qiao" id="fk-qiao">你说巧不巧</div>
          <div class="fk-like" id="fk-like">真正头一个西行取经的和尚，倒像唐僧那个贪吃的二徒弟</div>
          <div class="fk-honest" id="fk-honest">不过这里我得诚实 ——</div>
          <div class="fk-truth" id="fk-truth">正史《高僧传》只称朱士行 · 朱八戒是民间附会，找不到硬档案</div>
          <svg class="fk-linewrap" id="fk-linewrap" viewBox="0 0 1200 120">
            <line id="fk-line" x1="60" y1="60" x2="900" y2="60" class="fk-line"/>
            <text x="930" y="72" class="fk-tag">民间传说分支</text>
          </svg>"""),

# S9 元杂剧·猪妖自报 115.50–131.20（cue52–59）
Scene("sc-zaju", 115.50, 131.20, """
          <div class="zj2-tag" id="zj2-tag">第二条线 · 证据更硬，在元杂剧里</div>
          <svg class="zj2-tl" id="zj2-tl" viewBox="0 0 1400 300">
            <line x1="200" y1="170" x2="1200" y2="170" class="zj2-axis"/>
            <g id="zj-node"><circle cx="320" cy="170" r="20" class="zj2-n"/><text x="320" y="240" class="zj2-nt">元末 · 杨景贤杂剧《西游记》</text></g>
            <text x="660" y="140" class="zj2-gap">早两百年</text>
            <g id="wc-node"><circle cx="1080" cy="170" r="20" class="zj2-n dim"/><text x="1080" y="240" class="zj2-nt dim2">吴承恩《西游记》</text></g>
          </svg>
          <div class="zj2-actor" id="zj2-actor">那里面的猪妖，自报家门 ——</div>
          <div class="zj2-scroll"><div class="zj2-title" id="zj2-title">「摩利支天部下御车将军」</div></div>"""),

# S10 七金猪 131.20–137.75（cue60–63）
Scene("sc-chariot", 131.20, 137.75, """
          <div class="ch-lead" id="ch-lead">摩利支天，密教里的一位菩萨</div>
          <svg id="chariot" viewBox="0 0 1920 1080">
            <defs>
              <g id="pig">
                <path d="M22 24 L15 3 L37 17 Z" class="pig-ear"/>
                <ellipse cx="72" cy="48" rx="50" ry="29" class="pig-body"/>
                <circle cx="28" cy="42" r="23" class="pig-head"/>
                <ellipse cx="10" cy="49" rx="12" ry="9" class="pig-snout"/>
                <circle cx="6" cy="48" r="2" class="pig-nose"/><circle cx="15" cy="48" r="2" class="pig-nose"/>
                <circle cx="32" cy="35" r="3.2" class="pig-eye"/>
                <path d="M118 46 q12 -9 4 -16 q-9 -4 -9 5" class="pig-tail"/>
                <rect x="46" y="70" width="9" height="22" rx="3" class="pig-leg"/><rect x="64" y="70" width="9" height="22" rx="3" class="pig-leg"/>
                <rect x="86" y="70" width="9" height="22" rx="3" class="pig-leg"/><rect x="102" y="70" width="9" height="22" rx="3" class="pig-leg"/>
              </g>
            </defs>
            <g id="stage-all">
              <g id="piggroup">
                <use href="#pig" x="150" y="430"/><use href="#pig" x="290" y="430"/><use href="#pig" x="430" y="430"/>
                <use href="#pig" x="570" y="430"/><use href="#pig" x="710" y="430"/><use href="#pig" x="850" y="430"/>
                <use href="#pig" x="990" y="430"/>
              </g>
              <g id="cargroup">
                <line x1="205" y1="462" x2="1078" y2="462" class="yoke"/>
                <path d="M1078 462 L1230 518 L1258 518" class="shaft"/>
                <rect x="1255" y="430" width="300" height="200" rx="10" class="car-box"/>
                <path d="M1255 430 Q1405 340 1555 430" class="car-roof"/>
                <circle cx="1310" cy="660" r="62" class="wheel" id="wh1"/><circle cx="1500" cy="660" r="62" class="wheel" id="wh2"/>
                <circle cx="1405" cy="500" r="26" class="deva-head"/><path d="M1375 530 Q1405 560 1435 530 L1442 600 L1368 600 Z" class="deva-robe"/>
              </g>
            </g>
          </svg>
          <div class="ch-sub" id="ch-sub">她的座驾，是七头金色猪牵拉的一辆车</div>"""),

# S11 出处·印度原典 137.75–155.70（cue64–72）
Scene("sc-origin", 137.75, 155.70, """
          <div class="og-lead" id="og-lead">杂剧里「御车将军」的头衔，出处就在这儿</div>
          <div class="og-core" id="og-core">替这位菩萨管车、驾车的，本身就是一头猪</div>
          <div class="og-fit" id="og-fit">这个设定，跟印度原典严丝合缝</div>
          <div class="og-trace" id="og-trace">源头能一路追到 —— 印度佛经里的「猪形精怪」</div>"""),

# S12 传播链 155.70–166.60（cue73–77）
Scene("sc-chain", 155.70, 166.60, """
          <div class="cn-lead" id="cn-lead">也就是说 ——</div>
          <svg id="chain" viewBox="0 0 1920 600">
            <g class="cn-node" id="nn1"><circle cx="260" cy="300" r="52" class="cn-c"/><text x="260" y="312" class="cn-t">佛经</text><text x="260" y="400" class="cn-l">印度佛经</text></g>
            <path d="M330 300 L450 300" class="cn-arrow" id="ca1"/>
            <g class="cn-node" id="nn2"><circle cx="520" cy="300" r="52" class="cn-c"/><text x="520" y="312" class="cn-t">民间</text><text x="520" y="400" class="cn-l">传到民间</text></g>
            <path d="M590 300 L710 300" class="cn-arrow" id="ca2"/>
            <g class="cn-node" id="nn3"><circle cx="800" cy="300" r="52" class="cn-c"/><text x="800" y="312" class="cn-t">杂剧</text><text x="800" y="400" class="cn-l">唐僧收徒 · 赐名八戒</text></g>
            <path d="M870 300 L990 300" class="cn-arrow" id="ca3"/>
            <g class="cn-node" id="nn4"><circle cx="1080" cy="300" r="52" class="cn-c"/><text x="1080" y="312" class="cn-t">小说</text><text x="1080" y="400" class="cn-l">吴承恩小说</text></g>
          </svg>"""),

# S13 大型 merge 166.60–195.10（cue78–89）
Scene("sc-merge", 166.60, 195.10, """
          <div class="mg-lead" id="mg-lead">现在回头看吴承恩做的工作，就清楚了</div>
          <div class="mg-not" id="mg-not">他干的，不是从零发明</div>
          <div class="mg-big" id="mg-big">而是一次大型 <span class="mg-merge">merge</span></div>
          <svg id="merge" viewBox="0 0 1920 1080">
            <path class="mg-base" d="M180 300 C 700 300, 1000 470, 1380 470"/>
            <path class="mg-base" d="M180 410 C 700 410, 1000 470, 1380 470"/>
            <path class="mg-base" d="M180 530 C 700 530, 1000 470, 1380 470"/>
            <path class="mg-base" d="M180 650 C 700 650, 1000 470, 1380 470"/>
            <path class="mg-lit blue" id="mb1" d="M180 300 C 700 300, 1000 470, 1380 470"/>
            <path class="mg-lit gold" id="mb2" d="M180 410 C 700 410, 1000 470, 1380 470"/>
            <path class="mg-lit purple" id="mb3" d="M180 530 C 700 530, 1000 470, 1380 470"/>
            <path class="mg-lit folk" id="mb4" d="M180 650 C 700 650, 1000 470, 1380 470"/>
            <text x="180" y="262" class="mg-lab blue">戒律 · 八戒</text>
            <text x="180" y="380" class="mg-lab gold">密教 · 猪将</text>
            <text x="180" y="500" class="mg-lab purple">杂剧 · 桥段</text>
            <text x="180" y="628" class="mg-lab folk">民间 · 朱士行附会</text>
            <line x1="1380" y1="470" x2="1560" y2="470" class="mg-trunk" id="mg-trunk"/>
            <g id="mg-end"><circle cx="1640" cy="470" r="64" class="mg-endc"/><text x="1640" y="486" class="mg-endt">猪八戒</text></g>
          </svg>
          <div class="mg-personality" id="mg-personality">合并完，填入中国人最熟悉的性格 · 小毛病一堆，大节不含糊</div>
          <div class="mg-endline" id="mg-endline">真到了要紧关头，猪八戒从来没真的走过</div>"""),

# S14 接力·开源 195.10–208.60（cue90–96）
Scene("sc-open", 195.10, 208.60, """
          <div class="op-lead" id="op-lead">一个能活几百年的形象，不是某一个天才拍脑袋拍出来的</div>
          <svg id="open-graph" viewBox="0 0 1920 600">
            <line x1="200" y1="320" x2="1380" y2="320" class="op-axis"/>
            <circle class="op-dot" cx="250" cy="320" r="13"/><circle class="op-dot" cx="350" cy="320" r="13"/>
            <circle class="op-dot" cx="450" cy="320" r="13"/><circle class="op-dot" cx="550" cy="320" r="13"/>
            <circle class="op-dot" cx="650" cy="320" r="13"/><circle class="op-dot" cx="750" cy="320" r="13"/>
            <circle class="op-dot" cx="850" cy="320" r="13"/><circle class="op-dot" cx="950" cy="320" r="13"/>
            <circle class="op-dot" cx="1050" cy="320" r="13"/><circle class="op-dot" cx="1150" cy="320" r="13"/>
            <circle class="op-dot" cx="1250" cy="320" r="13"/>
            <circle cx="1430" cy="320" r="40" class="op-merge"/>
          </svg>
          <div class="op-key" id="op-key">是无数人接力提交，最后由一个人合并定型</div>
          <div class="op-end" id="op-end">文化这件事，跟开源项目，是一个道理</div>"""),

# S15 抛问·道别 208.60–225.01（cue97–104）
Scene("sc-end", 208.60, TOTAL, """
          <div class="en-lead" id="en-lead">那么问题来了 · 西游记师徒四人里</div>
          <div class="en-q" id="en-q">孙悟空，也有学者考证说原型来自印度神猴</div>
          <div class="en-ask" id="en-ask">这种「外来原型说」，是把经典说矮了，还是说明它底子更厚？</div>
          <div class="en-cmt" id="en-cmt">评论区聊聊</div>
          <div class="en-bye" id="en-bye">我是叶扬，我们下期见</div>"""),
]

# ---------- 场景专属 CSS（宣纸米·墨字·朱砂批注） ----------
PROJECT_CSS = """

      /* 纸张纹理：极淡的竖纹边框 */
      .scene-inner::before { content:""; position:absolute; inset:26px;
        border:1px solid rgba(120,100,60,.16); pointer-events:none; }

      /* ===== S1 ===== */
      .hk-book { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:56px; color:#5f574c; letter-spacing:.1em; }
      .hk-name { position:absolute; left:0; right:0; top:318px; text-align:center;
        font-size:188px; color:#2b2620; letter-spacing:.18em; text-indent:.18em; }
      .hk-slot { position:absolute; left:0; right:0; top:360px; height:170px;
        text-align:center; }
      .hk-slot::before { content:"猪八戒"; font-size:188px; letter-spacing:.18em; text-indent:.18em;
        color:transparent; -webkit-text-stroke:2px rgba(176,49,32,.55); }
      .hk-laugh { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:58px; color:#b03120; letter-spacing:.06em; }

      /* ===== S2 ===== */
      .flaw-grid { position:absolute; left:230px; right:230px; top:250px;
        display:grid; grid-template-columns:1fr 1fr; gap:34px 40px; }
      .flaw-card { padding:38px 20px; text-align:center; background:#fdfaf2;
        border:2px solid #d8cfb8; border-radius:16px; }
      .fc-k { font-size:54px; color:#2b2620; letter-spacing:.05em; }
      #fc4 .fc-k { font-size:46px; color:#b03120; }
      .flaw-turn { position:absolute; left:0; right:0; top:440px; text-align:center;
        font-size:52px; color:#5f574c; }
      .flaw-dear { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:88px; color:#b03120; letter-spacing:.08em; }

      /* ===== S3 ===== */
      .cl-lead { position:absolute; left:0; right:0; top:230px; text-align:center;
        font-size:52px; color:#2b2620; }
      .cl-big { position:absolute; left:0; right:0; top:360px; text-align:center;
        font-size:104px; color:#2b2620; letter-spacing:.08em; }
      .cl-no { color:#b03120; font-size:120px; margin-right:14px; }
      .cl-from { position:absolute; left:0; right:0; bottom:380px; text-align:center;
        font-size:54px; color:#2b2620; }
      .cl-more { position:absolute; left:0; right:0; bottom:286px; text-align:center;
        font-size:64px; color:#8a6418; letter-spacing:.1em; }

      /* ===== S4 ===== */
      .ar-hi { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:54px; color:#2b2620; }
      .ar-do { position:absolute; left:0; right:0; top:320px; text-align:center;
        font-size:64px; color:#8a6418; }
      .ar-charwrap { position:absolute; left:0; right:0; top:430px; text-align:center; }
      .ar-char { display:inline-block; font-size:120px; color:#2b2620; width:200px; }
      .ar-main { position:absolute; left:260px; right:260px; top:650px; width:auto; height:80px; }
      .ar-line { stroke:#b7a079; stroke-width:5; stroke-linecap:round; }
      .ar-node { fill:#b03120; }
      .ar-tip { position:absolute; left:0; right:0; bottom:230px; text-align:center;
        font-size:48px; color:#5f574c; }

      /* ===== S5 ===== */
      .j5-title { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:92px; color:#2b2620; }
      .j5-full { color:#1d4ed8; }
      .j5-sub { position:absolute; left:0; right:0; top:320px; text-align:center;
        font-size:46px; color:#5f574c; letter-spacing:.08em; }
      .j5-grid { position:absolute; left:300px; right:300px; top:410px;
        display:grid; grid-template-columns:1fr 1fr; gap:22px 60px; }
      .j5-item { padding:14px 10px; text-align:center; font-size:50px; color:#2b2620;
        background:#fdfaf2; border:2px solid #d8cfb8; border-radius:12px; }
      #ji6, #ji7, #ji8 { font-size:44px; }

      /* ===== S6 ===== */
      .se-lead { position:absolute; left:0; right:0; top:230px; text-align:center;
        font-size:48px; color:#5f574c; }
      .se-desire { position:absolute; left:0; right:0; top:330px; text-align:center;
        font-size:72px; color:#2b2620; }
      .seal { position:absolute; left:50%; top:430px; transform:translateX(-50%);
        width:180px; height:180px; line-height:168px; text-align:center;
        border:7px solid #b03120; border-radius:18px; color:#b03120;
        font-size:120px; background:rgba(176,49,32,.05); }
      .se-when { position:absolute; left:0; right:0; bottom:350px; text-align:center;
        font-size:50px; color:#2b2620; }
      .se-rev { position:absolute; left:0; right:0; bottom:270px; text-align:center;
        font-size:54px; color:#b03120; }

      /* ===== S7 ===== */
      .zs-tag { position:absolute; left:0; right:0; top:150px; text-align:center;
        font-size:46px; color:#5f574c; }
      .zs-name { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:96px; color:#2b2620; letter-spacing:.1em; }
      .zs-first { position:absolute; left:180px; right:180px; top:360px; text-align:center;
        font-size:52px; color:#b03120; }
      #silk { position:absolute; inset:0; width:1920px; height:1080px; }
      .silk-base { fill:none; stroke:#ddc9a0; stroke-width:6; stroke-linecap:round; }
      .silk-lit { fill:none; stroke:#8a6418; stroke-width:6; stroke-linecap:round;
        stroke-dasharray:1180; }
      .silk-dist { fill:#8a6418; font-size:44px; text-anchor:middle; }
      .silk-node { fill:#fdfaf2; stroke:#b7a079; stroke-width:3; }
      .silk-node.hot { fill:#f6e6c8; stroke:#b03120; }
      .silk-tx { fill:#2b2620; font-size:40px; text-anchor:middle; }
      .silk-walker { fill:#b03120; }
      .zs-age { position:absolute; left:0; right:0; bottom:210px; text-align:center;
        font-size:46px; color:#5f574c; }

      /* ===== S8 ===== */
      .fk-note { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:48px; color:#5f574c; }
      .fk-big { position:absolute; left:0; right:0; top:330px; text-align:center;
        font-size:180px; color:#b03120; letter-spacing:.2em; text-indent:.2em; }
      .fk-qiao { position:absolute; left:0; right:0; top:590px; text-align:center;
        font-size:46px; color:#8a6418; }
      .fk-like { position:absolute; left:160px; right:160px; top:650px; text-align:center;
        font-size:46px; color:#2b2620; line-height:1.5; }
      .fk-honest { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:50px; color:#8a6418; }
      .fk-truth { position:absolute; left:160px; right:160px; top:380px; text-align:center;
        font-size:46px; color:#2b2620; line-height:1.6; }
      .fk-linewrap { position:absolute; left:300px; right:300px; bottom:250px; width:auto; height:120px; }
      .fk-line { stroke:#b0894f; stroke-width:5; stroke-linecap:round; stroke-dasharray:16 12; }
      .fk-tag { fill:#9a6f3a; font-size:44px; }

      /* ===== S9 ===== */
      .zj2-tag { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:52px; color:#2b2620; }
      .zj2-tl { position:absolute; left:260px; right:260px; top:300px; width:auto; height:260px; }
      .zj2-axis { stroke:#d8cfb8; stroke-width:5; }
      .zj2-n { fill:#fdfaf2; stroke:#8a6418; stroke-width:4; }
      .zj2-n.dim { stroke:#b7a079; }
      .zj2-nt { fill:#2b2620; font-size:40px; text-anchor:middle; }
      .zj2-nt.dim2 { fill:#5f574c; }
      .zj2-gap { fill:#b03120; font-size:44px; text-anchor:middle; }
      .zj2-actor { position:absolute; left:0; right:0; bottom:380px; text-align:center;
        font-size:48px; color:#5f574c; }
      .zj2-scroll { position:absolute; left:120px; right:120px; bottom:270px; text-align:center; }
      .zj2-title { display:inline-block; padding:24px 56px; background:#fdfaf2;
        border:2px solid #d8cfb8; border-radius:12px;
        font-size:64px; color:#b03120; letter-spacing:.06em; }

      /* ===== S10 七金猪 ===== */
      .ch-lead { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:54px; color:#2b2620; }
      #chariot { position:absolute; inset:0; width:1920px; height:1080px; }
      .pig-body { fill:#d9a441; stroke:#8a6418; stroke-width:3; }
      .pig-head { fill:#dda94a; stroke:#8a6418; stroke-width:3; }
      .pig-ear { fill:#c8902e; stroke:#8a6418; stroke-width:2; }
      .pig-snout { fill:#e3b85e; stroke:#8a6418; stroke-width:2; }
      .pig-nose { fill:#6e4e12; }
      .pig-eye { fill:#3d2e08; }
      .pig-tail { fill:none; stroke:#8a6418; stroke-width:4; stroke-linecap:round; }
      .pig-leg { fill:#c8902e; stroke:#8a6418; stroke-width:2; }
      .yoke { stroke:#8a5a2b; stroke-width:5; stroke-linecap:round; }
      .shaft { stroke:#8a5a2b; stroke-width:7; stroke-linecap:round; fill:none; }
      .car-box { fill:#c98a4b; stroke:#8a5a2b; stroke-width:4; }
      .car-roof { fill:#b5743c; stroke:#8a5a2b; stroke-width:4; }
      .wheel { fill:#fdfaf2; stroke:#8a5a2b; stroke-width:7; }
      #wh1 line, #wh2 line { stroke:#b7a079; stroke-width:5; }
      .deva-head { fill:#e6d3b3; stroke:#8a5a2b; stroke-width:3; }
      .deva-robe { fill:#b03120; stroke:#8a5a2b; stroke-width:3; }
      .ch-sub { position:absolute; left:0; right:0; bottom:240px; text-align:center;
        font-size:56px; color:#2b2620; letter-spacing:.05em; }

      /* ===== S11 ===== */
      .og-lead { position:absolute; left:0; right:0; top:230px; text-align:center;
        font-size:50px; color:#2b2620; }
      .og-core { position:absolute; left:140px; right:140px; top:380px; text-align:center;
        font-size:78px; color:#b03120; line-height:1.4; }
      .og-fit { position:absolute; left:0; right:0; bottom:380px; text-align:center;
        font-size:64px; color:#2b2620; }
      .og-trace { position:absolute; left:0; right:0; bottom:272px; text-align:center;
        font-size:58px; color:#1d4ed8; }

      /* ===== S12 ===== */
      .cn-lead { position:absolute; left:0; right:0; top:230px; text-align:center;
        font-size:54px; color:#5f574c; }
      #chain { position:absolute; inset:0; width:1920px; height:600px; top:280px; }
      .cn-c { fill:#fdfaf2; stroke:#8a6418; stroke-width:5; }
      .cn-t { fill:#2b2620; font-size:52px; text-anchor:middle; font-weight:bold; }
      .cn-l { fill:#5f574c; font-size:36px; text-anchor:middle; }
      .cn-arrow { stroke:#b03120; stroke-width:6; fill:none; marker-end:url(#cn-arrowhead); }

      /* ===== S13 merge ===== */
      .mg-lead { position:absolute; left:0; right:0; top:170px; text-align:center;
        font-size:52px; color:#2b2620; }
      .mg-not { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:62px; color:#5f574c; }
      .mg-big { position:absolute; left:0; right:0; top:360px; text-align:center;
        font-size:110px; color:#2b2620; }
      .mg-merge { font-family:"Mono",monospace; color:#1d4ed8; }
      #merge { position:absolute; inset:0; width:1920px; height:1080px; }
      .mg-base { fill:none; stroke:#e0d8c4; stroke-width:7; stroke-linecap:round; }
      .mg-lit { fill:none; stroke-width:7; stroke-linecap:round; stroke-dasharray:1500; }
      .mg-lit.blue { stroke:#1d4ed8; } .mg-lit.gold { stroke:#c89b3c; }
      .mg-lit.purple { stroke:#6d28d9; } .mg-lit.folk { stroke-dasharray:16 12; stroke:#b0894f; }
      .mg-lab { font-size:42px; }
      .mg-lab.blue { fill:#1d4ed8; } .mg-lab.gold { fill:#8a6418; }
      .mg-lab.purple { fill:#6d28d9; } .mg-lab.folk { fill:#9a6f3a; }
      .mg-trunk { stroke:#2f7d5b; stroke-width:8; stroke-linecap:round; }
      .mg-endc { fill:#2f7d5b; }
      .mg-endt { fill:#fff; font-size:44px; text-anchor:middle; font-weight:bold; }
      .mg-personality { position:absolute; left:140px; right:140px; bottom:330px; text-align:center;
        font-size:50px; color:#2b2620; }
      .mg-endline { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:56px; color:#b03120; }

      /* ===== S14 ===== */
      .op-lead { position:absolute; left:140px; right:140px; top:230px; text-align:center;
        font-size:52px; color:#2b2620; }
      #open-graph { position:absolute; inset:0; width:1920px; height:600px; top:300px; }
      .op-axis { stroke:#d8cfb8; stroke-width:6; stroke-linecap:round; }
      .op-dot { fill:#8a6418; }
      .op-merge { fill:#2f7d5b; }
      .op-key { position:absolute; left:0; right:0; bottom:340px; text-align:center;
        font-size:56px; color:#2b2620; }
      .op-end { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:62px; color:#1d4ed8; }

      /* ===== S15 ===== */
      .en-lead { position:absolute; left:0; right:0; top:230px; text-align:center;
        font-size:52px; color:#5f574c; }
      .en-q { position:absolute; left:160px; right:160px; top:330px; text-align:center;
        font-size:64px; color:#2b2620; }
      .en-ask { position:absolute; left:120px; right:120px; top:430px; text-align:center;
        font-size:66px; color:#b03120; line-height:1.5; }
      .en-cmt { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:52px; color:#5f574c; }
      .en-bye { position:absolute; left:0; right:0; bottom:240px; text-align:center;
        font-size:62px; color:#2b2620; letter-spacing:.08em; }"""

# ---------- 场景时间轴（静态，绝对秒） ----------
SCENE_JS = """
      // ===== S1 古书拿掉 =====
      tl.fromTo('#sc-hook > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},0.0);
      tl.to('#sc-hook > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},5.35);
      tl.from('.hk-book',{opacity:0,y:-20,duration:.7},.2);
      tl.from('#hk-name',{opacity:0,scale:.8,duration:.9,ease:'back.out(1.5)'},.7);
      tl.to('#hk-name',{opacity:.12,scale:.82,duration:.55,ease:'power2.in'},2.1);
      tl.from('#hk-slot',{opacity:0,duration:.5},2.2);
      tl.from('#hk-laugh',{opacity:0,y:22,duration:.7,ease:'power2.out'},3.2);

      // ===== S2 毛病最亲 =====
      tl.fromTo('#sc-flaw > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},5.7);
      tl.to('#sc-flaw > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},17.2);
      tl.from('#fc1',{opacity:0,y:26,scale:.85,duration:.5,ease:'back.out(1.7)'},6.0);
      tl.from('#fc2',{opacity:0,y:26,scale:.85,duration:.5,ease:'back.out(1.7)'},6.6);
      tl.from('#fc3',{opacity:0,y:26,scale:.85,duration:.6,ease:'back.out(1.7)'},7.2);
      tl.from('#fc4',{opacity:0,y:26,scale:.85,duration:.7,ease:'back.out(1.7)'},9.6);
      tl.to('.flaw-grid',{autoAlpha:0,duration:.4},13.7);
      tl.from('#flaw-turn',{opacity:0,duration:.6},14.0);
      tl.from('#flaw-dear',{opacity:0,scale:.86,duration:.8,ease:'back.out(1.6)'},15.7);

      // ===== S3 断言 =====
      tl.fromTo('#sc-claim > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},17.6);
      tl.to('#sc-claim > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},28.8);
      tl.from('#cl-lead',{opacity:0,y:20,duration:.7},17.9);
      tl.from('#cl-big',{opacity:0,y:24,duration:.9,ease:'power2.out'},20.6);
      tl.from('.cl-no',{opacity:0,scale:.6,duration:.5,ease:'back.out(2)'},21.8);
      tl.from('#cl-from',{opacity:0,duration:.7},24.9);
      tl.from('#cl-more',{opacity:0,scale:.9,duration:.7,ease:'back.out(1.5)'},26.7);

      // ===== S4 代码考古 =====
      tl.fromTo('#sc-arch > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},29.2);
      tl.to('#sc-arch > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},37.0);
      tl.from('#ar-hi',{opacity:0,y:18,duration:.7},29.3);
      tl.to('#ar-hi',{autoAlpha:0,duration:.35},30.9);
      tl.from('#ar-do',{opacity:0,duration:.7},31.1);
      tl.from('.ar-char',{opacity:0,y:30,scale:.7,duration:.6,ease:'back.out(1.7)',stagger:.14},33.0);
      tl.to('#ac1',{x:-70,duration:.7,ease:'power2.inOut'},33.9);
      tl.to('#ac3',{x:70,duration:.7,ease:'power2.inOut'},33.9);
      tl.from('#ar-main',{opacity:0,scaleX:.2,duration:.9,ease:'power2.inOut',transformOrigin:'left center'},34.6);
      tl.from('#ar-tip',{opacity:0,y:18,duration:.7},35.0);

      // ===== S5 八关斋戒 =====
      tl.fromTo('#sc-jie > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},37.4);
      tl.to('#sc-jie > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},57.3);
      tl.from('#j5-title',{opacity:0,y:-18,duration:.7},39.4);
      tl.from('.j5-full',{opacity:0,duration:.6},43.6);
      tl.from('#j5-sub',{opacity:0,duration:.7},45.2);
      tl.from('.j5-item',{opacity:0,y:22,scale:.9,duration:.5,ease:'back.out(1.5)',stagger:.82},50.2);

      // ===== S6 盖章 =====
      tl.fromTo('#sc-seal > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},57.7);
      tl.to('#sc-seal > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},68.5);
      tl.from('#se-lead',{opacity:0,duration:.7},58.0);
      tl.to('#se-lead',{autoAlpha:0,duration:.35},62.2);
      tl.from('#se-desire',{opacity:0,y:18,duration:.7},62.6);
      tl.from('#seal',{opacity:0,scale:1.8,rotation:-12,duration:.5,ease:'power3.out'},63.7);
      tl.to('#seal',{rotation:0,duration:.3},64.2);
      tl.from('#se-when',{opacity:0,duration:.6},64.6);
      tl.from('#se-rev',{opacity:0,y:18,duration:.8},66.8);

      // ===== S7 朱士行丝路 =====
      tl.fromTo('#sc-zhushi > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},68.85);
      tl.to('#sc-zhushi > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},91.9);
      tl.from('#zs-tag',{opacity:0,y:18,duration:.7},70.7);
      tl.to('#zs-tag',{autoAlpha:0,duration:.3},72.9);
      tl.from('#zs-name',{opacity:0,scale:.9,duration:.8,ease:'back.out(1.5)'},73.6);
      tl.from('#zs-first',{opacity:0,y:20,duration:.8},77.6);
      tl.set('#silk-lit',{strokeDashoffset:1180});
      tl.set('#n-luo,#n-yu2',{opacity:.0});
      tl.set('#sw-inner',{x:0,y:0});
      tl.to('#n-luo',{opacity:1,duration:.3},84.7);
      tl.to('#silk-lit',{strokeDashoffset:0,duration:6.0,ease:'none'},84.7);
      tl.to('#sw-inner',{x:-980,y:-40,duration:6.0,ease:'none'},84.7);
      tl.to('#n-yu2',{opacity:1,duration:.3},90.2);
      tl.from('#zs-age',{opacity:0,duration:.7},91.1);

      // ===== S8 民间虚线 =====
      tl.fromTo('#sc-folk > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},92.25);
      tl.to('#sc-folk > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},115.1);
      tl.from('#fk-note',{opacity:0,duration:.7},92.4);
      tl.from('#fk-big',{opacity:0,scale:.7,duration:.8,ease:'back.out(1.7)'},95.0);
      tl.from('#fk-qiao',{opacity:0,duration:.6},96.5);
      tl.from('#fk-like',{opacity:0,y:18,duration:.9},97.8);
      tl.to('#fk-note,#fk-big,#fk-qiao,#fk-like',{autoAlpha:0,duration:.4},103.2);
      tl.from('#fk-honest',{opacity:0,duration:.6},103.6);
      tl.from('#fk-truth',{opacity:0,y:18,duration:.9},105.8);
      tl.from('#fk-linewrap',{opacity:0,duration:.7},113.0);

      // ===== S9 元杂剧自报 =====
      tl.fromTo('#sc-zaju > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},115.5);
      tl.to('#sc-zaju > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},130.8);
      tl.from('#zj2-tag',{opacity:0,duration:.7},115.7);
      tl.from('#zj-node',{opacity:0,scale:.8,duration:.7,ease:'back.out(1.5)'},118.0);
      tl.from('.zj2-gap',{opacity:0,duration:.6},119.2);
      tl.from('#wc-node',{opacity:0,scale:.8,duration:.7},120.6);
      tl.to('#zj2-tag,#zj2-tl',{autoAlpha:0,duration:.4},123.8);
      tl.from('#zj2-actor',{opacity:0,duration:.7},125.4);
      tl.from('#zj2-title',{opacity:0,y:30,duration:.9,ease:'power2.out'},127.2);

      // ===== S10 七金猪 =====
      tl.fromTo('#sc-chariot > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},131.2);
      tl.to('#sc-chariot > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},137.4);
      tl.from('#ch-lead',{opacity:0,duration:.7},131.4);
      tl.to('#ch-lead',{autoAlpha:0,duration:.35},133.8);
      tl.from('#stage-all',{opacity:0,duration:.8},134.0);
      tl.to('#stage-all',{y:8,duration:.5,ease:'sine.inOut',repeat:-1,yoyo:true},134.4);
      tl.to('#wh1',{rotation:360,svgOrigin:'1310 660',duration:3.2,ease:'none',repeat:-1},134.4);
      tl.to('#wh2',{rotation:360,svgOrigin:'1500 660',duration:3.2,ease:'none',repeat:-1},134.4);
      tl.from('#ch-sub',{opacity:0,y:18,duration:.7},134.9);

      // ===== S11 印度原典 =====
      tl.fromTo('#sc-origin > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},137.75);
      tl.to('#sc-origin > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},155.3);
      tl.from('#og-lead',{opacity:0,duration:.7},137.9);
      tl.from('#og-core',{opacity:0,y:22,duration:.8,ease:'power2.out'},141.4);
      tl.from('#og-fit',{opacity:0,duration:.7},145.5);
      tl.from('#og-trace',{opacity:0,y:20,duration:.9},148.7);

      // ===== S12 传播链 =====
      tl.fromTo('#sc-chain > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},155.7);
      tl.to('#sc-chain > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},166.2);
      tl.from('#cn-lead',{opacity:0,duration:.6},155.9);
      tl.from('#nn1',{opacity:0,scale:.6,duration:.6,ease:'back.out(1.8)'},156.8);
      tl.from('#ca1',{opacity:0,duration:.4},157.6);
      tl.from('#nn2',{opacity:0,scale:.6,duration:.6,ease:'back.out(1.8)'},158.0);
      tl.from('#ca2',{opacity:0,duration:.4},158.9);
      tl.from('#nn3',{opacity:0,scale:.6,duration:.6,ease:'back.out(1.8)'},159.4);
      tl.from('#ca3',{opacity:0,duration:.4},161.0);
      tl.from('#nn4',{opacity:0,scale:.6,duration:.6,ease:'back.out(1.8)'},161.4);

      // ===== S13 merge =====
      tl.fromTo('#sc-merge > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},166.6);
      tl.to('#sc-merge > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},194.7);
      tl.from('#mg-lead',{opacity:0,duration:.7},166.9);
      tl.to('#mg-lead',{autoAlpha:0,duration:.35},169.6);
      tl.from('#mg-not',{opacity:0,y:18,duration:.7},170.8);
      tl.to('#mg-not',{autoAlpha:0,duration:.35},172.4);
      tl.from('#mg-big',{opacity:0,scale:.9,duration:.8,ease:'back.out(1.5)'},172.7);
      tl.to('#mg-big',{autoAlpha:0,duration:.4},174.2);
      tl.set('#mb1,#mb2,#mb3',{strokeDashoffset:1500});
      tl.set('#mb4',{opacity:0});
      tl.set('#mg-trunk',{opacity:0});
      tl.set('#mg-end',{scale:.5,opacity:0,transformOrigin:'1640px 470px'});
      tl.to('#mb1',{strokeDashoffset:0,duration:1.7,ease:'power2.inOut'},174.6);
      tl.to('#mb2',{strokeDashoffset:0,duration:1.7,ease:'power2.inOut'},176.1);
      tl.to('#mb3',{strokeDashoffset:0,duration:1.7,ease:'power2.inOut'},177.7);
      tl.to('#mb4',{opacity:1,duration:1.4,ease:'power1.inOut'},179.4);
      tl.to('#mg-trunk',{opacity:1,duration:.5},182.2);
      tl.to('#mg-end',{scale:1,opacity:1,duration:.7,ease:'back.out(1.8)'},182.6);
      tl.from('#mg-personality',{opacity:0,y:20,duration:.8},185.8);
      tl.from('#mg-endline',{opacity:0,duration:.7},191.6);

      // ===== S14 接力开源 =====
      tl.fromTo('#sc-open > .scene-inner',{opacity:0},{opacity:1,duration:.5,ease:'power1.out'},195.1);
      tl.to('#sc-open > .scene-inner',{opacity:0,duration:.4,ease:'power1.in'},208.2);
      tl.from('#op-lead',{opacity:0,duration:.7},195.4);
      tl.to('#op-lead',{autoAlpha:0,duration:.35},201.0);
      tl.from('.op-dot',{scale:0,opacity:0,duration:.4,ease:'back.out(2)',stagger:.16},201.4);
      tl.from('.op-merge',{scale:0,duration:.6,ease:'back.out(1.8)'},203.6);
      tl.from('#op-key',{opacity:0,y:18,duration:.7},204.0);
      tl.from('#op-end',{opacity:0,duration:.7},205.6);

      // ===== S15 抛问道别 =====
      tl.fromTo('#sc-end > .scene-inner',{opacity:0},{opacity:1,duration:.6,ease:'power1.out'},208.6);
      tl.from('#en-lead',{opacity:0,duration:.7},208.9);
      tl.from('#en-q',{opacity:0,y:18,duration:.8},210.5);
      tl.to('#en-lead,#en-q',{autoAlpha:0,duration:.4},216.9);
      tl.from('#en-ask',{opacity:0,y:22,duration:.9,ease:'power2.out'},217.6);
      tl.to('#en-ask',{autoAlpha:0,duration:.4},221.9);
      tl.from('#en-cmt',{opacity:0,duration:.6},222.2);
      tl.from('#en-bye',{opacity:0,y:16,duration:.7},223.2);
"""

# ---------- 底部字幕轨道 ----------
frag = char_track(cues, chars, THEME.accent)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/zbj-yeyang.wav", TOTAL),
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
