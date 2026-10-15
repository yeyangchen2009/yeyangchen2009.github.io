# -*- coding: utf-8 -*-
"""复盘/审稿配图公共件：暗色画布、字体单例、缺字即失败的存盘。

三个历史脚本（hf03-review、hf04-review-figs、hf04-deep-figs）各自手抄
同一段开头：msyh.ttc / consola.ttf 注册、GitHub Dark 色板，存盘后再人肉
找日志里的 "Glyph missing"。收口为两件颜色/字体常量 ＋ 三个函数：

    import sys
    sys.path.insert(0, r"F:/Data/gmeek-site/videos/tools")
    from review_fig import setup_dark, save_fig, font_cjk, font_mono, BG, PANEL

    setup_dark()                                          # 暗色 rcParams
    fig, ax = plt.subplots(...)
    fig.patch.set_facecolor(BG)                           # 画布深色
    ax.text(..., fontproperties=font_mono())              # 数字/代码 Consolas
    save_fig(fig, out_path)                               # 缺字立即抛错、进程非零

出图踩坑（2026-10 hf03/hf04 实测，别再交学费）：
- ``ax.text(wrap=True)`` 在本环境不生效，长文本必须手动 ``"\\n"`` 断行；
  等宽字体里的间距不要用全角空格 U+3000（Consolas 无此字形），用三个
  ASCII 空格；雅黑没有 ✓ ✗ ⇒ 字形，改用 √ × →；
- matplotlib 缺字只发 UserWarning、进程退出码仍是 0，图里悄悄变方框流入
  稿件。``save_fig`` 在存盘窗口把 Glyph missing 升级成异常，让这种图根本
  存不下来；
- 中文要么 ``setup_dark()`` 走默认族，要么每个 text 显式 ``fontproperties``，
  只设 ``rcParams["font.sans-serif"]`` 在不同 Agg 版本回落不一致。

本模块是**本机出图工具**（依赖 Windows 系统字体），不属于 videopipe 包，
不经 ``videopipe/__init__.py`` 急切导入——渲染/转录环境不需要 matplotlib。
"""
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

WIN_FONT_DIR = Path("C:/Windows/Fonts")
CJK_FONT = WIN_FONT_DIR / "msyh.ttc"
MONO_FONT = WIN_FONT_DIR / "consola.ttf"

# GitHub Dark（与全站 mermaid/卡片配色同源）
BG = "#0d1117"
PANEL = "#161b22"
# PANEL2 比 PANEL 再亮一档，卡片嵌套/侧栏用
PANEL2 = "#21262d"
LINE = "#30363d"
TXT = "#e6edf3"
MUTED = "#8b949e"
BLUE = "#1f6feb"
BLUE_BD = "#79c0ff"
GREEN = "#3fb950"
GREEN2 = "#56d364"
GREEN_BD = "#7ee787"
GOLD = "#d29922"
GOLD_LT = "#fbbf24"
RED = "#ff7b72"
RED_BD = "#f85149"
RED_TX = "#ffa198"

_cjk_fp = None
_mono_fp = None


def font_cjk():
    """微软雅黑 FontProperties 单例（中文标题/正文/卡片文字）。"""
    global _cjk_fp
    if _cjk_fp is None:
        if not CJK_FONT.exists():
            raise RuntimeError("缺中文字体 %s：装微软雅黑或改 review_fig.CJK_FONT"
                               % CJK_FONT)
        font_manager.fontManager.addfont(str(CJK_FONT))
        _cjk_fp = font_manager.FontProperties(fname=str(CJK_FONT))
    return _cjk_fp


def font_mono():
    """Consolas FontProperties 单例（时间码/数字/代码/路径）。"""
    global _mono_fp
    if _mono_fp is None:
        if not MONO_FONT.exists():
            raise RuntimeError("缺等宽字体 %s：装 Consolas 或改 review_fig.MONO_FONT"
                               % MONO_FONT)
        _mono_fp = font_manager.FontProperties(fname=str(MONO_FONT))
    return _mono_fp


def setup_dark():
    """Agg 后端 ＋ 雅黑默认字体族 ＋ GitHub Dark rcParams。幂等可重复调。

    返回雅黑 FontProperties，供需要显式 fontproperties 的调用复用，
    避免重复取单例。
    """
    fp = font_cjk()
    plt.rcParams.update({
        "font.family": fp.get_name(),
        "axes.unicode_minus": False,
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "axes.edgecolor": LINE,
        "axes.labelcolor": TXT,
        "text.color": TXT,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.titlecolor": TXT,
    })
    return fp


def save_fig(fig, path, dpi=110):
    """建父目录并存盘；存盘窗口内 Glyph missing 告警升级为异常。

    缺字默认只是 UserWarning、退出码 0，方框会流入稿件；这里在 savefig
    期间挂 error 级过滤器，缺字即抛 ``UserWarning``，脚本非零退出。
    成功后关闭 fig。返回输出路径。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings():
        warnings.filterwarnings("error", message=r".*Glyph .* missing.*")
        fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path
