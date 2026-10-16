# -*- coding: utf-8 -*-
"""hf-05 · make_video 配套的二次精切（#569，沿 cut_shorts 体例）。

cut_shorts 产的 21 条 shorts 是「粗切宁长勿短」的素材（run 系 33.4s 含
0.3–6s 打字＋27s 等 check＋尾帧结果，edit 系动作落在片中后段）。
make_video 要的是与口播拍点对齐的**短动作段**（clip 时长一一等于媒体时长，
不依赖长媒体短 clip 的截断行为，hf-04 全片同体例）：

  python oneoffs/cut_final.py frames   从 shorts 抽密帧拼 contact sheet 目验
  python oneoffs/cut_final.py cut      按 CUTS2 重编码短段到 media/shorts/，
                                       新增 freeze（过程帧/列表帧）到 freezes/

CFR 硬闸同 cut_shorts：-vf fps=30 -g 30 -keyint_min 30 +faststart，crf18。
成片几何 1600×920 不变。产物命名：
  *-type.mp4  run 系片首打字段（0.05–6.3s）
  *-act.mp4   edit 系 NPP 动作短段（目验后定切点）
  kf-list.mp4 / kf-shotcmd.mp4      keyframes 列表段 / --shot 命令渲染段
  echo-act.mp4                      errlvl-zero 内 echo 打字＋0 初现段
  freezes/check-run{1..4}.png       check-good 六关滚动过程帧（S2 轮替）
  freezes/kf-list.png               keyframes 列表稳定帧
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHORTS = ROOT / "media" / "shorts"
FREEZES = ROOT / "media" / "freezes"
FRAMES = ROOT / "build" / "final-frames"

# ---- 密帧目验表（片内秒；目验后回填 CUTS2）----
PROBE2 = {
    "check-good":      [0.5, 1, 2, 3, 4, 5, 6, 7, 9, 11, 13, 15,
                        17, 19, 21, 23, 24, 25, 25.8, 26.3, 27, 30, 33],
    "dur-del":         [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.2],
    "dur-run":         [0.5, 2, 4, 5.5, 7, 15, 24, 25.7, 26.0, 26.3, 27, 30, 33],
    "overflow-run":    [0.5, 2, 4, 5.5, 7, 15, 24, 26.0, 26.3, 26.6, 27, 30, 33],
    "root-fix-edit":   [0.5, 2, 3.5, 5, 6.5, 8, 9.5, 11, 12.5, 13.3],
    "root-fix-run":    [0.5, 2, 4, 5.5, 7, 15, 25, 27, 30, 32.3, 33],
    "color-bad-edit":  [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 10.2],
    "color-bad-run":   [0.5, 2, 4, 5.5, 7, 15, 25, 26, 27, 30, 32.3, 33],
    "color-fix-edit":  [0.5, 1.5, 3, 4.5, 6, 7.5, 9, 10.5, 11.4],
    "color-fix-run":   [0.5, 2, 4, 5.5, 7, 15, 25, 27, 30, 31.8, 33],
    "same-track-run":  [0.5, 2, 4, 5.5, 7, 15, 25, 27, 30, 32.3, 33],
    "dom-swap":        [0.5, 2, 3.5, 5, 6.5, 8, 9.5, 11, 12.5, 14, 15.5, 16.5],
    "dom-swap-run":    [0.5, 2, 4, 5.5, 7, 15, 25, 27, 30, 32.3, 33],
    "occlude-code":    [0.5, 1.5, 2.5, 3.5, 4.5, 5.3],
    "occlude-run":     [0.5, 2, 4, 5.5, 7, 15, 25, 26, 27, 30, 32, 33],
    "nulltarget-code": [0.5, 1.5, 2.5, 3.5, 4.3, 5.3],
    "nulltarget-run":  [0.5, 2, 4, 5.5, 7, 15, 24, 25, 26, 27, 30, 30.8, 33],
    "kf":              [0.5, 2, 4, 6, 8, 9.5, 11, 13, 15, 17, 19, 21,
                        23, 25, 28, 32, 36, 40, 42, 44, 46, 48, 49.8, 51],
    "inspect-dep":     [0.5, 2, 4, 5.5, 7, 10, 13, 15, 17, 19, 21.8, 24],
    "beats":           [0.5, 2, 4, 5.5, 7, 9, 10.5, 12, 14, 16, 18.8, 20, 21.3],
    "errlvl-zero":     [0.3, 1, 2, 3, 4, 5, 5.7, 7, 8.5, 9.2],
}

# ---- 二次精切点（2026-10-16 全部 sheet 目验后回填）----
# 视频段时长一一等于成片窗口（hf-04 体例：clip duration＝媒体时长）。
# run 系报文在片内 25–27s 瞬刷、尾帧滚屏，一律只取片首打字段，结果交 freeze。
# id: (源 short, 片内起, 片内止)；("img", src, t) 抽单帧到 freezes/
CUTS2 = {
    # S2 首跑 check：npx 命令逐字出现 1–5s
    "check-good-type":  ("check-good",     0.40,  5.40),
    # S3 删 data-duration：选中→删除动作在 3.5–4.5s；黄字 run 取打字尾
    "dur-del-act":      ("dur-del",        3.40,  6.20),
    "dur-run-type":     ("dur-run",        4.50,  6.30),
    # S4 越界 run 打字尾；root 10→13 动作在 3.5–5s；复绿 run
    "overflow-type":    ("overflow-run",   4.40,  6.30),
    "root-fix-act":     ("root-fix-edit",  2.80,  6.10),
    "root-fix-type":    ("root-fix-run",   4.90,  6.30),
    # S6 对比度：#e6edf3→#1a1f26 在 1.5–2.5s；→rgb 在 1.5–3s
    "color-bad-act":    ("color-bad-edit", 1.00,  3.60),
    "color-bad-type":   ("color-bad-run",  4.70,  6.30),
    "color-fix-act":    ("color-fix-edit", 1.00,  4.20),
    "color-fix-type":   ("color-fix-run",  4.90,  6.30),
    # S8 同轨 run 打字；DOM 整块上移 2–4s；对调复绿；遮挡块静场；红 run
    "same-track-type":  ("same-track-run", 2.10,  6.30),
    "dom-swap-act":     ("dom-swap",       1.40,  5.00),
    "dom-swap-type":    ("dom-swap-run",   4.50,  6.30),
    "occlude-code-act": ("occlude-code",   0.40,  4.60),
    "occlude-type":     ("occlude-run",    4.70,  6.30),
    # S9 #sut 拼写行静场；3⚠ run 打字尾（id 加 -act 避免与源同名原地覆盖）
    "nulltarget-code-act": ("nulltarget-code", 0.40, 5.20),
    "nulltarget-type":  ("nulltarget-run", 4.70,  6.30),
    # S11 体检三连：keyframes 打字→列表刷出 13–17s→--shot 打字 25–31s；
    # inspect/beats 各取打字段
    "kf-cmd":           ("kf",             3.00,  6.50),
    "kf-list-pop":      ("kf",            12.40, 17.60),
    "kf-shotcmd":       ("kf",            25.00, 31.00),
    "inspect-type":     ("inspect-dep",    2.80,  6.40),
    "beats-type":       ("beats",          2.80,  6.40),
    # S12 echo %ERRORLEVEL% 打字 1.2–1.9s＋0 初现
    "echo-act":         ("errlvl-zero",    0.90,  3.20),

    # ---- 新增 freeze（原 freeze 均为尾帧，补三张过程帧＋一张警告帧）----
    # check-good 片内 15s：Checking proj 静场（六关逐条讲时终端陪伴帧）
    "check-running":    ("img", "check-good", 15.0),
    # color-bad-run 片内 30s：Contrast 四✗＋Try rgb＋4 errors＋Check failed
    # 同屏（尾帧 32.5s ✗ 行已滚出，故补此帧作全片红灯高点）
    "color-bad-full":   ("img", "color-bad-run", 30.0),
    # kf 片内 19s：列表完整（#title visual fromTo/flat 0s>1s＋0%/100%＋Tip）
    "kf-list":          ("img", "kf", 19.0),
    # nulltarget-run 三警告同屏候选（25.8/26.0 两帧目验后取一，另张备用）
    "nulltarget-warn-a": ("img", "nulltarget-run", 25.8),
    "nulltarget-warn-b": ("img", "nulltarget-run", 26.1),
}


def run(cmd):
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def phase_frames():
    FRAMES.mkdir(parents=True, exist_ok=True)
    for cid, pts in PROBE2.items():
        src = SHORTS / (cid + ".mp4")
        if not src.exists():
            print("跳过 %s（缺 %s）" % (cid, src))
            continue
        sheet_dir = FRAMES / cid
        sheet_dir.mkdir(exist_ok=True)
        stamped = []
        for t in pts:
            out = sheet_dir / ("%05.1f.png" % t)
            if not out.exists():
                run(["ffmpeg", "-y", "-loglevel", "error",
                     "-ss", str(t), "-i", str(src), "-frames:v", "1",
                     "-vf", ("scale=560:322,drawtext=text='%s s':x=10:y=8:"
                             "fontsize=30:fontcolor=yellow:box=1:"
                             "boxcolor=black@0.65") % t, str(out)])
            stamped.append(out)
        # 每张 sheet 最多 12 帧（4×3），超出分张
        per, idx = 12, 0
        for i in range(0, len(stamped), per):
            batch = stamped[i:i + per]
            listfile = sheet_dir / ("_list%d.txt" % idx)
            listfile.write_text("\n".join("file '%s'" % f.as_posix()
                                          for f in batch), encoding="utf-8")
            sheet = FRAMES / ("sheet-%s-%d.png" % (cid, idx))
            run(["ffmpeg", "-y", "-loglevel", "error",
                 "-f", "concat", "-safe", "0", "-i", str(listfile),
                 "-vf", "tile=4x3:margin=5:padding=5:color=black",
                 "-frames:v", "1", str(sheet)])
            idx += 1
        print("sheet-%s：%d 帧（%d 张）" % (cid, len(pts), idx))


def phase_cut():
    if not CUTS2:
        sys.exit("CUTS2 为空：先 frames 目验 contact sheet，再回填切点")
    for out_id, spec in CUTS2.items():
        if spec[0] == "img":
            _, src_id, t = spec
            run(["ffmpeg", "-y", "-loglevel", "error",
                 "-ss", str(t), "-i", str(SHORTS / (src_id + ".mp4")),
                 "-frames:v", "1", str(FREEZES / (out_id + ".png"))])
            print("img  %-18s %.1fs @ %s" % (out_id, t, src_id))
            continue
        src_id, s, e = spec
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(s), "-to", str(e), "-i",
             str(SHORTS / (src_id + ".mp4")),
             "-vf", "fps=30",
             "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
             "-g", "30", "-keyint_min", "30", "-movflags", "+faststart",
             "-an", str(SHORTS / (out_id + ".mp4"))])
        print("cut  %-18s %.2f–%.2f (%.2fs) @ %s"
              % (out_id, s, e, e - s, src_id))


if __name__ == "__main__":
    {"frames": phase_frames, "cut": phase_cut}[
        sys.argv[1] if len(sys.argv) > 1 else "frames"]()
