# -*- coding: utf-8 -*-
"""视觉主题：正文/字体/底部字幕的全部外观参数 + CSS 装配。

设计为深模块：项目只传一段"场景专属 CSS"（S1…Sn 规则，逐片手写、
彼此差异大、不适合下沉），通用骨架（reset / body / @font-face /
.scene / 底部字幕）由本模块按 Theme 参数拼出，顺序与空白逐字固定，
保证新生成 index.html 与老版可做零差异对比。

主题随各片迁移增量加入：每加入一个都经 verify.compare / snapshot
验证，而非凭记忆一次写全四套。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str
    bg: str                       # html,body 背景
    font_family: str              # html,body font-family 值（含引号）
    faces_css: str                # @font-face 块（多行，末尾无换行）
    accent: str                   # 逐字高亮色（char_track 的 color）
    ch_color: str                 # 字幕未读字色 .sub .ch
    ch_shadow: str                # 字幕字 text-shadow 值
    subshade: str                 # #subshade background 完整值
    subshade_height: int          # #subshade height
    subbar_bottom: int            # #subbar bottom
    sub_size: int                 # .sub font-size
    sub_comment: str = "底部字幕"  # 字幕块段注释（个别片带括注，零差异保留）


def local_cjk_faces() -> str:
    """本地楷体/宋体/等宽四连 @font-face（zsx 暗版实测）。"""
    return (
        "      @font-face { font-family:'KaiTi'; src:local('KaiTi'),"
        "local('STKaiti'),local('楷体'); }\n"
        "      @font-face { font-family:'STKaiti'; src:local('STKaiti'),"
        "local('KaiTi'); }\n"
        "      @font-face { font-family:'SimSun'; src:local('SimSun'),"
        "local('宋体'); }\n"
        "      @font-face { font-family:'Mono'; src:local('Consolas'),"
        "local('Courier New'),local('monospace'); }"
    )


def _scene_block() -> str:
    return (
        "\n\n      .scene { position:absolute; inset:0; width:1920px; "
        "height:1080px; }\n"
        "      .scene-inner { position:absolute; inset:0; width:1920px; "
        "height:1080px; }"
    )


def _subtitle_block(t: Theme) -> str:
    return (
        "\n\n      /* ===== %s ===== */\n"
        "      #subshade { position:absolute; left:0; right:0; bottom:0; "
        "height:%dpx;\n"
        "        background:%s; }\n"
        "      #subbar { position:absolute; left:0; right:0; bottom:%dpx; "
        "text-align:center; }\n"
        "      .sub { position:absolute; left:50px; right:50px; text-align:center;\n"
        "        font-size:%dpx; letter-spacing:.06em; opacity:0; }\n"
        "      .sub .ch { color:%s; text-shadow:%s; }"
        % (t.sub_comment, t.subshade_height, t.subshade, t.subbar_bottom,
           t.sub_size, t.ch_color, t.ch_shadow)
    )


def assemble_css(t: Theme, project_css: str) -> str:
    """通用骨架夹一段场景专属 CSS，返回 <style> 内的完整文本。"""
    head = (
        "      * { margin: 0; padding: 0; box-sizing: border-box; }\n"
        "      html, body {\n"
        "        width: 1920px; height: 1080px; overflow: hidden;\n"
        "        background: %s;\n"
        "        font-family: %s;\n"
        "      }\n"
        "%s"
        % (t.bg, t.font_family, t.faces_css)
    )
    return head + _scene_block() + project_css + _subtitle_block(t)


# ---- 预置主题 ----

DARK_GOLD_GH = Theme(
    name="dark-gold-gh",
    bg="#0d1117",
    font_family='"KaiTi","STKaiti","SimSun", serif',
    faces_css=local_cjk_faces(),
    accent="#e3b341",
    ch_color="#dbe2ec",
    ch_shadow="0 2px 12px rgba(0,0,0,.8)",
    subshade=("linear-gradient(transparent, rgba(13,17,23,.55) 40%, "
              "rgba(13,17,23,.92))"),
    subshade_height=240,
    subbar_bottom=74,
    sub_size=40,
)

DUNHUANG_WARM = Theme(
    name="dunhuang-warm",
    bg="#f5ecd4",
    font_family='"KaiTi","STKaiti","SimSun", serif',
    faces_css=local_cjk_faces(),
    accent="#c0392b",
    ch_color="#5a4632",
    ch_shadow="0 2px 10px rgba(255,250,240,.95)",
    subshade=("linear-gradient(transparent, rgba(245,236,212,.6) 38%, "
              "rgba(245,236,212,.95))"),
    subshade_height=240,
    subbar_bottom=72,
    sub_size=40,
    sub_comment="底部字幕（亮底渐变）",
)

THEMES = {t.name: t for t in (DARK_GOLD_GH, DUNHUANG_WARM)}
