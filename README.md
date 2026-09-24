# 叶扬的博客 :link: https://yeyangchen2009.github.io 
### :page_facing_up: [66](https://yeyangchen2009.github.io/tag.html) 
### :speech_balloon: 0 
### :hibiscus: 593015 
### :alarm_clock: 2026-09-25 07:22:57 
### Powered by :heart: [Gmeek](https://github.com/Meekdai/Gmeek)


<!-- BEGIN CUSTOM README -->
## 📖 关于本站

叶扬的个人博客，全程由 [Gmeek](https://github.com/Meekdai/Gmeek) 驱动：**在 GitHub Issues 里写文章，Actions 自动生成静态页面，GitHub Pages 部署上线**。零服务器、零数据库，Issue 一提交，几分钟后就是一篇新博客。

👉 在线阅读：<https://yeyangchen2009.github.io>

## 🗺️ 阅读顺序

站内有一套从零搭建本站的实战系列，路线图（全部篇目与进度）维护在 Issue [#5](https://github.com/yeyangchen2009/yeyangchen2009.github.io/issues/5)，也可以从[标签页](https://yeyangchen2009.github.io/tag.html)按主题浏览。

## 🗂️ 仓库结构

| 路径 | 说明 |
| --- | --- |
| `config.json` | 站点配置：标题、副标题、固定页、插件脚本注入顺序（`script`/`allHead`/`indexScript`）等 |
| `.github/workflows/Gmeek.yml` | 构建工作流：Issue 新建/编辑 → 增量构建；手动触发或每日定时 → 全局构建 |
| `static/plugins/` | 文章页插件。既有 Gmeek 官方插件，也有本站自研的 `GmeekSEO.js`（canonical、清洁摘要、Twitter Card、BlogPosting 结构化数据）、`GmeekMermaid.js`（Mermaid 暗色图表按需加载）、`GmeekArchive.js`（归档时间线）等 |
| `static/` | 静态资源：Mermaid 与 TocBot 库文件、`og.png`/`favicon.svg`、`robots.txt`、教程截图素材 `screenshots/` 等 |
| `tools/cdp-shot.js` | 零依赖无头浏览器截图器（Node ≥ 22，内置 WebSocket 直连 Chrome DevTools Protocol），配套[番外篇 /post/26.html](https://yeyangchen2009.github.io/post/26.html)；同目录附 `primer-21.0.7.css` 供离线应答复现 |
| `tools/build-readme.py` | 把本文件（`README.custom.md`）幂等拼接到自动生成的统计区下方 |
| `sitemap_gen.py` | 构建流程末尾自动生成 `sitemap.xml` |
| `backup/`、`blogBase.json` | Gmeek 每次构建自动更新的文章元数据与备份 |
| `docs/` | 构建产物，GitHub Pages 部署目录，请勿手改 |

## ✍️ 怎么发文章

1. 在本仓库新建 Issue，打上 `博客,Gmeek` 等标签，正文直接写 Markdown；
2. 保存即触发 Actions 增量构建，自动生成 `/post/<Issue 编号>.html` 并提交；
3. 编辑 Issue 会重新构建对应文章；**改动 `config.json` 后需手动 Run workflow 做一次全局重建**，静态资源变更同理。

## 🤝 给上游的回馈

使用过程中向 Gmeek 反馈过若干 Issue 与补丁，例如增量构建在文章无标签时会触发的 KeyError 修复：[Meekdai/Gmeek#319](https://github.com/Meekdai/Gmeek/pull/319)。

---

> ☝️ 最上方的文章数 / 评论数 / 总字数 / 时间戳由 Gmeek 每次构建自动重写，手工修改会被覆盖；以上自定义区块由 `tools/build-readme.py` 在构建时拼接，想改内容请编辑 `README.custom.md`。
<!-- END CUSTOM README -->
