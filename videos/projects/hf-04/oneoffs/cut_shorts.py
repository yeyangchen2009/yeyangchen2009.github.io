# -*- coding: utf-8 -*-
"""hf-04 · 从 12 take 切分镜短片＋定格帧（素材先行第⑥步，沿 hf-03 体例）。

两阶段：
  python oneoffs/cut_shorts.py frames   抽 PROBE 点帧拼 contact sheet 目验
  python oneoffs/cut_shorts.py cut      按 CUTS 帧精确重编码（crf18）到
                                       media/shorts/，并抽定格 PNG

seg8（console-seek）掐尾：实际 seek 动作约 0–59.8s，之后空提示符静场
（RECORD-NOTES 坑⑤，DevTools 关闭落在 ~71s 录区外）。
1600×920@30 gdigrab；-ss/-to 重编码 crf18（屏幕录制视觉无损）。
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MEDIA = ROOT / "media"
FRAMES = ROOT / "build" / "frames"
SHORTS = MEDIA / "shorts"
FREEZES = MEDIA / "freezes"

# ---- 第一轮：稀疏时间地图（目验后加密回填）----
PROBE = {
    "rec-play-static":  [0.3, 1, 2, 3, 4.5, 6, 7.5, 9, 10.5, 12],
    "rec-css-keyframes": [0.3, 1, 2.5, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 25.5],
    "rec-play-css":     [0.3, 1, 2, 3, 4.5, 6, 7.5, 9, 10.5, 12],
    "rec-snap-css":     [round(x * 4.0, 1) for x in range(1, 22)],       # 4–84
    "rec-timer-code":   [0.3, 1, 2.5, 4, 6, 8, 10, 12, 14, 16, 17.5],
    "rec-play-timer":   [0.3, 1, 2, 3, 4.5, 6, 7.5, 9, 10.5, 12],
    "rec-snap-timer":   [round(x * 5.0, 1) for x in range(1, 34)],       # 5–165
    "rec-check-pass":   [round(1 + x * 2.5, 1) for x in range(12)],      # 3.5–30.5
    "rec-gsap-three":   [round(0.5 + x * 3.0, 1) for x in range(16)],    # 0.5–45.5
    "rec-play-final":   [0.3, 1, 2, 3, 4.5, 6, 7.5, 9, 10.5, 12],
    "rec-console-seek": [round(0.5 + x * 4.0, 1) for x in range(18)],    # 0.5–68.5
    "rec-render":       [round(1 + x * 4.0, 1) for x in range(21)],      # 1–81
}

# ---- 第二轮：定稿切点（14 张 contact sheet 目验后回填，2026-10-14）----
# 粗切宁长勿短：每段预留拍前/拍后余量，精调交给 make_video 的
# data-start/data-duration。freeze_at 取信息最完整的尾帧。
# 叙事顺序即字典序（L3 承上 → … → L55 render）。
# id: (take, 源内起, 源内止, freeze_at)
CUTS = {
    # —— L3 承上：打开上集成果，静态标题「抨一下处在那」——
    "play-static":     ("rec-play-static",    0.3, 12.8, 10.5),
    # —— L9 前半：NPP 里敲 @keyframes flyin（透明/y60/0.8s 归位）——
    "css-kf-mid":      ("rec-css-keyframes", 13.5, 21.0, 20.5),
    "css-kf-done":     ("rec-css-keyframes", 21.0, 25.8, 25.3),
    # —— L9 尾/L11：回浏览器点播放，标题飞进来——
    "play-css":        ("rec-play-css",       0.3, 12.8,  9.0),
    # —— L17/L19：snapshot 三时刻 → saved → fc 逐字节「找不到差异」——
    "snap-css-cmd":    ("rec-snap-css",      27.0, 41.0, 38.0),
    "snap-css-run":    ("rec-snap-css",      47.0, 62.0, 60.5),
    "snap-css-eq":     ("rec-snap-css",      62.0, 72.5, 68.0),
    # —— L25：补计数器 setInterval 半秒一加；浏览器里跳得欢——
    "timer-code-mid":  ("rec-timer-code",     5.0, 10.0,  8.5),
    "timer-code-done": ("rec-timer-code",    13.5, 17.8, 17.0),
    "play-timer":      ("rec-play-timer",     0.3, 12.7,  9.0),
    # —— L27 race：排队 ser-1/2/3＝tick3/3/4（2 种）——
    "race-q-cmd":      ("rec-snap-timer",     4.0, 11.0,  9.0),
    "race-q-run":      ("rec-snap-timer",    13.0, 47.0, 42.0),
    "race-q-done":     ("rec-snap-timer",    49.0, 58.0, 54.0),
    # —— L27 race：6 路齐发 → tick4/6/7（3 种），总结行——
    "race-f-start":    ("rec-snap-timer",    58.0, 78.0, 75.0),
    "race-f-done":     ("rec-snap-timer",    92.0,112.0,108.0),
    # —— L29 尾：check 全绿，但守门员查不出不可定位——
    "check-run":       ("rec-check-pass",    15.0, 24.0, 22.0),
    "check-pass":      ("rec-check-pass",    24.5, 30.5, 27.0),
    # —— L33–L41：GSAP 三件事；html 段配「Main 是 #root 的 composition-id」——
    # register 起点 40.0：注册行源 41s 才敲入（35.5 窗内只有三条 fromTo）；
    # freeze 45.0 实证同屏含 window.__timelines 注册行＋tl.seek(0)（行42/43）。
    "gsap-html":       ("rec-gsap-three",     0.3,  7.0,  5.5),
    "gsap-paused":     ("rec-gsap-three",    13.5, 19.5, 17.0),
    "gsap-fromto":     ("rec-gsap-three",    26.0, 34.5, 33.0),
    "gsap-register":   ("rec-gsap-three",    40.0, 45.8, 45.0),
    # —— L45：三行凑齐回浏览器，2s 标题/3s 卡片/6s 副标题——
    "play-final":      ("rec-play-final",     0.3, 12.7, 11.0),
    # —— L47：DevTools 亲手播，window.__player＋seek 矩阵（掐尾在 58s）——
    # 源时间轴全分辨率帧实证（build/probe2，2026-10-14 二轮标定）：
    # 8.5 DevTools 开；19.8 前空台（12–15 有试探敲＋resize toast，弃用）；
    # 20.0–21.4 a 拍敲入 seek(2.4)（cs-player 取打字前半露 __player 全字样）；
    # b seek(3) 25–27；c seek(6.3) 30–32；d seek(9) 35.5–36.5；e seek(0)
    # 41–42.5 敲入、43.5 空舞台；f–j 五回 2.4 在 46.2–57.7（Edge 折叠重复
    # 历史，控制台始终只显一行 seek(2.4)，「五回」靠反复敲入动作表达）；
    # 57.8 起又有敲键，cs-five 止于 57.9。
    "cs-open":         ("rec-console-seek",   8.8, 11.2, 10.5),
    "cs-player":       ("rec-console-seek",  19.8, 21.4, 20.7),
    "cs-s24":          ("rec-console-seek",  21.4, 24.2, 23.6),
    "cs-s3":           ("rec-console-seek",  24.6, 27.8, 27.4),
    "cs-s63":          ("rec-console-seek",  30.0, 33.4, 33.0),
    "cs-s9":           ("rec-console-seek",  34.8, 37.2, 36.8),
    "cs-s0":           ("rec-console-seek",  40.0, 43.8, 43.2),
    "cs-five":         ("rec-console-seek",  46.2, 57.9, 57.7),
    # —— L55：render 300 帧实打 39s，烤成 mp4——
    "render-cmd":      ("rec-render",         4.0, 14.0, 12.0),
    "render-run":      ("rec-render",        24.0, 56.0, 50.0),
    "render-done":     ("rec-render",        60.5, 70.0, 66.0),
}


def run(cmd):
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def phase_frames():
    FRAMES.mkdir(parents=True, exist_ok=True)
    for take, pts in PROBE.items():
        sheet_dir = FRAMES / take
        sheet_dir.mkdir(exist_ok=True)
        thumbs = []
        for t in pts:
            out = sheet_dir / ("%s_%05.1f.png" % (take, t))
            thumbs.append(out)
            if out.exists():
                continue
            run(["ffmpeg", "-y", "-loglevel", "error",
                 "-ss", str(t), "-i", str(MEDIA / (take + ".mp4")),
                 "-frames:v", "1", "-vf", "scale=480:276", str(out)])
        stamped = sheet_dir / "stamped"
        stamped.mkdir(exist_ok=True)
        stamped_files = []
        for t, thumb in zip(pts, thumbs):
            s = stamped / ("%05.1f.png" % t)
            stamped_files.append(s)
            if not s.exists():
                run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(thumb),
                     "-vf", ("drawtext=text='%s':x=10:y=8:fontsize=26:"
                             "fontcolor=yellow:box=1:boxcolor=black@0.6") % t,
                     str(s)])
        per, idx = 24, 0
        for i in range(0, len(stamped_files), per):
            batch = stamped_files[i:i + per]
            listfile = sheet_dir / ("_list%d.txt" % idx)
            listfile.write_text("\n".join("file '%s'" % f.as_posix()
                                          for f in batch), encoding="utf-8")
            sheet = FRAMES / ("sheet-%s-%d.png" % (take, idx))
            run(["ffmpeg", "-y", "-loglevel", "error",
                 "-f", "concat", "-safe", "0", "-i", str(listfile),
                 "-vf", "tile=6x4:margin=4:padding=4:color=black",
                 "-frames:v", "1", str(sheet)])
            idx += 1
        print("sheet-%s：%d 帧（%d 张）" % (take, len(pts), idx))


def phase_cut():
    if not CUTS:
        sys.exit("CUTS 为空：先 frames 目验，再回填切点")
    SHORTS.mkdir(parents=True, exist_ok=True)
    FREEZES.mkdir(parents=True, exist_ok=True)
    for cid, (take, s, e, fat) in CUTS.items():
        src = MEDIA / (take + ".mp4")
        out = SHORTS / (cid + ".mp4")
        # -vf fps=30 强制 CFR 并重建 PTS：gdigrab 源帧时间戳抖动，精切后
        # avg_frame_rate 会掉到 5–24（r 仍 30/1），hyperframes 据 |r-avg|/r>10%
        # 误判 VFR → 走 rawvideo NUT 双管道抽帧，33 路并发时 16 路 ffmpeg
        # 一帧未写即崩（hf-03 仅 13 路侥幸过；2026-10-14 hf-04 render 实证）。
        # -g 30 -keyint_min 30：每秒一个 IDR，消 compile 期 sparse keyframes
        # warning（默认 GOP 250 时 8s 段仅开头一个关键帧）；+faststart 便回放。
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(s), "-to", str(e), "-i", str(src),
             "-vf", "fps=30",
             "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
             "-g", "30", "-keyint_min", "30", "-movflags", "+faststart",
             "-an", str(out)])
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(fat if fat is not None else e - 0.05),
             "-i", str(src), "-frames:v", "1", str(FREEZES / (cid + ".png"))])
        print("cut %-18s %s  %.2f–%.2f (%.2fs)" % (cid, take, s, e, e - s))


if __name__ == "__main__":
    {"frames": phase_frames, "cut": phase_cut}[
        sys.argv[1] if len(sys.argv) > 1 else "frames"]()
