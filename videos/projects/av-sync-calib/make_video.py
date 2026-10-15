# -*- coding: utf-8 -*-
"""音画偏移标定片（hf-05 路径 C 第一步）。

不讲故事、不取音、不挂字幕：整片 13s 黑底，t=3/5/7/9/11s 各有一次
0.1s（3 帧）全屏白闪，同时 media/beeps.wav 在同一时刻给出 1kHz/60ms
窄脉冲。渲染后逐帧测亮度突变沿、对音频做能量 onset，两者配对即得
「画面时间 vs 声音时间」的实测偏移，给后续整片 time_offset 定标用。

事件时刻刻意从 3s 起：finalize --intro 会裁掉正片头 2s，裁完首事件
恰落在终片 1s，body 版与终片版可同方案测量、拆出拼接延迟。
"""
import io
import sys
from pathlib import Path

# projects/<name>/make_video.py -> videos/ 在 parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from videopipe import (
                       DARK_GOLD_GH,
                       ProjectPaths,
                       Scene,
                       assemble_css,
                       audio_tag,
                       render_page,
                       render_scenes,
)

P = ProjectPaths.at(Path(__file__).resolve().parent)
P.ensure()

TOTAL = 13.0
EVENTS = [3.0, 5.0, 7.0, 9.0, 11.0]   # 白闪 + BEEP 同一时刻
FLASH = 0.1                           # 秒＝3 帧@30fps，纯 display 切换无渐变

# ---- 黑底：track 0 全程；root 自身近黑，显式铺纯黑把对比拉满 ----
black = (
    '      <div id="bg" class="clip" data-start="0.00" data-duration="%.3f" '
    'data-track-index="0" style="position:absolute;inset:0;background:#000;">'
    '</div>' % TOTAL
)

# ---- 白闪：track 1，clip 原生显隐是最锐利的亮度跳变（不用 GSAP） ----
SCENES = [
    Scene("flash-%d" % i, t, round(t + FLASH, 3),
          '<div style="position:absolute;inset:0;background:#fff;"></div>')
    for i, t in enumerate(EVENTS)
]

body = "\n".join([
    audio_tag("media/beeps.wav", TOTAL),
    "",
    black,
    "",
    render_scenes(SCENES),
])

html = render_page(total=TOTAL,
                   css=assemble_css(DARK_GOLD_GH, ""),
                   body=body, js="")
io.open(P.index_html, "w", encoding="utf-8").write(html)
print("已生成标定片 index.html（%.0fs，%d 个事件）" % (TOTAL, len(EVENTS)))
