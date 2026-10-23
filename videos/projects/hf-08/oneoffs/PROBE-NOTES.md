# hf-08 前制真机探针台账：render 把网页烤成 MP4（0.8.107，2026-10-21）

> 目的：开拍前把 `render` 在 0.8.107 的真机行为摸清——确定性、烤片流水线、
> 两条捕获路径、worker 决策、门控与失败行为。全部命令实跑，数字附日志出处。
> 主沙盒工程：`projects/av-sync-calib`（13s／390 帧／黑底＋5 白闪，仓库内标定片）；
> 产物与日志：`F:\_hftest\hf08-probe\`（仓库外）。
> 环境：Node v24.6.0／npx hyperframes@0.8.107（latest 0.8.181，**全季钉死不升**）／
> FFmpeg 7.1.1／HeadlessChrome 152.0.7977.30／UHD 620 驱动 D3D11／16GB RAM／8 逻辑核。

---

## 0. 结论先行（喂口播）

1. **render 是逐字节确定的函数**：同一工程、同版本、同 GPU 模式，连跑两次
   整文件 sha256 相同；与 2026-10-15 历史产物跨 6 天重跑**仍然相同**；
   软件 3-worker、软件 1-worker、硬件 drawElement 三条路径六个文件
   **全部同一个 sha256**（`2057d037…c6c5a83`，61145B）。容器层不写
   可变时间戳，像素流 md5 也全等。绑定条件：同输入素材＋同 CLI 版本。
2. **烤片流水线（--debug 实物解剖）**：compiled/index.html（编译后工程＋
   summary.json 媒体清单）→ capture-calibration（真开一次浏览器，采样
   第 0/97/195/292/389 五帧量 p95 抓帧耗时）→ N 个 Chrome worker 逐帧
   seek＋截图 → captured-frames/frame_000000.jpg…390 张 → video-only.mp4
   → 与 audio.m4a 合成 output.mp4。`--format png-sequence` 可直接停在
   「390 张 PNG＋audio.m4a」一步（3.2MB vs MP4 59.7KB）。
3. **两条捕获路径（本集教学主轴）**：
   - **软件路径**（`--no-browser-gpu`，SwiftShader）：screenshot capture
     （Page.captureScreenshot），多 worker 各启 Chrome **分帧段并行抓盘**
     （capture_disk），抓完再统一 encode；
   - **硬件路径**（`--browser-gpu`，UHD620 D3D11 真机 probe 通过）：
     drawElement capture（CDP 直接读 DOM 合成），本机恒为 **1 worker**
     边抓边流式编码（capture_streaming）——长片由 deInversion 反转钉 1
     （实测单 worker 全面更快），并行 router 被 24GB 内存地板关在门外。
   - 13s 小工程墙钟：软件首跑 68.1s（校准占 16.4s）／软件热跑 55.7s／
     硬件 52.4s。小工程差异被校准/启动吃掉，**长片才见路径差距**（引 hf-07 账）。
   - 【hf-08 入镜口径 2026-10-23】分镜软件路两段录屏（rec-sw1/2）取自**热态
     演录**母带（连续开机 26h 后，用户拍板不重启）：ENTER≈11s、banner≈30s、
     calibration 134–152s、worker 配置 153–158s，母带 160s 停录时正式 capture
     未开始，**尾报不入镜**。口播「首跑六十八秒／开浏览器试截几帧十六秒」
     仍以上行冷态探针台账（68.1s／setup 16.4s）为事实依据，数字与文案不动；
     热态母带只承担操作过程重演（代录重演体例）。rec-sw2 窗口 153.8–158.6s
     给出 workerCount:3／streaming-encode gate enabled:false reason
     multi_worker／forceScreenshot:true／useStreamingEncode:false／
     0/3 ready／swiftshader launched 的字面证据，与「三家交活再统一编码、
     不能边截边编是门控」逐句对应。
4. **worker 数是算出来的，不是拍的**（dist 源码）：auto 取
   min(CPU 核−2, 内存50%÷1536MB, 帧数÷30, heap 账) 再被 contention 规则压；
   本机 16GB／8 核 → cpu6／mem5／frame13／heap5，13s 工程 contention 压到 **3**。
   帧数 <60 直接 1 worker（too_few_frames）。drawElement 路径与低内存模式
   （总内存 ≤8GB 自动）硬钉 1 worker。
5. **render 自带 lint 但默认不拦**：有 error 也继续烤（exit 0 出片），
   墙钟动画真的会被烤进 MP4（实测红块 1s 帧 x=246、5s 帧 x=966）；
   `--strict` 才在 lint error 时中止（exit 1 无产物）。所以 **check 0 error
   是流程纪律，不是 render 的强制前提**。
6. **best-effort 不是什么都放**：缺音频源时默认模式照样 exit 1——输出会
   缺一条音轨（video-only）属正确性错误，不是 readiness 警告。
7. 无 `window.__timelines` 注册又没标 `data-no-timeline` 的工程，producer
   轮询时间轴注册最多 45s（playerReadyTimeout），**白等 45s**（warning 明说）。

## 1. 命令面（render --help 实测要点）

- `render [DIR] -o out.mp4`；`-c/--composition` 指定子合成；`--format`
  mp4/webm/mov（透明）/gif/png-sequence/hls；`-f/--fps`（默认取 root data-fps
  否则 30，支持 30000/1001）；`-q/--quality` draft/looks(默认 CRF16)/delivery。
- `-w/--workers` 数字或 auto（每 worker 一个 Chrome 进程，约 256MB 起）；
  `--browser-gpu` / `--no-browser-gpu`（auto 首启 probe，失败回退软件）。
- `--strict`（lint error 即败）／`--strict-all`（warning 也败）／
  `--no-best-effort`（媒体未就绪即败）。
- `--video-frame-format auto|jpg|png`（UI 录屏/色敏素材用 png）；
  `--resolution landscape-4k` 等（Chrome 提 DPR，比例须同、整数倍）。
- `--variables/--variables-file/--batch`（变量化批量出片）；
  `--resume/--keep-segments`（分段捕获复用）；`--debug`（保留全部中间件，
  落在 npx 包目录 `.debug/<jobId>/`）。
- `--frames-cache-dir`：源视频抽帧的**内容寻址缓存**（默认 tmp 目录，
  C 盘紧张可重定向；off 关闭）。
- 超时三件套：`--browser-timeout`（page.goto，默认 60s）／
  `--protocol-timeout`（CDP，300s）／`--player-ready-timeout`（就绪轮询 45s）。
- 环境开关：PRODUCER_BROWSER_GPU_MODE、PRODUCER_LOW_MEMORY_MODE、
  PRODUCER_CORES_PER_WORKER（默认 2.5）、PRODUCER_MIN_PARALLEL_FRAMES（120）、
  HYPERFRAMES_EXTRACT_CACHE_DIR 等。
- render 结尾自报钉版过期：`This project pins hyperframes@0.8.107 (latest
  0.8.181)`——不升级（像素不保证跨版本一致，全季可复现性优先）。

## 2. 确定性实验（本集最硬证据）

工程 av-sync-calib，同一条命令仅改输出名，全部 390 帧：

| 跑 | 命令要点 | 墙钟 | 产物 sha256（前8位） |
|---|---|---|---|
| 2026-10-15 旧档 | 历史 body.mp4 | — | 2057d037 |
| run-a | --no-browser-gpu（3 worker） | 1m8.1s | 2057d037 |
| run-b | 同上 | 55.7s | 2057d037 |
| w1 | --no-browser-gpu -w 1（streaming 开） | 50.7s | 2057d037 |
| hw-a | --browser-gpu（drawElement 1 worker） | 52.4s | 2057d037 |
| hw-b | 同上 | 54.1s | 2057d037 |

三层校验全一致：整文件 sha256＝`2057d037…c6c5a83`；视频压缩流
`ffmpeg -c copy -f md5`＝b55c5ad2…；解码逐像素 yuv420p rawvideo
md5＝fb0c5653…；音频流 md5＝42de6ec9…。

**口径注意（写稿/录屏引用边界）**：本工程内容极简（纯黑＋3 帧白闪），
证明的是「同一渲染路径帧位置由 seek 时间码唯一决定、编码与 mux 不带入
随机量」。复杂工程跨软件/硬件路径的像素级一致性本次未做全样本比对，
口播不断言「任意工程软/硬件逐字节相同」，只断言「同参数重跑逐字节相同」。

## 3. 烤片流水线（--debug 目录实物）

`.debug/<jobId>/`（在 npx 缓存的 node_modules 下）：

```
compiled/index.html + summary.json   编译后工程；summary 列尺寸/13s/videos[]/audios[]/renderModeHints
capture-calibration/                 校准会话（真浏览器采样 5 帧量耗时）
capture-attempt-0/worker-0…2/        每 worker 一个 Chrome，领一段帧号
captured-frames/frame_000000.jpg…    汇合后 390 张 JPG（6 位编号，0 起）
audio.m4a / audio.duration-normalized.m4a   音频处理＋时长归一化
video-only.mp4                       390 JPG → 无声 H.264（37157B）
output.mp4                           video-only＋audio mux（61145B，与正式产物同 hash）
perf-summary.json + render.log       阶段账与全量 trace
```

- 帧内容真确性已像素验证：frame 89 mean=0、**90/91/92 mean=255**
  （t=3.000–3.066s 三帧白闪精确）、93 归 0。
- 静态均匀画面 JPG 体积巧合相同（黑帧/白闪帧均 12998B），不要拿文件大小
  判帧内容，以像素为准。
- png-sequence：`--format png-sequence -o <dir>` 产物＝390 张 frame_XXXXXX.png
  （1 起编号）＋audio.m4a，共 3.2MB，encode 仅 0.4s（不封视频流）。
- perf-summary.json 关键字段：compositionHash（内容指纹）、totalElapsedMs、
  stages{compileOnly,browserProbe,compile,videoExtract,audioProcess,
  capture{captureFrame,captureSetup},encode,assemble}、workerSizing、
  captureCalibration{sampledFrames,p95Ms,multiplier}、tmpPeakBytes。

## 4. 两条捕获路径详账

### 4a. 软件 screenshot 路径（run-a，3 worker）

- 浏览器：`HeadlessChrome/152.0.7977.30 … gl=--use-gl=angle
  --use-angle=swiftshader`，captureMode=screenshot／captureScreenshot。
- 阶段：compile 0.6s · extract 0.0s（无源视频）· audio 0.9s · probe 0.2s
  · setup 16.4s · capture 33.6s · encode 14.2s · assemble 1.9s。
- setup 大头＝capture_calibration 15.1s（另起校准浏览器，goto→GSAP proxy
  flush→pollHfReady→时间轴/媒体/字体就绪→采样 5 帧）；热跑 setup 5.5s。
- trace 关键门：`streaming-encode gate enabled:false reason:"multi_worker"`
  → 多 worker 只能抓盘后统一编码；单 worker 时
  `enabled:true reason:"single_worker"`（另有 240s 时长闸 maxDurationSeconds）。
- initSession 序列（每 worker 每次导航）：page.goto → GSAP proxy flush →
  pollHfReady → pollSubCompositionTimelines → applyVideoMetadataHints →
  media+fonts+tailwind ready → static-frame dedup 判定
  （av-sync 无 GSAP tween，disabled；梁武片曾复用 57/3682 静帧）。

### 4b. 硬件 drawElement 路径（hw-a，1 worker）

- GPU probe：`browserGpuMode probe → hardware (ANGLE Intel UHD Graphics
  620 D3D11)`；captureMode=drawelement／captureOperation=drawElement，
  phase=capture_streaming，workerCount=1。
- 阶段：compile 0.5 · audio 0.7 · probe 0.2 · setup 8.9
  · **capture 40.5s 与 encode(during capture) 40.5s 完全重叠** · assemble 1.6。
- 帮助文案称 fast capture「macOS + hardware-GPU」才可 engage，**实测
  Windows＋UHD620＋152 版 Chrome 已 engage**（文案滞后，以真机为准）；
  不兼容构图与自校验失败会自动回退 screenshot。
- 长片实例＝hf-07：16777 帧 drawelement 单 worker，capture 本体
  2349.4s（≈7.1 帧/s）、墙钟 2436.3s、总 41m43.3s。

> 术语澄清：日志 `htmlInCanvasDetected:false` 与 captureMode=drawelement
> 不矛盾。drawElement 是 CDP 直接读取 DOM 合成的常规硬件捕获；
> htmlInCanvas（drawElementImage）是 HTML 被画进 canvas 的特殊构图
> （另走一条硬钉 1 的分支）。hf-07 是普通 drawElement，不是 htmlInCanvas。

### 4c. worker sizing 源码（chunk-D5EJCP26.js computeWorkerSizing ＋ chunk-3WG63KFW.js 路由）

常量：MEMORY_PER_WORKER=1536MB（内存预算取总量 50%）、HEAP_PER_WORKER=640、
HEAP_RESERVED=1024、MIN_FRAMES_PER_WORKER=30；CPU 账＝逻辑核−2；
coresPerWorker=2.5；minParallelFrames=120；largeRenderThreshold=1000。
- 帧数 <60 → 1（too_few_frames）；optimal=min(cpu,mem,frame,heap)；
  大渲染再按 cpuCount÷(2.5×成本倍数) 压（boundBy=contention，本机即此）。
- **钉 1 的分支不止两处**（按 0.8.107 源码）：
  1. htmlInCanvas 构图（drawElementImage 路径，日志「pinning to 1
     worker (Chrome concurrency limitation)」）；
  2. 低内存 profile（总内存 ≤8GB 自动或 --low-memory-mode）；
  3. **drawElement 反转 deInversion**：硬件捕获下 ≥900 帧
     （HF_DE_SINGLE_MIN_FRAMES 默认）且单 worker streaming 可用时，
     源码认定「实测每个 worker 数下单 worker 都更快」，把算出的多 worker
     反转钉 1，日志原文「Fast capture: single-worker drawElement streaming
     preferred over N-worker screenshot capture … measured faster at every
     worker count」；短工程另有 ≥250 帧 short-band（元素数门槛 2500）。
  4. 显式 `-w 1`；OOM/静默 worker 退出重试也钉 1。
- **多 worker drawElement 确实存在（parallel router，钉死 3 worker 并发
  硬件 Chrome）**，但 `shouldPreferParallelDrawElement` 有 RAM floor
  **24GB**（HF_DE_PARALLEL_MIN_MEM_MB 默认 24576）＋≥700 帧双门槛。
  源码注释自述原因（CLI 0.7.52 事故）：16GB 机器上三个并发硬件 Chrome
  烤出过**竖直黑条**——GPU/内存压力下合成器 tile 被驱逐，自校验采样可能
  漏检局部损坏；故地板以下「只扣下并行这一注，单 worker inversion 照常开」。
  本机 16GB → deParallelRouterEligible 恒 false（hf-07 日志该字段即此）。
- captureCost multiplier：shader 转场 +2、rAF +1、iframe +0.5，
  贵帧构图自动降 worker 防 Chrome 合成器饿死；校准实测 multiplier 可覆盖静态估计。
- 内存耗尽类失败有「静默 worker 退出」检测，报错直接建议 --workers=1 隔离。
- **教学口径**：本机（16GB/无独显）上「硬件路径＝1 worker」不是 Chrome
  玄学，而是三层明确规则——帧段太短不值得并行、长片单 worker 实测更快、
  并行赌注被 24GB 地板关掉（黑条事故的遗产）。

## 5. 门控与失败三实验（F:\_hftest\hf08-probe 坏工程）

### E1. lint error 默认照烤，--strict 才拦（bad-lint/，6s 红块 rAF 工程）

- lint 原文：`✗ requestanimationframe_in_composition: requestAnimationFrame
  runs on wall-clock time, not the GSAP timeline … may cause flickering or
  missed frames during rendering. Fix: Use GSAP tweens …`
- 默认 render：`Lint: 2 error(s), 1 warning(s) … Continuing render despite
  lint issues`，exit 0，产物 24527B；抽帧量红块质心：**第 30 帧（1s）
  x=246、第 150 帧（5s）x=966**——墙钟动画真的进了 MP4（呼应 hf-07：
  render 忠实烤每一帧，好坏照烤；check 是人事门控）。
- `--strict`：exit 1 `Aborting render due to lint issues`，无产物。
- 第 2 个 warning（本工程无时间轴）：`missing_data_no_timeline … producer
  polls for timeline registration for up to 45 seconds … Add data-no-timeline`
  ——纯静态/非 GSAP 工程记得标 data-no-timeline，每 render 白省 45s。

### E2. 缺音频源：best-effort 也拦（missing-media/）

- audio src=media/nope.wav：lint 3 error 2 warning 后继续进管线，
  capture 完成后 `[WARN] Audio track failed … reason:source_not_found …
  Render blocked by 1 correctness warning: audio_processing_failed: Audio
  mix failed; output would be video-only`，**exit 1**；
  `--no-best-effort` 同样 exit 1（仅 strictness 字段不同）。
- 教学口径：best-effort 容忍的是「就绪度警告」，输出少一整条轨道这种
  正确性问题不免考。

### E3.（待录屏时补）真实长片 render 启动行/Timing 报告

终端实拍素材：av-sync 短工程全流程（启动→进度→Timing 一行）已可录；
hf-07 的 41 分钟长 render 不重跑，录「启动命令＋Timing 报告」两端
（报告数字以 hf-07 build/render.log 为准，必要时 freeze 补拍）。

## 6. ★ hf-07 旧账勘误：worker=1 不是因为含视频

文章计时日志 hf-07 节现写「worker=1（含视频元素的工程降到单 worker）」，
与源码/真机不符，hf-08 探针反证：

- hf-07 build/render.log 真机字段：browserGpuMode=**auto→probe hardware**、
  captureMode=**drawelement**、capture_streaming、workerCount=1
  （htmlInCanvasDetected 校准字段另算）；
- av-sync 工程**无任何 video 元素**，hardware 跑同样 1 worker；
- 源码里 worker 决策不看 videoCount（videoCount 只影响
  captureBeyondViewport=true 与抽帧/音轨处理）。
- 正确归因：**hardware GPU probe 通过 → drawElement 硬件捕获 → 16777 帧
  ≥900 触发 deInversion（单 worker streaming 实测全面更快），而并行
  drawElement router 又被 24GB 内存地板关掉（本机 16GB，CLI 0.7.52 竖直
  黑条事故遗产）→ 钉 1 worker**。视频元素影响的是 video_extract 抽帧段
  （hf-07 该段 35.7s/11 源视频/2090 帧）与每帧 currentTime seek，
  不决定 worker 数。
- 处置：hf-08 PR 中顺手勘误计时日志该句（video 元素不背锅；真因＝
  drawElement inversion＋24GB router 地板）。

## 7. 对分镜/录屏的约束（喂 STORYBOARD）

1. 主视觉公式候选：一条时间轴帧序列 0…389 ＋ Chrome 图标/烤炉意象；
   「同一份 HTML，烤多少次都同一个 sha256」是本集金句候选。
2. 终端实拍全部真机：render 进度条＋Timing 行、--debug 目录树、
   390 张 JPG、sha256 三连、--strict 拦截、缺音轨拦截。
3. 两条路径用同一工程两次 render 的 Timing 行并排（screenshot 多 worker
   vs drawelement 1 worker streaming），不后期伪造。
4. 长 render 用 hf-07 真实日志/数字（16777 帧、41m43s、7.1 帧/s），
   现场只跑 13s 工程，避免录屏等一小时。
5. worker 决策用「算账卡」：cpu−2=6／内存 5／帧 13／heap 5→contention 3；
   钉 1 的两条件单独成卡。
6. check 段与上集衔接一句话：check 管「该不该烤」，render 管「烤得准不准」。

## 8. 未探项（用到再补）

- `--docker` 确定性容器（本机不用 Docker，口播不提或一句带过）；
- HLS/分片 `--resume`、`--batch` 变量矩阵（本集工程不用）；
- HDR/4K 路径、MOV 透明、WebM；
- 复杂工程（字体/CSS 渐变/阴影）软/硬件像素差异——不断言跨路径逐字节；
- OOM 实操复现（16GB 本机难自然触发；只讲 sizing 账与 --workers=1 退路）。
