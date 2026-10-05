# -*- coding: utf-8 -*-
"""结构提取与新旧 index.html 零差异对比。"""
import difflib
import re
from html.parser import HTMLParser

_PATH_ATTR = re.compile(r'(=\s*["\'])([^"\']*[/])([^"\'/]+)(["\'])')


def _basename_attrs(line: str) -> str:
    """把属性里的路径收敛为 basename（忽略 media/ 等目录前缀差异）。"""
    return _PATH_ATTR.sub(lambda m: m.group(1) + m.group(3) + m.group(4),
                          line)


def compare(old: str, new: str):
    """行级对比，返回差异行列表；0 条即通过。

    唯一被宽恕的差异：资源路径的目录前缀（老版裸文件名 vs 新版
    media/ 前缀），比较时统一取 basename。
    """
    a = [_basename_attrs(x) for x in old.splitlines()]
    b = [_basename_attrs(x) for x in new.splitlines()]
    if a == b:
        return []
    return list(difflib.unified_diff(a, b, "old", "new", lineterm="",
                                    n=2))


class _Struct(HTMLParser):
    def __init__(self):
        super().__init__()
        self.total = None
        self.audio = None
        self.scenes = []
        self.subs = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "div" and d.get("id") == "root":
            self.total = d.get("data-duration")
        if tag == "audio":
            self.audio = d.get("src")
        classes = d.get("class", "")
        if tag == "div" and "scene" in classes and "clip" in classes:
            self.scenes.append(d.get("id"))
        if tag == "span" and "sub" in classes and "ch" not in classes:
            self.subs.append(d.get("id"))


def structure(html: str) -> dict:
    p = _Struct()
    p.feed(html)
    return {"total": p.total, "audio": p.audio,
            "scenes": p.scenes, "subs": p.subs}
