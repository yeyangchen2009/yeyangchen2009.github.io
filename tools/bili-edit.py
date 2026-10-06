#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B 站视频稿件编辑工具：查看稿件分 P / 修改分 P 名。

biliup CLI 只提供 upload/append/list/show 等命令，不支持编辑已有稿件；
其底层库中虽有 edit 方法但未暴露为子命令。本工具走创作者中心 app
同口径接口（依据 biliup 1.2.11 源码 crates/biliup/src/uploader/bilibili.rs）：

    回显 GET  https://member.bilibili.com/x/client/archive/view?access_key=..&aid=..
    提交 POST https://member.bilibili.com/x/vu/app/edit/full

biliup 格式 cookies.json 中自带 token_info.access_token，无需另行登录。
凭证仅在进程内部使用，不打印、不入日志。

典型用法：
    # 查看默认稿件（朱士行 BV1xxHz65E6n）的分 P
    python tools/bili-edit.py

    # 查看任意稿件
    python tools/bili-edit.py --bvid BV1xxHz65E6n
    python tools/bili-edit.py --aid 117380248241781

    # 把 P2 改名为「升级版」（先 dry-run 预览）
    python tools/bili-edit.py --index 2 --name "升级版：……"
    # 确认无误后真正提交
    python tools/bili-edit.py --index 2 --name "升级版：……" --commit

    # 更换稿件整体封面（B 站稿件只有一个封面，非每分 P 各一个）
    python tools/bili-edit.py --cover cover.png          # 先预览
    python tools/bili-edit.py --cover cover.png --commit # 上传并提交

凭证路径优先级：--cookie > 环境变量 BILIUP_COOKIE > 内置默认路径。
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import time
import urllib.parse
import urllib.request

DEFAULT_COOKIE = r"D:\Code\poju-zyz\zyz\cookies.json"
DEFAULT_AID = "117380248241781"  # 朱士行稿件 BV1xxHz65E6n
APP_KEY = "4409e2ce8ffd12b8"     # AppKeyStore::BiliTV
APP_SEC = "59b43e04ad6965f34319062b478f83dd"
UA = ("Mozilla/5.0 BiliDroid/7.80.0 (bbcallen@gmail.com) os/android model/MI 6 "
      "mobi_app/android build/7800300 channel/bili innerVer/7800310 osVer/13 network/2")
WEB_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")


def load_web_cookies(cookie_file):
    """读 biliup cookie_info.cookies，返回 (Cookie 头, bili_jct)。"""
    doc = json.load(open(cookie_file, encoding="utf-8"))
    jar = {c["name"]: str(c["value"])
           for c in doc["cookie_info"]["cookies"]}
    for must in ("SESSDATA", "bili_jct"):
        if must not in jar:
            sys.exit(f"cookie 缺少必需字段 {must}，请先 python -m biliup login")
    header = "; ".join(f"{k}={v}" for k, v in jar.items())
    return header, jar["bili_jct"]


def cover_up(cookie_file, image_path):
    """上传封面（web 接口 x/vu/web/cover/up），返回封面 url。"""
    cookie_header, csrf = load_web_cookies(cookie_file)
    with open(image_path, "rb") as f:
        raw = f.read()
    mime = "image/png" if raw.startswith(b"\x89PNG") else "image/jpeg"
    body = urllib.parse.urlencode({
        "cover": f"data:{mime};base64,{base64.b64encode(raw).decode()}",
        "csrf": csrf,
    }).encode()
    req = urllib.request.Request(
        "https://member.bilibili.com/x/vu/web/cover/up", data=body,
        headers={"User-Agent": WEB_UA, "Cookie": cookie_header,
                 "Content-Type": "application/x-www-form-urlencoded",
                 "Referer": "https://member.bilibili.com/"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read().decode("utf-8"))
    if res.get("code") != 0:
        sys.exit(f"封面上传失败: {res.get('code')} {res.get('message')}")
    return res["data"]["url"]


def http_json(url, data=None):
    """发 GET（data=None）或 POST application/json，返回解析后的 JSON。"""
    headers = {"User-Agent": UA}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers,
                                 method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def resolve_aid(args):
    """确定稿件 aid：显式 --aid 优先，否则 --bvid 走公开接口转换。"""
    if args.aid:
        return str(args.aid)
    if args.bvid:
        res = http_json("https://api.bilibili.com/x/web-interface/view?"
                        + urllib.parse.urlencode({"bvid": args.bvid}))
        if res.get("code") != 0:
            sys.exit(f"bvid 查询失败: {res.get('code')} {res.get('message')}")
        return str(res["data"]["aid"])
    return DEFAULT_AID


def fetch_studio(access_key, aid):
    """回显稿件，返回 (archive, videos)；videos 每项只留 title/filename/desc。"""
    q = urllib.parse.urlencode({"access_key": access_key, "aid": aid})
    view = http_json(f"https://member.bilibili.com/x/client/archive/view?{q}")
    if view.get("code") != 0:
        sys.exit(f"稿件回显失败: {view.get('code')} {view.get('message')}")
    data = view["data"]
    archive = dict(data["archive"])
    archive.pop("limited_free", None)
    videos = [{
        "title": v.get("title"),
        "filename": v["filename"],
        "desc": v.get("desc", ""),
    } for v in data["videos"]]
    return archive, videos


def submit_edit(access_key, body):
    """全量回写稿件（编辑接口语义＝提交完整 archive + videos）。"""
    payload = {
        "access_key": access_key,
        "appkey": APP_KEY,
        "build": 7800300,
        "c_locale": "zh-Hans_CN",
        "channel": "bili",
        "disable_rcmd": 0,
        "mobi_app": "android",
        "platform": "android",
        "s_locale": "zh-Hans_CN",
        "statistics": '"appId":1,"platform":3,"version":"7.80.0","abtest":""',
        "ts": int(time.time()),
    }
    # 参数按字典序拼接（对齐 serde BTreeMap 行为），md5(encoded + appsec)
    encoded = urllib.parse.urlencode(sorted(payload.items()))
    payload["sign"] = hashlib.md5((encoded + APP_SEC).encode()).hexdigest()
    url = ("https://member.bilibili.com/x/vu/app/edit/full?"
           + urllib.parse.urlencode(sorted(payload.items())))
    return http_json(url, data=json.dumps(body).encode("utf-8"))


def main():
    # Windows 控制台默认 GBK，统一为 UTF-8 输出，避免中文乱码
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    parser = argparse.ArgumentParser(
        description="B 站视频稿件编辑：查看分 P / 改分 P 名（创作者中心同口径接口）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cookie",
                        help="biliup cookies.json 路径（默认读环境变量 BILIUP_COOKIE，"
                             "再退回内置默认路径）")
    parser.add_argument("--aid", help="稿件 aid（默认朱士行稿件）")
    parser.add_argument("--bvid", help="稿件 bvid，如 BV1xxHz65E6n（与 --aid 二选一）")
    parser.add_argument("--index", type=int,
                        help="要改名的分 P 序号（从 1 开始）")
    parser.add_argument("--name", help="新分 P 名；不提供时只查看不修改")
    parser.add_argument("--cover", help="新封面图片路径（jpg/png）；更换稿件整体封面")
    parser.add_argument("--commit", action="store_true",
                        help="真正提交修改；默认 dry-run 只预览")
    args = parser.parse_args()

    cookie_file = args.cookie or os.environ.get("BILIUP_COOKIE") or DEFAULT_COOKIE
    try:
        doc = json.load(open(cookie_file, encoding="utf-8"))
        access_key = doc["token_info"]["access_token"]
    except (OSError, KeyError, ValueError) as e:
        sys.exit(f"无法从 {cookie_file} 读取 token_info.access_token：{e}\n"
                 "可用 --cookie 指定 biliup cookies.json，或先 python -m biliup login 登录。")

    aid = resolve_aid(args)
    archive, videos = fetch_studio(access_key, aid)
    print("稿件 aid:", aid)
    print("稿件标题:", archive.get("title"))
    print("当前封面:", archive.get("cover"))
    print("分 P 数量:", len(videos))
    for i, v in enumerate(videos, 1):
        print(f"  P{i} {v['title']!r}")

    if not args.name and not args.cover:
        return  # 纯查看模式

    changes = []

    # 改名：确定目标分 P
    if args.name:
        if args.index is None:
            if len(videos) == 1:
                args.index = 1
            else:
                sys.exit("多 P 稿件必须用 --index 指定要改名的分 P（从 1 开始）")
        if not 1 <= args.index <= len(videos):
            sys.exit(f"--index 超出范围：稿件共 {len(videos)} 个分 P")
        old_title = videos[args.index - 1]["title"]
        videos[args.index - 1]["title"] = args.name
        changes.append(f"P{args.index} {old_title!r} -> {args.name!r}")

    body = dict(archive)
    body["videos"] = videos

    # 封面：dry-run 只列意图，真正上传留到 --commit（避免无谓占用图床）
    if args.cover:
        if not os.path.isfile(args.cover):
            sys.exit(f"封面文件不存在: {args.cover}")
        if args.commit:
            cover_url = cover_up(cookie_file, args.cover)
            body["cover"] = cover_url
            changes.append(f"封面 -> {cover_url}")
        else:
            changes.append(f"封面将更换为本地文件 {args.cover}")

    if not args.commit:
        print("\n[dry-run] 本次将：")
        for c in changes:
            print("  -", c)
        print("确认无误后加 --commit 提交。凭证不会被打印。")
        return

    res = submit_edit(access_key, body)
    if res.get("code") != 0:
        sys.exit(f"提交失败: {res.get('code')} {res.get('message')}")
    print("提交成功：")
    for c in changes:
        print("  -", c)
    print("提示：公开 API 有几秒到十几秒缓存延迟，稍后复查即可。")


if __name__ == "__main__":
    main()
