# -*- coding: utf-8 -*-
"""生成 index.html（起点骨架：替换 SCENES / project_css / SCENE_JS）。

深模块约定：本文件只写"本片独有"的东西——分镜 body、场景专属 CSS、
场景动画 JS；页面骨架、主题、字幕、场景 clip 外壳全部复用 videopipe。
"""
import io
import sys
from pathlib import Path

# projects/<name>/make_video.py -> videos/ 在 parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (ProjectPaths, load_cues, Scene, render_scenes,
                       scene_fade_js, char_track, assemble_css,
                       render_page, audio_tag, DARK_GOLD_GH)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

data = load_cues(P.cues_json)
cues, chars, total = data["cues"], data["chars"], data["duration"]
THEME = DARK_GOLD_GH

# ---- 本片分镜：Scene(id, start, end, body)；body 逐片手写 ----
SCENES = [
    Scene("sc-hello", 0.0, total, """
          <div style="position:absolute;left:0;right:0;top:42%;text-align:center;
               font-size:120px;color:%s;letter-spacing:.2em;">新片开场</div>
""" % THEME.accent),
]

# ---- 场景专属 CSS（S1…Sn 规则；通用骨架/字幕由 theme 拼） ----
PROJECT_CSS = ""

# ---- 场景动画 JS（时间一律显式给秒；淡变针对 #id > .scene-inner） ----
SCENE_JS = scene_fade_js("sc-hello", in_at=0.0, out_at=round(total - 0.5, 2))

# ---- 底部字幕轨道 ----
frag = char_track(cues, chars, THEME.accent)

# ---- 组装 ----
body = "\n".join([
    audio_tag("media/audio.wav", total),
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
