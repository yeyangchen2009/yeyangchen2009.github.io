# -*- coding: utf-8 -*-
"""hf-05 · 从 20 take 切分镜短片＋定格帧（沿 hf-03/hf-04 体例，#567 精切阶段）。

两阶段：
  python oneoffs/cut_shorts.py frames   抽 PROBE 点帧拼 contact sheet 目验
  python oneoffs/cut_shorts.py cut      按 CUTS 帧精确重编码（crf18）到
                                       media/shorts/，并抽定格 PNG 到 freezes/

前置：母带在录制机 F:\\_hftest\\hf05-rec\\takes\\，开切前复制到仓库
gitignored 目录（不入 git）：
  mkdir videos\\projects\\hf-05\\media
  copy F:\\_hftest\\hf05-rec\\takes\\*.mp4 videos\\projects\\hf-05\\media\\

硬闸（hf-04 VFR 16 崩教训）：gdigrab 原始段必 VFR，精切必须 -vf fps=30
强制 CFR＋-g 30 -keyint_min 30＋+faststart；shorts 逐个过 probe-fps
（avg_frame_rate 30/1 才准进 render）。1600×920@30，crf18 屏幕视觉无损。

take→shorts 映射（STORYBOARD-FRAMEWORK 第 2/4 节锁定，切点目验后回填 CUTS）：
  t1-check-good        → check-good
  t2a-dur-del          → dur-del
  t2b-dur-run          → dur-run
  t3a-overflow-run     → overflow-run
  t3b-root-fix-npp ＋ t3c-root-fix-run → root-fix（必要时拆 edit/run 两名）
  t4a-color-bad-npp ＋ t4b-color-bad-run → color-bad
  t4c-color-fix-npp ＋ t4d-color-fix-run → color-fix；t4d 尾 → errlvl-zero
  t5a-same-track-run   → same-track-run
  t5b-dom-swap         → dom-swap
  t5d0-occlude-code ＋ t5d-occlude-run → occlude-run
  t6a-nulltarget-code ＋ t6b-nulltarget-run → nulltarget-run
  t7a-kf → kf；t7b-inspect → inspect-dep；t7c-beats → beats
（t5c-dom-swap-run 是对调后复绿的备用尾帧，按口播节奏决定并入 dom-swap
还是单切；s3-contrast 备份态未录，叙事走 t4 现场改色。）
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

# ---- 第一轮：稀疏时间地图（母带到齐后跑；目验后按需加密）----
# 时长＝record_segments.record(...) 实参：check 系 34s（6+CHECK_WAIT28），
# t4d 40s，t7a 39s，t7b 25s，t7c 17s，t5b 17s，t3b 14s，t4c/t2a 12s，
# t4a 11s，静场 code 系 6s。
PROBE = {
    "t1-check-good":      [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t2a-dur-del":        [0.3, 2, 4, 6, 8, 10, 11.5],
    "t2b-dur-run":        [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t3a-overflow-run":   [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t3b-root-fix-npp":   [0.3, 2, 4, 6, 8, 10, 12, 13.5],
    "t3c-root-fix-run":   [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t4a-color-bad-npp":  [0.3, 2, 4, 6, 8, 10],
    "t4b-color-bad-run":  [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t4c-color-fix-npp":  [0.3, 2, 4, 6, 8, 10, 11.5],
    "t4d-color-fix-run":  [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39],
    "t5a-same-track-run": [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t5b-dom-swap":       [0.3, 2, 4, 6, 8, 10, 12, 14, 16],
    "t5c-dom-swap-run":   [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t5d0-occlude-code":  [0.3, 2, 4, 5.5],
    "t5d-occlude-run":    [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t6a-nulltarget-code": [0.3, 2, 4, 5.5],
    "t6b-nulltarget-run": [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t7a-kf":             [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 38],
    "t7b-inspect":        [0.3, 3, 6, 9, 12, 15, 18, 21, 24],
    "t7c-beats":          [0.3, 3, 6, 9, 12, 14, 16],
}

# ---- 第二轮：定稿切点（contact sheet 目验后回填；粗切宁长勿短）----
# id: (take, 源内起, 源内止, freeze_at)
CUTS = {
    # "# 567 目验后回填，shorts 名见模块 docstring 映射表": None,
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
    FREEZES.mkdir(parents=True, exist_ok=True)
    for cid, (take, s, e, fat) in CUTS.items():
        src = MEDIA / (take + ".mp4")
        out = SHORTS / (cid + ".mp4")
        # -vf fps=30 强制 CFR 并重建 PTS：gdigrab 源帧时间戳抖动，不重建则
        # hyperframes 据 avg_frame_rate 误判 VFR，33 路并发抽帧会崩
        # （hf-03/hf-04 实证）。-g 30 -keyint_min 30 每秒一个 IDR，消 sparse
        # keyframes warning；+faststart 便回放。
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
