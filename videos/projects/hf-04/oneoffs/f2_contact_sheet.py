# -*- coding: utf-8 -*-
"""hf-04 F2 成片复查：从终片抽 57 点拼 3 张 contact sheet 目验。

终片为 finalize --intro 产物：0–2s 封面静帧（声音＝正片前 2s），
2s 起终片时刻 T 即正片时刻 t。复查点：
  A intro 接合 4 点（封面带声、封面末、正片首帧）；
  B 26 幕中点（概念幕看排版、录屏幕看画面阶段）；
  C S18 cs 八段每段首/尾帧（CFR 重切后帧边界微移，核对结果帧卡命令、
    段间接缝不跳错画面）＋ cs-five freeze；
  D 六处 video→freeze 接缝前后帧（动作帧→同源定格应无视觉跳变）。
输出 build/f2/sheet-*.png（6×4，帧左上盖 ASCII 标签＋秒数）。
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FINAL = ROOT / "media" / "hf-04-yeyang-cover.mp4"
OUT = ROOT / "build" / "f2"
# ffmpeg 7.1.1/Windows 的 filtergraph 不认盘符冒号转义；字体复制到
# build/f2/ 下用无盘符相对路径（subprocess cwd=ROOT）。
FONT_SRC = Path("C:/Windows/Fonts/consola.ttf")
FONT_REL = "build/f2/consola.ttf"

# (秒, 标签)
POINTS = [
    # —— A intro 接合 ——
    (0.5, "A0-cover"), (1.9, "A1-cover-end"), (2.1, "A2-body-in"), (2.6, "A3-s1"),
    # —— B 26 幕中点 ——
    (7.5, "S1-static"), (22.5, "S2-fly"), (45.5, "S3-playcss"), (64.0, "S4-how"),
    (90.0, "S5-seekable"), (117.2, "S6-css25"), (140.0, "S7-runtime"),
    (157.2, "S8-timercode"), (188.5, "S9-ser3"), (221.5, "S10-tk6"),
    (255.0, "S11-checkrun"), (277.0, "S12-schro"), (299.0, "S13-pausedfz"),
    (321.0, "S14-fromtofz"), (348.0, "S15-regfz"), (373.0, "S16-agent"),
    (397.0, "S17-playfinal"), (420.0, "S18-cs63"), (449.0, "S19-direct"),
    (476.0, "S20-butler"), (510.0, "S21-renderrun"), (538.0, "S22-adapter"),
    (566.0, "S23-action3"), (590.2, "S24-soul"), (598.0, "S25-next"),
    (605.6, "S26-bye"),
    # —— C cs 八段：每段 start+0.12 / end-0.12，末加 freeze ——
    (408.12, "C-open-h"), (410.08, "C-open-t"),
    (410.32, "C-player-h"), (411.68, "C-player-t"),
    (411.92, "C-s24-h"), (414.48, "C-s24-t"),
    (414.72, "C-s3-h"), (417.68, "C-s3-t"),
    (417.92, "C-s63-h"), (421.08, "C-s63-t"),
    (421.32, "C-s9-h"), (423.48, "C-s9-t"),
    (423.72, "C-s0-h"), (426.88, "C-s0-t"),
    (427.12, "C-five-h"), (434.00, "C-five-t"),
    (435.20, "C-five-fz"),
    # —— D 六处 video→freeze 接缝：前/后 ——
    (128.85, "D-eq-v"), (129.20, "D-eq-fz"),
    (296.10, "D-pause-v"), (296.50, "D-pause-fz"),
    (315.40, "D-fromto-v"), (315.70, "D-fromto-fz"),
    (344.60, "D-html-v"), (344.90, "D-reg-fz"),
    (402.30, "D-final-v"), (402.70, "D-final-fz"),
]


def run(cmd):
    subprocess.run(cmd, check=True, cwd=str(ROOT),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    if not FINAL.exists():
        sys.exit("缺终片：%s" % FINAL)
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FONT_SRC, ROOT / FONT_REL)
    thumbs = []
    for i, (t, label) in enumerate(POINTS):
        raw = OUT / ("%02d.png" % i)
        stamp = ("%s  %.2fs" % (label, t)).replace(":", "\\:")
        vf = ("scale=480:270,"
              "drawtext=fontfile=%s:text='%s':x=8:y=6:fontsize=20:"
              "fontcolor=yellow:box=1:boxcolor=black@0.65" % (FONT_REL, stamp))
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t),
             "-i", str(FINAL), "-frames:v", "1", "-vf", vf, str(raw)])
        thumbs.append(raw)
        print("%2d %7.2f %s" % (i, t, label))
    per, idx = 24, 0
    for i in range(0, len(thumbs), per):
        batch = thumbs[i:i + per]
        listfile = OUT / ("_list%d.txt" % idx)
        listfile.write_text("\n".join("file '%s'" % f.as_posix()
                                      for f in batch), encoding="utf-8")
        sheet = OUT / ("sheet-%d.png" % (idx + 1))
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
             "-safe", "0", "-i", str(listfile),
             "-vf", "tile=6x4:margin=4:padding=4:color=black",
             "-frames:v", "1", str(sheet)])
        print("→ %s（%d 帧）" % (sheet.relative_to(ROOT), len(batch)))
        idx += 1


if __name__ == "__main__":
    main()
