# -*- coding: utf-8 -*-
"""hf-03 录屏：通过 CDP 让 Edge Studio 页 reload 归位（段③播放前用）。

dev Edge 实例开着 --remote-debugging-port=9222，本脚本找 dev server
(localhost:3002) 的 page target，发 Page.reload(ignoreCache=true)，
等浏览器报 loadEventFired 后返回，保证播放头回到 t=0。
用法：python cdp_reload.py
"""
import json
import sys
import time
import urllib.request

import websocket  # websocket-client

CDP = "http://127.0.0.1:9222"
PAGE_MATCH = "3002"


def main():
    with urllib.request.urlopen(CDP + "/json", timeout=5) as resp:
        targets = json.load(resp)
    pages = [t for t in targets
             if t.get("type") == "page" and PAGE_MATCH in t.get("url", "")]
    if not pages:
        raise RuntimeError(f"CDP 中找不到 url 含 {PAGE_MATCH} 的 page target："
                           + ", ".join(t.get("url", "?") for t in targets))
    ws_url = pages[0]["webSocketDebuggerUrl"]
    print("reload:", pages[0]["url"])
    # Chromium 校验 Origin：websocket-client 默认发 Origin 头会被 403，
    # suppress_origin 后握手不带 Origin（同 cdp-shot.js 的手写握手）。
    ws = websocket.create_connection(ws_url, timeout=10, suppress_origin=True)
    try:
        ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
        ws.recv()
        ws.send(json.dumps({"id": 2, "method": "Page.reload",
                            "params": {"ignoreCache": True}}))
        t0 = time.time()
        while time.time() - t0 < 12:
            msg = json.loads(ws.recv())
            if msg.get("method") == "Page.loadEventFired":
                print("loadEventFired  %.1fs" % (time.time() - t0))
                return
        print("警告：12s 内未等到 loadEventFired，继续（dev 热更可能无需重载）")
    finally:
        ws.close()


if __name__ == "__main__":
    sys.exit(main())
