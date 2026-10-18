# -*- coding: utf-8 -*-
"""hf-06 · 从 16 take 切分镜短片＋定格帧（沿 hf-03/04/05 体例）。

两阶段：
  python oneoffs/cut_shorts.py frames   抽 PROBE 点帧拼 contact sheet 目验
  python oneoffs/cut_shorts.py cut      按 CUTS 帧精确重编码（crf18）到
                                        media/shorts/，并抽定格 PNG 到 freezes/

前置：母带在录制机 F:\\_hftest\\hf06-rec\\takes\\，开切前复制到仓库
gitignored 目录（不入 git）：
  mkdir videos\\projects\\hf-06\\media
  copy F:\\_hftest\\hf06-rec\\takes\\*.mp4 videos\\projects\\hf-06\\media\\

硬闸（hf-04 VFR 教训）：gdigrab 原始段必 VFR，精切必须 -vf fps=30 强制
CFR＋-g 30 -keyint_min 30＋+faststart；shorts 逐个过 probe-fps
（avg_frame_rate 30/1 才准进 render）。1600×920@30，crf18 屏幕视觉无损。

take→shorts 拟用名（CUTS 待代录 contact sheet 目验后回填）：
  t0-good            → good-run（五段全绿 Check passed）
  t1a-del-id         → del-id-edit；t1b-noid-run → noid-run（FROZEN）
  t2a-del-muted      → del-muted-edit；t2b → nomuted-run
  t3a-bad-src        → bad-src-edit；t3b → badaudio-run（silent）
  t4-missing         → missing-run；t5-sametrack → sametrack-run（⚠ 但 passed）
  t6-beats           → beats-run（23 拍）；t7-norm-dry → norm-dry
  t8-norm-write      → norm-write（写回 2.371374＋withinTolerance）
  t9-ceiling         → ceiling（needs 16.0 dB）；t10-badid → badid（两条 exit1）
  t11-treatment      → treatment；t12-placeholder → placeholder-run
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
# 时长＝record_segments.record(...) 实参：check 系 34（6+CHECK_WAIT28），
# beats 24，norm/treatment 系 24（8+NORM_WAIT14+2），t8 43（两条 normalize），
# t10 49（4+TYPE5.5+NORM14+TYPE5.5+TREAT16+4，两条 exit1），t11 24，edit 系 10/12。
# 节奏：敲命令 0.3–7s、headless 分析 7–21s、报文/JSON 终态 21s 起。
PROBE = {
    "t0-good":            [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t1a-del-id":         [0.3, 2, 3.5, 5, 6.5, 8, 9.5, 11],
    "t1b-noid-run":       [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t2a-del-muted":      [0.3, 2, 3.5, 5, 6.5, 8, 9.3],
    "t2b-nomuted-run":    [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t3a-bad-src":        [0.3, 2, 3.5, 5, 6.5, 8, 9.5, 11],
    "t3b-badaudio-run":   [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t4-missing":         [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t5-sametrack":       [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "t6-beats":           [0.3, 2, 4, 6, 9, 12, 15, 18, 20, 22, 23.3],
    "t7-norm-dry":        [0.3, 3, 6, 8, 11, 14, 17, 20, 21.5, 23],
    "t8-norm-write":      [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33,
                           36, 39, 42],
    "t9-ceiling":         [0.3, 3, 6, 8, 11, 14, 17, 20, 21.5, 23],
    "t10-badid":          [0.3, 3, 6, 9, 12, 15, 18, 20, 22, 25, 28, 31,
                           34, 37, 39.5, 42, 44, 46, 47.5],
    "t11-treatment":      [0.3, 3, 6, 8, 11, 14, 17, 20, 21.5, 23],
    "t12-placeholder":    [0.3, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
}

# ---- 第二轮：定稿切点（2026-10-18 目验 build/frames/sheet-* 回填）----
# 粗切宁长勿短，make_video 阶段按幕二次裁；edit/run 拆两名给跳切自由度。
# id: (take, 源内起, 源内止, freeze_at)
# check 系（t1b/t2b/t3b/t4/t5/t12，录像 38s）：freeze 统一取 35.5——
# _run_check 滚轮 freeze 窗（约 33–36.5s）中帧，重录目验 35.5s 帧六条
# 报错原文（FROZEN/muted/voise/missing/⚠/will 404）全部入镜。
CUTS = {
    "good-run":       ("t0-good",          0.2, 33.7, 32.5),  # Check passed 同屏
    "del-id-edit":    ("t1a-del-id",       0.2, 11.7, 11.3),  # 尾帧 id 已删
    "noid-run":       ("t1b-noid-run",     0.2, 37.7, 35.5),  # FROZEN 回滚帧
    "del-muted-edit": ("t2a-del-muted",    0.2,  9.8,  9.2),  # 尾帧 muted 已删
    "nomuted-run":    ("t2b-nomuted-run",  0.2, 37.7, 35.5),  # missing_muted 回滚帧
    "bad-src-edit":   ("t3a-bad-src",      0.2, 11.7, 11.3),  # 尾帧 voise.wav
    "badaudio-run":   ("t3b-badaudio-run", 0.2, 37.7, 35.5),  # src_not_found 回滚帧
    "missing-run":    ("t4-missing",       0.2, 37.7, 35.5),  # missing×2 回滚帧
    "sametrack-run":  ("t5-sametrack",     0.2, 37.7, 35.5),  # ⚠ 全文＋passed
    "beats-run":      ("t6-beats",         0.2, 23.8, 20.0),  # Wrote 24 beats 255.3
    "norm-dry":       ("t7-norm-dry",      0.2, 23.8, 21.5),  # dry JSON 全量
    "norm-write":     ("t8-norm-write",    0.2, 42.7, 41.0),  # 幂等 withinTolerance
    "ceiling":        ("t9-ceiling",       0.2, 23.8, 21.5),  # needs 16.0 dB 长句
    "badid":          ("t10-badid",        0.2, 48.7, 46.0),  # bgn/dem 双 JSON 同屏
    "treatment":      ("t11-treatment",    0.2, 23.8, 22.5),  # suggestedPatch JSON
    "placeholder-run": ("t12-placeholder", 0.2, 37.7, 35.5),  # will 404 回滚帧
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
        # （hf-03/hf-04 实证）。-g 30 每秒一个 IDR 消 sparse keyframes warning。
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
