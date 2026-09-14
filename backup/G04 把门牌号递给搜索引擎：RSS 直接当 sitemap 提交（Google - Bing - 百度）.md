# G04 把门牌号递给搜索引擎：RSS 直接当 sitemap 提交（Google / Bing / 百度）

> G03 给博客挂上了 favicon 和分享封面，门面算是装好了。可互联网上没人知道这个地址——搜索引擎的爬虫靠链接在网上漫游，一个零外链的新站，它可能几个月都溜达不过来。这一期 G04 要干的事很像去派出所报备地址：主动把全站页面清单递到 Google、Bing、百度三家手里。这是整个系列里代码最少、"外交事务"最多的一篇。

## 先说原理：sitemap 是什么

sitemap（站点地图）就是一个 XML 文件，里面列着网站所有可以公开抓取的网址，通常还带着最后更新时间：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/post/1.html</loc>
    <lastmod>2026-09-13</lastmod>
    <priority>0.8</priority>
  </url>
</urlset>
```

爬虫每次来访先读它，就知道"这个站有哪些页、哪篇更新了"，不用再靠外链一个一个摸。

那 Gmeek 生成 sitemap.xml 吗？不生成。早在 [Gmeek 官方 issue #145](https://github.com/Meekdai/Gmeek/issues/145) 就有人向作者提过这个需求，作者的回复很有意思：

> "目前的 rss.xml 文件已经包含整个网站的所有重要页面的链接。我就是把 rss.xml 提交给 google 的。"

普通博客系统的 RSS 只吐最近几篇文章，但叶扬实测过本站的 `rss.xml`——从 G03 一路到《楞严咒》，**九篇文章加 About 页全在里面**，它本质上就是一份套着 RSS 外壳的完整页面清单。提问题的网友也跟帖确认："我把 rss 地址提交到必应和谷歌，可以正常识别抓取。"

而 Google 和 Bing 的官方文档都明确接受 **RSS 2.0 / Atom 1.0 feed** 作为站点地图提交（feed 天然带发布时间，对发现新文章反而更快）。所以这一期的前半场，可以零代码。

不过有一家例外：**百度**的普通收录工具按 [sitemaps.org](https://www.sitemaps.org/protocol.html) 协议解析，对 RSS 这种"套壳"格式不太买账。为了不让百度这位同学对着 RSS 挠头，叶扬写了 15 行脚本，让博客每次构建时顺手产出一份标准 `sitemap.xml`——Google 和 Bing 也一并提交，双保险。

## 代码同步：让构建自己长出 sitemap.xml

数据是现成的：Gmeek 每次构建都会生成 `docs/postList.json`，结构如下：

```json
{
  "P9": {
    "labels": ["博客", "Gmeek"],
    "postTitle": "G03 给博客一张脸：自制 SVG favicon 与社交分享封面",
    "postUrl": "post/9.html",
    "createdDate": "2026-09-14"
  }
}
```

在仓库根目录新建 `sitemap_gen.py`（`GITHUB_REPOSITORY` 是 Actions 自动注入的环境变量，本地运行则回退到从 config 的 exlink 推导域名）：

```python
# -*- coding: utf-8 -*-
"""Generate docs/sitemap.xml from docs/postList.json and config.json."""
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
    owner, name = cfg["exlink"]["github"].rstrip("/").split("/")[-2:]

if name == owner + ".github.io":
    base = "https://%s/" % name
else:  # project pages live under /<repo>/
    base = "https://%s.github.io/%s/" % (owner, name)

with open(os.path.join(WORK, "docs", "postList.json"), encoding="utf-8") as f:
    posts = json.load(f)

today = datetime.date.today().isoformat()
urls = [(base, today, "1.0")]                          # 首页
for sp in cfg.get("singlePage", []):                   # About 这类固定页
    urls.append((base + sp + ".html", today, "0.5"))
urls.append((base + "tag.html", today, "0.4"))         # 标签页
for v in posts.values():
    if "postUrl" not in v:                             # singlePage 条目无 postUrl
        continue
    urls.append((base + v["postUrl"], v.get("createdDate", today), "0.8"))

items = "".join(
    '  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>\n'
    % (u, d, p) for u, d, p in urls
)
with open(os.path.join(WORK, "docs", "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + items + "</urlset>\n")
```

然后在 `.github/workflows/Gmeek.yml` 里，紧跟 "Generate new html" 步骤后面加一步（此时 docs 已从构建目录拷回工作区）：

```yaml
      - name: Generate sitemap.xml
        run: python sitemap_gen.py
```

这样每次发文章触发的增量构建、每天的定时构建，都会重刷一次 `sitemap.xml` 并自动 commit——它永远和文章列表同步，比手写一份然后忘更新强太多了。提交后手动全局重建一次（改了 workflow 老规矩：push、深呼吸几秒、`gh workflow run "build Gmeek"`），访问 `https://你的域名/sitemap.xml` 就能看到十一行 URL 清单。

## 第一站：Google Search Console（需代理）

地址：<https://search.google.com/search-console>，用任意 Google 账号登录。

**1）添加资源时选"网址前缀"，不要选"网域"。** 网域资源要求去域名服务商那里加 DNS TXT 记录——github.io 的 DNS 不归我们管，此路不通。网址前缀框里填 `https://yeyangchen2009.github.io/`。

**2）验证所有权。** 提供多种方式，对静态站最友好的是"HTML 文件"：下载一个形如 `google1a2b3c4d5e6f7g8h.html` 的文件，丢进仓库 `static/` 目录，等它上线（编辑任意 issue 触发构建，或手动 dispatch），浏览器能匿名打开后，回来点"验证"。这个文件验证后**不要删**，Google 会不定期复检。

**3）提交站点地图。** 左侧菜单"索引 → 站点地图"，依次提交两个：

- `rss.xml`——feed 形式，Google 对 feed 的新内容发现很积极；
- `sitemap.xml`——标准完整清单，给百度准备的那份，Google 也照收。

状态显示"成功"可能要等几小时甚至一两天；刚提交时刷出"无法读取"先别慌，用浏览器无痕窗口确认文件本身能公开访问，再回来等。

**4）主动请求收录首页。** 顶上"网址检查"框贴入站点根地址，若提示"网址不在 Google 上"，点"请求编入索引"。每篇文章不必逐一请求，sitemap 和 RSS 会负责后续。

## 第二站：Bing 网站管理员工具（国内直连）

地址：<https://www.bing.com/webmasters>，微软账号（MSN/Outlook/LinkedIn 同体系）登录。

Bing 最讨喜的一点：添加站点时有个 **"从 Google Search Console 导入"** 按钮，OAuth 授权一次，站点、验证状态、站点地图全部继承过来，三十秒收工。叶扬强烈建议走这条路——刚在 Google 那边做的功课不花白做。

如果想手动添加（或以后换账号），验证方式同样是三种：

| 方式 | 做法 | 适合场景 |
|---|---|---|
| XML 文件 | 下载 `BingSiteAuth.xml` 放 `static/` | 静态站首选 |
| Meta 标签 | 给 `<head>` 加 `<meta name="msvalidate.01" content="...">` | 懒得放文件时，可塞进 config 的 `allHead` |
| DNS TXT | 域名商后台加记录 | 自有域名用户 |

"配置我的网站 → 站点地图"里同样提交 `rss.xml` 和 `sitemap.xml`。顺带一提：Bing 后台是全球统一的，这里提交一次，cn.bing.com 和国际版都生效。

## 第三站：百度搜索资源平台（国内主场）

地址：<https://ziyuan.baidu.com>，百度账号登录，进"用户中心 → 添加网站"，协议记得选 `https`。

**1）验证站点**，三选一：

- **文件验证**：下载 `baidu_verify_xxxx.html` 放 `static/`——和 Google、Bing 的文件凑成一锅，一次构建全部上线；
- **HTML 标签验证**：拿到 `<meta name="baidu-site-verification" content="xxxx">`，整段塞进 `config.json` 的 `allHead` 字段（GmeekVercount 那行旁边拼上即可），再全局重建；
- CNAME 验证：自有域名才用得上，github.io 忽略。

**2）数据引入 → 普通收录 → sitemap**，提交 `https://yeyangchen2009.github.io/sitemap.xml`。注意这里喂标准协议文件，不喂 RSS。状态显示"等待处理"是常态，百度的处理周期以**周**计。

**3）做好心理预期管理。** github.io 服务器在海外、站点未备案，百度对这类域名的抓取和收录一向冷淡，可能一个月后 `site:` 查询仍是零条。这不是操作有误，是中文互联网的客观地形——面向中文读者，百度这边做了不亏，但 Google/Bing 才是独立博客的主战场，不用为百度的冷脸焦虑。

## 验证文件的"三文件一锅端"技巧

走完三家会拿到三个文件：`google*.html`、`BingSiteAuth.xml`、`baidu_verify_*.html`。它们的共同归宿都是仓库 `static/` 目录（构建时原样复制到站点根目录，机制在[第 1 篇](/post/1.html)讲过）。全部丢进去，一次全局重建，三个平台挨个点"验证"即可。两个铁律：

1. 文件名和内容一字不改，平台是按它给的原名回源比对的；
2. 验证通过后文件永久保留，删了会被复检打回原形。

## 收尾：怎么知道报备生效了

在任意搜索引擎的搜索框输入 `site:yeyangchen2009.github.io`，能查到页数说明已被收录；刚提交的几天查不到是正常的，索引以天到周为单位。之后想观察动态：

- **GSC** 的"网页索引编制"报告会展示收录/未收录原因，是最值得常看的面板；
- **Bing** 的"URL 检查"可以单页请求抓取；
- 比提交地图更有效的收录加速器永远是**外链**——在 Gmeek 官方仓库 issue 下留言交流、以后做友链页互链，都是在给爬虫修路。

下一期 G05 回归代码：装官方 lightbox 插件，让文章里的图片点击放大、左右切换，手机上看大图不再靠两根手指硬撑。

## 参考

- Gmeek 官方关于 sitemap 的讨论（作者确认 RSS 可提交）：<https://github.com/Meekdai/Gmeek/issues/145>
- Google 提交站点地图帮助（含 RSS/Atom feed 说明）：<https://developers.google.com/search/docs/crawling-indexing/sitemaps/submit-sitemap>
- Bing 网站管理员工具 · 站点地图：<https://www.bing.com/webmasters/help/sitemaps-3b5cf6ed>
- sitemap 协议官方站：<https://www.sitemaps.org/protocol.html>
- 百度搜索资源平台：<https://ziyuan.baidu.com>
- 系列总揽：[Gmeek 插件与功能全景调研（第 0 篇）](/post/5.html)
