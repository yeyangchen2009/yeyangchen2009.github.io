> 浏览器的收藏夹里一排灰扑扑的默认图标，聊天框里甩出去的链接光秃秃只有一行字——这都是博客在"社死现场"。这一期 G03，叶扬给博客做了两张脸：标签页上的 favicon，和链接分享时的大封面。一个是纯手写 SVG（还会明暗自适应），一个是用 Python 画出来的 PNG。不借助任何在线设计工具。

## 先看看之前有多凑合

Gmeek 其实早就给了默认值。[Gmeek.py:100](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L100) 写着：不配置 `faviconUrl` 时，favicon 默认就是 `avatarUrl`；不配置 `ogImage` 时，[分享封面也默认头像](https://github.com/Meekdai/Gmeek/blob/main/Gmeek.py#L103)。

也就是说，叶扬之前的博客在任何场景下都顶着同一个 GitHub 头像：标签页、收藏夹、分享卡片……头像是给"人"看的，图标是给"站"看的，混在一起，辨识度约等于校服上别了枚别人的校徽。

这一期要做两件东西：

| 文件 | 出现的地方 | 格式要求 |
|---|---|---|
| `favicon.svg` | 浏览器标签页、书签、历史记录 | SVG 现代浏览器通吃 |
| `og.png` | 链接被分享到微信/QQ/X/Telegram 时的卡片 | **必须 PNG/JPG**，1200×630 |

## favicon：一个"叶"字的自我修养

### 设计思路

个人博客的图标最讨巧的做法就是用名字。"叶扬"的"叶"字简体只有五笔，几何感强——左边一个方框（口），右边一个十字（十），缩小到 16 像素仍然认得出来，简直是被字体设计师开过光的 logo 坯子。

配色直接继承博客的视觉血脉：GitHub 暗底（`#0d1117`）+ Gmeek 控制台绿（`#02d81d`），就是每次构建时那个绿色 logo 的颜色。

### 最终 SVG，全文不到 20 行

放在仓库 `static/favicon.svg`：

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="leafGreen" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#3fb950"/>
      <stop offset="1" stop-color="#02d81d"/>
    </linearGradient>
  </defs>
  <style>
    .bg { fill: #ffffff; }
    .ring { stroke: url(#leafGreen); opacity: .55; }
    @media (prefers-color-scheme: dark) {
      .bg { fill: #0d1117; }
      .ring { opacity: .35; }
    }
  </style>
  <rect class="bg" width="512" height="512" rx="112"/>
  <rect class="ring" x="18" y="18" width="476" height="476" rx="98"
        fill="none" stroke-width="10"/>
  <text x="256" y="266" text-anchor="middle" dominant-baseline="central"
        font-family="'PingFang SC','Hiragino Sans GB','Microsoft YaHei',
                     'Noto Sans CJK SC',sans-serif"
        font-size="300" font-weight="800" fill="url(#leafGreen)">叶</text>
</svg>
```

几个值得说的细节：

1. **SVG favicon 是矢量的**。同一个文件应对 16px 的标签页、32px 的书签栏、甚至拖到手机主屏幕的 180px，永远锐利，文件只有不到 1KB。
2. **它会跟着浏览器换肤色**。SVG 内部可以写 `@media (prefers-color-scheme: dark)`——这是 SVG favicon 相对 `.ico` 的超能力：亮色标签栏时是白底绿字，暗色标签栏时自动变成 GitHub 暗底。叶扬第一次看到标签页上的小方块跟着系统主题变色时，确实愣了一下。
3. **文字没有引入任何外部字体**，而是列了一串系统中文字体回退栈：苹方 → 冬青黑 → 微软雅黑 → Noto → 无衬线。SVG 在访客本地渲染，中文系统必然命中其中之一。代价是极个别没有 CJK 字体的极简 Linux 环境会显示豆腐块——对中文博客来说可以忽略。
4. `y="266"` 而不是 256，是因为中文字面重心普遍偏上，下沉 10 像素视觉上才居中。这种玄学微调，做过 PPT 的人都懂。

> 如果你不想用文字，把 `<text>` 换成任意 `<path>` 图形即可。作者本人用的就是一个[手绘风格的 SVG](https://blog.meekdai.com/favicon.svg)，可以去作者仓库参观。

## ogImage：社交平台不给 SVG 入场券

favicon 可以潇洒地用矢量，分享封面却不行。Open Graph 协议的 `og:image` 在各大社交平台（微信、QQ、X、Telegram、Facebook、Slack）只认 **PNG/JPG 等位图格式**，扔一个 SVG 链接进去，卡片会优雅地假装没看见。

行业标准尺寸是 **1200×630**（1.91:1），小于 600px 宽的图在 Facebook 上不会以大图卡片展示。

### 用 Python 画一张，而不是开 Photoshop

封面的构成很简单：深色渐变底、绿色描边徽章里一个"叶"、标题、副标题、一行小字署名。这种"色块 + 系统字体"的图，[Pillow](https://python-pillow.org/) 十几行就画了，还能进 Git 版本管理，想改文案重跑一次即可。

环境准备：

```bash
pip install pillow
```

核心代码（完整脚本就是生成本站封面的这一份）：

```python
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H), (13, 17, 23))
px = img.load()
for y in range(H):                       # 手工竖向渐变
    t = y / H
    for x in range(W):
        px[x, y] = (int(13+9*t), int(17+10*t), int(23+11*t))

d = ImageDraw.Draw(img)

# 绿色描边圆角徽章 + “叶”
d.rounded_rectangle((80, 155, 400, 475), radius=64,
                    fill=(13, 17, 23), outline=(2, 216, 29), width=6)
fb = "C:/Windows/Fonts/msyhbd.ttc"       # 微软雅黑 Bold，macOS 换 PingFang.ttc
d.text((240, 318), "叶", font=ImageFont.truetype(fb, 190),
       fill=(2, 216, 29), anchor="mm")

# 标题与副标题
d.text((470, 205), "叶扬的博客", font=ImageFont.truetype(fb, 88), fill=(230, 237, 243))
d.text((470, 350), "我是叶扬，人生苦短，我用 AI ～",
       font=ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 38), fill=(139, 148, 158))

img.save("og.png", "PNG", optimize=True)
```

成品就是现在你把这个链接丢进任何聊天框会看到的卡片：左侧绿色描边徽章、右侧标题与口号、底部一行 "Gmeek · 用 GitHub Issues 写博客"，底部还有一条渐变绿线收边。

> 两个坑替叶扬踩过：① Pillow 画渐变只能逐像素手搓，没有 API，但 1200×630 的循环瞬间完成；② 中文字体必须显式指定 `msyhbd.ttc`，否则 Pillow 默认字体不认识中文，出来一排豆腐块。

## 配置：两行，然后手动重建

两个文件放进 `static/`，构建时会被原样复制到站点根目录（这个机制在[第 1 篇](/post/1.html)详细讲过）。然后打开 `config.json`：

```json
{
    "faviconUrl": "https://yeyangchen2009.github.io/favicon.svg",
    "ogImage": "https://yeyangchen2009.github.io/og.png"
}
```

注意**必须写完整的绝对 URL**，不能图省事写 `/og.png`。模板 [base.html:9](https://github.com/Meekdai/Gmeek/blob/main/templates/base.html#L9) 里 favicon 用相对路径浏览器还能自己补全，但 `og:image` 是给微信、Facebook 这些外部爬虫读的——它们手里没有你的域名上下文，相对路径等于无效地址。

老规矩三连：提交、push、**深呼吸几秒**、手动全局重建：

```bash
gh workflow run "build Gmeek"
```

（push 完立刻触发构建可能 checkout 到旧代码，叶扬在 [G02](/post/8.html) 已经替大家表演过一次了。）

## 验证清单

- [x] 浏览器标签页显示绿色"叶"图标，切换系统明暗主题，图标底色跟着变；
- [x] 查看页面源码，`<link rel="icon" href="...favicon.svg">` 已就位；
- [x] `og:image` 的 content 是 `https://` 开头的绝对 PNG 地址；
- [x] 把文章链接贴到 <https://www.opengraph.xyz/>（免登录的 OG 预览工具），能看到完整大图卡片；
- [x] 微信/Telegram 发给"文件传输助手"实测卡片效果（平台有缓存，第一次抓取后隔几分钟才更新）。

## 还能怎么玩

1. **每篇文章单独封面**：文章正文最后一行的隐藏 JSON 支持 `"ogImage"` 字段，给重点文章配专属头图（G06 会细讲这个机制）；
2. **favicon 也可以走纯图形派**：不写字，画个代码括号 `</>`、一片叶子，或者你的猫的剪影；
3. **想要 ico 兼容老古董浏览器**：用任意在线转换工具把 SVG/PNG 转一份 `favicon.ico` 丢进 `static/`，再通过 `allHead` 加一行 `<link rel="alternate icon">`，新旧通吃。叶扬选择不伺候。

## 小结

图标和封面这种东西，不影响任何功能，但它决定了博客在"站外"的样子——读者还没点进来，就已经在标签页和聊天框里见过它两次了。一个自己写的 SVG 加上一张自己画的 PNG，成本半小时，辨识度是永久的。

下一期 G04 是整个系列里最"躺赢"的一篇：不写一行代码、不放一个文件，只要去两个网站点几下提交——把 RSS 喂给 Google 和 Bing，让搜索引擎开始带陌生读者上门。

## 参考

- 模板中的 favicon 与 OG 注入点：<https://github.com/Meekdai/Gmeek/blob/main/templates/base.html>
- Open Graph 协议（图片要求一节）：<https://ogp.me/>
- SVG favicon 与 prefers-color-scheme：<https://developer.mozilla.org/en-US/docs/Web/Manifest/icons>
- 作者的 favicon 样本：<https://github.com/Meekdai/meekdai.github.io/blob/main/favicon.svg>
- OG 卡片在线预览：<https://www.opengraph.xyz/>
- 系列总揽：[Gmeek 插件与功能全景调研（第 0 篇）](/post/5.html)
