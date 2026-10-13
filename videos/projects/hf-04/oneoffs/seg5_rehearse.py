# -*- coding: utf-8 -*-
"""hf-04 段⑤彩排：裸 composition 窗口 + DevTools Console 亲手 __player.seek。

安全铁律（2026-10-12 事故后固化）：
  每个键鼠动作前必须 guard.assert_fg_isolated()；每个点击/拖拽前
  必须 guard.assert_point_isolated(x,y)。前台不是隔离 Edge（9222 实例）
  一律中止——用户回机操作时脚本自动让路，绝不碰用户 WT/主 Edge/NPP。

分步跑：
  python seg5_rehearse.py open     摆窗+确保 DevTools 开（底停靠）+截图
  python seg5_rehearse.py split    分隔条像素闭环拖到面板顶缘 555+fit+截图
  python seg5_rehearse.py zoom     CDP 合成键：reset 后 +2（z2, dpr 1.875）
  python seg5_rehearse.py seek     控制台十连打 seek，逐条断言 getTime+截图
  python seg5_rehearse.py close    关 DevTools 并验证
  python seg5_rehearse.py all      一次跑完整条链（约 40s）

2026-10-13 真机标定结论（probe_seek2/probe_split3/probe_layout/probe_seek10）：
  - 控制台输入框是自定义元素 DEVTOOLS-TEXT-EDITOR；控制台 tab 一打开
    activeElement 默认就是它，真实键盘直敲即可，禁止鼠标点输入行
    （z2 下坐标判读两次点偏、一次把 DevTools 点关）。
  - zoom 必须 CDP Input.dispatchKeyEvent 合成：真实键盘误触曾把 zoom
    推到 400%（dpr=6），console-view 高度挤成 0。定档 z2：Ctrl+0
    复位后两次 Ctrl+=（dpr=1.875，iw≈848/ih≈422，消息区 7–8 行）。
  - 分隔条只信截图像素：亮度阶跃检测行＝标签图标亮行＝面板真实顶缘
    +30；拖拽热区＝检测行+2（检测行本身及上方全空拖）；鼠标位移与
    面板顶缘 1:1 跟手。CDP innerWidth/Height 是逻辑视口，与屏幕几何
    脱节，不能用来反算分隔条位置。
  - 每条 seek 返回 undefined 占一历史行（一对约 55 物理像素）；消息区
    同屏约 3–4 条命令，「五回一样」靠画面重复叙事，不追求历史同屏。
"""
import ctypes
import json
import os
import sys
import time
import urllib.request

import websocket

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, "..", "..", "hf-03", "oneoffs"))
sys.path.insert(0, HERE)
import rec_automate as ra  # noqa: E402
import guard  # noqa: E402
import cdp_fit  # noqa: E402
import cdp_ctrl  # noqa: E402

# 独立分步运行也要八原语自动过闸（record_segments 导入本模块时幂等跳过）
guard.install_input_guards(ra)

# 取景窗必须与 record_segments.WND_* 同一规格：Win11 DWM 右缘 12px
# 透明带，外框 (-12,0,1624,928) 才让实体右缘到物理 1600，录区零穿帮
WND = (-12, 0, 1624, 928)
PANEL_TOP = 555                  # DevTools 面板真实顶缘目标（物理）
ROW_OFFSET = 30                  # 亮度检测行 = 顶缘 + 30（标签栏 32px）
SPLIT_X = 760
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
    """裸 player tab 就位：按 URL 认 target→物理置前 Edge→CDP 切 tab→摆窗。

    2026-10-13 实测：cdp_ctrl.browser_activate 走 Page.bringToFront，
    只切 tab 不抬 OS 窗口（终端启动脚本时前台仍是终端，hotkey 全落空）。
    必须先 guard.force_isolated_edge_foreground() 破前台锁物理置前。
    不调 ensure_tabs：edge:// 设置页不在 /json，会被误判 player 丢失而新开 tab。
    """
    tab = cdp_ctrl.find_page(cdp_ctrl.PLAYER_NEEDLE)
    if not tab:
        raise SystemExit("CDP 找不到裸 player tab，中止（布景应先 ensure_tabs）")
    hwnd = guard.force_isolated_edge_foreground()
    cdp_ctrl.browser_activate(tab["id"])   # 窗口已在前台，这步只负责切活动 tab
    time.sleep(0.6)
    guard.assert_fg_isolated()
    ra.move(hwnd, *WND)
    time.sleep(0.4)
    guard.assert_fg_isolated()
    return tab["id"]


def shot(name):
    p = os.path.join(SHOT_DIR, name + ".png")
    ra.screenshot(p, 1920, 1080)
    print("shot:", p, flush=True)


def safe_click(x, y):
    guard.assert_fg_isolated()
    guard.assert_point_isolated(x, y)
    ra.mouse_click(x, y)


# ---------- DevTools target 的 CDP 通道（edge webContents，suppress_origin） ----------

_mid = [0]


def dt_ws():
    ts = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json"))
    hits = [x for x in ts if x["url"].startswith("devtools://")]
    if not hits:
        return None
    return websocket.create_connection(
        hits[0]["webSocketDebuggerUrl"], max_size=None, suppress_origin=True)


def cdp_call(ws, method, params=None):
    _mid[0] += 1
    m = _mid[0]
    ws.send(json.dumps({"id": m, "method": method, "params": params or {}}))
    while True:
        r = json.loads(ws.recv())
        if r.get("id") == m:
            return r


def cdp_ev(ws, expr):
    r = cdp_call(ws, "Runtime.evaluate",
                 {"expression": expr, "returnByValue": True})
    return r.get("result", {}).get("result", {}).get("value")


def cdp_key(ws, code, vkc, k, ctrl=False):
    """合成按键给 DevTools 自身（不是被检页面）：zoom 唯一可靠通道。"""
    mods = 2 if ctrl else 0
    cdp_call(ws, "Input.dispatchKeyEvent",
             {"type": "rawKeyDown", "code": code,
              "windowsVirtualKeyCode": vkc, "key": k, "modifiers": mods})
    cdp_call(ws, "Input.dispatchKeyEvent",
             {"type": "keyUp", "code": code,
              "windowsVirtualKeyCode": vkc, "key": k, "modifiers": mods})


def player_ws(tid):
    """被检 player tab 的长连（十条 seek 全程复用）。

    2026-10-13 实测：cdp_ctrl.eval_tab 每次 pages()(/json 2.0s)＋新建
    ws(~2s)＋关闭，单次 getTime 4.1s，十条白花 41s。长连后每次 eval
    是毫秒级 round-trip，step_seek 从 93s 回收至 ~50s。
    """
    ts = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json"))
    t = next((x for x in ts if x["id"] == tid), None)
    if not t:
        raise SystemExit("player tab 已消失: " + tid)
    return websocket.create_connection(
        t["webSocketDebuggerUrl"], max_size=None, suppress_origin=True)


def ensure_focus(ws):
    """控制台 DEVTOOLS-TEXT-EDITOR 必须是 activeElement；丢焦则 CDP 兜底。"""
    tag = cdp_ev(ws, "(document.activeElement&&document.activeElement.tagName)||''")
    if tag != "DEVTOOLS-TEXT-EDITOR":
        cdp_ev(ws, "(function(){var es=document.querySelectorAll("
                   "'devtools-text-editor');for(var i=es.length-1;i>=0;i--){"
                   "var r=es[i].getBoundingClientRect();"
                   "if(r.width>0&&r.height>0){es[i].focus();return;}}})()")
        time.sleep(0.2)
        tag = cdp_ev(ws, "(document.activeElement&&"
                         "document.activeElement.tagName)||''")
    return tag


# ---------- 分步动作 ----------

def step_open():
    prep_window()
    if not cdp_ctrl.devtools_open():
        guard.assert_fg_isolated()
        ra.hotkey("ctrl", "shift", "j")
        time.sleep(2.2)
    else:
        print("devtools already open", flush=True)
    if not cdp_ctrl.devtools_open():
        raise SystemExit("DevTools 打开失败")
    shot("30-open")


def _detect_label_row():
    """亮度阶跃检测标签图标亮行（物理 y）。检测行＝面板真实顶缘+30。

    必须在 seek(0) 黑舞台态调用：舞台有亮色内容后行均值差判据失效。
    """
    tmp = os.path.join(SHOT_DIR, "split-probe.png")
    ra.screenshot(tmp, 1920, 1080)
    from PIL import Image
    px = Image.open(tmp).convert("L").load()
    prev = None
    for y in range(300, 850):
        vals = [px[x, y] for x in range(200, 1500, 8)]
        avg = sum(vals) / len(vals)
        if prev is not None and avg - prev > 25:
            return y
        prev = avg
    raise RuntimeError("检测不到面板顶缘亮行（seek(0) 黑舞台前提是否成立？）")


def _drag(y0, y1, step=6):
    guard.assert_fg_isolated()
    guard.assert_point_isolated(SPLIT_X, y0)
    ra.mouse_move(SPLIT_X, y0)
    time.sleep(0.15)
    ra.mouse_down()
    try:
        d = step if y1 > y0 else -step
        y = y0
        while (d > 0 and y < y1) or (d < 0 and y > y1):
            y += d
            guard.assert_point_isolated(SPLIT_X, y)
            ra.mouse_move(SPLIT_X, y)
            time.sleep(0.025)
    finally:
        ra.mouse_up()
    time.sleep(0.6)


def step_split():
    pid = prep_window()
    # 检测需要全黑舞台：布景态本应为 0，长连查时＋必要时回零（不入控制台历史）
    pws = player_ws(pid)
    try:
        t = cdp_ev(pws, "window.__player.getTime()")
        if t is None or abs(float(t)) > 0.01:
            cdp_ev(pws, "window.__player.seek(0)")
            time.sleep(0.4)
    finally:
        pws.close()
    for i in range(3):
        row = _detect_label_row()
        edge = row - ROW_OFFSET
        print("split round %d: row=%d edge=%d" % (i, row, edge), flush=True)
        if abs(edge - PANEL_TOP) <= 5:
            break
        _drag(row + 2, row + 2 + (PANEL_TOP - edge))
    else:
        raise SystemExit("split 三轮未收敛到顶缘 %d" % PANEL_TOP)
    cdp_fit.inject_once()             # 视口改变后必须重注 fit
    time.sleep(0.6)
    shot("31-split-fit")


def step_zoom():
    prep_window()
    ws = dt_ws()
    if ws is None:
        raise SystemExit("DevTools 未开，无法 zoom")
    try:
        cdp_key(ws, "Digit0", 48, "0", ctrl=True)   # 复位 z0
        time.sleep(0.5)
        for _ in range(2):
            cdp_key(ws, "Equal", 0xBB, "=", ctrl=True)
            time.sleep(0.35)
        dpr = cdp_ev(ws, "devicePixelRatio")
    finally:
        ws.close()
    print("zoom z2, dpr =", dpr, flush=True)
    if dpr is None or abs(float(dpr) - 1.875) > 0.05:
        raise SystemExit("zoom 定档失败：dpr=%s（期望 1.875）" % dpr)
    shot("32-zoom")


# 命令必须带 window. 全称：成片画面要与口播「window 点 __player」一致；
# e 之后连着五回 2.4（粗稿「五回画面一模一样」），截图 33-seek-a..j。
# 时间点按 s4 编排反推（title 入 2.0–3.4、subtitle 入 6.0–7.2）：
# 2.4 标题半透明浮半路、3 标题就位、6.3 副标题半路、9 全就位、0 空台。
CMDS = [
    ("a", "window.__player.seek(2.4)", 2.4),
    ("b", "window.__player.seek(3)", 3),
    ("c", "window.__player.seek(6.3)", 6.3),
    ("d", "window.__player.seek(9)", 9),
    ("e", "window.__player.seek(0)", 0),
    ("f", "window.__player.seek(2.4)", 2.4),
    ("g", "window.__player.seek(2.4)", 2.4),
    ("h", "window.__player.seek(2.4)", 2.4),
    ("i", "window.__player.seek(2.4)", 2.4),
    ("j", "window.__player.seek(2.4)", 2.4),
]


def step_seek():
    pid = prep_window()
    ws = dt_ws()
    if ws is None:
        raise SystemExit("DevTools 未开，无法 seek")
    pws = player_ws(pid)
    fails = []
    try:
        # 清台（Ctrl+L 在编辑器聚焦时＝清控制台，实测不丢焦）。
        if ensure_focus(ws) != "DEVTOOLS-TEXT-EDITOR":
            raise SystemExit("控制台编辑器无法聚焦")
        guard.assert_fg_isolated()
        ra.hotkey("ctrl", "l")
        time.sleep(0.4)
        # 静默回零：CDP 直 eval 不进控制台历史，保证十条命令从空台起步
        # （正式布景 seek(0) 过；分步单跑 seek 时这里兜底）。
        cdp_ev(pws, "window.__player.seek(0)")
        time.sleep(0.3)
        for tag, cmd, expect in CMDS:
            guard.assert_fg_isolated()
            foc = ensure_focus(ws)
            ra.type_text(cmd, delay=0.05)
            time.sleep(0.12)
            ra.tap("enter")
            time.sleep(1.2)
            got = cdp_ev(pws, "window.__player.getTime()")
            shot("33-seek-" + tag)
            ok_t = got is not None and abs(float(got) - expect) < 0.01
            print("%s: getTime=%s expect=%s %s focus=%s" % (
                tag, got, expect, "OK" if ok_t else "**TIME FAIL**", foc),
                flush=True)
            if not ok_t:
                fails.append(tag)
            if foc != "DEVTOOLS-TEXT-EDITOR":
                fails.append(tag + ":focus")
    finally:
        ws.close()
        pws.close()
    if fails:
        raise SystemExit("seek 序列失败：%s" % fails)


def step_close():
    prep_window()
    if cdp_ctrl.devtools_open():
        guard.assert_fg_isolated()
        ra.hotkey("ctrl", "shift", "j")
        time.sleep(1.2)
    if cdp_ctrl.devtools_open():
        raise SystemExit("DevTools 未关闭")
    shot("34-closed")


def step_all():
    step_open()
    step_split()
    step_zoom()
    step_seek()
    step_close()
    print("ALL STEPS PASS", flush=True)


if __name__ == "__main__":
    _dpi()
    what = sys.argv[1] if len(sys.argv) > 1 else "open"
    {
        "open": step_open,
        "split": step_split,
        "zoom": step_zoom,
        "seek": step_seek,
        "close": step_close,
        "all": step_all,
    }[what]()
