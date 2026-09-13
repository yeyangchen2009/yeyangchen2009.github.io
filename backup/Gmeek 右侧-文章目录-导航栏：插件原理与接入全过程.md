# Gmeek 右侧"文章目录"导航栏：插件原理与接入全过程

> 长文没有目录，读者只能靠滚动条判断自己读到了哪。Gmeek 官方文档页右侧挂着一个随滚随用的"文章目录"，本文拆解它的实现原理，并记录把它接入自己博客的完整过程——看完这篇文章时，你可以直接在右侧观察它的实际效果。

## 为什么长文需要一个目录

上一篇 [《用 GitHub Issues 写博客》](/post/1.html) 讲完整个搭建过程后，叶扬回头查资料时先遇到的问题就是：文章一长，想跳到某个小节只能 Ctrl+F。成熟博客一般都会在正文旁侧放一个 **TOC（Table of Contents，文章目录）**，作用有三个：

1. **导航**：点击标题直接跳转到对应章节；
2. **定位**：滚动时知道自己处在文章的什么位置；
3. **预览**：点开文章先扫一遍目录，就知道这篇值不值得读完。

Gmeek 官方文档站（blog.meekdai.com）的文章页右侧就有一个，叶扬打开开发者工具扒了一遍，发现它正是 Gmeek 源码仓库 `plugins/` 目录里自带的插件——`GmeekTOC.js`。整个插件只有 100 行原生 JavaScript，零依赖。

## 两个候选插件

官方仓库的 [plugins 目录](https://github.com/Meekdai/Gmeek/tree/main/plugins) 里其实有两个目录插件：

| 插件 | 实现方式 | 依赖 | 特点 |
|---|---|---|---|
| **GmeekTOC.js** | 纯手写原生 JS | 无 | 官方文档站自己在用；目录 + 回顶按钮 |
| **GmeekTocBot.js** | 封装开源库 [tocbot](https://tscanlin.github.io/tocbot/) | cdnjs CDN 上的 tocbot | 滚动时**高亮当前章节**，层级缩进更美观 |

两者定位完全相同：把一个固定的目录盒子挂在正文右侧，窄屏时自动收起到文章顶部。区别只在体验细节：

- 想要"零依赖、不挂任何第三方 CDN"——选 `GmeekTOC.js`，断网或者 CDN 被墙都不影响；
- 想要"滚动跟随高亮当前标题"——选 `GmeekTocBot.js`，代价是多加载一个第三方 JS/CSS。

叶扬选择前者。这个博客所有静态资源都坚持放在自己仓库里（连 Mermaid 都是本地化的），不把可用性押在第三方 CDN 上。

## 实现原理：100 行代码做了什么

读完源码，它一共干了四件事。

### 一、扫描标题，生成目录树

页面 `DOMContentLoaded` 之后，插件找到 `id="content"` 的正文容器，扫描里面所有的 `h1` 到 `h6`：

```javascript
const headings = contentContainer.querySelectorAll('h1, h2, h3, h4, h5, h6');
if (headings.length === 0) {
    return;  // 没有标题就不生成目录
}
```

对每个标题，如果 GitHub 渲染时没给它自动生成锚点 id，就用标题文字自己造一个（空白替换成连字符），然后创建一个指向该锚点的 `<a>` 加进目录盒子。层级缩进靠的是标题级别——`h1` 不缩进，每深一级多缩进 10px：

```javascript
link.style.paddingLeft = `${(parseInt(heading.tagName.charAt(1)) - 1) * 10}px`;
```

最后在盒子尾部追加一个 "Top" 链接，点击平滑滚动回页面顶部。

### 二、用 fixed 定位把目录"钉"在正文右侧

目录盒子的定位是整个插件最巧妙的一段 CSS。正文容器在页面中居中，目录要贴在它右边，于是先移动到页面中线，再向右平移半个正文宽度多一点：

```css
.toc {
    position: fixed;
    top: 130px;
    left: 50%;
    transform: translateX(50%) translateX(320px);
    width: 200px;
    max-height: 70vh;
    overflow-y: auto;
}
```

`position: fixed` 让它不随页面滚动；`max-height: 70vh` 加上 `overflow-y: auto`，标题再多也只会在盒子内部滚动，不会撑爆屏幕。

### 三、响应式：窄屏自动收为正文内块

宽屏挂右侧，手机上右边没有空间怎么办？一行媒体查询解决——屏幕宽度小于 1249px 时，目录从固定定位变回普通文档流，显示在文章开头：

```css
@media (max-width: 1249px) {
    .toc {
        position: static;
        transform: none;
        margin-bottom: 20px;
    }
}
```

### 四、暗色模式零成本适配

插件没有写死任何颜色，全部引用 GitHub Primer 设计系统的 CSS 变量，比如：

```css
.toc a:hover {
    background-color: var(--color-select-menu-tap-focus-bg);
}
```

Gmeek 的明暗主题切换本质上就是切换这套变量，所以目录的配色自动跟着站点主题走，插件自己一行暗色适配都不用写。

另外那个 "Top" 按钮默认隐藏，监听滚动事件：页面向下滚动超过 20px 时才显示，回到顶部附近又自动隐藏。

## 接入全过程：三步

原理清楚后，接入反而非常简单。

### 第一步：把插件放进 static/ 目录

在博客仓库根目录建立 `static/plugins/` 文件夹，把官方的 `GmeekTOC.js` 放进去：

```text
static/
├── GmeekVercount.js
├── mermaid.min.js
├── mermaid-init.js
└── plugins/
    └── GmeekTOC.js
```

为什么必须是 `static/` 目录？Gmeek 的构建脚本 `Gmeek.py` 在每次生成站点时，会把 `static/` 下的所有文件和子目录**原样复制**到发布目录 `docs/`：

```python
if os.path.isdir(src):
    shutil.copytree(src, dst)   # static/plugins -> docs/plugins
```

所以本地的 `static/plugins/GmeekTOC.js`，发布后对应的 URL 就是 `https://用户名.github.io/plugins/GmeekTOC.js`。

### 第二步：在 config.json 里注入 script

Gmeek 没有专门的 "plugin" 配置项，插件统一通过往页面注入 `<script>` 标签生效。打开仓库根目录的 `config.json`，在已有的 `allHead` 旁边增加一个 `script` 字段：

```json
{
    "allHead": "<script src='/GmeekVercount.js'></script>",
    "script": "<script src='/plugins/GmeekTOC.js'></script>"
}
```

注意这里有一个**必须避开的坑**：不要图省事把 TOC 插件塞进 `allHead`。两个字段的注入范围完全不同：

| 配置字段 | 注入位置 | 加载页面 |
|---|---|---|
| `allHead` | 每个页面的 `<head>` | 全站（首页、标签页、文章页） |
| `script` | 文章页模板底部 | **仅文章页** |
| `indexScript` | 列表页模板 | 仅首页等列表页 |

访问统计需要在每个页面待命，所以 `GmeekVercount.js` 放在 `allHead`；而 `GmeekTOC.js` 启动第一行代码就是：

```javascript
var contentContainer = document.getElementById('content');
const headings = contentContainer.querySelectorAll('h1, h2, h3, h4, h5, h6');
```

首页和标签页根本不存在 `id="content"` 的元素，`contentContainer` 为 `null`，再调用 `.querySelectorAll` 直接抛 TypeError，控制台一片红。这也是官方文档站把它放在文章页底部、而不是 `<head>` 里的原因。

### 第三步：手动全局重建

修改 `config.json` 不会自动触发构建（平时新建 Issue 才会）。需要到 GitHub 仓库手动跑一次工作流：

**Actions → build Gmeek → Run workflow → 选择 main 分支**。

用 [GitHub CLI](https://cli.github.com/) 则只需一行命令，不用点开网页：

```bash
gh workflow run "build Gmeek"
gh run list --limit 3          # 查看构建状态
```

约一分钟后构建完成，打开任意一篇含多个小标题的文章，右侧即可看到目录。

## 验证清单

接入后可以按这几项检查：

- [x] 宽屏（>1249px）下目录固定在正文右侧，滚动页面时位置不动；
- [x] 点击任意标题平滑滚动到对应章节；
- [x] 向下滚动后 "Top" 按钮出现，点击回到页顶；
- [x] 浏览器窗口拖窄或用手机访问，目录变为文章顶部的普通块；
- [x] 切换暗色主题，目录配色自动跟随；
- [x] 打开首页和标签页，控制台没有 `Cannot read properties of null` 报错。

## 小结

这个插件值得拆开看一遍，因为它体现了 Gmeek 生态里"插件"的标准形态：**一个自包含的 JS 文件，放 `static/` 目录，用 `script`/`allHead` 字段注入，自己注入所需 CSS，不改动上游模板**。这种方式的好处是 Gmeek 本身升级时，你的自定义功能不受影响——删掉那一行配置就能完整回退。

下一篇准备系统盘点一下：一个博客除了评论和互动，还需要哪些基础功能，以及叶扬给这个博客定下的建设路线图。
