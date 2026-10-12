# -*- coding: utf-8 -*-
"""对照三种 seek 入口在 reload 后的 clip 显隐联动。
组1 __timelines.main.seek / 组2 __player.seek / 组3 __player.renderSeek。
每轮：CDP Page.reload（忽略期间事件）-> 重连 page ws -> 等待 player ready -> seek -> 探针。
"""
import json
import sys
import time
import urllib.request

import websocket

CDP = "http://localhost:9222"


def tabs():
    return [t for t in json.load(urllib.request.urlopen(CDP + "/json")) if t["type"] == "page"]


def preview_tab():
    return [t for t in tabs() if "preview?__hf" in t["url"]][0]


def browser_ws():
    v = json.load(urllib.request.urlopen(CDP + "/json/version"))
    return v["webSocketDebuggerUrl"]


def reload_target(tid):
    ws = websocket.create_connection(browser_ws(), suppress_origin=True)
    ws.settimeout(5)
    ws.send(json.dumps({"id": 1, "method": "Target.attachToTarget",
                        "params": {"targetId": tid, "flatten": True}}))
    sid = None
    end = time.time() + 5
    while time.time() < end:
        try:
            r = json.loads(ws.recv())
            if r.get("id") == 1:
                sid = r["result"]["sessionId"]
                break
        except websocket.WebSocketTimeoutException:
            break
    ws.send(json.dumps({"id": 2, "method": "Page.reload", "sessionId": sid}))
    time.sleep(0.5)
    ws.close()


def page_conn():
    t = preview_tab()
    ws = websocket.create_connection(t["webSocketDebuggerUrl"], suppress_origin=True)
    ws.settimeout(8)
    return ws


def ev(ws, expr, await_promise=False):
    mid = ev.i
    ev.i += 1
    ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate",
                        "params": {"expression": expr, "awaitPromise": await_promise}}))
    end = time.time() + 10
    while time.time() < end:
        r = json.loads(ws.recv())
        if r.get("id") == mid:
            return r
    raise TimeoutError(expr)


ev.i = 100


def wait_ready(ws, seconds=12):
    end = time.time() + seconds
    while time.time() < end:
        r = ev(ws, "String(window.__playerReady === true && !!window.__timelines && !!window.__timelines.main)")
        if r.get("result", {}).get("result", {}).get("value") == "true":
            return
        time.sleep(0.5)
    raise TimeoutError("player not ready")


PROBE = """(function(){var cs=id=>getComputedStyle(document.querySelector(id));
 return JSON.stringify({pt:window.__player?window.__player.getTime():null,
  tl:window.__timelines.main.time(),
  title:cs('#title').display+'/'+cs('#title').visibility+'/'+cs('#title').opacity,
  card:cs('#card').visibility+'/'+cs('#title').opacity+'/'+cs('#card').opacity,
  sub:cs('#subtitle').display+'/'+cs('#subtitle').opacity});})()"""


def round_trip(label, seek_expr, await_promise=False):
    tid = preview_tab()["id"]
    reload_target(tid)
    time.sleep(2.5)
    ws = page_conn()
    try:
        wait_ready(ws)
        time.sleep(0.5)
        ev(ws, seek_expr, await_promise=await_promise)
        time.sleep(0.6)
        r = ev(ws, PROBE)
        print(label, "->", r["result"]["result"].get("value"), flush=True)
    finally:
        ws.close()


if __name__ == "__main__":
    round_trip("tl.seek(2.4)      ", "window.__timelines.main.seek(2.4)")
    round_trip("player.seek(2.4)  ", "window.__player.seek(2.4)")
    round_trip("renderSeek(2.4)   ", "Promise.resolve(window.__player.renderSeek(2.4)).then(String)", await_promise=True)
