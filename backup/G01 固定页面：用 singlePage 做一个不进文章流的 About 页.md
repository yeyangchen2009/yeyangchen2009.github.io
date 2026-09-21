> 普通 Issue 一发布就会进入首页时间流和 RSS，但"关于页""友链页"这类内容不应该是一篇会被新文章冲走的日志。Gmeek 内置了 `singlePage` 机制专门解决这个问题。本文是系列第一篇实操教程：叶扬会把自己的 About 页从配置到上线完整走一遍，包括途中真实踩到的一个坑。效果先放这里：<https://yeyangchen2009.github.io/about.html>

## 固定页与普通文章差在哪

| | 普通文章 | singlePage 固定页 |
|---|---|---|
| URL | `/post/6.html`（issue 编号） | `/about.html`（**标签名**，短链接） |
| 首页文章列表 | 出现 | **不出现** |
| RSS 订阅源 | 收录 | 不收录 |
| 页头入口 | 无 | 自动多一个图标按钮，全站可见 |
| 排序 | 按时间参与列表排序 | 独立存在，与时间无关 |

自我介绍、友情链接、作品集这类"常驻信息"，要的就是后一列的行为。

## 实操：三步上线

### 第一步：config.json 开启 singlePage

在仓库根目录的 `config.json` 里增加一个数组：

```json
"singlePage": ["about"]
```

数组里填的是**标签名**。也就是说，"哪些标签的 Issue 生成固定页"完全由这个数组决定。以后想加友情链接页，就写成 `["about", "link"]`。

### 第二步：确保 about 标签存在

`singlePage` 里写的标签必须在仓库的 Label 列表中真实存在，否则建 Issue 时会直接报错 `could not add label: 'about' not found`。用 [GitHub CLI](https://cli.github.com/) 一行创建：

```bash
gh label create "about" --color "6e40c9" --description "固定页面标签，不进文章列表"
```

### 第三步：发一篇只打 about 标签的 Issue

- **标题**：建议中文，如"关于叶扬"。它会同时成为页面大标题和页头按钮的 hover 提示；
- **正文**：正常写 Markdown；
- **标签**：只打 `about` 这一个（原因见下节"两个必须知道的规则"）；
- 提交后等待 Actions 构建，访问 `https://用户名.github.io/about.html`。

页头导航栏会自动多出一个人形图标（GitHub Octicon 的 person 图标），无需任何前端代码。

## 踩坑实录：第一次上线，它变成了普通文章

叶扬第一次操作时，配置和标签都正确，构建也显示 success，但结果是：

- `about.html` 返回 404；
- 文章反而被生成成了 `/post/6.html`；
- 首页列表里混进了"关于叶扬"；
- 页头没有图标按钮。

**根因：修改 `config.json` 后，Issue 事件触发的是增量构建，它不会重新加载配置结构。**

Gmeek 的工作流在收到 Issue 的 opened/edited 事件时，会带上 `--issue_number` 参数只处理这一篇。此时站点全局状态 `blogBase.json` 是直接读取仓库里的旧缓存——`singlePage` 这个新字段还不在里面，于是新 Issue 被按普通文章处理。

解决办法是官方 README 里写过、但很容易跳过的那一步：**手动跑一次全局重建**。

```bash
gh workflow run "build Gmeek"
```

全局重建不带 `--issue_number`，会清空 `docs/` 与 `backup/`，重新拉取全部 Issues 并按最新配置逐篇判定。重建完成后，错误生成的 `/post/6.html` 被清除，`about.html` 正确生成。

> **结论：凡是修改 `config.json`（新增 singlePage、改注入字段、换主题等），都要手动全局重建一次。** 日常新建/编辑文章则不用。

## 原理：源码里发生了什么

知其所以然，以后出问题不用猜。关键逻辑都在 [Gmeek.py](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py) 里。

### 1. 用第一个标签决定身份

构建器给每篇 Issue 分类时，判断的是**标签数组的第一个元素**（[Gmeek.py:316](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L316)）：

```python
if issue.labels[0].name in self.blogBase["singlePage"]:
    listJsonName='singeListJson'
    htmlFile='{}.html'.format(self.createFileName(issue,useLabel=True))
else:
    listJsonName='postListJson'
    htmlFile='{}.html'.format(self.createFileName(issue))
```

- 命中：存入 `singeListJson`（源码里就是这个拼写，少了个 l），文件名取标签名 → `about.html`，放在站点根目录；
- 未命中：存入 `postListJson`，按 `urlMode` 命名进 `post/` 目录。

### 2. 页头按钮由数据自动渲染

列表页模板 [plist.html](https://github.com/Meekdai/Gmeek/blob/main/templates/plist.html) 会遍历 `singeListJson`，为每个固定页渲染一个圆形按钮，链接指向 `/标签名.html`，hover 标题取 Issue 标题。

按钮的 SVG 图标按**标签名**查字典，字典在 [Gmeek.py:25](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L25) 的 `IconBase` 中，内置了两个固定页图标：`about`（人形）和 `link`（链条）。图标表与用户自定义 `iconList` 的合并逻辑在 [Gmeek.py:216](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L216)，用户配置覆盖内置值。

这也解释了官方文档为什么说"about 和 link 可以不用设置图标"——开箱即用。

### 3. 固定页不加载全局页脚文字

文章页模板里，如果该页是 singlePage，会把 `bottomText` 清空（[Gmeek.py:197](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L197)）。固定页通常是独立排版的页面，不套"转载请注明出处"这类全局尾巴，框架连这个细节都考虑到了。

## 两个必须知道的规则

1. **`about` 必须是第一个标签。** 判断条件是 `labels[0]`，而 GitHub API 返回的标签顺序未必等于你勾选的顺序。所以最稳妥的做法就是只打 `about` 一个标签；确实要多标签时，先在网页上取消再重勾，把它排到第一位。
2. **标签名直接成为文件名，优先用英文。** 标签叫 `about`，URL 才是干净的 `/about.html`；叫"关于"就会生成 `/关于.html`，中文 URL 会被百分号编码，不利于分享和收录。

## 常见扩展

| 需求 | 做法 |
|---|---|
| 友情链接页 | `singlePage` 加 `"link"`，建一篇只打 `link` 标签的 Issue，自动得到 `/link.html` 和链条图标 |
| 自定义名称的固定页（如 `projects`） | 数组里加 `"projects"`，同时必须在 `iconList` 里提供 16px 的 SVG path（`"projects": "M...."`），否则按钮图标是空的 |
| 外部链接按钮（个人音乐站、GitHub 之外的主页） | 那不是 singlePage，用 `exlink` 配置，并在 `iconList` 配同名图标。作者博客的音乐站就是[这么配的](https://github.com/Meekdai/meekdai.github.io/blob/main/config.json) |
| 固定页需要单独插件/样式 | 和普通文章一样，在正文最后一行写[文章级 JSON](/post/5.html)（G06 会细讲） |

## 验证清单

上线后按这几项核对：

- [x] `https://用户名.github.io/about.html` 直接可访问；
- [x] 页头出现人形图标按钮，hover 显示 Issue 标题；
- [x] 首页文章列表与 RSS 中都不出现该页；
- [x] 站点下不存在误入的 `/post/编号.html`；
- [x] 改过 `config.json` 后已经跑过一次手动全局重建。

## 小结

`singlePage` 体现了 Gmeek 的典型设计哲学：**不新增页面类型，只给"标签"赋予语义**。一个数组声明哪些标签特殊，构建器分流渲染，模板自动生成入口——没有数据库、没有路由配置，全部数据仍然只是 Issue 和 Label。

下一篇 G02，叶扬会继续用"改一行配置"的方式装修页脚：`bottomText` 版权声明和 `startSite` 运行天数。

## 参考

- 官方进阶文档《[【Gmeek 进阶】插件功能的使用](https://blog.meekdai.com/post/%E3%80%90Gmeek-jin-jie-%E3%80%91-cha-jian-gong-neng-de-shi-yong.html)》
- 构建器源码：<https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py>
- 作者本人配置样本：<https://github.com/Meekdai/meekdai.github.io/blob/main/config.json>
- 系列总揽：[Gmeek 插件与功能全景调研（第 0 篇）](/post/5.html)
