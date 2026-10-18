# -*- coding: utf-8 -*-
"""hf-06 · make_video 配套二次精切（沿 hf-05 cut_final 体例）。

cut_shorts 产的 16 条 shorts 是「粗切宁长勿短」的素材（run 系约 30s 含
打字＋等待＋报文终态，edit 系约 10s 含整段 NPP 动作）。make_video 要的
是与口播拍点对齐的**短动作段**（clip 时长一一等于媒体时长，不依赖长媒体
短 clip 的截断行为，hf-04/hf-05 全片同体例）：

  python oneoffs/cut_final.py frames   从 shorts 抽密帧拼 contact sheet 目验
  python oneoffs/cut_final.py cut      按 CUTS2 重编码短段到 media/shorts/，
                                       新增过程 freeze 到 freezes/

CFR 硬闸同 cut_shorts：-vf fps=30 -g 30 -keyint_min 30 +faststart，crf18。
成片几何 1600×920 不变。

最终产物→ make_video VIDEOS 段映射（代录回填 CUTS2 后同步改 VIDEOS 的
src/时长；当前 VIDEOS 用粗切同名占位）：
  S2  good-type.mp4（打字）＋good-run.png 尾帧全绿（cut_shorts 已产）
  S3  de-id-act.mp4＋del-id-edit.png｜noid-type.mp4＋noid-run.png(FROZEN)
  S4  dm-act.mp4＋del-muted-edit.png｜nomuted-type.mp4＋nomuted-run.png
  S5  bs-act.mp4＋bad-src-edit.png｜badaudio-type.mp4＋badaudio-run.png
  S6  miss-type.mp4＋missing-run.png
  S8  sametrack-type.mp4＋sametrack-run.png
  S9  beats-cmd.mp4＋beats-run.png（Wrote 23 beats）
  S11 dry-cmd.mp4＋dry-json.png（JSON -21.8/-37.3/7.5 同屏）
  S12 write-cmd.mp4＋write-json.png｜idem-cmd.mp4＋idem-json.png(withinTolerance)
  S13 ceil-cmd.mp4＋ceiling.png（ok:false/needs 16.0）
  S14 bgn-cmd.mp4＋bgn-err.png(Target audio #bgn was not found)
      dem-cmd.mp4＋dem-err.png(Selector did not match: #dem)
      ——两段均出自 t10-badid（49s 双命令），勿用 t11-treatment
  S15 url-type.mp4＋placeholder-run.png(404/error)
      treat-cmd.mp4（t11 打字段）＋treat-result.png（analyze 方子终态）
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SHORTS = ROOT / "media" / "shorts"
FREEZES = ROOT / "media" / "freezes"
FRAMES = ROOT / "build" / "final-frames"

# ---- 密帧目验表（片内秒；粗切长度待 cut_shorts CUTS 回填后据实收紧）----
# 节奏参照：run 系 0.3–6s 打字、7–21s headless 分析、21s 起报文/JSON 终态；
# t8 双命令（write 约 3–19s、idem 约 24–40s）；t10 双命令
# （bgn 打字约 9.5–13s、exit1 约 15–28s；dem 打字约 34.5–38s、exit1 约 40–47s）；
# edit 系 NPP 动作集中在 2–6s。
PROBE2 = {
    "good-run":       [0.5, 1, 2, 3, 4, 5, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33],
    "del-id-edit":    [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5],
    "noid-run":       [0.5, 2, 4, 5.5, 7, 15, 21, 24, 26, 28, 30, 32.3],
    "del-muted-edit": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.8],
    "nomuted-run":    [0.5, 2, 4, 5.5, 7, 15, 21, 24, 26, 28, 30, 32.3],
    "bad-src-edit":   [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5],
    "badaudio-run":   [0.5, 2, 4, 5.5, 7, 15, 21, 24, 26, 28, 30, 32.3],
    "missing-run":    [0.5, 2, 4, 5.5, 7, 15, 21, 24, 26, 28, 30, 32.3],
    "sametrack-run":  [0.5, 2, 4, 5.5, 7, 15, 21, 24, 26, 28, 30, 32.3],
    "beats-run":      [0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 7, 9, 10.5, 12, 14,
                       16, 18, 20, 21.3],
    "norm-dry":       [0.5, 2, 4, 5.5, 7, 10, 13, 16, 19, 21, 22.5, 23.3],
    "norm-write":     [0.5, 2, 4, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33,
                       36, 39, 42],
    "ceiling":        [0.5, 2, 4, 5.5, 7, 10, 13, 16, 19, 21, 22.5, 23.3],
    "badid":          [0.5, 3, 6, 9, 11, 13, 15, 18, 21, 24, 26, 28,
                       31, 34, 36, 38, 40, 42, 44, 46, 47.5],
    "treatment":      [0.5, 2, 4, 5.5, 7, 10, 13, 16, 19, 21, 22.5, 23.3],
    "placeholder-run": [0.5, 2, 4, 5.5, 7, 15, 21, 24, 26, 28, 30, 32.3],
}

# ---- 二次精切点（2026-10-18 目验 build/final-frames/sheet-* 18 张全量回填）----
# 视频段时长一一等于成片窗口（hf-04/hf-05 体例：clip duration＝媒体时长）。
# run 系报文在分析结束后瞬刷、尾帧滚屏，一律只取片首打字段，结果交 freeze；
# 尾帧若已滚出关键行（如 hf-05 color-bad 30s 帧），改用过程 img 帧。
# id: (源 short, 片内起, 片内止)；("img", src, t) 抽单帧到 freezes/
#
# 目验依据（sheet 帧位）：
#   check 系 run 六条同构——0.5–2 提示符、3–5.5 打字（5.5 帧命令完整）、
#     15 Checking proj、21s 起停底报文 → 打字段统一 (1.5, 6.0)。
#   sametrack 特例：GPU probe 行 15–32.3s 仍在屏（t5 三录后热态亦带 probe），
#     打字段不受影响，⚠ 全文帧在 cut_shorts 35.5s 回滚 freeze 已验。
#   placeholder：35.5s 回滚 freeze 已含 StaticGuard＋will 404 同屏（坑 12）。
#   norm-write 双命令：一令打字 4–9、首 JSON 21–27；二令打字 27–30、
#     幂等 JSON 39–42（withinTolerance/previousVolume 2.371374 同屏 41s 帧）。
#   badid 双命令：bgn 打字 3–9、exit1 18–28；dem 打字 24–28、exit1 38–47.5，
#     46s 帧双 JSON 同屏（dem-err 取此帧，dem JSON 在下半屏完整可读）。
CUTS2 = {
    # S2 首跑全绿：打字 3–5（5s 帧完整）→ 段 (1.5, 5.7)
    "good-type":      ("good-run", 1.5, 5.7),
    # S3 删 id：0.5–2.5 id="demo" 高亮、3.5 已删 → (1.0, 4.0)
    "de-id-act":      ("del-id-edit", 1.0, 4.0),
    "noid-type":      ("noid-run", 1.5, 6.0),
    # S4 删 muted：0.5–3.5 muted 高亮、4.5 已删 → (1.0, 5.0)
    "dm-act":         ("del-muted-edit", 1.0, 5.0),
    "nomuted-type":   ("nomuted-run", 1.5, 6.0),
    # S5 voice→voise：3.5 打字中、4.5 完整（补全框已 Esc）→ (1.0, 5.0)
    "bs-act":         ("bad-src-edit", 1.0, 5.0),
    "badaudio-type":  ("badaudio-run", 1.5, 6.0),
    # S6/S8
    "miss-type":      ("missing-run", 1.5, 6.0),
    "sametrack-type": ("sametrack-run", 1.5, 6.0),
    # S9 beats：2.5–4.5 打字 → (1.0, 5.0)
    "beats-cmd":      ("beats-run", 1.0, 5.0),
    # S11 dry：4–10 打字（5.5 折行、10 完整）→ (3.0, 10.5)
    "dry-cmd":        ("norm-dry", 3.0, 10.5),
    "dry-json":       ("img", "norm-dry", 21.0),
    # S12 write＋幂等
    "write-cmd":      ("norm-write", 3.0, 9.8),
    "write-json":     ("img", "norm-write", 24.0),
    "idem-cmd":       ("norm-write", 27.2, 31.0),
    "idem-json":      ("img", "norm-write", 41.0),
    # S13 天花板：打字 4–10 → (3.0, 10.5)
    "ceil-cmd":       ("ceiling", 3.0, 10.5),
    # S14 双 exit1（均出自 t10-badid）
    "bgn-cmd":        ("badid", 1.5, 9.8),
    "bgn-err":        ("img", "badid", 21.0),
    "dem-cmd":        ("badid", 24.5, 28.8),
    "dem-err":        ("img", "badid", 46.0),
    # S15 占位 URL＋treatment 方子
    "url-type":       ("placeholder-run", 1.5, 6.0),
    "treat-cmd":      ("treatment", 3.0, 10.5),
    "treat-result":   ("img", "treatment", 22.5),
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
