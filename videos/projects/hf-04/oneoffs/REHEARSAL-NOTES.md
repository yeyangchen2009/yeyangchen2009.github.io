# hf-04《seek》真实彩排笔记（fork①，2026-10-12 06:34–08:25）

> 本文件只记录机制实测发现，不碰沙盒文件。沙盒 `F:\_hftest\hf04-seek` 由主控会话并行彩排，
> index.html 的最终形态以主控为准（08:22 版＝paused timeline＋title/card/subtitle 三个 fromTo
> 挂 2/3/6＋注册 main，已是正解）。

## 环境

- HyperFrames 钉版 0.8.107；preview server：`cd F:\_hftest\hf04-seek && npm run dev`
  （必须以项目目录为 cwd；`npm --prefix` 不改 cwd，会注册成 gmeek-site 项目，踩过）。端口 3002。
- Studio 是浅色壳＋`hyperframes-player` 自定义元素，composition 在其 shadowRoot 的**同源 iframe** 里
  （`/api/projects/hf04-seek/preview?__hf_shader_capture_scale=1&__hf_shader_loading=player`）。
- player 元素暴露 `seek(t)/play()/pause()/currentTime/paused/duration`，可从宿主页 CDP 直接驱动。
- **不要对 preview iframe 直接 `contentWindow.location.reload()`**：会永久卡在 readyState=loading、空 body。
  重载 composition 的真实路径＝保存文件触发 watcher HMR；重载整个 Studio 用 CDP `Page.reload`（顶层）。
- preview server 会在 index.html 变更瞬间另存一份 `index.start.html`（根级 composition 快照），
  导致 lint `multiple_root_compositions`；该文件不是备份，确认无用后删除即 0 error。
- CDP Edge：`--remote-debugging-port=9222 --user-data-dir=F:\_hftest\edge-cdp`（实例仍开着）。
  探测脚本：沙盒内 probe1–4.mjs、reload_studio.mjs；通用 `F:\_hftest\cdp_eval.mjs`、cdp_shot_clip.mjs。

## ★核心发现：0.8.107 运行时对全局 GSAP 动画有 `__proxied` 兜底代理

粗稿开场假设「裸 `gsap.from` 在浏览器能动、Preview/拖进度条不动」。**Studio 路径实测不成立**：

- 事故版 `<script>gsap.from("#title",{opacity:0,y:24,duration:0.6})</script>`，不建 timeline、不注册。
- iframe 内仍出现 `window.__timelines = { main: <GSAP Timeline>, __proxied: ... }`——运行时自动兜底。
- player.seek 扫描（每次间隔 90ms，连测）：

  | seek(t) | display | opacity | translateY |
  |---|---|---|---|
  | 0 | block（visibility:hidden，clip 窗外） | 0 | 60 |
  | 2.0（title clip 起点） | block | 0 | 60 |
  | 2.1 | block | 0.095 | 54 |
  | 2.2 | block | 0.295 | 42 |
  | 2.3 | block | 0.513 | 29 |
  | 2.45 | block | 0.727 | 16 |
  | 2.6 | block | 0.885 | 7 |
  | 3.0+ | block | 1 | 0 |

  seek(2.3) 连测两次数值完全一致（确定性）；+500ms 后状态保持，不漂。
- 此时 `gsap.getTweensOf(title)` 为空（tween 播完即 kill）、`globalTimeline.time()≈0.01`（墙钟被冻）。
  插值不是 GSAP 算的，是运行时自己施加的（inline style 仅 `visibility/position`，transform/opacity
  不出现在 element.style 与静态样式表中，疑似运行时代理层直接驱动）。
- 注意起点是 y=60 而非源码的 24：该数据采自主控的 CSS `@keyframes flyin`（translateY 60px）中间版本，
  非我的 y:24 版本；代理对 CSS keyframes 同样接管（见下）。
- lint 对「不注册 timeline」零报错。

**对粗稿的影响**：开场事故必须重选。候选：
1. 先验证 `snapshot --at`/render 抓帧路径是否也走代理（主控 08:22 正在跑双轮 snapshot 确定性对比）。
   若抓帧路径不兜底 → 「Studio 里好好的，渲染出来全是终态」是更真实、更精彩的事故。
2. setInterval/requestAnimationFrame 墙钟反例（主控 08:18 已建「定时器驱动的动画/tick」版）：
   代理管不了非 GSAP 的 DOM 副作用，seek 后 tick 计数不可倒拨——这才是代理时代仍成立的 seekable 反例。
3. CSS `@keyframes` + addClass/transition：代理实测能驱动 keyframes（flyin 版可 seek），
   「addClass＋transition 帧帧不确定」段是否仍成立需重新实测，别照旧稿讲。

## 正解版（主控 08:22 定稿形态）

`gsap.timeline({paused:true})`＋三个 fromTo 带位置参数（title 挂 2、card 挂 3、subtitle 挂 6）
＋`window.__timelines["main"]=tl`（main＝#root 的 data-composition-id）＋`tl.seek(0)`。
AGENTS.md 第 97–104 行明确：每个 composition 注册一个 paused root timeline；场景子 timeline 不许 paused。

## 录屏提醒（hf-03 遗留）

- 录屏取景区与窗口严格同宽，根治右缘 27px 穿帮。
- check 实拍等待按最差环境上浮（hf-03 实测 TTY＋录屏并发 33–36s，留 42s）。

## 夜间代录 runbook（2026-10-12，用户离机/授权后才执行）

铁律：guard 三身份白名单闸每个动作生效中；前台不是隔离 Edge(pid 动态查 9222)/
标题含 `_hftest\hf04-seek` 的隔离 NPP/`hf04-rec` 终端，脚本自中止。用户在机一律不动桌面。

### A0. 开录前必跑：锚点静态自检（2026-10-12 新增，零桌面动作）

`python oneoffs/check_anchors.py`——在 backup 五权威态文本上全量校验
record_segments 每个 take 的 line_of/reveal_in_line/insert/replace 锚点。
退出码非 0 不许开拍。新增/改动任何 NPP 锚点或备份后必须重跑。

2026-10-12 静态核对已抓出并修复 **4 处跨行取景 bug**（reveal_in_line 的
end 锚必须与行锚在同一物理行，跨行实拍即抛 AssertionError；多行块一律
scroll_anchor 垂直取景）：

1. seg2a keyframes 全块：尾锚 `translateY(0);` 在块内第 8 行 → 改 scroll_anchor；
2. seg2a animation 行：起锚误写 `#title {`（在选择器行而非属性行）→ 改 `animation: flyin`；
3. seg4a 开场/回块两拍：`}, 500);` 与 `let tick = 0;` 均不在 setInterval 开口行
   → 开场选区留 56 行、回块选区落 54 行，块底统一 scroll_anchor 保 54–59 同框；
4. seg6 注册行：尾锚 `tl.seek(0);` 在下一物理行 → 尾锚改同行 `= tl;`，下一行 scroll_anchor。

同日**备份收敛**：s4-final.html 原为主控手写多行展开写法，与 seg6 实拍工艺
（replace 单行注释→三行单行 fromTo）排版不一致；已用 s3 经实拍文本变换的
单行款覆盖（去空白 JS 逐字符等价、node --check 通过，s1 备份本就与 seg2a
产物逐字一致）。旧多行版归档 `backup/archive/s4-final-multiline-20261012.html`
（全部 seek 实测数据采自该版，JS 等价故 2.1/2.3 插值表继续有效）。
沙盒现场 index.html 已同步为单行 s4。

同日**终端标题撞闸修复**：npm/npx 在 cmd 下运行会 SetConsoleTitle，WT 默认
跟随应用把 tab 标题改成 npm 命令，guard 白名单 `startswith("hf04-rec")`
立即失配——seg3 第二条 snapshot 注入前、seg5b/seg9 收尾 park_mouse 都会撞
自己的闸（hf-03 无闸未暴露）。open_rec_term 启动参数已加
`--suppressApplicationTitle`，tab 标题恒为 hf04-rec。**彩排首验**：建窗后
跑一句 `npm -v`，WT tab 标题必须保持 hf04-rec；开录前若有旧参数启动的
残留 hf04-rec 窗先手动关掉（复用分支不会重加参数）。

同日**装闸收口**：guard.install_input_guards(rec) 幂等装八原语；
seg5_rehearse 独立分步跑也在模块级装同一套闸（与 record_segments 共享同一
rec_automate 模块对象）。已运行时验证：独立 import seg5 即带闸、再 import
record 幂等、八原语全 `guarded_*`、非白名单前台首击即 UnsafeForeground
（当场用用户前台的 Excel 终端实测拦截成功）。

同日**第三轮：缓冲区 vs 磁盘命门（实拍必崩级，静态抓出）**：npp_ops 的
`read_file/line_of/_byte_position` 全部读**磁盘**，而 `replace_all`（Ctrl+H）
与 `insert_after_line`（goto＋Enter＋粘贴）只改 NPP **内存缓冲区**、不存盘。
seg6 act 与 `_gsap_edits` 原序列「replace 后未 save 即 line_of 新行、两次
insert 之间未 save」，实拍必抛 AssertionError（锚在磁盘还是旧 s3 态）。
已修：三处编辑后均 `n.save(磁盘谓词)`（seg2a 本就每步 save，无此 bug）。
固化手段＝check_anchors.py 新增 `NppDiskModel` 双态（disk/buf）编辑序列
步进模拟器，逐拍镜像 take_seg6/_gsap_edits/take_seg2a 的真实调用序，
每个 line_of/reveal/insert 锚点断言「当前磁盘态」唯一命中、每个 save 谓词
必须通过、三序列终态须与 s1/s4 备份逐字相等。**变异测试已证网有效**：
人为删掉任一 save，校验器退出码 1（「磁盘命中 0 次——前面的编辑是不是忘
了 save？」）。改实拍编辑序列必须同步改模拟器（act 内有★镜像注释）。

**seg6 时长 46s 静态复核（加 save 后仍够）**：record 预算模型
`action ≤ duration−2.2s`（录屏起 1.0＋尾 1.2）→ 预算 43.8s。act 精算：
固定 sleep 19.5s（3.0/2.4/.5/3.0/.4/.4/2.6/3.0/4.2）＋replace_all ≈5.0
（内置等待 2.68＋find 98 字符逐字 1.96）＋save×3 ≈0.9＋insert×2 ≈4.8
（goto 序列内置等待 1.45＋粘贴复位 .66）＋reveal×5/behind/guard/park ≈2.2
＝**≈32.4s，余量 11.4s**；忙机极端（打字倍速＋save 全满轮询 1.5s）≈38s
仍安全。尾帧约 11s 偏长，剪辑掐尾即可，时长不上调（避免与 hf-03 节奏分叉）。

### A. 开录前必做的九项实拍标定（结果回填本文件）

1. ~~PLAY_X/Y 坐标~~ **已标定（2026-10-13）**：新摆位录区内 Preview Play
   bbox 770..782×422..436，质心 **(775, 429)**，常量已改 PLAY_X,PLAY_Y=775,428
   （hf-03 旧值 775,487 作废）。
2. ~~snapshot -o 自建目录~~ **已静态坐实（2026-10-12）**：0.8.107
   `snapshot-MSGC7HTA.js:315` `mkdirSync(snapshotDir,{recursive:true})`，
   -o 不存在自建，无需脚本兜底。
3. ~~snapshot 实拍耗时~~ **已回填（2026-10-13）**：三帧
   `--at 2.1,2.5,2.9 --no-end` 单轮 headless 真机约 **14–17s**，take_seg3
   snap_wait **14→20**（record 6+2*20+12=58s）。帧命名静态坐实仍有效
   （snapshot-MSGC7HTA.js：`frame-${i pad2}-at-${Number(t.toFixed(3))}s.png`，
   i 从 0 每时间点一帧）→ seg3 fc 路径 `frame-00-at-2.1s.png` 正确；
   race 单点 --at 2 → `frame-00-at-2s.png` 与脚本校验一致。**seg5a 已不用单帧轮**，
   改跑 `python race-snapshot.py`（见下「段⑤a 实证工艺」），race_wait 维持
   150（闲机实测整段 94s；正式 take 若忙机超 150 再上调）。
4. ~~check 实拍耗时~~ **已回填（2026-10-13）**：s2 页真机 `npm run check`
   全绿约 **22–24s**，take_seg5b check_wait **42→26**（record 31s）。
   ⚠️ 待正式 take 复核：hf-03 记载 TTY＋录屏 gdigrab 并发下 check 曾达
   **33–36s**，若实拍尾帧被截，立即回 42 重录 seg5b（第 65 行旧记载保留对照）。
5. ~~render 实拍耗时（seg9 定量）~~ **已实测（2026-10-14 凌晨）**：沙盒 s4 页
   非录屏空跑 `npm run render -- -o rec-render/hf04-seek.mp4`，墙钟 **47.5s**
   （HF 自报 35.4s＝compile 2.6＋setup 10.1＋capture 22.0＋assemble 0.2，
   drawelement/hardware gpu/workerCount 1，300 帧 10s，exit 0）。render_wait=80
   **不动**（TTY＋gdigrab 并发按 hf-03 check 教训预留 +30~50%，尾帧长剪辑掐尾）。
   **seg9 纳入 ALL_TAKES（第三批压轴）**：capture 期枚举可见顶层窗口无新 Chrome
   弹窗（worker 为 headless，不盖 hf04-rec 终端），终端镜头安全。命令合法性
   静态坐实：package.json 有 check/render 脚本（npx 透传 `--`），
   render-EXSRG666.js 官方示例 `render -c ... -o intro.mp4` 同形。
6. ~~DevTools 分隔条/控制台坐标~~ **已整段重标定（2026-10-13 深夜，seg5_rehearse.py 固化）**。
   旧值 SPLIT_Y=700／CONSOLE_Y=830／Ctrl+=×4 全部作废，新工艺：
   - **open**：Ctrl+Shift+J 开底停靠。控制台输入框是自定义元素
     `DEVTOOLS-TEXT-EDITOR`，tab 一打开 activeElement 默认就是它——
     **真实键盘直敲、严禁鼠标点输入行**（z2 下两次点偏、一次把 DevTools 点关）。
   - **split（像素闭环，不信 CDP 几何）**：innerWidth/Height 是 DevTools 内部
     逻辑视口，与屏幕几何脱节。seek(0) 黑舞台前提下，PIL 行亮度阶跃（阈值 25，
     x=200..1500 步长 8）检出标签图标亮行 row；**面板真实顶缘 edge＝row−ROW_OFFSET(30)**，
     拖拽热区＝row+2，鼠标位移与顶缘 **1:1 跟手**；目标 **PANEL_TOP=555**
     （实测 row=585 一轮收敛），最多 3 轮、|edge−555|≤5 收口。split/zoom 后必须
     重注 `cdp_fit.inject_once()`。
   - **zoom 必须 CDP 合成键**：`Input.dispatchKeyEvent` 发 Ctrl+Digit0 复位＋
     两次 Ctrl+Equal（vkc 0xBB）＝**z2，devicePixelRatio=1.875**（断言 ±0.05）。
     严禁真实键盘 Ctrl+=（曾误触到 400%、dpr=6、console-view 高度挤 0）。
   - **脱敏**：Edge 工具栏「其他搜索框」热搜轮播会穿帮（实拍「英方单方面停考
     雅思」入镜），edge://settings 外观页关之（开关物理位约 (1245,771)，
     鼠标点 tab 标题切换，Ctrl+2 直发不切）；edge-cdp profile 已持久关闭。
   - **OS 前台**：CDP `Page.bringToFront` 只切活动 tab、**不抬 OS 窗口**；
     终端启动脚本时热键会全落空并被 guard 拦。必须先
     `guard.force_isolated_edge_foreground()`（EnumWindows 按 pid 找最大
     Chrome_WidgetWin_1、关 <1/3 面积辅助窗、AttachThreadInput 破前台锁、置后验 pid）。
   - **CDP 端点**：必须 `127.0.0.1:9222`——localhost 先解析 IPv6 ::1（Edge
     只听 IPv4）每次 /json 白等 ~2s 超时回退；十条 seek 用 player tab **ws 长连**
     （eval_tab 短连单次 4.1s，长连后 seek 段 93→43s）。devtools:// target 的
     ws 要 `suppress_origin=True`。
   - 分步命令：`python seg5_rehearse.py open|split|zoom|seek|close|all`，
     证据图 seg5-shots/30-open、31-split-fit、32-zoom、33-seek-a..j、34-closed。
7. ~~裸 player 窗标题匹配~~ **已改 CDP 直连（2026-10-12，10-13 真机全验）**：
   prep_window 按 `find_page(PLAYER_NEEDLE)` 的 URL 认 tab（preview 页
   `<title>` 不含 URL，旧标题匹配＋前台 fallback 会在同进程 Studio tab 误开
   DevTools）。tab 缺失由布景 ensure_tabs 建齐；**prep_window 自身不调
   ensure_tabs**（edge:// 设置页不在 /json，会被误判 player 丢失而新开）。
   真机已目验：open 后 DevTools 确实开在裸 player tab 而非 Studio。
   激活两道：`guard.force_isolated_edge_foreground()` 物理抬窗＋
   `browser_activate` 切 tab；前台 pid==cdp_pid 过闸。seek 段另开 player tab
   ws 长连直 eval（回零/读时间不走控制台、不留历史），细节见第 6 条。
8. ~~npp_ops 首次真机 reset/build_s1＋scroll_anchor 目验~~ **已真机全验（2026-10-14 凌晨）**。
   一次性探针（已删）镜像 seg2a/seg6 全序列实拍，13 张证据图留 npp-shots/（不入 git；
   右缘 1600 外含用户 WT 边缘，同 seg5-shots 口径禁提交），结论：
   - **窗口几何零穿帮坐实**：外框 `(-12,0,1624,928)` 下像素量测实体右缘恰在 **x=1600**、
     窗口底缘 **y≈918**，水平滚动条 y≈880–882、状态栏 y≈884–917 **完整在录区 920 内**；
     行高 pitch≈22.5px（zoom 0）、编辑区一屏约 31 行。
   - **scroll_anchor 机理（文件尾块）**：SETSEL 只做「caret 刚好可见」最小滚动，
     锚点行停在客户区底缘内侧（行底 y≈855–868，距录区底 ≥52px），锚点以下的收尾
     标签行（s2 的 L60–62、s4 的 L44–46）被滚出客户区、文档外留白刷白色——叙事无妨。
     **早先「L59 落 y≈985 被切」的怀疑是目测误判**（放大裁剪＋像素量测推翻）：
     seg4a setInterval 块 L56–59 完整同框（npp-05：选区 L56、块底 L59 底缘 y≈868）。
   - seg2a 三拍：#title 选区 y=745–767（npp-02）；@keyframes 十行块 L30–38 完整
     （npp-03）；animation 行无锚点最小滚动贴底，选区 y=837–859，余量 61px（npp-04）。
   - seg4a 三拍：setInterval 六行块（npp-05）；id="subtitle" h2 选区 y≈668（npp-06）；
     回 let tick 行复用同锚点同视图。
   - seg6 七拍（s3 仅 45 行）：**开场 reveal 补了 scroll_anchor＝tl.seek(0)**
     （record_segments 已改，npp_ops 共享模块零改动）——无锚点时 L38 会被压到屏底、
     注释样例行出屏、第二拍还多一次滚屏；加锚后 npp-seg6-39 骨架四行（timeline/
     注释/注册/seek）一次同框、选区 y≈800。注释行（40）、title（41，长行横滚到
     `}, 2);` 完整）、card（42）、subtitle（43）均完整；注册行＋seek 收口（44）
     选区 y≈862–883 完整。card→subtitle 两拍视图零滚动（下一行已在屏内）。
   - 机检：每步 save 后读盘谓词全过；s0→s1、s3→s4 终态 live index.html 与 backup
     金标准**逐字相等**；check_anchors.py 复跑 31 项全 PASS、退出码 0；五脚本 py_compile 通过。
   - 锚点行号静态核对（check_anchors 覆盖）：KEYFRAMES 插 `#card {` 前＝L30；
     animation 锚 letter-spacing＝L56 后→L57；GSAP 注释 L39→title，card L40、
     subtitle L41、注册行 L42、seek L43。
9. ~~seg8 时长 48→58 静态精算~~ **已真机定量（2026-10-13 深夜）**：五步链
   `seg5_rehearse.py all` 实测 **open 4.8／split 4.5／zoom 3.6／seek 43.3／
   close 3.5＝59.8s**（优化前 IPv6＋短连曾达 157.5s；127.0.0.1＋player 长连
   后落 59.8s；其中截图 ra.screenshot 1920×1080 ≈1.04s/张、inject_once≈4.1s）。
   record 预算 **58→70s**（act 开头静场 1.2＋拖拽余量＋五步 59.8），尾帧停在
   j 的 seek(2.4) 半透明标题（设计如此，片尾静场剪辑掐尾；close 不回零）。
   十条 seek 已逐帧目验 33-a..j（命令带 `window.` 全称，与口播一致；时间点按
   新时长 1.4/0.5/1.2 反推）：**a=2.4 灰标题半透明浮半路／b=3 纯白标题就位／
   c=6.3 暗弱副标题半路／d=9 副标题清晰全就位／e=0 空黑台／f..j=2.4 五张与 a
   完全一致**（max-cell-delta=0；4×4 网格均值签名对小笔画不灵敏，c/d delta=0
   但肉眼明暗明确有差，以目验为准）。十条 getTime 断言 |got−expect|<.01 全 OK、
   focus 全程 DEVTOOLS-TEXT-EDITOR。

### A2. 段⑤a 实证工艺（2026-10-12 定稿，原「同秒三连拍」已证伪废弃）

- **粗稿旧 L27「同一秒连截三张、tick 三四各不同」是错的**：权威 s2 页串行
  snapshot 同一 t，三帧**逐字节相同**（全 tick 3，MD5 前缀 fb939dee9344）。
  分叉只在**并行抢 CPU**时出现——对应 render workers=auto 多 Chrome 工况。
- 入镜脚本＝`oneoffs/race_snapshot.py`（git 源），布景时复制为沙盒根
  `race-snapshot.py`，实拍只敲 `python race-snapshot.py`。两轮一镜到底：
  1. 排队轮：3 次串行 `snapshot --at 2 --no-end --no-browser-gpu`
     → `rec-shots/ser-1..3`，MD5 分组「1 种内容」；
  2. 一窝蜂轮：ThreadPool 6 路并发同命令 → `rec-shots/tk-1..6`，
     每 5s 心跳行（防 90s 死画面），收口「排队 1 种；一窝蜂 N 种」。
- 实测（probe-s2-three，s2 权威拷贝，闲机）：串行墙钟 46s（14–18s/路）、
  并发墙钟 47s、整段 94s；并发 6 帧 **3 种：tk-1/2=tick 4、tk-6=tick 6、
  tk-3/4/5=tick 7**（目验三代表帧确认；tick 7＝被挤最狠、截帧前墙钟已过 3.5s）。
  沙盒忙工况（Edge+dev server+用户在机）并发墙钟 95s、6 帧 5 种；
  种数随负载变化，**粗稿口播按正式 take 的终端分组回填，不钉死数字**。
- 若深夜实拍并发轮不幸 1 种（全同）：脚本会打印「全同」提示，重拍或
  临时 `-n 8`（命令变 `python race-snapshot.py -n 8`，时长近翻倍，慎用）。
- `for /L ... start /b` 一行流方案已废弃：管道/交互控制台实测子进程秒退
  （仅建奇数空目录、日志剩一个乱码字），Python ThreadPool＋shell=True
  （npx 是 npx.cmd）才是稳的。

### B. 正式录序（全部在 guard 下，单 take 可独立重跑）

`python record_segments.py seg1 seg2a seg2b seg3 seg4a seg4b seg5a seg5b seg6 seg7 seg8 seg9`
（分三批：① seg1 seg2a seg2b seg3；② seg4a seg4b seg5a seg5b seg6；③ seg7 seg8 seg9——
每批抽帧目验再往下。）
每个 take 后看 takes/<name>.mp4 抽帧（fps=1/4, scale=800），穿帮/误窗立即停跑排查。
seg5b 尾帧重点盯 npm run check 是否滚完（并发若超 26s 回 42 重录）；seg5a race 种数
按终端实际分组记录；seg9 尾帧确认出现输出路径行。
完成后：素材归位 media/、更新文章计时日志、报告总耗时。**不发布 B 站。**

### C. 当前现场（冻结时状态，开录前只读核验）

- dev server 3002 在跑；隔离 Edge CDP 9222 **只听 IPv4（必须用 127.0.0.1，
  localhost 走 ::1 白等 2s/次）**，tab 仅 2 个：Studio／裸 player；DevTools
  当前关态（seg8 脚本自行开/关）。工具栏「其他搜索框」热搜已关（edge-cdp
  profile 持久，重开 Edge 不复活；若换 profile 必须重关，见 A⑥）。
- index.html＝s4 正解态（**新时长 title 1.4／card 0.5／subtitle 1.2**，与
  backup/s4-final.html 逐字一致，五权威态 2026-10-13 已随编排更新）；
  index.start.html 若出现先删（lint multiple_root_compositions）。player
  停在 time=2.4（j 状态，seg8 布景 reload＋seek(0) 兜底）。
- seg5-shots/ 证据图：**28 为误拍用户 WT 的事故留档，含用户桌面，禁入 git**；
  30-open/31-split-fit/32-zoom/33-seek-a..j/34-closed 为 10-13 正式标定图；
  tab2-*/settings-* 为热搜开关处置留档（同目录，均不入库）。
- npp-shots/ 证据图（10-14 A⑧）：npp-01..06（seg2a/seg4a 六拍）、
  npp-seg6-38..44（seg6 七拍）；全屏截图 x>1600 含用户 WT 边缘内容，**整目录禁入 git**。
- 布景期临时产物（代录后清）：沙盒根 `race-probe-*`（忙工况验证残留）、
  `probe-s2-three`（独立实验项目，含 out-a/b/c、out-p1..6、rec-shots 证据，
  全流程结束后整个删）、`rec-render/`（A⑤ 定量产物 hf04-seek.mp4＋probe.mp4）、
  calib-timings.py 与 rec-shots/calib-timing*；`race-snapshot.py` 是 seg5a
  布景复制物，保留无害。oneoffs 下 probe_*.py／seek_api_probe.py 等一次性
  探针用完即删（以主控候删清单为准）。
- **2026-10-12 第二轮静态加固（用户在机、零桌面动作完成）**：① 终端启动加
  `--suppressApplicationTitle`（修 npm 改标题撞闸）；② seg8 48→58s（精算
  52.6s 旧值必截）；③ 帧命名/render `-o`/package.json 脚本静态坐实；
  ④ 装闸幂等运行时验证全 PASS（八原语、拦截实测）；⑤ check_anchors 21 项
  保持全 PASS；五脚本 py_compile 通过。
- **2026-10-12 第三轮静态加固（零桌面动作）**：抓出 seg6/_gsap_edits
  「编辑只改缓冲区、line_of 只读磁盘、中间漏 save」实拍必崩 bug，三处补
  save＋磁盘谓词；check_anchors 增 NppDiskModel 双态步进模拟器（三序列＋
  终态对备份），变异测试两连拦（删 save 即 FAIL）；seg6 46s 静态精算
  ≈32.4s/预算 43.8s，时长不动。开录前只剩 A 节实拍标定（用户离机后）。
- **2026-10-13→14 深夜真机标定（用户离机，A 节收口）**：① PLAY(775,428)；
  ③ snap_wait=20（真机三帧 14–17s）；④ check_wait=26（真机全绿 22–24s，
  ⚠️ 与 hf-03 并发 33–36s 记载有张力，正式 take 盯尾帧）；⑤ render 墙钟
  47.5s、worker headless 不弹窗，seg9 纳入 ALL_TAKES，render_wait=80 不动；
  ⑥ DevTools 新工艺整段重标定（见 A⑥，旧 SPLIT_Y/CONSOLE_Y/×4 全废）；
  ⑦ CDP 直连补物理置前/127.0.0.1/长连；⑨ 五步链真机 59.8s、record 70；
  编排入场时长定稿 1.4/0.5/1.2（seek 六演示点目验全符合），s4 金标准备份
  已同构重建（check_anchors 重跑全 PASS）。另：Edge 热搜开关脱敏已处置；
  A0 check_anchors 曾因 s4 备份仍旧时长拦 2 项，重建后全绿。
  **A 节九项真机标定全部收口（含 A⑧ NPP 13 图目验），A0 闸门 31 项 PASS，可以开拍。**
  ⑧ 补记：seg6 开场 reveal 加 scroll_anchor＝seek 行（唯一编排改动，npp_ops 零改动）。
