# -*- coding: utf-8 -*-
"""音画偏移测量：BEEP 能量 onset vs 白闪帧亮度突变沿。

用法（body 与终片同口径，事件都在片内 3/5/7/9/11s）：
    python oneoffs/measure_av_sync.py renders/body.mp4
    python oneoffs/measure_av_sync.py renders/final-intro.mp4

finalize --intro 虽裁掉正片头 2s 画面，但封面静帧正好占住 0–2s，裁后
body 画面接在 2s 处放 body t=2，且音频整段不动——所以五事件在终片里
仍是 3/5/7/9/11s，两版可直接比较，无需折回。

偏移口径：offset = t_visual - t_audio（正＝画面晚于声音，即要把视觉往
前挪 |offset| 才对齐，与字幕 time_offset「正值＝视觉提前」同向）。
门限：配对比 >= 3/5 且 spread <= 1 帧（33.4ms@30fps）。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EXPECT_BODY = [3.0, 5.0, 7.0, 9.0, 11.0]
FRAME_TOL = 0.10          # 事件与期望时刻的容差（秒）
SPREAD_MAX_FRAMES = 1    # spread 门限：1 帧


def ffprobe_fps(mp4: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate,nb_frames",
         "-of", "json", str(mp4)],
        capture_output=True, text=True, check=True)
    st = json.loads(out.stdout)["streams"][0]
    num, den = st["r_frame_rate"].split("/")
    return float(num) / float(den)


def visual_edges(mp4: Path) -> list:
    """signalstats 逐帧 YAVG，返回亮度上升沿帧号列表（黑->白）。"""
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(mp4),
         "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG",
         "-an", "-f", "null", "-"],
        capture_output=True, text=True, check=True)
    yavg = []
    for line in p.stderr.splitlines():
        # 行形如 "[Parsed_metadata_1 @ 0x..] lavfi.signalstats.YAVG=235"
        if "lavfi.signalstats.YAVG=" in line:
            yavg.append(float(line.rsplit("=", 1)[1]))
    yavg = np.asarray(yavg)
    diffs = np.diff(yavg)
    # 黑(≈0)->白(≈255) 单帧跳变；阈值 50 远低于白闪沿、远高于编码噪声
    edges = [int(i + 1) for i in np.where(diffs > 50)[0]]
    # 沿若连续（理论不会，纯白只 3 帧），合并为每组第一帧
    merged = []
    for n in edges:
        if not merged or n - merged[-1] > 2:
            merged.append(n)
    return merged, yavg


def audio_onsets(mp4: Path, sr: int = 24000) -> list:
    """解出单声道 PCM，按幅值阈值分组，返回各脉冲 onset 秒。"""
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(mp4),
         "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
        capture_output=True, check=True)
    x = np.frombuffer(p.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    hot = np.abs(x) > 0.15                    # 脉冲 peak 0.5；AAC 底噪远低于此
    idx = np.where(hot)[0]
    groups, start, prev = [], int(idx[0]), int(idx[0])
    for i in idx[1:]:
        if i - prev > int(sr * 0.05):         # 间隔 >50ms 算新脉冲
            groups.append(start)
            start = int(i)
        prev = int(i)
    groups.append(start)
    return [g / sr for g in groups]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4")
    args = ap.parse_args()
    mp4 = Path(args.mp4)
    fps = ffprobe_fps(mp4)
    frame_dur = 1.0 / fps

    edges, yavg = visual_edges(mp4)
    onsets = audio_onsets(mp4)
    expect = EXPECT_BODY

    print("文件：%s" % mp4)
    print("fps=%.3f（帧宽 %.2fms）视觉沿 %d 个、音频 onset %d 个"
          % (fps, frame_dur * 1000, len(edges), len(onsets)))
    print("期望事件（body / intro 终片同时刻）：%s" % expect)
    print("-" * 78)

    pairs = min(len(edges), len(onsets))
    rows = []
    for k in range(pairs):
        t_a = onsets[k]
        t_v = edges[k] / fps
        off = t_v - t_a
        ok_exp = any(abs(t_v - e) < FRAME_TOL for e in expect)
        rows.append((k, t_a, edges[k], t_v, off, ok_exp))
        print("事件%d  audio=%9.4fs  白闪帧=%4d  visual=%9.4fs  "
              "offset=%+8.1fms  %s"
              % (k + 1, t_a, edges[k], t_v, off * 1000,
                 "OK" if ok_exp else "✗ 偏离期望"))

    if len(edges) != 5 or len(onsets) != 5:
        print("-" * 78)
        print("✗ 事件数不是 5/5：视觉 %d、音频 %d" % (len(edges), len(onsets)))
        sys.exit(1)

    offs = np.array([r[4] for r in rows])
    spread = offs.max() - offs.min()
    print("-" * 78)
    print("配对 %d/5  offset 中位数=%+.1fms  均值=%+.1fms  "
          "min=%+.1fms  max=%+.1fms  spread=%.1fms（%.2f 帧）"
          % (pairs, np.median(offs) * 1000, offs.mean() * 1000,
             offs.min() * 1000, offs.max() * 1000,
             spread * 1000, spread / frame_dur))

    gates = pairs >= 3 and spread <= SPREAD_MAX_FRAMES * frame_dur + 1e-9
    all_expect = all(r[5] for r in rows)
    print("门限：配对 %s（≥3/5）  spread %s（≤1 帧）  期望时刻 %s"
          % ("PASS" if pairs >= 3 else "FAIL",
             "PASS" if spread <= frame_dur + 1e-9 else "FAIL",
             "PASS" if all_expect else "FAIL"))
    print("结论：%s" % ("PASS" if gates and all_expect else "FAIL"))
    print("建议 time_offset ≈ %+.3fs（视觉提前量；中位数口径）"
          % np.median(offs))
    sys.exit(0 if gates and all_expect else 1)


if __name__ == "__main__":
    main()
