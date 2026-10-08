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


def finalize_concat(head, body, out_mp4, *, seconds, workdir) -> None:
    """封面头 + 正片 → 终片（音画严格对齐版）。

    视频走 concat `-c copy`（帧精确，正片不重编码）；音频**不**做段拼接——
    而是取正片 PCM，与封面静音在一条 concat filter 里整段重编码 AAC。

    为什么：两段独立 AAC 用 `-c copy` 拼接时，正片段头部的 encoder priming
    （约 21–92ms 静音采样）被原样保留在拼接点，从该处起画面领先声音、偏移
    贯穿全片（实测达摩片图快声 92ms）。整段重编码后拼接点是连续采样、无
    段边界 priming，AAC priming 只出现整条最开头一次（落在封面静音区，无感）。
    """
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    head, body, out_mp4 = str(head), str(body), str(out_mp4)
    ar, ac = config.AAC["ar"], config.AAC["ac"]

    vlist = workdir / "_vlist.txt"
    vlist.write_text(
        "file '%s'\nfile '%s'\n"
        % (Path(head).resolve().as_posix(), Path(body).resolve().as_posix()),
        encoding="utf-8")
    full_v = workdir / "full-video.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(vlist),
         "-map", "0:v", "-c", "copy", "-an", str(full_v)],
        check=True)

    body_wav = workdir / "body-audio.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", body,
         "-vn", "-acodec", "pcm_s16le", "-ar", str(ar), "-ac", str(ac),
         str(body_wav)],
        check=True)

    full_a = workdir / "full-audio.m4a"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "lavfi", "-t", str(seconds),
         "-i", "anullsrc=r=%d:cl=stereo" % ar,
         "-i", str(body_wav),
         "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]",
         "-map", "[a]", "-c:a", "aac", "-b:a", "192k",
         "-ar", str(ar), "-ac", str(ac), str(full_a)],
        check=True)

    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-i", str(full_v), "-i", str(full_a),
         "-map", "0:v", "-map", "1:a",
         "-c", "copy", "-movflags", "+faststart", out_mp4],
        check=True)
