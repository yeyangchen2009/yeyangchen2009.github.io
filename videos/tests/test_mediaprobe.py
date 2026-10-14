# -*- coding: utf-8 -*-
"""mediaprobe 纯函数与扫描分类测试（不依赖本机 ffmpeg：ffprobe 被替换）。"""
import pytest

from videopipe import mediaprobe as mp


def test_parse_ratio():
    assert mp.parse_ratio("30/1") == pytest.approx(30.0)
    assert mp.parse_ratio("15360/512") == pytest.approx(30.0)
    assert mp.parse_ratio("0/0") is None
    assert mp.parse_ratio("N/A") is None
    assert mp.parse_ratio("") is None
    assert mp.parse_ratio("abc/1") is None


def test_vfr_ratio():
    assert mp.vfr_ratio(30.0, 30.0) == pytest.approx(0.0)
    # hf-04 极端段：30 声明、5 实测 → 偏差 83%
    assert mp.vfr_ratio(30.0, 5.0) == pytest.approx(0.833333, rel=1e-4)
    assert mp.vfr_ratio(None, 30.0) is None
    assert mp.vfr_ratio(0.0, 0.0) is None


def _fake_probe(table):
    def _probe(path):
        return table.get(path.name)
    return _probe


def test_scan_classifies(monkeypatch, tmp_path):
    (tmp_path / "good.mp4").write_bytes(b"x")
    (tmp_path / "bad.mkv").write_bytes(b"x")
    (tmp_path / "weird.mov").write_bytes(b"x")
    table = {
        "good.mp4": {"path": "good", "r_fps": 30.0, "avg_fps": 30.0,
                     "ratio": 0.0, "duration": 10.0},
        "bad.mkv": {"path": "bad", "r_fps": 30.0, "avg_fps": 5.2,
                    "ratio": 0.8267, "duration": 46.0},
        # 帧率字段缺失归 unreadable，不默默放行
        "weird.mov": {"path": "weird", "r_fps": None, "avg_fps": None,
                      "ratio": None, "duration": None},
    }
    monkeypatch.setattr(mp, "probe_video", _fake_probe(table))
    healthy, vfr, unreadable = mp.scan([tmp_path], threshold=0.1)
    assert [x["path"] for x in healthy] == ["good"]
    assert [x["path"] for x in vfr] == ["bad"]
    assert [x["path"] for x in unreadable] == ["weird"]


def test_iter_videos(tmp_path):
    (tmp_path / "a.mp4").write_bytes(b"x")
    (tmp_path / "b.txt").write_bytes(b"x")
    sub = tmp_path / "nested"
    sub.mkdir()
    (sub / "c.MKV").write_bytes(b"x")
    names = sorted(f.name for f in mp.iter_videos(tmp_path))
    assert names == ["a.mp4", "c.MKV"]
    assert [f.name for f in mp.iter_videos(tmp_path / "b.txt")] == []
