# -*- coding: utf-8 -*-
"""Generate docs/sitemap.xml from docs/postList.json and config.json.

Runs at the end of every "build Gmeek" workflow run (both incremental and
full rebuild), so the sitemap always matches the latest posts.
"""
import datetime
import json
import os

WORK = os.environ.get("GITHUB_WORKSPACE", ".")

with open(os.path.join(WORK, "config.json"), encoding="utf-8") as f:
    cfg = json.load(f)

repo = os.environ.get("GITHUB_REPOSITORY", "")
if repo:
    owner, name = repo.split("/", 1)
else:  # local fallback: derive from exlink.github
    repo_url = cfg["exlink"]["github"]
    owner, name = repo_url.rstrip("/").split("/")[-2:]

if name == owner + ".github.io":
    base = "https://%s/" % name
else:  # project pages live under /<repo>/
    base = "https://%s.github.io/%s/" % (owner, name)

with open(os.path.join(WORK, "docs", "postList.json"), encoding="utf-8") as f:
    posts = json.load(f)

today = datetime.date.today().isoformat()

# (loc, lastmod, priority)
urls = [(base, today, "1.0")]
for sp in cfg.get("singlePage", []):
    urls.append((base + sp + ".html", today, "0.5"))
urls.append((base + "tag.html", today, "0.4"))
for v in posts.values():
    if "postUrl" not in v:  # singlePage entries carry no postUrl
        continue
    urls.append((base + v["postUrl"], v.get("createdDate", today), "0.8"))

items = "".join(
    '  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n' % (u, d, p)
    for u, d, p in urls
)
xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + items
    + "</urlset>\n"
)
with open(os.path.join(WORK, "docs", "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(xml)
print("sitemap.xml generated with %d urls -> %s" % (len(urls), base))
