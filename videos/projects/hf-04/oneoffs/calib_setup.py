# -*- coding: utf-8 -*-
"""hf-04 实拍标定·第一步（零键鼠注入）：

起隔离 Edge（9222）＋保证 Studio/裸 player 两 tab，沙盒置 s0，reload Studio，
把窗口摆到 (0,0,1600,920)，gdigrab 截一帧全屏（与录屏完全同坐标系），
并打印窗口/客户区 rect 供人工量 Play 按钮中心、核算 PLAY_X/Y。
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

# 1. 沙盒置 s0（静态 clips 态）；启 Edge＋两 tab（返回的是 tab id 字符串）
R.reset("s0")
studio, player = R.ensure_edge()
print("studio id:", studio)
print("player id:", player)

# 2. reload Studio，等 composition 起来
cdp_ctrl.reload_tab(studio)
time.sleep(7.0)

# 3. 窗口摆 (0,0,1600,920) 并前置（仅 activate/move，不注入键鼠）
#    CDP activate 在用户主 Edge 挡前台时抢不过前台锁，故按 pid 定窗强前置
cdp_ctrl.browser_activate(studio)  # Studio tab 置为窗内活动 tab
time.sleep(0.8)
hwnd = guard.force_isolated_edge_foreground()
r.u.ShowWindow(hwnd, r.SW_RESTORE)
r.move(hwnd, R.WND_X, R.WND_Y, R.WND_W, R.WND_H)
time.sleep(0.4)
r.activate(hwnd)
time.sleep(0.6)
guard.assert_fg_isolated()


class RECT(r.ctypes.Structure):
    _fields_ = [("left", r.wintypes.LONG), ("top", r.wintypes.LONG),
                ("right", r.wintypes.LONG), ("bottom", r.wintypes.LONG)]


wrect = RECT()
r.u.GetWindowRect(hwnd, r.ctypes.byref(wrect))
print("window rect:", (wrect.left, wrect.top, wrect.right, wrect.bottom),
      "size:", (wrect.right - wrect.left, wrect.bottom - wrect.top))
pt = r.wintypes.POINT(0, 0)
r.u.ClientToScreen(hwnd, r.ctypes.byref(pt))
print("client origin (screen):", (pt.x, pt.y))

# 4. 走真实录屏链路：screen-rec.js 按 (0,0,1600,920) 录 1.5s 再抽末帧，
#    与正式 take 完全同坐标（直接 ffmpeg desktop 会忽略输出端区域选项抓全屏）
rec_mp4 = os.path.join(OUT, "calib-rec.mp4")
screen_png = os.path.join(OUT, "calib-screen.png")
subprocess.run(["node", R.SCREEN_REC, rec_mp4,
                "--width", "1600", "--height", "920",
                "--x", "0", "--y", "0", "--duration", "1.5"], check=True)
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-sseof", "-0.2", "-i", rec_mp4,
                "-frames:v", "1", screen_png], check=True)
print("wrote", screen_png)
print("window WND_X/Y/W/H =", R.WND_X, R.WND_Y, R.WND_W, R.WND_H)
print("current PLAY_X/Y =", R.PLAY_X, R.PLAY_Y)
print("目验：录区右缘/下缘须全暗窗无穿帮；Play 三角中心核对 PLAY_X/Y")
