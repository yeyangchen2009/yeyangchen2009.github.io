# -*- coding: utf-8 -*-
"""隔离 Edge（CDP 9222）生命周期与 tab 控制：hf-04 录屏专用。

- start_edge()：用隔离 profile 启动 Edge 并开 Studio；已在跑则直接复用。
- ensure_tabs()：保证同窗内有 Studio 与裸 player 两个 tab，处理 welcome 页。
- reload_tab()/eval_tab()/wait_for()：flatten session 直连，事件流按 id 过滤。
全部只读/只动隔离 profile，不碰用户主 Edge。
"""
import json
import subprocess
import time
import urllib.request

import websocket

CDP = "http://localhost:9222"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PROFILE_DIR = r"F:\_hftest\edge-cdp"
STUDIO_URL = "http://localhost:3002/"
PLAYER_URL = ("http://localhost:3002/api/projects/hf04-seek/preview"
              "?__hf_shader_loading=player")
STUDIO_NEEDLE = "localhost:3002/"
PLAYER_NEEDLE = "preview?__hf_shader_loading"

WELCOME_MARKERS = ("welcome", "newtab", "first-run", "new-device")


class CdpError(RuntimeError):
    pass


# ---------- HTTP /json ----------

def _http(path, method="GET"):
    req = urllib.request.Request(CDP + path, method=method)
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))


def pages():
    return [t for t in _http("/json") if t["type"] == "page"]


def find_page(needle, exclude=None):
    """按 URL 子串找 tab；exclude（子串或元组）命中则跳过。

    STUDIO_NEEDLE="localhost:3002/" 是 player URL 的子串，
    故找 Studio 必须 exclude PLAYER_NEEDLE，否则两者返回同一 tab。
    """
    if isinstance(exclude, str):
        exclude = (exclude,)
    for t in pages():
        if needle in t["url"] and not (exclude and any(x in t["url"] for x in exclude)):
            return t
    return None


def cdp_alive():
    try:
        _http("/json/version")
        return True
    except Exception:
        return False


# ---------- 启动 ----------

def start_edge(wait=25):
    """启动隔离 Edge（Studio tab）。已在跑则复用。返回 version info。"""
    if cdp_alive():
        return _http("/json/version")
    subprocess.Popen([
        EDGE_EXE,
        "--remote-debugging-port=9222",
        "--user-data-dir=" + PROFILE_DIR,
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=msEdgeWelcomeFLX",
        # 残留实例被强杀后重启不弹「还原页面」气泡（会挡 activate/前置）
        "--disable-session-crashed-bubble",
        "--hide-crash-restore-bubble",
        STUDIO_URL,
    ])
    t0 = time.time()
    while time.time() - t0 < wait:
        if cdp_alive():
            break
        time.sleep(0.5)
    else:
        raise CdpError("等不到 CDP 9222 上线")
    time.sleep(2.0)  # 浏览器/tab 初始化
    return _http("/json/version")


# ---------- browser-level ws（建/关/激活 tab） ----------

def _browser_ws():
    v = _http("/json/version")
    ws = websocket.create_connection(v["webSocketDebuggerUrl"], suppress_origin=True)
    ws.settimeout(8)
    return ws


def _bcmd(ws, method, params=None, sid=None, timeout=8):
    mid = getattr(_bcmd, "_i", 0) + 1
    _bcmd._i = mid
    msg = {"id": mid, "method": method, "params": params or {}}
    if sid:
        msg["sessionId"] = sid
    ws.send(json.dumps(msg))
    end = time.time() + timeout
    while time.time() < end:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            if "error" in r:
                raise CdpError("%s -> %s" % (method, r["error"]))
            return r.get("result", {})
    raise CdpError("CDP 超时: " + method)


def browser_new_tab(url):
    ws = _browser_ws()
    try:
        return _bcmd(ws, "Target.createTarget", {"url": url})["targetId"]
    finally:
        ws.close()


def browser_close_tab(tid):
    ws = _browser_ws()
    try:
        _bcmd(ws, "Target.closeTarget", {"targetId": tid})
    finally:
        ws.close()


def browser_activate(tid):
    ws = _browser_ws()
    try:
        _bcmd(ws, "Target.activateTarget", {"targetId": tid})
    finally:
        ws.close()


def dismiss_welcome():
    """welcome/newtab 等非本集 tab：先导航 about:blank，edge:// 拒绝就关 tab。"""
    for t in pages():
        url = t["url"].lower()
        if any(m in url for m in WELCOME_MARKERS):
            try:
                eval_tab(t["id"], "location.href='about:blank'")
            except CdpError:
                browser_close_tab(t["id"])
            time.sleep(0.5)


def devtools_open():
    """DevTools 前端在 /json 里是 devtools:// 的 page target（底停靠也算）。"""
    return any(t["url"].startswith("devtools://") for t in pages())


def ensure_tabs():
    """返回 (studio_tab, player_tab)，必要时建 tab。不切前台。"""
    studio = find_page(STUDIO_NEEDLE, exclude=PLAYER_NEEDLE)
    player = find_page(PLAYER_NEEDLE)
    if not studio:
        browser_new_tab(STUDIO_URL)
        time.sleep(1.5)
        studio = find_page(STUDIO_NEEDLE, exclude=PLAYER_NEEDLE)
    if not player:
        browser_new_tab(PLAYER_URL)
        time.sleep(2.0)
        player = find_page(PLAYER_NEEDLE)
    dismiss_welcome()
    if not studio or not player:
        raise CdpError("tab 不齐: studio=%s player=%s" % (bool(studio), bool(player)))
    return studio["id"], player["id"]


# ---------- page-level 直连 ----------

def _page_ws(tid):
    t = next((x for x in pages() if x["id"] == tid), None)
    if not t:
        raise CdpError("tab 不存在: " + tid)
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True)
    ws.settimeout(10)
    return ws


def eval_tab(tid, expr, await_promise=False, timeout=10):
    ws = _page_ws(tid)
    mid = 1
    try:
        ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate", "params": {
            "expression": expr, "returnByValue": True,
            "awaitPromise": await_promise}}))
        end = time.time() + timeout
        while time.time() < end:
            r = json.loads(ws.recv())
            if r.get("id") == mid:
                res = r.get("result", {})
                if "exceptionDetails" in res:
                    raise CdpError("JS 异常: " + json.dumps(
                        res["exceptionDetails"], ensure_ascii=False)[:300])
                return res.get("result", {}).get("value")
        raise CdpError("eval 超时: " + expr[:60])
    finally:
        ws.close()


def wait_for(tid, expr, timeout=15, interval=0.5):
    """轮询求值直到表达式返回真值。"""
    end = time.time() + timeout
    last = None
    while time.time() < end:
        try:
            v = eval_tab(tid, expr, timeout=5)
            if v:
                return v
            last = v
        except CdpError:
            pass
        time.sleep(interval)
    raise CdpError("等待条件超时(%ss): %s last=%s" % (timeout, expr[:80], last))


def reload_tab(tid, wait_ready=None, ready_timeout=15):
    """flatten attach 后 Page.reload（不碰 iframe contentWindow，避开 loading 卡死）。

    wait_ready: 可选 JS 表达式，reload 后轮询为真。
    """
    ws = _browser_ws()
    ws.settimeout(10)
    try:
        sid = _bcmd(ws, "Target.attachToTarget",
                    {"targetId": tid, "flatten": True})["sessionId"]
        _bcmd(ws, "Page.enable", sid=sid)
        _bcmd(ws, "Page.reload", {"ignoreCache": True}, sid=sid)
    finally:
        ws.close()
    if wait_ready:
        time.sleep(1.0)  # 导航最小间隔
        wait_for(tid, wait_ready, timeout=ready_timeout)


# ---------- hf-04 语义封装 ----------

PLAYER_READY = ("window.__playerReady === true && !!window.__timelines "
                "&& !!window.__timelines.main")


def player_seek(tid, t):
    eval_tab(tid, "window.__player.seek(%s)" % t)


def player_current(tid):
    return eval_tab(tid, "window.__player && window.__player.getTime()")


def prep_player_tab():
    """段⑤布景：裸 player tab 存在→reload→就绪→seek(0)。返回 tid。"""
    _, player = ensure_tabs()
    reload_tab(player, PLAYER_READY, ready_timeout=18)
    time.sleep(0.5)
    player_seek(player, 0)
    return player


def prep_studio_tab():
    """播放镜头布景：Studio tab reload→等 SPA＋player 挂载。返回 tid。"""
    studio, _ = ensure_tabs()
    # Studio 是 SPA；顶层 ready 标志在 iframe 内访问不到，按固定时间等编译
    reload_tab(studio)
    time.sleep(6.0)
    return studio


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        start_edge()
        s, p = ensure_tabs()
        print("studio:", s)
        print("player:", p)
