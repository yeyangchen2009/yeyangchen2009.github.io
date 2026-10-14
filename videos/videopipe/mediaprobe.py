# -*- coding: utf-8 -*-
"""媒体录像体检：录屏素材进管线前的 ffprobe 帧率门禁。

背景（hf-04 实证，2026-10-14）：gdigrab 录屏的 r_frame_rate 恒为 30/1，
但桌面合成打嗝时 avg_frame_rate 会掉到 5–24fps（VFR）。这种素材进
「假设输入等间隔」的精切滤镜链后，rawvideo 在管道里驻留暴涨，
多路无界并发时 OOM 大批暴毙（hf-04 首轮 33 路崩 16 路；hf-03 13 路
体量小＋桌面安静侥幸过——「上次能跑」不证明素材健康）。

门禁用法（录完、精切前必跑）：

    python -m videopipe.mediaprobe projects/hf-05/media
    python -m videopipe.mediaprobe a.mp4 b.mkv --threshold 0.1

退出码：0 全部 CFR；2 发现 VFR（同时列出嫌疑文件与两个帧率）；
1 运行错误（ffprobe 缺失/文件不可读）。判据与 hyperframes render 前
preflight 同源：|rFps − avgFps| / max > threshold（默认 10%）。
"""
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".m4v", ".webm"}


def parse_ratio(text):
    """把 ffprobe 的 '30/1'、'15360/512' 分数串解析成 float；坏值返回 None。"""
    if not text or text in ("0/0", "N/A"):
        return None
    try:
        return float(Fraction(text))
    except (ValueError, ZeroDivisionError):
        return None


def vfr_ratio(r_fps, avg_fps):
    """两个帧率字段的相对偏差；任一无效返回 None。"""
    if not r_fps or not avg_fps:
        return None
    denom = max(r_fps, avg_fps)
    if denom == 0:
        return None
    return abs(r_fps - avg_fps) / denom


def probe_video(path):
    """对单个文件跑 ffprobe，取首条视频流；拿不到返回 None。"""
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0",
           "-show_entries",
           "stream=r_frame_rate,avg_frame_rate:format=duration",
           "-of", "json", str(path)]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError("ffprobe 失败（%s）：%s" % (path, e))
    data = json.loads(out)
    streams = data.get("streams") or []
    if not streams:
        return None
    st = streams[0]
    r_fps = parse_ratio(st.get("r_frame_rate"))
    avg_fps = parse_ratio(st.get("avg_frame_rate"))
    duration = None
    fmt_dur = (data.get("format") or {}).get("duration")
    if fmt_dur:
        try:
            duration = float(fmt_dur)
        except ValueError:
            duration = None
    return {"path": str(path), "r_fps": r_fps, "avg_fps": avg_fps,
            "ratio": vfr_ratio(r_fps, avg_fps), "duration": duration}


def iter_videos(target):
    """文件直接收；目录递归常见视频容器（不跟随符号链接）。"""
    p = Path(target)
    if p.is_file():
        if p.suffix.lower() in VIDEO_EXTS:
            yield p
        return
    if p.is_dir():
        for f in sorted(p.rglob("*")):
            if f.is_file() and not f.is_symlink() \
                    and f.suffix.lower() in VIDEO_EXTS:
                yield f


def scan(targets, threshold=0.1):
    """扫描路径列表，返回 (healthy, vfr, unreadable) 三个 info 列表。

    ratio 为 None（帧率字段缺失，如图片序列/损坏文件）归 unreadable，
    不默默放行——门禁的职责是把「无法确认健康」与「健康」分开。
    """
    healthy, vfr, unreadable = [], [], []
    for target in targets:
        for f in iter_videos(target):
            try:
                info = probe_video(f)
            except RuntimeError:
                unreadable.append({"path": str(f), "ratio": None})
                continue
            if info is None:
                unreadable.append({"path": str(f), "ratio": None})
            elif info["ratio"] is None:
                unreadable.append(info)
            elif info["ratio"] > threshold:
                vfr.append(info)
            else:
                healthy.append(info)
    return healthy, vfr, unreadable


def _fmt_fps(v):
    return "%.3f" % v if v is not None else "?"


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    threshold = 0.1
    if "--threshold" in args:
        i = args.index("--threshold")
        try:
            threshold = float(args[i + 1])
            del args[i:i + 2]
        except (IndexError, ValueError):
            print("--threshold 需要一个数值参数", file=sys.stderr)
            return 1

    healthy, vfr, unreadable = scan(args, threshold)
    print("CFR %d 段" % len(healthy))
    for info in vfr:
        print("VFR  %s  r=%s avg=%s 偏差 %.1f%%"
              % (info["path"], _fmt_fps(info["r_fps"]),
                 _fmt_fps(info["avg_fps"]), info["ratio"] * 100))
    for info in unreadable:
        print("???? %s  帧率字段缺失或不可读" % info["path"])
    if unreadable:
        print("%d 段无法确认帧率，按异常处理（先 ffprobe 人工看）"
              % len(unreadable), file=sys.stderr)
        return 1
    if vfr:
        print("%d 段 VFR：精切命令必须加 -vf fps=30 重建 PTS，"
              "或先跑规范精切件" % len(vfr), file=sys.stderr)
        return 2
    print("帧率门禁通过（阈值 %.0f%%）" % (threshold * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
