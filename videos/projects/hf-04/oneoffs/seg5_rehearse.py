# -*- coding: utf-8 -*-
"""hf-04 段⑤彩排：裸 composition 窗口 + DevTools Console 亲手 __player.seek。

安全铁律（2026-10-12 事故后固化）：
  每个键鼠动作前必须 guard.assert_fg_isolated()；每个点击/拖拽前
  必须 guard.assert_point_isolated(x,y)。前台不是隔离 Edge（9222 实例）
  一律中止——用户回机操作时脚本自动让路，绝不碰用户 WT/主 Edge/NPP。

分步跑：
  python seg5_rehearse.py open     摆窗+开 DevTools（底停靠）+截图
  python seg5_rehearse.py split    拖高分隔条+注入 fit+截图
  python seg5_rehearse.py zoom     放大 DevTools 字体+截图
  python seg5_rehearse.py seek     键入 __player.seek 序列，每条截图
  python seg5_rehearse.py close    关 DevTools
"""
import ctypes
import os
import sys
import time

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "hf-03", "oneoffs"))
sys.path.insert(0, HERE)
import rec_automate as ra  # noqa: E402
import guard  # noqa: E402
import cdp_fit  # noqa: E402
import cdp_ctrl  # noqa: E402

# 独立分步运行也要八原语自动过闸（record_segments 导入本模块时幂等跳过）
guard.install_input_guards(ra)

WND = (0, 0, 1600, 920)          # 取景窗：与录屏严格同宽同高
SPLIT_Y = 700                    # DevTools 分隔条目标 y（物理）
CONSOLE_Y = 830                  # 控制台输入行点击 y（物理，split 后）
SHOT_DIR = os.path.join(HERE, "seg5-shots")
os.makedirs(SHOT_DIR, exist_ok=True)


def _dpi():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def prep_window():
    """CDP 直连裸 player tab：按 URL 认 target→激活→验前台 pid→摆窗前置。

    tab 身份以 CDP /json 的 url 为准（preview 页 <title> 不含 URL，旧版靠
    窗口标题＋前台 fallback 会在同进程的 Studio tab 上误开 DevTools）；
    窗身份仍以前台 pid==cdp_pid 过闸，不放松校验。tab 缺失时自动建齐，
    但不 reload/seek——页状态（PLAYER_READY、seek(0)）由布景方负责。
    """
    tab = cdp_ctrl.find_page(cdp_ctrl.PLAYER_NEEDLE)
    if not tab:
        cdp_ctrl.start_edge()
        cdp_ctrl.ensure_tabs()
        time.sleep(1.0)
        tab = cdp_ctrl.find_page(cdp_ctrl.PLAYER_NEEDLE)
    if not tab:
        raise SystemExit("CDP 找不到裸 player tab，中止")
    cdp_ctrl.browser_activate(tab["id"])
    time.sleep(0.8)
    hwnd, pid = guard.fg_hwnd_pid()
    if pid != guard.cdp_pid():
        raise SystemExit("激活 player 后前台不是隔离 Edge（pid=%s），中止" % pid)
    ra.move(hwnd, *WND)
    ra.activate(hwnd)
    time.sleep(0.4)
    guard.assert_fg_isolated()
    return hwnd


def shot(name):
    p = os.path.join(SHOT_DIR, name + ".png")
    ra.screenshot(p, 1920, 1080)
    print("shot:", p, flush=True)


def safe_click(x, y):
    guard.assert_fg_isolated()
    guard.assert_point_isolated(x, y)
    ra.mouse_click(x, y)


def step_open():
    prep_window()
    ra.hotkey("ctrl", "shift", "j")    # profile 记忆：直接底部停靠打开
    time.sleep(2.0)
    guard.assert_fg_isolated()
    shot("30-open")


def step_split():
    prep_window()
    # 分隔条在画面区底缘（约 y=420）；起点/终点都必须落在隔离 Edge 内
    x = 760
    guard.assert_fg_isolated()
    guard.assert_point_isolated(x, 420)
    ra.mouse_move(x, 420)
    time.sleep(0.2)
    ra.mouse_down()
    try:
        for y in range(440, SPLIT_Y + 1, 15):
            guard.assert_point_isolated(x, y)
            ra.mouse_move(x, y)
            time.sleep(0.03)
    finally:
        ra.mouse_up()
    time.sleep(0.8)
    cdp_fit.inject_once()             # resize 后注入 fit
    time.sleep(0.6)
    shot("31-split-fit")


def _ctrl_zoom(times):
    u = ra.u
    for _ in range(times):
        guard.assert_fg_isolated()            # 直接 keybd_event 绕过原语，手动过闸
        u.keybd_event(0x11, 0, 0, 0)          # Ctrl
        u.keybd_event(0xBB, 0, 0, 0)          # =
        time.sleep(0.03)
        u.keybd_event(0xBB, 0, 0x0002, 0)
        u.keybd_event(0x11, 0, 0x0002, 0)
        time.sleep(0.18)


def step_zoom():
    prep_window()
    safe_click(760, CONSOLE_Y)
    time.sleep(0.3)
    _ctrl_zoom(4)
    time.sleep(0.4)
    shot("32-zoom")


# 命令必须带 window. 全称：成片画面要与口播「window 点 __player」一致；
# e 之后连着五回 2.4（粗稿「五回画面一模一样」），截图 33-seek-a..j
CMDS = [
    ("a", "window.__player.seek(2.4)"),
    ("b", "window.__player.seek(3)"),
    ("c", "window.__player.seek(6.3)"),
    ("d", "window.__player.seek(9)"),
    ("e", "window.__player.seek(0)"),
    ("f", "window.__player.seek(2.4)"),
    ("g", "window.__player.seek(2.4)"),
    ("h", "window.__player.seek(2.4)"),
    ("i", "window.__player.seek(2.4)"),
    ("j", "window.__player.seek(2.4)"),
]


def step_seek():
    prep_window()
    time.sleep(0.3)
    safe_click(760, CONSOLE_Y)
    time.sleep(0.4)
    ra.hotkey("ctrl", "l")            # 清控制台
    time.sleep(0.3)
    for tag, cmd in CMDS:
        guard.assert_fg_isolated()
        ra.type_text(cmd, delay=0.05)
        time.sleep(0.15)
        ra.tap("enter")
        time.sleep(1.2)
        shot("33-seek-" + tag)


def step_close():
    prep_window()
    ra.hotkey("ctrl", "shift", "j")
    time.sleep(1.0)
    shot("34-closed")


if __name__ == "__main__":
    _dpi()
    what = sys.argv[1] if len(sys.argv) > 1 else "open"
    {
        "open": step_open,
        "split": step_split,
        "zoom": step_zoom,
        "seek": step_seek,
        "close": step_close,
    }[what]()
