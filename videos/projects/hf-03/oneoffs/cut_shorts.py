# -*- coding: utf-8 -*-
"""hf-03 · 从 7 个长 take 切分镜短片＋定格帧（素材先行第⑥步工具）。

两阶段：
  python oneoffs/cut_shorts.py frames
      按 PROBE 点从 media/rec-*.mp4 抽缩放帧，拼 contact sheet 到 build/frames/，
      人工目验后把定稿切点写入 CUTS。
  python oneoffs/cut_shorts.py cut
      按 CUTS 重编码切短片（帧精确，crf18）到 media/shorts/，并从每片末点
      （或指定 freeze 点）抽定格 PNG 到 media/freezes/。

录屏 1600x920@30 gdigrab；stream copy 的 -ss 落在最近关键帧不精确，
一律 libx264 重编码（源是屏幕录制、crf18 视觉无损）。
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

# ---- 目验点：take -> [秒…]（粗窗来自 REC-NOTES，密集 0.5–1s 采样） ----
PROBE = {
    "rec-attrs-cdn": [0.5, 3.0, 3.6, 4.2, 5.0, 5.8, 6.6, 7.4, 7.8, 8.4, 9.2,
                      10.0, 10.8, 11.4, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0,
                      18.0, 19.0, 20.0, 20.8, 24.0],
    "rec-title-time": [0.5, 3.0, 4.5, 5.5, 6.0, 8.4, 9.0, 9.8, 10.8, 11.6,
                       12.4, 13.2, 14.0, 15.0, 15.8, 16.4, 17.0, 18.0, 19.2,
                       20.0, 23.0],
    "rec-play": [0.2, 1.0, 2.0, 2.4, 3.0, 4.0, 4.4, 5.0, 5.7, 6.5, 7.5, 8.3,
                 8.6, 9.2, 10.0, 10.8, 11.5],
    "rec-stack": [0.5, 2.0, 3.6, 4.5, 5.6, 6.5, 7.5, 8.6, 9.2, 10.0, 11.0,
                  11.8, 12.5, 16.5, 17.5, 18.5, 19.5, 20.5, 21.0, 21.8, 22.8,
                  23.6, 26.5, 27.2, 27.8, 28.5, 29.2, 29.8, 30.3, 30.8, 31.5,
                  32.2, 33.0, 33.8, 34.2, 35.5, 36.2, 36.8, 37.5, 38.2, 38.8,
                  39.4, 40.0, 42.0, 42.8, 43.5, 44.2, 45.0, 45.8, 46.4, 47.5,
                  49.0],
    "rec-check-fail": [1.0, 3.0, 3.6, 5.0, 8.0, 33.0, 34.0, 34.6, 35.0,
                       35.6, 36.5, 40.0, 44.0],
    "rec-allow-overlap": [0.5, 2.0, 3.2, 4.5, 5.5, 6.2, 7.0, 7.8, 8.6, 9.2,
                          9.6, 10.2, 11.0, 13.0],
    "rec-check-pass": [1.0, 3.0, 3.6, 5.0, 8.0, 33.0, 34.0, 34.6, 35.0,
                       35.6, 36.5, 40.0, 44.0],
}

# ---- 定稿切点（frames 目验后回填，2026-10-11）----
# id: (take, start, end, freeze_at)
# 成片映射（start 为成片音频秒，在 make_video.py VIDEOS 中用）：
#  attrs-a  37.10  attrs-b 83.46  title-a 103.30  play 115.60
#  stack-a 131.30  stack-b 138.60 stack-c 146.80  stack-d 163.30
#  stack-e 175.00  stack-f 185.70 fail 238.30     allow 264.30  pass 269.40
CUTS = {
    "s-attrs-a": ("rec-attrs-cdn", 3.8, 8.0, 7.8),
    "s-attrs-b": ("rec-attrs-cdn", 12.0, 20.6, 20.4),
    "s-title-a": ("rec-title-time", 13.1, 16.2, 16.0),
    "s-play":    ("rec-play", 2.0, 9.2, 8.6),
    "s-stack-a": ("rec-stack", 5.4, 8.8, 8.4),
    "s-stack-b": ("rec-stack", 16.6, 20.7, 20.5),
    "s-stack-c": ("rec-stack", 27.6, 30.4, 30.2),
    "s-stack-d": ("rec-stack", 31.2, 32.6, 32.4),
    "s-stack-e": ("rec-stack", 34.2, 36.2, 35.9),
    "s-stack-f": ("rec-stack", 42.6, 46.0, 45.4),
    "s-fail":    ("rec-check-fail", 32.8, 36.0, 35.8),
    "s-allow":   ("rec-allow-overlap", 9.0, 11.2, 11.0),
    "s-pass":    ("rec-check-pass", 32.8, 36.0, 35.8),
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
            tag = "%05.1f" % t
            out = sheet_dir / ("%s_%s.png" % (take, tag))
            thumbs.append(out)
            if out.exists():
                continue
            run(["ffmpeg", "-y", "-loglevel", "error",
                 "-ss", str(t), "-i", str(MEDIA / (take + ".mp4")),
                 "-frames:v", "1", "-vf", "scale=480:276", str(out)])
        # 拼 tile：每张 sheet 最多 24 帧（6x4），帧上烧时间戳
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
        print("sheet:", FRAMES / ("sheet-%s-*.png（%d 帧）" % (take, len(pts))))


def phase_cut():
    if not CUTS:
        sys.exit("CUTS 为空：先 frames 目验，再回填切点")
    SHORTS.mkdir(parents=True, exist_ok=True)
    FREEZES.mkdir(parents=True, exist_ok=True)
    for cid, (take, s, e, fat) in CUTS.items():
        src = MEDIA / (take + ".mp4")
        out = SHORTS / (cid + ".mp4")
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(s), "-to", str(e), "-i", str(src),
             "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
             "-an", str(out)])
        fz = FREEZES / (cid + ".png")
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(fat if fat is not None else e - 0.05),
             "-i", str(src), "-frames:v", "1", str(fz)])
        print("cut %s  %.2f–%.2f (%.2fs)" % (cid, s, e, e - s))


if __name__ == "__main__":
    {"frames": phase_frames, "cut": phase_cut}[sys.argv[1] if len(sys.argv) > 1
                                               else "frames"]()
