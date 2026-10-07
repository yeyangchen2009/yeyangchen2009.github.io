# -*- coding: utf-8 -*-
"""封面静帧头 + concat 无损拼接（ffmpeg / ffprobe）。"""
import subprocess
from pathlib import Path

from . import config
from .audioio import probe_duration


def make_cover_head(cover_png, out_mp4, *, seconds=config.COVER_HOLD) -> None:
    """封面 PNG → 精确 N 秒静帧（静音 AAC，参数对齐正片）。"""
    out_mp4 = str(out_mp4)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-loop", "1", "-i", str(cover_png),
         "-f", "lavfi", "-i", "anullsrc=r=%d:cl=stereo" % config.AAC["ar"],
         "-t", str(seconds),
         "-c:v", "libx264", "-profile:v", config.X264["profile"],
         "-pix_fmt", config.X264["pix_fmt"], "-r", str(config.FPS),
         "-crf", str(config.X264["crf"]),
         "-c:a", "aac", "-ar", str(config.AAC["ar"]),
         "-ac", str(config.AAC["ac"]),
         "-shortest", out_mp4],
        check=True)
    dur = probe_duration(out_mp4)
    assert abs(dur - seconds) < 0.001, "封面头时长 %f != %f" % (dur, seconds)


def concat_copy(parts, out_mp4, *, faststart=True, workdir=None) -> None:
    """concat demuxer `-c copy` 无损拼接 parts（顺序即成片顺序）。

    AAC priming 偶发 1 条 Non-monotonic DTS（容器时长差约 21ms），
    观感无影响，属已知接受项，不在此报错。
    """
    workdir = Path(workdir or (Path(out_mp4).parent))
    workdir.mkdir(parents=True, exist_ok=True)
    listfile = workdir / "_concat_list.txt"
    # concat list 用正斜杠绝对路径（Windows 亦被接受）。
    lines = ["file '%s'" % str(Path(p).resolve()).replace("\\", "/")
             for p in parts]
    listfile.write_text("\n".join(lines), encoding="utf-8")

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "concat", "-safe", "0", "-i", str(listfile),
           "-c", "copy"]
    if faststart:
        cmd += ["-movflags", "+faststart"]
    cmd.append(str(out_mp4))
    subprocess.run(cmd, check=True)
