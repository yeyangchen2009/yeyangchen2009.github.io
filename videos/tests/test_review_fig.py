# -*- coding: utf-8 -*-
"""review_fig 出图公共件测试（matplotlib 缺失时整体跳过；字体是 Windows 本机件）。"""
import sys
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import matplotlib.pyplot as plt  # noqa: E402

from review_fig import (BG, CJK_FONT, MONO_FONT, TXT, font_cjk, font_mono,  # noqa: E402
                        save_fig, setup_dark)

pytestmark = pytest.mark.skipif(
    not (CJK_FONT.exists() and MONO_FONT.exists()),
    reason="本机 Windows 字体（msyh.ttc/consola.ttf）不在，出图模块只服务本机")


def test_setup_dark_idempotent():
    fp1 = setup_dark()
    fp2 = setup_dark()
    assert fp1 is fp2
    assert plt.rcParams["text.color"] == TXT
    assert plt.rcParams["figure.facecolor"] == BG
    assert font_cjk() is font_cjk()
    assert font_mono() is font_mono()


def test_save_fig_writes_png(tmp_path):
    setup_dark()
    fig, ax = plt.subplots(figsize=(4, 2))
    # 雅黑实战字集：中文＋√×→，hf03/hf04 已验证不缺字
    ax.text(0.1, 0.5, "门禁通过 √  偏差 83% ×  30fps → CFR",
            fontproperties=font_cjk())
    out = save_fig(fig, tmp_path / "nested" / "ok.png")
    assert out.exists() and out.stat().st_size > 1000


def test_save_fig_missing_glyph_raises(tmp_path):
    # Consolas 无 CJK 字形：缺字必须升级为异常，而不是静默出方框
    setup_dark()
    fig, ax = plt.subplots(figsize=(4, 2))
    ax.text(0.1, 0.5, "中文字形测试", fontproperties=font_mono())
    with pytest.raises(UserWarning, match="Glyph .* missing"):
        save_fig(fig, tmp_path / "bad.png")
