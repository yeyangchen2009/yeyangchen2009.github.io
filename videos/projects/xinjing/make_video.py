# -*- coding: utf-8 -*-
"""《心经》成片生成器。

本片结构在五片中最特殊，全部作为项目内容保留：
- 动态云雾 mp4 背景（track3，media/bg.mp4，制作过程见 make_bg.md）
- bgveil 四层暗化叠层 + halo 双环
- 标题卡（0–3.4s）退场时，#caption-wrap 从 y:151 上移到 y:0
- 中央 76px 逐字 cue clip（260 字，到点变金带光晕）
- 底部整句字幕（.sub 直接放整句，.28s 淡变）
- 结尾卡（69.9–71.5s）
双时长：root 71.5s，口播音轨 70.19s。
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, assemble_css, render_page,
                       audio_tag, center_char_clips, sentence_track,
                       DARK_GOLD_XJ)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars = data["cues"], data["chars"]
TOTAL = 71.5
AUDIO_DUR = 70.19
THEME = DARK_GOLD_XJ

# ---------- 项目专属 CSS（含 @font-face；无公共 .scene / 字幕块） ----------
PROJECT_CSS = """
      /* 动态云雾视频背景 */
      #bgvideo {
        position: absolute; inset: 0;
        width: 1920px; height: 1080px;
        object-fit: cover;
      }
      /* 暗化叠层：彩色版——四周减暗保鲜艳，仅中央局部暗盒承托金字 + 极淡金光 */
      #bgveil {
        position: absolute; inset: 0;
        background:
          radial-gradient(ellipse 60% 45% at 50% 46%, rgba(232,184,75,.07), transparent 70%),
          radial-gradient(ellipse 135% 105% at 50% 50%, transparent 55%, rgba(0,0,0,.42) 100%),
          radial-gradient(ellipse 60% 44% at 50% 47%, rgba(5,8,15,.55), transparent 72%),
          linear-gradient(rgba(5,8,15,.12), rgba(5,8,15,.12));
      }
      #halo {
        position: absolute; left: 50%; top: 50%;
        width: 760px; height: 760px; transform: translate(-50%,-50%);
        border: 1px solid rgba(232,184,75,.10); border-radius: 50%;
      }
      #halo2 {
        position: absolute; left: 50%; top: 50%;
        width: 1040px; height: 1040px; transform: translate(-50%,-50%);
        border: 1px solid rgba(232,184,75,.05); border-radius: 50%;
      }

      #title {
        position: absolute; left: 0; right: 0; top: 150px;
        text-align: center; color: #e8b84b;
      }
      #title .t1 { font-size: 60px; letter-spacing: .25em; text-indent: .25em; }
      #title .t2 { margin-top: 26px; font-size: 30px; letter-spacing: .35em; text-indent: .35em; color: #b79a5f; }

      @font-face { font-family: 'KaiTi'; src: local('KaiTi'), local('STKaiti'), local('楷体'); }
      @font-face { font-family: 'STKaiti'; src: local('STKaiti'), local('KaiTi'); }
      @font-face { font-family: 'SimSun'; src: local('SimSun'), local('宋体'); }

      #caption-wrap {
        position: absolute; left: 0; right: 0; top: 50%;
      }
      .cue {
        position: absolute; left: 0; right: 0; text-align: center;
        top: -60px;
      }
      .cue .ch {
        display: inline-block;
        font-size: 76px; color: #dfe3ea; letter-spacing: .14em;
        text-shadow: 0 2px 12px rgba(0,0,0,.7);
      }

      /* 底部整句字幕：渐变暗条 + 字幕 */
      #subshade {
        position: absolute; left: 0; right: 0; bottom: 0; height: 230px;
        background: linear-gradient(transparent, rgba(5,8,15,.5) 42%, rgba(5,8,15,.88));
      }
      #subbar {
        position: absolute; left: 0; right: 0; bottom: 96px; text-align: center;
      }
      .sub {
        position: absolute; left: 60px; right: 60px; text-align: center;
        font-size: 40px; color: #eef1f6; letter-spacing: .12em;
        opacity: 0;
        text-shadow: 0 2px 14px rgba(0,0,0,.85);
      }

      #endcard {
        position: absolute; left: 0; right: 0; top: 44%;
        text-align: center; color: #e8b84b;
      }
      #endcard .e1 { font-size: 58px; letter-spacing: .25em; text-indent: .25em; }
      #endcard .e2 { margin-top: 34px; font-size: 30px; letter-spacing: .3em; text-indent: .3em; color: #9aa3b2; }"""

# ---------- 标题卡 / 结尾卡 body ----------
TITLE_HTML = (
    '      <div id="title" class="clip" data-start="0" data-duration="3.4" '
    'data-track-index="1">\n'
    '        <div class="t1">般若波罗蜜多心经</div>\n'
    '        <div class="t2">唐三藏法师玄奘译</div>\n'
    '      </div>'
)

ENDCARD_HTML = (
    '      <div id="endcard" class="clip" data-start="69.9" data-duration="1.6" '
    'data-track-index="1">\n'
    '        <div class="e1">般若波罗蜜多心经 · 终</div>\n'
    '        <div class="e2">叶扬　敬诵</div>\n'
    '      </div>'
)

BG_VIDEO = (
    '      <video id="bgvideo" class="clip" data-start="0" '
    'data-duration="%.1f" data-track-index="3"\n'
    '             src="media/bg.mp4" muted playsinline preload="auto"></video>'
    % TOTAL
)

# ---------- 标题动效（含 caption-wrap 上移） ----------
TITLE_JS = """      // 标题入场/退场，字幕区随之上移到画面正中
      tl.from('#title', { opacity: 0, y: 30, duration: 1.2, ease: 'power2.out' }, 0);
      tl.to('#title', { opacity: 0, y: -40, duration: 0.8, ease: 'power2.in' }, 2.6);
      tl.fromTo('#caption-wrap', { y: 151 }, { y: 0, duration: 1.2, ease: 'power2.inOut' }, 2.6);"""

ENDCARD_JS = ("      // 结尾卡淡入\n"
              "      tl.from('#endcard', { opacity: 0, duration: 0.8, "
              "ease: 'power2.out' }, 70.0);")

# ---------- 中央逐字 + 底部整句 ----------
center = center_char_clips(cues, chars, THEME.accent)
sent = sentence_track(cues)

# ---------- 组装 ----------
body = "\n".join([
    BG_VIDEO,
    '      <div id="bgveil"></div>',
    '      <div id="halo2"></div>',
    '      <div id="halo"></div>',
    "",
    audio_tag("media/xinjing-yeyang-v3.wav", AUDIO_DUR),
    "",
    TITLE_HTML,
    "",
    '      <div id="caption-wrap">',
    center.html,
    '      </div>',
    "",
    '      <div id="subshade"></div>',
    '      <div id="subbar">',
    sent.html,
    '      </div>',
    "",
    ENDCARD_HTML,
])
js = "\n".join([
    TITLE_JS,
    "",
    sent.js,
    "",
    ENDCARD_JS,
    "",
    center.word_js,
])

html = render_page(total=TOTAL,
                   css=assemble_css(THEME, PROJECT_CSS,
                                   with_scene=False, with_subtitle=False),
                   body=body, js=js, body_lead_blank=False)
io.open(P.index_html, "w", encoding="utf-8").write(html)
print("已生成 index.html（%.1f 秒，中央 %d 字，整句 %d 条）"
      % (TOTAL, len(chars), len(cues)))
