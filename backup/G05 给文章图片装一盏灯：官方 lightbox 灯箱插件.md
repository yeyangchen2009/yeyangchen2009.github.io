# G05 给文章图片装一盏灯：官方 lightbox 灯箱插件

> G04 把博客的门牌号递给了搜索引擎，这期回到读者的阅读体验上。不知你注意过没有：在 Gmeek 文章里点一张图片，浏览器会"哐当"一下跳到一个只有图片的空白页——看完还得点浏览器返回，手机上想放大看清细节，全靠两根手指在屏幕上较劲。这期 G05 装的 lightbox 灯箱插件，就是让图片在**当前页面原地放大**：暗角背景、左右切换、滚轮翻页、键盘 Esc 关闭，全套体验一次补齐。

## 默认行为为什么烦人

这不是浏览器的锅，是 Gmeek 模板里图片默认就是裸链接，点上去等于导航到图片地址。社区在 [issue #151「新增灯箱插件」](https://github.com/Meekdai/Gmeek/issues/151)里提的第一条诉求就是："关闭默认的点击图片后新标签页打开图片事件，改为原网页预览图片"。

作者采纳后合并进官方插件库，随后 [issue #157](https://github.com/Meekdai/Gmeek/issues/157) 又补了一轮升级：超大图完整显示、Ctrl+滚轮缩放、表格内图片显示不全修复、透明背景加高斯模糊以兼容明暗主题。我们现在直接拿到的就是迭代后的成品。

## 代码同步：两步落地

**第一步**，把官方 `plugins/lightbox.js` 下载到仓库的 `static/plugins/` 目录（和 G03 时代接的 GmeekTOC.js 做邻居）：

```
static/
└── plugins/
    ├── GmeekTOC.js
    └── lightbox.js      ← 新增
```

**第二步**，打开 `config.json`，在 `script` 字段里把第二个插件**拼在同一行**：

```json
"script": "<script src='/plugins/GmeekTOC.js'></script><script src='/plugins/lightbox.js'></script>"
```

多插件的拼接写法是在 [issue #152](https://github.com/Meekdai/Gmeek/issues/152)里专门说明过的：一个字段、多个标签、空格或紧挨着都行，**不要另起一个 "script" 键**，JSON 同名键会互相覆盖。

push、深呼吸几秒、手动全局重建（改了 config 的老规矩）。插件零依赖、零配置，源码末尾写着自动初始化：

```javascript
window.Lightbox = Lightbox;
document.addEventListener('DOMContentLoaded', () => {
  new Lightbox();
});
```

不用 new、不用传参，加载即生效。

## 现场验货

下面这两张图都是本站现成的素材（G03 做的社交封面和 favicon）。**点一下任意一张试试**：

![1200×630 的社交分享封面 og.png](/og.png)

![明暗自适应的叶字 favicon.svg](/favicon.svg)

灯箱打开后可以这样玩：

| 操作 | 效果 |
|---|---|
| 点击左/右圆形箭头，或**鼠标滚轮** | 切换上一张/下一张 |
| 键盘 **← →** | 翻页，**Esc** 关闭 |
| **Ctrl + 滚轮** | 放大/缩小（手机上直接双指捏合） |
| 手机**左右滑动** | 触屏翻页 |
| 点击图片外的暗色区域 | 关闭灯箱 |

注意切换时几乎感觉不到加载停顿——插件会**预加载**当前图前后各一张，翻页是现成的。两张图的几何形状差异很大（横版封面 vs 正方形图标），正好能验证它的自适应：每张图都以 `object-fit: contain` 完整落在视口内，绝不出现长图只露半截的尴尬。

## 读源码：它是怎么找到图片的

插件没有扫描全页图片，核心选择器只有一行：

```javascript
this.images = Array.from(document.querySelectorAll('.markdown-body img, table img'));
```

只接管两个区域里的图：Markdown 正文容器（`.markdown-body`）和表格里的图。头像、页脚图标、按钮背景统统不受影响——这也是为什么装完插件后，页面其他该跳链接的地方照常跳。

另一个值得学的设计是**事件委托**：它没有给每张图片逐个绑 click，而是在 `document` 上挂一个捕获阶段的监听：

```javascript
document.addEventListener('click', this.handleImageClick.bind(this), true);
// ...
const clickedImage = event.target.closest('img');
if (clickedImage && !this.isOpen) {
  event.preventDefault();   // 关键：拦掉"跳转到图片地址"的默认行为
```

`preventDefault()` 就是"不再新标签页打开图片"的那一刀。事件委托的好处是：文章里的图是加载时就有的静态内容，哪怕以后用脚本动态插图，新图也自动被接管。

叶扬翻源码时还撞见一个小瑕疵：关闭灯箱时的 `unbindEvents()` 里，每个 `removeEventListener` 都重新 `.bind(this)` 生成了**新函数引用**，而 removeEventListener 要求引用与绑定时完全一致，所以这些解绑其实全部静默失败了。不过它在整个页面生命周期里只 `new Lightbox()` 一次，监听不会累积，外加 `!this.isOpen` 状态守卫，实际使用零影响——属于"代码不完美但 bug 被结构兜住了"的有趣案例。强迫症同学可以给官方提 PR，叶扬选择白嫖。

## 为什么不用 medium-zoom

[issue #74](https://github.com/Meekdai/Gmeek/issues/74) 曾有人推荐 [medium-zoom](https://github.com/francoischalifour/medium-zoom) 库，效果确实优雅，但它是外部依赖。官方后来自研的 lightbox.js 单文件 11KB、零网络请求、不依赖任何 CDN——在国内访问环境下，少一个外部域名就少一次"转圈等加载"，这与 Gmeek 一贯的极简路线一致。插件文件在自己仓库里，版本永远不动，也不存在某天 CDN 跑路的风险。

## 一个边界：script 字段只在文章页生效

顺带复习 Gmeek 配置注入的作用域：`script` 字段只注入文章页底部，所以首页文章列表、标签页都不会加载 lightbox——列表页本来也不展示正文图片，这是精准投放，不是漏了。如果哪天需要全站（包括首页）都加载的脚本，那要走 `allHead` 字段，G04 提过的统计脚本就是待在那里。

## 小结

一个文件、一行配置，换来的是读者看图体验的完整度：原地放大、滚轮翻页、触屏滑动、键盘操作、预加载、明暗主题自适应。成本五分钟，属于"装了就再也回不去"的那类改进。

下一期 G06 聊一个藏在每篇文章最末尾的秘密机关：正文最后一行那串 `<!-- ##{...}## -->` 隐藏 JSON，它能给单篇文章单独定制 script、style、ogImage 和时间戳——G03 留的"每篇文章单独封面"的钩子，到时候展开讲。

## 参考

- 灯箱插件源码：<https://github.com/Meekdai/Gmeek/blob/main/plugins/lightbox.js>
- issue #151 新增灯箱插件（特性与诉求）：<https://github.com/Meekdai/Gmeek/issues/151>
- issue #157 Update lightbox.js（缩放/超大图/主题兼容）：<https://github.com/Meekdai/Gmeek/issues/157>
- issue #152 多个插件同时安装的配置写法：<https://github.com/Meekdai/Gmeek/issues/152>
- issue #74 medium-zoom 方案讨论：<https://github.com/Meekdai/Gmeek/issues/74>
- 系列总揽：[Gmeek 插件与功能全景调研（第 0 篇）](/post/5.html)
