# -*- coding: utf-8 -*-
"""hf-05 F2 成片复查：从终片抽 40 点拼 contact sheet 目验。

终片为 finalize --intro --hold 2 产物：0–2s 封面静帧（声音＝正片前 2s），
终片时刻 T ＝ 正片时刻 t＋2。复查点（时间均为终片秒）：
  A intro 接合 4 点（封面带声、封面末、正片首帧）；
  B 17 幕中点（概念幕看排版、录屏幕看画面阶段）；
  C 9 个关键状态帧（六关递进首/尾、contrast 大红 err 卡、g9 全绿/
    text_occluded 红、g10 三警告、kf-list/shot freeze）；
  D 5 处 video→freeze 接缝前后帧（动作帧→同源定格应无视觉跳变）。
输出 build/f2/sheet-*.png（6×4，帧左上盖 ASCII 标签＋秒数）。

seek 工艺：纯 output seek（-ss 在 -i 后）在 552s 片上每点要从头解码，
40 点耗时超 10 分钟；改「粗 input seek t-1.5（落到最近关键帧）＋
精 output seek 1.5」组合，每点秒出，时间精度仍由 output seek 保证。
"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FINAL = ROOT / "media" / "hf-05-yeyang-cover.mp4"
OUT = ROOT / "build" / "f2"
# ffmpeg 7.1.1/Windows 的 filtergraph 不认盘符冒号转义；字体复制到
# build/f2/ 下用无盘符相对路径（subprocess cwd=ROOT）。
FONT_SRC = Path("C:/Windows/Fonts/consola.ttf")
FONT_REL = "build/f2/consola.ttf"

# (终片秒, 标签)
POINTS = [
    # —— A intro 接合 ——
    (0.5, "A0-cover"), (1.9, "A1-cover-end"), (2.1, "A2-body-in"), (2.6, "A3-open"),
    # —— B 17 幕中点（t 正片中点＋2）——
    (30.0, "B1-open"), (86.2, "B2-sixgates"), (134.0, "B3-missing"),
    (168.4, "B4-overflow"), (193.8, "B5-warnrule"), (229.9, "B6-contrast"),
    (271.8, "B7-layers"), (293.0, "B8-trackintro"), (328.9, "B9-track"),
    (376.9, "B10-sut"), (404.3, "B11-greenrule"), (451.0, "B12-checkup"),
    (494.6, "B13-echo"), (507.6, "B14-scope"), (525.8, "B15-action"),
    (545.2, "B16-next"), (553.4, "B17-bye"),
    # —— C 关键状态帧 ——
    (73.0, "C-gate1"),          # 六关递进：只 Lint 亮
    (112.3, "C-gate6pass"),     # 六关全亮＋g2 复绿
    (222.0, "C-errred"),        # contrast 大红 1.14:1 err 卡采样段
    (304.0, "C-g9green"),       # 同 track-index 全绿
    (344.0, "C-g9occluded"),    # text_occluded 红
    (374.0, "C-g10warn3"),      # #sut 三警告 passed 卡
    (425.7, "C-kflist"),        # keyframes 列表 freeze
    (445.4, "C-kfshot"),        # --shot 命令 freeze
    (497.0, "C-echo0"),         # echo %ERRORLEVEL% ＝ 0
    # —— D video→freeze 接缝：前/后 ——
    (67.85, "D-type-v"), (68.30, "D-type-fz"),
    (218.85, "D-badrun-v"), (219.05, "D-badrun-fz"),
    (322.45, "D-swap-v"), (322.65, "D-swap-fz"),
    (371.15, "D-warn-v"), (371.35, "D-warn-fz"),
    (497.75, "D-echo-v"), (497.95, "D-echo-fz"),
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
        coarse = max(0.0, t - 1.5)
        run(["ffmpeg", "-y", "-loglevel", "error",
             "-ss", str(coarse), "-i", str(FINAL),
             "-ss", str(t - coarse), "-frames:v", "1", "-vf", vf, str(raw)])
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
