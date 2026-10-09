# HyperFrames 视频教程选题库（技术教程线 · 叶扬频道）

> 与《选题库-中国佛教史人物与主题》并行的另一条线：这是**教程序员 / AI agent 用 HTML 做视频**的技术教程。
> 主角是工具 HyperFrames（Apache 2.0 开源，钉死版本 **0.8.107**），官方口号：
> **「Write HTML. Render video. Built for agents.」**
> 主线严格对齐官方 production loop：**plan → write valid HTML → wire seekable animations → add media → lint → preview → render**。
> 每集成片 = 屏幕录制（真实终端/编辑器操作，screen-rec）＋ GSAP 概念卡 ＋ 逐字字幕，最终本身也是一个 HyperFrames 工程（用 HyperFrames 讲 HyperFrames）。

## 节目定位

- **受众**：会写一点 HTML/CSS/JS 的程序员，以及替人干活的 AI coding agent。
- **一句话主张**：视频不必在时间轴上拖轨道，写网页就能确定性地烤出 MP4；同一份输入，逐字节同一份输出——所以它敢说「为 agent 而生」。
- **画面两类来源**：
  - `screen-rec`（gdigrab）录真人桌面操作：终端、编辑器、浏览器；
  - `cdp-shot --record` / HyperFrames 自身：逐帧确定性导出概念卡与动画。
- **单集目标时长**：5–8 分钟；口播 300–350 字/分。

## 第一季 · 用 HTML 做视频：从 0 到第一条成片（8 集，约 50 分钟）

> 目标：看完能独立把一个纯 HTML 页面做成一条 MP4，并理解「确定性 / 可定位动画」这两条命脉。

| 集 | 标题 | 时长 | 屏幕录制演示 | 核心知识点（官方概念） |
|---|------|------|-------------|----------------------|
| hf-01 | 写 HTML，出视频：这东西是给 AI 用的 | ~5min | `hyperframes --help`、`hyperframes doctor` | 定位与口号；三大依赖（Node≥22 / FFmpeg / Chrome）；确定性＝同输入同输出；与录屏、剪辑软件、Remotion 的区别 |
| hf-02 | init 三十秒：一个项目长什么样 | ~6min | `hyperframes init`、看目录、`hyperframes preview` | 项目骨架；合成契约：`data-composition-id`、`class="clip"`、`data-start`、`data-duration`、`data-track-index`；stage / tracks |
| hf-03 | 第一个 clip：把网页摆上时间轴 | ~6min | 写标题卡、preview 验证 | 纯 HTML/CSS 静态画面；clip 起止与轨道层叠；`data-width/height`；时间即 DOM 属性 |
| hf-04 | 灵魂在 seek：让动画可以被定位（核心集） | ~8min | 写 GSAP `timeline({paused:true})`、注册 `window.__timelines['main']`、seek 演示 | 为什么普通 CSS 动画无法逐帧渲染；seekable 动画适配器（GSAP / CSS / WAAPI / Lottie / Three.js / Anime.js / 自定义 frame adapter）；`seek(t)` |
| hf-05 | check 门控：让机器先帮你挑错 | ~6min | 故意写错 → `check` 报错 → 修好 | `lint` / `validate` / `check` 三层；常见错（缺 duration、时间轴越界、track 冲突、对比度）；`beats` / `inspect` / `keyframes` 体检 |
| hf-06 | 加媒体：图、音、视频进场 | ~7min | 放配音/背景音乐/视频，调音量 | 媒体 clip；`data-volume`；`media.autoProxy` 与 `media-treatment`；`normalize-audio`（LUFS 对齐）；音频轨 |
| hf-07 | preview 到 snapshot：把每一帧看清楚 | ~6min | `preview`/`present` 实时看，`snapshot` 指定时点出图 | 实时预览 vs 离帧快照；snapshot 逐帧目检；`keyframes` onion-shot；`compare` / `grade-compare` 变体对照 |
| hf-08 | render：无头 Chrome 怎样把网页烤成 MP4 | ~6min | `render` 出成片、核对确定性 | 渲染原理：无头 Chrome 逐帧 seek → capture → FFmpeg 编码；render 参数（fps / 分辨率 / `--no-browser-gpu`）；确定性逐字节一致；预告云端 `cloud` / `lambda` / `cloudrun` 与第二季 |

## 第二季 · 进阶（暂定，开播前再细化）

- 多 composition 与注册表（`add` / `catalog` / registry blocks、components）。
- 可定位动画深水区：Lottie / Three.js / 自定义 frame adapter 实战。
- 音频全流程：`transcribe` 词级时间戳、`tts`（Kokoro 本地）、`beats` 卡点、`normalize-audio` 母带。
- 云端与分布式渲染：`cloud` / `lambda` / `cloudrun`、`benchmark` 选档。
- 给 agent 的 skills：`hyperframes skills`（21 个官方 skill）与「PR → 视频」「录播剪」等 creation workflow。
- 综合实战：复刻一条本频道的佛教史卡片视频（呼应佛教史线）。

## 制作 SOP（每集九步，复用 videos 深模块，详见 videos/docs/workflow.md）

1. 封面先行（`make_cover.py`，立意锚点）；
2. 双稿：`src/` 正字稿（字幕用）→ `tts` 借音稿（TTS 用，多音字替换）；
3. 蝉镜试听 0 豆取音（绝不点「立即生成」）；
4. `python -m videopipe transcribe` 得 word 级时间戳；
5. `python -m videopipe cues` 组句对齐，落 `cues/cues.json`；
6. 无人值守屏幕录制：自动开可见终端跑真实命令，`screen-rec` 录 mp4，抽帧目检后裁切归位 `media/`；
7. `make_video.py` 编排：录屏 mp4 作 `<video class="clip">` ＋ 概念卡 ＋ 逐字字幕；
8. `check` 门控 0 error → `snapshot` 抽帧 → `render` → `finalize` 拼封面；
9. 走分支 PR（只入源文件，成片/中间产物 gitignored）。

## 版本与确定性约束

- HyperFrames 全季钉死 **0.8.107**，不因 doctor 提示升级（像素/行为需逐集可比）。
- 生成脚本禁 `Math.random` / `Date.now`（录屏器内仅作挂钟统计、不进帧）；固定切点、`--no-browser-gpu`，同输入逐字节一致。
- 录屏画面里出现的命令一律真实执行，输出以本机实测为准（本机基线：Node v24.6.0 / FFmpeg 7.1.1 / Chrome headless-shell 152）。
