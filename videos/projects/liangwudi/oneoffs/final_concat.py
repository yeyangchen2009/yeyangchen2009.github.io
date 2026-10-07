# -*- coding: utf-8 -*-
"""oneoff · 梁武帝终片拼接：封面 2s 静帧头 + 正片（无损 concat copy）。

输入：snapshots/cover-final.png、renders/liangwudi-body.mp4
产物：build/cover-head.mp4、media/liangwudi-yeyang-cover.mp4
终片时长应 ≈ 2.00 + 245.41 = 247.41 秒。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from videopipe import ProjectPaths, make_cover_head, concat_copy, probe_duration

P = ProjectPaths.at(Path(__file__).resolve().parents[1])
COVER_PNG = P.snapshots_dir / "cover-final.png"
BODY_MP4 = P.renders_dir / "liangwudi-body.mp4"
HEAD_MP4 = P.build_dir / "cover-head.mp4"
OUT_MP4 = P.media_dir / "liangwudi-yeyang-cover.mp4"

assert COVER_PNG.exists(), COVER_PNG
assert BODY_MP4.exists(), BODY_MP4

make_cover_head(COVER_PNG, HEAD_MP4)
print("封面头 %.3fs" % probe_duration(HEAD_MP4))
print("正片   %.3fs" % probe_duration(BODY_MP4))

concat_copy([HEAD_MP4, BODY_MP4], OUT_MP4, workdir=P.build_dir)
total = probe_duration(OUT_MP4)
print("终片   %.3fs → %s" % (total, OUT_MP4))
assert abs(total - 247.41) < 0.1, total
print("RESULT PASS")
