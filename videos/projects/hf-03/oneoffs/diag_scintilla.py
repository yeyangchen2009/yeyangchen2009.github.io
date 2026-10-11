# -*- coding: utf-8 -*-
"""诊断：枚举当前 NPP 实例全部 Scintilla 控件，逐个读回状态并实测 SETSEL。"""
import ctypes
import os
import sys
from ctypes import wintypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec_automate as r
import npp_ops as n

SCI_GETLENGTH = 2006
SCI_GETLINECOUNT = 2154
SCI_GETCURRENTPOS = 2008
SCI_GETSELECTIONSTART = 2189
SCI_GETSELECTIONEND = 2190
SCI_GETZOOM = 2374
SCI_SETSEL = 2160

n.launch(r"F:\_hftest\hf03-npptest\index.html")
print("NPP hwnd:", hex(n.hwnd))

sa = n._senda

for i, s in enumerate(n._scintillas()):
    rc = wintypes.RECT()
    r.u.GetWindowRect(s, ctypes.byref(rc))
    vis = r.u.IsWindowVisible(s)
    length = sa(s, SCI_GETLENGTH, 0, 0)
    lines = sa(s, SCI_GETLINECOUNT, 0, 0)
    pos = sa(s, SCI_GETCURRENTPOS, 0, 0)
    zoom = sa(s, SCI_GETZOOM, 0, 0)
    # 实测：发 SETSEL(900,920) 再读回
    sa(s, SCI_SETSEL, 900, 920)
    sel_a = sa(s, SCI_GETSELECTIONSTART, 0, 0)
    sel_b = sa(s, SCI_GETSELECTIONEND, 0, 0)
    print(f"[{i}] hwnd={hex(s)} vis={vis} rect=({rc.left},{rc.top},{rc.right},{rc.bottom}) "
          f"len={length} lines={lines} pos={pos} zoom={zoom} "
          f"after SETSEL -> ({sel_a},{sel_b})")

act = n.active_scintilla()
print("active_scintilla() ->", hex(act))
