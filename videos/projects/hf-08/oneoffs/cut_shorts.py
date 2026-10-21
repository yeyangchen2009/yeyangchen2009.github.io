# -*- coding: utf-8 -*-
"""hf-08 · 从 6 母带切 4 条分镜短片（沿 hf-03/04/05/06 体例）。

两阶段：
  python oneoffs/cut_shorts.py frames   抽 PROBE 点帧拼 contact sheet 目验
  python oneoffs/cut_shorts.py cut      按 CUTS 帧精确重编码（crf18）到
                                        media/shorts/

前置：母带在录制机 F:\\_hftest\\hf08-rec\\takes\\，开切前复制到仓库
gitignored 目录（不入 git）：
  mkdir videos\\projects\\hf-08\\media
  copy F:\\_hftest\\hf08-rec\\takes\\*.mp4 videos\\projects\\hf-08\\media\\

切点设计（与 make_video.py VIDEOS 的 data-media-start 严格配套）：
sw/hw 两段 clip 共用一个文件、各取源内区间——short 必须从母带 0 点整段切，
data-media-start 直接是母带源内秒（不是 short 内偏移）：
  sw-render.mp4   ← t0-sw  0.0–66.0  含 rec-sw1 源内 1.0–6.2（打字段）
                                    ＋rec-sw2 源内 60.5–65.3（尾报前的
                                    Timing 进行段，不是结论行）
  hw-render.mp4   ← t1-hw  0.0–52.0  含 rec-hw1 源内 5.0–9.8
                                    ＋rec-hw2 源内 44.5–51.3（streaming）
  hash6-run.mp4   ← t2-hash 0.0–9.2  rec-hash6 源内 0.8–8.7
  badlint-run.mp4 ← t3-badlint 0.0–9.5 rec-badlint 源内 0.5–8.8
中间不播的大段（sw 渲染 54s、t3 中段 45s 死等）留在文件里无妨，clip 只播
data-media-start 起 data-duration 的区间。

二切按真机尾报秒 T 反推（尾报精确数字不进动态录屏，口播钉死值由布景日志
freeze 作证）：sw 取 [T−7.6, T−2.8]（探针 T=68.1 对到 60.5–65.3）、
hw 取 [T−7.9, T−1.1]（T=52.4 对到 44.5–51.3）；区间必须全是滚动计时行、
无静止提示符，data-media-start 偏差 ≤0.1s。

freeze 不在本脚本抽：3 张母带尾帧（hash6-run/strict-abort/missing-audio）
由 record_segments.py tail-freeze 出，11 张回放/NPP freeze 由 freeze/freeze
-all 出；归位时 copy F:\\_hftest\\hf08-rec\\freezes\\*.png media\\freezes。

硬闸（hf-04 VFR 教训）：gdigrab 原始段必 VFR，精切必须 -vf fps=30 强制
CFR＋-g 30 -keyint_min 30＋+faststart；切完逐个过 probe-fps：
  python -m videopipe probe-fps projects/hf-08/media/t0-sw.mp4   # 必 exit 2
  python -m videopipe probe-fps projects/hf-08/media/shorts       # 必 exit 0
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MEDIA = ROOT / "media"
FRAMES = ROOT / "build" / "frames"
SHORTS = MEDIA / "shorts"

# ---- 第一轮：稀疏时间地图（母带到齐后跑；目验后按需加密）----
# 母带时长＝record(...) 实参（2026-10-21 彩排真机回填 WAIT）：
# t0-sw 75.0／t1-hw 64.0／t2-hash 22.0／t3-badlint 149.5／t4-strict 22.5／
# t5-missing 26.5（t4/t5 全程弃视频，尾帧 freeze 由 tail-freeze 抽，不布点）。
# t3 render 真机 141.2s（两轮 45000ms 等待，poll45×2），Continuing 尾报约在
# 源内 145.7s；成片只取头 8.8s，尾部点只为确认尾报已落屏。
PROBE = {
    "t0-sw":    [0.3, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 8, 10, 30, 55, 60,
                 61.5, 63, 64.5, 66, 70, 73],
    "t1-hw":    [0.3, 2, 4, 5.5, 7, 8.5, 9.8, 12, 30, 43, 45, 47, 49,
                 50.5, 52, 55, 60],
    "t2-hash":  [0.3, 1.5, 3, 4.5, 6, 7.5, 8.7, 10, 12, 14, 16, 18, 20],
    "t3-badlint": [0.3, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5,
                   138, 142, 145, 147],
}

# ---- 第二轮：定稿切点（代录 contact sheet 目验后回填微调）----
# id: (take, 源内起, 源内止)。均从母带 0 点切（data-media-start 用源内秒）。
# 止点预留 0.5–0.7s 余量，二切再收紧（data-media-start 偏差 ≤0.1s）。
CUTS = {
    "sw-render":   ("t0-sw", 0.0, 66.0),
    "hw-render":   ("t1-hw", 0.0, 52.0),
    "hash6-run":   ("t2-hash", 0.0, 9.2),
    "badlint-run": ("t3-badlint", 0.0, 9.5),
}


def run(cmd):
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def phase_frames():
    FRAMES.mkdir(parents=True, exist_ok=True)
    for take, pts in PROBE.items():
        src = MEDIA / (take + ".mp4")
        if not src.exists():
            print("跳过 %s（母带未复制到 %s）" % (take, src))
            continue
        sheet_dir = FRAMES / take
        sheet_dir.mkdir(exist_ok=True)
        thumbs = []
        for t in pts:
            out = sheet_dir / ("%s_%05.1f.png" % (take, t))
            thumbs.append(out)
            if out.exists():
                continue
            run(["ffmpeg", "-y", "-loglevel", "error",
                 "-ss", str(t), "-i", str(src),
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
        sys.exit("CUTS 为空：先 copy 母带→ frames 目验 contact sheet→回填切点")
    SHORTS.mkdir(parents=True, exist_ok=True)
    for cid, (take, s, e) in CUTS.items():
        src = MEDIA / (take + ".mp4")
        out = SHORTS / (cid + ".mp4")
        # -vf fps=30 强制 CFR 并重建 PTS：gdigrab 源帧时间戳抖动，不重建则
        # hyperframes 据 avg_frame_rate 误判 VFR（hf-03/hf-04 实证）。
        # -g 30 每秒一个 IDR 消 sparse keyframes warning。
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(s), "-to", str(e), "-i", str(src),
             "-vf", "fps=30",
             "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
             "-g", "30", "-keyint_min", "30", "-movflags", "+faststart",
             "-an", str(out)])
        print("cut %-14s %s  %.1f–%.1f (%.1fs)" % (cid, take, s, e, e - s))
    print("\n双闸：")
    print("  python -m videopipe probe-fps projects/hf-08/media/t0-sw.mp4  # 期望 exit 2")
    print("  python -m videopipe probe-fps projects/hf-08/media/shorts      # 期望 exit 0")


if __name__ == "__main__":
    {"frames": phase_frames, "cut": phase_cut}[
        sys.argv[1] if len(sys.argv) > 1 else "frames"]()
