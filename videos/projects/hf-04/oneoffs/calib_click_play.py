# -*- coding: utf-8 -*-
"""hf-04 实拍标定·Play 点击冒烟：过双闸点 Preview Play，录 3s，
抽首/末帧供目验时间码是否走动（命中＝00:03，点偏＝停在 00:00）。
验完 reload Studio 复原到 s0 初态。必须在 calib_setup 之后跑（沙盒 s0）。
"""
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HF03 = os.path.join(HERE, "..", "..", "hf-03", "oneoffs")
sys.path.insert(0, HF03)
sys.path.insert(0, HERE)

import rec_automate as r  # noqa: E402
import guard             # noqa: E402
import cdp_ctrl          # noqa: E402
import record_segments as R  # noqa: E402

OUT = r"F:\_hftest\hf04-rec\calib"
os.makedirs(OUT, exist_ok=True)

studio, player = R.ensure_edge()
hwnd = R.edge_foreground_hwnd(studio)   # activate＋摆窗＋前台/落点双闸
print("edge hwnd:", hwnd, "→ click", R.PLAY_X, R.PLAY_Y)
guard.assert_fg_isolated()
R.safe_click(R.PLAY_X, R.PLAY_Y)

mp4 = os.path.join(OUT, "calib-play.mp4")
subprocess.run(["node", R.SCREEN_REC, mp4,
                "--width", "1600", "--height", "920",
                "--x", "0", "--y", "0", "--duration", "3"], check=True)
first = os.path.join(OUT, "calib-play-0.png")
last = os.path.join(OUT, "calib-play-1.png")
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", mp4, "-frames:v", "1", first], check=True)
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-sseof", "-0.1", "-i", mp4, "-frames:v", "1", last], check=True)
# 裁时间码带（控制条左侧）便于目验
for tag in ("0", "1"):
    src = os.path.join(OUT, "calib-play-%s.png" % tag)
    crop = os.path.join(OUT, "calib-tc-%s.png" % tag)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", src, "-vf", "crop=300:44:400:406", crop], check=True)
print("wrote calib-tc-0.png / calib-tc-1.png（末帧应显示 00:03）")

# 复原：Studio reload 回 s0 编译初态
cdp_ctrl.reload_tab(studio)
time.sleep(7.0)
print("studio reloaded, 复原完成")
