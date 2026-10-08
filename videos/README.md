# videos — 视频工作流

「封面先行」的深模块化视频管线。前端 HyperFrames（HTML/GSAP），后端
Python（faster-whisper / pypinyin / numpy）。五部成片已迁入
`projects/`，公共逻辑收敛在 `videopipe/`。

## 五部成片（projects/）

| 目录 | 片 | 特性 |
|---|---|---|
| `xinjing` | 心经敬诵（71.5s） | 动态云雾 mp4 背景、中央 76px 逐字 cue、底部整句轨、双时长 |
| `zhushixing` | 朱士行素版 | 暗色金、11 场景丝路图、刻意保留 blur |
| `zhushixing-pro` | 朱士行 Pro demo | noto faces、跨项目 cues 切片、camera/FX |
| `zhushixing-wang` | 朱士行王版（287s） | 敦煌暖、17 幕、宏观阿尔法封面 |
| `zbj` | 猪八戒（225s） | 宣纸「考古工作台」、15 幕 git merge 母题、同款封面 |

## 标准流程（封面先行）

下列 ③④⑧ 已收成 videopipe CLI（在 `videos/` 目录下运行），无需再手抄 oneoff：

```
① 封面 make_cover.py   先定「一句话主张 + 主视觉」，锁立意/配色/母题
② 备双稿 + TTS         先写 src/<片>-src.txt 正字稿（字幕/对参照用）；
                        再派生 src/<片>-tts.txt 借音稿（易错多音字换成
                        读音确定的同音字）；★只拿 tts.txt 跑蝉镜试听
                        （0 豆），wav 放 media/。详见下「多音字借音」
③ transcribe           python -m videopipe transcribe projects/<片>
④ cues                 python -m videopipe cues projects/<片>；评审 align-check/srt
                        无误后加 --install 落地 cues/cues.json
⑤ make_video.py        写分镜（本片独有），通用部分调 videopipe
⑥ check + snapshot     0 error；SwiftShader 抽帧，与老版零差异
                        ★snapshot 会清空整个 snapshots/（连封面一起删）
⑦ render               npx hyperframes render → renders/
⑧ 重截封面→finalize    make_cover＋cdp-shot 重截封面，再
                        python -m videopipe finalize projects/<片>
                        （封面 2s 静帧头进首帧，时长自动断言；视频 copy、
                        音频整段重编码——见下「音画对齐」）
⑨ 验收 + 计时日志/记忆
```

封面先行的意义：它是全片最早、最便宜的验收锚点；在约 12 分钟的昂贵
渲染前就把立意和视觉锁死，避免渲染完才发现方向错。

## 多音字借音（② 的硬规矩，先借音再 TTS）

TTS 引擎碰到多音字和非常用字（如「伽／偈／降／差」）经常读错，而一旦
合成完再发现读错，只能整条重跑。所以 **TTS 前必须先备双稿**：

1. **正字稿** `src/<片>-src.txt`：正确字形，**字幕**和 ③transcribe 的
   对参照都用它（观众看到的永远是正字）。
2. **借音稿** `src/<片>-tts.txt`：把易错字**只换字形**为读音唯一确定的
   常用同音字，语义与断句不变；**只拿它去跑 TTS**。

铁律顺序：`src 正字稿 → tts 借音稿 → TTS 出 wav → 用 src 做字幕`。
绝不能拿正字稿直接合成。借音稿建议用脚本从 src 派生（`.replace(...)`）
而非手敲，保证两稿逐字一致、只差借字；同时在
`oneoffs/<片>-pronunciation.md` 记正音表（高风险字＋借音预案）。

| 正字（src，上字幕） | 借音（tts，喂 TTS） | 锁定读音 |
|---|---|---|
| 楞伽经 | 楞茄经 | 伽 **qié** |
| 那首偈 | 那首记 | 偈 **jì** |
| 当差 | 当拆 | 差 **chāi** |
| 降将 | 祥将 | 降 **xiáng** |

合成后务必抽听这几处确认读音，再进 ③。

## 目录

```
videos/
├── videopipe/            公共包（深模块，全部入库）
├── templates/project/    脚手架模板
├── new_project.py        python new_project.py <name>
├── assets/               共享字体（fonts/ 与 wenkai/ 入库，local-fonts/ 忽略）
├── docs/                 HyperFrames / agent 注意事项
├── requirements.txt
└── projects/<片>/
    ├── hyperframes.json package.json meta.json   项目配置（入库）
    ├── make_video.py                             分镜（入库，本片独有）
    ├── make_cover.py                             封面（入库，有封面的片）
    ├── src/                正字/TTS 稿（入库）
    ├── cues/cues.json                            评审锁定版对齐（入库）
    ├── oneoffs/            一次性脚本（入库）
    ├── index.html                                生成产物（忽略）
    ├── media/ build/ renders/ snapshots/         本地产物（忽略）
```

## 新建项目

```bash
python new_project.py my-video      # 生成标准骨架
```

随后按①–⑨填内容。`make_video.py` 里只需写本片独有的 `Scene` body、
场景专属 CSS、场景动画 JS，其余全部 `from videopipe import ...`。

## videopipe CLI（在 videos/ 下）

```bash
python -m videopipe transcribe projects/<片>          # ③ wav→16k→whisper 词级转录
python -m videopipe cues projects/<片>                # ④ NW 对齐组句（只写 build/）
python -m videopipe cues projects/<片> --install      # 评审后落地 cues/cues.json
python -m videopipe finalize projects/<片>            # ⑧ 封面头+正片→media/<片>-yeyang-cover.mp4
```

路径默认按项目目录名约定推导，可用 `--wav/--src/--body/--cover/--out` 覆盖。

## 常用命令（在 projects/<片>/ 下）

```bash
npx --yes hyperframes@0.8.107 check          # lint+runtime+layout（改完必跑）
npx --yes hyperframes@0.8.107 preview        # 人工预览
npx --yes hyperframes@0.8.107 snapshot --at 60 --no-browser-gpu   # 确定性抽帧
npx --yes hyperframes@0.8.107 render         # 渲染 MP4
```

## videopipe 模块

| 模块 | 职责 |
|---|---|
| `config` | 帧率/时长/编码/路径等全部常量单一来源 |
| `page` | HTML 外壳、audio 标签 |
| `theme` | 主题参数、CSS 装配（通用骨架夹场景专属 CSS） |
| `scene` | Scene、clip/scene-inner 渲染、淡变 |
| `subtitle` | 底部逐字高亮/整句轨 + 中央逐字 cue clip（心经） |
| `cover` | 封面骨架（宣纸/铅笔/construction 层，主视觉 SVG 片内手写） |
| `audioio` / `whisper_asr` | 转码、PCM、word 级转录 |
| `align` | Needleman-Wunsch 字形+拼音对齐 |
| `cues` | 组句、单调修正、cues.json/SRT |
| `concat` | 封面静帧头、无损拼接 |
| `verify` | 结构提取、新旧零差异对比 |

## 铁坑（迁移实测，详见 docs/hyperframes-agent.md）

- **StaticGuard**：不要在带 `class="clip"` 的元素上动画 autoAlpha；
  clip 内包 `.scene-inner`，淡变目标 `#id > .scene-inner`、只动 opacity。
- **GSAP SVG**：被 GSAP 控制的 `g` 不可自带 transform，基点放不动画
  的外层 `g`；初始态 set 必须显式传秒（无 position 的 set 会追加到末尾）。
- **blur 与捕获性能**：`filter:blur` 会从 drawElement streaming 回退慢速
  screenshot。wang/zbj 零 blur；**素版 zsx 刻意保留 blur，不得顺手统一**。
- **确定性**：生成脚本禁 `Math.random`/`Date.now`；抽帧固定切点、
  `--no-browser-gpu`（SwiftShader），同输入逐字节一致。
- **沙箱内存上限**：Claude Code 沙箱给子进程设了提交内存上限，4K 的
  libx264 编码（`finalize` 的封面头）会报 `x264 malloc ... failed`；
  `transcribe/cues`（whisper）不受影响。跑 4K 的 `finalize` 与 `render`
  时需在非沙箱（用户授权）下执行。

## 音画对齐（⑧ 的硬规矩，别让封面头顶出偏移）

封面头与正片是两段独立 AAC，若用 ffmpeg concat demuxer `-c copy` 直接拼，
正片段头部的 **encoder priming**（一段几十毫秒的静音采样）会被原样保留在
拼接点：画面在精确 2.0s 已切进正片，真正的声音却晚到，形成「图比声快」、
偏移固定且贯穿全片（达摩片实测 92ms）。

所以 `finalize` 走 `videopipe.finalize_concat`：

- **视频**：封面头 + 正片 concat `-c copy`，帧精确、正片不重编码；
- **音频**：取正片 PCM，与封面静音在一条 `concat` filter 里**整段重编码**
  AAC——拼接点是连续采样、无段边界 priming（priming 只剩整条最开头一次，
  落在封面静音区，无感）。

验收：`ffprobe` 音视频两条流 `start_time` 都应是 `0.000000`；也可对拼接点
做能量检测，正片首个成声帧应精确落在 2.000s。旧片（梁武帝等）已用
`concat_copy` 发布，不回改。
