# -*- coding: utf-8 -*-
"""黑垫窗：遮住 Win11 入镜窗底缘圆角透明缝。

920 高的 NPP/Edge 底缘（y≈915–920）有几 px 圆角透明区，后方用户最大化
WT（绝不能动）里的红字/白字会从缝里透入录制区。解决办法不是加高窗口
（加高破坏 probe 定型的构图），而是在入镜窗紧后垫一个无边框纯黑窗：
入镜窗不透明的状态栏把垫子挡住，只在透明缝处露黑，观感同「窗口外的
黑桌面」。

Tk 窗必须在创建它的线程里泵消息，故 daemon 线程跑 mainloop；behind()
只是一次 Win32 SetWindowPos，可从主线程直接调。进程的 PerMonitor DPI
感知由 rec_automate 在主线程 import 时声明（同进程线程继承），geometry
用物理坐标，不被 1.5x 虚拟化。
"""
import threading

import tkinter as tk


class BlackMat:
    def __init__(self, x=0, y=900, w=1640, h=110):
        self._x, self._y, self._w, self._h = x, y, w, h
        self.hwnd = None
        self._root = None
        self._u = None
        self.ready = threading.Event()
        self._closed = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()
        if not self.ready.wait(5):
            raise RuntimeError("黑垫窗 5s 内未就绪")

    def _run(self):
        import rec_automate as r
        self._u = r.u
        root = tk.Tk()
        root.overrideredirect(True)               # 无标题栏/边框
        root.geometry(f"{self._w}x{self._h}+{self._x}+{self._y}")
        root.configure(bg="black")
        root.attributes("-topmost", False)
        root.update_idletasks()
        root.update()
        self.hwnd = int(root.frame(), 16)
        self._root = root
        # 解除 tkinter 模块级默认根引用（它在主线程持有 Tk 对象，
        # 进程退出时会在错误线程删解释器，报 Tcl_AsyncDelete）
        tk._default_root = None
        self.ready.set()
        root.mainloop()
        # Tcl 解释器必须在创建它的线程内销毁，否则进程退出时
        # Tcl_AsyncDelete: async handler deleted by the wrong thread
        root.destroy()
        self._closed.set()

    def behind(self, anchor_hwnd):
        """把黑垫插到 anchor（入镜窗）z 序紧后一位。

        录制中前台始终是 anchor，其他窗（含 hf03-check/用户 WT）全部
        位于黑垫下方，透明缝处只能看到黑色。"""
        self._u.SetWindowPos(
            self.hwnd, anchor_hwnd, 0, 0, 0, 0,
            0x0010 | 0x0002 | 0x0001)  # NOACTIVATE | NOMOVE | NOSIZE

    def close(self):
        if self._root is not None:
            root = self._root
            self._root = None
            root.after(0, root.quit)  # 让 mainloop 在 Tk 线程返回
            self._closed.wait(2)
            self._t.join(2)
