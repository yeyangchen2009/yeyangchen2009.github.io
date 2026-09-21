> 自研三连（G08–G10）写完插件，这一期叶扬处理两个建站起就欠着的小尾巴：G04 做 SEO 时测过本站的 robots.txt 是 **404**——没有 robots 文件时绝大多数爬虫默认"全站可抓"，所以没出事故，但 sitemap 的门牌号已经挂出去了，总不能还让 Googlebot 每次来都撞一扇没挂牌子的大门；另一边，输错地址的读者此前看到的是 GitHub Pages 默认的白地 404，和博客毫无关系。两个文件，一个管机器、一个管人，都不用写 Python、不用动配置，放进 `static/` 就行。

## 先看现场

- 爬虫视角：<https://yeyangchen2009.github.io/robots.txt> 现在返回 200，白纸黑字写着"全站欢迎，并附 sitemap 地址"；
- 读者视角：随便敲一个不存在的地址，比如 <https://yeyangchen2009.github.io/this-page-has-left>，不再是 GitHub 的英文默认页，而是博客同款配色的中文 404——大渐变色 404、回首页/逛归档两个入口，下面还列着最新 5 篇文章，迷路的读者顺手就能被接住。

## 一、robots.txt 是什么，不是什么

robots.txt 是爬虫协议（2022 年正式成为标准 [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309)），放在站点根目录，用极简的"分组声明"语法告诉合规爬虫：哪些路径欢迎、哪些别碰。本站最终的文件只有七行：

```text
# robots.txt — https://yeyangchen2009.github.io
# 全站欢迎合规爬虫收录，无任何屏蔽
User-agent: *
Allow: /

# G04 起由 sitemap_gen.py 每次构建自动刷新
Sitemap: https://yeyangchen2009.github.io/sitemap.xml
```

逐个字段说：

- **`User-agent: *`**：对所有爬虫生效。也可以单独点名，比如 `User-agent: GPTBot` 给 AI 爬虫单独立规矩；
- **`Allow: /`**：根路径下全部允许（没有 robots.txt 时其实也是这个默认行为，但显式写出来是给爬虫和自己看的"态度声明"）；
- **`Sitemap:`**：[sitemaps.org](https://www.sitemaps.org/protocol.html#submit_robots) 规定的发现指令，**必须写完整绝对 URL**。G04 在 Google/Bing 后台手动提交过 sitemap，那是"递名片"；在这里声明则是"把名片钉在大门上"，以后任何遵守协议的新爬虫第一次来访就能自己找到全站地图，包括以后可能开放的百度。

三个常见误解顺手掰正：

1. **robots.txt 不是安全措施**。它只是"君子协定"，恶意爬虫完全无视；真正要保护的内容得靠鉴权或 `noindex`，不能指望它；
2. **Disallow 挡不住已经被别处链接的 URL 被索引**——协议只管"抓不抓"，不管"收不收"。要消失得用 noindex 或移除工具；
3. **文件本身必须在根路径**（`/robots.txt`），放子目录无效；协议规定爬虫只认这一个入口，且返回非 200 时行为各异（404 通常视为"无限制"但不优雅）。

## 二、为什么放进 static/ 就能到达站点根

G03 的 favicon、G04 的两个搜索引擎验证文件都是这么部署的，这一期把原理从源码里翻出来。构建脚本 [Gmeek.py](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py) 的初始化逻辑（约 77–88 行）：

```python
if os.path.exists(self.static_dir):
    for item in os.listdir(self.static_dir):
        src = os.path.join(self.static_dir, item)
        dst = os.path.join(self.root_dir, item)
        if os.path.isfile(src):
            shutil.copy(src, dst)     # 文件：原样拷到 docs/ 根
        elif os.path.isdir(src):
            shutil.copytree(src, dst) # 目录：整目录递归复制
```

结合上面第 70–75 行——**每次构建先把整个 docs/ 目录删掉重建**，再逐字节原样复制 static/：没有文件名白名单、没有内容处理。这解释了三件事：

- `robots.txt`、`404.html`、`google*.html`、`BingSiteAuth.xml`、`favicon.svg` 这些"非文章"文件靠同一个机制直达根路径；
- plugins/、mermaid.min.js 等目录整包复制，所以 config 里 `/plugins/xxx.js` 这种绝对路径引用永远可用；
- **docs/ 里手改任何东西都活不过下次构建**——要持久化的文件必须在 static/（或像 G04 的 sitemap.xml那样由构建脚本生成）。

## 三、自定义 404：GitHub Pages 的规则

GitHub Pages 对自定义 404 有[官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-custom-404-page-for-github-pages-site)，规则比想象的简单，也有一个著名的坑：

- 在发布目录根放一个 **`404.html`**，任何未匹配的 URL 都会由服务器返回这个文件，**HTTP 状态码是真·404**（不是软 200）；
- 直接访问 `/404.html` 本身返回 200——这是正常的，别拿这个当故障；
- **坑：project 站点（`用户名.github.io/仓库名/`）有目录边界**，深层路径可能 fall back 不到根的 404；本站是 user 站点（`yeyangchen2009.github.io`），根域名下全部路径统一生效——叶扬实测了根路径不存在页、`/post/999.html`、甚至 `/a/b/c` 三层深路径，全部返回 404 状态码与自定义内容。

还有一个 SEO 细节：错误路径返回 404 时搜索引擎知道这页无效；但 `/404.html` 直接访问是 200，万一被谁链了就可能被索引。所以 `<head>` 里主动写了：

```html
<meta name="robots" content="noindex">
```

## 四、404 页怎么写才像"自己人"

框架模板不管 404，这页就是一个**完全独立的静态 HTML**，设计时叶扬定了四条规矩：

**1. 资源一律绝对路径，视觉自成体系。** 404 可能在 `/a/b/c` 任意深度触发，相对路径会全部错位，所以 favicon、首页链接、postList.json 全部 `/` 开头。CSS 不引 Primer（那是文章页才加载的），自己用同名 CSS 变量写了 30 行，色值直接对齐 GitHub Dark 色板（`#0d1117` / `#58a6ff` 等）。

**2. 主题与主站三态一致。** G08 讲过 Gmeek 把主题存在 `localStorage` 的 `meek_theme` 键里（light/dark/auto），同域页面共享。404 页开头读这个键，复刻主站的判定：dark 直接暗色，light 亮色，auto 跟 `prefers-color-scheme`：

```javascript
var t = localStorage.getItem('meek_theme') || 'auto';
var dark = t === 'dark' ||
    (t !== 'light' && window.matchMedia &&
     window.matchMedia('(prefers-color-scheme: dark)').matches);
document.documentElement.setAttribute('data-color-mode', dark ? 'dark' : 'light');
```

这样读者在主站选了暗色，手滑进 404 不会被白页闪瞎。注意这是独立页的折中方案——它不监听主题切换按钮（页面上压根没有），但进入瞬间的状态永远和主站一致。

**3. 迷路时给内容，不只给按钮。** 这页也 fetch 了 `postList.json`，取最新 5 篇文章（排序逻辑与 G08/G10 同款：日期倒序、编号兜底），渲染成"或者，从最新文章里挑一篇"。读者输错地址时，被接住的最好方式是直接给读者可看的东西。fetch 失败整块隐藏——降级成只有两个按钮的简洁版，绝不报错。

**4. 零外部依赖。** 不加载任何第三方 CSS/JS/字体，系统字体栈兜底。404 是"出错时刻"，页面必须在网络最差的时候也能秒开。

页面结构就是一张居中卡片：渐变数字 404、一句叶扬式调侃（"这页大概是坐时光机走丢了"）、两个按钮（🏠 首页 / 🗂 归档——归档入口正好用上 G10 成果）、最新文章列表、页脚签名。

实拍一张（故意访问一个不存在的地址）：

![自定义 404 页：渐变 404、坐时光机走丢了文案、回首页/逛归档按钮、最新五篇文章](/screenshots/g11-404.png)

## 五、验证清单

| 检查 | 期望 | 实测 |
|---|---|---|
| `GET /robots.txt` | 200，`text/plain`，无 BOM、LF 行尾 | ✅ 首字节 `23 20 72`（`# r`），0 个 CR |
| Googlebot UA 访问 | 同样 200 可读 | ✅ |
| `GET /404.html` | 200，含 noindex | ✅ |
| 不存在的根路径 | **404 状态码** + 自定义页内容 | ✅ |
| `/post/999.html`、`/a/b/c` | 404 + 自定义页（深层路径生效） | ✅ |
| sitemap / RSS | 条数不变（19 URLs），不含 404/robots | ✅ |
| 最新文章列表 | #17、#15、#14、#13、#12 | ✅ |

行尾和 BOM 值得多说一句：Windows 上 git 默认可能在工作区把 LF 转成 CRLF（提交时能看到那两条 warning），但仓库 blob 存的是 LF，Action checkout 后复制到线上的仍是干净 LF——叶扬专门 curl 下来 `tr -cd '\r' | wc -c` 数过，为 0。robots 解析器对 CRLF 其实也兼容，但干净永远是好习惯。

## 小结

两个文件，零配置，补齐了站点的两副面孔：**对机器**，robots.txt 显式表达收录态度、钉上 sitemap 入口；**对人**，404 页用同色系、同主题、最新文章把迷路读者接住。原理上就记住一句：**static/ 是"原样到达站点根"的传送门，且每次构建全量重刷**。

> 顺带记录一个现场：本文发布后普通文章达到 16 篇，越过了 config 里 `onePageListNum:15` 的单页上限，首页底部**第一次出现"下一页"分页条**（框架自动生成 page2.html，最早的搭建篇被请去了第二页）。纯框架行为，无需任何操作——数字分页的美化留给 G13。

下一期 G12 做个体验小补丁：让正文中的外链自动在新标签页打开（`target="_blank"` 加 `rel="noopener"`），内链保持当前页跳转——读者点开参考资料时不再被"逐出"博客。

## 参考

- GitHub Pages 自定义 404 官方文档：<https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-custom-404-page-for-github-pages-site>
- Robots Exclusion Protocol 标准 RFC 9309：<https://www.rfc-editor.org/rfc/rfc9309>
- Sitemap 协议（robots 中的 Sitemap 指令）：<https://www.sitemaps.org/protocol.html#submit_robots>
- static 复制逻辑：[Gmeek.py](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py)（约 70–88 行）
- 相关前作：[G04 SEO 与 sitemap](/post/10.html)、[G08 上一篇/下一篇](/post/14.html)、[G10 时间线归档页](/post/17.html)
- 系列总揽：[Gmeek 插件与功能全景调研（第 0 篇）](/post/5.html)

