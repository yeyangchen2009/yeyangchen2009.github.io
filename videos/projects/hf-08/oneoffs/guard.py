# -*- coding: utf-8 -*-
"""hf-08 录屏安全闸：键鼠/窗口动作前强制校验前台属于「隔离录制环境」。

沿用 hf-04 误触事故后固化、hf-05/hf-06 实践过的铁律：每次键鼠注入前过闸，
前台/落点必须属于本集隔离环境身份之一，否则立即 abort。hf-08 两身份
（无浏览器、无 CDP、无 dev server——render 自开的无头 Chrome 不算身份）：

 1. 隔离 NPP：类名 Notepad++、标题含 chunk-3WG63KFW.js 的窗口所属进程
    （F:\\_hftest\\npp-local 便携实例，仅 src-blackbar 一张 freeze 用；
    用户日常 NPP 不会开着 npx 缓存里的 chunk，永不命中）；
 2. 隔离终端：标题为 hf08-rec 的 WT 窗口（-w new 独立窗口，--title hf08-rec
    --suppressApplicationTitle；t2 的 PowerShell 是 cmd 内敲入的子进程而非
    第二 tab，标题恒锁；绝不按 WindowsTerminal 进程名批量认）。

⚠️ 白名单按**具体顶层窗 HWND** 认，不按 PID（2026-10-22 热录事故实证）：
`wt -w new` 的新窗口与用户主 WT 同属一个 WindowsTerminal.exe 进程，
若按 PID 放白名单，hf08-rec 窗存在期间，同一进程里跑 Claude Code 的
另一窗口也会被判为隔离环境——activate 落空时打字会静直流向错误窗口。
HWND 精确到「标题匹配的那个窗」，同进程的邻居窗不在白名单。

用户一回机把自己的窗口切前台，下一个注入立即 UnsafeForeground 中止。
"""
import ctypes
from ctypes import wintypes

u = ctypes.windll.user32

NPP_TITLE_NEEDLE = "chunk-3WG63KFW.js"
TERM_TITLE = "hf08-rec"


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


def isolated_windows():
    """当前隔离环境白名单：{hwnd: (class, title, pid)}，每动作现查不缓存。

    认窗不认进程：WT 的 -w new 新窗与用户主窗同 PID，按 PID 判会把
    同进程的 Claude Code 窗一起放行（2026-10-22 洞穿事故）。
    """
    win = {}
    for hwnd, cn, title, pid in _enum_windows():
        if cn == "Notepad++" and NPP_TITLE_NEEDLE in title:
            win[hwnd] = (cn, title, pid)
        if title.strip().startswith(TERM_TITLE):
            win[hwnd] = (cn, title, pid)
    return win


def isolated_pids():
    """白名单窗所属 pid 集合（仅日志/排查用；判定一律走 HWND）。"""
    return {info[2] for info in isolated_windows().values()}


def identify(pid):
    """给报错用的人类可读身份串（按 pid 反查，同 pid 多窗取首个）。"""
    for _, cn, title, p in _enum_windows():
        if p == pid:
            if cn == "Notepad++":
                return "非隔离 NPP（%s）" % title[:40]
            if "WindowsTerminal" in cn or cn == "CASCADIA_HOSTING_WINDOW_CLASS":
                return "非隔离终端（%s）" % title[:40]
            return "%s（%s）" % (cn or "未知窗", title[:40])
    return "pid=%s" % pid


def identify_hwnd(hwnd):
    """给报错用：hwnd 的 class/标题/pid 精确身份串。"""
    for h, cn, title, p in _enum_windows():
        if h == hwnd:
            kind = ("非隔离 NPP" if cn == "Notepad++"
                    else "非隔离终端" if "WindowsTerminal" in cn
                    or cn == "CASCADIA_HOSTING_WINDOW_CLASS"
                    else cn or "未知窗")
            return "%s hwnd=%s pid=%s「%s」" % (kind, hwnd, p, title.strip()[:50])
    return "hwnd=%s（已隐藏或销毁）" % hwnd


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
    """键鼠动作前调用：前台窗必须就是隔离白名单里那个具体 HWND。"""
    hwnd, pid = fg_hwnd_pid()
    allow = isolated_windows()
    if hwnd not in allow:
        raise UnsafeForeground(
            "前台 %s 不是隔离录制窗（允许 hwnd=%s）——用户可能正在用机或"
            "activate 落空，全部动作中止"
            % (identify_hwnd(hwnd),
               sorted("%s「%s」" % (h, (t or "").strip()[:30])
                      for h, (_, t, _) in allow.items())))
    return hwnd


def assert_point_safe(x, y):
    """点击/拖拽前调用：落点根窗也必须是隔离白名单 HWND。"""
    pid, child, root = window_pid_at(x, y)
    allow = isolated_windows()
    if root not in allow:
        raise UnsafeForeground(
            "落点 (%d,%d) 命中 %s 而非隔离录制窗 hwnd=%s，中止"
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
    if getattr(rec, "_hf08_guards_installed", False):
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
    rec._hf08_guards_installed = True
