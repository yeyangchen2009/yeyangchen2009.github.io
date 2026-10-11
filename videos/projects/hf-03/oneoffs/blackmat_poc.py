# -*- coding: utf-8 -*-
"""黑垫 POC：无边框纯黑窗 (0,900,1640,110)，验证能否遮住入镜窗底缝。
import rec_automate 附带 PerMonitor DPI 感知，否则 tk 坐标被 1.5x 虚拟化。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec_automate as r  # noqa: F401  (DPI 感知 + ctypes/u)
import tkinter as tk

root = tk.Tk()
root.overrideredirect(True)
root.geometry("1640x110+0+900")
root.configure(bg="black")
root.attributes("-topmost", False)
root.update_idletasks()
root.update()
hwnd = int(root.frame(), 16)
print("black hwnd:", hex(hwnd), flush=True)

# 放到 NPP（0x2212a6）紧后面：SetWindowPos(hwnd, hwndInsertAfter=锚窗)
r.u.SetWindowPos(hwnd, 0x2212a6, 0, 0, 0, 0,
                 0x0010 | 0x0002 | 0x0001)  # NOACTIVATE|NOMOVE|NOSIZE
print("z-order set behind NPP", flush=True)
root.mainloop()
