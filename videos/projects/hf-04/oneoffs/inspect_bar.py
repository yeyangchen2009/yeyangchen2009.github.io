# -*- coding: utf-8 -*-
"""枚举屏幕底部可疑贴靠条窗口的类名/进程，一次性别工具。"""
import ctypes
import os
from ctypes import wintypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

u = ctypes.windll.user32
k = ctypes.windll.kernel32
rows = []


def cb(h, _):
    if not u.IsWindowVisible(h):
        return True
    r = wintypes.RECT()
    u.GetWindowRect(h, ctypes.byref(r))
    if r.bottom - r.top > 0 and r.top > 680 and r.left < 1100 and r.bottom < 1010:
        cls = ctypes.create_unicode_buffer(256)
        u.GetClassNameW(h, cls, 256)
        pid = wintypes.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(pid))
        n = u.GetWindowTextLengthW(h)
        b = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(h, b, n + 1)
        hp = k.OpenProcess(0x1000, False, pid.value)
        name = ctypes.create_unicode_buffer(260)
        pname = "?"
        if hp:
            sz = wintypes.DWORD(260)
            if k.QueryFullProcessImageNameW(hp, 0, name, ctypes.byref(sz)):
                pname = os.path.basename(name.value)
            k.CloseHandle(hp)
        rows.append((hex(h), cls.value, b.value[:30],
                     (r.left, r.top, r.right, r.bottom), pname))
    return True


u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(cb), 0)
for x in rows:
    print(x)
