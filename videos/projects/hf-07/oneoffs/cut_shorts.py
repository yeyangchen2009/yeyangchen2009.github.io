# -*- coding: utf-8 -*-
"""hf-07 · 9 take 精切＋定格帧（沿 hf-03/04/05/06 体例）：t06 切两段
（报告段／洋葱皮段），其余每 take 一条整段 short；另抽 t05 #nope、
t06 #bad 两处错误终端态 freeze（报告帧由 keyframes-run 的 freeze 兼）。

两阶段：
  python oneoffs/cut_shorts.py frames   抽 PROBE 点帧拼 contact sheet 目验
  python oneoffs/cut_shorts.py cut      按 CUTS 帧精确重编码（crf18）到
                                        media/shorts/，并抽定格 PNG 到 freezes/

前置：母带在录制机 F:\\_hftest\\hf07-rec\\takes\\，开切前复制到仓库
gitignored 目录（不入 git）：
  mkdir videos\\projects\\hf-07\\media
  copy F:\\_hftest\\hf07-rec\\takes\\t0*.mp4 videos\\projects\\hf-07\\media\\

硬闸（hf-04 VFR 教训）：gdigrab 原始段必 VFR（本批实测 avg≈10.7fps、
偏差 64%），精切必须 -vf fps=30 强制 CFR＋-g 30 -keyint_min 30＋
+faststart；shorts 逐个过 probe-fps（avg_frame_rate 30/1 才准进 render）。
1600×920@30，crf18 屏幕视觉无损。

freeze 来源分工（STORYBOARD 第三节）：画面产物本身（contact4/frame10/
contact5/zoom 裁图/onion-good/compare/grade）直接用 artifacts/ 真机 PNG
进 make_video，不从录像抽；本脚本 freeze 只抽**录屏里才有**的终端态：
尾状态行/Saved 行，以及 t05 #nope、t06 报告 3 items、t06 #bad 三处中帧。
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
# 时长＝record(...) 实参（2026-10-19 真机耗时 24.4/16.4/31.3/29.4/30.4/
# 53.3/72.3/36.3/31.3）。各终端 take 节奏：~2.2s 起敲命令，snapshot 系
# 真机 13–15s 出 Saved 行，compare 19.7s、grade 14.8s；t06 三命令串行
# （KF wait11 → SHOT_GOOD wait18 → SHOT_BAD wait17）；t05 两命令串行
# （zoom 成 wait18 → #nope wait17）。
PROBE = {
    "t00-prev-bg":  [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 23.5],
    "t01-preview":  [0.3, 2, 3.8, 5, 6.5, 8, 10, 12, 14, 15.5],
    "t02-snap4":    [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
                     28, 30],
    "t03-forwards": [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
                     28],
    "t04-frames5":  [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
                     28, 29.5],
    "t05-zoom":     [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
                     28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 51],
    "t06-keyframes": [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
                      28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52,
                      54, 56, 58, 60, 62, 64, 66, 68, 70],
    "t07-compare":  [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
                     28, 30, 32, 34, 35],
    "t08-grade":    [0.3, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
                     28, 30],
}

# ---- 第二轮：定稿切点（2026-10-20 目验 build/frames/sheet-* 后回填）----
# 粗切宁长勿短，make_video 阶段按幕二次裁。id: (take, 源内起, 源内止,
# freeze_at)；freeze-only 条目 s/e 为 None——只抽定格不切段。
# 目验时序（sheet 帧态）：
#   t00 6s 命令完整／18s 后台状态行完整，停到 23.5
#   t01 0.3s 起就是 player（蓝块随时间轴 0→800、红块墙钟），15.5s 蓝在右
#   t02 18s Capturing／24s 起 4 frames saved 完整列表，停到 30
#   t03 18s Capturing／24s saved＋contact／26s 回提示符
#   t04 24s 起 5 frames saved 完整，停到 29.5
#   t05 第一条 24s saved 停到 40；第二条 36s 起敲、46s 红行、48–51 停屏
#   t06 报告 12–34s 完整 3 items；第二条 38s 敲／42s Saved 停到 60；
#       第三条 62s 敲／68s 起红行 nothing animates，停到 70
#   t07 18s Rendering／28s Comparison saved／30s 回提示符
#   t08 旧录（修复前 no-op 档）：20s 暖色 inactive/no-op 警告＋Rendering、
#       24s 双警告同屏、28s Grade saved＋回提示符——整段保留，m17 可讲
#       「写错档白烤一遍」；三格 freeze 不用录像，用布景重建后 software
#       重生成的 artifacts/t08-grade/grade.png（adjust 档）。
CUTS = {
    # id:                take             s     e     freeze_at
    "prev-bg-run":      ("t00-prev-bg",    3.0,  23.8, 22),    # 后台状态行
    "player-run":       ("t01-preview",    0.3,  15.8, 14),    # player t≈9.9s
    "snap4-run":        ("t02-snap4",      7.0,  30.3, 28),    # 4 frames 列表
    "slow10-run":       ("t03-forwards",   7.0,  28.3, 27),    # 1 frame saved
    "frames5-run":      ("t04-frames5",    7.0,  29.8, 28),    # 5 frames 列表
    "zoom-run":         ("t05-zoom",       7.0,  40.5, 30),    # 第一条 saved
    # t06 切两段：报告段＋洋葱皮段；报告帧即 keyframes-run 的 freeze，
    # 不另设 kf-report freeze-only（同一秒位重复抽帧无意义）。
    "keyframes-run":    ("t06-keyframes",  7.0,  35.0, 22),    # 报告 3 items
    "onion-good-run":   ("t06-keyframes", 36.5,  60.5, 44),    # Saved 洋葱皮
    "compare-run":      ("t07-compare",    7.0,  30.2, 29),    # Comparison saved
    "grade-run":        ("t08-grade",      7.5,  30.5, 25),    # 双 no-op 警告同屏
    # freeze-only：录屏终端错误态（成片里以静帧卡出现）
    "zoom-nope-err":    ("t05-zoom",      None, None, 49),     # #nope 红行
    "kf-bad-err":       ("t06-keyframes", None, None, 69),     # nothing animates 红行
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
    pending = [k for k, v in CUTS.items() if v[3] is None]
    if pending:
        sys.exit("CUTS 未回填（freeze_at 仍为 None）：%s\n"
                 "先 frames 目验 contact sheet 再回填切点。" % ", ".join(pending))
    SHORTS.mkdir(parents=True, exist_ok=True)
    FREEZES.mkdir(parents=True, exist_ok=True)
    for cid, (take, s, e, fat) in CUTS.items():
        src = MEDIA / (take + ".mp4")
        freeze_dst = FREEZES / (cid + ".png")
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(fat), "-i", str(src), "-frames:v", "1",
             str(freeze_dst)])
        if s is None:
            print("freeze %-18s %s @%.1f" % (cid, take, fat))
            continue
        out = SHORTS / (cid + ".mp4")
        # -vf fps=30 强制 CFR 并重建 PTS：gdigrab 源帧时间戳抖动（本批
        # avg≈10.7fps），不重建则 hyperframes 据 avg_frame_rate 误判 VFR、
        # 多路并发抽帧崩（hf-03/04 实证）。-g 30 每秒一个 IDR 消 sparse
        # keyframes warning。
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(s), "-to", str(e), "-i", str(src),
             "-vf", "fps=30",
             "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
             "-g", "30", "-keyint_min", "30", "-movflags", "+faststart",
             "-an", str(out)])
        print("cut %-18s %s  %.2f–%.2f (%.2fs)" % (cid, take, s, e, e - s))


if __name__ == "__main__":
    {"frames": phase_frames, "cut": phase_cut}[
        sys.argv[1] if len(sys.argv) > 1 else "frames"]()
