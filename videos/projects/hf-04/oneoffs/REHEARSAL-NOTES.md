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

1. **PLAY_X/Y 坐标**：`record_segments.py` 现沿用 hf-03 的 (775,487)。Studio tab 摆到
   (0,0,1600,920) 后截图实测 Preview Play 按钮中心，不符就改常量再录 seg1。
2. ~~snapshot -o 自建目录~~ **已静态坐实（2026-10-12）**：0.8.107
   `snapshot-MSGC7HTA.js:315` `mkdirSync(snapshotDir,{recursive:true})`，
   -o 不存在自建，无需脚本兜底。
3. **snapshot 实拍耗时**：三帧 `--at 2.1,2.5,2.9 --no-end` 在 TTY 空跑计时一次，
   回填 snap_wait（预算 13–14s/次，seg3 两轮）。帧命名已静态坐实
   （snapshot-MSGC7HTA.js：`frame-${i pad2}-at-${Number(t.toFixed(3))}s.png`，
   i 从 0 每时间点一帧）→ seg3 fc 路径 `frame-00-at-2.1s.png` 正确；
   race 单点 --at 2 → `frame-00-at-2s.png` 与脚本校验一致。**seg5a 已不用单帧轮**，
   改跑 `python race-snapshot.py`（见下「段⑤a 实证工艺」），TTY 计时整段
   回填 race_wait（闲机实测 94s，默认预算 150s）。
4. **check 实拍耗时**：s2 页 TTY 下计时，回填 check_wait（预算 42s）。
5. **render 实拍耗时**（seg9 定量）：`npm run render -- -o rec-render/hf04-seek.mp4`
   非录屏空跑计时（预算 80s），决定 seg9 是否进 ALL_TAKES 及 render_wait。
   命令合法性已静态坐实：package.json 有 check/render 脚本（npx 透传 `--`），
   render-EXSRG666.js 官方示例 `render -c ... -o intro.mp4` 同形。
6. **DevTools 分隔条/控制台坐标**：seg5 open→split→zoom 分步跑，目验 30/31/32 截图：
   分隔条 SPLIT_Y=700、控制台行 CONSOLE_Y=830、Ctrl+=×4 字号；坐标不符就地改常量。
7. ~~裸 player 窗标题匹配~~ **已改 CDP 直连（2026-10-12）**：prep_window 按
   `find_page(PLAYER_NEEDLE)` 的 URL 认 tab（preview 页 `<title>` 不含 URL，
   旧标题匹配＋前台 fallback 会在同进程 Studio tab 误开 DevTools），激活后
   以前台 pid==cdp_pid 过闸。tab 缺失自动 ensure_tabs 建齐，不 reload/seek。
   彩排首跑目验：open 后 DevTools 确实开在裸 player tab 而非 Studio。
8. **npp_ops 跨集复用**：锚点行号已静态全量核对（check_anchors.py 21 项 PASS：
   KEYFRAMES 插在 `#card {` 前＝s1 第 30 行；animation 行锚 letter-spacing（第 56 行后）；
   GSAP 注释行 L39→TT_TITLE；三条 fromTo 单行尾锚 `}, 2/3/6);`＝L39–41；注册行 L42）。
   首次 reset()/build_s1 真机仍盯 launch/set_zoom/close 与 scroll_anchor 垂直取景效果
   （SETSEL 跨进程通道 hf-03 实测有效，本集新增的 scroll_anchor 拍法需目验块体同框）；保存后读盘校验。
9. **seg8 时长已静态上调 48→58s（2026-10-12）**：逐段精算 act 内部——
   5 次 prep_window（CDP activate＋sleep 1.2＋move/activate）≈1.7×5＝8.5s、
   open 2.5、split 4.1、zoom 2.9、seek 十条×≈3.2（打字 25 字符×.05≈1.25＋
   等 1.2＋证据截图 .4）≈32、close 1.5，合计 ≈52.6s，旧值 48 必截 close。
   彩排实测一轮后回收（截图耗时是唯一未定量项），尾帧 DevTools 关闭画面，
   长了剪辑掐尾即可。十条 seek 画面逐帧看 33-a..j
   （命令已带 `window.` 全称，与口播一致）：
   2.4 半透明半路／3 标题就位／6.3 副标题半路／9 全在／0 空舞台／**2.4×5 五张全同**
   （粗稿「连着五回 seek 同一个二点四，五回画面一模一样」）。

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

`python record_segments.py seg1 seg2a seg2b seg3 seg4a seg4b seg5a seg5b seg6 seg7 seg8`
（先分段：seg1→seg2b→seg3 一批，seg4*→seg5* 一批，seg6→seg8 一批，每批抽帧目验再往下。）
每个 take 后看 takes/<name>.mp4 抽帧（fps=1/4, scale=800），穿帮/误窗立即停跑排查。
完成后：素材归位 media/、更新文章计时日志、报告总耗时。**不发布 B 站。**

### C. 当前现场（冻结时状态，开录前只读核验）

- dev server 3002 在跑；隔离 Edge CDP 9222（IPv6 only），tab：Studio／裸 player（带 fit 注入）／
  DevTools 底停靠残留（seg8 脚本会先 Ctrl+Shift+J 关掉再开）。
- index.html 保持 s4 正解态；backup/ 五权威态不动；index.start.html 若出现先删（lint multiple_root_compositions）。
- seg5-shots/ 17–34 证据图勿删（28 为误拍用户 WT 的事故留档）。
- 布景期临时产物（彩排后清）：沙盒根 `race-probe-*`（忙工况验证残留）、
  `probe-s2-three`（独立实验项目，含 out-a/b/c、out-p1..6、rec-shots 证据，
  全流程结束后整个删）；`race-snapshot.py` 是 seg5a 布景复制物，保留无害。
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
