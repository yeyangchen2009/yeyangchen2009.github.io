# -*- coding: utf-8 -*-
"""给裸 preview 页注入舞台 fit 缩放（录屏辅助，不经控制台历史，观众无感）。

裸 player 页 #root 固定 1920x1080、不随视口缩放；段⑤要画面与 DevTools 同框，
需把舞台等比 fit 进可视区。CDP 连接期内用 addScriptToEvaluateOnNewDocument
持久注册（reload 不丢），并对当前页立即执行一次。MutationObserver 兜底
runtime 重写 #root 行内 style。

用法：
  python cdp_fit.py on     # 注册并立即注入（连接保持时有效）
  python cdp_fit.py once   # 只对当前页注入一次（reload 即失效，用于彩排）
"""
import json
import sys
import time
import urllib.request

import websocket

CDP = "http://127.0.0.1:9222"  # localhost 走 IPv6 每次 /json 白等 2s（见 cdp_ctrl）

FIT_JS = r"""
(function () {
  if (window.__hfRecFitInstalled) return;
  window.__hfRecFitInstalled = true;
  var st = document.createElement('style');
  st.textContent = 'html,body{overflow:hidden!important;background:#0a0a0a!important;margin:0!important;}'
    + '#root{transform-origin:top left!important;}';
  (document.head || document.documentElement).appendChild(st);
  var W = 1920, H = 1080, guard = false;
  function fit() {
    var r = document.querySelector('#root');
    if (!r) return;
    var sc = Math.min(window.innerWidth / W, window.innerHeight / H);
    var x = (window.innerWidth - W * sc) / 2;
    var y = (window.innerHeight - H * sc) / 2;
    guard = true;
    r.style.transform = 'translate(' + x + 'px,' + y + 'px) scale(' + sc + ')';
    guard = false;
  }
  window.addEventListener('resize', fit);
  new MutationObserver(function () {
    if (guard) return;
    var r = document.querySelector('#root');
    if (r && /(^|[;\s])transform\s*:/.test(r.getAttribute('style') || '') === false) fit();
  }).observe(document.documentElement, { childList: true, subtree: true, attributes: true });
  var timer = setInterval(function () {
    if (document.querySelector('#root')) { fit(); clearInterval(timer); }
  }, 100);
  fit();
})();
"""


def _preview_tab():
    tabs = [t for t in json.load(urllib.request.urlopen(CDP + "/json")) if t["type"] == "page"]
    return [t for t in tabs if "preview?__hf" in t["url"]][0]


def _send(ws, mid, method, params=None):
    ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
    end = time.time() + 8
    while time.time() < end:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r
    raise TimeoutError(method)


def inject_once():
    """对当前页立即注入一次。"""
    ws = websocket.create_connection(_preview_tab()["webSocketDebuggerUrl"], suppress_origin=True)
    ws.settimeout(8)
    r = _send(ws, 1, "Runtime.evaluate", {"expression": FIT_JS})
    ws.close()
    return r


def inject_persistent():
    """注册到新文档（reload 不丢）+ 当前页立即注入。返回保持中的 ws（勿关）。"""
    ws = websocket.create_connection(_preview_tab()["webSocketDebuggerUrl"], suppress_origin=True)
    ws.settimeout(8)
    _send(ws, 1, "Page.enable")
    r = _send(ws, 2, "Page.addScriptToEvaluateOnNewDocument", {"source": FIT_JS})
    _send(ws, 3, "Runtime.evaluate", {"expression": FIT_JS})
    print("registered:", r.get("result", {}))
    return ws


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "once"
    if what == "once":
        print(inject_once())
    elif what == "on":
        ws = inject_persistent()
        print("persistent injection active, Ctrl-C to drop")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            ws.close()
