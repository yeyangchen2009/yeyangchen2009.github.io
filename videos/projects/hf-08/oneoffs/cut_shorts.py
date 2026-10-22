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

切点设计（与 make_video.py VIDEOS 的 data-media-start 严格配套，2026-10-22
录制日真机回填；sw 待冷态 t0）：short 必须从母带 0 点整段切，data-media-start
直接是母带源内秒（不是 short 内偏移）：
  sw-render.mp4   ← t0-sw  0.0–146.0 rec-sw1 源内 ≈8.0（打字段，冷态 sheet 校）
                                    ＋rec-sw2 源内 ≈144.0（尾报前进行段，校）
  hw-render.mp4   ← t1-hw  0.0–83.5  rec-hw1 源内 8.0–12.8（cls→打字→回车）
                                    ＋rec-hw2 源内 73.0–79.8（52%→92%
                                    Streaming 245→357/390；尾报 85s＝54.2s）
  hash6-run.mp4   ← t2-hash 0.0–25.2 rec-hash6 源内 16.0–23.9（PS 提示→
                                    打字→21.8s 六行同值表全出）
  badlint-run.mp4 ← t3-badlint 0.0–28.5 rec-badlint 源内 18.5–26.8（命令→
                                    横幅→Lint 2 error 1 warning/Continuing
                                    →25% capture 照烤；尾报 157s＝2m8.0s）
中间不播的大段（hw npx 前置、t3 两轮 45s 死等）留在文件里无妨，clip 只播
data-media-start 起 data-duration 的区间。

区间必须全是设计画面（打字/横幅/滚动计时/结果表）、无意外残屏，
data-media-start 偏差 ≤0.1s。

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
# 母带时长＝2026-10-22 录制日真机（RECORD-NOTES 第十一节）：
# t1-hw 87.8（第三轮，尾报 85–86s＝rendered in 54.2s）／t2-hash 25.3
# （表 21–24s）／t3-badlint 159.7（横幅≈19–23s，尾报 128–132s＝2m8.0s）／
# t4-strict 80.3、t5-missing 28.8 不出 short（尾帧走 tail-freeze）。
# t0-sw 冷态未录（重启后第一件事补），布点保留，母带缺位时 frames 自动跳过。
PROBE = {
    "t0-sw":    [0.3, 2, 4, 6, 7, 8, 9, 10, 11, 12, 30, 60, 90, 120,
                 130, 134, 137, 139, 141, 143, 145, 148, 152, 156],
    "t1-hw":    [0.3, 2, 4, 6, 7, 8, 9, 10, 11, 12,
                 27, 28, 29, 30, 31, 32,
                 44, 48, 52, 56, 60, 64, 68, 70, 72, 74, 76, 78, 80,
                 82, 83, 84, 85, 86, 87],
    "t2-hash":  [0.3, 2, 4, 5, 6, 7, 8, 15, 16, 17, 18, 18.8, 19.5,
                 20.2, 20.8, 21.3, 21.8, 22.3, 22.8, 23.3, 23.8,
                 24.3, 24.8],
    "t3-badlint": [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 17.5, 18.5, 19.5,
                   20.5, 21.5, 22.5, 23.5, 24.5, 25.5, 26.5, 27.5,
                   126, 128, 130, 132, 134, 140, 150, 157],
}

# ---- 第二轮：定稿切点（stamped sheet 目验后回填微调）----
# id: (take, 源内起, 源内止)。均从母带 0 点切（data-media-start 用源内秒）。
# data-duration 是与口播音频对齐的定稿值不动，只平移 data-media-start。
# 止点包住最长播放窗口＋余量；sw 待冷态 t0（二切窗口预计 137–143s）。
CUTS = {
    "sw-render":   ("t0-sw", 0.0, 146.0),
    "hw-render":   ("t1-hw", 0.0, 83.5),
    "hash6-run":   ("t2-hash", 0.0, 25.2),
    "badlint-run": ("t3-badlint", 0.0, 28.5),
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
        if not src.exists():
            print("跳过 %s（母带 %s 缺位——sw 等冷态 t0 重录后补切）"
                  % (cid, src.name))
            continue
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
