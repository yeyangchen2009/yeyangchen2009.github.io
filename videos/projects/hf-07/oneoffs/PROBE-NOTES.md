# hf-07 前制真机探针台账（0.8.107，2026-10-19）

> 目的：开拍前把 preview / snapshot / keyframes / compare / grade-compare
> 在 0.8.107 的真实行为摸清，并**在真机验证本集灵魂教学事故**——
> 「preview 里好好的，snapshot 抓出来不对」。全部命令实跑，现象附实测证据。
> 沙盒工程：`F:\_hftest\hf07-probe\`（仓库外，不入库；种子 HTML 见
> `oneoffs/probe-seeds/`）。Node v24.6.0 / npx hyperframes@0.8.107 / UHD620。

---

## ★ 2026-10-19 勘误（重大翻转：主角不是 CSS，是「自掐表」黑户）

下文 E2/E3/E4/E5（CSS 段）/E6（暗线段）的原结论**系对原档的误读，已作废**，
保留原文仅作探侦过程留档。翻转起因：第五次彩排 c03 断言「红四帧异位」在
CSS 红块上**稳定失败**（四帧红全 0.3432 同位）。复核方法：不重跑历史，
直接对沙盒残留原档 `F:\_hftest\hf07-probe\build\probe1–4\*.png` 用 PIL
条带采样量红蓝质心——probe3 四帧红全 0.3432（同位）、probe4 at=10 红在
终点 0.5516（随 seek），与台账文本记载恰好相反。

**五级实现矩阵（2026-10-19 真机，同一红蓝对照工程逐一替换红块实现）**：

| 红块实现 | check | 四连帧（同 at） | 结论 |
|---|---|---|---|
| CSS `animation`（infinite/forwards 任意时长） | pass | **同位** | snapshot 经 **WAAPI 把 CSS 动画虚拟化到时间轴**，seek 到 at 相位；player 里 getComputedStyle 实测暂停冻结、seek(6)→translateX(400)。CSS 是合法居民 |
| 裸 `requestAnimationFrame` | **硬 error** | （四位置，拿不到帧） | StaticGuard：`requestAnimationFrame runs on wall-clock time, not the GSAP timeline...` |
| `setInterval`＋读 `Date.now()` | **硬 error** | （四位置） | non_deterministic_code：`Fix: Use GSAP timeline position instead of wall-clock time` |
| **`setInterval`＋闭包内自有计数器**（不碰任何时间 API、不注册 `__timelines`、不走 rAF） | **pass** | **四帧四位置**（两轮可复现，轮间相位不同）、不理 at | ★真正主角：自掐表黑户 |
| 同上，周期改 60s（v3 慢表） | pass | at=10 三跑 red≈0.146 稳定贴左、blue=0.5516 在终点 | 第十秒补刀镜头 |

**体检可见性（keyframes，新主角下真机重测）**：

- 无参报告对自掐表**完全隐身**：v1 现有 3 items＝#good（fromTo/flat @0→8s）、
  #clock（to/flat @0→12s）、`@keyframes legalPulse css #legal`，无 #bad；
  `--json` 里 #bad 既不在 tweens.targets 也不在 cssKeyframes.selectors。
- `keyframes v1/index.html --shot build/x.png --selector #bad`：**exit 1
  不出图**，文案 `--shot: nothing animates under '#bad'. Nearest animated
  elements: #good, #clock, #legal.`——机器连它在动都不知道。
- 布景因此在三工程左上角加入**合法 CSS 居民 #legal**（绿点 legalPulse 2s
  alternate；四连帧绿点质心四帧全 0.0373 同位），与蓝块一起构成
  「登记在册＝seek 管得住」的正衬，红块是唯一黑户。
- 旧 E5「CSS 检出≠驱动、onion 残影推几何时间标乱序」一并作废：0.8.107
  对 CSS 是**既检得出也驱得动**（WAAPI）；--shot 只对登记在册的元素出图。

**compare 暗线修正（旧 E6）**：两格自掐表实例在同一浏览器实例内近乎同时
导航/截图，相位被启动时差锁死，格内质心差实测 ≈0.002–0.006（几乎同相），
「两格各停各墙钟」**不成立**；事故证据只认同一命令 `--at 2,2,2,2` 的
四连帧（c03）。compare 仍正常出 1212×372 两格图，教学点回到「两方案一排」。

**其它勘误**：compare `--labels` 数量不符真机 **exit 1**（非旧表 exit 2），
文案 `--labels count (1) must match path count (2)`。

新叙事一句话：**check 0 error 的工程里，没登记时间轴、自己 setInterval
掐表跑的动画，preview 里顺滑无痕，snapshot 同秒连拍四张四个样，体检报告
里连户口都没有。** 种子已替换：01＝自掐表 4s、02＝同构 x500 变绿、
03＝自掐表 60s 慢表（旧 03-css-forwards.html 已删），三页均带 #legal 绿点。

---

## 0. 结论先行（分镜约束）

> ⚠︎ 本节第 1/2 条已被文首勘误翻转：CSS 动画被 WAAPI seek 接管（合法居民），
> 真正不可 seek 的是 setInterval 自掐表黑户；第 2 条「检出≠驱动」对 CSS
> 不成立。以下原文留档，以文首五级矩阵为准。

1. **核心事故成立且比预想更尖锐**：CSS animation 无论 `infinite` 还是
   `forwards`、无论时长是否与 composition 对齐，snapshot/烤片时**只认浏览器
   墙钟、不听时间线 seek**。同一个时间码连抓多帧，CSS 元素位置帧帧不同；
   GSAP seekable 元素像素级一致。口号＝「同一份输入、同一秒，画面不一样
   ——确定性死了」。
2. keyframes 命令能**静态检出** CSS @keyframes 的全部声明，但 onion-shot
   对 CSS 目标只按声明「推几何」，时间标乱序、实像位置仍看墙钟。
   「体检看得到」≠「时间线驱得动」。
3. compare 是本集新工具主角之一：2+ 个 HTML 变体同一 t 截成一张带号对照页，
   天然适合「两个方案摆一起挑」。compare/grade-compare/keyframes --shot
   默认走**硬件 GPU**（无 SwiftShader 开关），snapshot 用 `--no-browser-gpu`
   走 SwiftShader 保确定性。
4. grade-compare 是调色选片工具（original 基线＋候选格），与逐帧验收主线
   弱相关，正片一句话带过或只进图文。
5. preview 后台语义完整（--background/--status/--list/--stop 按项目路径
   绑定），录屏 take 用前台可见 Studio，编排可用后台 server。

## 1. 命令面（help 实测，2026-10-19）

| 命令 | 关键事实 |
|---|---|
| `preview [DIR]` | 默认端口 **3002**；`--port/--force-new/--background/--foreground/--status/--stop/--list/--kill-all/--open(默认true)/--lint-verbose`。后台日志 `C:\Users\<用户>\.local\state\hyperframes\previews\<hash>.log`。子目录工程的 Studio URL 形如 `http://127.0.0.1:3021/#project/v1`。 |
| `snapshot [DIR]` | **位置参数只收目录**，传单 HTML 报 `Not a directory`；目录里只有 index.html（无 hyperframes.json/meta.json）也能跑。`--frames N`（默认5，**均分**，3 帧实测 0/6/11.64s）、`--at a,b,c`（可重复同值不去重，文件名仍 frame-0X-at-2s.png）、`--end`（默认 true 尾帧）、`-o`（目录自建）、`--zoom '<sel>'\|'x,y,w,h'`（选择器命中不了是 error）、`--zoom-scale 3`、`--angle`、`--against <video>`（参考视频 pair sheet）、`--describe`（有 GEMINI_API_KEY 才跑 vision）、`--no-browser-gpu`（SwiftShader 确定性）。 |
| `keyframes [TARGET]` | TARGET 可收目录或单个 composition HTML。`--runtime gsap\|css\|anime\|all`、`--json`、`--shot=<out.png>`（**必须带值给输出路径**，当布尔开关用不出图、只打印 tip）、`--samples 9`、`--layout path(默认)\|strip`（strip 真像素 filmstrip 仅 SVG 选择器；DOM 元素＝1 live frame＋矢量 marker）、`--from/--to/--angle/--fit/--ghost/--selector`。 |
| `compare [PATH]` | 「2+ paths」：传多个 composition HTML（或项目目录）。`--at <秒>`（单点）、`--labels a,b`（**逗号分隔，标签内禁逗号**，数量不符直接 exit 2）、`--out ./compare.png`、`--cols`（≤4）、`--json`、`--timeout`。 |
| `grade-compare --for <图|视频>` | `--grades` **是 JSON 文件路径**（内联 JSON 字符串被当文件名报错，help 未写明）；JSON＝`[{"label","grading"}]`，grading 实测吃 CSS filter 串（`sepia(0.6)`、`brightness(1.25) saturate(1.2)`）；`--luts a.cube,b.cube`、`--baseline`（默认 prepend original 格）、`--out`、`--project`。 |
| `present [DIR]` | 幻灯片演讲模式＋audience sync，默认端口 3004。**不是日常预览工具**，本集不展开。 |

## 2. 事故实验矩阵（核心证据）

探针页（probe-seeds/01-css-vs-gsap.html）：12s composition，两个 120px 方块
同一轨迹（x 0→800）：

- `#good` 蓝：`gsap.timeline({paused:true})` + fromTo 8s +
  `window.__timelines['main']` 注册（seekable 正解）；
- `#bad` 红：`animation: slide 4s linear infinite`（v1）/
  `8s linear forwards`（v3，边界实验）；
- 右上 clock：GSAP dummy tween 的 onUpdate 写 `t=<tl.time()>`，
  证明截图瞬间引擎确实 seek 到了该秒。

### E1. CDN 依赖在无头环境翻车（布景坑，非教学事故）

- 引 jsdelivr 的 gsap CDN，check 直接两条 error：
  `request_failed: Failed to load npm/gsap@3.14.2/dist/gsap.min.js:
  net::ERR_CONNECTION_RESET` ＋ `page_error: gsap is not defined`；
  snapshot 四帧蓝块全趴起点、clock 停 `t=?`。
- 换本地 gsap.min.js（正式工程惯例）即恢复。**录屏布景铁律：gsap 必须本地**。

### E2. 四时点 seek（infinite 版，--at 1,4,8,11）　【⚠︎ 已勘误，见文首】

- 蓝块：x ≈ 100/400/800/800，严格随 seek（单帧目验 11s 精确停终点）。
- 红块：前三帧贴左（截图都在页面加载后 1s 内），**11s 帧漂到
  translateX ≈ 628**——与时间码无关，只与该帧截获时的墙钟有关。

### E3. ★同点连抓（--at 2,2,2,2，build/probe3/contact-sheet.jpg）　【⚠︎ 已勘误：原档四帧红同位 0.3432，见文首】

- 四帧角标全是 **t=2.00s**；蓝块四帧像素级同一位置；
  **红块四帧四个位置**（translateX ≈ 50 / 170 / 215 / 105px）。
- 这是本集最硬一帧证据：同一 t、同一输入，CSS 动画给四张不同的图。
- 截图原档：沙盒 `build/probe3/`。

### E4. forwards 边界（v3，--at 2,2,2,10,10，build/probe4）　【⚠︎ 已勘误：原档 at=10 红在终点 0.5516；v3 已换 60s 自掐表慢表，见文首】

- 8s linear forwards、声明与时间轴等长：t=2 三帧红块仍微差；
  **t=10 两帧红块都在左侧**（截图离页面加载约 1s 墙钟，动画才走 1/8），
  蓝块已在终点。有限时长/forwards/对齐时长**都不构成适配**，结论无豁免。

### E5. keyframes 体检：检出 ≠ 驱动　【⚠︎ 已勘误：本节 CSS 观察作废；新事实＝自掐表完全隐身＋--shot #bad 硬 error，见文首】

- `--json`：GSAP tween 全结构化（id/target/method/start/end/keyframes/path）；
  CSS 动画在 `cssKeyframes` 数组里静态可见（name=slide、selectors=#bad、
  from/to 声明完整）；traces/anime 为空。
- `--shot` onion 目验（build/onion-good.png / onion-bad.png）：
  - #good：5 ghost 沿真实路径 0→800，标 0/3/6/9/12s（9/12 叠终点），
    live frame 在 t=12 终点，青色路径线；
  - #bad：ghost 只是按 from/to 声明**推的几何**，时间标出现 0/9/6/3 乱序，
    live frame 是 t=12 截获瞬间的墙钟相位（实测贴左，纯巧合）。
- **坑**：timeline 里若有 target 为空对象 `{}` 的 tween，工具给它生成
  id `dwell/hold`，--shot 拿去 querySelector 直接
  `SyntaxError: 'dwell/hold' is not a valid selector` 崩掉。
  dummy tween 挂真实元素（#clock）规避。正式工程几乎不会踩，探针已排。

### E6. compare 变体对照（build/compare.png）　【⚠︎ 暗线已勘误：两格红近似同相，质心差≈0.002–0.006；另 labels exit 1 非 2】

- v1（x800 蓝）与 v2（sed 改 x500 绿）`compare ... --at 4
  --labels 方案A·x800,方案B·x500`：一张横排两格 PNG，左上自带
  「1. 方案A·x800」「2. 方案B·x500」标号，两格角标 t=4.00s。
- 红块两格各停各的墙钟相位——compare 同样让 CSS 动画露馅（可作教学暗线）。
- labels 数量不符 exit 2；标签里写逗号被切成 4 段。

### E7. grade-compare（build/grade.png）

- grades.json 三格成品：original（自动基线）/暖色/高亮，CSS filter 实时
  生效，2×2 末格留空。定位＝调色候选对照，正片一句话。

### E8. snapshot 输出目录语义（hf-04 老经验精确化）

- 默认输出 `<project>/snapshots/`；预置 `MARKER.txt` 与
  `frame-99-at-99s.png` 后跑 `--frames 3`：**MARKER.txt 保留，旧
  frame-*.png 被清**，新帧 frame-00-at-0s / 01-at-6s / 02-at-11.64s，
  contact-sheet.jpg 重写。
- 结论：snapshot 只清自己模式的帧产物、不删其他文件；F2/取证输出一律放
  build/，别借 snapshots/（会被连坐）。
- 每次 snapshot 同目录自动附 **contact-sheet.jpg**（grid 总览，本集可直接
  当录屏画面：一张图看完五个时刻）。

### E9. preview 生命周期

- `preview v1 --background --no-open --port 3021`：后台 PID 6244，
  curl 根路径 HTTP 200；`--status` 给 Studio/Server 双 URL＋PID＋日志路径；
  `--list` 一行 `Port 3021 v1 <路径> (PID …)`；`--stop` 后 list
  `No active preview servers found`。
- 录屏 take：前台 preview（自动开浏览器）拍 Studio 交互；后台 server
  可在 take 前先起好、减少录入等待与启动动画。关 DevTools 窗口跳矩形的
  hf-04 旧坑仍按 screen-rec.md §6 处理。

## 3. 对分镜/录屏的约束（喂 STORYBOARD）

> ⚠︎ 本节第 1/2 条随文首翻转更新：三件套现为 GSAP 蓝块＋合法 CSS 绿点
> （登记在册、seek 管得住）＋自掐表红块（黑户）；preview 里顺滑的是
> 自掐表红块。最终口径以 STORYBOARD-FRAMEWORK.md（v1）为准。

1. 事故演示三件套同屏：GSAP 蓝块＋CSS 红块＋t= 时钟，一个工程讲完
   「谁听 seek」。E3 的 `--at 2,2,2,2` 接触表是高潮镜头。
2. 拍 Studio 实时段：CSS 红块在 preview 里顺滑循环（观感完全正常），
   切到 snapshot 接触表立刻穿帮——「眼睛骗人，帧不会」。
3. 工具出场顺序建议：preview（实时）→ snapshot（离帧/接触表/--zoom）→
   keyframes（体检＋onion）→ compare（方案对照）；grade-compare/present
   片尾一句带过。
4. 终端命令布景：一律本地 gsap.min.js；命令真实跑、输出以本机为准；
   compare 的 labels 不带逗号；keyframes --shot 必须给路径。
5. 浏览器录屏段回归 hf-04 SOP：guard CDP/Edge 身份、swapchain 双轨、
   扩展 reload 重注、1600×920 外框盖死、preview server 后台预起。
6. 录屏里出现的 contact-sheet / onion / compare 图全部用本工程真机产出物，
   不后期伪造。

## 4. 未探项（录屏前按需补）

- `snapshot --zoom` 选择器/像素区裁剪、`--angle` 3D 相机（help 清楚，
  分镜用到再真机，注意 zoom 选择器命中不了是硬 error）。
- `snapshot --against` 参考视频 pair sheet（迁移/复刻场景才用，本集大概率
  不进正片）。
- `keyframes --ghost`（canvas/WebGL 真帧洋葱皮）、`--layout strip` 的 SVG
  路径（本集无 canvas/SVG 运动主角）。
- Studio GUI 内操作（拖时间轴/播放头/暂停）属真人录屏段，彩排时补台账。
