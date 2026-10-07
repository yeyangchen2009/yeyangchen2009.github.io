# -*- coding: utf-8 -*-
"""
Issue 正文拉取器：从 GitHub issue 拉 body 落地到 drafts/ 作为工作稿，
拉取的同一道动作里把站内图片路径替换成完整云端 URL——
落盘的 md 可以直接粘到知乎等平台，不用事后再转换。

图片替换：
  /screenshots/a.png  → 云端完整 URL（默认 Pages，最稳）
  /casts/、/asciinema/ 同理；/og.png 等根路径按 static/ 约定映射。
  已是 http(s) 完整链接的图片原样保留。

注意：这是「分发工作稿」，不是保真备份。保真备份（与 issue 逐字一致）
仍然走 backup/ 目录，灾难重建用，两者不要混用。

用法：
  python tools/fetch-drafts.py 76                  # 拉 issue #76 → drafts/post-76.md
  python tools/fetch-drafts.py 74 75 76            # 一次拉多篇（串行）
  python tools/fetch-drafts.py 76 -b raw           # 用 GitHub raw 链接
  python tools/fetch-drafts.py 76 -b jsdelivr      # 用 jsDelivr CDN 链接
  python tools/fetch-drafts.py 76 -o drafts/c.md   # 指定输出文件
"""
import argparse
import os
import re
import subprocess
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS = os.path.join(ROOT, "drafts")
DOMAIN = "https://yeyangchen2009.github.io"

# 部署路径前缀 -> 仓库内路径前缀（Gmeek 把 static/ 的内容部署到站点根）
DEPLOY_TO_REPO = {
    "/screenshots/": "static/screenshots/",
    "/casts/": "static/casts/",
    "/asciinema/": "static/asciinema/",
}

MD_IMG_RE = re.compile(r"(!\[[^\]]*\]\(\s*)([^)\s]+)([^)]*\))")
HTML_IMG_RE = re.compile(r"(<img\s+[^>]*?src=[\"'])([^\"']+)([\"'])", re.I)


def get_repo_info():
    """从 git remote 解析 owner/repo 与当前分支。"""
    url = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()
    m = re.search(r"github\.com[:/]([^/]+)/(.+?)(?:\.git)?$", url)
    if not m:
        sys.exit("无法从 git remote 解析 GitHub 仓库：" + url)
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip() or "main"
    return m.group(1), m.group(2), branch


def fetch_body(number):
    result = subprocess.run(
        ["gh", "issue", "view", str(number), "--json", "body", "-q", ".body"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        sys.exit("拉取 issue #{} 失败：{}".format(number, result.stderr.strip()))
    return result.stdout


def to_cloud(url, backend, owner, repo, branch):
    """站内路径 -> 云端完整 URL；完整外链原样返回。"""
    if re.match(r"https?://", url) or url.startswith("//") or url.startswith("data:"):
        return url, False

    repo_path = None
    for dep, src in DEPLOY_TO_REPO.items():
        if url.startswith(dep):
            repo_path = src + url[len(dep):]
            break
    if repo_path is None:
        # /og.png 等根路径：Gmeek 约定对应仓库 static/og.png
        if url.startswith("/") and "." in os.path.basename(url):
            repo_path = "static" + url
        else:
            return url, False  # 不是图片资源路径，不动

    if backend == "pages":
        # static/og.png -> DOMAIN/og.png；static/screenshots/a.png -> DOMAIN/screenshots/a.png
        return DOMAIN + "/" + repo_path[len("static/"):], True
    if backend == "raw":
        return "https://raw.githubusercontent.com/{}/{}/{}/{}".format(
            owner, repo, branch, repo_path), True
    if backend == "jsdelivr":
        return "https://cdn.jsdelivr.net/gh/{}/{}@{}/{}".format(
            owner, repo, branch, repo_path), True
    sys.exit("未知后端：" + backend)


def convert(text, backend, owner, repo, branch):
    count = 0

    def replace(match):
        nonlocal count
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)
        new_url, changed = to_cloud(url, backend, owner, repo, branch)
        if changed:
            count += 1
            print("  {} -> {}".format(url, new_url))
        return prefix + new_url + suffix

    text = MD_IMG_RE.sub(replace, text)
    text = HTML_IMG_RE.sub(replace, text)
    return text, count


def main():
    parser = argparse.ArgumentParser(description="拉取 issue 正文到 drafts/，图片路径落地即为云端 URL")
    parser.add_argument("numbers", nargs="+", type=int, help="issue 编号，可多个")
    parser.add_argument("-o", "--output", help="输出文件（只在拉单篇时有效），默认 drafts/post-N.md")
    parser.add_argument("-b", "--backend", choices=["pages", "raw", "jsdelivr"],
                        default="pages", help="云端链接后端，默认 pages")
    args = parser.parse_args()

    if args.output and len(args.numbers) > 1:
        sys.exit("-o/--output 只能在拉取单篇时使用")

    owner, repo, branch = get_repo_info()
    os.makedirs(DRAFTS, exist_ok=True)

    for number in args.numbers:
        print("拉取 issue #{}：".format(number))
        body = fetch_body(number)
        converted, count = convert(body, args.backend, owner, repo, branch)
        output = args.output or os.path.join(DRAFTS, "post-{}.md".format(number))
        with open(output, "w", encoding="utf-8") as f:
            f.write(converted)
        print("  替换图片 {} 张，已写入 {}\n".format(count, os.path.relpath(output, ROOT)))


if __name__ == "__main__":
    main()
