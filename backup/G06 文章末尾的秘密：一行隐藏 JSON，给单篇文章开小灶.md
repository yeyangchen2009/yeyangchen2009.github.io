> 前面几期装修的都是"全屋"：TOC、灯箱、favicon、页脚……写在 `config.json` 里的东西对所有页面一视同仁。可总有那么几篇文章想搞特殊：一篇多图教程想单独加载个插件、一篇旧文补发想把日期改回当年、一篇镇站之宝想配专属分享封面。Gmeek 的答案藏在一个很不正经的地方——**文章正文的最后一行，一条 HTML 注释**。这一期 G06 把它拆开讲，而且你正在读的这篇文章，本身就是实验品。

## 先看现场

不用翻后台，三个证据此刻就在这一页上：

1. **看本文的每个二级标题**——左边是不是多了一条绿色竖线？全站其他文章没有；
2. **拉到本文最底部**——有一个绿色虚线框的小徽章，全站也只有这篇有；
3. 按 **F12** 打开浏览器控制台，能看到一行绿色的彩蛋日志。

这三样东西不在 `config.json` 里，不在任何插件文件里，它们的全部"源代码"就是本文末尾那一行注释：

```html
<!-- ##{"style":"...","script":"..."}## -->
```

页面加载时，Gmeek 在构建阶段把这行注释解析掉，里面的 CSS 和 JS 就只注入到了这一篇文章。读者看正文时它是不可见的注释，编译器眼里它是一份配置文件——一石二鸟。

## 源码：它是怎么被抠出来的

核心逻辑在 [Gmeek.py 第 357 行附近](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L357)，五行看懂：

```python
try:
    postConfig = json.loads(issue.body.split("\r\n")[-1:][0].split("##")[1])
    print("Has Custom JSON parameters")
except:
    postConfig = {}
```

拆解这一行链式调用：

1. `issue.body` 是整篇 issue 正文；
2. `.split("\r\n")[-1:][0]`——按换行切开，**只取最后一行**；
3. `.split("##")[1]`——最后一行再按 `##` 切成三段，取中间那段。注释长这样：

   ```
   <!-- ##{...JSON...}## -->
        ↑第一段  ↑JSON(第二段)  ↑第三段
   ```

4. `json.loads()` 解析；任何一步失败（没有注释、JSON 写错）都静默回退到空字典——文章照常发布，只是定制不生效，**不会报错给你看**。这是它最坑的地方：写错了没有任何红叉提示。

紧接着是五个字段的分发（[363–386 行](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L363-L386)）：

```python
if "timestamp" in postConfig:
    post["createdAt"] = postConfig["timestamp]          # 覆盖
if "style" in postConfig:
    post["style"] = self.blogBase["style"] + postConfig["style"]   # 追加
if "script" in postConfig:
    post["script"] = self.blogBase["script"] + postConfig["script"] # 追加
if "head" in postConfig:
    post["head"] = self.blogBase["head"] + postConfig["head"]       # 追加
if "ogImage" in postConfig:
    post["ogImage"] = postConfig["ogImage"]             # 覆盖
```

字段清单：

| 字段 | 策略 | 典型用途 |
|---|---|---|
| `style` | 追加在全局样式**之后** | 单篇排版微调、标题装饰（本文的绿竖条） |
| `script` | 追加在全局脚本之后 | 单篇才需要的交互/插件（本文的徽章和彩蛋） |
| `head` | 追加进 `<head>` | 单篇额外的 meta、第三方库 CSS |
| `ogImage` | **覆盖**全站封面 | 重点文章的专属分享大图（G03 留的钩子） |
| `timestamp` | **覆盖**发布时间 | 补发旧文、修正日期 |

模板侧的注入点也对得上：[post.html](https://github.com/Meekdai/Gmeek/blob/main/templates/post.html) 里 `style` 输出在主样式表之后（所以单篇 CSS 天然拥有更高优先级），`script` 在页尾脚本块，`ogImage` 直接喂给 `<meta property="og:image">`。

## 本文的配方

贴上本文最后一行的真身（换行是为了方便阅读，**实际必须压成一行**）：

```html
<!-- ##{"style":"<style>.markdown-body h2{border-left:4px solid #2da44e;padding-left:.6em}</style>","script":"<script>console.log('%c G06 隐藏 JSON 已生效 ','color:#2da44e');document.getElementById('content').appendChild(Object.assign(document.createElement('div'),{textContent:'🪄 本篇样式由正文最后一行的隐藏 JSON 注入',style:'margin-top:2.5em;padding:.8em 1em;border:1px dashed #2da44e;border-radius:10px;color:#2da44e'}));</script>"}## -->
```

两个写作要点：

- JSON 的**键和值都必须用双引号**，值内部的 JavaScript 全部改用单引号，否则引号大战会逼疯你；
- 值里的 `<style>`、`<script>` 标签要写全——这两个字段最终是拼进 HTML 的字符串，不是裸 CSS/JS。

## 六个必须知道的坑

**1）必须是正文最后一行，后面连一个空行都不能有。** 解析器是机械地取最后一行，你在注释后面随手敲个回车，最后一行就变成空字符串，JSON 解析失败，静默失效。

**2）值里不能出现连续的 `##`。** 因为解析器自己就是拿 `##` 当分隔符。JS 里写锚点 `a.href='x##y'` 这种代码会把整行切崩。要写请用 `'#'+'#'` 拼。

**3）它是"追加"，不是"替换"。** 单篇 `script` 会接在全局 TOC、lightbox 之后执行——你没法用它**关掉**某篇的灯箱，只能叠加东西或用 CSS 覆盖样式。想反其道而行之（只给一篇装插件）反而正是它的主场：全局不配，单篇给。

**4）`timestamp` 是秒级 Unix 时间戳，且牵一发动全身。** 它改的是文章的 `createdAt`，连带影响：首页排序、RSS 里的发布时间、文章日期标签的颜色（源码里日期颜色按年份取模选色）、以及 G04 那个自动 sitemap 的 lastmod。在 `urlMode:"issue"` 下文章 URL 是编号不受影响，但如果用的是路径模式，URL 也会跟着变。补发一篇 2020 年的旧文，就填 `1577836800`（2020-01-01 00:00 UTC）。

**5）换行符的学问：放心用，但要懂原理。** 源码按 `\r\n`（Windows 换行）切分，看着吓人——本地写稿都是 `\n`（Unix 换行）怎么办？叶扬翻过 Action 构建出来的 backup 原文，**所有文章无一例外都是 CRLF**：无论你在网页编辑还是用 gh API 发文，GitHub 存进 issue 的正文都会被规范化成 CRLF。所以这条只在"本地拿源码调试解析逻辑"时才需要注意。

**6）改完要触发一次构建。** 给已发布文章补这行注释，本质是编辑 issue，会触发增量构建重新解析正文，不用全局重建。

## 怎么确认它真的生效了

这是 Gmeek 少有的"沉默功能"，好在源码留了一扇窗：构建日志里，解析成功会打印一行——

```
Has Custom JSON parameters
{'style': '...', 'script': '...'}
```

发布后去 Actions 点开本次构建日志搜 "Custom JSON"，能看到解析出的字典，就是成了；什么都没有，就是最后一行没写对。线上再 F12 核对元素，双保险。

## 三个实战用法

**① 镇站之宝配专属封面。** 给某篇单独指定分享大图（规矩和 G03 一样：PNG/JPG、绝对 URL）：

```html
<!-- ##{"ogImage":"https://yeyangchen2009.github.io/images/g01-cover.png"}## -->
```

顺嘴一提：[Gmeek.py 第 494 行](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L494)会在写 postList.json 前把每篇的 ogImage 字段删掉——列表数据用不上它，不删白白撑大 JSON。框架的体贴都在这种小地方。

**② 单篇加载重型库。** 比如只有一篇文章用到图表库，就只给那篇的 `head` 加 CDN 样式、`script` 加库代码，不让其他读者替它还债。

**③ 旧文搬家。** 从其他博客平台导入文章时，用 `timestamp` 保留原始发布日期，时间线不会因为搬家全挤到今天。

## 小结

一行注释，五个字段，换来了全局配置之外的"单篇自治权"：样式能定制、脚本能私加、封面能专属、时间能回退。它的设计哲学和 Gmeek 一脉相承——不建数据库、不开后台，所有配置都寄生在已有的内容载体里（全局靠 config.json，单篇靠 issue 正文）。代价是静默失败，所以"最后一行 + 看日志"这八个字值回全文。

下一期 G07 回到写作本身：GitHub 风格的 Alert 提示块、数学公式、Mermaid 图表在 Gmeek 里的正确写法和各自的加载策略。

## 参考

- 隐藏 JSON 解析与字段分发：<https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L357-L386>
- 文章模板注入点：<https://github.com/Meekdai/Gmeek/blob/main/templates/post.html>
- 官方配置说明（进阶用法）：<https://github.com/Meekdai/Gmeek#readme>
- 系列总揽：[Gmeek 插件与功能全景调研（第 0 篇）](/post/5.html)
<!-- ##{"style":"<style>.markdown-body h2{border-left:4px solid #2da44e;padding-left:.6em}</style>","script":"<script>console.log('%c🪤 G06 隐藏 JSON 已生效','color:#2da44e;font-size:16px;font-weight:bold');(function(){var b=document.createElement('div');b.textContent='🪤 这篇文章的二级标题绿竖条、这行小字、以及控制台彩蛋，全部来自正文最后一行的隐藏 JSON';b.style.cssText='margin-top:2.5em;padding:.8em 1em;border:1px dashed #2da44e;border-radius:10px;color:#2da44e;font-size:.92em';document.getElementById('content').appendChild(b);})();</script>"}## -->