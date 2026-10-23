# -*- coding: utf-8 -*-
r"""hf-03 录屏：Notepad++ 操作封装（在 rec_automate 之上）。

实例管理：NPP_EXE 是 F:\_hftest\npp-local 下的安装版副本（doLocalConf.xml
模式，配置只写自身目录），`-multiInst -nosession` 启动独立实例打开录制文件，
与用户日常安装版 NPP（%APPDATA% 配置）完全隔离：暗色主题、Alt+Up/Down
行移动映射、Wrap=no 都在便携目录配置里。

坐标：rec_automate 已声明 PerMonitor DPI 感知，全部坐标为物理 1920×1080。
NPP 录制窗口与 Edge/终端一样摆 (0,0,1600,920)，gdigrab 固定录该区。
每步操作后读磁盘文件校验，不凭感觉。
"""
import ctypes
from ctypes import wintypes
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec_automate as r

# 隔离实例＝用户本机已安装的 NPP 7.8.8 整目录复制到 F:\_hftest\npp-local
# （可信二进制，非外部下载），同目录放 doLocalConf.xml 便携标志：配置只写
# 该目录，完全不碰用户 %APPDATA%。7.8.8 不支持 -settingsDir（7.9.2 才加入，
# 传了会被当成文件名弹「不存在」框）；隔离靠副本目录 + -multiInst。
NPP_EXE = r"F:\_hftest\npp-local\notepad++.exe"
HTML = r"F:\_hftest\hf03-clip\index.html"
TITLE_SUB = "index.html"  # 窗口标题子串（用户的 .md/new 窗口不会撞）

hwnd = None
path = HTML


def _windows_of_pid(pid):
    """该 PID 下所有可见顶层 Notepad++ 窗口 [(hwnd, title)]。"""
    out = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        p = r.wintypes.DWORD()
        r.u.GetWindowThreadProcessId(wnd, r.ctypes.byref(p))
        if p.value == pid:
            c = r.ctypes.create_unicode_buffer(64)
            r.u.GetClassNameW(wnd, c, 64)
            if c.value == "Notepad++" and r.u.IsWindowVisible(wnd):
                b = r.ctypes.create_unicode_buffer(256)
                r.u.GetWindowTextW(wnd, b, 256)
                out.append((wnd, b.value))
        return True

    r.u.EnumWindows(cb, 0)
    return out


def launch(file_path=None, x=0, y=0, w=1600, h=920, timeout=90.0):
    """启动独立 NPP 实例打开 file_path（默认正式录制文件）并摆位；已开则复用。

    NPP 冷启动（-settingsDir 首次初始化＋插件）本机实测可达 30-60s，
    timeout 默认 90s。就绪判定＝新进程窗口标题含文件名（只出现 "new 1"
    空窗算启动异常，直接报错，不用错窗口录下去）。
    注意：上一个 -multiInst 实例必须退净再启动，否则文件参数会丢成空文档。
    """
    global hwnd, path
    if file_path:
        path = file_path
    title_sub = path.split("\\")[-1]
    hwnd = r.find_window(title_sub)
    if hwnd is None:
        proc = subprocess.Popen([NPP_EXE, "-multiInst", "-nosession", path])
        t0 = time.time()
        while time.time() - t0 < timeout:
            wins = _windows_of_pid(proc.pid)
            ready = [w for w, t in wins if title_sub in t]
            if ready:
                hwnd = ready[0]
                break
            time.sleep(0.5)
        if hwnd is None:
            alive = _windows_of_pid(proc.pid)
            raise RuntimeError(
                f"等不到 {path} 的窗口；PID {proc.pid} 现存窗口: {alive}")
    r.activate(hwnd)
    r.u.ShowWindow(hwnd, r.SW_RESTORE)
    time.sleep(0.3)
    r.move(hwnd, x, y, w, h)
    time.sleep(0.4)
    r.disable_ime(hwnd)
    force_wrap_off()
    return hwnd


SCI_SETWRAPMODE = 2260
SC_WRAP_NONE = 0


def _scintillas():
    """枚举 NPP 主窗下的 Scintilla 编辑控件（主/副两视图）。"""
    out = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(child, _):
        b = r.ctypes.create_unicode_buffer(32)
        r.u.GetClassNameW(child, b, 32)
        if b.value == "Scintilla":
            out.append(child)
        return True

    r.u.EnumChildWindows(hwnd, cb, 0)
    return out


def force_wrap_off():
    """向 Scintilla 发 SCI_SETWRAPMODE(WRAP_NONE) 关软换行（config.xml Wrap=no
    之外的运行态双保险）。不关的话 END 在长逻辑行只到视觉折行尾，Enter 会把行劈断。"""
    r.u.SendMessageW.restype = r.wintypes.LPARAM
    for s in _scintillas():
        r.u.SendMessageW(s, SCI_SETWRAPMODE, SC_WRAP_NONE, 0)


# ---------- 取景（缩放 / 选区自动滚入镜）----------

SCI_SETZOOM = 2373
SCI_SETSEL = 2160

_senda = ctypes.windll.user32.SendMessageA
_senda.restype = r.wintypes.LPARAM
_senda.argtypes = [r.wintypes.HWND, r.wintypes.UINT,
                   r.wintypes.WPARAM, r.wintypes.LPARAM]


def active_scintilla():
    """当前可见的编辑控件 hwnd。

    NPPM_GETCURRENTSCINTILLA/NPPM_GETSCINTILLA 在 7.8.8 实测取不到（返回 0，
    插件还会多建隐藏 Scintilla）；可靠判据＝枚举子窗里 class=="Scintilla"、
    可见且窗口尺寸正常（插件的隐藏控件 rect 为 0 或 100×100）的那一个。
    """
    candidates = []
    for s in _scintillas():
        rc = wintypes.RECT()
        r.u.GetWindowRect(s, ctypes.byref(rc))
        if r.u.IsWindowVisible(s) and rc.right - rc.left > 200 and rc.bottom - rc.top > 200:
            candidates.append(s)
    if not candidates:
        raise RuntimeError("找不到可见的 Scintilla 编辑控件")
    return candidates[0]


def set_zoom(z=0):
    """录制统一 zoom=0（config 默认 zoom=2 时长行超出窗口）。

    zoom=0 下四属性长行仍装不下整行：实测 -1/-2 缩字后依旧超宽且字号
    偏小，故方案定为 zoom=0 保可读性＋reveal_in_line 两拍横移取景。"""
    for s in _scintillas():
        r.u.SendMessageW(s, SCI_SETZOOM, z, 0)


def _byte_position(n, anchor=None):
    """第 n 行 anchor 起点的 UTF-8 字节偏移；anchor=None 取行首。"""
    text = read_file()
    lines = text.splitlines(keepends=True)
    if not 1 <= n <= len(lines):
        raise AssertionError(f"行号 {n} 越界（共 {len(lines)} 行）")
    line = lines[n - 1]
    col = 0 if anchor is None else line.find(anchor)
    if anchor is not None and col < 0:
        raise AssertionError(f"第 {n} 行找不到锚 {anchor!r}")
    return len("".join(lines[:n - 1]).encode("utf-8")) + len(line[:col].encode("utf-8"))


def reveal_in_line(n, start_anchor, end_anchor=None,
                   extend_left=0, extend_right=0, scroll_anchor=None):
    """在第 n 行选中「start_anchor 起、end_anchor 末」区间，视图自动滚入镜。

    init 样板属性行近 2000px，1600 窗口装不下，长行靠分段取景：拍 A 选
    class..data-duration、拍 B 选 data-track-index..行尾，两次选区移动
    即画面横移，口播跟着镜头讲四属性。

    跨进程实测（64 位 Python → 32 位 NPP 7.8.8，WOW64）：SCI_SETXOFFSET/
    SCI_LINESCROLL/SCI_GOTOLINE 的滚动在本通道不生效；SCI_SETSEL 会自动
    把选区滚到可见区，取景全靠它。参数序实测 wParam=左端、lParam=右端
    （与官方文档 SCI_SETSEL(caret, anchor) 相反）——以本机实测为准，
    升级 NPP 大版本后必须重测本函数。

    Scintilla 位置是 UTF-8 字节偏移，全部在 Python 侧按磁盘内容算好，
    只跨进程发纯数字消息（SCI_SEARCHINTARGET 的 lParam 是调用方缓冲区
    原指针，跨进程解引用无效，不能用）。

    end_anchor 缺省＝只选 start_anchor；extend_* 向两侧扩列，用来控制
    取景宽度（如 CDN 行选到版本号为止，避免选区到行尾把 URL 头部滚出框）。
    scroll_anchor=(行号, 锚)：垂直取景辅助，先把 caret 送到该位置逼视图
    滚动（用于展示规则块时选块底行，让整块入镜），再回目标行建选区。
    """
    text = read_file()
    lines = text.splitlines(keepends=True)
    if not 1 <= n <= len(lines):
        raise AssertionError(f"行号 {n} 越界（共 {len(lines)} 行）")
    line = lines[n - 1]
    c1 = line.find(start_anchor)
    if c1 < 0:
        raise AssertionError(f"第 {n} 行找不到起点锚 {start_anchor!r}")
    if end_anchor is None:
        c2 = c1 + len(start_anchor)
    else:
        hit = line.find(end_anchor, c1)
        if hit < 0:
            raise AssertionError(f"第 {n} 行找不到终点锚 {end_anchor!r}")
        c2 = hit + len(end_anchor)
    c1 = max(0, c1 - extend_left)
    c2 = min(len(line.rstrip("\r\n")), c2 + extend_right)
    prefix = "".join(lines[:n - 1])
    p1 = len(prefix.encode("utf-8")) + len(line[:c1].encode("utf-8"))
    p2 = len(prefix.encode("utf-8")) + len(line[:c2].encode("utf-8"))
    pend = len(prefix.encode("utf-8")) + len(line.rstrip("\r\n").encode("utf-8"))
    s = active_scintilla()
    # 垂直方向同理：SETSEL 只做「caret 刚好可见」的最小滚动，选区落在规则块
    # 开口行时块体在屏外下方。scroll_anchor=(底行号, 锚) 先把 caret 送到块底
    # 逼视图下压，再回开口行——此刻开口行已在镜内，后续 SETSEL 视图不动。
    if scroll_anchor is not None:
        sn, sa = scroll_anchor
        sp = _byte_position(sn, sa)
        _senda(s, SCI_SETSEL, sp, sp)
    # SETSEL 只保证 caret 端可见、且 caret 已在镜内时视图完全不动；从上一个
    # 右侧镜头直接选到中段，选区左半会留在屏外。三发序列强制左端贴左缘：
    # ① 折到行尾逼视图到最右 → ② 折到 p1（此刻在左外侧）逼回左缘
    # → ③ 正式建选区（p2 在可见区内，视图不再动）。三条连发无 sleep，
    # 30fps 录屏抓不到中间态。
    _senda(s, SCI_SETSEL, pend, pend)
    _senda(s, SCI_SETSEL, p1, p1)
    _senda(s, SCI_SETSEL, p1, p2)


def close():
    """关录制实例（每步均已 Ctrl+S，缓冲区与磁盘一致，不应弹保存框）。"""
    if hwnd:
        r.u.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE


def _activate():
    r.activate(hwnd)
    time.sleep(.2)


def read_file():
    with open(path, encoding="utf-8") as f:
        return f.read()


def line_of(substring, occurrence=1):
    """磁盘文件中 substring 第 occurrence 次命中的行号（1 起）。"""
    n = 0
    for i, line in enumerate(read_file().splitlines(), 1):
        if substring in line:
            n += 1
            if n == occurrence:
                return i
    raise AssertionError(f"文件中找不到 {substring!r}（第 {occurrence} 次）")


def save(check=None, timeout=1.5):
    """Ctrl+S；check(text) 为真才认为磁盘落盘成功。"""
    _activate()
    r.hotkey("CTRL", "S")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if check is None or check(read_file()):
            return
        time.sleep(.1)
    if check is not None and not check(read_file()):
        raise AssertionError("保存后磁盘内容未达预期")


def replace_all(find, repl):
    """Ctrl+H 替换对话框：find -> repl（全部替换）。

    对话框流程（已实测）：
      Ctrl+H → 焦点在查找框 → Ctrl+A/Delete 清空 → 输入 find
      → TAB 到替换框 → 粘贴 repl → Alt+A 全部替换
      → Enter 确认数量 → Esc 关闭。
    find 走逐字 Unicode 输入（中英通用），repl 走剪贴板整块粘贴。
    """
    _activate()
    r.hotkey("CTRL", "H")
    time.sleep(.55)
    r.hotkey("CTRL", "A")
    time.sleep(.12)
    r.tap("DELETE")
    time.sleep(.12)
    r.type_text(find, delay=.02)
    time.sleep(.2)
    r.tap("TAB")
    time.sleep(.18)
    r.paste(repl)
    time.sleep(.2)
    r.hotkey("ALT", "A")
    time.sleep(.7)
    r.tap("ENTER")
    time.sleep(.2)
    r.tap("ESC")
    time.sleep(.25)
    r.tap("HOME")
    time.sleep(.06)
    r.tap("HOME")
    time.sleep(.1)


def goto_line_end(n):
    """Ctrl+G 跳到第 n 行，END 到逻辑行尾。

    END 按两次：配置已关 word-wrap（SETTINGS_DIR/config.xml Wrap=no），
    一次即到行尾；双按是历史防御（wrap 开启时第一次只到视觉折行尾）。
    """
    _activate()
    r.hotkey("CTRL", "G")
    time.sleep(.5)
    r.type_text(str(n), delay=.03)
    time.sleep(.15)
    r.tap("ENTER")
    time.sleep(.4)
    r.tap("END")
    time.sleep(.08)
    r.tap("END")
    time.sleep(.12)


def goto_anchor_end(substring, occurrence=1):
    """按内容锚点跳到行尾。"""
    goto_line_end(line_of(substring, occurrence))


def insert_after_line(n, block):
    """在第 n 行之后插入整块文本。

    已在 NPP 配置关闭 MaitainIndent：Enter 新行光标停 col 1，
    缩进完全由 block 自带。注意不能按 HOME——Scintilla 的 HOME 在某些
    状态下会落到缩进后一位。
    """
    goto_line_end(n)
    r.tap("ENTER")
    time.sleep(.2)
    r.paste(block)
    time.sleep(.3)
    # 复位水平滚动（长行操作后视图可能停在右侧）；HOME 双按兼容 wrap 态
    r.tap("HOME")
    time.sleep(.06)
    r.tap("HOME")
    time.sleep(.1)


def insert_after_anchor(substring, block, occurrence=1):
    """在锚点行之后插块。"""
    insert_after_line(line_of(substring, occurrence), block)


def move_line_up(n):
    """Alt+Up：把第 n 行整体上移一行。

    NPP 默认 Ctrl+Shift+Up 在本机被后台程序拦截，已在 shortcuts.xml 把
    IDM 42014/42015 重映射到 Alt+Up/Down。
    """
    goto_line_end(n)
    r.hotkey("ALT", "UP")
    time.sleep(.25)


def move_line_down(n):
    """Alt+Down：把第 n 行整体下移一行。"""
    goto_line_end(n)
    r.hotkey("ALT", "DOWN")
    time.sleep(.25)
