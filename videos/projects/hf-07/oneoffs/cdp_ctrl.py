# -*- coding: utf-8 -*-
"""隔离 Edge（CDP 9222）生命周期与 tab 控制：hf-07 录屏专用（净改自 hf-04）。

- start_edge()：用隔离 profile 启动 Edge 并直接开裸 player；已在跑则复用。
- ensure_player_tab()：保证 player tab 存在，处理 welcome 页。
- reload_tab()/eval_tab()/wait_for()：flatten session 直连，事件流按 id 过滤。
只动隔离 profile F:\\_hftest\\edge-cdp，不碰用户主 Edge。

前置：3021 后台 preview server 已由 take t00 真起
（`hyperframes preview v1 --background --no-open --port 3021`，PROBE E9）。
PLAYER_URL 按 hf-04 同形路由推导，**录前彩排 curl/CDP 真机验证**
（若 404，用 /json 看真实路由后只改本常量）。
"""
import json
import subprocess
import time
import urllib.request

import websocket

# 必须 127.0.0.1：localhost 在本机 urllib 先走 IPv6 ::1，/json 每次多等 ~2s
# （hf-04 实测 2.0s→0.002s）。
CDP = "http://127.0.0.1:9222"
EDGE_EXE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PROFILE_DIR = r"F:\_hftest\edge-cdp"
PORT = 3021
STUDIO_URL = "http://127.0.0.1:%d/" % PORT
# TODO(彩排验证)：hf-04 路由为 /api/projects/<id>/preview?__hf_shader_loading=player
PLAYER_URL = ("http://127.0.0.1:%d/api/projects/v1/preview"
              "?__hf_shader_loading=player" % PORT)
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


def find_page(needle):
    """按 URL 子串找 tab。"""
    for t in pages():
        if needle in t["url"]:
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
    """启动隔离 Edge（直接开 player tab）。已在跑则复用。返回 version info。"""
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
        PLAYER_URL,
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


def ensure_player_tab():
    """保证 player tab 存在。不切前台。返回 tab id。"""
    player = find_page(PLAYER_NEEDLE)
    if not player:
        browser_new_tab(PLAYER_URL)
        time.sleep(2.0)
        player = find_page(PLAYER_NEEDLE)
    dismiss_welcome()
    if not player:
        raise CdpError("player tab 起不来（PLAYER_URL 是否 404？）: " + PLAYER_URL)
    return player["id"]


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


# ---------- hf player 语义封装 ----------

PLAYER_READY = ("window.__playerReady === true && !!window.__timelines "
                "&& !!window.__timelines.main && !!window.__player")


def player_seek(tid, t):
    eval_tab(tid, "window.__player.seek(%s)" % t)


def player_play(tid):
    eval_tab(tid, "window.__player.play()")


def player_pause(tid):
    eval_tab(tid, "window.__player.pause && window.__player.pause()")


def player_current(tid):
    return eval_tab(tid, "window.__player && window.__player.getTime()")


# 沉浸式翻译扩展在每个网页右缘注入 #immersive-translate-popup（Shadow DOM
# 红圆浮动钮），hf-04 实拍贴 player 视口右缘入镜。display:none 宿主即连
# shadow 一起不渲染。reload 后注入失效，须每次 reload 后重注。
HIDE_EXT_JS = r"""
(function(){
  function inject(){
    if(!document.getElementById('__rec-hide-ext')){
      var s=document.createElement('style');
      s.id='__rec-hide-ext';
      s.textContent='#immersive-translate-popup{display:none!important;visibility:hidden!important}';
      (document.head||document.documentElement).appendChild(s);
    }
    var el=document.getElementById('immersive-translate-popup');
    if(el){el.style.setProperty('display','none','important');}
  }
  inject();
  if(!window.__recHideObs){
    window.__recHideObs=new MutationObserver(function(){inject();});
    window.__recHideObs.observe(document.documentElement,{childList:true,subtree:true});
  }
  return 'ok';
})()
"""


def hide_page_extensions(tid):
    """隐藏浏览器扩展往页面注入的浮动钮（沉浸式翻译等），含延迟注入兜底。"""
    eval_tab(tid, HIDE_EXT_JS)


def prep_player_tab():
    """t01 布景：player tab 存在→reload→就绪→隐藏扩展→seek(0)。返回 tid。"""
    tid = ensure_player_tab()
    reload_tab(tid, PLAYER_READY, ready_timeout=18)
    time.sleep(0.5)
    hide_page_extensions(tid)
    player_seek(tid, 0)
    return tid


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        start_edge()
        p = ensure_player_tab()
        print("player:", p)
