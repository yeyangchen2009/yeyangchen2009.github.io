# -*- coding: utf-8 -*-
"""长片多点抽帧公共件：混合 seeking（粗 input＋精 output）秒级出帧。

hf-05/hf-06 的 F2 复查各自在 oneoffs 里抄了一份抽帧脚本，同一段 seek
工艺沉淀两次仍靠复制：纯 output seeking（``-ss`` 在 ``-i`` 后）对
490s+ 终片每点从头解码，20–40 点必超时；改「输入侧 ``-ss t-lead`` 落
就近关键帧＋输出侧 ``-ss lead`` 精确定位」后每点秒出，精度仍由
output seek 保证（sparse-keyframe 源 input seeking 会退回前一个关键
帧，hf-04 曾在 296s 抽到 22.5s 的内容）。收口为本模块，hf-07 起 F2
直接继承，别再抄。

CLI：
    python videos/tools/frames_at.py final.mp4 0.5 30.0=B1-open 86.2 \\
        -o build/f2 --sheet
    → build/f2/000.png 001.png …（帧左上盖「标签 秒数」）＋ sheet-1.png…

库用法（从 videos/projects/<片>/oneoffs/ 下的脚本，位置无关）：
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "tools"))
    from frames_at import Point, extract_points, make_sheets

铁律（videos/docs/screen-rec.md §8 全部内化）：
- 批量循环必加 ``-nostdin``（ffmpeg 交互解析器会吞循环的 stdin）；
- drawtext 的 fontfile 不能带盘符冒号（filtergraph 分隔符），字体复制
  到输出目录、用纯文件名相对路径（subprocess cwd=输出目录）；
- drawtext 文本里的冒号必须 ``\\:`` 转义。

本模块只依赖 ffmpeg，不属于 videopipe 包（渲染环境不需要）。
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_FONT = Path("C:/Windows/Fonts/consola.ttf")
DEFAULT_LEAD = 1.5      # 粗 seek 提前量（秒）；hf-05 用 1.5、hf-06 用 3 均验
DEFAULT_SCALE = "480:270"
DEFAULT_TILE = "6x4"


class Point(tuple):
    """(秒, 标签)抽帧点；标签可空。"""

    __slots__ = ()

    def __new__(cls, t, label=""):
        return super().__new__(cls, (float(t), label))

    @property
    def t(self):
        return self[0]

    @property
    def label(self):
        return self[1]


def parse_point(text):
    """'30.0=B1-open' → Point(30.0, 'B1-open')；'30.0' → Point(30.0, '')。"""
    if "=" in text:
        t, label = text.split("=", 1)
    else:
        t, label = text, ""
    return Point(float(t), label.strip())


def seek_prefix(t, lead=DEFAULT_LEAD):
    """混合 seeking 参数对：(输入侧秒, 输出侧秒)；片首附近粗 seek 钳到 0。"""
    coarse = max(0.0, t - lead)
    return coarse, t - coarse


def escape_drawtext(text):
    """drawtext 文本转义：冒号是 filtergraph 分隔符。"""
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _run(cmd, cwd):
    subprocess.run(cmd, check=True, cwd=str(cwd),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def extract_points(video, points, outdir, *, lead=DEFAULT_LEAD,
                   scale=DEFAULT_SCALE, stamp=True, font_src=DEFAULT_FONT):
    """按混合 seeking 抽帧到 outdir，返回帧路径列表（与 points 同序）。

    stamp=True 时帧左上盖「label  t.2fs」黄字标签；字体复制进 outdir
    用纯文件名（盘符冒号坑），ffmpeg 以 outdir 为 cwd。
    """
    video, outdir = Path(video), Path(outdir)
    if not video.exists():
        sys.exit("缺视频：%s" % video)
    outdir.mkdir(parents=True, exist_ok=True)
    font_rel = ""
    if stamp:
        if not font_src.exists():
            sys.exit("缺字体：%s（--no-stamp 可跳过）" % font_src)
        shutil.copyfile(font_src, outdir / font_src.name)
        font_rel = font_src.name
    width = max(3, len(str(len(points) - 1)))
    frames = []
    for i, pt in enumerate(points):
        raw = outdir / ("%0*d.png" % (width, i))
        coarse, fine = seek_prefix(pt.t, lead)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-nostdin",
               "-ss", "%.3f" % coarse, "-i", str(video.resolve()),
               "-ss", "%.3f" % fine, "-frames:v", "1"]
        vf = "scale=%s" % scale if scale else ""
        if stamp:
            text = escape_drawtext(
                ("%s  %.2fs" % (pt.label, pt.t)) if pt.label
                else "%.2fs" % pt.t)
            dt = ("drawtext=fontfile=%s:text='%s':x=8:y=6:fontsize=20:"
                  "fontcolor=yellow:box=1:boxcolor=black@0.65"
                  % (font_rel, text))
            vf = "%s,%s" % (vf, dt) if vf else dt
        if vf:
            cmd += ["-vf", vf]
        cmd.append(raw.name)
        _run(cmd, outdir)
        frames.append(raw)
        print("%*d %8.2f %s" % (width, i, pt.t, pt.label))
    return frames


def make_sheets(frames, outdir, *, tile=DEFAULT_TILE):
    """把帧拼成 contact sheet（tile='6x4'，每张放满再开下一张）。"""
    cols, rows = (int(x) for x in tile.lower().split("x"))
    per = cols * rows
    outdir = Path(outdir)
    sheets = []
    for idx in range(0, len(frames), per):
        batch = frames[idx:idx + per]
        listfile = outdir / ("_list%d.txt" % len(sheets))
        # concat listfile 的相对路径按其所在目录解析：写纯文件名最稳
        listfile.write_text("\n".join("file '%s'" % f.name for f in batch),
                            encoding="utf-8")
        sheet = outdir / ("sheet-%d.png" % (len(sheets) + 1))
        _run(["ffmpeg", "-y", "-loglevel", "error", "-nostdin",
              "-f", "concat", "-safe", "0", "-i", listfile.name,
              "-vf", "tile=%s:margin=4:padding=4:color=black" % tile,
              "-frames:v", "1", sheet.name], outdir)
        sheets.append(sheet)
        print("→ %s（%d 帧）" % (sheet, len(batch)))
    return sheets


def main(argv=None):
    p = argparse.ArgumentParser(
        description="长片多点抽帧（混合 seeking）：final.mp4 t[=label] …")
    p.add_argument("video", help="视频文件路径")
    p.add_argument("points", nargs="+",
                   help="抽帧点：秒 或 秒=标签（如 30.0=B1-open）")
    p.add_argument("-o", "--out", default="build/frames",
                   help="输出目录（默认 build/frames）")
    p.add_argument("--lead", type=float, default=DEFAULT_LEAD,
                   help="粗 seek 提前量秒数（默认 %(default)s）")
    p.add_argument("--scale", default=DEFAULT_SCALE,
                   help="缩放（默认 %(default)s；空串不缩放）")
    p.add_argument("--no-stamp", action="store_true", help="不盖时间戳标签")
    p.add_argument("--sheet", nargs="?", const=DEFAULT_TILE, default="",
                   help="拼 contact sheet，可指定 tile 如 4x3（默认 6x4）")
    args = p.parse_args(argv)
    frames = extract_points(
        args.video, [parse_point(s) for s in args.points], args.out,
        lead=args.lead, scale=args.scale, stamp=not args.no_stamp)
    if args.sheet:
        make_sheets(frames, args.out, tile=args.sheet)


if __name__ == "__main__":
    main()
