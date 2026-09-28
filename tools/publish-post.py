# -*- coding: utf-8 -*-
"""一键发布：pre-flight（markdown/裸他）→ 图片在 main 确认 → 建 issue
→ 门户并行打勾 → 限时轮询等文章与门户双绿 → curl 验证。

与旧手工流程的差别：
  - 不做图片全量重建（issue 构建 checkout 最新 main，图片随文章一起部署）；
  - 门户编辑与文章创建同时机，两个构建并行；
  - 等待用限时轮询，不用会静默挂死的 gh run watch；
  - 全程日志带时间戳，可用 --log-file 落盘。

用法：
  python tools/publish-post.py vault/.../中16-xxx.md --series zhong
  python tools/publish-post.py xxx.md --series zhong --dry-run
"""
import argparse
import importlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- 裸他：逐字符枚举，豁免按「覆盖该位置」判定，防裸子串误判 ----
TA_EXEMPT = ["其他", "自他", "依他起", "他力", "他日", "多罗那他", "别人"]

# ---- mermaid 暗色 init（若将来要校验）----
IMG_RE = re.compile(r"!\[[^\]]*\]\((/screenshots/[^)\s]+)\)")


def log(msg, fh=None):
    line = "[{}] {}".format(datetime.now().strftime("%H:%M:%S"), msg)
    print(line)
    if fh:
        fh.write(line + "\n")
        fh.flush()


def run(args, **kw):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", **kw)


def git_repo():
    r = run(["git", "remote", "get-url", "origin"])
    url = r.stdout.strip()
    m = re.search(r"[:/]([^/]+)/([^/]+?)(\.git)?$", url)
    return m.group(1), m.group(2)


def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    meta = {}
    if not m:
        return meta, text
    body = text[m.end():]
    key = None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if km:
            key = km.group(1)
            meta[key] = km.group(2).strip()
            if key == "tags":
                meta["tags"] = []
        elif re.match(r"^\s+-\s+", line) and key == "tags":
            meta["tags"].append(re.sub(r"^\s+-\s+", "", line).strip())
    return meta, body


def render_gfm(text):
    payload = json.dumps({"text": text, "mode": "gfm"})
    r = run(["gh", "api", "/markdown", "--input", "-"], input=payload)
    if r.returncode != 0:
        raise RuntimeError("gh api /markdown 失败：" + r.stderr.strip())
    return r.stdout


def find_bare_ta(text):
    out = []
    for ln_no, line in enumerate(text.split("\n"), 1):
        for j, ch in enumerate(line):
            if ch != "他":
                continue
            covered = False
            for w in TA_EXEMPT:
                p = line.find(w, max(0, j - 3), j + 4)
                while p != -1:
                    if p <= j < p + len(w):
                        covered = True
                    p = line.find(w, p + 1, j + 4)
            if not covered:
                out.append((ln_no, line[max(0, j - 10):j + 10]))
    return out


def file_on_main(owner, repo, repo_path):
    r = run(["gh", "api",
             "repos/{}/{}/contents/{}".format(owner, repo, repo_path)])
    return r.returncode == 0


def http_ok(url):
    try:
        with urlopen(Request(url, method="HEAD"), timeout=20) as resp:
            return resp.status == 200
    except HTTPError as e:
        return e.code == 200
    except Exception:
        return False


def _parse_iso(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def wait_runs(title, portal_run_title, since, timeout, fh):
    """限时轮询文章 run 与门户 run，不用 gh run watch。
    since：只认该时刻之后创建的 run（防误认历史同名 run）。"""
    deadline = time.time() + timeout
    article_ok = portal_ok = False
    article_id = portal_id = None
    while time.time() < deadline:
        r = run(["gh", "run", "list", "--workflow=build Gmeek", "--limit", "10",
                 "--json", "databaseId,status,conclusion,displayTitle,createdAt"])
        for it in json.loads(r.stdout or "[]"):
            if _parse_iso(it["createdAt"]) < since:
                continue
            if it["displayTitle"] == title:
                article_id = it["databaseId"]
                if it["conclusion"] == "success":
                    article_ok = True
                elif it["conclusion"] == "failure":
                    raise RuntimeError("文章构建失败，run {}（gh run view {}）".format(
                        it["databaseId"], it["databaseId"]))
            if portal_run_title and it["displayTitle"] == portal_run_title:
                portal_id = it["databaseId"]
                if it["conclusion"] == "success":
                    portal_ok = True
                elif it["conclusion"] == "failure":
                    raise RuntimeError("门户构建失败，run {}".format(it["databaseId"]))
        need_article = not article_ok
        need_portal = bool(portal_run_title) and not portal_ok
        if not need_article and not need_portal:
            return article_id, portal_id
        log("等待构建… 文章 {}/门户 {}（run {}/{}）".format(
            "✓" if article_ok else "…", "✓" if portal_ok else "…",
            article_id, portal_id), fh)
        time.sleep(20)
    raise TimeoutError("等待构建超过 {}s，最后状态 文章 run={}、门户 run={}".format(
        timeout, article_id, portal_id))


def main():
    ap = argparse.ArgumentParser(description="一键发布博客文章")
    ap.add_argument("draft")
    ap.add_argument("--series", required=True, help="门户 hook 名，如 zhong")
    ap.add_argument("--title")
    ap.add_argument("--labels", help="逗号分隔；默认 frontmatter tags")
    ap.add_argument("--no-portal", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-ta", action="store_true")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--log-file")
    args = ap.parse_args()

    fh = open(args.log_file, "a", encoding="utf-8") if args.log_file else None
    t0 = time.time()
    try:
        text = open(args.draft, encoding="utf-8").read()
        meta, body = parse_frontmatter(text)
        title = args.title or meta.get("title") or os.path.basename(args.draft)
        labels = (args.labels.split(",") if args.labels else meta.get("tags", []))
        series_index = int(meta.get("series_index", "0"))
        if not title or not labels or (not args.no_portal and not series_index):
            ap.error("缺 title/labels/series_index（frontmatter 是否齐全？）")

        log("发布对象：{}（{}，标签 {}）".format(title, series_index, labels), fh)

        # 1) pre-flight：markdown
        log("pre-flight：gh api /markdown", fh)
        html = render_gfm(body)
        so, sc = html.count("<strong>"), html.count("</strong>")
        stars = html.count("*")
        log("strong {}/{}，字面星号 {}".format(so, sc, stars), fh)
        if so != sc or stars:
            raise RuntimeError("markdown 起符校验失败，先修粗体再发")

        # 2) pre-flight：裸他
        ta = find_bare_ta(body)
        if ta:
            for ln, seg in ta:
                log("  裸他 L{}：{}".format(ln, seg), fh)
            if not args.allow_ta:
                raise RuntimeError("发现 {} 处裸他（--allow-ta 可强制继续）".format(len(ta)))
        else:
            log("裸他 0", fh)

        # 3) 图片已在 main（无需全量重建）
        owner, repo = git_repo()
        imgs = sorted(set(IMG_RE.findall(body)))
        for url in imgs:
            repo_path = "static" + url
            if not file_on_main(owner, repo, repo_path):
                raise RuntimeError("图片未入库 main：{}，先 git push".format(url))
        log("图片 {} 张均已在 main".format(len(imgs)), fh)

        if args.dry_run:
            log("dry-run：pre-flight 全过，不建 issue", fh)
            return

        # 4) 建文章 issue（记录时间窗，run 识别只用此之后的新 run）
        since = datetime.now(timezone.utc) - timedelta(seconds=15)
        body_file = os.path.join(ROOT, "Temp", "publish-body.tmp.md")
        with open(body_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
        cmd = ["gh", "issue", "create", "--title", title,
               "--body-file", body_file]
        for lb in labels:
            cmd += ["--label", lb]
        r = run(cmd)
        if r.returncode != 0:
            raise RuntimeError("gh issue create 失败：" + r.stderr.strip())
        issue_url = r.stdout.strip()
        m = re.search(r"/issues/(\d+)$", issue_url)
        issue_no = int(m.group(1))
        log("已建 issue #{}：{}".format(issue_no, issue_url), fh)

        # 5) 门户并行打勾（门户构建与文章构建并行）
        portal_title = None
        if not args.no_portal:
            hook = importlib.import_module("portal_hooks." + args.series)
            portal_issue = hook.PORTAL_ISSUE
            pr = run(["gh", "issue", "view", str(portal_issue),
                      "--json", "body", "--jq", ".body"])
            if pr.returncode != 0:
                raise RuntimeError("取门户 body 失败：" + pr.stderr.strip())
            new_body, note = hook.apply(pr.stdout, series_index, issue_no)
            portal_file = os.path.join(ROOT, "Temp", "publish-portal.tmp.md")
            with open(portal_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_body)
            er = run(["gh", "issue", "edit", str(portal_issue),
                      "--body-file", portal_file])
            if er.returncode != 0:
                raise RuntimeError("门户编辑失败：" + er.stderr.strip())
            portal_title = None  # 门户 run 的 displayTitle 需在下方识别
            log("门户 #{} 已更新（{}），与文章构建并行".format(portal_issue, note), fh)
            # 门户 issue 的 displayTitle 用其标题，取一次
            vr = run(["gh", "issue", "view", str(portal_issue),
                      "--json", "title", "--jq", ".title"])
            portal_title = vr.stdout.strip()

        # 6) 限时轮询双绿
        article_id, portal_id = wait_runs(
            title, portal_title, since, args.timeout, fh)
        log("双绿：文章 run {}，门户 run {}".format(article_id, portal_id), fh)

        # 7) curl 验证
        base = "https://{}.github.io".format(owner)
        post_url = "{}/post/{}.html".format(base, issue_no)
        time.sleep(8)
        if not http_ok(post_url):
            raise RuntimeError("文章页未 200：" + post_url)
        for url in imgs:
            if not http_ok(base + url):
                raise RuntimeError("图片未 200：" + url)
        log("文章与图片全部 200：{}".format(post_url), fh)
        log("发布完成，用时 {:.0f} 秒".format(time.time() - t0), fh)
    finally:
        if fh:
            fh.close()


if __name__ == "__main__":
    main()
