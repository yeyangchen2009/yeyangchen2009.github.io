# -*- coding: utf-8 -*-
"""朱士行（王利杰风格版）成片生成器。

本片独有：17 幕 body、S1…S17 敦煌帛书·暖绢亮色主题 CSS、场景时间轴
（含 S11 丝路地图 stroke-dashoffset 点亮＋行者西行＋得经数据卡）。
页面骨架 / 主题 / 字幕 / clip 外壳全部复用 videopipe。零 blur，渲染走
drawElement streaming 快路径。walker 在老 gen 里已是双层 g 修复版。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       DUNHUANG_WARM)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars, TOTAL = data["cues"], data["chars"], data["duration"]
THEME = DUNHUANG_WARM

# ---------- 17 幕 ----------
SCENES = [

# S1 玄奘钩子 0–13.3（cue0–6）
Scene("sc-hook", 0.0, 13.30, """
        <div class="hook-xuan">玄奘</div>
        <div class="hook-ring r1"></div>
        <div class="hook-ring r2"></div>
        <div class="hook-line" id="hl1">唐僧师徒</div>
        <div class="hook-line" id="hl2">九九八十一难</div>
        <div class="hook-line" id="hl3">电视剧播了几十年</div>
"""),

# S2 翻转 13.1–25.9（cue7–13）
Scene("sc-flip", 13.10, 25.90, """
        <div class="flip-lead">第一个西行求法的中国和尚</div>
        <div class="flip-no" id="flip-no">不是玄奘</div>
        <div class="flip-big"><span class="flip-300">300</span><span class="flip-unit">年</span></div>
        <div class="flip-pre">他比玄奘，早了整整三百多年</div>
        <div class="flip-note">——而且他这一辈子，连印度的边都没摸到</div>
"""),

# S3 报名＋人物 25.7–36.1（cue14–21）
Scene("sc-intro", 25.70, 36.10, """
        <div class="intro-hi">哈喽大家好，我是叶扬</div>
        <div class="intro-name">朱士行<div class="intro-seal">戒</div></div>
        <div class="intro-era">三国 · 魏　颍川人</div>
        <div class="intro-rename">讲他这趟路之前，先给这趟「取经」改个名字</div>
"""),

# S4 重构修 bug 35.9–50.9（cue22–29）
Scene("sc-bug", 35.90, 50.90, """
        <div class="bug-q">你以为他是去——</div>
        <div class="bug-chips">
          <span class="chip-b" id="bc1">求法</span>
          <span class="chip-b" id="bc2">成佛</span>
          <span class="chip-b" id="bc3">攒一份功德</span>
        </div>
        <div class="bug-no" id="bug-no">不是！</div>
        <div class="bug-term" id="bug-term">他这一趟，是去修一个 <span class="bug-mono">BUG</span></div>
        <div class="bug-loc" id="bug-loc">这个 bug，不在他自己这儿 —— 在<span class="bug-up">上游</span></div>
        <div class="bug-next" id="bug-next">先说他是怎么发现这个 bug 的</div>
"""),

# S5 洛阳讲经＋朱八戒趣称 50.7–75.9（cue30–43）
Scene("sc-bajie", 50.70, 75.90, """
        <div class="ly-wrap">
          <div class="ly-place">洛阳 · 出家后</div>
          <div class="ly-book">《道行般若经》</div>
          <div class="ly-insert">讲他怎么卡住之前，先插个有意思的事 ——</div>
        </div>
        <div class="bj-wrap">
          <div class="bj-lead">后世民间，给他安过一个听着特别耳熟的趣称 ——</div>
          <div class="bj-big">朱八戒</div>
          <div class="bj-yes">对，就是《西游记》里猪八戒，那个「八戒」</div>
          <div class="bj-fun">真正头一个西行取经的中国和尚，名字倒像唐僧那个贪吃的二徒弟</div>
          <div class="bj-miao">你说这缘分，妙不妙？</div>
        </div>
"""),

# S6 正史分量·首位受戒 76.2–94.7（cue44–52）
Scene("sc-jie", 76.20, 94.70, """
        <div class="jie-turn">不过，趣称归趣称 ——</div>
        <div class="jie-weight">他在正史里真正的分量，恰恰落在一个<span class="jie-gold">「戒」</span>字上</div>
        <div class="jie-big">中国历史上第一个正式受戒出家的汉族和尚</div>
        <div class="jie-before">
          <div class="jbf" id="jbf1">在那以前：剃个头、披件袈裟</div>
          <div class="jbf" id="jbf2">没有完整的受戒仪式</div>
          <div class="jbf" id="jbf3">算不上真正的比丘</div>
        </div>
"""),

# S7 回正题·讲不下去 94.6–103.9（cue53–58）
Scene("sc-stuck", 94.60, 103.90, """
        <div class="st-back">好了，趣闻聊完，回正题 ——</div>
        <div class="st-q">他到底是怎么卡住的？</div>
        <div class="st-book">《道行般若经》</div>
        <div class="st-stop">讲着讲着……真就讲不下去了</div>
"""),

# S8 残卷硬涩＋打补丁 103.7–122.9（cue59–68）
Scene("sc-rough", 103.70, 122.90, """
        <div class="rg-card">
          <div class="rg-title">早期传抄本</div>
          <div class="rg-lines">
            <span class="ln">识　性　□　游　□</span>
            <span class="ln dim">萨　芸　若　波　罗</span>
            <span class="ln">道　□　行　□　无</span>
            <span class="ln dim">从　法　□　意　□</span>
            <span class="ln">生　□　□　断……</span>
          </div>
        </div>
        <div class="rg-words">
          <div class="rgw" id="rgw1">译人对中文生疏，翻得又硬又涩</div>
          <div class="rgw" id="rgw2">许多地方前后不接、道理不通</div>
          <div class="rgw" id="rgw3">一般人读到这一步，会怎么办？</div>
          <div class="rgw" id="rgw4">要么怪自己悟性不够——硬啃</div>
          <div class="rgw" id="rgw5">要么凑合着用，在下游一处处打补丁</div>
        </div>
"""),

# S9 工程师定位＋源数据 122.66–150.4（cue69–81）
Scene("sc-diag", 122.66, 150.40, """
        <div class="dg-lead">但朱士行做了一件特别工程师的事 ——</div>
        <div class="dg-step">他先判断：问题到底出在哪一层？</div>
        <div class="dg-list">
          <div class="dgl" id="dgl1"><span class="tk-ok">✓</span> 不是他没读懂</div>
          <div class="dgl" id="dgl2"><span class="tk-ok">✓</span> 也不是下游打补丁能补回来的</div>
          <div class="dgl dgl-bad" id="dgl3"><span class="tk-no">✗</span> 是这份「文档」本身就坏了</div>
        </div>
        <div class="dg-why" id="dg-why">要么当年的译者把原典删节过，要么手里只是个残缺抄本</div>
        <div class="dg-rumor" id="dg-rumor">大家都在传：西域应该有一部更完整的全本</div>
        <div class="dg-loc" id="dg-loc">源数据，在源头<span class="dg-notlocal">——不在本地</span></div>
"""),

# S10 260 出发＋年龄 150.2–161.8（cue82–90）
Scene("sc-depart", 150.20, 161.80, """
        <div class="dp-year">公元 260 年</div>
        <div class="dp-dec">他做了个决定：自己去上游，把最原始的那份，亲手取回来</div>
        <div class="dp-agelead">这一年，按后人的推算 ——</div>
        <div class="dp-age">五十七八，快六十了</div>
"""),

# S11 ★丝路地图＋得经 161.6–184.2（cue91–105）
Scene("sc-map", 161.60, 184.20, """
        <div class="map-title" id="map-title">公元 260 年 · 西行路线</div>
        <svg id="map" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid meet">
          <path id="desert" d="M700,520 C600,600 470,640 360,620" fill="none"
                stroke="#c9b48c" stroke-width="2" stroke-dasharray="4 14"/>
          <path class="route-base" d="M1560,520 L1280,470" />
          <path class="route-base" d="M1280,470 L1000,440" />
          <path class="route-base" d="M1000,440 L700,480" />
          <path class="route-base" d="M700,480 C590,560 470,600 360,560" />
          <path class="route-lit" id="seg1" pathLength="100" d="M1560,520 L1280,470" />
          <path class="route-lit" id="seg2" pathLength="100" d="M1280,470 L1000,440" />
          <path class="route-lit" id="seg3" pathLength="100" d="M1000,440 L700,480" />
          <path class="route-lit" id="seg4" pathLength="100" d="M700,480 C590,560 470,600 360,560" />
          <g class="node" id="n-luo"><circle cx="1560" cy="520" r="9"/><text x="1560" y="486">洛阳</text></g>
          <g class="node" id="n-guan"><circle cx="1280" cy="470" r="9"/><text x="1280" y="436">关中</text></g>
          <g class="node" id="n-he"><circle cx="1000" cy="440" r="9"/><text x="1000" y="406">河西</text></g>
          <g class="node" id="n-yang"><circle cx="700" cy="480" r="9"/><text x="700" y="446">阳关</text></g>
          <g class="node" id="n-yu"><circle cx="360" cy="560" r="10"/><text x="360" y="612">于阗</text></g>
          <g transform="translate(1560,520)">
            <g id="walker">
              <circle r="9" fill="#c0392b"/>
              <circle r="17" fill="none" stroke="#a9741d" stroke-opacity=".55" stroke-width="2"/>
            </g>
          </g>
        </svg>
        <div class="map-notes">
          <span class="mn" id="mn1">没有徒弟四人</span>
          <span class="mn" id="mn2">没有白龙马</span>
          <span class="mn" id="mn3">更没有神仙护法</span>
        </div>
        <div class="map-dist" id="map-dist">一万多里 · 每一步都是拿命在赌</div>
        <div class="map-place" id="map-place">于阗 · 就是今天新疆的和田</div>
        <div class="get-wrap" id="get-wrap">
          <div class="get-lead">在那儿，他真找到了想要的东西</div>
          <div class="get-data">
            <div class="gd" id="gd1"><div class="gd-n">大品</div><div class="gd-l">般若经</div></div>
            <div class="gd" id="gd2"><div class="gd-n">九十</div><div class="gd-l">章</div></div>
            <div class="gd" id="gd3"><div class="gd-n">25000</div><div class="gd-l">颂</div></div>
          </div>
        </div>
"""),

# S12 阻拦＋火验 184–201.3（cue106–116）
Scene("sc-fire", 184.00, 201.30, """
        <div class="fr-hard">过程当然不容易</div>
        <div class="fr-block">当地有一派僧人，不愿意经本外传</div>
        <div class="fr-stop">百般阻拦</div>
        <div class="fire-wrap">
          <div class="flame f1"></div>
          <div class="flame f2"></div>
          <div class="flame f3"></div>
          <div class="sutra-book">梵本</div>
        </div>
        <div class="fr-fire">史书里记了一段：把经书投进火里</div>
        <div class="fr-out">火，却自己熄灭了</div>
        <div class="fr-note">灵不灵验我们今天另说 —— 但你能想见当年这趟事有多难</div>
"""),

# S13 老了客死 201.1–223.3（cue117–128）
Scene("sc-death", 201.10, 223.30, """
        <svg class="death-map" viewBox="0 0 1920 1080">
          <path class="droute" d="M1560,520 L1280,470 L1000,440 L700,480 C590,560 470,600 360,560"/>
          <circle class="dn dim" cx="1560" cy="520" r="8"/>
          <circle class="dn dim" cx="1280" cy="470" r="8"/>
          <circle class="dn dim" cx="1000" cy="440" r="8"/>
          <circle class="dn dim" cx="700" cy="480" r="8"/>
          <circle class="dn hot" id="d-yu" cx="360" cy="560" r="11"/>
        </svg>
        <div class="dh-done">可经是取到了，朱士行也老了</div>
        <div class="dh-no">他再也走不回洛阳</div>
        <div class="dh-send">他让弟子护送梵本东归，自己留在于阗</div>
        <div class="dh-age">从快六十岁 → 八十岁</div>
        <div class="dh-die">八十岁，在他乡去世</div>
        <div class="dh-never">他到死，都没能亲眼看见这部经被翻成中文</div>
"""),

# S14 说回开头·不是给自己取 223.1–237.3（cue129–137）
Scene("sc-point", 223.10, 237.30, """
        <div class="pt-back">讲到这儿，得说回开头那句话 ——</div>
        <div class="pt-core">他这一趟，根本不是去给自己取东西的</div>
        <div class="pt-knew">出发前其实就想明白了：这一来回上万里，自己这个年纪，<br/>等不到结果落地的那一天</div>
        <div class="pt-why">那他图什么？</div>
"""),

# S15 放光经·道安流通 237.1–253.6（cue138–145）
Scene("sc-spread", 237.10, 253.60, """
        <div class="spread-center">
          <div class="ripple" id="rp1"></div>
          <div class="ripple" id="rp2"></div>
          <div class="ripple" id="rp3"></div>
          <div class="ripple" id="rp4"></div>
          <div class="spread-dot"></div>
          <div class="spread-name">洛阳</div>
        </div>
        <div class="spread-title">《放光般若经》</div>
        <div class="spread-lines">
          <div class="sl" id="sl1">译本一出 · 立刻风行全国</div>
          <div class="sl" id="sl2">鸠摩罗什来华之前，中国最流通的佛经</div>
          <div class="sl" id="sl3">高僧道安，晚年几乎每年都要讲一遍</div>
        </div>
"""),

# S16 工程师代码隐喻 253.4–269.8（cue146–154）
Scene("sc-code", 253.40, 269.80, """
        <div class="cb-lead">你看，他提交的这份东西 ——</div>
        <div class="terminal" id="terminal">
          <div class="term-bar"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
            <span class="term-file">prajna · commit</span><span class="term-tag">于阗 · 公元约280</span></div>
          <pre class="term-body"><span class="c-com"># 朱士行 提交于 于阗</span>
<span class="c-add">+</span> <span class="c-key">大品般若经</span>　<span class="c-num">九十章</span>　<span class="c-num">25000颂</span>
<span class="c-pun">用的人</span>：<span class="c-str">不是他自己</span>
<span class="c-pun">→</span> <span class="c-str">往后一两百年里，所有的人</span></pre>
        </div>
        <div class="cb-eng">这就像一个工程师，明知道这个功能自己赶不上用 ——</div>
        <div class="cb-do">还是把它干干净净 · 写完 → 提交 → 合并</div>
        <div class="cb-next">留给下一个接手的人</div>
"""),

# S17 种树格言＋抛问·道别 269.6–284.665（cue155–164）
Scene("sc-end", 269.60, TOTAL, """
        <div class="end-tree" id="end-tree">有些人种树，从第一天起，就不是为了自己乘凉</div>
        <div class="end-lead" id="end-lead">所以我想把一个问题留给你 ——</div>
        <div class="end-ask" id="end-ask">
          <div class="ea-q">如果一件事，你明知道自己等不到结果的那一天，</div>
          <div class="ea-q ea-q2">你，还会选择出发吗？</div>
        </div>
        <div class="end-cmt" id="end-cmt">评论区告诉我</div>
        <div class="end-bye" id="end-bye">我是叶扬，我们下期见</div>
"""),
]

# ---------- 场景专属 CSS（敦煌帛书·暖绢亮色） ----------
PROJECT_CSS = """

      /* ===== S1 玄奘钩子 ===== */
      .hook-xuan {
        position:absolute; left:0; right:0; top:278px; text-align:center;
        font-size:150px; color:#4d3a28; letter-spacing:.2em; text-indent:.2em;
      }
      .hook-ring {
        position:absolute; left:50%; top:353px; width:340px; height:340px;
        margin-left:-170px; border:1px solid rgba(192,57,43,.4); border-radius:50%;
      }
      .hook-ring.r2 { width:480px; height:480px; margin-left:-240px;
        border-color:rgba(192,138,46,.3); }
      .hook-line { position:absolute; left:0; right:0; text-align:center;
        font-size:42px; color:#6f5638; letter-spacing:.24em; text-indent:.24em; }
      #hl1 { top:520px; } #hl2 { top:600px; color:#c0392b; }
      #hl3 { top:680px; }

      /* ===== S2 翻转 ===== */
      .flip-lead { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:52px; color:#4d3a28; letter-spacing:.1em; }
      .flip-no { position:absolute; left:0; right:0; top:296px; text-align:center;
        font-size:78px; color:#c0392b; letter-spacing:.14em; text-indent:.14em; }
      .flip-big { position:absolute; left:0; right:0; top:392px; text-align:center; }
      .flip-300 { font-size:172px; color:#a9741d; font-family:"Mono",monospace;
        line-height:1; }
      .flip-unit { font-size:96px; color:#a9741d; margin-left:8px; }
      .flip-pre { position:absolute; left:0; right:0; top:628px; text-align:center;
        font-size:46px; color:#4d3a28; letter-spacing:.08em; }
      .flip-note { position:absolute; left:0; right:0; top:708px; text-align:center;
        font-size:38px; color:#6f5638; letter-spacing:.06em; }

      /* ===== S3 报名＋人物 ===== */
      .intro-hi { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:54px; color:#4d3a28; letter-spacing:.1em; }
      .intro-name { position:absolute; left:0; right:0; top:340px; text-align:center;
        font-size:128px; color:#4d3a28; letter-spacing:.24em; text-indent:.24em; }
      .intro-seal { display:inline-block; width:92px; height:92px; line-height:88px;
        margin-left:26px; vertical-align:middle; border:3px solid #c0392b; border-radius:12px;
        font-size:58px; color:#c0392b; letter-spacing:0; text-indent:0; }
      .intro-era { position:absolute; left:0; right:0; top:560px; text-align:center;
        font-size:42px; color:#6f5638; letter-spacing:.2em; text-indent:.2em; }
      .intro-rename { position:absolute; left:160px; right:160px; bottom:300px; text-align:center;
        font-size:40px; color:#a9741d; }

      /* ===== S4 修 bug ===== */
      .bug-q { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:48px; color:#4d3a28; }
      .bug-chips { position:absolute; left:0; right:0; top:350px; text-align:center; }
      .chip-b { display:inline-block; margin:0 20px; padding:18px 42px;
        background:#fbf5e6; border:2px solid #a9741d; border-radius:12px;
        font-size:46px; color:#a9741d; }
      .bug-no { position:absolute; left:0; right:0; top:320px; text-align:center;
        font-size:120px; color:#c0392b; letter-spacing:.1em; text-indent:.1em; }
      .bug-term { position:absolute; left:0; right:0; top:360px; text-align:center;
        font-size:64px; color:#4d3a28; }
      .bug-mono { font-family:"Mono",monospace; color:#c0392b; font-weight:bold; }
      .bug-loc { position:absolute; left:0; right:0; top:500px; text-align:center;
        font-size:52px; color:#4d3a28; }
      .bug-up { color:#a9741d; font-size:60px; border-bottom:4px solid #a9741d; }
      .bug-next { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:38px; color:#6f5638; }

      /* ===== S5 洛阳＋朱八戒 ===== */
      .ly-place { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:50px; color:#6f5638; letter-spacing:.14em; }
      .ly-book { position:absolute; left:0; right:0; top:350px; text-align:center;
        font-size:104px; color:#4d3a28; letter-spacing:.12em; text-indent:.12em; }
      .ly-insert { position:absolute; left:180px; right:180px; bottom:300px; text-align:center;
        font-size:40px; color:#a9741d; }
      .bj-lead { position:absolute; left:120px; right:120px; top:230px; text-align:center;
        font-size:44px; color:#6f5638; }
      .bj-big { position:absolute; left:0; right:0; top:320px; text-align:center;
        font-size:186px; color:#c0392b; letter-spacing:.16em; text-indent:.16em; }
      .bj-yes { position:absolute; left:0; right:0; top:580px; text-align:center;
        font-size:46px; color:#4d3a28; }
      .bj-fun { position:absolute; left:140px; right:140px; bottom:300px; text-align:center;
        font-size:38px; color:#6f5638; line-height:1.5; }
      .bj-miao { position:absolute; left:0; right:0; bottom:226px; text-align:center;
        font-size:42px; color:#a9741d; }

      /* ===== S6 戒 ===== */
      .jie-turn { position:absolute; left:0; right:0; top:230px; text-align:center;
        font-size:44px; color:#6f5638; }
      .jie-weight { position:absolute; left:120px; right:120px; top:310px; text-align:center;
        font-size:50px; color:#4d3a28; line-height:1.5; }
      .jie-gold { color:#a9741d; font-size:62px; border-bottom:4px solid #a9741d; }
      .jie-big { position:absolute; left:140px; right:140px; top:470px; text-align:center;
        font-size:60px; color:#c0392b; line-height:1.4; }
      .jie-before { position:absolute; left:0; right:0; bottom:290px; text-align:center; }
      .jbf { font-size:40px; color:#4d3a28; line-height:1.7; }
      #jbf3 { color:#6f5638; }

      /* ===== S7 卡住 ===== */
      .st-back { position:absolute; left:0; right:0; top:270px; text-align:center;
        font-size:46px; color:#6f5638; }
      .st-q { position:absolute; left:0; right:0; top:360px; text-align:center;
        font-size:60px; color:#4d3a28; }
      .st-book { position:absolute; left:0; right:0; top:480px; text-align:center;
        font-size:86px; color:#a9741d; letter-spacing:.1em; text-indent:.1em; }
      .st-stop { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:54px; color:#c0392b; }

      /* ===== S8 残卷＋补丁 ===== */
      .rg-card { position:absolute; left:180px; top:230px; width:540px;
        padding:42px 38px; background:#fbf5e6; border:2px solid #d8bd8a; border-radius:14px; }
      .rg-title { text-align:center; font-size:40px; color:#6f5638;
        letter-spacing:.16em; text-indent:.16em; margin-bottom:26px; }
      .rg-lines .ln { display:block; font-size:38px; color:#4d3a28;
        letter-spacing:.3em; line-height:1.5; text-align:center; }
      .rg-lines .ln.dim { color:#a99572; }
      .rg-words { position:absolute; left:800px; top:250px; right:180px; }
      .rgw { font-size:42px; color:#4d3a28; line-height:1.7; }
      #rgw2 { color:#a5513f; } #rgw3 { color:#6f5638; }
      #rgw5 { color:#a9741d; }

      /* ===== S9 定位 ===== */
      .dg-lead { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:46px; color:#4d3a28; }
      .dg-step { position:absolute; left:0; right:0; top:290px; text-align:center;
        font-size:48px; color:#4d3a28; }
      .dg-list { position:absolute; left:420px; top:380px; }
      .dgl { font-size:46px; color:#4d3a28; line-height:1.7; }
      .tk-ok { color:#a9741d; font-weight:bold; }
      .dgl-bad { color:#c0392b; } .tk-no { font-weight:bold; }
      .dg-why { position:absolute; left:200px; right:200px; top:390px; text-align:center;
        font-size:42px; color:#4d3a28; line-height:1.5; }
      .dg-rumor { position:absolute; left:200px; right:200px; top:300px; text-align:center;
        font-size:44px; color:#a9741d; }
      .dg-loc { position:absolute; left:0; right:0; top:420px; text-align:center;
        font-size:108px; color:#c0392b; letter-spacing:.1em; text-indent:.1em; }
      .dg-notlocal { font-size:52px; color:#6f5638; }

      /* ===== S10 出发＋年龄 ===== */
      .dp-year { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:88px; color:#c0392b; letter-spacing:.12em; text-indent:.12em; }
      .dp-dec { position:absolute; left:200px; right:200px; top:420px; text-align:center;
        font-size:48px; color:#4d3a28; line-height:1.5; }
      .dp-agelead { position:absolute; left:0; right:0; bottom:380px; text-align:center;
        font-size:42px; color:#6f5638; }
      .dp-age { position:absolute; left:0; right:0; bottom:290px; text-align:center;
        font-size:92px; color:#a9741d; letter-spacing:.1em; text-indent:.1em; }

      /* ===== S11 地图 ===== */
      #map-title { position:absolute; left:0; right:0; top:96px; text-align:center;
        font-size:46px; color:#4d3a28; letter-spacing:.18em; text-indent:.18em; }
      #map { position:absolute; inset:0; width:1920px; height:1080px; }
      .route-base { fill:none; stroke:#ddc9a0; stroke-width:6; stroke-linecap:round; }
      .route-lit { fill:none; stroke:#a9741d; stroke-width:6; stroke-linecap:round;
        stroke-dasharray:100 100; stroke-dashoffset:100; }
      .node circle { fill:#efe3c6; stroke:#b7a079; stroke-width:2; }
      .node text { fill:#4d3a28; font-size:34px; text-anchor:middle; }
      #n-yu circle { fill:#f6e6c8; stroke:#c0392b; stroke-width:2.5; }
      .map-notes { position:absolute; left:0; right:0; bottom:330px; text-align:center; }
      .mn { display:inline-block; margin:0 22px; font-size:36px; color:#6f5638; }
      .map-dist { position:absolute; left:0; right:0; bottom:262px; text-align:center;
        font-size:40px; color:#a9741d; letter-spacing:.08em; }
      .map-place { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:40px; color:#c0392b; }
      .get-wrap { position:absolute; left:0; right:0; top:300px; text-align:center; }
      .get-lead { font-size:44px; color:#6f5638; margin-bottom:30px; }
      .gd { display:inline-block; width:280px; margin:0 18px; padding:30px 10px;
        background:#fbf5e6; border:2px solid #a9741d; border-radius:14px; }
      .gd-n { font-size:52px; color:#c0392b; font-family:"Mono",monospace; }
      .gd-l { margin-top:8px; font-size:34px; color:#4d3a28; }

      /* ===== S12 火 ===== */
      .fr-hard { position:absolute; left:0; right:0; top:210px; text-align:center;
        font-size:46px; color:#6f5638; }
      .fr-block { position:absolute; left:160px; right:160px; top:270px; text-align:center;
        font-size:46px; color:#4d3a28; line-height:1.5; }
      .fr-stop { position:absolute; left:0; right:0; top:350px; text-align:center;
        font-size:60px; color:#c0392b; letter-spacing:.2em; text-indent:.2em; }
      .fire-wrap { position:absolute; left:50%; top:330px; transform:translateX(-50%);
        width:240px; height:280px; }
      .flame { position:absolute; bottom:26px; left:50%; width:120px; height:190px;
        margin-left:-60px; border-radius:60% 60% 55% 55%; transform-origin:center bottom;
        background:radial-gradient(ellipse at 50% 80%, #ffd166 0%, #ef6c00 55%, rgba(180,40,0,0) 80%);
        opacity:.85; }
      .flame.f2 { width:90px; height:150px; margin-left:-45px; opacity:.7; }
      .flame.f3 { width:64px; height:112px; margin-left:-32px;
        background:radial-gradient(ellipse at 50% 80%, #fff3c4 0%, #ffb703 60%, rgba(255,150,0,0) 85%); }
      .sutra-book { position:absolute; bottom:0; left:50%; transform:translateX(-50%);
        width:120px; height:46px; line-height:46px; text-align:center;
        background:#fbf5e6; border:2px solid #a9741d; border-radius:6px;
        font-size:30px; color:#4d3a28; }
      .fr-fire { position:absolute; left:0; right:0; top:650px; text-align:center;
        font-size:46px; color:#4d3a28; }
      .fr-out { position:absolute; left:0; right:0; top:720px; text-align:center;
        font-size:52px; color:#c0392b; }
      .fr-note { position:absolute; left:160px; right:160px; bottom:290px; text-align:center;
        font-size:36px; color:#6f5638; line-height:1.5; }

      /* ===== S13 客死 ===== */
      .death-map { position:absolute; inset:0; width:1920px; height:1080px; opacity:.55; }
      .droute { fill:none; stroke:#d8bd8a; stroke-width:5; stroke-linecap:round; }
      .dn.dim { fill:#ddc9a0; stroke:#c9b48c; stroke-width:2; }
      .dn.hot { fill:#d98b7e; stroke:#c0392b; stroke-width:2.5; }
      .dh-done { position:absolute; left:0; right:0; top:220px; text-align:center;
        font-size:52px; color:#4d3a28; }
      .dh-no { position:absolute; left:0; right:0; top:310px; text-align:center;
        font-size:56px; color:#c0392b; }
      .dh-send { position:absolute; left:180px; right:180px; top:400px; text-align:center;
        font-size:46px; color:#4d3a28; line-height:1.5; }
      .dh-age { position:absolute; left:0; right:0; top:540px; text-align:center;
        font-size:64px; color:#a9741d; }
      .dh-die { position:absolute; left:0; right:0; top:640px; text-align:center;
        font-size:48px; color:#4d3a28; }
      .dh-never { position:absolute; left:160px; right:160px; bottom:290px; text-align:center;
        font-size:44px; color:#c0392b; line-height:1.5; }

      /* ===== S14 说回开头 ===== */
      .pt-back { position:absolute; left:0; right:0; top:250px; text-align:center;
        font-size:46px; color:#6f5638; }
      .pt-core { position:absolute; left:160px; right:160px; top:340px; text-align:center;
        font-size:58px; color:#4d3a28; line-height:1.5; }
      .pt-knew { position:absolute; left:200px; right:200px; top:480px; text-align:center;
        font-size:42px; color:#6f5638; line-height:1.7; }
      .pt-why { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:96px; color:#c0392b; letter-spacing:.1em; text-indent:.1em; }

      /* ===== S15 放光流通 ===== */
      .spread-center { position:absolute; left:50%; top:360px; transform:translate(-50%,-50%);
        width:20px; height:20px; }
      .ripple { position:absolute; left:50%; top:50%; width:300px; height:300px;
        margin:-150px 0 0 -150px; border:2px solid rgba(192,138,46,.65); border-radius:50%; }
      .spread-dot { position:absolute; left:50%; top:50%; width:22px; height:22px;
        margin:-11px 0 0 -11px; background:#c0392b; border-radius:50%; }
      .spread-name { position:absolute; left:50%; top:50%; margin:26px 0 0 -40px;
        width:80px; text-align:center; font-size:32px; color:#4d3a28; }
      .spread-title { position:absolute; left:0; right:0; top:160px; text-align:center;
        font-size:76px; color:#a9741d; letter-spacing:.16em; text-indent:.16em; }
      .spread-lines { position:absolute; left:0; right:0; bottom:300px; text-align:center; }
      .spread-lines .sl { font-size:40px; color:#4d3a28; line-height:1.8; }

      /* ===== S16 代码隐喻（暗墨砚板，亮底上唯一深色块，刻意为之） ===== */
      .cb-lead { position:absolute; left:0; right:0; top:180px; text-align:center;
        font-size:44px; color:#6f5638; }
      .terminal { position:absolute; left:50%; top:250px; transform:translateX(-50%);
        width:1180px; background:#35271a; border:2px solid #4d3a28; border-radius:12px;
        overflow:hidden; }
      .term-bar { padding:16px 22px; background:#43342a; border-bottom:1px solid #5a4632; }
      .dot { display:inline-block; width:14px; height:14px; border-radius:50%; margin-right:8px; }
      .dot.red{background:#e0715f;} .dot.yellow{background:#e0b44a;} .dot.green{background:#8fae6b;}
      .term-file { margin-left:18px; color:#e6dcc6; font-size:28px; font-family:"Mono",monospace; }
      .term-tag { float:right; color:#a8947a; font-size:24px; font-family:"Mono",monospace; }
      .term-body { padding:30px 34px 34px; font-family:"Mono",monospace; font-size:33px;
        line-height:1.75; color:#efe6d2; }
      .c-com { color:#9a8668; } .c-add { color:#e0715f; }
      .c-key { color:#e0b44a; } .c-num { color:#e6dcc6; }
      .c-pun { color:#b8a486; } .c-str { color:#efe6d2; }
      .cb-eng { position:absolute; left:160px; right:160px; bottom:360px; text-align:center;
        font-size:42px; color:#4d3a28; }
      .cb-do { position:absolute; left:0; right:0; bottom:300px; text-align:center;
        font-size:44px; color:#c0392b; }
      .cb-next { position:absolute; left:0; right:0; bottom:232px; text-align:center;
        font-size:38px; color:#a9741d; }

      /* ===== S17 结尾 ===== */
      #end-tree { position:absolute; left:200px; right:200px; top:300px; text-align:center;
        font-size:64px; color:#a9741d; line-height:1.5; }
      #end-lead { position:absolute; left:0; right:0; top:300px; text-align:center;
        font-size:44px; color:#6f5638; }
      .end-ask { position:absolute; left:0; right:0; top:360px; text-align:center; }
      .ea-q { font-size:54px; color:#4d3a28; line-height:1.6; }
      .ea-q2 { color:#c0392b; font-size:72px; margin-top:24px; }
      #end-cmt { position:absolute; left:0; right:0; bottom:330px; text-align:center;
        font-size:42px; color:#6f5638; }
      #end-bye { position:absolute; left:0; right:0; bottom:250px; text-align:center;
        font-size:50px; color:#4d3a28; letter-spacing:.1em; }"""

# ---------- 场景时间轴（静态，绝对秒） ----------
SCENE_JS = """
      // ===== S1 玄奘钩子 =====
      tl.fromTo('#sc-hook > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 0.0);
      tl.to('#sc-hook > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 12.9);
      tl.from('.hook-xuan', {opacity:0, scale:.92, duration:1.2, ease:'power2.out'}, .3);
      tl.from('.hook-ring', {scale:.6, opacity:0, duration:3.0, ease:'power2.out', repeat:1, yoyo:true}, .8);
      tl.from('#hl1', {opacity:0, y:20, duration:.7, ease:'power2.out'}, 4.9);
      tl.from('#hl2', {opacity:0, y:20, duration:.7, ease:'power2.out'}, 6.2);
      tl.from('#hl3', {opacity:0, y:20, duration:.8, ease:'power2.out'}, 7.6);

      // ===== S2 翻转 =====
      tl.fromTo('#sc-flip > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 13.1);
      tl.to('#sc-flip > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 25.5);
      tl.from('.flip-lead', {opacity:0, y:26, duration:.8, ease:'power2.out'}, 13.6);
      tl.from('#flip-no', {opacity:0, scale:.8, duration:.6, ease:'back.out(1.8)'}, 18.7);
      tl.from('.flip-big', {opacity:0, scale:.7, duration:.9, ease:'back.out(1.6)'}, 19.9);
      tl.from('.flip-pre', {opacity:0, y:18, duration:.7, ease:'power2.out'}, 20.9);
      tl.from('.flip-note', {opacity:0, y:16, duration:.7, ease:'power2.out'}, 22.5);

      // ===== S3 报名＋人物 =====
      tl.fromTo('#sc-intro > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 25.7);
      tl.to('#sc-intro > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 35.7);
      tl.from('.intro-hi', {opacity:0, y:22, duration:.8, ease:'power2.out'}, 26.2);
      tl.to('.intro-hi', {autoAlpha:0, duration:.4}, 28.6);
      tl.from('.intro-name', {opacity:0, scale:.85, duration:.9, ease:'back.out(1.5)'}, 29.9);
      tl.from('.intro-era', {opacity:0, y:16, duration:.6, ease:'power2.out'}, 30.9);
      tl.from('.intro-rename', {opacity:0, y:18, duration:.8, ease:'power2.out'}, 32.2);

      // ===== S4 修 bug =====
      tl.fromTo('#sc-bug > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 35.9);
      tl.to('#sc-bug > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 50.5);
      tl.from('.bug-q', {opacity:0, duration:.7}, 36.3);
      tl.from('#bc1', {opacity:0, y:24, duration:.5, ease:'back.out(1.6)'}, 37.0);
      tl.from('#bc2', {opacity:0, y:24, duration:.5, ease:'back.out(1.6)'}, 37.9);
      tl.from('#bc3', {opacity:0, y:24, duration:.6, ease:'back.out(1.6)'}, 38.9);
      tl.to('.bug-chips', {autoAlpha:0, duration:.35}, 40.7);
      tl.to('.bug-q', {autoAlpha:0, duration:.35}, 40.7);
      tl.from('#bug-no', {opacity:0, scale:.6, duration:.5, ease:'back.out(2)'}, 41.2);
      tl.to('#bug-no', {autoAlpha:0, duration:.3}, 42.2);
      tl.from('#bug-term', {opacity:0, y:24, duration:.7, ease:'power2.out'}, 42.9);
      tl.from('#bug-loc', {opacity:0, duration:.7}, 46.3);
      tl.from('#bug-next', {opacity:0, y:16, duration:.6}, 48.5);

      // ===== S5 洛阳＋朱八戒 =====
      tl.fromTo('#sc-bajie > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 50.7);
      tl.to('#sc-bajie > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 75.5);
      tl.from('.ly-place', {opacity:0, y:18, duration:.6}, 51.0);
      tl.from('.ly-book', {opacity:0, scale:.9, duration:.7, ease:'back.out(1.5)'}, 53.9);
      tl.from('.ly-insert', {opacity:0, duration:.7}, 55.6);
      tl.to('.ly-wrap', {autoAlpha:0, duration:.45}, 58.0);
      tl.from('.bj-lead', {opacity:0, duration:.7}, 58.8);
      tl.from('.bj-big', {opacity:0, scale:.7, duration:.9, ease:'back.out(1.7)'}, 60.3);
      tl.from('.bj-yes', {opacity:0, y:18, duration:.7}, 64.3);
      tl.from('.bj-fun', {opacity:0, duration:.8}, 69.4);
      tl.from('.bj-miao', {opacity:0, scale:.9, duration:.6, ease:'back.out(1.5)'}, 73.3);

      // ===== S6 戒 =====
      tl.fromTo('#sc-jie > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 76.2);
      tl.to('#sc-jie > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 94.3);
      tl.from('.jie-turn', {opacity:0, duration:.6}, 76.5);
      tl.to('.jie-turn', {autoAlpha:0, duration:.35}, 78.6);
      tl.from('.jie-weight', {opacity:0, y:20, duration:.8, ease:'power2.out'}, 78.0);
      tl.from('.jie-big', {opacity:0, scale:.92, duration:.9, ease:'back.out(1.4)'}, 80.3);
      tl.from('#jbf1', {opacity:0, y:16, duration:.6}, 87.3);
      tl.from('#jbf2', {opacity:0, y:16, duration:.6}, 91.1);
      tl.from('#jbf3', {opacity:0, y:16, duration:.6, ease:'power2.out'}, 93.0);

      // ===== S7 卡住 =====
      tl.fromTo('#sc-stuck > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 94.6);
      tl.to('#sc-stuck > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 103.5);
      tl.from('.st-back', {opacity:0, duration:.6}, 95.0);
      tl.to('.st-back', {autoAlpha:0, duration:.35}, 96.6);
      tl.from('.st-q', {opacity:0, y:20, duration:.7, ease:'power2.out'}, 96.9);
      tl.from('.st-book', {opacity:0, scale:.9, duration:.7, ease:'back.out(1.5)'}, 99.0);
      tl.to('.st-book', {autoAlpha:0, scale:.92, duration:.4}, 101.2);
      tl.from('.st-stop', {opacity:0, y:20, duration:.7, ease:'power2.out'}, 101.6);

      // ===== S8 残卷＋补丁 =====
      tl.fromTo('#sc-rough > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 103.7);
      tl.to('#sc-rough > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 122.5);
      tl.from('.rg-card', {opacity:0, x:-40, duration:.9, ease:'power2.out'}, 104.1);
      tl.from('#rgw1', {opacity:0, y:16, duration:.6}, 107.0);
      tl.to('#rgw1', {autoAlpha:0, duration:.35}, 109.6);
      tl.from('#rgw2', {opacity:0, y:16, duration:.6}, 111.4);
      tl.to('#rgw2', {autoAlpha:0, duration:.35}, 113.6);
      tl.from('#rgw3', {opacity:0, y:16, duration:.6}, 114.2);
      tl.to('#rgw3', {autoAlpha:0, duration:.35}, 116.2);
      tl.from('#rgw4', {opacity:0, y:16, duration:.6}, 116.6);
      tl.to('#rgw4', {autoAlpha:0, duration:.35}, 119.2);
      tl.from('#rgw5', {opacity:0, y:16, duration:.7}, 119.6);

      // ===== S9 定位 =====
      tl.fromTo('#sc-diag > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 122.66);
      tl.to('#sc-diag > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 150.0);
      tl.from('.dg-lead', {opacity:0, duration:.7}, 123.1);
      tl.to('.dg-lead', {autoAlpha:0, duration:.35}, 126.2);
      tl.from('.dg-step', {opacity:0, y:18, duration:.7}, 127.0);
      tl.from('#dgl1', {opacity:0, x:-24, duration:.5}, 128.8);
      tl.from('#dgl2', {opacity:0, x:-24, duration:.5}, 130.2);
      tl.from('#dgl3', {opacity:0, x:-24, duration:.6, ease:'power2.out'}, 132.4);
      tl.to('.dg-step,.dg-list', {autoAlpha:0, duration:.4}, 134.4);
      tl.from('#dg-why', {opacity:0, y:18, duration:.8}, 134.8);
      tl.to('#dg-why', {autoAlpha:0, duration:.35}, 140.6);
      tl.from('#dg-rumor', {opacity:0, duration:.8}, 141.3);
      tl.to('#dg-rumor', {autoAlpha:0, duration:.35}, 145.6);
      tl.from('#dg-loc', {opacity:0, scale:.9, duration:.9, ease:'back.out(1.5)'}, 146.3);
      tl.from('.dg-notlocal', {opacity:0, duration:.5}, 149.3);

      // ===== S10 出发＋年龄 =====
      tl.fromTo('#sc-depart > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 150.2);
      tl.to('#sc-depart > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 161.4);
      tl.from('.dp-year', {opacity:0, y:-18, duration:.7}, 150.5);
      tl.from('.dp-dec', {opacity:0, y:22, duration:.9, ease:'power2.out'}, 151.9);
      tl.to('.dp-dec', {autoAlpha:0, duration:.35}, 156.4);
      tl.from('.dp-agelead', {opacity:0, duration:.7}, 157.0);
      tl.from('.dp-age', {opacity:0, scale:.85, duration:.9, ease:'back.out(1.6)'}, 159.2);

      // ===== S11 丝路地图＋得经 =====
      tl.fromTo('#sc-map > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 161.6);
      tl.to('#sc-map > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 183.8);
      tl.from('#map-title', {opacity:0, y:-18, duration:.7}, 161.9);
      tl.set('#seg1,#seg2,#seg3,#seg4', {strokeDashoffset:100});
      tl.set('#walker', {x:0, y:0});
      tl.set('.node', {opacity:.35});
      // 洛阳 162.0
      tl.to('#n-luo', {opacity:1, duration:.3}, 162.0);
      tl.to('#seg1', {strokeDashoffset:0, duration:1.2, ease:'power1.inOut'}, 162.0);
      tl.to('#walker', {x:-280, y:-50, duration:1.2, ease:'power1.inOut'}, 162.0);
      // 关中 163.2
      tl.to('#n-guan', {opacity:1, duration:.25}, 163.2);
      tl.to('#seg2', {strokeDashoffset:0, duration:.8, ease:'power1.inOut'}, 163.2);
      tl.to('#walker', {x:-560, y:-80, duration:.8, ease:'power1.inOut'}, 163.2);
      // 河西 164.0
      tl.to('#n-he', {opacity:1, duration:.25}, 164.0);
      tl.to('#seg3', {strokeDashoffset:0, duration:.8, ease:'power1.inOut'}, 164.0);
      tl.to('#walker', {x:-860, y:-40, duration:.8, ease:'power1.inOut'}, 164.0);
      // 阳关 164.9
      tl.to('#n-yang', {opacity:1, duration:.25}, 164.9);
      // 大漠 165.0 → 173.9
      tl.to('#seg4', {strokeDashoffset:0, duration:8.9, ease:'none'}, 165.0);
      tl.to('#walker', {x:-1200, y:40, duration:8.9, ease:'none'}, 165.0);
      // 于阗 173.9
      tl.fromTo('#n-yu', {scale:.8}, {scale:1.3, duration:.5, yoyo:true, repeat:1}, 173.9);
      tl.to('#n-yu', {opacity:1, duration:.3}, 173.9);
      // 旁注
      tl.from('#mn1', {opacity:0, y:12, duration:.5}, 168.6);
      tl.from('#mn2', {opacity:0, y:12, duration:.5}, 170.0);
      tl.from('#mn3', {opacity:0, y:12, duration:.5}, 171.2);
      tl.from('#map-dist', {opacity:0, duration:.6}, 172.7);
      tl.to('.map-notes', {autoAlpha:0, duration:.35}, 173.5);
      tl.from('#map-place', {opacity:0, duration:.6}, 174.2);
      // 退地图，进数据卡
      tl.to('#map-title,.map-notes,.map-dist,.map-place', {autoAlpha:0, duration:.4}, 177.9);
      tl.to('#map', {opacity:.16, duration:.5}, 177.9);
      tl.from('#get-wrap', {opacity:0, duration:.5}, 178.4);
      tl.from('.get-lead', {opacity:0, duration:.6}, 178.8);
      tl.from('#gd1', {opacity:0, y:26, scale:.85, duration:.6, ease:'back.out(1.5)'}, 180.7);
      tl.from('#gd2', {opacity:0, y:26, scale:.85, duration:.5, ease:'back.out(1.5)'}, 181.9);
      tl.from('#gd3', {opacity:0, y:26, scale:.85, duration:.5, ease:'back.out(1.5)'}, 182.9);

      // ===== S12 阻拦火验 =====
      tl.fromTo('#sc-fire > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 184.0);
      tl.to('#sc-fire > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 200.9);
      tl.from('.fr-hard', {opacity:0, duration:.6}, 184.3);
      tl.to('.fr-hard', {autoAlpha:0, duration:.35}, 185.6);
      tl.from('.fr-block', {opacity:0, duration:.7}, 185.9);
      tl.to('.fr-block', {autoAlpha:0, duration:.35}, 188.4);
      tl.from('.fr-stop', {opacity:0, scale:.9, duration:.5, ease:'back.out(1.6)'}, 189.0);
      tl.to('.fr-stop', {autoAlpha:0, duration:.35}, 190.8);
      tl.from('.fire-wrap', {opacity:0, duration:.7}, 191.0);
      tl.fromTo('.flame', {scaleY:.8, scaleX:.9, opacity:.75}, {scaleY:1.12, scaleX:1.05, opacity:1, duration:.55, ease:'sine.inOut', repeat:-1, yoyo:true}, 191.2);
      tl.from('.fr-fire', {opacity:0, duration:.7}, 191.7);
      tl.from('.fr-out', {opacity:0, y:16, duration:.6}, 193.9);
      tl.to('.fr-fire,.fr-out', {autoAlpha:0, duration:.35}, 195.6);
      tl.from('.fr-note', {opacity:0, duration:.8}, 196.6);

      // ===== S13 客死 =====
      tl.fromTo('#sc-death > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 201.1);
      tl.to('#sc-death > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 222.9);
      tl.from('.death-map', {opacity:0, duration:1.0}, 201.4);
      tl.to('#d-yu', {attr:{r:16}, duration:.8, yoyo:true, repeat:3}, 201.6);
      tl.from('.dh-done', {opacity:0, y:20, duration:.8}, 201.6);
      tl.to('.dh-done', {autoAlpha:0, duration:.35}, 203.8);
      tl.from('.dh-no', {opacity:0, duration:.7}, 204.3);
      tl.to('.dh-no', {autoAlpha:0, duration:.35}, 205.4);
      tl.from('.dh-send', {opacity:0, duration:.8}, 205.9);
      tl.to('.dh-send', {autoAlpha:0, duration:.35}, 211.6);
      tl.from('.dh-age', {opacity:0, y:18, duration:.7}, 212.3);
      tl.from('.dh-die', {opacity:0, duration:.6}, 215.5);
      tl.to('.dh-age,.dh-die', {autoAlpha:0, duration:.35}, 217.2);
      tl.from('.dh-never', {opacity:0, y:18, duration:.8}, 217.8);

      // ===== S14 说回开头 =====
      tl.fromTo('#sc-point > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 223.1);
      tl.to('#sc-point > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 236.9);
      tl.from('.pt-back', {opacity:0, duration:.6}, 223.5);
      tl.to('.pt-back', {autoAlpha:0, duration:.35}, 226.2);
      tl.from('.pt-core', {opacity:0, y:20, duration:.8, ease:'power2.out'}, 226.8);
      tl.to('.pt-core', {autoAlpha:0, duration:.35}, 228.8);
      tl.from('.pt-knew', {opacity:0, duration:.9}, 229.1);
      tl.to('.pt-knew', {autoAlpha:0, duration:.35}, 235.4);
      tl.from('.pt-why', {opacity:0, scale:.9, duration:.7, ease:'back.out(1.6)'}, 236.2);

      // ===== S15 放光流通 =====
      tl.fromTo('#sc-spread > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 237.1);
      tl.to('#sc-spread > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 253.2);
      tl.fromTo('#rp1', {scale:.1, opacity:.6}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 237.4);
      tl.fromTo('#rp2', {scale:.1, opacity:.55}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 238.5);
      tl.fromTo('#rp3', {scale:.1, opacity:.5}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 239.6);
      tl.fromTo('#rp4', {scale:.1, opacity:.45}, {scale:2.4, opacity:0, duration:3.4, ease:'power2.out'}, 240.7);
      tl.from('.spread-dot', {scale:0, duration:.6, ease:'back.out(2)'}, 237.4);
      tl.from('.spread-name', {opacity:0, duration:.6}, 238.0);
      tl.from('.spread-title', {opacity:0, y:-16, duration:.8}, 239.4);
      tl.from('#sl1', {opacity:0, y:16, duration:.6}, 243.2);
      tl.from('#sl2', {opacity:0, y:16, duration:.6}, 245.6);
      tl.from('#sl3', {opacity:0, y:16, duration:.6}, 249.8);

      // ===== S16 代码隐喻 =====
      tl.fromTo('#sc-code > .scene-inner', {opacity:0}, {opacity:1,duration:.5,ease:'power1.out'}, 253.4);
      tl.to('#sc-code > .scene-inner', {opacity:0,duration:.4,ease:'power1.in'}, 269.4);
      tl.from('.cb-lead', {opacity:0, duration:.6}, 253.8);
      tl.to('.cb-lead', {autoAlpha:0, duration:.35}, 255.2);
      tl.from('#terminal', {opacity:0, y:34, scale:.96, duration:.8, ease:'power2.out'}, 254.6);
      tl.from('.cb-eng', {opacity:0, duration:.7}, 260.6);
      tl.to('.cb-eng', {autoAlpha:0, duration:.35}, 264.0);
      tl.from('.cb-do', {opacity:0, y:18, duration:.7}, 264.6);
      tl.from('.cb-next', {opacity:0, duration:.6}, 268.0);

      // ===== S17 结尾 =====
      tl.fromTo('#sc-end > .scene-inner', {opacity:0}, {opacity:1,duration:.6,ease:'power1.out'}, 269.6);
      tl.from('#end-tree', {opacity:0, y:26, duration:1.0, ease:'power2.out'}, 270.1);
      tl.to('#end-tree', {autoAlpha:0, y:-22, duration:.5, ease:'power1.in'}, 274.4);
      tl.from('#end-lead', {opacity:0, duration:.7}, 275.1);
      tl.to('#end-lead', {autoAlpha:0, duration:.35}, 276.2);
      tl.from('.ea-q', {opacity:0, y:20, duration:.8}, 276.5);
      tl.from('.ea-q2', {opacity:0, y:20, duration:.9}, 279.9);
      tl.from('#end-cmt', {opacity:0, duration:.5}, 281.4);
      tl.from('#end-bye', {opacity:0, y:16, duration:.7}, 282.7);
"""

# ---------- 底部字幕轨道 ----------
frag = char_track(cues, chars, THEME.accent)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/zhushixing-wang-yeyang-v2.wav", TOTAL),
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
