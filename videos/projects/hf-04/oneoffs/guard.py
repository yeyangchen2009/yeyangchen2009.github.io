# -*- coding: utf-8 -*-
"""录屏安全闸：键鼠/窗口动作前强制校验前台属于「隔离录制环境」。

2026-10-12 教训：用户回到电脑前把自己的 WT 切到前台，脚本未察觉，
mouse_click/拖拽落到用户 WT 上。此后所有自动化脚本在每次键鼠动作前
必须过闸：前台/落点必须属于本集隔离环境三身份之一，否则立即 abort：

  1. 隔离 Edge：监听 127.0.0.1:9222 的进程（--user-data-dir=F:\\_hftest\\edge-cdp）；
  2. 隔离 NPP：类名 Notepad++、标题含 _hftest\\hf04-seek 的窗口所属进程
     （F:\\_hftest\\npp-local 实例；用户日常 NPP 标题不含该串，永不命中）；
  3. 隔离终端：标题为 hf04-rec 的 WT 窗口所属进程（-w new 独立窗口，
     绝不按 WindowsTerminal 进程名批量认——用户 WT 是另一个进程）。

段⑤只允许隔离 Edge 时用 assert_fg_isolated/assert_point_isolated（Edge 专闸）；
跨 NPP/终端的录屏编排用 assert_fg_safe/assert_point_safe（白名单闸）。
"""
import ctypes
import subprocess
from ctypes import wintypes

u = ctypes.windll.user32

CDP_PORT = 9222
NPP_TITLE_NEEDLE = r"_hftest\hf04-seek"
TERM_TITLE = "hf04-rec"
_cdp_pid_cache = None


class UnsafeForeground(RuntimeError):
    pass


# ---------- 三身份解析 ----------

def cdp_pid():
    """监听 CDP 端口的进程 pid（隔离 Edge 实例的权威身份）。"""
    global _cdp_pid_cache
    if _cdp_pid_cache:
        return _cdp_pid_cache
    # 中文 Windows 下 netstat 输出 GBK；PYTHONUTF8=1 时 text=True 会按 utf-8
    # 解码直接抛 UnicodeDecodeError，这里按字节抓再容错解码。
    # 不能加 -p TCP：隔离 Edge 的 CDP 只绑 IPv6 [::1]:9222，-p TCP 只列 v4，
    # 会误判「Edge 未启动」；全量 netstat 同时含 TCPv6（2026-10-12 实测）。
    out = subprocess.run(
        ["netstat", "-ano"],
        capture_output=True, timeout=10).stdout.decode("gbk", "replace")
    pids = set()
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 5 and f[1].endswith(":%d" % CDP_PORT) and f[3] == "LISTENING":
            pids.add(int(f[4]))
    if not pids:
        raise UnsafeForeground("找不到监听 %d 的进程，隔离 Edge 未启动" % CDP_PORT)
    if len(pids) > 1:
        raise UnsafeForeground("端口 %d 有多个监听 pid: %s" % (CDP_PORT, pids))
    _cdp_pid_cache = pids.pop()
    return _cdp_pid_cache


def _enum_windows():
    """[(hwnd, class, title, pid)] 所有可见顶层窗。"""
    rows = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(wnd, _):
        if not u.IsWindowVisible(wnd):
            return True
        cn = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(wnd, cn, 64)
        ln = u.GetWindowTextLengthW(wnd)
        b = ctypes.create_unicode_buffer(ln + 1)
        u.GetWindowTextW(wnd, b, ln + 1)
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(wnd, ctypes.byref(pid))
        rows.append((wnd, cn.value, b.value, pid.value))
        return True

    u.EnumWindows(cb, 0)
    return rows


def isolated_pids():
    """当前隔离环境三身份 pid 集合（每动作现查，不缓存窗口归属）。"""
    pids = set()
    try:
        pids.add(cdp_pid())
    except UnsafeForeground:
        pass  # Edge 没开时，NPP/终端段仍应可过闸
    for _, cn, title, pid in _enum_windows():
        if cn == "Notepad++" and NPP_TITLE_NEEDLE in title:
            pids.add(pid)
        if title.strip().startswith(TERM_TITLE):
            pids.add(pid)
    return pids


def identify(pid):
    """给报错用的人类可读身份串。"""
    try:
        if pid == cdp_pid():
            return "隔离 Edge"
    except UnsafeForeground:
        pass
    for _, cn, title, p in _enum_windows():
        if p == pid:
            if cn == "Notepad++":
                return "非隔离 NPP（%s）" % title[:40]
            if "WindowsTerminal" in cn or cn == "CASCADIA_HOSTING_WINDOW_CLASS":
                return "非隔离终端（%s）" % title[:40]
            return "%s（%s）" % (cn or "未知窗", title[:40])
    return "pid=%s" % pid


# ---------- 现场探测 ----------

def fg_hwnd_pid():
    hwnd = u.GetForegroundWindow()
    pid = wintypes.DWORD()
    u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return hwnd, pid.value


def window_pid_at(x, y):
    class P(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    h = u.WindowFromPoint(P(int(x), int(y)))
    # WindowFromPoint 可能命中子窗（Chrome_RenderWidgetHostHWND），取根 hwnd 的 pid
    root = u.GetAncestor(h, 2) or h  # GA_ROOT = 2
    pid = wintypes.DWORD()
    u.GetWindowThreadProcessId(root, ctypes.byref(pid))
    return pid.value, h, root


# ---------- 白名单闸（NPP/Edge/终端） ----------

def assert_fg_safe():
    """键鼠动作前调用：前台必须是隔离三身份之一。"""
    hwnd, pid = fg_hwnd_pid()
    allow = isolated_pids()
    if pid not in allow:
        raise UnsafeForeground(
            "前台 %s 不属于隔离录制环境（允许 pid=%s）——用户可能正在用机，全部动作中止"
            % (identify(pid), sorted(allow)))
    return hwnd


def assert_point_safe(x, y):
    """点击/拖拽前调用：落点窗口也必须属于隔离环境。"""
    pid, child, root = window_pid_at(x, y)
    allow = isolated_pids()
    if pid not in allow:
        raise UnsafeForeground(
            "落点 (%d,%d) 命中 %s 而非隔离环境 pid=%s，中止"
            % (x, y, identify(pid), sorted(allow)))
    return root


# ---------- Edge 专闸（段⑤） ----------

def assert_fg_isolated():
    """前台必须是隔离 Edge（CDP 9222 实例）。Edge 未开直接报错。"""
    hwnd, pid = fg_hwnd_pid()
    want = cdp_pid()
    if pid != want:
        raise UnsafeForeground(
            "前台 %s 不是隔离 Edge pid=%s——用户可能正在用机，全部动作中止"
            % (identify(pid), want))
    return hwnd


def assert_point_isolated(x, y):
    """落点窗口必须属于隔离 Edge。"""
    pid, child, root = window_pid_at(x, y)
    want = cdp_pid()
    if pid != want:
        raise UnsafeForeground(
            "落点 (%d,%d) 命中 %s 而非隔离 Edge pid=%s，中止"
            % (x, y, identify(pid), want))
    return root


# ---------- 注入原语统一装闸 ----------

GUARDED_PRIMITIVES = ("tap", "hotkey", "type_text", "paste",
                      "mouse_move", "mouse_down", "mouse_up", "mouse_click")


def install_input_guards(rec, checker=None):
    """给 rec_automate 模块的八个注入原语统一套前台白名单闸（幂等）。

    record_segments 与 seg5_rehearse（含独立分步运行）共享同一 rec_automate
    模块对象，任一方 import 时装一次即可；装过后再调直接返回。每击键/点击/
    粘贴在「注入的那一瞬」复查前台：序列中途用户回机切窗，下一个注入立即
    UnsafeForeground 中止。默认 checker 为三身份白名单闸（Edge 是其子集，
    故 Edge 专段同样适用，专段另有显式 assert_fg_isolated/落点闸收紧）。
    activate、move(hwnd)、screenshot、定向 SendMessage、直接 keybd_event
    不包——非原语的调用方须自己显式过闸。
    """
    if checker is None:
        checker = assert_fg_safe
    if getattr(rec, "_hf04_guards_installed", False):
        return
    for name in GUARDED_PRIMITIVES:
        orig = getattr(rec, name)

        def make(fn):
            def guarded(*a, **k):
                checker()
                return fn(*a, **k)
            guarded.__name__ = "guarded_" + fn.__name__
            return guarded

        setattr(rec, name, make(orig))
    rec._hf04_guards_installed = True
