# Gmeek 插件与功能全景调研：系列教程总揽（第 0 篇）

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

### 2. GmeekTOC.js —— 右侧文章目录（已装）

- **功能**：扫描正文 `h1~h6` 生成固定在右侧的目录，按标题级别缩进，窄屏自动收为文章内块，附 Top 回顶按钮。零依赖，100 行。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/GmeekTOC.js)；接入全过程见本站[第 3 篇教程](/post/3.html)。
- **关键坑**：只能走 `script` 字段（仅文章页注入），**不能放 `allHead`**——首页没有 `id="content"` 元素，会抛 TypeError。
- **叶扬的判断**：官方文档站自己在用，配色全走 Primer CSS 变量自动适配暗色，已装。

### 3. lightbox.js —— 图片灯箱（强烈推荐，待装）

- **功能**：文章图片点击放大，支持滚轮缩放、左右键切换上一张/下一张、触屏滑动、相邻图片预加载、毛玻璃遮罩、点遮罩关闭。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/lightbox.js)（357 行，零外部依赖，所有样式与 DOM 都由插件自建）；官方进阶教程收录，由社区用户 **Tiengming** 贡献。
- **叶扬的判断**：官方插件里完成度最高的一个。本站目前文章几乎无图，但只要开始贴图（比如 Gmeek 操作截图教程）立刻需要，列入 G05。

### 4. articletoc.js —— 悬浮按钮式目录（移动端备选）

- **功能**：不在正文里占位置，而是在右下角放一个 ☰ 圆形按钮，点击弹出目录浮层，再点外部关闭；自带亮/暗两套 CSS 变量。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/articletoc.js)，同为 Tiengming 贡献。
- **叶扬的判断**：它与 GmeekTOC 解决同一个问题，**桌面端二选一**。它的价值在手机：GmeekTOC 窄屏时会在文章开头占一整块，而它只占一个按钮。可选方案：桌面保留现有 GmeekTOC，小屏用媒体查询隐藏之、换挂这个——属于体验优化，不急。

### 5. GmeekTocBot.js —— tocbot 版目录（不建议）

- **功能**：封装成熟库 [tocbot](https://tscanlin.github.io/tocbot/)，视觉层级更好，独有**滚动时高亮当前章节**能力。
- **出处**：[插件源码](https://github.com/Meekdai/Gmeek/blob/main/plugins/GmeekTocBot.js)；依赖 `cdnjs.cloudflare.com` 上的 tocbot 4.27.4。
- **叶扬的判断**：功能最强但依赖第三方 CDN，与本站"静态资源全部本地化"的原则冲突。真想要"当前章节高亮"，未来可把 tocbot 的 JS/CSS 下载到 `static/` 再改注入地址，列入远期备选。

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

`bottomText` 一举解决路线图里的「文末版权声明」，列入 **G02**。

### 身份与分享

| 配置项 | 作用 | 备注 |
|---|---|---|
| `faviconUrl` | 浏览器标签页图标；不配置时默认复用 `avatarUrl` | 作者用的是自制 SVG |
| `ogImage` | Open Graph 分享卡片封面；不配置时默认头像 | 文章级还能单独覆盖 |
| `displayTitle` | 页头显示标题，默认与 `title` 一致 | 想让站名短、标题完整时用 |
| `homeUrl` | 站点绝对地址 | **绑定自定义域名后必须配**，否则分页/RSS 链接错乱 |

favicon + ogImage 列入 **G03**。

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

列入 **G06**，是"单篇插件"和"补发旧文"两个场景的关键。

## 四、你可能没意识到的开箱功能

以下能力不用配置、不用插件，写 Markdown 时直接存在：

1. **代码块一键复制**：GitHub 同款 copy/check 图标按钮，[post.html](https://github.com/Meekdai/Gmeek/blob/main/templates/post.html) 内置（对应早期社区 issue #134 的诉求，现已官方解决）。
2. **数学公式按需加载**：正文中用 `<math-renderer>$E=mc^2$</math-renderer>` 包裹公式，框架检测到该标签才注入 MathJax，不写公式的文章零开销（`Gmeek.py:154`）。
3. **GitHub Alert 提示块**：`> [!NOTE]`、`> [!TIP]`、`> [!IMPORT]`、`> [!WARNING]`、`> [!CAUTION]` 自动渲染成 GitHub 官网同款彩色边框块，框架自动补样式（`Gmeek.py:159` 起）。
4. **三态主题与评论联动**：亮 → 暗 → 跟随系统循环；切换时通过 `postMessage` 让 utterances 评论 iframe 同步换肤（[base.html:54](https://github.com/Meekdai/Gmeek/blob/main/templates/base.html)）。
5. **列表分页**：文章数超过 `onePageListNum`，首页自动出现上一页/下一页。
6. **每日定时重建**：工作流除了监听 issue 事件，还有一条 `schedule: cron("0 16 * * *")`，即**北京时间每天 0:00 自动全量重建**一次。Webhook 丢失、改了配置忘记手动构建，第二天都会自愈。注意：Issue 事件只触发**增量构建**，`config.json` 的结构性变更（如新增 singlePage）不会被加载，必须手动跑一次全局重建——G01 实操时踩过这个坑。
7. **Markdown 原文自动备份**：每次构建把 issue 正文存进仓库 `backup/` 目录，`git clone` 即整站离线副本。
8. **RSS 即 sitemap**：见下节，单独说。

写作技巧（Alert、公式、Mermaid 本站已配）单独成篇，列入 **G07**。

## 五、SEO：被问得最多，答案却最简单

社区 issue [#145](https://github.com/Meekdai/Gmeek/issues/145) 里有人建议生成 `sitemap.xml`，作者的回复是：**`rss.xml` 已包含全站所有重要页面链接，他自己就是把 rss.xml 提交给 Google 的**；提问者随后验证，必应和谷歌都能正常识别 RSS 作为站点地图。

因此路线图里的"sitemap.xml"可以划掉，正确做法零代码：

- Google Search Console 添加资源后，站点地图直接填 `https://用户名.github.io/rss.xml`；
- Bing 站长工具同样提交该地址（国内环境下 Bing/必应的收录价值远高于 Google）；
- RSS 之外，`robots.txt` 和自定义 `404.html` 直接放进 `static/` 根目录即可，构建时原样复制到站点根，GitHub Pages 原生识别。

这组操作列入 **G04** 与 **G11**。

## 六、社区生态盘点：有宝贝，也有大坑

Gmeek 没有独立插件市场，[issue #167「插件分享基地」](https://github.com/Meekdai/Gmeek/issues/167)事实上承担了这个角色。翻遍社区代码后：

**值得借鉴的：**

- **数字分页条**：把"上一页/下一页"换成 1/2/3 页码，文章几十篇以后有用。作者在 [issue #186](https://github.com/Meekdai/Gmeek/issues/186) 中确认可由插件实现，社区已有教程：李轶凡《[给博客添加数字分页条](https://blog.liyifan.xyz/post/gei-bo-ke-tian-jia-shu-zi-fen-ye-tiao.html)》。列入 **G13**（文章多了再做）。
- **外链新窗口打开**：同 issue #186 的头号需求，十几行 JS 给正文外链加 `target="_blank" rel="noopener"`，可顺手加 `rel="nofollow"` 的 SEO 讨论（见 issue #145）。列入 **G12**。

**看看就好、不要搬的：**

- 社区用户 luliy6 的 `enhance.js`：约 5884 行的整站换肤方案——开屏动画、全屏 Hero、六张分类卡片、APlayer 音乐播放器、抽屉式菜单。代码本身值得学习"一个 JS 能做到什么程度"，但它与本系列[第 4 篇](/post/4.html)立的三条规矩（静态优先、走插件机制不改模板、为长期写作服务）全部冲突，**明确不借鉴**。
- GitHub 代码搜索能找到的其他"插件"，90% 是把官方 5 个 JS 复制改名，无新东西。

## 七、框架的空白：需要自研的功能

对照[第 4 篇](/post/4.html)的清单，以下功能官方与社区都没有可靠现成方案，需要自己写插件。好在 Gmeek 把数据都放在了 `postList.json`，自研难度不高，这也会是本系列最"硬核"的几篇：

| 功能 | 实现思路 | 编号 |
|---|---|---|
| 文章末尾上一篇/下一篇 | 读取 `postList.json` 按 issue 编号取相邻文章，注入到 `#postBody` 之后 | G08 |
| 字数统计与预计阅读时长 | 统计 `.markdown-body` 文本长度，按中文约 400 字/分钟估算 | G09 |
| 时间线归档页 | 读 `postList.json` 按年份分组渲染；可挂 `singlePage` 机制做成固定页 | G10 |

这三篇会完整演示"如何写一个自己的 Gmeek 插件"，而不只是抄配置。

## 八、系列教程路线图

总揽即 roadmap。每完成一篇，这里会更新链接；状态图例：✅ 已发布 / ⏳ 计划中 / 💤 远期再说。

| 编号 | 教程 | 功能 | 类型 | 状态 |
|---|---|---|---|---|
| 前传 | [搭建全过程与原理](/post/1.html) | 建站 | 教程 | ✅ |
| 前传 | [博客基础功能建设清单](/post/4.html) | 规划 | 清单 | ✅ |
| G00 | 本文 | 全景调研 | 总揽 | ✅ |
| —— | [右侧文章目录插件](/post/3.html) | GmeekTOC | 教程 | ✅ |
| G01 | [固定页面机制：做一个不进文章流的 About 页](/post/7.html) | `singlePage` + `iconList` | 配置 | ✅ |
| G02 | 页脚装修：版权声明与"本站已运行 N 天" | `bottomText` + `startSite` | 配置 | ⏳ |
| G03 | favicon 与社交分享封面 ogImage | `faviconUrl` + `ogImage` | 配置 | ⏳ |
| G04 | 不写 sitemap：把 RSS 提交给 Google 和 Bing | Search Console / 站长工具 | SEO | ⏳ |
| G05 | 图片灯箱：lightbox 插件接入 | 官方插件 | 教程 | ⏳ |
| G06 | 文章末尾的隐藏 JSON：单篇插件、自定义封面、补发旧文 | 文章级配置 | 原理 | ⏳ |
| G07 | 写作增强：GitHub Alert 块、数学公式、Mermaid | 内置语法 | 教程 | ⏳ |
| G08 | 自研插件（一）：文章末尾上一篇/下一篇 | `postList.json` | 自研 | ⏳ |
| G09 | 自研插件（二）：字数统计与阅读时长 | DOM 统计 | 自研 | ⏳ |
| G10 | 自研插件（三）：时间线归档页 | `singlePage` + 数据渲染 | 自研 | ⏳ |
| G11 | robots.txt 与自定义 404 页 | `static/` 直出 | 运维 | ⏳ |
| G12 | 外链自动新窗口打开 | 小插件 | 自研 | 💤 |
| G13 | 数字分页条 | 社区插件 | 借鉴 | 💤 |
| G14 | 移动端目录：articletoc 与响应式策略 | 官方插件 | 体验 | 💤 |
| G15 | tocbot 本地化：当前章节滚动高亮 | CDN 资源本地化 | 进阶 | 💤 |

更新方式：每篇教程发布后，叶扬会回来编辑本文（Gmeek 监听 issue 的 `edited` 事件，编辑即自动重建），所以这张表会一直是最新的。

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

G01 已完成，下一篇 G02，从页脚装修（版权声明与运行天数）继续。
