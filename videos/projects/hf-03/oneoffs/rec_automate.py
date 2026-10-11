# -*- coding: utf-8 -*-
"""Windows 桌面自动化底座（零依赖，ctypes）——hf-03 录屏专用。

提供窗口查找/激活/定位、键盘输入（逐键 ASCII）、剪贴板整块粘贴、
屏幕截图。所有输入最终走 keybd_event/SendInput 等效路径。
"""
import ctypes
import time
from ctypes import wintypes

# PerMonitorV2 DPI 感知：本机显示缩放 150%。不声明的话，SetCursorPos/GetWindowRect
# 等一切坐标都会被系统虚拟化（虚拟 1280×720 ↔ 物理 1920×1080），
# 导致按物理截图坐标点击时被再次 ×1.5、飞出屏幕。必须在任何坐标调用前设置。
# 注意：SetProcessDpiAwarenessContext(-4) 在本机 git-bash 启动的 python 中
# 返回 0（失败但不抛异常），必须检查返回值，否则进程静默停留在 DPI unaware，
# 后续一切坐标被系统虚拟化（1280×720↔1920×1080）。shcore(2) 实测可靠。
if not ctypes.windll.user32.SetProcessDpiAwarenessContext(-4):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

u = ctypes.windll.user32
k = ctypes.windll.kernel32

# ---------- 窗口 ----------

SW_RESTORE = 9


def find_window(title_substring):
    """按标题子串找顶层窗口，返回 hwnd。"""
    result = [None]

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(hwnd, _):
        if u.IsWindowVisible(hwnd):
            n = u.GetWindowTextLengthW(hwnd)
            if n:
                b = ctypes.create_unicode_buffer(n + 1)
                u.GetWindowTextW(hwnd, b, n + 1)
                if title_substring.lower() in b.value.lower():
                    result[0] = hwnd
                    return False
        return True

    u.EnumWindows(cb, 0)
    return result[0]


def activate(hwnd):
    """强制前台激活（AttachThreadInput 绕过前台锁）。"""
    fg = u.GetForegroundWindow()
    fg_tid = u.GetWindowThreadProcessId(fg, None)
    cur_tid = k.GetCurrentThreadId()
    attached = u.AttachThreadInput(cur_tid, fg_tid, True) if fg_tid != cur_tid else False
    try:
        if u.IsIconic(hwnd):
            u.ShowWindow(hwnd, SW_RESTORE)
        u.SetForegroundWindow(hwnd)
        u.BringWindowToTop(hwnd)
    finally:
        if attached:
            u.AttachThreadInput(cur_tid, fg_tid, False)
    time.sleep(0.25)


def move(hwnd, x, y, w, h):
    u.MoveWindow(hwnd, x, y, w, h, True)


imm32 = ctypes.windll.imm32


def _set_ime(hwnd, open_status):
    """对窗口本身及其 Scintilla 子控件设置 IME 开关。"""
    targets = [hwnd]

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def cb(child, _):
        b = ctypes.create_unicode_buffer(32)
        u.GetClassNameW(child, b, 32)
        if b.value == "Scintilla":
            targets.append(child)
        return True

    u.EnumChildWindows(hwnd, cb, 0)

    for t in targets:
        himc = imm32.ImmGetContext(t)
        if himc:
            imm32.ImmSetOpenStatus(himc, open_status)
            imm32.ImmReleaseContext(t, himc)


def disable_ime(hwnd):
    """关闭中文输入法（逐键打 ASCII 前必须调用）。"""
    _set_ime(hwnd, False)


def enable_ime(hwnd):
    _set_ime(hwnd, True)


# ---------- 键盘 ----------

KEYEVENTF_KEYUP = 0x0002

VK = {
    "SHIFT": 0x10, "CTRL": 0x11, "ALT": 0x12,
    "ENTER": 0x0D, "ESC": 0x1B, "BACK": 0x08, "TAB": 0x09,
    "HOME": 0x24, "END": 0x23, "DELETE": 0x2E,
    "UP": 0x26, "DOWN": 0x28, "LEFT": 0x25, "RIGHT": 0x27,
    "PGDN": 0x22, "PGUP": 0x21,
    "SPACE": 0x20,
}
for _c in range(1, 13):
    VK[f"F{_c}"] = 0x70 + _c - 1
for _i in range(26):
    VK[chr(ord("A") + _i)] = 0x41 + _i

# ASCII -> (虚拟键码, 是否需要 Shift)
OEM1 = 0xBA  # ;:
OEM_PLUS = 0xBB  # =+
OEM_COMMA = 0xBC  # ,<
OEM_MINUS = 0xBD  # -_
OEM_PERIOD = 0xBE  # .>
OEM_2 = 0xBF  # /?
OEM_4 = 0xDB  # [{
OEM_5 = 0xDC  # \\|
OEM_6 = 0xDD  # ]}
OEM_7 = 0xDE  # '"
OEM_3 = 0xC0  # `~


def _ascii_vk(ch):
    o = ord(ch)
    if ch in " \t":
        return 0x20, False
    if "0" <= ch <= "9":
        return 0x30 + (o - 0x30), False
    if "a" <= ch <= "z":
        return 0x41 + (o - 0x61), False
    if "A" <= ch <= "Z":
        return 0x41 + (o - 0x41), True
    table = {
        ";": (OEM1, False), ":": (OEM1, True),
        "=": (OEM_PLUS, False), "+": (OEM_PLUS, True),
        ",": (OEM_COMMA, False), "<": (OEM_COMMA, True),
        "-": (OEM_MINUS, False), "_": (OEM_MINUS, True),
        ".": (OEM_PERIOD, False), ">": (OEM_PERIOD, True),
        "/": (OEM_2, False), "?": (OEM_2, True),
        "[": (OEM_4, False), "{": (OEM_4, True),
        "\\": (OEM_5, False), "|": (OEM_5, True),
        "]": (OEM_6, False), "}": (OEM_6, True),
        "'": (OEM_7, False), '"': (OEM_7, True),
        "`": (OEM_3, False), "~": (OEM_3, True),
    }
    if ch in table:
        return table[ch]
    raise ValueError(f"不支持逐键输入的字符: {ch!r}")


def _tap_vk(vk, shift=False, hold=0.02):
    if shift:
        u.keybd_event(VK["SHIFT"], 0, 0, 0)
    u.keybd_event(vk, 0, 0, 0)
    time.sleep(hold)
    u.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    if shift:
        u.keybd_event(VK["SHIFT"], 0, KEYEVENTF_KEYUP, 0)


def tap(name, hold=0.02):
    _tap_vk(VK[name.upper()], hold=hold)


def hotkey(*names):
    vks = [VK[n.upper()] for n in names]
    for v in vks:
        u.keybd_event(v, 0, 0, 0)
        time.sleep(0.02)
    for v in reversed(vks):
        u.keybd_event(v, 0, KEYEVENTF_KEYUP, 0)


INPUT_KEYBOARD = 1
KEYEVENTF_UNICODE = 0x0004


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT),
                ("padding", ctypes.c_ubyte * 32)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD),
                ("u", INPUT_UNION)]


u.SendInput.restype = wintypes.UINT
u.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]


def _send_unicode(ch, key_up):
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.u.ki.wScan = ord(ch)
    inp.u.ki.dwFlags = KEYEVENTF_UNICODE | (KEYEVENTF_KEYUP if key_up else 0)
    sent = u.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    if sent != 1:
        raise OSError(f"SendInput 失败: {ch!r}")


def type_text(text, delay=0.045):
    """逐字符输入（Unicode 注入，绕过键盘布局与任何 IME，中英通用）。"""
    for ch in text:
        _send_unicode(ch, False)
        time.sleep(0.02)
        _send_unicode(ch, True)
        time.sleep(delay)


# 旧名兼容
type_ascii = type_text


# ---------- 剪贴板粘贴 ----------

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


k.GlobalAlloc.restype = wintypes.HGLOBAL
k.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
k.GlobalLock.restype = ctypes.c_void_p
k.GlobalLock.argtypes = [wintypes.HGLOBAL]
k.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
u.SetClipboardData.restype = wintypes.HANDLE
u.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]


def set_clipboard(text):
    data = (text + "\0").encode("utf-16-le")
    h_mem = k.GlobalAlloc(GMEM_MOVEABLE, len(data))
    if not h_mem:
        raise MemoryError("GlobalAlloc 失败")
    ptr = k.GlobalLock(h_mem)
    ctypes.memmove(ptr, data, len(data))
    k.GlobalUnlock(h_mem)
    if not u.OpenClipboard(0):
        raise OSError("OpenClipboard 失败")
    try:
        u.EmptyClipboard()
        if not u.SetClipboardData(CF_UNICODETEXT, h_mem):
            raise OSError("SetClipboardData 失败")
    finally:
        u.CloseClipboard()


def paste(text, pause=0.35):
    """整块写入剪贴板并 Ctrl+V（中文/长文本走这里）。"""
    set_clipboard(text)
    time.sleep(0.12)
    hotkey("CTRL", "V")
    time.sleep(pause)


# ---------- 鼠标 ----------

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


def mouse_move(x, y):
    u.SetCursorPos(int(x), int(y))


def mouse_down():
    u.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)


def mouse_up():
    u.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)


def mouse_click(x=None, y=None, hold=.05):
    """真实鼠标左键点击（会移动系统光标，录屏可见）。"""
    if x is not None and y is not None:
        mouse_move(x, y)
        time.sleep(.15)
    mouse_down()
    time.sleep(hold)
    mouse_up()


# ---------- 截图 ----------

def screenshot(path, w=1920, h=1080):
    """整屏截图（走 PowerShell System.Drawing，实测最稳）。"""
    import subprocess
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
        f"$b=New-Object System.Drawing.Bitmap({w},{h});"
        "$g=[System.Drawing.Graphics]::FromImage($b);"
        "$g.CopyFromScreen(0,0,0,0,$b.Size);"
        f"$b.Save('{path}');"
        "$g.Dispose();$b.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
