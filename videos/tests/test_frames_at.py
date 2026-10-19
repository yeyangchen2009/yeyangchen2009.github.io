# -*- coding: utf-8 -*-
"""frames_at 纯函数测试＋ffmpeg 集成测试（ffmpeg 缺失时跳过集成项）。"""
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from frames_at import Point, escape_drawtext, extract_points, make_sheets, parse_point, seek_prefix  # noqa: E402

FFMPEG = shutil.which("ffmpeg")
needs_ffmpeg = pytest.mark.skipif(FFMPEG is None, reason="本机无 ffmpeg")


def test_parse_point():
    assert parse_point("30.0=B1-open") == (30.0, "B1-open")
    assert parse_point("0.5") == (0.5, "")
    assert parse_point("12.34=带中文-标签") == (12.34, "带中文-标签")
    assert parse_point("7=a=b").label == "a=b"      # 只切第一个等号
    p = parse_point("3.5")
    assert p.t == 3.5 and p.label == ""


def test_point_properties():
    pt = Point(1.25, "A0")
    assert pt.t == 1.25 and pt.label == "A0"
    assert Point(2.0).label == ""


def test_seek_prefix():
    # 混合 seeking：粗（输入侧，落就近关键帧）＋精（输出侧，保精度）
    assert seek_prefix(30.0, 1.5) == (28.5, 1.5)
    assert seek_prefix(1.0, 1.5) == (0.0, 1.0)      # 片首附近粗 seek 钳到 0
    assert seek_prefix(300.0, 3.0) == (297.0, 3.0)  # hf-06 的 lead=3 用法


def test_escape_drawtext():
    assert escape_drawtext("A0  1.50s") == "A0  1.50s"
    assert escape_drawtext("a:b") == "a\\:b"        # 冒号必须转义
    assert escape_drawtext("it's") == "it\\'s"


def _make_test_video(path, seconds=4.0):
    cmd = [FFMPEG, "-y", "-loglevel", "error",
           "-f", "lavfi", "-i", "testsrc=duration=%s:size=320x180:rate=30"
           % seconds, "-pix_fmt", "yuv420p", str(path)]
    import subprocess
    subprocess.run(cmd, check=True)


@needs_ffmpeg
def test_extract_and_sheet(tmp_path):
    video = tmp_path / "v.mp4"
    _make_test_video(video)
    out = tmp_path / "out"
    frames = extract_points(video, [Point(0.5, "A0"), Point(2.0, "B1"),
                                    Point(3.5)], out, scale="160:90")
    assert len(frames) == 3
    assert all(f.exists() and f.stat().st_size > 500 for f in frames)
    assert [f.name for f in frames] == ["000.png", "001.png", "002.png"]
    assert (out / "consola.ttf").exists() or sys.platform != "win32"
    sheets = make_sheets(frames[:2], out, tile="2x1")
    assert len(sheets) == 1 and sheets[0].name == "sheet-1.png"
    assert sheets[0].stat().st_size > 500
