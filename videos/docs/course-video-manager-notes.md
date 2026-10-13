# 调研笔记：mattpocock/course-video-manager 对本流水线的借鉴

> 调研日期：2026-10-13。仓库：<https://github.com/mattpocock/course-video-manager>（805★，2025-07-24 建仓，调研时活跃提交中；TypeScript/Turborepo，2104 文件，无 license）。
> 本地浅克隆：`F:\_hftest\ref\course-video-manager`（只读参考，不在任何项目内）。
> 调研方式：三路 agent 并行深读源码/ADR/GLOSSARY，下为综合笔记，供 hf-04 之后的管线改造取用。

## 0. 一句话定位

Matt Pocock（Total TypeScript）给自己课程业务建的「课程视频发布工厂」：Postgres 域库（Drizzle）＋ React Router 本地全栈应用 ＋ 常驻 recorder/sidecar 进程 ＋ 本地 faster-whisper ＋ Remotion overlay 渲染器 ＋ Dropbox 不可变发布 ＋ 给 AI agent 用的 `cvm` CLI 与标签驱动的自治工作流（.sandcastle）。

**架构层面（公司级全栈）对我们个人本地 Python 深模块＋git 是过度投资，不学；工艺层有大量同构问题的成熟答案，按下面清单取用。**

## 1. 创作流域：值得知道的实体与机制

域语言单一真源是根目录 `GLOSSARY.md`（每个术语带 _Avoid_ 禁用词），CLI help 文本手工与其保持同步。

创作序：**Learning Goal**（Section 级先写、有优先级，Beat 反向挂接）→ **Beat**（录前规划单元，6 kind：Definition/Walkthrough/Playthrough/Quest/Reaction/Setup，Setup 是制作备注永不发布）→ **Clip Mockup**（录前定死的「一静图＋一句口播」，两者必填）→ Script → 录制 → Transcript → **Body**（发布正文）。

- **Animatic（预审片）**：mockup 静图来自 agent 写的 HTML 文件，Playwright headless Chromium 截 1920×1080 PNG（8 页并发）；CLI 只收图片不收描述，逼 agent 真建画面，缺图显红底「frame missing」。语音是 Kokoro TTS job。Remotion `<Series>` 按「口播时长＋0.08s gap」排时间轴，下一镜 premount 0.5s 防黑帧。**未合成的句用词数回归估时长：1.65s＋0.337s/词（5088 条样本最小二乘，`estimate-spoken-seconds.ts`）**。
- Chapter（成片时间轴分隔符，1:1 YouTube 章节）与 mockup 共享一条 fractional order 空间、隐式归属（上方最近 chapter），插入不扰动其他行。
- Comment 钉在单个 mockup/chapter 上；**不进提词器**（提词器只读 Script），关于文章的 comment 是唯一可越过 Transcript 给写作模型的指令。
- **Teleprompter**：只显示 title＋Script，秒级轮询热更新；Script 解析 heading/para/cue（`[方括号即兴提示]` 不念）/list/code/instructions（`<instructions>` 教师备注不念）；右上角常驻「刚录 Clip 的真实 Transcript」对照说出口的 vs 想说的。
- **Article writer**：保真阶梯喂模型、每源可开关并显示 token 数（Transcript 是最高事实裁决者，另有 Script/Beats/Animatic 文本/Diagram 内联/course memory）。模型在正文里吐 `<ChooseScreenshot clipIndex={N} alt="…"/>` 占位符，UI 在**真实 footage 上逐 clip 帧步进让人选帧 capture**——模型不瞎编时间戳（印证我们 F2「沿时间轴定位韵腹」教训）。
- **警告三层（全部派生不存储、纯函数）**：
  - 规划警告：Beat 不挂 Learning Goal / Goal 无 Beat（琥珀三角，永不阻塞，section-lint 退出 0 只报 findings）；
  - 创作警告：missingBody/missingDescription/missingChapters/duplicateQuizId（行内徽标＋课程树总数徽标）；
  - 发布硬阻断：角色组合非法、shipping 视频缺 clips/正文/简介（service 层抛错，绕 UI 也守得住）。

## 2. 视频工程子系统

### 2.1 录制（recorder-service，不经 OBS 的主路线）

- 常驻 WebSocket 服务，直接起 ffmpeg 录三路 `screen.mkv/camera.mkv/mic.mkv`（dshow＋ddagrab），Windows wallclock 打时间戳共享一条时间轴；record 命令必须带 calibration 否则拒绝。
- **录 MKV**：崩溃产生无 duration 的 MKV，用 `ffmpeg -c copy` remux 修复，原件留 `.raw.mkv`（我们录 mp4 崩溃即废，可学）。
- OBS 只是横屏老路线：obs-websocket 连接，强制切专用命名 profile「Landscape Recording」（缺失报错让人手动建，录制中不切）——隔离理念与我们便携 NPP/隔离 Edge 相同，实现是「独立 profile」而非改用户配置。

### 2.2 转录

- 唯一引擎本地 faster-whisper（ADR 0033）：large-v3-turbo/CUDA float16/batched 8/en/word_timestamps（**我们无独显，模型档不可学**）。常驻 Python worker 子进程，模型驻 VRAM、空闲 10 分钟卸载、串行、预取；venv 与模型在 `~/.cache/cvm/whisper`，`pip --require-hashes`。
- **切块**：抽 mono 64kbps mp3、≤25MB 一趟；超长以静音点切（目标 27 分钟、允许 0.5–1.5×、取最接近目标的静音点，绝不切词中），逐块转录加 offset 合并。
- **缓存键＝源文件流式 SHA-256 的 sidecar JSON**（非路径/mtime），换文件自动失效；chunk 计划与结果存 `.transcript.partial/<hash>/`，重启断点续转。
- 人工修订很弱：词只支持整组替换＋重转，无逐词编辑器。中文同音错字场景我们应做得比它好（整句重合成工艺已有，见 hf-03 PR#122）。
- word 五态可抄：transcribing / has-words / failed / nothing-to-time / missing。

### 2.3 ⭐ 音画校准（av-calibration＋clap-detection）——我们 time_offset 的系统化答案

- 标定片：10s 静音 → 5 次拍手 → 5 句朗读/停顿 → 1 句大喊。
- 第二趟 ffmpeg：astats 测底噪、ebur128 测语音积分响度（目标 −27 LUFS±2）与排除掌声窗的 true peak（≤−6 dBTP），静默阈值＝语音−16dB（clamp −45～−30）。
- **Mic Offset 量化算法**（`packages/clap-detection/lib/`）：
  - 音频端：mic 解 48kHz f32le PCM，onset＝5ms 内升 20dB、100ms 内衰 15dB（`audio-onsets.ts`）；
  - 画面端：camera 走 signalstats 运动检测，在 onset ±0.3s 内找手部运动 burst 骤停的接触帧（亚帧插值，`match.ts`）；
  - `micOffsetMs = median(video − audio)`，**≥3/5 配对且 spread ≤ 一帧（33.4ms@30fps）才通过**；mic 启动数字静音 gap ≥20ms 判不可信；
  - 通过后**绑定设备名、7 天有效**（ADR 0038），offset 在切段时让 mic 起点提前（`clip-segment-args.ts`）。
- 我们的适配版（无摄像头、纯屏录＋TTS）：做 3–5 个「窄脉冲 BEEP＋全屏白闪」的 HyperFrames 标定片，成片后能量检测找声音时刻、帧亮度突变找画面时刻，取中位数，要求同样的配对比与 spread 门限；另做 finalize 前后两版标定，可**拆分 TTS 前置延迟与拼接延迟**，替代每集 onset 试错（0.28/0.37/0.29）。

### 2.4 Overlay 渲染与缓存

- `packages/overlay-renderer`：Remotion 4.0.347 独立包（自带 Chromium，不进主依赖图、不进应用 CI），主应用 shell out 调 `bin.mjs`（不 import 渲染路径）。渲透明 ProRes4444 .mov，1920×1080@60，一个 composition 覆盖 subtitles/CTA（竖屏）/Definition Card/Bullet Panel。
- **缓存键**＝`sha256({v: OVERLAY_RENDERER_VERSION=2, 标题/描述/bullets/revealAt/动画开关…})` 前 32 位，文件 `{courseId}-{hash}.mov`，存在即命中、无索引；写 `.partial` 后**原子 rename**。
- 合成单趟 `filter_complex`：每段 mov `setpts` 平移＋`overlay enable=between()` 链式叠加。
- **三级版本号分离**：EXPORT_VERSION（ffmpeg 设置）/ OVERLAY_RENDERER_VERSION（卡片样式）/ OVERLAY_CAMERA_VERSION（transform 算法）互不连带。
- Clip Zoom 是 115% 静态 crop；与 bullet panel 横移叠加被 guard 拒绝（互斥镜头运动有静态闸——思路同我们的 StaticGuard）。

### 2.5 ⭐ Export Hash：两层内容寻址的增量导出

`app/services/export-hash.ts`：

- 成片名＝`sha256({v: EXPORT_VERSION=1, fmt, clips:[{f:源路径,s,e,长暂停,缩放,overlay数组,micOffsetMs,均衡器,布局版本…}]})` 前 32 位，输出 `{courseId}-{hash}.mp4`，**文件存在即跳过整段导出**；
- 默认值字段一律省略（加新特性不使旧缓存失效）；overlay 数组先排序消除 DB 顺序影响；
- 按全版本有效哈希集合 GC 旧文件。
- 发布层另有区分（ADR 0027）：**Bundle 地址按配方指纹，传不传按真实字节哈希**——截断/损坏文件会被重传。
- 我们的映射：成片 hash payload＝分镜序列＋cues 文本与时间＋每镜 TTS 音频内容 hash＋time_offset＋HyperFrames/渲染器版本；改一句旁白只重渲一镜（分段 encode＋stream-copy concat 天然支持）。

### 2.6 ffmpeg 工程手法（`services/ffmpeg-*.ts`）

- **重编码并发槽默认 2**（实测百输入 concat 峰值 ~10GB RSS，6 并发 OOM 杀死全机）；另有 CPU 槽 12；排队/获槽都记日志含等待时长。
- `-progress pipe:1` 解析 `out_time_us` 出单调百分比（clamp 99）。
- stdout/stderr 并发抽干（防 64KB 管缓冲死锁），逐 chunk 异常隔离；stderr tee 终端同时留 8000 字符有界 tail 入错误与日志。
- NVENC 失败自动整遍 libx264 回退；fiber 中断杀子进程；**父进程 exit/SIGINT/SIGTERM 时 SIGKILL 全部孤儿**（child-registry）。
- 每 Clip 单独编码再 stream-copy concat，进度按时长加权。

## 3. 发布流

- 阶段：validating → freezing（Submit 纯 DB 事务：Draft 冻结为 **Pending Version** 拒写，同时克隆新 Draft 继续编——渲染途中改稿不作废）→ cloning → exporting（最长片先编码）→ uploading → complete。
- **Bundle**＝自包含不可变发布物，地址 `versions/{sha256(versionId)16}-{sha256(recipe)32}/`，**编码前即知地址**；根 `course.json` 最后原子覆写，是「当前版」唯一 marker，落地后才 Promote。
- **崩溃恢复**：比对根 course.json 的 versionId 判 committed/absent；reuse-plan 读上一版 manifest 建「字节哈希→文件」表，命中走 Dropbox `copy_batchv2` 服务端拷贝（0 出网），失败回退真传。中途停止的发布绝不 resume，留下 Pending Version 等人 Promote/Discard。
- **Readiness 四清单**：三张阻断（课/视频 lint 警告、角色组合非法、shipping 视频缺 clips/正文/简介），一张不阻断（unexported——发布命令自己渲染，只报 exportsRequired）。
- Lesson 三种命运：ships 完整发布 / Placeholder（只发标题占位，保持身份将来替换而非重复）/ withheld（不发且必带原因）。
- **长任务 sidecar**：独立 Node 进程＋Unix socket＋租约单实例＋崩溃退避重启。Job＝DB 一行＋事件；default/publish 两车道（publish 并发 1）；30s claim 租约＋心跳，启动先恢复过期 Job；SSE（先订阅后读快照、Last-Event-ID 重放）；重试分级：**导出 3 次、转录/autofill 1 次；发帖类与 publish 绝不自动重排**——中断后 post-checks 去平台查证 posted/not-posted/unknown；结果事件丢失也报「release 已发出，勿重发」（PublishResultLostError）。

## 4. AI agent 化运作

- **`cvm` CLI**：read-mostly，19 个名词，全部经一条 HTTP 传输打 remote API（无 in-process fallback），自带 schema version 握手（版本号＝Drizzle 迁移 journal 条目数，每请求带头，不等则 409→exit 6，解药 git pull）；6 个触机命令 local-only（`CVM_LOCAL_MACHINE=true` 声明，worktree 永不算作者机，读写前拒，exit 7）。退出码 0/2 not-found/3 input/4 db/5 auth/6 schema/7 local-only。ROOT_HELP 约 220 行，是领域教材。
- 长任务命令只 enqueue＋nudge 即返回 `{jobId, status:"queued", log:".data/logs/jobs/<id>.jsonl"}`，`--wait` 轮询事件重建退出码。
- **.sandcastle 自治闭环**（GitHub label 是唯一操纵杆，全 labeled 触发，链式加标必须 PAT——GITHUB_TOKEN 加的标不再触发）：
  人写 PRD 打标 → to-issues-prd（**agent 只出 JSON，脚本用 gh 确定性建 tracer-bullet 扁平子 issue**）→ implement（单 issue 开 draft PR）/ implement-prd（取首个子 issue 链式自转）→ review（双轴，可直接改码，幻觉评论用真 diff 校验丢弃）→ 人评论后 implement-pr 逐条 Address/Decline/Defer → update-branch（能 merge 不劳 agent）→ 前置关闭时 promote-queued 经原生 blockedBy 自动提升。失败挂 `agent:blocked`。
  **人只介入四处：写 PRD 打首标、认可拆单、merge（agent 永不 merge）、blocked 排障摘标。**
- 两原语：`run-with-retry`（无副作用调用，回灌校验错误续会话）；`run-with-extraction`（干活/提取两会话分离，失败只重提取不重提交——防重复副作用）。
- **verify-cvm**：每次验证用 `CREATE DATABASE TEMPLATE` 从作者生产快照模板克隆一次性库（白名单端口＋库名正则），外呼指丢弃端口、凭据不克隆、文件重定向 scratch/；对全部用户表装语句级触发器同事务记录 insert/update/delete，产出 **WRITE-LEDGER.md**（clean / writes landed / PENDING / 生产写尝试）。CLAUDE.md 硬规：**任何有可见 UI 效果的改动，PR 前必须浏览器实测，测试绿不替代它**；PR body 必须写清点了什么、看到什么、截图/证据路径。
- ADR 共 0001–0039。最相关：0023（Bundle 寻址＋原子可见）、0027（地址按配方、发送按字节哈希）、0029（门禁分层：只有硬缺口阻断）、0032（长任务进 sidecar、发布不自动重跑）、0033（本地 whisper）、0038（录制需 AV 校准）。
- 工程规约也值得看：`lint:boundaries`（dependency-cruiser 强制 core 无 fs/child_process/git，需要机器能力的从外层注入）；slow-request 日志（>2s 打印路由/耗时/SQL 语句数，高 dbStatements 即行循环信号，提示该 Job 化）；dev/start 输出 tee 到 `.data/logs/`，latest 软链，保留一天。

## 5. 对本流水线的借鉴清单（按 ROI 排序，含落地时机）

| 优先级 | 事项 | 对应我们的痛点 | 时机 |
|---|---|---|---|
| ⭐⭐⭐ | **音画偏移标定片**：3–5 个「BEEP＋白闪」事件，能量 onset vs 亮度突变取中位数，配对比/spread ≤1 帧门限，绑「音色＋TTS 版本＋渲染参数」复用；finalize 前后两版拆分延迟来源 | time_offset 靠 0.28/0.37/0.29 经验，每集试 onset | **hf-04 就地**（本来就要测 onset） |
| ⭐⭐⭐ | **两层内容寻址增量渲染**：分镜/cues/每镜音频 hash/time_offset/版本号→成片 hash，命中跳过；`.partial`→原子 rename；模板/ffmpeg/对齐算法三级版本号；有效 hash 集合 GC | F2 补丁整片重来；render 占夜间机时 | hf-04 后、hf-05 前 |
| ⭐⭐⭐ | **投稿幂等**：BV/分 P 号即 commit marker，重发先 list 查证；投稿命令零自动重试＋事后 posted/not-posted/unknown 查证；中断提示「可能已发出，勿重发」 | biliup append --title 不生效、双发恐惧靠人肉记 | hf-04 后（bili-pub.py 改造） |
| ⭐⭐ | **animatic 预审命令**（`videopipe animatic`）：句音频＋静帧按句长拼草稿片，渲染前审节奏；未取音句用词数回归估时长（先攒我们自己的样本再拟合系数，CVM 系数 1.65＋0.337/词是英文口径不能直接用） | 粗稿时长只有字数粗估，节奏成片才知道 | hf-05 阶段 |
| ⭐⭐ | **门禁三层显式化**：硬阻断（StaticGuard/结构非法/缺封面标题简介）／机器的活不阻断只列（未取音未渲染未转录，命令自己补）／规划建议退出 0（多音字表覆盖、正音风险字数） | check/StaticGuard 已有雏形但分层不显 | 随增量渲染一起 |
| ⭐⭐ | **转录缓存改源文件内容 SHA-256 sidecar**；长音频静音切块＋chunk 断点 | CPU whisper 不短，换 TTS 文件后手清缓存 | hf-05 阶段 |
| ⭐⭐ | **ffmpeg 治理**：重编码槽 1–2（沙箱 4K 内存）、`-progress pipe:1` 百分比、stderr 有界 tail、父子退出钩子杀孤儿、分段 encode＋concat、编码器回退 | 沙箱 OOM 已有同款教训；夜间任务日志/孤儿靠手工 | hf-05 阶段 |
| ⭐ | 录屏容器换 MKV＋崩溃 `-c copy` remux（原件留 .raw） | mp4 崩溃即废 | 下次录屏基建改动时 |
| ⭐ | 选帧固化：模型/脚本只给 clipIndex＋alt，人用帧步进在真实素材上 capture（写进 SOP） | F2 韵腹选帧教训已有，补成条文 | 立刻可写入 workflow.md |
| ⭐ | agent 侧效原语：副作用步骤「干活/提取」分离；agent 永不 merge；失败挂 blocked；确定性动作（建 issue/加标）归脚本 | #497 已有流程，可对照补「两会话」 | 远期 |
| ⭐ | 「测试绿不替代真机/浏览器实测」＋改动证据写 PR body；桌面 guard 的 Write Ledger 思路（对隔离环境的所有写操作留台账） | 我们有身份闸但无写台账 | 远期 |

**明确不学**：Postgres/全栈/Turborepo/Vercel/Dropbox（个人本地 Python＋git 足够）；Remotion（我们赛道是 HyperFrames）；CUDA turbo 模型（无独显）；它的弱词级修订（我们整句重合成更细，保持）。

## 6. 关键源码索引（相对克隆根）

- 术语/规约：`GLOSSARY.md`、`CLAUDE.md`、`CODING_STANDARDS.md`、`docs/adr/0023、0027、0029、0032、0033、0038`
- 创作流：`apps/local/app/features/animatic/`、`features/beats/beat-kinds.ts`（在 packages/core）、`features/article-writer/format-{animatic,beats}-context.ts`、`features/teleprompter/`、`services/{video,lesson,section,beat-learning-goal}-warnings*`、`app/packages/`（estimate-spoken-seconds 等）
- 视频工程：`apps/local/recorder-service/`、`packages/clap-detection/lib/{audio-onsets,match}.ts`、`features/av-calibration/`、`services/{footage-chunking,footage-transcription,footage-cache,whisper-transcription-service}.ts`、`services/overlay-*.ts`、`services/ffmpeg-*.ts`、`services/export-hash.ts`、`packages/overlay-renderer/`
- 发布：`services/course-publish-*.ts`、`features/publish/`、`apps/local/sidecar/`、`features/jobs/`
- agent：`.sandcastle/`、`.github/workflows/agent-*.yml`、`.claude/skills/verify-cvm/`、`apps/local/app/cli/`
