# -*- coding: utf-8 -*-
"""慧能成片生成器（宣纸主题 XUANZHI，445.41s，31 幕）。

承接达摩视觉。本片独有：31 幕 body 与场景时间轴，围绕「两首偈」——
承上小团体（S1）→黄梅弘忍考题（S2/S3）→神秀众望（S4）→半夜题墙（S5）
→全寺念偈（S6）→碓房苦力「还没到家」（S7）→慧能亮相报名（S8/S9）
→出身闻经（S10）→南蛮佛性（S11）→踏碓八月（S12）→神秀偈（S13）
→公道话渐修（S14）→「擦」的两层问题（S15/S16）→慧能偈（S17）
→掀根重构（S18）→debug 类比（S19）→鞋擦偈保慧能（S20）→三夜讲经悟道
（S21）→衣钵不再传（S22）→大庾岭惠明（S23）→猎人队肉边菜（S24）
→风幡仁者心动·剃度曹溪（S25）→南顿北渐（S26）→神会争正统·坛经（S27）
→两个极端（S28/S29）→自我追问（S30）→预告佛图澄道安＋道别（S31）。

字幕不再用 word_lead 靠耳朵猜：silencedetect 实测全片 onset 中位数 +290ms
（whisper 吞句间停顿、时间戳整体偏早），用 char_track(time_offset=.29)。
页面骨架／主题／clip 外壳全部复用 videopipe。
"""
import io
import sys
from pathlib import Path

# projects/<name>/make_video.py -> videos/ 在 parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       char_track, assemble_css, render_page, audio_tag,
                       stage_gsap, XUANZHI)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()
stage_gsap(P)

data = load_cues(P.cues_json)
cues, chars, total = data["cues"], data["chars"], data["duration"]
THEME = XUANZHI
RED, GOLD, INK, MUTE = "#b03120", "#8a6418", "#2b2620", "#5f574c"

# ---------- 31 幕（边界严格首尾相接，交叉淡变） ----------
SCENES = [

# S1 承上 0.00–10.08（cue0–4）
Scene("sc-recap", 0.00, 10.08, """
          <div class="L t1 fs-lead" id="rp1">上一集，我们讲到 ——</div>
          <div class="L t3 fs-huge" id="rp2">达摩 · 慧可</div>
          <div class="L b1 fs-note" id="rp3">雪地里站到天亮，衣钵传了下去</div>
          <div class="L b2 fs-tail" id="rp4">可那时禅宗，还只是个不起眼的小团体</div>"""),

# S2 黄梅大寺 10.08–17.94（cue5–9）
Scene("sc-huangmei", 10.08, 17.94, """
          <div class="L t2 fs-lead" id="hm1">真正让它天翻地覆的 ——</div>
          <div class="L t4 fs-big" id="hm2">两百多年后 · 湖北黄梅</div>
          <div class="L b2 fs-note" id="hm3">一座大寺，方丈是五祖弘忍</div>"""),

# S3 考题 17.94–25.40（cue10–13）
Scene("sc-exam", 17.94, 25.40, """
          <div class="L t2 fs-lead" id="ex1">弘忍年纪大了，要选接班人</div>
          <div class="L t4 fs-big" id="ex2">考题，只有一道</div>
          <div class="k-card L b1 fs-q" id="ex3">写一首偈，把修行的体会写出来</div>"""),

# S4 无人动笔·神秀 25.40–42.50（cue14–24）
Scene("sc-shenxiu", 25.40, 42.50, """
          <div class="L t1 fs-lead" id="sx1">全寺一千多号人，没一个敢动笔</div>
          <div class="L t2 fs-note" id="sx2">因为大家心里都有数 ——</div>
          <div class="L t3 fs-huge" id="sx3">神秀</div>
          <div class="L t5 fs-note" id="sx4">教授师 · 学问第一 · 讲经说法没人比得上</div>
          <div class="L b2 fs-tail" id="sx5">六祖的位子，除了他还能有谁？</div>"""),

# S5 半夜题墙 42.50–59.38（cue25–33）
Scene("sc-night", 42.50, 59.38, """
          <div class="L t1 fs-lead" id="nt1">神秀压力大到 —— 半夜不睡觉</div>
          <svg id="nt-svg" viewBox="0 0 1000 430">
            <line x1="40" y1="372" x2="960" y2="372" id="nt-ground"/>
            <rect x="520" y="70" width="380" height="302" id="nt-wall"/>
            <line x1="520" y1="70" x2="900" y2="70" id="nt-eave"/>
            <g transform="translate(300,372)"><g id="nt-monk">
              <circle cx="0" cy="-150" r="30" id="nt-head"/>
              <path d="M-40 -26 Q0 -118 40 -26 L46 0 L-46 0 Z" id="nt-robe"/>
              <line x1="30" y1="-86" x2="118" y2="-150" id="nt-arm"/>
            </g></g>
            <g id="nt-words"><text x="560" y="140">偈</text></g>
          </svg>
          <div class="L b2 fs-note" id="nt2">说好我就认，说不好，我也不丢人</div>"""),

# S6 全寺念偈 59.38–64.42（cue34–36）
Scene("sc-chant", 59.38, 64.42, """
          <div class="L t2 fs-big" id="ch1">第二天一早</div>
          <div class="L t4 fs-note" id="ch2">全寺都在念这首偈</div>
          <div class="L b2 fs-tail" id="ch3">眼看六祖，就算定了</div>"""),

# S7 苦力·还没到家 64.42–77.58（cue37–45）
Scene("sc-coolie", 64.42, 77.58, """
          <div class="L t1 fs-lead" id="cl1">这时候，后厨碓房里 ——</div>
          <svg id="cl-svg" viewBox="0 0 1000 400">
            <line x1="40" y1="356" x2="960" y2="356" id="cl-ground"/>
            <line x1="470" y1="120" x2="470" y2="356" id="cl-post"/>
            <g id="cl-lever"><line x1="250" y1="150" x2="720" y2="150" id="cl-beam"/>
              <rect x="250" y="138" width="60" height="24" id="cl-foot"/></g>
            <ellipse cx="720" cy="350" rx="58" ry="16" id="cl-mortar"/>
            <line x1="720" y1="150" x2="720" y2="330" id="cl-pestle"/>
            <g transform="translate(250,150)"><g id="cl-man">
              <circle cx="0" cy="-64" r="26" id="cl-head"/>
              <path d="M-34 0 Q0 -52 34 0 L38 0 L-38 0 Z" id="cl-robe"/>
            </g></g>
          </svg>
          <div class="L t5 fs-note" id="cl2">踩了八个月舂米碓，听见念偈，停下了活</div>
          <div class="L b2 fs-tail" id="cl3">这偈还没到家 —— 我也有一首，替我写上去</div>"""),

# S8 慧能亮相 77.58–80.90（cue46–47）
Scene("sc-huineng", 77.58, 80.90, """
          <div class="L t2 fs-note" id="hn1">这个苦力，大字不识一个</div>
          <div class="L t4 fs-huge" id="hn2">他，就是慧能</div>"""),

# S9 报名 80.90–85.60（cue48–50）
Scene("sc-hi", 80.90, 85.60, """
          <div class="L t3 fs-huge" id="hi1" style="font-size:120px">哈喽大家好，我是叶扬</div>
          <div class="L b2 fs-tail" id="hi2">先说说，慧能怎么混进碓房的</div>"""),

# S10 出身·闻经奔黄梅 85.60–106.72（cue51–63）
Scene("sc-origin", 85.60, 106.72, """
          <div class="L t1 fs-lead" id="or1">慧能生在岭南，今天的广东</div>
          <div class="k-rows" id="or2">
            <div class="k-row" id="orr1"><span class="kr-k">壹</span><span class="kr-t">从小没了爹</span></div>
            <div class="k-row" id="orr2"><span class="kr-k">贰</span><span class="kr-t">不识字</span></div>
            <div class="k-row" id="orr3"><span class="kr-k">叁</span><span class="kr-t">劈柴卖柴，养活老娘</span></div>
          </div>
          <div class="L t5 fs-note" id="or3">二十二岁送柴到客店，听见有人念《金刚经》</div>
          <div class="L b2 fs-tail" id="or4">心里一下被抓住 —— 安顿好老娘，一路奔了黄梅</div>"""),

# S11 南蛮佛性 106.72–118.90（cue64–73）
Scene("sc-barbarian", 106.72, 118.90, """
          <div class="L t1 fs-lead" id="br1">头回见面，弘忍没怎么客气</div>
          <div class="L t2 fs-q" id="br2">你这南蛮之人，也想成佛？</div>
          <div class="L t4 fs-big" id="br3">人有南北</div>
          <div class="L b2 fs-tail" id="br4">佛性，也分南北吗？</div>"""),

# S12 碓房八月 118.90–127.88（cue74–79）
Scene("sc-eightmo", 118.90, 127.88, """
          <div class="L t2 fs-note" id="em1">弘忍没再接话，心里明白 —— 这人根器厉害</div>
          <div class="L t4 fs-lead" id="em2">嘴上什么也没说，直接打发去踏碓</div>
          <div class="L b2 fs-big" id="em3">一踏，八个月</div>"""),

# S13 神秀偈 127.88–136.20（cue80–86）
Scene("sc-gatha1", 127.88, 136.20, """
          <div class="L t1 fs-lead" id="g1a">回到那两首偈。先看神秀写的 ——</div>
          <div class="gatha" id="g1b">
            <div class="g-line" id="g1l1">身是菩提树</div>
            <div class="g-line" id="g1l2">心如明镜台</div>
            <div class="g-line" id="g1l3">时时勤拂拭</div>
            <div class="g-line" id="g1l4">勿使惹尘埃</div>
          </div>"""),

# S14 公道话·渐修 136.20–157.34（cue87–98）
Scene("sc-fair", 136.20, 157.34, """
          <div class="L t1 fs-lead" id="fa1">先替神秀说句公道话</div>
          <div class="L t2 fs-big" id="fa2">这首偈，一点都没写错</div>
          <div class="L t4 fs-note" id="fa3">人心像镜子，用久了落灰，得天天擦，擦得亮亮的</div>
          <div class="k-card L t5 fs-q" id="fa4" style="padding:18px 40px">扎扎实实的渐修 · 一步一个脚印</div>
          <div class="L b2 fs-tail" id="fa5">弘忍说：按这首偈修，有大好处</div>"""),

# S15 擦的问题·灰当实有 157.34–177.20（cue99–108）
Scene("sc-wipe1", 157.34, 177.20, """
          <div class="L t1 fs-lead" id="w1a">但问题，恰恰藏在「擦」这个动作里</div>
          <svg id="w1-svg" viewBox="0 0 560 300">
            <line x1="60" y1="262" x2="500" y2="262" id="w1-ground"/>
            <line x1="280" y1="150" x2="280" y2="262" id="w1-stand"/>
            <g id="w1-mirror"><circle cx="280" cy="120" r="86" id="w1-rim"/>
              <circle cx="280" cy="120" r="74" id="w1-face"/>
              <circle cx="250" cy="96" r="6" class="w1-dust"/>
              <circle cx="312" cy="132" r="6" class="w1-dust"/>
              <circle cx="268" cy="150" r="6" class="w1-dust"/>
            </g>
            <path d="M420 70 q-40 26 -86 8" id="w1-arm"/>
          </svg>
          <div class="L t4 fs-note" id="w1b">天天擦，首先得默认 —— 镜子上真的有灰</div>
          <div class="L b2 fs-tail" id="w1c">烦恼本性是空的，当成真脏东西对着干，念头打不完</div>"""),

# S16 谁在擦 177.20–189.06（cue109–116）
Scene("sc-wipe2", 177.20, 189.06, """
          <div class="L t1 fs-lead" id="w2a">再往深问一步 ——</div>
          <div class="L t2 fs-huge" id="w2b" style="font-size:130px">是谁，在擦？</div>
          <div class="L t4 fs-note" id="w2c">一个要修行的「我」，一堆要被擦掉的「脏」</div>
          <div class="L b2 fs-tail" id="w2d">这一对立立起来 —— 门，就还没进去</div>"""),

# S17 慧能偈 189.06–196.44（cue117–121）
Scene("sc-gatha2", 189.06, 196.44, """
          <div class="L t1 fs-lead" id="g2a">那慧能的偈，怎么写的？</div>
          <div class="gatha" id="g2b">
            <div class="g-line" id="g2l1">菩提本无树</div>
            <div class="g-line" id="g2l2">明镜亦非台</div>
            <div class="g-line hot" id="g2l3">本来无一物</div>
            <div class="g-line" id="g2l4">何处惹尘埃</div>
          </div>"""),

# S18 掀根重构 196.44–222.58（cue122–135）
Scene("sc-reframe", 196.44, 222.58, """
          <div class="L t1 fs-note" id="rf1">根本没有那棵树，也没有那台镜子</div>
          <div class="L t2 fs-huge" id="rf2">本来无一物</div>
          <div class="L t3 fs-q" id="rf3">你说，灰往哪儿落？</div>
          <div class="L t4 fs-lead" id="rf4">不是抬杠 —— 是把整件事的根，掀了</div>
          <div class="L t5 fs-note" id="rf5">不是做减法，把脏东西一点点擦</div>
          <div class="L b2 fs-tail" id="rf6">你本来就是干净的 —— 是认出你本来的样子</div>"""),

# S19 debug 类比 222.58–242.00（cue136–146）
Scene("sc-debug", 222.58, 242.00, """
          <div class="L t1 fs-lead" id="db1">打个程序员熟悉的比方</div>
          <div class="term" id="db2">
            <div class="term-bar"><span class="tb-dot"></span><span class="tb-dot"></span><span class="tb-dot"></span><span class="tb-title">shenxiu — debug</span></div>
            <div class="term-body">
              <div class="term-line" id="dbl1"><span class="tl-prompt">&gt;</span> bug found &hellip; fixing</div>
              <div class="term-line" id="dbl2"><span class="tl-prompt">&gt;</span> fixed ✓</div>
              <div class="term-line" id="dbl3"><span class="tl-prompt">&gt;</span> bug found &hellip; <span class="tl-cur" id="dbcur">▋</span></div>
            </div>
          </div>
          <div class="L t5 fs-note" id="db3">慧能说：先别急着修，往下看一层 ——</div>
          <div class="L b2 fs-tail" id="db4">「被污染的系统」压根不存在 —— 参照系拿错了</div>"""),

# S20 鞋擦偈·保慧能 242.00–252.56（cue147–154）
Scene("sc-shoe", 242.00, 252.56, """
          <div class="L t2 fs-lead" id="sh1">弘忍心里有数，嘴上什么也没说</div>
          <div class="L t3 fs-note" id="sh2">当着众人的面，脱下鞋，几下把偈擦掉</div>
          <div class="L t5 fs-big" id="sh3">也没见性</div>
          <div class="L b2 fs-tail" id="sh4">他是在，保慧能</div>"""),

# S21 三夜讲经·悟道 252.56–272.84（cue155–165）
Scene("sc-awaken", 252.56, 272.84, """
          <div class="L t1 fs-lead" id="aw1">当夜三更，悄悄叫到房里，亲自讲《金刚经》</div>
          <div class="L t2 fs-big" id="aw2" style="font-size:84px">应无所住，而生其心</div>
          <div class="L t3 fs-huge" id="aw3" style="font-size:118px">慧能，豁然大悟</div>
          <div class="L b2 fs-note" id="aw4">何其自性 —— 本自清净 · 本不生灭 · 能生万法……</div>"""),

# S22 传衣钵·别再传 272.84–281.68（cue166–170）
Scene("sc-pass", 272.84, 281.68, """
          <div class="L t2 fs-lead" id="ps1">弘忍当即把衣钵传了过去</div>
          <div class="L t3 fs-note" id="ps2">这衣钵，是争端的由头</div>
          <div class="L t5 fs-big" id="ps3">从你这儿开始，别再往下传</div>
          <div class="L b2 fs-tail" id="ps4">催着慧能，连夜下山</div>"""),

# S23 大庾岭·惠明 281.68–301.36（cue171–184）
Scene("sc-dayuling", 281.68, 301.36, """
          <div class="L t1 fs-lead" id="dy1">没跑多远，大庾岭上，有人追了上来</div>
          <svg id="dy-svg" viewBox="0 0 1000 360">
            <path d="M0 320 L260 120 L420 320 Z" id="dy-mtn1"/>
            <path d="M300 320 L560 150 L760 320 Z" id="dy-mtn2"/>
            <line x1="40" y1="322" x2="960" y2="322" id="dy-ground"/>
            <g transform="translate(560,322)"><g id="dy-bundle">
              <rect x="-34" y="-40" width="68" height="40" rx="6" id="dy-cloth"/>
              <line x1="-34" y1="-24" x2="34" y2="-24" id="dy-knot"/>
            </g></g>
            <g transform="translate(700,322)"><g id="dy-huiming">
              <circle cx="0" cy="-120" r="26" id="dy-head"/>
              <path d="M-36 -10 Q0 -100 36 -10 L42 0 L-42 0 Z" id="dy-robe"/>
              <line x1="-30" y1="-58" x2="-96" y2="-30" id="dy-arm"/>
            </g></g>
          </svg>
          <div class="L t5 fs-note" id="dy2">惠明出家前当过将军，衣钵放石头上，居然提不动</div>
          <div class="L b2 fs-tail" id="dy3">别思善别思恶 —— 哪个是你惠明的本来面目？</div>"""),

# S24 避难猎人·肉边菜 301.36–312.38（cue185–190）
Scene("sc-hunter", 301.36, 312.38, """
          <div class="L t2 fs-lead" id="ht1">慧能在南方避难，整整十五年</div>
          <div class="L t3 fs-note" id="ht2">混在猎人队里守网，反倒偷偷把猎物放走</div>
          <div class="L t5 fs-huge" id="ht3">肉边菜</div>
          <div class="L b2 fs-tail" id="ht4">自己没素的吃，就吃肉边菜</div>"""),

# S25 风幡·剃度曹溪 312.38–338.78（cue191–207）
Scene("sc-flag", 312.38, 338.78, """
          <div class="L t1 fs-lead" id="fl1">十五年后，广州法性寺</div>
          <svg id="fl-svg" viewBox="0 0 1000 300">
            <line x1="200" y1="30" x2="200" y2="272" id="fl-pole"/>
            <g id="fl-cloth"><path d="M200 60 q120 30 240 0 q60 -14 120 0 l0 70 q-60 14 -120 0 q-120 30 -240 0 Z" id="fl-banner"/></g>
            <g id="fl-wind">
              <path d="M620 80 q50 -16 100 0" class="fl-windline"/>
              <path d="M640 130 q50 -16 100 0" class="fl-windline"/>
              <path d="M620 180 q50 -16 100 0" class="fl-windline"/>
            </g>
          </svg>
          <div class="L t3 fs-big" id="fl2" style="font-size:78px">不是风动，不是幡动 —— 仁者心动</div>
          <div class="L t5 fs-note" id="fl3">满座皆惊。印宗法师反过来给他剃度，还拜他为师</div>
          <div class="L b2 fs-tail" id="fl4">正式出山，长住韶关曹溪 —— 今天的南华寺</div>"""),

# S26 南顿北渐 338.78–354.08（cue208–218）
Scene("sc-schools", 338.78, 354.08, """
          <div class="L t1 fs-lead" id="sc1">而神秀呢？去了北方</div>
          <div class="L t2 fs-note" id="sc2">被武则天拜为国师 · 两京法主 · 三帝国师</div>
          <div class="L t4 fs-huge" id="sc3">南顿北渐</div>
          <div class="L b2 fs-tail" id="sc4">慧能在南讲顿悟，神秀在北讲渐修</div>"""),

# S27 神会·坛经 354.08–372.44（cue219–226）
Scene("sc-shenhui", 354.08, 372.44, """
          <div class="L t1 fs-lead" id="shh1">最后翻格局的，是弟子神会</div>
          <div class="L t2 fs-note" id="shh2">拼了命北上争正统，南宗才成了主流</div>
          <div class="L t4 fs-huge" id="shh3" style="font-size:120px">《六祖坛经》</div>
          <div class="L b2 fs-tail" id="shh4">法海记录 —— 僧人著作里，唯一尊称「经」的一部</div>"""),

# S28 极端一·神秀非失败 372.44–394.26（cue227–239）
Scene("sc-extreme1", 372.44, 394.26, """
          <div class="L t1 fs-lead" id="e1a">说到这儿，你可别走两个极端</div>
          <div class="L t2 fs-note" id="e1b">一个极端：觉得神秀是失败者 —— 不是</div>
          <div class="L t3 fs-q" id="e1c">神秀在北方度了无数人，北宗传了很久</div>
          <div class="L t4 fs-big" id="e1d" style="font-size:80px">走到镜前 · 看穿镜子</div>
          <div class="L b2 fs-tail" id="e1e">没有「时时勤拂拭」，「本来无一物」多半只是口头禅</div>"""),

# S29 极端二·不立文字 394.26–405.88（cue240–244）
Scene("sc-extreme2", 394.26, 405.88, """
          <div class="L t1 fs-lead" id="e2a">另一个极端：读书没用，不识字反而厉害？</div>
          <div class="L t2 fs-huge" id="e2b" style="font-size:110px">不立文字</div>
          <div class="L t4 fs-note" id="e2c">是说那个最终的东西，文字装不下、学历给不了</div>
          <div class="L b2 fs-tail" id="e2d">可不是，让你把书烧了</div>"""),

# S30 自我追问 405.88–422.90（cue245–253）
Scene("sc-askself", 405.88, 422.90, """
          <div class="L t1 fs-lead" id="as1">绕回到我们自己身上</div>
          <div class="L t2 fs-note" id="as2">小马达又转起来 —— 嫌不够好，列一堆缺点，跟念头较劲</div>
          <div class="L t3 fs-big" id="as3">停一秒，问一句</div>
          <div class="L t5 fs-q" id="as4">那个等着被修好的「我」，真的存在吗？</div>
          <div class="L b2 fs-tail" id="as5">答案，你自己心里有数就好</div>"""),

# S31 预告＋道别 422.90–total（cue254–264）
Scene("sc-next", 422.90, total, """
          <div class="L t1 fs-lead" id="nx1">第一季到这里，禅宗的来龙去脉，讲完了</div>
          <div class="L t2 fs-note" id="nx2">下一季：乱世里有个会「变魔术」的和尚</div>
          <div class="L t3 fs-q" id="nx3">靠咒语混进军阀大营，救下几十万苍生</div>
          <div class="L t4 fs-note" id="nx4">他徒弟，让全中国的和尚都姓了「释」</div>
          <div class="L t5 fs-big" id="nx5" style="font-size:80px">佛图澄 · 道安，下一季见</div>
          <div class="L b2 fs-huge" id="nx6" style="font-size:74px">我是叶扬，我们下期见</div>"""),
]

# ---------- 场景专属 CSS ----------
PROJECT_CSS = """
      /* ===== 通用定位/字号组合 ===== */
      .L { position:absolute; left:140px; right:140px; text-align:center; }
      .t1{ top:120px; } .t2{ top:226px; } .t3{ top:336px; }
      .t4{ top:452px; } .t5{ top:566px; }
      .b1{ bottom:322px; } .b2{ bottom:214px; }
      .fs-note{ font-size:47px; color:#5f574c; line-height:1.5; }
      .fs-lead{ font-size:54px; color:#5f574c; }
      .fs-q{ font-size:62px; color:#2b2620; line-height:1.4; }
      .fs-big{ font-size:92px; color:#b03120; letter-spacing:.08em; line-height:1.25; }
      .fs-huge{ font-size:140px; color:#b03120; letter-spacing:.1em; line-height:1.2; }
      .fs-tail{ font-size:54px; color:#b03120; line-height:1.4; }

      /* ===== 通用卡片/行 ===== */
      .k-card { background:#fdfaf2; border:3px solid #d8cfb8; border-radius:18px;
        padding:24px 44px; }
      .k-rows { position:absolute; left:50%; top:300px; transform:translateX(-50%);
        width:680px; background:#fdfaf2; border:3px solid #d8cfb8; border-radius:18px;
        padding:14px 40px; }
      .k-row { display:flex; align-items:center; padding:14px 0;
        border-bottom:2px dashed #d8cfb8; }
      .k-row:last-child { border-bottom:none; }
      .kr-k { font-size:44px; color:#b03120; width:80px; }
      .kr-t { font-size:54px; color:#2b2620; letter-spacing:.05em; }

      /* ===== 偈（S13/S17） ===== */
      .gatha { position:absolute; left:50%; top:268px; transform:translateX(-50%);
        background:#fdfaf2; border:3px solid #d8cfb8; border-radius:18px;
        padding:22px 70px; }
      .g-line { font-size:62px; color:#2b2620; line-height:1.62; letter-spacing:.1em; }
      .g-line.hot { color:#b03120; }

      /* ===== 长场景文字块 ID 级位置修正（避重叠，不影响通用类） ===== */
      #w1b { top:486px; }                    /* S15 图示底 476 */
      #rf2 { top:196px; font-size:120px; }   /* S18 */
      #rf3 { top:356px; }
      #rf4 { top:470px; }
      #rf5 { top:572px; }
      #aw2 { top:210px; font-size:78px; }    /* S21 */
      #aw3 { top:322px; font-size:104px; }
      #fl2 { top:436px; font-size:70px; }    /* S25 图示底 424 */

      /* ===== S5 半夜题墙 ===== */
      #nt-svg { position:absolute; left:50%; top:218px; transform:translateX(-50%);
        width:760px; height:328px; }
      #nt-ground { stroke:#2b2620; stroke-width:5; }
      #nt-wall { fill:#f3ead6; stroke:#2b2620; stroke-width:5; }
      #nt-eave { stroke:#2b2620; stroke-width:7; }
      #nt-head { fill:#fdfaf2; stroke:#2b2620; stroke-width:5; }
      #nt-robe { fill:rgba(176,49,32,.08); stroke:#b03120; stroke-width:5;
        stroke-linejoin:round; }
      #nt-arm { stroke:#2b2620; stroke-width:6; stroke-linecap:round; }
      #nt-words text { font-size:52px; fill:#8a6418; }

      /* ===== S7 踏碓 ===== */
      #cl-svg { position:absolute; left:50%; top:200px; transform:translateX(-50%);
        width:720px; height:288px; }
      #cl-ground { stroke:#2b2620; stroke-width:5; }
      #cl-post { stroke:#8a6418; stroke-width:7; }
      #cl-beam { stroke:#2b2620; stroke-width:9; stroke-linecap:round; }
      #cl-foot { fill:#b03120; }
      #cl-mortar { fill:rgba(138,100,24,.18); stroke:#8a6418; stroke-width:5; }
      #cl-pestle { stroke:#2b2620; stroke-width:7; }
      #cl-head { fill:#fdfaf2; stroke:#2b2620; stroke-width:5; }
      #cl-robe { fill:rgba(176,49,32,.08); stroke:#b03120; stroke-width:5;
        stroke-linejoin:round; }

      /* ===== S15 擦镜 ===== */
      #w1-svg { position:absolute; left:50%; top:240px; transform:translateX(-50%);
        width:440px; height:236px; }
      #w1-ground { stroke:#2b2620; stroke-width:5; }
      #w1-stand { stroke:#8a6418; stroke-width:7; }
      #w1-rim { fill:#f3ead6; stroke:#2b2620; stroke-width:6; }
      #w1-face { fill:#faf4e4; stroke:#b7a079; stroke-width:3; }
      .w1-dust { fill:rgba(43,38,32,.4); }
      #w1-arm { fill:none; stroke:#2b2620; stroke-width:7; stroke-linecap:round; }

      /* ===== S19 终端 ===== */
      .term { position:absolute; left:50%; top:230px; transform:translateX(-50%);
        width:800px; background:#fdfaf2; border:3px solid #b7a079; border-radius:16px;
        overflow:hidden; }
      .term-bar { background:#ece2cb; padding:14px 22px; }
      .tb-dot { display:inline-block; width:15px; height:15px; border-radius:50%;
        background:#c9bda2; margin-right:9px; }
      .tb-title { margin-left:16px; font-size:30px; color:#5f574c;
        font-family:Consolas,monospace; }
      .term-body { padding:24px 30px; text-align:left;
        font-family:Consolas,'Courier New',monospace; }
      .term-line { font-size:42px; color:#2b2620; line-height:1.7; }
      .tl-prompt { color:#4d7c2f; margin-right:14px; }
      .tl-cur { color:#b03120; }

      /* ===== S23 大庾岭 ===== */
      #dy-svg { position:absolute; left:50%; top:224px; transform:translateX(-50%);
        width:780px; height:282px; }
      #dy-mtn1, #dy-mtn2 { fill:rgba(138,100,24,.14); stroke:#8a6418;
        stroke-width:5; stroke-linejoin:round; }
      #dy-ground { stroke:#2b2620; stroke-width:5; }
      #dy-cloth { fill:rgba(176,49,32,.18); stroke:#b03120; stroke-width:5; }
      #dy-knot { stroke:#b03120; stroke-width:5; }
      #dy-head { fill:#fdfaf2; stroke:#2b2620; stroke-width:5; }
      #dy-robe { fill:rgba(176,49,32,.08); stroke:#b03120; stroke-width:5;
        stroke-linejoin:round; }
      #dy-arm { stroke:#2b2620; stroke-width:6; stroke-linecap:round; }

      /* ===== S25 风幡 ===== */
      #fl-svg { position:absolute; left:50%; top:196px; transform:translateX(-50%);
        width:720px; height:228px; }
      #fl-pole { stroke:#2b2620; stroke-width:7; }
      #fl-banner { fill:rgba(176,49,32,.14); stroke:#b03120; stroke-width:5;
        stroke-linejoin:round; }
      .fl-windline { fill:none; stroke:#8a6418; stroke-width:6;
        stroke-linecap:round; }
"""

# ---------- 场景时间轴（时间显式给秒） ----------
SCENE_JS = """
      /* S1 承上 0–10.08 */
      tl.fromTo('#sc-recap > .scene-inner',{opacity:0},{opacity:1,duration:.5},0);
      tl.from('#rp1',{y:26,opacity:0,duration:.6},.2);
      tl.from('#rp2',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.5)'},1.6);
      tl.from('#rp3',{y:22,opacity:0,duration:.6},4.6);
      tl.from('#rp4',{y:22,opacity:0,duration:.6},6.6);
      tl.to('#sc-recap > .scene-inner',{opacity:0,duration:.4},9.68);

      /* S2 黄梅 10.08–17.94 */
      tl.fromTo('#sc-huangmei > .scene-inner',{opacity:0},{opacity:1,duration:.5},10.08);
      tl.from('#hm1',{y:24,opacity:0,duration:.6},10.3);
      tl.from('#hm2',{scale:.74,opacity:0,duration:.8,ease:'back.out(1.5)'},12.4);
      tl.from('#hm3',{y:22,opacity:0,duration:.6},15.9);
      tl.to('#sc-huangmei > .scene-inner',{opacity:0,duration:.4},17.54);

      /* S3 考题 17.94–25.40 */
      tl.fromTo('#sc-exam > .scene-inner',{opacity:0},{opacity:1,duration:.5},17.94);
      tl.from('#ex1',{y:24,opacity:0,duration:.6},18.2);
      tl.from('#ex2',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.7)'},20.6);
      tl.from('#ex3',{y:30,opacity:0,duration:.7},22.8);
      tl.to('#sc-exam > .scene-inner',{opacity:0,duration:.4},25.0);

      /* S4 无人动笔·神秀 25.40–42.50 */
      tl.fromTo('#sc-shenxiu > .scene-inner',{opacity:0},{opacity:1,duration:.5},25.40);
      tl.from('#sx1',{y:24,opacity:0,duration:.6},25.7);
      tl.from('#sx2',{y:20,opacity:0,duration:.6},30.2);
      tl.from('#sx3',{scale:.66,opacity:0,duration:.85,ease:'back.out(1.6)'},33.3);
      tl.from('#sx4',{y:22,opacity:0,duration:.6},36.8);
      tl.from('#sx5',{y:22,opacity:0,duration:.6},39.6);
      tl.to('#sc-shenxiu > .scene-inner',{opacity:0,duration:.4},42.1);

      /* S5 半夜题墙 42.50–59.38 */
      tl.fromTo('#sc-night > .scene-inner',{opacity:0},{opacity:1,duration:.5},42.50);
      tl.from('#nt1',{y:24,opacity:0,duration:.6},42.8);
      tl.from('#nt-svg',{y:36,opacity:0,duration:.8,ease:'back.out(1.3)'},45.4);
      tl.to('#nt-arm',{rotation:-7,transformOrigin:'left center',duration:.7,
        ease:'sine.inOut',yoyo:true,repeat:3},50.0);
      tl.from('#nt2',{y:22,opacity:0,duration:.6},55.6);
      tl.to('#sc-night > .scene-inner',{opacity:0,duration:.4},58.98);

      /* S6 全寺念偈 59.38–64.42 */
      tl.fromTo('#sc-chant > .scene-inner',{opacity:0},{opacity:1,duration:.5},59.38);
      tl.from('#ch1',{scale:.7,opacity:0,duration:.7,ease:'back.out(1.6)'},59.6);
      tl.from('#ch2',{y:22,opacity:0,duration:.6},61.2);
      tl.from('#ch3',{y:22,opacity:0,duration:.6},62.8);
      tl.to('#sc-chant > .scene-inner',{opacity:0,duration:.35},64.02);

      /* S7 苦力·还没到家 64.42–77.58 */
      tl.fromTo('#sc-coolie > .scene-inner',{opacity:0},{opacity:1,duration:.5},64.42);
      tl.from('#cl1',{y:22,opacity:0,duration:.6},64.7);
      tl.from('#cl-svg',{y:34,opacity:0,duration:.8,ease:'back.out(1.3)'},66.8);
      tl.to('#cl-lever',{rotation:9,transformOrigin:'470px 150px',duration:.9,
        ease:'sine.inOut',yoyo:true,repeat:5},69.0);
      tl.from('#cl2',{y:22,opacity:0,duration:.6},71.6);
      tl.from('#cl3',{y:24,opacity:0,duration:.7,ease:'back.out(1.5)'},74.0);
      tl.to('#sc-coolie > .scene-inner',{opacity:0,duration:.4},77.18);

      /* S8 慧能亮相 77.58–80.90 */
      tl.fromTo('#sc-huineng > .scene-inner',{opacity:0},{opacity:1,duration:.5},77.58);
      tl.from('#hn1',{y:22,opacity:0,duration:.55},77.8);
      tl.from('#hn2',{scale:.62,opacity:0,duration:.8,ease:'back.out(1.8)'},78.7);
      tl.to('#sc-huineng > .scene-inner',{opacity:0,duration:.3},80.6);

      /* S9 报名 80.90–85.60 */
      tl.fromTo('#sc-hi > .scene-inner',{opacity:0},{opacity:1,duration:.5},80.90);
      tl.from('#hi1',{y:34,opacity:0,duration:.7,ease:'back.out(1.5)'},81.1);
      tl.from('#hi2',{y:22,opacity:0,duration:.6},83.6);
      tl.to('#sc-hi > .scene-inner',{opacity:0,duration:.4},85.2);

      /* S10 出身闻经 85.60–106.72 */
      tl.fromTo('#sc-origin > .scene-inner',{opacity:0},{opacity:1,duration:.5},85.60);
      tl.from('#or1',{y:22,opacity:0,duration:.6},85.9);
      tl.from('#or2',{y:36,opacity:0,duration:.8,ease:'back.out(1.3)'},88.2);
      tl.from('#orr1,#orr2,#orr3',{x:-36,opacity:0,duration:.5,stagger:.8},89.4);
      tl.from('#or3',{y:22,opacity:0,duration:.6},98.0);
      tl.from('#or4',{y:24,opacity:0,duration:.7,ease:'back.out(1.4)'},102.2);
      tl.to('#sc-origin > .scene-inner',{opacity:0,duration:.4},106.32);

      /* S11 南蛮佛性 106.72–118.90 */
      tl.fromTo('#sc-barbarian > .scene-inner',{opacity:0},{opacity:1,duration:.5},106.72);
      tl.from('#br1',{y:22,opacity:0,duration:.6},107.0);
      tl.from('#br2',{scale:.72,opacity:0,duration:.7,ease:'back.out(1.5)'},110.6);
      tl.from('#br3',{y:30,opacity:0,duration:.7,ease:'back.out(1.5)'},114.6);
      tl.from('#br4',{y:22,opacity:0,duration:.6},116.8);
      tl.to('#sc-barbarian > .scene-inner',{opacity:0,duration:.4},118.5);

      /* S12 碓房八月 118.90–127.88 */
      tl.fromTo('#sc-eightmo > .scene-inner',{opacity:0},{opacity:1,duration:.5},118.90);
      tl.from('#em1',{y:22,opacity:0,duration:.6},119.2);
      tl.from('#em2',{y:22,opacity:0,duration:.6},123.6);
      tl.from('#em3',{scale:.66,opacity:0,duration:.8,ease:'back.out(1.8)'},125.2);
      tl.to('#sc-eightmo > .scene-inner',{opacity:0,duration:.4},127.48);

      /* S13 神秀偈 127.88–136.20 */
      tl.fromTo('#sc-gatha1 > .scene-inner',{opacity:0},{opacity:1,duration:.5},127.88);
      tl.from('#g1a',{y:22,opacity:0,duration:.55},128.1);
      tl.from('#g1b',{y:36,opacity:0,duration:.8,ease:'back.out(1.3)'},129.6);
      tl.from('#g1l1,#g1l2,#g1l3,#g1l4',{x:-30,opacity:0,duration:.45,stagger:.62},130.6);
      tl.to('#sc-gatha1 > .scene-inner',{opacity:0,duration:.4},135.8);

      /* S14 公道话渐修 136.20–157.34 */
      tl.fromTo('#sc-fair > .scene-inner',{opacity:0},{opacity:1,duration:.5},136.20);
      tl.from('#fa1',{y:22,opacity:0,duration:.6},136.5);
      tl.from('#fa2',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.6)'},139.2);
      tl.from('#fa3',{y:22,opacity:0,duration:.6},143.4);
      tl.from('#fa4',{y:26,opacity:0,duration:.6,ease:'back.out(1.4)'},149.8);
      tl.from('#fa5',{y:22,opacity:0,duration:.6},153.6);
      tl.to('#sc-fair > .scene-inner',{opacity:0,duration:.4},156.94);

      /* S15 擦的问题 157.34–177.20 */
      tl.fromTo('#sc-wipe1 > .scene-inner',{opacity:0},{opacity:1,duration:.5},157.34);
      tl.from('#w1a',{y:22,opacity:0,duration:.6},157.6);
      tl.from('#w1-svg',{scale:.8,opacity:0,duration:.8,ease:'back.out(1.4)'},160.6);
      tl.to('#w1-mirror',{rotation:-6,transformOrigin:'280px 256px',duration:1.0,
        ease:'sine.inOut',yoyo:true,repeat:4},163.0);
      tl.from('#w1b',{y:22,opacity:0,duration:.6},167.6);
      tl.from('#w1c',{y:22,opacity:0,duration:.6},172.4);
      tl.to('#sc-wipe1 > .scene-inner',{opacity:0,duration:.4},176.8);

      /* S16 谁在擦 177.20–189.06 */
      tl.fromTo('#sc-wipe2 > .scene-inner',{opacity:0},{opacity:1,duration:.5},177.20);
      tl.from('#w2a',{y:22,opacity:0,duration:.6},177.5);
      tl.from('#w2b',{scale:.6,opacity:0,duration:.85,ease:'back.out(1.8)'},179.6);
      tl.from('#w2c',{y:22,opacity:0,duration:.6},183.6);
      tl.from('#w2d',{y:22,opacity:0,duration:.6},186.0);
      tl.to('#sc-wipe2 > .scene-inner',{opacity:0,duration:.4},188.66);

      /* S17 慧能偈 189.06–196.44 */
      tl.fromTo('#sc-gatha2 > .scene-inner',{opacity:0},{opacity:1,duration:.5},189.06);
      tl.from('#g2a',{y:22,opacity:0,duration:.5},189.3);
      tl.from('#g2b',{y:34,opacity:0,duration:.75,ease:'back.out(1.3)'},190.4);
      tl.from('#g2l1,#g2l2,#g2l3,#g2l4',{x:-30,opacity:0,duration:.42,stagger:.5},191.0);
      tl.to('#sc-gatha2 > .scene-inner',{opacity:0,duration:.4},196.04);

      /* S18 掀根重构 196.44–222.58 */
      tl.fromTo('#sc-reframe > .scene-inner',{opacity:0},{opacity:1,duration:.5},196.44);
      tl.from('#rf1',{y:20,opacity:0,duration:.55},196.7);
      tl.from('#rf2',{scale:.6,opacity:0,duration:.85,ease:'back.out(1.8)'},199.0);
      tl.from('#rf3',{y:22,opacity:0,duration:.6},201.6);
      tl.from('#rf4',{y:22,opacity:0,duration:.6},205.4);
      tl.from('#rf5',{y:20,opacity:0,duration:.6},210.4);
      tl.from('#rf6',{y:22,opacity:0,duration:.65},216.6);
      tl.to('#sc-reframe > .scene-inner',{opacity:0,duration:.4},222.18);

      /* S19 debug 222.58–242.00 */
      tl.fromTo('#sc-debug > .scene-inner',{opacity:0},{opacity:1,duration:.5},222.58);
      tl.from('#db1',{y:22,opacity:0,duration:.6},222.9);
      tl.from('#db2',{y:34,opacity:0,duration:.8,ease:'back.out(1.3)'},225.2);
      tl.from('#dbl1,#dbl2,#dbl3',{x:-26,opacity:0,duration:.45,stagger:.7},227.0);
      tl.to('#dbcur',{opacity:.2,duration:.5,ease:'sine.inOut',yoyo:true,repeat:6},230);
      tl.from('#db3',{y:22,opacity:0,duration:.6},235.0);
      tl.from('#db4',{y:22,opacity:0,duration:.65},238.0);
      tl.to('#sc-debug > .scene-inner',{opacity:0,duration:.4},241.6);

      /* S20 鞋擦偈 242.00–252.56 */
      tl.fromTo('#sc-shoe > .scene-inner',{opacity:0},{opacity:1,duration:.5},242.00);
      tl.from('#sh1',{y:22,opacity:0,duration:.6},242.3);
      tl.from('#sh2',{y:22,opacity:0,duration:.6},246.4);
      tl.from('#sh3',{scale:.66,opacity:0,duration:.8,ease:'back.out(1.8)'},249.0);
      tl.from('#sh4',{y:22,opacity:0,duration:.55},251.2);
      tl.to('#sc-shoe > .scene-inner',{opacity:0,duration:.4},252.16);

      /* S21 讲经悟道 252.56–272.84 */
      tl.fromTo('#sc-awaken > .scene-inner',{opacity:0},{opacity:1,duration:.5},252.56);
      tl.from('#aw1',{y:22,opacity:0,duration:.6},252.8);
      tl.from('#aw2',{y:26,opacity:0,duration:.7,ease:'back.out(1.5)'},258.0);
      tl.from('#aw3',{scale:.62,opacity:0,duration:.85,ease:'back.out(1.8)'},261.4);
      tl.from('#aw4',{y:22,opacity:0,duration:.6},266.4);
      tl.to('#sc-awaken > .scene-inner',{opacity:0,duration:.4},272.44);

      /* S22 传衣钵 272.84–281.68 */
      tl.fromTo('#sc-pass > .scene-inner',{opacity:0},{opacity:1,duration:.5},272.84);
      tl.from('#ps1',{y:22,opacity:0,duration:.6},273.1);
      tl.from('#ps2',{y:22,opacity:0,duration:.6},275.4);
      tl.from('#ps3',{scale:.7,opacity:0,duration:.8,ease:'back.out(1.7)'},277.6);
      tl.from('#ps4',{y:22,opacity:0,duration:.6},279.8);
      tl.to('#sc-pass > .scene-inner',{opacity:0,duration:.4},281.28);

      /* S23 大庾岭 281.68–301.36 */
      tl.fromTo('#sc-dayuling > .scene-inner',{opacity:0},{opacity:1,duration:.5},281.68);
      tl.from('#dy1',{y:22,opacity:0,duration:.6},281.9);
      tl.from('#dy-svg',{y:32,opacity:0,duration:.8,ease:'back.out(1.3)'},284.6);
      tl.to('#dy-huiming',{x:6,duration:.55,ease:'sine.inOut',yoyo:true,repeat:5},290.0);
      tl.from('#dy2',{y:22,opacity:0,duration:.6},292.0);
      tl.from('#dy3',{y:22,opacity:0,duration:.65},296.4);
      tl.to('#sc-dayuling > .scene-inner',{opacity:0,duration:.4},300.96);

      /* S24 猎人肉边菜 301.36–312.38 */
      tl.fromTo('#sc-hunter > .scene-inner',{opacity:0},{opacity:1,duration:.5},301.36);
      tl.from('#ht1',{y:22,opacity:0,duration:.6},301.7);
      tl.from('#ht2',{y:22,opacity:0,duration:.6},305.4);
      tl.from('#ht3',{scale:.66,opacity:0,duration:.8,ease:'back.out(1.8)'},307.6);
      tl.from('#ht4',{y:22,opacity:0,duration:.55},310.4);
      tl.to('#sc-hunter > .scene-inner',{opacity:0,duration:.4},311.98);

      /* S25 风幡剃度曹溪 312.38–338.78 */
      tl.fromTo('#sc-flag > .scene-inner',{opacity:0},{opacity:1,duration:.5},312.38);
      tl.from('#fl1',{y:22,opacity:0,duration:.6},312.7);
      tl.from('#fl-svg',{y:30,opacity:0,duration:.8,ease:'back.out(1.3)'},314.4);
      tl.to('#fl-cloth',{x:16,duration:1.2,ease:'sine.inOut',yoyo:true,repeat:5},316);
      tl.to('#fl-wind',{x:24,opacity:.5,duration:1.1,ease:'sine.inOut',
        yoyo:true,repeat:5},316);
      tl.from('#fl2',{y:26,opacity:0,duration:.7,ease:'back.out(1.4)'},321.0);
      tl.from('#fl3',{y:22,opacity:0,duration:.6},329.0);
      tl.from('#fl4',{y:22,opacity:0,duration:.6},334.0);
      tl.to('#sc-flag > .scene-inner',{opacity:0,duration:.4},338.38);

      /* S26 南顿北渐 338.78–354.08 */
      tl.fromTo('#sc-schools > .scene-inner',{opacity:0},{opacity:1,duration:.5},338.78);
      tl.from('#sc1',{y:22,opacity:0,duration:.6},339.1);
      tl.from('#sc2',{y:22,opacity:0,duration:.6},341.0);
      tl.from('#sc3',{scale:.66,opacity:0,duration:.85,ease:'back.out(1.8)'},346.0);
      tl.from('#sc4',{y:22,opacity:0,duration:.6},350.8);
      tl.to('#sc-schools > .scene-inner',{opacity:0,duration:.4},353.68);

      /* S27 神会坛经 354.08–372.44 */
      tl.fromTo('#sc-shenhui > .scene-inner',{opacity:0},{opacity:1,duration:.5},354.08);
      tl.from('#shh1',{y:22,opacity:0,duration:.6},354.4);
      tl.from('#shh2',{y:22,opacity:0,duration:.6},358.4);
      tl.from('#shh3',{scale:.66,opacity:0,duration:.85,ease:'back.out(1.8)'},363.0);
      tl.from('#shh4',{y:22,opacity:0,duration:.6},368.0);
      tl.to('#sc-shenhui > .scene-inner',{opacity:0,duration:.4},372.04);

      /* S28 极端一 372.44–394.26 */
      tl.fromTo('#sc-extreme1 > .scene-inner',{opacity:0},{opacity:1,duration:.5},372.44);
      tl.from('#e1a',{y:22,opacity:0,duration:.6},372.7);
      tl.from('#e1b',{y:22,opacity:0,duration:.6},375.0);
      tl.from('#e1c',{y:22,opacity:0,duration:.6},378.8);
      tl.from('#e1d',{scale:.74,opacity:0,duration:.8,ease:'back.out(1.6)'},383.0);
      tl.from('#e1e',{y:22,opacity:0,duration:.6},389.0);
      tl.to('#sc-extreme1 > .scene-inner',{opacity:0,duration:.4},393.86);

      /* S29 极端二 394.26–405.88 */
      tl.fromTo('#sc-extreme2 > .scene-inner',{opacity:0},{opacity:1,duration:.5},394.26);
      tl.from('#e2a',{y:22,opacity:0,duration:.6},394.6);
      tl.from('#e2b',{scale:.66,opacity:0,duration:.8,ease:'back.out(1.8)'},397.0);
      tl.from('#e2c',{y:22,opacity:0,duration:.6},400.4);
      tl.from('#e2d',{y:22,opacity:0,duration:.55},403.6);
      tl.to('#sc-extreme2 > .scene-inner',{opacity:0,duration:.4},405.48);

      /* S30 自我追问 405.88–422.90 */
      tl.fromTo('#sc-askself > .scene-inner',{opacity:0},{opacity:1,duration:.5},405.88);
      tl.from('#as1',{y:22,opacity:0,duration:.6},406.1);
      tl.from('#as2',{y:22,opacity:0,duration:.6},408.6);
      tl.from('#as3',{scale:.72,opacity:0,duration:.8,ease:'back.out(1.6)'},413.0);
      tl.from('#as4',{y:24,opacity:0,duration:.7,ease:'back.out(1.4)'},416.0);
      tl.from('#as5',{y:22,opacity:0,duration:.6},420.4);
      tl.to('#sc-askself > .scene-inner',{opacity:0,duration:.4},422.5);

      /* S31 预告道别 422.90–TOTAL */
      tl.fromTo('#sc-next > .scene-inner',{opacity:0},{opacity:1,duration:.5},422.90);
      tl.from('#nx1',{y:22,opacity:0,duration:.6},423.2);
      tl.from('#nx2',{y:22,opacity:0,duration:.6},427.4);
      tl.from('#nx3',{y:22,opacity:0,duration:.6},430.0);
      tl.from('#nx4',{y:22,opacity:0,duration:.6},434.4);
      tl.from('#nx5',{scale:.72,opacity:0,duration:.8,ease:'back.out(1.6)'},437.0);
      tl.from('#nx6',{y:22,opacity:0,duration:.6},443.0);
"""

# ---------- 底部字幕轨道 ----------
# onset 实测中位数 +290ms（whisper 吞句间停顿、整体偏早）：整句与逐字一起后移
frag = char_track(cues, chars, THEME.accent, time_offset=0.29)

# ---------- 组装 ----------
body = "\n".join([
    audio_tag("media/huineng-yeyang.wav", total),
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
