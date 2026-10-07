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

```
① 封面 make_cover.py   先定「一句话主张 + 主视觉」，锁立意/配色/母题
② TTS 音频             蝉镜试听取音（0 豆），放 media/
③ audioio + whisper    转 16k → word 级转录 raw（build/）
④ align + cues         NW 对齐正字稿，人工评审后 cues/cues.json
⑤ make_video.py        写分镜（本片独有），通用部分调 videopipe
⑥ check + snapshot     0 error；SwiftShader 抽帧，与老版零差异
⑦ render               npx hyperframes render → renders/
⑧ concat               封面 2s 静帧头 concat_copy 进首帧
⑨ 验收 + 计时日志/记忆
```

封面先行的意义：它是全片最早、最便宜的验收锚点；在约 12 分钟的昂贵
渲染前就把立意和视觉锁死，避免渲染完才发现方向错。

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
