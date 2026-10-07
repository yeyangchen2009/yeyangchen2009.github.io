#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B 站视频投稿与合集（season）管理工具。

biliup CLI 的能力缺口：
- 新版 YAML 扁平配置投稿报 missing field streamers；Rust CLI 传中文在
  Windows 上有 argv 编码问题；
- season 子命令只能 list/sections/add/remove/sort，不能创建合集、
  不能改合集标题与简介。

本工具两条通道：
- 投稿：直接 Python 调 stream_gears.upload()（biliup 底层扩展），
  原生 str 传中文，无编码问题；
- 合集：创作者中心网页正在使用的 /x2/creative/web/* 同口径接口，
  纯标准库实现。

典型用法：
    # 投稿（公开、自制、人文历史分区；--desc 可换 --desc-file）
    python tools/bili-pub.py upload --video xx-cover.mp4 \\
        --title "标题" --desc-file desc.txt --cover cover.png

    # 列合集 / 看合集详情（含小节与稿件）
    python tools/bili-pub.py seasons
    python tools/bili-pub.py season 9255943

    # 把多个稿件一次加入同一小节
    python tools/bili-pub.py season-add 10349359 \\
        --vid BV1xxHz65E6n --vid BV1vrHd6MEFA

    # 改合集标题 / 简介（简介建议写泛，别写死具体视频名）
    python tools/bili-pub.py season-edit 9255943 --desc-file intro.txt

    # 按 BV 顺序重排小节稿件
    python tools/bili-pub.py season-sort 10349359 \\
        --order BV1xxHz65E6n,BV1vrHd6MEFA

合集创建仍需在创作者中心官方网页操作（无公开接口）：
https://member.bilibili.com/platform/upload-manager/series

凭证路径优先级：--cookie > 环境变量 BILIUP_COOKIE > 内置默认路径。
凭证仅在进程内部使用，不打印、不入日志。
"""
import argparse
import http.cookiejar
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_COOKIE = r"D:\Code\poju-zyz\zyz\cookies.json"
MEMBER = "https://member.bilibili.com"
API = "https://api.bilibili.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# 投稿默认参数
DEFAULT_TID = 228       # 人文历史
DEFAULT_LINE = "bda2"   # 百度云上传线，实测 4MB/s 以上


class PubError(RuntimeError):
    """接口业务失败。"""


# --- 会话：cookie 与 opener ---

def _make_jar(cookie_file):
    """从 biliup cookies.json 装载 CookieJar。"""
    jar = http.cookiejar.CookieJar()

    def add(name, value, domain=".bilibili.com"):
        jar.set_cookie(http.cookiejar.Cookie(
            version=0, name=name, value=value, port=None,
            port_specified=False, domain=domain, domain_specified=True,
            domain_initial_dot=True, path="/", path_specified=True,
            secure=False, expires=None, discard=False, comment=None,
            comment_url=None, rest={}, rfc2109=False))

    raw = open(cookie_file, "rb").read()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except ValueError:
        ncj = http.cookiejar.MozillaCookieJar(cookie_file)
        ncj.load(ignore_discard=True, ignore_expires=True)
        for c in ncj:
            jar.set_cookie(c)
        return jar, None

    cookies = {i["name"]: str(i["value"])
               for i in doc["cookie_info"]["cookies"]}
    for k, v in cookies.items():
        add(k, v)
    return jar, cookies.get("bili_jct")


def new_session(cookie_file):
    """返回 (opener, csrf)。补 buvid3/buvid4 设备指纹，避免 member 接口 412。"""
    jar, csrf = _make_jar(cookie_file)
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [("User-Agent", UA)]
    with opener.open(API + "/x/frontend/finger/spi", timeout=30) as r:
        spi = json.loads(r.read().decode("utf-8"))["data"]

    def add(name, value):
        jar.set_cookie(http.cookiejar.Cookie(
            0, name, value, None, False, ".bilibili.com", True, True,
            "/", True, False, None, False, None, None, {}, False))

    add("buvid3", spi["b_3"])
    add("buvid4", spi["b_4"])
    if not csrf:
        sys.exit("cookie 缺少 bili_jct，请先 python -m biliup login")
    return opener, csrf


def _request(opener, method, url, body=None, json_body=True):
    """发请求；body 为 dict 时按 json 或 form 发送。返回解析后的 JSON。"""
    data = None
    headers = {}
    if body is not None:
        if json_body:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        else:
            data = urllib.parse.urlencode(body).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Referer"] = (MEMBER +
                          "/platform/upload-manager/series")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with opener.open(req, timeout=30) as r:
            doc = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise PubError("HTTP %s %s" % (e.code, url))
    if doc.get("code") != 0:
        raise PubError("code=%s message=%s url=%s"
                       % (doc.get("code"), doc.get("message"), url))
    return doc.get("data")


# --- 公开稿件信息 ---

def archive_view(opener, vid):
    """按 BV/AV 查公开稿件，返回 {aid, bvid, title, cid(首页)}。"""
    key = "bvid" if vid.upper().startswith("BV") else "aid"
    url = "%s/x/web-interface/view?%s" % (API,
                                         urllib.parse.urlencode({key: vid}))
    data = _request(opener, "GET", url)
    pages = data.get("pages") or []
    cid = pages[0]["cid"] if pages else data.get("cid")
    return {"aid": data["aid"], "bvid": data["bvid"],
            "title": data["title"], "cid": cid}


# --- 投稿 ---

def _latest_archive_ctime(opener):
    """查创作者中心全部状态稿件，返回账号最新稿件 (ctime, bvid)。

    用于上传后定位新稿：stream_gears.upload() 不返回 bvid，且其 Rust
    日志直写 OS 文件描述符、Python 层重定向捕获不到。
    """
    latest = (0, None)
    for status in ("is_pubing", "pubed", "not_pubed"):
        url = ("%s/x/web/archives?pn=1&ps=10&status=%s"
               % (MEMBER, status))
        try:
            data = _request(opener, "GET", url)
        except PubError:
            continue
        for a in (data or {}).get("arc_audits") or []:
            arc = a["Archive"]
            if arc["ctime"] > latest[0]:
                latest = (arc["ctime"], arc["bvid"])
    return latest


def upload_video(*, cookie_file, video, title, desc, cover="",
                 tid=DEFAULT_TID, tags="", line=DEFAULT_LINE,
                 copyright=1, dynamic=""):
    """调 stream_gears.upload() 投稿。返回新稿 bvid。"""
    try:
        from stream_gears import upload, UploadLine
    except ImportError:
        sys.exit("缺少 stream_gears：pip install biliup（提供底层上传扩展）")

    lines = {"bda2": UploadLine.Bda2, "tx": UploadLine.Tx}
    upload_line = lines.get(line)

    # 记录上传前最新稿件，便于从列表中识别新稿
    opener, _ = new_session(cookie_file)
    before, _ = _latest_archive_ctime(opener)

    upload(
        video_path=[video],
        cookie_file=cookie_file,
        title=title,
        tid=tid,
        tag=tags,
        copyright=copyright,
        desc=desc,
        dynamic=dynamic,
        cover=cover,
        line=upload_line,
    )

    # 列表有缓存；轮询直到出现比上传前更新的稿件（最长约 2 分钟）
    for _ in range(20):
        time.sleep(6)
        ctime, bvid = _latest_archive_ctime(opener)
        if bvid and ctime > before:
            return bvid
    raise PubError("上传已执行，但 2 分钟内未能在稿件列表中确认新稿；"
                   "请用 seasons 命令或创作者中心查看。")


# --- 合集只读 ---

def list_seasons(opener, pn=1, ps=30):
    q = urllib.parse.urlencode({
        "pn": pn, "ps": ps, "order": "mtime",
        "sort": "desc", "draft": "1"})
    return _request(opener, "GET",
                    "%s/x2/creative/web/seasons?%s" % (MEMBER, q))


def get_season(opener, season_id):
    q = urllib.parse.urlencode({"id": season_id})
    return _request(opener, "GET",
                    "%s/x2/creative/web/season?%s" % (MEMBER, q))


def get_section(opener, section_id):
    q = urllib.parse.urlencode({"id": section_id})
    return _request(opener, "GET",
                    "%s/x2/creative/web/season/section?%s" % (MEMBER, q))


# --- 合集写入 ---

def add_to_season(opener, csrf, section_id, vids):
    """把多个稿件加入小节。episodes 的 aid/cid/title 从公开接口补齐。"""
    episodes = []
    for vid in vids:
        v = archive_view(opener, vid)
        episodes.append({"aid": v["aid"], "cid": v["cid"],
                         "title": v["title"], "charging_pay": 0})
    body = {"sectionId": section_id, "episodes": episodes, "csrf": csrf}
    url = "%s/x2/creative/web/season/section/episodes/add?%s" % (
        MEMBER, urllib.parse.urlencode({"csrf": csrf}))
    _request(opener, "POST", url, body)


def edit_season(opener, csrf, season_id, title=None, desc=None):
    """改合集标题/简介。

    服务端要求 body 里的 season 完整回显（缺字段一律 -400），
    因此先取详情、只替换指定字段再提交。
    """
    season = dict(get_season(opener, season_id)["season"])
    if title is not None:
        season["title"] = title
    if desc is not None:
        season["desc"] = desc
    body = {"season": season, "captcha_token": "", "csrf": csrf}
    url = "%s/x2/creative/web/season/edit?%s" % (
        MEMBER, urllib.parse.urlencode({"csrf": csrf}))
    _request(opener, "POST", url, body)
    return season


def sort_section(opener, csrf, section_id, ordered_vids):
    """按给定 BV/AV 顺序重排整个小节（必须覆盖全部稿件）。"""
    detail = get_section(opener, section_id)
    section = detail["section"]
    by_bvid = {}
    for ep in detail["episodes"]:
        # 公开接口把 aid 换成 bvid，便于按 --order 匹配
        q = urllib.parse.urlencode({"aid": ep["aid"]})
        v = _request(opener, "GET",
                     "%s/x/web-interface/view?%s" % (API, q))
        by_bvid[v["bvid"]] = ep["id"]

    if set(ordered_vids) != set(by_bvid):
        raise PubError("--order 必须恰好包含小节全部稿件：现有 %s"
                       % ",".join(sorted(by_bvid)))
    sorts = [{"id": by_bvid[bv], "sort": i}
             for i, bv in enumerate(ordered_vids, 1)]
    body = {
        "section": {"id": section["id"], "type": 1,
                    "seasonId": section["seasonId"],
                    "title": section["title"]},
        "sorts": sorts, "captcha_token": "",
    }
    url = "%s/x2/creative/web/season/section/edit?%s" % (
        MEMBER, urllib.parse.urlencode({"csrf": csrf}))
    _request(opener, "POST", url, body)


# --- 展示辅助 ---

def show_seasons(data):
    for entry in data["seasons"]:
        s = entry["season"]
        sections = entry.get("sections", {}).get("sections", [])
        sec = sections[0] if sections else {}
        print("合集 %s  %s" % (s["id"], s["title"]))
        if s.get("desc"):
            print("  简介：%s" % s["desc"])
        print("  小节 %s  %s（%s 个稿件）"
              % (sec.get("id"), sec.get("title"), sec.get("epCount")))


def show_season(data):
    s = data["season"]
    print("合集 %s  %s" % (s["id"], s["title"]))
    print("简介：%s" % (s["desc"] or "（空）"))
    for sec in data.get("sections", {}).get("sections", []):
        print("小节 %s  %s（%s 个稿件）"
              % (sec["id"], sec["title"], sec.get("epCount")))


def show_section(data):
    sec = data["section"]
    print("小节 %s  %s" % (sec["id"], sec["title"]))
    for i, ep in enumerate(data.get("episodes") or [], 1):
        print("  %d. %s  %s" % (i, ep.get("bvid") or
                                ("av%s" % ep["aid"]), ep["title"]))


def _text(value, path):
    if path:
        return io.open(path, encoding="utf-8").read().strip()
    return value


# --- CLI ---

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    p = argparse.ArgumentParser(
        description="B 站视频投稿与合集管理（stream_gears 直调 + 创作中心同口径接口）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--cookie",
                   help="biliup cookies.json（默认环境变量 BILIUP_COOKIE，"
                        "再退回内置默认路径）")
    sub = p.add_subparsers(dest="cmd", required=True)

    up = sub.add_parser("upload", help="投稿视频")
    up.add_argument("--video", required=True, help="视频文件路径")
    up.add_argument("--title", help="标题（与 --title-file 二选一）")
    up.add_argument("--title-file", help="标题文本文件")
    up.add_argument("--desc", help="简介（与 --desc-file 二选一）")
    up.add_argument("--desc-file", help="简介文本文件")
    up.add_argument("--cover", default="", help="封面图片路径")
    up.add_argument("--tid", type=int, default=DEFAULT_TID,
                    help="分区 id，默认 228 人文历史")
    up.add_argument("--tags", default="", help="逗号分隔的标签")
    up.add_argument("--line", default=DEFAULT_LINE,
                    help="上传线 bda2/tx，默认 bda2")
    up.add_argument("--dynamic", default="", help="随稿动态文字")

    sub.add_parser("seasons", help="列自己的合集")
    sp = sub.add_parser("season", help="看合集详情")
    sp.add_argument("season_id", type=int)

    sa = sub.add_parser("season-add", help="把稿件加入小节")
    sa.add_argument("section_id", type=int)
    sa.add_argument("--vid", action="append", required=True,
                    help="AV/BV 号，可重复")

    se = sub.add_parser("season-edit", help="改合集标题/简介")
    se.add_argument("season_id", type=int)
    se.add_argument("--title", help="新标题（与 --title-file 二选一）")
    se.add_argument("--title-file", help="标题文本文件")
    se.add_argument("--desc", help="新简介（与 --desc-file 二选一）")
    se.add_argument("--desc-file", help="简介文本文件")

    ss = sub.add_parser("season-sort", help="按 BV 顺序重排小节")
    ss.add_argument("section_id", type=int)
    ss.add_argument("--order", required=True,
                    help="逗号分隔的 BV 顺序，须覆盖小节全部稿件")

    args = p.parse_args()
    cookie_file = args.cookie or os.environ.get("BILIUP_COOKIE") or DEFAULT_COOKIE

    # upload 只依赖 cookie 文件本身（stream_gears 内部读取），无需建会话
    if args.cmd == "upload":
        title = _text(args.title, args.title_file)
        desc = _text(args.desc, args.desc_file)
        if not title or desc is None:
            sys.exit("upload 需要 --title/--title-file 与 --desc/--desc-file")
        bvid = upload_video(
            cookie_file=cookie_file, video=args.video, title=title,
            desc=desc, cover=args.cover, tid=args.tid, tags=args.tags,
            line=args.line, dynamic=args.dynamic)
        print("投稿成功：https://www.bilibili.com/video/%s" % bvid)
        print("提示：转码与缓存有几十秒延迟，稍后用 season 命令复查。")
        return

    opener, csrf = new_session(cookie_file)
    if args.cmd == "seasons":
        show_seasons(list_seasons(opener))
    elif args.cmd == "season":
        data = get_season(opener, args.season_id)
        show_season(data)
        for sec in data.get("sections", {}).get("sections", []):
            show_section(get_section(opener, sec["id"]))
    elif args.cmd == "season-add":
        add_to_season(opener, csrf, args.section_id, args.vid)
        print("已加入小节 %s：%s" % (args.section_id, ", ".join(args.vid)))
    elif args.cmd == "season-edit":
        title = _text(args.title, args.title_file) \
            if args.title or args.title_file else None
        desc = _text(args.desc, args.desc_file) \
            if args.desc or args.desc_file else None
        if title is None and desc is None:
            sys.exit("season-edit 至少给 --title 或 --desc")
        season = edit_season(opener, csrf, args.season_id, title, desc)
        print("已更新合集 %s" % args.season_id)
        print("标题：%s" % season["title"])
        print("简介：%s" % season["desc"])
    elif args.cmd == "season-sort":
        vids = [v.strip() for v in args.order.split(",") if v.strip()]
        sort_section(opener, csrf, args.section_id, vids)
        print("已重排小节 %s：%s" % (args.section_id, ", ".join(vids)))


if __name__ == "__main__":
    main()
