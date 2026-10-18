# -*- coding: utf-8 -*-
"""hf-06 录屏安全闸：键鼠/窗口动作前强制校验前台属于「隔离录制环境」。

沿用 hf-04 误触事故后固化、hf-05 实践过的铁律：每次键鼠注入前过闸，
前台/落点必须属于本集隔离环境身份之一，否则立即 abort。hf-06 两身份
（无浏览器、无 CDP、无 dev server——check/normalize/beats 都直接读磁盘）：

  1. 隔离 NPP：类名 Notepad++、标题含 _hftest\\hf06-media 的窗口所属进程
     （F:\\_hftest\\npp-local 便携实例；用户日常 NPP 标题不含该串，永不命中）；
  2. 隔离终端：标题为 hf06-rec 的 WT 窗口（-w new 独立窗口，
     --suppressApplicationTitle 锁名；绝不按 WindowsTerminal 进程名批量认
     ——用户 WT 是另一个进程）。

用户一回机把自己的窗口切前台，下一个注入立即 UnsafeForeground 中止。
"""
import ctypes
from ctypes import wintypes

u = ctypes.windll.user32

NPP_TITLE_NEEDLE = r"_hftest\hf06-media"
TERM_TITLE = "hf06-rec"


class UnsafeForeground(RuntimeError):
    pass


# ---------- 两身份解析 ----------

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
    """当前隔离环境两身份 pid 集合（每动作现查，不缓存窗口归属）。"""
    pids = set()
    for _, cn, title, pid in _enum_windows():
        if cn == "Notepad++" and NPP_TITLE_NEEDLE in title:
            pids.add(pid)
        if title.strip().startswith(TERM_TITLE):
            pids.add(pid)
    return pids


def identify(pid):
    """给报错用的人类可读身份串。"""
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
    root = u.GetAncestor(h, 2) or h  # GA_ROOT = 2
    pid = wintypes.DWORD()
    u.GetWindowThreadProcessId(root, ctypes.byref(pid))
    return pid.value, h, root


# ---------- 白名单闸（NPP/终端） ----------

def assert_fg_safe():
    """键鼠动作前调用：前台必须是隔离两身份之一。"""
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


# ---------- 注入原语统一装闸 ----------

GUARDED_PRIMITIVES = ("tap", "hotkey", "type_text", "paste",
                      "mouse_move", "mouse_down", "mouse_up", "mouse_click")


def install_input_guards(rec, checker=None):
    """给 rec_automate 模块的八个注入原语统一套前台白名单闸（幂等）。

    每击键/点击在「注入的那一瞬」复查前台：序列中途用户回机切窗，
    下一个注入立即 UnsafeForeground 中止。activate、move(hwnd)、screenshot、
    定向 SendMessage 不包——非原语的调用方须自己显式过闸。
    """
    if checker is None:
        checker = assert_fg_safe
    if getattr(rec, "_hf06_guards_installed", False):
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
    rec._hf06_guards_installed = True
