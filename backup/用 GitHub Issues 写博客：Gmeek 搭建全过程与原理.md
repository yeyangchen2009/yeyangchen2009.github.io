# 用 GitHub Issues 写博客：Gmeek 搭建全过程与原理

> 把博客托管在 GitHub 上，写作却不用碰 Git——新建一个 Issue、打个标签，文章自动上线。本文记录叶扬把原有文档站替换成 Gmeek 的完整过程、背后的运行原理，以及踩过的坑。

## 为什么是 GitHub

一个问题：如果你想写一段文字，让 100 年后的人还能访问到，你会写在哪里？

知乎、微博这类平台，100 年后公司还在不在都要打问号；自己买域名加云服务器，每年续费、还要承担被攻击的风险。GitHub 是世界上最大的源代码托管平台，已经是计算机科学的基础设施之一，又背靠微软，长期运行的概率很高。把博客放在这里，免费、无服务器、无域名费用，是一种"让博客长寿"的选择。

当然也要承认它的代价：**国内访问 github.io 不稳定**，这是这个方案最大的现实问题，能接受再往下看。

## 三个免费组件各干什么

Gmeek 不是一个需要安装的博客程序，它是一套"配置文件 + 一个云端构建脚本"，完全运行在 GitHub 提供的免费服务上：

| 组件 | 在博客里的角色 |
|---|---|
| **GitHub Issues** | 写作编辑器。Issue 标题 = 文章标题，正文 = Markdown 正文 |
| **GitHub Actions** | 构建器。监听到 Issue 新建/编辑，自动把 Markdown 渲染成 HTML |
| **GitHub Pages** | 托管。把生成的静态网页发布到 `用户名.github.io` |

三者都是 GitHub 原生功能，零费用，唯一的"成本"是每次构建占用 Actions 的免费额度（公开仓库不计费）。

### 一张图看懂三者的关系

```mermaid
flowchart LR
    U(["你"]) -->|"新建 / 编辑 Issue"| I[("GitHub Issues<br/>写作编辑器")]
    I -->|"opened / edited 事件"| A["GitHub Actions<br/>运行 Gmeek.py"]
    A -->|"渲染产物提交回仓库"| R[("仓库 docs/ 页面<br/>+ backup/ Markdown 原文")]
    A -->|"上传 artifact"| P["GitHub Pages<br/>静态托管"]
    P --> V["读者访问<br/>用户名.github.io"]
```


## 一次发文背后发生了什么

理解这张链路，后面所有操作和排错都不用死记：

```mermaid
sequenceDiagram
    autonumber
    actor 你
    participant I as GitHub Issues
    participant A as GitHub Actions
    participant G as Gmeek.py
    participant R as 仓库
    participant P as GitHub Pages
    你->>I: 新建 Issue 并打上标签
    I->>A: opened 事件触发工作流
    A->>G: 拉取最新源码、安装依赖后运行
    G->>I: 通过 API 读取 Issue 正文
    G->>G: Jinja2 模板把 Markdown 渲染成 HTML
    G->>R: 提交 docs/ 页面与 backup/ 原文
    G->>P: 打包 artifact 并部署
    P-->>你: 约 1 分钟后文章上线
```

大约一分钟，文章就能在 `https://用户名.github.io` 访问。每篇 Issue 对应 `docs/post/` 下一个 HTML 文件，正文同时备份在仓库的 `backup/` 目录——也就是说，**你的文章不依赖 Gmeek 项目本身，Markdown 原件一直在你自己的仓库里**。

每天还会有一次定时构建兜底，也可以在 Actions 页面手动 Run workflow 做全局重建。

## 实操步骤（2026 年当前版本核对过）

### 1. 通过模板创建仓库

在 [Meekdai/Gmeek](https://github.com/Meekdai/Gmeek) 仓库页点"通过模板创建仓库"，仓库名按 GitHub Pages 的规矩填：

```
<你的用户名>.github.io
```

这样才能获得 `https://<你的用户名>.github.io` 这个免费域名；用别的名字，地址会变成 `用户名.github.io/仓库名`。

### 2. 把 Pages 发布源切到 Actions

仓库 `Settings → Pages → Build and deployment → Source`，选择 **GitHub Actions**。

这一步最关键。Pages 有两种发布模式：

- **legacy（从分支发布）**：直接托管某个分支上的现成文件，是传统 docsify/Jekyll 站的模式；
- **workflow（从 Actions 发布）**：部署由工作流产出的 artifact，Gmeek 必须用这种。

选错了模式，Action 显示构建成功但页面不更新，是新手最容易困惑的地方。

两种模式的区别：

```mermaid
flowchart TD
    S["Settings → Pages → Source"] --> B["Deploy from a branch<br/>旧模式"]
    S --> C["GitHub Actions<br/>新模式 ✅"]
    B --> B1["直接托管分支上的现成文件<br/>没有构建步骤"]
    C --> C1["工作流构建 → artifact → deploy-pages"]
    C1 --> C2["Gmeek 必须选这个"]
```

### 3. 配置 config.json

模板仓库里唯一需要改的文件：

```json
{
    "title": "博客标题",
    "subTitle": "博客副标题/一句话描述",
    "avatarUrl": "头像图片地址",
    "email": "用于自动提交的邮箱",
    "GMEEK_VERSION": "last"
}
```

`GMEEK_VERSION` 保持 `"last"` 即每次构建自动使用 Gmeek 最新 release，也可以锁定具体版本号。头像直接填 `https://github.com/用户名.png` 就能用 GitHub 头像。

**改完 config.json 不会自动重新构建**（它不是 Issue 事件），需要去 `Actions → build Gmeek → Run workflow` 手动跑一次全局生成。

### 4. 建一个文章标签

Issues 里写文章，**必须至少打一个 Label**，没有标签的 Issue 不会被生成成页面。叶扬建的标签叫 `Document`。标签还有两个特殊用途：标签的颜色会成为文章的主题色标记；标签名写进 config 的 `singlePage` 数组后，该标签的 Issue 会生成独立单页（比如"关于"页）。

### 5. 写第一篇文章

`Issues → New issue`，标题随意，正文用 Markdown，右侧勾上 `Document`，提交。等 Actions 跑完打勾，刷新博客首页即可看到。

## 一个特殊需求：怎样保住仓库里已有的静态页面

叶扬替换旧站时有个约束：原来的 `lengyanzhou.html`（楞严咒）页面必须保留，链接最好也不变。

读了一遍 Gmeek 的构建脚本，它每次生成前会**清空 `docs/` 目录**，所以把 HTML 直接丢进 docs 是活不过下次构建的。但脚本里有这样一段逻辑：

```python
if os.path.exists(self.static_dir):   # static/
    for item in os.listdir(self.static_dir):
        # 原样复制到 docs/
```

每次构建时 `static/` 的命运：

```mermaid
flowchart TD
    A(["每次构建开始"]) --> B["清空 docs/<br/>旧页面全部删除"]
    B --> C["根据所有 Issue 重新生成页面"]
    C --> D{"static/ 目录存在？"}
    D -->|"是"| E["static/ 内的文件<br/>原样复制进 docs/"]
    D -->|"否"| F["跳过这一步"]
    E --> G["部署 docs/ 到 Pages"]
    F --> G
    H["favicon、计数器脚本、mermaid 库等<br/>自定义静态文件"] -.-> E
```

**仓库根目录的 `static/` 会在每次构建时被原样拷贝到站点根目录。** 于是把 `lengyanzhou.html` 放进 `static/`，它就在每次自动构建后依然出现在 `https://用户名.github.io/lengyanzhou.html`，链接完全不变。要放 favicon、robots.txt、自定义 JS（本文的图表库和浏览量统计脚本就是这样放的），都是同一个位置。

## 日常使用

- **写文**：New issue + Document 标签
- **改文**：直接编辑对应 Issue，保存即触发重新构建
- **删文**：Close 这个 Issue 并重新全局构建（或在备份目录处理后手动 Run workflow）
- **插图**：Issue 编辑器里直接粘贴/拖拽图片，自动上传
- **评论**：内置 utteranc.es，评论本身也是 Issue
- **自定义域名**：Settings → Pages 填域名；子域名只需在 DNS 加一条 CNAME 指向 `用户名.github.io`。若域名托管在 Cloudflare，HTTPS 由它负责，GitHub 这边的 Enforce HTTPS 要取消勾选

什么时候自动、什么时候要手动：

```mermaid
flowchart LR
    A["想更新博客"] --> B{"改了什么？"}
    B -->|"写新文章 / 修改正文"| C["新建或编辑 Issue"] --> E["保存即自动构建"]
    B -->|"改 config.json / static/"| D["Actions 页手动 Run workflow"] --> E
```

## 排错清单

| 现象 | 原因 |
|---|---|
| Actions 成功但页面没变化 | Pages 的 Source 没切成 GitHub Actions |
| Issue 提交后没有触发构建 | 没打标签，或仓库设置里 Actions 权限被限制 |
| 改了 config.json 不生效 | 配置改动不触发构建，手动 Run workflow |
| 文章 404 | 标签名拼写、或构建还在跑（约一分钟） |
| 自己放的 HTML 下次构建消失 | 要放在 `static/`，不能放 `docs/` |

## 小结

这套方案的本质是：**用 GitHub 的 Issue 系统"借用"了一个带 Markdown 编辑器、登录体系和评论系统的后台**，用 Actions 替代服务器定时任务，用 Pages 替代虚拟主机。牺牲的是国内访问速度和一点上手配置，得到的是零成本、无广告、数据完全在自己仓库里的博客。

写作这件事，最重要的永远是开始写。

##{"style":"#postBody>p:last-of-type{display:none;}.mermaid-wrap{margin:18px 0;overflow-x:auto;}","script":"<script src='/mermaid.min.js'></script><script src='/mermaid-init.js'></script>"}