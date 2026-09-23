> 🗺 [博客地图](/post/47.html) ｜ 全部系列的总入口（本篇只管 G 进阶篇）

> 这是 Gmeek 系列教程的**第 0 篇**：一张完整的功能地图。本文不教具体操作，而是回答两个问题——Gmeek 到底还藏着哪些能力？哪些值得搬、哪些不值得搬？文中每个结论都附了一手出处（官方源码、作者博客、社区 issue、原始教程），后续每动手复现一个功能，就会发一篇编号教程并在文末路线图里打勾。博客现阶段的内容方向也由此确定：**先把 Gmeek 本身玩透**。

## 怎么读这篇文章

- **想抄作业**：直接跳到文末「系列教程路线图」，按编号等后续教程；
- **想自己深挖**：每个功能都附了出处链接，优先看源码而不是二手转述；
- **想看结论**：每节末尾都有"叶扬的判断"。

本系列的编号约定：第 0 篇是总揽，之后每篇教程以 G01、G02…… 编号，文末路线图会持续更新。前面三篇相关文章是本系列的前传：

- [用 GitHub Issues 写博客：Gmeek 搭建全过程与原理](/post/1.html)
- [Gmeek 右侧"文章目录"导航栏：插件原理与接入全过程](/post/3.html)
- [一个博客除了评论还需要什么：叶扬的博客基础功能建设清单](/post/4.html)

## 调查的一手来源

结论不是凭印象，全部来自以下材料交叉验证：

| 来源 | 链接 | 价值 |
|---|---|---|
| Gmeek 源码仓库 | [Meekdai/Gmeek](https://github.com/Meekdai/Gmeek) | `plugins/`、`templates/`、`Gmeek.py` 是最终事实依据 |
| 官方插件目录 | [plugins/](https://github.com/Meekdai/Gmeek/tree/main/plugins) | 官方全部 5 个插件 |
| 构建脚本 | [Gmeek.py](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py) | 所有配置项的默认值与解析逻辑 |
| 官方插件进阶教程 | 《[【Gmeek 进阶】插件功能的使用](https://blog.meekdai.com/post/%E3%80%90Gmeek-jin-jie-%E3%80%91-cha-jian-gong-neng-de-shi-yong.html)》 | 作者亲自维护的插件收录文，好插件会被收入 |
| 作者本人博客配置 | [meekdai.github.io/config.json](https://github.com/Meekdai/meekdai.github.io/blob/main/config.json) | 官方"最佳实践"样本 |
| Issue #167 | [插件分享基地](https://github.com/Meekdai/Gmeek/issues/167) | 社区插件集散地 |
| Issue #145 | [SEO 优化相关问题](https://github.com/Meekdai/Gmeek/issues/145) | 作者确认 RSS 可直接当 sitemap 提交 |
| Issue #186 | [提一些需求](https://github.com/Meekdai/Gmeek/issues/186) | 外链新窗口、数字分页条等社区需求出处 |
| Issue #100 / #134 | [目录需求](https://github.com/Meekdai/Gmeek/issues/100)、[代码复制建议](https://github.com/Meekdai/Gmeek/issues/134) | 功能演进的来龙去脉 |

## 一、官方插件全档案

官方插件一共 5 个，全部位于源码仓库 `plugins/` 目录，机制完全一致：**一个自包含 JS，放进 `static/` 目录，用配置字段注入页面，CSS 自己动态注入**。这是 Gmeek 插件哲学的核心——不改上游模板，升级零冲突，删掉一行配置即回退。

### 1. GmeekVercount.js —— 访问统计（已装）

- **功能**：站点总 PV/UV、文章页 PV，数据自存在 [Vercount](https://vercount.one/) 服务，无需注册。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/GmeekVercount.js)
- **官方态度**：进阶教程里**首推**。替代的不蒜子（busuanzi）已长期无人维护，且在 Safari 下计数不准。
- **叶扬的判断**：保留。只记数字、不追踪个人身份，符合[第 4 篇](/post/4.html)立的统计克制原则。另一个统计插件 `GmeekBSZ.js`（不蒜子）**不要装**。

### 2. GmeekTOC.js —— 右侧文章目录（~~已装~~ 已退役留档，见 [G16](/post/25.html)）

- **功能**：扫描正文 `h1~h6` 生成固定在右侧的目录，按标题级别缩进，窄屏自动收为文章内块，附 Top 回顶按钮。零依赖，100 行。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/GmeekTOC.js)；接入全过程见本站[第 3 篇教程](/post/3.html)。
- **关键坑**：只能走 `script` 字段（仅文章页注入），**不能放 `allHead`**——首页没有 `id="content"` 元素，会抛 TypeError。
- **叶扬的判断**：官方文档站自己在用，配色全走 Primer CSS 变量自动适配暗色。本站第一个接入的插件（前传 #3），平铺目录无 scrollspy；**G16 起被本地化改造的 GmeekTocBot 接替，config 摘除引用、文件留在 `static/plugins/` 留档可回退**。

### 3. lightbox.js —— 图片灯箱（✅ 已装，见 [G05](/post/11.html)）

- **功能**：文章图片点击放大，支持滚轮缩放、左右键切换上一张/下一张、触屏滑动、相邻图片预加载、毛玻璃遮罩、点遮罩关闭。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/lightbox.js)（357 行，零外部依赖，所有样式与 DOM 都由插件自建）；官方进阶教程收录，由社区用户 **Tiengming** 贡献。
- **叶扬的判断**：官方插件里完成度最高的一个，G05 已接入（`static/plugins/lightbox.js` + config `script` 拼接）；教程里用 og.png/favicon.svg 两张图做了可点击演示。

### 4. articletoc.js —— 悬浮按钮式目录（✅ 已装，见 [G14](/post/21.html)）

- **功能**：不在正文里占位置，而是在右下角放一个 ☰ 圆形按钮，点击弹出目录浮层，再点外部关闭；自带亮/暗两套 CSS 变量。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/articletoc.js)，同为 Tiengming 贡献。
- **叶扬的判断**：原版与 GmeekTOC 同名 `.toc`，同时加载会被浮层的 `opacity:0;visibility:hidden` 连坐藏掉桌面目录，所以官方只让二选一。**G14 已用类名隔离（`.toc-mobile`）实现共存**：桌面 >1249px 常驻右侧目录、圆形按钮隐藏；≤1249px 隐藏桌面目录退化出的文首静态块、右下角 ☰ 浮层当班（G16 起桌面目录换成 GmeekTocBot，契约不变、分工不变）。另把原版 `prefers-color-scheme` 暗色换成 Primer 变量（#196 三态失配），补空标题守卫、点链接/Esc 收起与 aria-expanded 键盘可达。

### 5. GmeekTocBot.js —— tocbot 版目录（✅ 已本地化接入，见 [G16](/post/25.html)）

- **功能**：封装成熟库 [tocbot](https://tscanlin.github.io/tocbot/)，视觉层级更好，独有**滚动时高亮当前章节**能力。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/GmeekTocBot.js)；依赖 `cdnjs.cloudflare.com` 上的 tocbot 4.27.4。
- **叶扬的判断**：功能最强但原版依赖第三方 CDN，与本站"静态资源全部本地化"的原则冲突。**G16 已按当年预案落地**：tocbot 4.27.4 引擎（11KB）下载到 `static/tocbot/tocbot.min.js`，CSS 六条规则内联并全换 Primer 变量；适配版 `static/plugins/GmeekTocBot.js` 另修官方壳六处将就（id 缺 toLowerCase、100vh 空白 div、容器清空、window.onscroll 覆盖、无空标题守卫、暗色裸奔），接替 GmeekTOC 接管桌面目录。

> **插件组合用法**（官方进阶教程原文给出的方式）：多个插件可以直接拼在同一个字段里：
> `"script":"<script src='...GmeekTOC.js'></script><script src='...lightbox.js'></script>"`

## 二、改一行配置就能解锁的框架能力

读 `Gmeek.py` 第 91 行的默认配置字典和作者本人博客的 `config.json`，发现一大批**框架早就支持、但本站配置里没写**的能力。这是性价比最高的一层：不用写任何代码。

### 固定页面与导航

| 配置项 | 作用 | 出处/样本 |
|---|---|---|
| `singlePage` | **固定页面机制**：值是 label 名数组，如 `["about"]`。新建一个带 `about` 标签的 issue，框架会生成根路径下的独立页 `about.html`，**不进文章列表**，页头自动出现入口按钮 | 作者配置 `"singlePage":["link","about"]`，对应 [about 页](https://blog.meekdai.com/about.html) |
| `iconList` | 定义页头按钮的 SVG 路径（16px）。内置 sun/moon/sync/search/rss/upload/post/home/github/copy/check，自定义页面按钮需在此配图标 | `Gmeek.py:215` 按钮渲染逻辑 |
| `exlink` | 页头外部链接按钮，如作者的 `"music":"https://music.meekdai.com"` | 作者配置实测 |

这正是[第 4 篇](/post/4.html)路线图里 P0「About 页面」的官方正解，已由 **[G01](/post/7.html)** 完成（含一个真实踩坑：新增 singlePage 后必须手动全局重建）。

### 页脚信息

| 配置项 | 作用 | 出处 |
|---|---|---|
| `bottomText` | 全站页脚底部追加一行自定义文字，作者写的是 `❤️ 转载文章请注明出处，谢谢！❤️` | [footer.html](https://github.com/Meekdai/Gmeek/blob/main/templates/footer.html) |
| `startSite` | 建站日期（如 `"02/16/2015"`），页脚自动显示"本站已运行 N 天" | footer.html 内联脚本 |
| `filingNum` | ICP 备案号，自动链到工信部备案系统 | 绑定国内备案域名后才有用 |

`bottomText` 一举解决路线图里的「文末版权声明」，已由 **[G02](/post/8.html)** 完成（另含 `startSite` 运行天数与日期格式的时区坑）。

### 身份与分享

| 配置项 | 作用 | 备注 |
|---|---|---|
| `faviconUrl` | 浏览器标签页图标；不配置时默认复用 `avatarUrl` | 作者用的是自制 SVG |
| `ogImage` | Open Graph 分享卡片封面；不配置时默认头像 | 文章级还能单独覆盖 |
| `displayTitle` | 页头显示标题，默认与 `title` 一致 | 想让站名短、标题完整时用 |
| `homeUrl` | 站点绝对地址 | **绑定自定义域名后必须配**，否则分页/RSS 链接错乱 |

favicon + ogImage 已由 **[G03](/post/9.html)** 完成：自制"叶"字 SVG 图标（明暗自适应）+ Pillow 生成 1200×630 PNG 封面；注意 `ogImage` 只认位图绝对 URL，SVG 不行。

### 注入与自定义（插件体系的另一半）

| 配置项 | 注入位置 | 加载范围 |
|---|---|---|
| `allHead` | 所有页面 `<head>` | 全站（统计脚本用它） |
| `head` | 文章页 `{% block head %}` | 仅文章页头部 |
| `script` | 文章页底部 | **文章级插件**（TOC、lightbox） |
| `style` | 文章页 | 文章级 CSS |
| `indexScript` / `indexStyle` | 首页与列表页 | 仅列表页 |

出处：模板 [base.html](https://github.com/Meekdai/Gmeek/blob/main/templates/base.html)、[post.html](https://github.com/Meekdai/Gmeek/blob/main/templates/post.html)、[plist.html](https://github.com/Meekdai/Gmeek/blob/main/templates/plist.html) 中的注入点，以及 `Gmeek.py:91` 默认值。

### 外观与排版

| 配置项 | 作用 | 默认 |
|---|---|---|
| `themeMode` | `manual`（亮/暗/跟随系统三态手动切换）或 `fix` 固定 | `manual` |
| `dayTheme` / `nightTheme` | GitHub 主题名，可换 `dark_dimmed`、`dark_colorblind` 等 | `light` / `dark` |
| `commentLabelColor` | 标签颜色 | `#006b75` |
| `yearColorList` | 按年份轮换的日期标签色，作者博客四种颜色 | 四色数组 |
| `onePageListNum` | 首页每页文章数，超过自动分页 | 15 |
| `primerCSS` | Primer CSS 地址，**默认已是南科大国内镜像**，国内访问无需折腾 | `mirrors.sustech.edu.cn` |
| `i18n` | `CN` / `EN` / `RU` 界面语言 | `CN` |
| `showPostSource` | `1` 显示文末"Issue 原文"按钮，`0` 隐藏 | 1 |

### URL 与订阅

| 配置项 | 作用 |
|---|---|
| `urlMode` | 文章 URL 模式：`pinyin`（标题转拼音，默认）/ `issue`（本站使用，`/post/编号.html`，永久不受改标题影响）/ `ru_translit` |
| `rssSplit` | RSS 摘要截断规则：`sentence`（第一句句号）或其他自定义分隔符 |
| `needComment` | `1` 开评论 / `0` 全站关闭 utterances |
| `UTC` | 时区偏移，默认 `+8` |

## 三、单篇文章的"隐藏语法"

`Gmeek.py:355` 会解析每篇 issue 正文**最后一行**的特殊 HTML 注释，实现文章级配置，这是官方进阶教程里明确支持、但很多人不知道的功能：

```html
<!-- ##{"script":"<script src='...'></script>","style":"...","ogImage":"https://.../cover.png","timestamp":1700000000}## -->
```

| 字段 | 用途 |
|---|---|
| `script` / `style` / `head` | 只给这一篇注入插件和样式（如只有一篇多图文章需要 lightbox） |
| `ogImage` | 单篇专属分享封面 |
| `timestamp` | **自定义发布时间戳**，补发旧文、迁移文章时让排序归位 |

**G06 已完成**（[教程](/post/12.html)）：文章自身就是活 demo——末行 JSON 给本篇注入了 h2 绿竖条、文末虚线徽章和控制台彩蛋。补充两个实测细节：解析行在新版源码为 `Gmeek.py:357`；gh API 发布的 LF 正文会被 GitHub 规范化为 CRLF（backup 实锤），所以换行坑只存在于本地调试。

## 四、你可能没意识到的开箱功能

以下能力不用配置、不用插件，写 Markdown 时直接存在：

1. **代码块一键复制**：GitHub 同款 copy/check 图标按钮，[post.html](https://github.com/Meekdai/Gmeek/blob/main/templates/post.html) 内置（对应早期社区 issue #134 的诉求，现已官方解决）。
2. **数学公式按需加载**：正文直接写 `$E=mc^2$`（行内）或 `$$...$$`（块级），GitHub 渲染成 `<math-renderer>` 标签后，框架剥掉标签壳、注入 MathJax 3（jsdelivr CDN），不写公式的文章零开销（[G07](/post/13.html) 已实测；坑：正文中的美元金额要用反引号包，避免成对 `$` 被当公式）。
3. **GitHub Alert 提示块**：`> [!NOTE]`、`> [!TIP]`、`> [!IMPORT]`、`> [!WARNING]`、`> [!CAUTION]` 自动渲染成 GitHub 官网同款彩色边框块，框架检测到 `markdown-alert-title` 自动补五套配色（`Gmeek.py:159` 起，颜色走 Primer CSS 变量，明暗自适应）。注意 API 渲染的标题是英文 Note/Tip/…，静态页不做本地化。
4. **三态主题与评论联动**：亮 → 暗 → 跟随系统循环；切换时通过 `postMessage` 让 utterances 评论 iframe 同步换肤（[base.html:54](https://github.com/Meekdai/Gmeek/blob/main/templates/base.html)）。
5. **列表分页**：文章数超过 `onePageListNum`，首页自动出现上一页/下一页。
6. **每日定时重建**：工作流除了监听 issue 事件，还有一条 `schedule: cron("0 16 * * *")`，即**北京时间每天 0:00 自动全量重建**一次。Webhook 丢失、改了配置忘记手动构建，第二天都会自愈。注意：Issue 事件只触发**增量构建**，`config.json` 的结构性变更（如新增 singlePage）不会被加载，必须手动跑一次全局重建——G01 实操时踩过这个坑。
7. **Markdown 原文自动备份**：每次构建把 issue 正文存进仓库 `backup/` 目录，`git clone` 即整站离线副本。
8. **RSS 即 sitemap**：见下节，单独说。

写作技巧已由 **[G07](/post/13.html)** 完成：Alert/公式零配置；Mermaid 非内置（GitHub API 只语法高亮不出图）。**[G15](/post/24.html) 已把 mermaid 升级为自动检测、按需加载**：`static/plugins/GmeekMermaid.js` 检测到 `highlight-source-mermaid` 块才动态加载 `static/mermaid.min.js`（v11，3.5MB），跟随三态主题重绘，作者零配置——G07 时代「含图文章末行手写挂载 JSON」的旧三件套已退役（末行 JSON 漏写即静默失败，是 G15 案发根因）。另有内联反引号 `Gmeek-html` 直出 HTML 的彩蛋（围栏代码块不生效）。

## 五、SEO：被问得最多，答案却最简单

社区 issue [#145](https://github.com/Meekdai/Gmeek/issues/145) 里有人建议生成 `sitemap.xml`，作者的回复是：**`rss.xml` 已包含全站所有重要页面链接，作者本人就是把 rss.xml 提交给 Google 的**；提问者随后验证，必应和谷歌都能正常识别 RSS 作为站点地图。

**G04 已落地**（[教程](/post/10.html)）：

- Google Search Console / Bing 站长工具直接提交 `rss.xml` 即可（Bing 添加站点时还能从 GSC 一键导入，验证状态继承）；
- 百度的 sitemap 工具按 sitemaps.org 协议解析、不认 RSS，已在工作流新增 `sitemap_gen.py`，每次构建从 `postList.json` 自动生成标准 `sitemap.xml`，三家都提交它做双保险；
- RSS 之外，`robots.txt` 和自定义 `404.html` 直接放进 `static/` 根目录即可，构建时原样复制到站点根，GitHub Pages 原生识别（✅ 已完成，见 [G11](/post/18.html)：robots 显式 Allow + Sitemap 绝对 URL；404 独立页 noindex、三态主题读 meek_theme、fetch 最新 5 篇）。

## 六、社区生态盘点：有宝贝，也有大坑

Gmeek 没有独立插件市场，[issue #167「插件分享基地」](https://github.com/Meekdai/Gmeek/issues/167)事实上承担了这个角色。翻遍社区代码后：

**值得借鉴的：**

- **数字分页条** ✅：把"上一页/下一页"换成 1/2/3 页码，文章几十篇以后有用，[issue #186](https://github.com/Meekdai/Gmeek/issues/186) 需求 2。社区李轶凡《[给博客添加数字分页条](https://blog.liyifan.xyz/post/gei-bo-ke-tian-jia-shu-zi-fen-ye-tiao.html)》提供了思路，但 2026-09 调研时原站 DNS 失联、GitHub 仓库源码已撤、Wayback 无存档，**已完成见 [G13](/post/20.html)（借鉴失败转为自研）**：`static/plugins/GmeekPager.js`，90 行零 CSS——复用 Primer 21 内建 `.current/.gap` 样式与三档响应式显隐；保留框架原生 prev/next 节点只插中间数字；`config.indexScript` 首次启用（仅注入 index/pageN，tag 页不注入）；fetch postList.json 计数过滤 labelColorDict；≤7 页全显、否则首尾页+当前页±1+省略号；单页/失败/超界三态静默降级。
- **外链新窗口打开** ✅：同 issue #186 的头号需求，**已完成见 [G12](/post/19.html)**。`static/plugins/GmeekExternal.js`：URL 构造器按 hostname 判内外（协议相对 URL/自家绝对 URL 都不误判），外链补 `target=_blank` + 合并 `rel=noopener`；显式 target 不覆盖、rel 只合并不替换；不自动加 nofollow（SEO）、不加 noreferrer（保留来路）。

**看看就好、不要搬的：**

- 社区用户 luliy6 的 `enhance.js`：约 5884 行的整站换肤方案——开屏动画、全屏 Hero、六张分类卡片、APlayer 音乐播放器、抽屉式菜单。代码本身值得学习"一个 JS 能做到什么程度"，但它与本系列[第 4 篇](/post/4.html)立的三条规矩（静态优先、走插件机制不改模板、为长期写作服务）全部冲突，**明确不借鉴**。
- GitHub 代码搜索能找到的其他"插件"，90% 是把官方 5 个 JS 复制改名，无新东西。

## 七、框架的空白：需要自研的功能

对照[第 4 篇](/post/4.html)的清单，以下功能官方与社区都没有可靠现成方案，需要自己写插件。好在 Gmeek 把数据都放在了 `postList.json`，自研难度不高，这也会是本系列最"硬核"的几篇：

| 功能 | 实现思路 | 编号 |
|---|---|---|
| ~~文章末尾上一篇/下一篇~~ ✅ | **已完成，见 [G08](/post/14.html)**：`static/plugins/GmeekPrevNext.js`，90 行零依赖；URL 正则定位当前篇（顺带防 about 页）、createdDate+编号排序（兼容 timestamp 补发）、Primer 变量自适应暗色、插在评论按钮前、首尾显示禁用占位 | G08 ✅ |
| ~~字数统计与预计阅读时长~~ ✅ | **已完成，见 [G09](/post/15.html)**：`static/plugins/GmeekReadTime.js`，50 行零依赖；CJK 汉字按字（三个表意文字区段，码位转义防同形字）+ 拉丁串按词混合计数、标点不计、代码块计入；中文 400 字/分钟，不足 1 分钟按 1 分钟；插在 `#content` 最前；Primer 变量三态适配；手机端仅缩字号不重排 | G09 ✅ |
| ~~时间线归档页~~ ✅ | **已完成，见 [G10](/post/17.html)**：新增 archive 固定页（issue #16，只打 archive 标签）+ `static/plugins/GmeekArchive.js`；Gmeek-html 彩蛋写挂载点 div；读 postList.json 过滤 labelColorDict 假键、日期倒序+编号兜底、按年分组、sticky 年份与时间线 CSS；iconList 配 Octicon archive 图标；RSS 置顶收录固定页、sitemap 自动+1；发布须双次全局重建 | G10 ✅ |

这三篇完整演示"如何写一个自己的 Gmeek 插件"，而不只是抄配置。

## 八、系列教程路线图

总揽即 roadmap。每完成一篇，这里会更新链接；状态图例：✅ 已发布 / ⏳ 计划中 / 💤 远期再说。

| 编号 | 教程 | 功能 | 类型 | 状态 |
|---|---|---|---|---|
| 前传 | [搭建全过程与原理](/post/1.html) | 建站 | 教程 | ✅ |
| 前传 | [博客基础功能建设清单](/post/4.html) | 规划 | 清单 | ✅ |
| G00 | 本文 | 全景调研 | 总揽 | ✅ |
| —— | [右侧文章目录插件](/post/3.html) | GmeekTOC | 教程 | ✅ |
| G01 | [固定页面机制：做一个不进文章流的 About 页](/post/7.html) | `singlePage` + `iconList` | 配置 | ✅ |
| G02 | [页脚装修：版权小字与"本站已运行 N 天"](/post/8.html) | `bottomText` + `startSite` | 配置 | ✅ |
| G03 | [给博客一张脸：自制 SVG favicon 与社交分享封面](/post/9.html) | `faviconUrl` + `ogImage` | 配置 | ✅ |
| G04 | [把门牌号递给搜索引擎：RSS 直接当 sitemap 提交](/post/10.html) | GSC / Bing / 百度 + `sitemap_gen.py` | SEO | ✅ |
| G05 | [给文章图片装一盏灯：官方 lightbox 灯箱插件](/post/11.html) | 官方插件 | 教程 | ✅ |
| G06 | [文章末尾的秘密：一行隐藏 JSON，给单篇文章开小灶](/post/12.html) | 文章级配置 | 原理 | ✅ |
| G07 | [写作三件套：Alert 提示块、数学公式、Mermaid 图表](/post/13.html) | 内置语法 + mermaid 三件套 | 教程 | ✅ |
| G08 | [自研插件（一）：文章末尾的"上一篇 / 下一篇"](/post/14.html) | `postList.json` | 自研 | ✅ |
| G09 | [自研插件（二）：标题下的字数与阅读时长](/post/15.html) | DOM 统计 | 自研 | ✅ |
| G10 | [自研插件（三）：凭空造出的时间线归档页](/post/17.html) | `singlePage` + 数据渲染 | 自研 | ✅ |
| G11 | [运维两小件：robots.txt 与自定义 404 页](/post/18.html) | `static/` 直出 | 运维 | ✅ |
| G12 | [小补丁：外链自动新标签页打开](/post/19.html) | URL 判定 + noopener | 自研 | ✅ |
| G13 | [数字分页条：借不到轮子，就自己造一个](/post/20.html) | `indexScript` + Primer 内建分页样式 | 自研（社区方案失联） | ✅ |
| G14 | [手机上的文章目录：右下角 ☰ 与两个 TOC 插件的和平共处](/post/21.html) | articletoc 适配 + 类名隔离/响应式分工 | 官方插件适配 | ✅ |
| G15 | [Mermaid 翻车记：自动检测按需加载，顺手给 Gmeek 提个 PR](/post/24.html) | GmeekMermaid 自研插件 + 上游 #236/PR#319 | 自研 + 开源回馈 | ✅ |
| G16 | [目录会读心：把 tocbot 请到本地，让当前章节一路高亮](/post/25.html) | CDN 资源本地化 + scrollspy | 进阶 | ✅ |
| 番外 | [给博客拍证件照：零依赖无头截图流水线，与一桩白底怪案](/post/26.html) | CDP + Fetch 域拦截 | 工具/方法论 | ✅ |
| G17 | [SEO 收尾战：canonical、结构化数据和干净的摘要，一次补齐](/post/27.html) | GmeekSEO 运行时注入 canonical/JSON-LD/twitter/清洁 description | SEO | ✅ |
| 番外二 | [我给 Gmeek 提了三个 PR：一次开源回馈的完整流水线](/post/28.html) | 11 件自研件过筛 + PR #319/#320/#321 + issue #322 + review #307 | 开源回馈/方法论 | ✅ |
| G18 | [被浮动挤扁的"上一篇 / 下一篇"：一桩 BFC 避让案](/post/29.html) | float:right 与 BFC 避让致卡片被压窄；clear:both + 小屏去浮动 + meta 行合并，移动/桌面双修复 | CSS/修 bug | ✅ |
| 番外三 | [浏览器外的屏幕怎么截：ffmpeg gdigrab 抓窗口三坑记](/post/31.html) | DComp 黑白窗 / 高 DPI 逻辑坐标 / 越界与 error 5；成品 `tools/shot-window.ps1` | 工具/方法论 | ✅ |
| 番外四 | [点到为止：让 AI 借你已登录的浏览器截一张图](/post/33.html) | Win32 UI 自动化登录态截图六场翻车 + 安全边界；EnumWindows 正向定位/命令行委派导航/样式位辨真假全屏；成品 `tools/ui-shot.ps1`；截图三部曲收束 | 工具/方法论/AI 协作 | ✅ |
| 番外五 | [踩坑手册怎样变成 AI 技能：博客、CLAUDE.md、记忆与 Skill 的分工](/post/37.html) | 以 mermaid v11 时序图不可读为贯穿案例讲四层归宿；渐进式披露/记忆索引常驻/CLAUDE.md 是 context 非强制配置；官方文档 code.claude.com 为凭 | AI 协作/方法论 | ✅ |
| 实操一 | [零后端全站搜索：给 Gmeek 博客接 Pagefind 的完整实操](/post/68.html) | Pagefind：Actions 每次构建自动索引（72 页/2MB）＋GmeekPagefind 插件全站入口＋明暗适配；中文 extended 二进制词典分词＋Intl.Segmenter；**「GitHub 好项目实操」系列开篇** | 好项目实操 | ✅ |
| 实操二 | [终端录屏也能写成脚本：VHS 完整实操（Windows 三坑＋asciinema 对比）](/post/69.html) | VHS：`.tape` 声明式脚本渲染终端 GIF/MP4/WebM，三百多主题；Windows 三坑＝ttyd error 267（`-w .` 包装器）/v0.12.0 已取消 ctx（钉 v0.11.0）/首字 race（先 Sleep）；asciinema cast 纯文本＋player 可暂停复制 | 好项目实操 | ✅ |
| 实操三 | [一个 CLI 统管七十多种存储：rclone 备份同步完整实操（crypt 加密＋Actions 定时）](/post/70.html) | rclone：copy 只增不删 / sync 镜像（必先 `--dry-run`）/ check 验证；`--backup-dir` 留档＋`--filter` 有序过滤＋`--bwlimit` 限速；crypt 包裹层把内容与文件名全加密（RCLONE 魔数、143 字符安全线、obfuscation 退路、filename_encoding）；坑＝serve `--pass` 要明文别喂 obscure；Actions 定时备份（凭据走 Secrets）；restic 去重快照分工 | 好项目实操 | ✅ |

更新方式：每篇教程发布后，叶扬会回来编辑本文（Gmeek 监听 issue 的 `edited` 事件，编辑即自动重建），所以这张表会一直是最新的。

## 另一条线：地基篇（B 系列）

G 系列默认读者**已经有一个博客**。不少新读者反馈"连仓库都还没建，不知道该从哪篇看起"，于是另开了一条零起点线，从"一个 GitHub 账号都没有"讲起：

👉 **从零开始请直接读 [B00 地基篇总览](/post/30.html)**，B01–B03 已发布、B04–B08 计划中；地基篇的路线图表与发布日志都维护在 B00 一篇里，本文不再搬运，以免两张表各说各话。

两条线的分工一句话：**B 系列让你拥有一个博客，G 系列让你拥有"你的"博客。**

## 收官之后：候选选题池（G17 起）

正篇 G01–G16 收官，[建设清单（前传 #4）](/post/4.html)也已回填，但清单并非一无所有。2026-09-15 盘出以下候选，按写作意愿排序：

| 候选 | 内容 | 依据 | 状态 |
| --- | --- | --- | --- |
| ~~**G17 SEO 收尾战**~~ | 文章页补 `<link rel="canonical">`、JSON-LD（BlogPosting 结构化数据）、twitter:card；顺手清洁 `meta description`——框架当前直接取正文开头，会把 `>` 引用符和 `[文字](链接)` 语法原样塞进搜索摘要。**成品 [`static/plugins/GmeekSEO.js`](https://github.com/yeyangchen2009/yeyangchen2009.github.io/blob/main/static/plugins/GmeekSEO.js)（135 行，运行时注入，挂 script 首位）** | #4 清单上仅剩的技术缺口 | ✅ 已发布（2026-09-15，[G17](/post/27.html)） |
| ~~番外·给博客拍证件照~~ | 零依赖无头浏览器截图教程：Node 内置 WebSocket 直连 CDP（不装 puppeteer），Fetch 域拦截 CSS 破解 headless 样式加载失败、localStorage 注入暗色、2x 高清、元素级 clip 截全图；产物即本批 9 张教程插图。**成品脚本 [`tools/cdp-shot.js`](https://github.com/yeyangchen2009/yeyangchen2009.github.io/blob/main/tools/cdp-shot.js)** | 给 9 篇老教程补截图的完整实战 | ✅ 已发布（2026-09-15，[番外](/post/26.html)） |
| ~~番外二·开源回馈流水线~~ | 11 个自研件按"需求佐证 / 形态匹配 / 兼容包袱"三标准过筛 → PR [#320](https://github.com/Meekdai/Gmeek/pull/320) GmeekExternal、[#321](https://github.com/Meekdai/Gmeek/pull/321) GmeekSEO（另带 #319 KeyError 修复），根治 issue [#322](https://github.com/Meekdai/Gmeek/issues/322)；帮 [#307](https://github.com/Meekdai/Gmeek/pull/307) 写验证式 review、[#318](https://github.com/Meekdai/Gmeek/issues/318) 贴对照日志；PR 前抓到两桩通用性 bug（project pages 子路径、空 ogImage）。**三个 PR 全部 Open 待合并，未被官方收录** | 维护者在 #145 亲口承诺"有空写插件"七个月未兑现 + #319 探路 | ✅ 已发布（2026-09-16，[番外二](/post/28.html)） |
| ~~番外三·gdigrab 抓窗口~~ | 番外一的 cdp-shot.js 只管浏览器内；浏览器外改用 ffmpeg gdigrab 抓 desktop 合成表面再按窗口矩形裁剪。三坑：① `title=` 直抓 DirectComposition 窗口（Windows Terminal）非黑即白，只能抓 desktop 裁剪；② 150% 缩放下非 DPI 感知进程拿到逻辑坐标，必须先 `SetProcessDPIAware` 取物理像素；③ Win11 隐形边框致矩形越界 8px，用 `GetSystemMetrics` clamp，且 `SetForegroundWindow` 后偶发 `error 5`（ACCESS_DENIED）需重试。另记 PS 5.1 中文环境两坑（UTF-8 必须带 BOM、Stop 模式把原生命令 stderr 包装成终止错误）。**成品脚本 [`tools/shot-window.ps1`](https://github.com/yeyangchen2009/yeyangchen2009.github.io/blob/main/tools/shot-window.ps1)** | 番外一截图能力向浏览器外的自然延伸 | ✅ 已发布（2026-09-16，[番外三](/post/31.html)） |
| **番外·收录实战** | G04 提交一周后，Google/Bing 真实收录数据对比、GSC"无法抓取"复查结论，回答"RSS 当 sitemap 到底有没有用"；顺带追踪三个上游 PR 的合并进展 | [G04](/post/10.html)、G16 结尾均已预告 | 📅 约 2026-09-21 后 |
| 实操四·restic 版本化备份 | restic/restic：内容分块去重＋快照版本＋客户端加密的备份工具，[实操三](/post/70.html)已对比分工；可与 rclone 组合（rclone 搬运 restic 仓库做异地容灾） | 好项目实操系列，实操三结尾已预告 | ⏳ 下一篇 |
| 候选·备份双保险 | 用 Actions 把 `backup/` 定期镜像到私有仓库 | #4 运维章自己提的建议 | 待定 |
| 候选·阅读进度条 | 文章顶部滚动进度条，G16 scrollspy 的姊妹篇 | 体验增强 | 选题偏薄，可能并入杂谈 |
| 候选·图片懒加载 | 正文 `img` 补 `loading="lazy"` | #4 清单（灯箱做了、懒加载没做） | 本站每篇图极少，价值低 |
| 候选·跟版方法论 | Gmeek 版本升级流程、PR [#319](https://github.com/Meekdai/Gmeek/pull/319) 合并后的跟踪与回馈闭环 | 运维 | 等上游合并后才有料 |
| ⏭️ 主动挂起 | 分享按钮、友链固定页、独立域名 + 百度收录 | #4 P2 | 有真实需求再说，不算欠债 |

### 2026-09-15 上游复盘：为什么说"功能做得差不多了"

当天又把官方仓库和社区翻了一遍，给"还该不该继续堆功能"一个明确交代：

- **官方没有新轮子**：插件仍是 6 个（GmeekBSZ / GmeekTOC / GmeekTocBot / GmeekVercount / articletoc / lightbox），最后更新停在 2026-02-05；[插件基地 #167](https://github.com/Meekdai/Gmeek/issues/167) 两年来无新评论。唯一没装的 GmeekBSZ 明确不装——Vercount 已覆盖其功能，且它在 Safari 下有 PV 重复统计的 bug。
- **搜索只搜标题，知道但暂不修**：框架 `tag.html` 的 `searchShow()` 只对列表条目标题做 `indexOf` 过滤，不索引正文。全站 25 篇标题均可命中；正文搜索要引入 lunr/Pagefind 一类索引，和静态极简路线冲突，等文章量级真的需要再说。
- **图片懒加载，收益以毫秒计**：框架正文 `img` 无 `loading="lazy"`，但全站图片总量极少（本批补图后才略有改善），不做。
- **分享按钮 / 友链页 / 独立域名 + 百度**：均为主动放弃而非欠债——系统自带分享面板与 URL 复制已够用；友链等有真实社交圈再开；百度对未备案的 github.io 域名收录极差，G04 已决定跳过。

结论：除 G17 四项 SEO 技术缺口外，没有"该做没做"的功能了。下一步的写作方向从"造功能"转向"晒方法论"——截图教程、收录实战、跟版记录都属此类。

### 2026-09-16 上游回馈第二波：三 PR + 一 issue + 两条评论

G17 之后把 11 个自研件整体过了一遍筛子（详见 [番外二](/post/28.html)），结论落地为：

- **三个 PR 全部 Open 待合并**：[#319](https://github.com/Meekdai/Gmeek/pull/319)（无标签 issue 增量构建 KeyError，3 行）、[#320](https://github.com/Meekdai/Gmeek/pull/320)（GmeekExternal 外链新标签，42 行，对接 #186）、[#321](https://github.com/Meekdai/Gmeek/pull/321)（GmeekSEO 四件套，138 行，对接 #145 维护者 2024 年的承诺）；
- **根治 issue [#322](https://github.com/Meekdai/Gmeek/issues/322)**：`Gmeek.py:347` 直接取 issue.body 原文做 description，建议构建期从渲染后 HTML 转纯文本——插件是过渡，构建期才是根治；
- **review [#307](https://github.com/Meekdai/Gmeek/pull/307)（sitemap 内建生成）**：五条核对确认（分页页数边界、labelColorDict 时序、runOne 数据完整、两种 Pages 形态、输出位）+ 两条非阻塞建议；质量过关，合并后本站 `sitemap_gen.py` 回迁内建方案；
- **[#318](https://github.com/Meekdai/Gmeek/issues/318) 伪 bug 排查**：当天构建日志实证 lxml 6.1.3 有 cp38 manylinux wheel，帮助定位为环境问题；
- **第二梯队压着不提**：PrevNext/ReadTime/Pager/Archive 四个等维护者对前三连的响应节奏，不一次性轰炸；Mermaid（3.5MB 本地资产）与 articletoc（类名兼容包袱、原作者 PR 在排队）确认缓提。
- PR 前的通用性加固已同步本站：`GmeekSEO.js` 兼容 project pages 子路径、未配 ogImage 时省略图片字段（commit `9e9f21e`，已重建上线）。

### 2026-09-17 站外多平台分发调研（备忘，暂不执行）

番外四发布后盘点了"把系列教程分发到知乎/CSDN 等平台"的可行性，结论先存档，**近期不做**，有传播需要时再启动。

**平台 API 现状：**

| 平台 | 官方发文 API | 备注 |
| --- | --- | --- |
| 博客园 | ✅ MetaWeblog（XML-RPC） | 后台开启即可脚本发布，最省心 |
| Dev.to / Hashnode | ✅ REST / GraphQL | API key 直发，适合技术文 |
| 自建 WordPress | ✅ REST + 应用密码 | 全自动，媒体也能上传 |
| Medium | ⚠️ 半死 | 老 token 可用，新申请基本不批 |
| 微信公众号 | ⚠️ 门槛高 | 个人订阅号接口权限受限 |
| **知乎 / CSDN** | ❌ 无 | 只能 cookies/浏览器模拟，违反用户协议、风控严、**封号风险高，不拿主号试** |
| 掘金 / 思否 / 简书 / 51CTO | ❌ 无 | 只能手工粘贴 |

**两个所有平台通用的坑：** ① 知乎/CSDN/博客园都不渲染 Mermaid，必须先用本地 `mermaid.min.js` + CDP 渲染成 PNG 再上传；② 图片外链——知乎粘贴 Markdown 会自动转存，CSDN 有防盗链需重新上传。

**定位澄清（为什么做、不为什么做）：** 分发**不是为了给独立站引流**——平台外链是 `nofollow`/中转链接不传权重，百度基本不收录 github.io，独立站也没有订阅/产品等转化路径。真正的价值是：搜索占位（百度"Gmeek 教程"关键词目前是空坑）、防搬运抢原创、给上游 Gmeek 项目带新用户、跨平台账号资产。

**同日排查上游官方入口的结论：** Gmeek 仓库 README 无教程区、Discussions 未启用、无 docs/awesome 仓库、作者博客只有自家【Gmeek进阶】系列；作者在 [#179](https://github.com/Meekdai/Gmeek/issues/179) 明确"没有交流群，issue 讨论即可"，无运营社区聚合的打算。唯一社区入口是 hst1189 发起的[#285 网站收录虫洞](https://github.com/Meekdai/Gmeek/issues/285)（`gmeek.dpdns.org` 随机跳转，收录网站而非教程，作者点过赞但非官方背书，今年仍活跃）。未来两个动作挂起：虫洞跟帖报名（一分钟）；等三个 PR 有合并进展后再开"系列教程自荐 issue"（届时身份是贡献者而非广告）。番外五既已发布（2026-09-18），择机可去 [#311 Gmeek 发帖 Skill](https://github.com/Meekdai/Gmeek/issues/311) 分享"图片静态文件走 git commit"的解法（该帖唯一评论正卡在这个问题上）。

**若未来启动，三步走：** ① 先写本地"多平台适配包"导出脚本（`gh issue view` 取 Markdown 源 → Mermaid 转 PNG → Alert 语法降级 → 输出 `dist/<n>/文章.md + images/`），纯本地零风险；② 博客园/Dev.to 走 API 自动化；③ 知乎/CSDN 半自动——脚本备好包，人工登录粘贴发布，文末仅留一行原文链接满足原创声明，正文操作链接指向上游仓库而非自己的站。

### 2026-09-18 番外五发布：踩坑经验的四层归宿

发布 **[番外五·踩坑手册怎样变成 AI 技能](/post/37.html)**，兑现番外四结尾的预告。全篇以"mermaid v11 时序图信号文字在亮色文章页不可读"这一个坑为贯穿案例，讲清一条经验的四层归宿——**博客写给人看、CLAUDE.md 每次会话全量在场立规矩、Auto memory 跨会话记事实（MEMORY.md 索引常驻、主题文件按需读）、Skill 只有 description 常驻而正文/脚本调用时才加载（渐进式披露）**。所有机制以官方文档 `code.claude.com/docs/en/memory` 与 `/skills` 为凭，关键结论：CLAUDE.md 与 memory 都是**上下文而非强制配置**（硬拦截要 PreToolUse hook）；多步流程应从记忆/规矩升级成 Skill。

同一坑的四份归宿都已落地：① 博客——B01/B04 时序图已改 flowchart、本篇讲清原理；② CLAUDE.md——全局那份 Mermaid 约定里"时序图可追加 actorBkg 等变量"的条款已被 v11 证伪，2026-09-18 经本人确认已改为"示意图一律优先 flowchart TD、慎用 sequenceDiagram；确需时序图信号文字需自备不透明底盒"（配图 extra5-claudemd.png 为修订前实拍，留作 before 示意）；③ memory——教程规划已记 v11 教训；④ Skill——`SKILL.md` 新增"重型运行时别赌固定 settle、改图先本地 file:// 预检、flowchart 优先"两段纪律。配图 8 张：1 张当晚 A/B 实测对比、1 张文内原生 flowchart、4 张纯本地 conhost（CLAUDE.md / memory 目录与索引 / SKILL.md frontmatter / 技能目录含 ui-shot.ps1 SAFETY 头）、2 张官方文档暗色实拍；全程零借窗。拍摄新增一条工具经验：Windows Terminal 会劫持 `Start-Process powershell` 的新窗成标签页，显式 `conhost.exe powershell.exe …` 才起独立经典控制台；Win11 经典控制台抓图要用 DWM 扩展框（`DwmGetWindowAttribute` attr 9）取物理几何，比 GetWindowRect 大约 1 倍 DPI 边框量。

## 参考资料汇总

- Gmeek 源码：<https://github.com/Meekdai/Gmeek>
- 官方进阶插件教程：<https://blog.meekdai.com/post/%E3%80%90Gmeek-jin-jie-%E3%80%91-cha-jian-gong-neng-de-shi-yong.html>
- 官方快速上手：<https://blog.meekdai.com/post/Gmeek-kuai-su-shang-shou.html>
- Primer CSS（GitHub 同源设计系统）：<https://primer.style/css>
- utterances 评论系统：<https://utteranc.es/>
- tocbot 目录库：<https://tscanlin.github.io/tocbot/>
- Vercount 计数服务：<https://vercount.one/>
- 插件分享基地（issue #167）：<https://github.com/Meekdai/Gmeek/issues/167>

## 小结

调研结论可以浓缩成三句话：

1. **配置层的红利还没吃完**——About 页、版权声明、运行天数、favicon、分享封面全是一行配置的事，这是接下来 G01–G03 的内容；
2. **SEO 几乎零成本**——RSS 直接当 sitemap 提交，robots/404 放静态目录即可；
3. **真正有含金量的是自研三小件**（上下篇、阅读时长、归档页），它们会逼出"如何写一个 Gmeek 插件"的完整方法论，那才是这个系列从"会用"走向"会造"的分水岭。

G01–G16 正篇与 **[G17 SEO 收尾战](/post/27.html)**（canonical + JSON-LD + twitter:card + 清洁 description，前传 #4 清单清零）均已完成；方法论番外已有五篇：**[番外·给博客拍证件照](/post/26.html)**（零依赖 CDP 无头截图，成品脚本 `tools/cdp-shot.js`）、**[番外二·开源回馈流水线](/post/28.html)**（三个上游 PR 待合并，见上方 2026-09-16 小节）、**[番外三·gdigrab 抓窗口](/post/31.html)**（浏览器外截图，成品脚本 `tools/shot-window.ps1`）、**[番外四·点到为止](/post/33.html)**（借用户已登录浏览器窗口拍登录态页面，Win32 UI 自动化 + 安全边界，成品脚本 `tools/ui-shot.ps1`；截图三部曲——浏览器内 CDP／浏览器外 gdigrab／登录态借窗——至此收束）与 **[番外五·踩坑手册怎样变成 AI 技能](/post/37.html)**（博客/CLAUDE.md/memory/Skill 四层归宿，见上方 2026-09-18 小节）。2026-09-16 另发布 **[G18 被浮动挤扁的"上一篇/下一篇"](/post/29.html)**：G08 导航卡片在移动端被版权小字的 `float:right` + BFC 避让规则压成 60% 窄列、标题竖排；`clear:both` 拿回全宽、小屏去浮动、meta 行合并，移动/桌面同取景前后对比验收。零起点读者另走**地基篇（B 系列）**：[B00 地基篇总览](/post/30.html)以及 [B01 18 秒建站实录](/post/32.html)、[B02 毛坯房装修：认识 config.json](/post/34.html)、[B03 在 Issues 里过日子](/post/35.html)、[B04 门铃与名片：评论区与 About 页](/post/36.html) 均已发布；地基篇的路线图表与发布日志统一维护在 B00 一篇里（本文不再搬运），下一篇动手向为 **B05 Actions 篇**（回收 B04"评论数为何不实时"的伏笔）。G 系列方向下一篇待写仍是约 2026-09-21 的 **G04 收录实战番外**——用 Google/Bing 的真实收录数据回答"RSS 当 sitemap 提交到底有没有用"，届时一并验收 G17 富结果与清洁摘要的真实生效情况、追踪上游 PR 进展。更远的候选见上方选题池。



















