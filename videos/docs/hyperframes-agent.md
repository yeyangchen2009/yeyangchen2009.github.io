# HyperFrames 注意事项（agent 工作指南）

合并自各项目原 CLAUDE.md / AGENTS.md，只保留本管线真正用到的规则与
五片实测铁坑。写/改任何 composition 前先读这里。

## 版本钉死

CLI 统一 `npx --yes hyperframes@0.8.107`，GSAP `3.14.2` 本地副本。钉版本是
为了数周后仍逐像素一致渲染。升级另开，用 `@latest upgrade --project .`。

## 基本规则

1. 每个定时元素都要 `data-start` + 时长；`data-start` 决定它被定时，
   `data-track-index` 只是 Studio 显示轨道，渲染不读。
2. 定时可视元素给 `class="clip"`；框架按 `data-start` 决定可见性，
   `.clip` 的 CSS 提供全屏盒。
3. 每个 composition 在 `window.__timelines` 注册**一条 paused 根时间轴**：
   ```js
   window.__timelines = window.__timelines || {};
   window.__timelines['main'] = gsap.timeline({ paused: true });
   ```
   手动加进根轴的场景时间轴不能 paused（seek 根时 paused 子轴不前进）。
4. 有声口播放 `<audio id="a-roll-audio" data-track-index="2">`；静音
   b-roll/背景用 `muted`。
5. 只允许确定性逻辑：禁 `Math.random` / `Date.now` / 网络抓取。

## 时间轴写法

- `gsap.timeline({paused:true})`，全部**绝对秒**定位（动画第 4 参数）。
- 无 position 参数的 `set` 会追加到时间轴**末尾**；初始态 set 必须显式
  传秒，否则初始态被排到片尾。
- 片源注册名固定 `'main'`（对应 `data-composition-id="main"`）。

## ★ StaticGuard（最重要的坑）

不要在带 `class="clip"` 的元素上动画 `autoAlpha` —— 静态守卫会拦截。
规避固化在 `scene.py`：clip 内再包一层 `.scene-inner`，淡变目标写成
`#id > .scene-inner`、**只动 opacity**：

```js
tl.fromTo('#sc-x > .scene-inner', {opacity:0}, {opacity:1,…}, inAt);
tl.to('#sc-x > .scene-inner', {opacity:0,…}, outAt);
```

## ★ GSAP 控制 SVG 的铁律

- 被 GSAP 动画的 `g` **不可自带 transform**，否则基点/平移会乱（被动画
  的 g 上 `set x:0` 会瞬移到原点，行者飞出画面）。
- 需要固定基点时，把基点放在**不动画的外层 `g`**，内层 g 交给 GSAP。
- SVG 装饰 `path` 若要当线，显式 `fill:none`。
- 路线/分支点亮用 `stroke-dasharray` + `stroke-dashoffset`。

## ★ blur 与捕获性能

含 `filter:blur` 的画面会从 drawElement streaming（快、hardware gpu）
回退到 screenshot capture（慢）。因此：
- wang / zbj：零 blur，走快路径。
- **素版 zsx 刻意保留 blur（残卷朦胧是设计语言），迁移时不得"顺手统一"
  去掉 —— 这里"不一致即正确"。**

## 验证门控（便宜 → 昂贵，默认只做前两层）

- **A check**：改完必跑，0 error。已知 warning（gsap_infinite_repeat /
  composition_file_too_large / timeline_track_too_dense /
  nested_structure）五片都有，属接受项；迁移前后 warning 集合要相同。
- **B compare + snapshot**：`verify.compare(老, 新)` 要求 0 差异（仅宽恕
  `media/` 前缀）；`snapshot --at <每幕中点> --no-browser-gpu`
  （SwiftShader）两侧像素一致。
- **C render**：仅当 B 出现无法解释差异时整段重渲染（pro 最短，优先选）。

## 已知无害项

- concat 点偶发 1 条 `Non-monotonic DTS`：AAC priming，容器时长差约
  21ms，观感无影响，接受。
