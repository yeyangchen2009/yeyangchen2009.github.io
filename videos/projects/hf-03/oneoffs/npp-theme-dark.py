# -*- coding: utf-8 -*-
"""把本机 Notepad++ 7.88 配置改成深色大字号（hf-03 录屏专用）。

只改 %APPDATA%/Notepad++/stylers.xml；原文件备份在 oneoffs/backup/。
恢复：把备份覆盖回去后重启 Notepad++。

用法：
    python npp-theme-dark.py            # 写入深色主题
    python npp-theme-dark.py --restore  # 从 backup/ 恢复
"""
import re
import sys
import shutil
from pathlib import Path

APPDATA = Path.home() / "AppData" / "Roaming" / "Notepad++"
STYLERS = APPDATA / "stylers.xml"
HERE = Path(__file__).resolve().parent
BACKUP = HERE / "backup" / "stylers.xml"

# GitHub Dark 配色
BG = "0d1117"       # 编辑区底
PANEL = "161b22"    # 行号/当前行
INK = "e6edf3"     # 默认文字
MUTED = "8b949e"   # 行号/次要
SELECT_BG = "264f78"
CARET = "e6edf3"

# 浅色语义色 -> GitHub Dark 语义色（对全部 lexer 生效）
COLOR_MAP = {
    "FFFFFF": BG,       # 白底
    "000000": INK,      # 黑字
    "008000": "7ee787",
    "007F00": "7ee787",
    "808040": "7ee787",
    "FF8000": "f0883e",
    "007F7F": "56d4dd",
    "0000FF": "79c0ff",
    "FF0000": "ff7b72",
    "8000FF": "d2a8ff",
    "808080": MUTED,
    "E8E8FF": PANEL,
    "C4F9FD": BG,
    "E4E4E4": PANEL,
    "F3F3F3": PANEL,
    "E9E9E9": PANEL,
    "C0C0C0": "30363d",
    "CDE8CF": BG,
    "FFFF80": "f2cc60",
}

FONT_SIZE = 20
FONT_NAME = "Consolas"

GLOBAL_STYLES = f'''    <GlobalStyles>
        <!-- Attention : Don't modify the name of styleID="0" -->
        <WidgetStyle name="Global override" styleID="0" fgColor="{INK}" bgColor="{BG}" fontName="{FONT_NAME}" fontStyle="0" fontSize="{FONT_SIZE}" enableFontFace="yes" enableFontSize="yes" />
        <WidgetStyle name="Default Style" styleID="32" fgColor="{INK}" bgColor="{BG}" fontName="{FONT_NAME}" fontStyle="0" fontSize="{FONT_SIZE}" />
        <WidgetStyle name="Indent guideline style" styleID="37" fgColor="30363d" bgColor="{BG}" fontName="" fontStyle="0" fontSize="" />
        <WidgetStyle name="Brace highlight style" styleID="34" fgColor="79c0ff" bgColor="{BG}" fontName="" fontStyle="1" fontSize="{FONT_SIZE}" />
        <WidgetStyle name="Bad brace colour" styleID="35" fgColor="ff7b72" bgColor="{BG}" fontName="" fontStyle="0" fontSize="" />
        <WidgetStyle name="Current line background colour" styleID="0" bgColor="{PANEL}" fontStyle="0" fgColor="{MUTED}" fontSize="" />
        <WidgetStyle name="Selected text colour" styleID="0" bgColor="{SELECT_BG}" fontStyle="0" fgColor="ffffff" />
        <WidgetStyle name="Caret colour" styleID="2069" fgColor="{CARET}" fontStyle="0" bgColor="{BG}" />
        <WidgetStyle name="Edge colour" styleID="0" fgColor="30363d" fontStyle="0" bgColor="{BG}" fontSize="" />
        <WidgetStyle name="Line number margin" styleID="33" fgColor="{MUTED}" bgColor="{PANEL}" fontName="" fontStyle="0" fontSize="" />
        <WidgetStyle name="Fold" styleID="0" fgColor="{MUTED}" bgColor="{PANEL}" fontStyle="0" fontSize="8" />
        <WidgetStyle name="Fold active" styleID="0" fgColor="ff7b72" fontStyle="0" bgColor="{PANEL}" fontSize="8" />
        <WidgetStyle name="Fold margin" styleID="0" fgColor="ffffff" bgColor="{PANEL}" fontStyle="0" fontSize="" />
        <WidgetStyle name="White space symbol" styleID="0" fgColor="484f58" fontStyle="0" bgColor="{BG}" />
        <WidgetStyle name="Smart HighLighting" styleID="29" bgColor="bb8009" fontStyle="0" fgColor="fff8c5" fontSize="" />
        <WidgetStyle name="Find Mark Style" styleID="31" bgColor="9e6a03" fontStyle="0" fgColor="fff8c5" fontSize="{FONT_SIZE}" />
        <WidgetStyle name="Mark Style 1" styleID="25" bgColor="1f6feb" fontStyle="0" fgColor="ffffff" fontSize="{FONT_SIZE}" />
        <WidgetStyle name="Mark Style 2" styleID="24" bgColor="f0883e" fontStyle="0" />
        <WidgetStyle name="Mark Style 3" styleID="23" bgColor="bb8009" fontStyle="0" fgColor="fff8c5" />
        <WidgetStyle name="Mark Style 4" styleID="22" bgColor="8957e5" fontStyle="0" fgColor="ffffff" fontSize="{FONT_SIZE}" />
        <WidgetStyle name="Mark Style 5" styleID="21" bgColor="238636" fontStyle="0" fgColor="ffffff" fontSize="{FONT_SIZE}" />
        <WidgetStyle name="Incremental highlight all" styleID="28" bgColor="1f6feb" fontStyle="0" fgColor="ffffff" />
        <WidgetStyle name="Tags match highlighting" styleID="27" bgColor="8957e5" fontStyle="0" fgColor="ffffff" />
        <WidgetStyle name="Tags attribute" styleID="26" bgColor="bb8009" fontStyle="0" fgColor="fff8c5" />
        <WidgetStyle name="Active tab focused indicator" styleID="0" fgColor="f0883e" fontStyle="0" bgColor="{PANEL}" />
        <WidgetStyle name="Active tab unfocused indicator" styleID="0" fgColor="1f6feb" fontStyle="0" bgColor="{PANEL}" />
        <WidgetStyle name="Active tab text" styleID="0" fgColor="{INK}" fontStyle="0" bgColor="{PANEL}" />
        <WidgetStyle name="Inactive tabs" styleID="0" fgColor="{MUTED}" bgColor="21262d" fontStyle="0" />
        <WidgetStyle name="URL hovered" styleID="0" fgColor="79c0ff" fontStyle="0" bgColor="21262d" />
    </GlobalStyles>'''


def replace_color_attr(match):
    attr, value = match.group(1), match.group(2).upper()
    return f'{attr}="{COLOR_MAP.get(value, value)}"'


def main():
    if "--restore" in sys.argv:
        shutil.copy2(BACKUP, STYLERS)
        print(f"已恢复 {STYLERS}")
        return

    text = STYLERS.read_text(encoding="utf-8")

    # 1) 全部 lexer 语义色映射（GlobalStyles 整段随后重写，不受影响）
    text = re.sub(r'(fgColor|bgColor)="([0-9A-Fa-f]{6})"', replace_color_attr, text)

    # 2) GlobalStyles 整段替换
    text = re.sub(r"    <GlobalStyles>.*?</GlobalStyles>",
                  lambda _: GLOBAL_STYLES, text, flags=re.S)

    STYLERS.write_text(text, encoding="utf-8")
    print(f"已写入深色主题 -> {STYLERS}")


if __name__ == "__main__":
    main()
