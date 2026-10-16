# hf-05《check 门控》正式录屏台账

> 上游：`src/hf-05-draft.txt`（粗稿 1914 字）、`STORYBOARD-FRAMEWORK.md`（12 幕/t1–t7）、
> `REHEARSAL-NOTES.md`（七权威态真机台账）。本篇只记**正式录屏**的机位、命令、
> take 表、实测耗时与坑。布景＝`setup_scenes.py` 在 `F:\_hftest\hf05-check` 生成。

## 一、机位（沿用 hf-04，本片只有两身份）

| 身份 | 窗口 | 标题针 | 外框几何 |
|---|---|---|---|
| 便携 NPP | `F:\_hftest\npp-local\notepad++.exe -multiInst -nosession F:\_hftest\hf05-check\proj\index.html` | 含 `_hftest\hf05-check` | (-12,0,1624,928) |
| 终端 | `wt.exe -w new --title hf05-rec --suppressApplicationTitle -d <proj> cmd /k <env>` | startswith `hf05-rec` | (-12,0,1632,1000) |

- 录区：gdigrab 物理 **(0,0,1600,920)@30**；系统 DPI 150%，坐标全是物理像素。
- 右边 12px 圆角透明带：实体右缘到 1600 才零穿帮（hf-03 右缘 27px 事故的根治）。
- BlackMat 垫窗 y=900 遮底缘缝；鼠标 park (12,884)。
- 无浏览器/CDP/dev server：check 直接读磁盘文件。guard 白名单只两身份，
  用户回机切窗，下一注入立即 `UnsafeForeground` 中止。
- 终端三环境变量：`HYPERFRAMES_FONT_CACHE_DIR=F:\_hftest\.cache\fonts`、
  `HYPERFRAMES_NO_UPDATE_CHECK=1`、`HYPERFRAMES_SKIP_SKILLS=1`。
- `--suppressApplicationTitle` 必须有：npx 会 SetConsoleTitle，没它标题针失配。

## 二、命令与等待常量（2026-10-16 真机标定，包缓存热态，UHD620）

| 命令 | 墙钟 | 备注 |
|---|---|---|
| `npx --yes hyperframes@0.8.107 check .`（冷/热） | 24.1s / 20.1s | 六态全在 20.0–21.2s；录制态取 **CHECK_WAIT=28** |
| `… keyframes` | 7.9s | KF_WAIT=12 |
| `… keyframes --shot rec-shots/onion.png` | 14.1s | 自建父目录；尾行打印 saved 全路径；SHOT_WAIT=19 |
| `… inspect .` | 15.8s，rc=0 | deprecated 文案在输出尾；INSP_WAIT=21 |
| `… beats .` | 8.3s，**rc=1** | `No music track found. Add data-timeline-role="music"…`；BEATS_WAIT=13 |

全新 cmd 首轮 npx 冷启另算（hf-04 实测 68s），正式录前必须跑 `warmup` 吞掉。
录制态 gdigrab 负载下按 +20–30% 留余量；check 尾帧必须拍到 `Check passed/failed`。

## 三、七态 check 逐字基准（目验母带对照，已去 GPU 行）

- **s0-good**：六段全绿，`Contrast 10/10`，`◇ Check passed`，rc=0。
- **s1-no-duration**：Lint
  `⚠ timeline_element_missing_timing: <div id="title"> is a timeline element without data-duration, so the timeline cannot draw where it ends.`
  ＋`Fix: Add data-duration (in seconds) to <div id="title">.`，1 warning，passed。
- **s2-overflow**：Lint
  `⚠ clip_ends_past_root_duration: <div id="tail"> runs from 8s to 13s, past the root composition's data-duration of 10s, so it is cut off in previews, posters and renders.`
  ＋`Fix: Extend the root data-duration to 13, or make <div id="tail"> end at or before 10s.`
  Contrast **11/11**（比 s0 多 tail 文字）。
- **s3-contrast**：Contrast 五采样点 `t=0.556/2.778/5/7.222/9.444s`
  `✗ #title 1.14:1 (need 3:1, …)`＋`Try rgb(93,97,102); source index.html`，
  5 errors，`◇ Check failed`，**rc=1**。
- **s4-same-track**：全绿，Contrast **6/6**。
- **s5-null-target**：Runtime 3⚠——
  `GSAP target #sut not found. https://gsap.com`（t=0s）＋两条
  `GSAP target  not found.`（t=0s、t=1.667s），Layout 0 issues，passed。
- **s6-occluded**：Layout
  `✗ t=0.56-9.44s (9 samples) text_occluded #title inside #block "check 门控：让机器先帮你挑错" — Text is hidden beneath an opaque element.`
  ＋Fix 三修法（own zone / stacking order / `data-layout-allow-occlusion`），
  Contrast 不连坐 10/10，**rc=1**。
- GPU 行 `browserGpuMode probe → hardware … UHD Graphics 620 … D3D11` 在合并
  流里位于末尾，真实终端出现时刻以 t1 母带为准（保留与否剪接定）。

## 四、take 表（20 母带，录制顺序＝ALL_TAKES）

| take | 起点态 | 内容 | duration | 产 shorts |
|---|---|---|---|---|
| t1-check-good | reset s0 | 首跑 check，六段全滚（别敲第二遍） | 34 | check-good |
| t2a-dur-del | reset s0＋NPP | 删 title ` data-duration="10"`、存盘 | 12 | dur-del |
| t2b-dur-run | 接态 | check 黄⚠ passed | 34 | dur-run |
| t3a-overflow-run | reset s2 | check 越界双修复 | 34 | overflow-run |
| t3b-root-fix-npp | 开 NPP | tail 行静场→root L17 `10`→`13`、存盘 | 14 | root-fix（上） |
| t3c-root-fix-run | 接态 | check 复绿 11/11 | 34 | root-fix（下） |
| t4a-color-bad-npp | 接 t3 末态 | L11 `#e6edf3`→`#1a1f26`、存盘 | 11 | color-bad（上） |
| t4b-color-bad-run | 接态 | check 红 5✗ rc=1（全片高点） | 34 | color-bad（下） |
| t4c-color-fix-npp | 接态 | →`rgb(93,97,102)`、存盘 | 12 | color-fix（上） |
| t4d-color-fix-run | 接态 | check 复绿；**分两行** echo %ERRORLEVEL%→0 | 40 | color-fix／errlvl-zero |
| t5a-same-track-run | reset s4 | check 全绿 6/6 | 34 | same-track-run |
| t5b-dom-swap | 开 NPP | L20-21 整选剪切→L18 前粘贴、存盘 | 17 | dom-swap |
| t5c-dom-swap-run | 接态 | 对调后 check 仍绿 | 34 | （备尾帧） |
| t5d0-occlude-code | reset s6＋NPP | block L22-25 静场（整块新增跳切） | 6 | occlude-run（上） |
| t5d-occlude-run | 接态 | check text_occluded 9/9 红 | 34 | occlude-run（下） |
| t6a-nulltarget-code | reset s5＋NPP | L26 `#sut` 拼写行静场 | 6 | nulltarget-run（上） |
| t6b-nulltarget-run | 接态 | check 3⚠ passed | 34 | nulltarget-run（下） |
| t7a-kf | reset s0，关 NPP | keyframes 列表→cls→--shot 洋葱皮 | 39 | kf |
| t7b-inspect | 接态 | inspect deprecated | 25 | inspect-dep |
| t7c-beats | 接态 | beats 无音乐轨（rc=1） | 17 | beats |

净素材 ≈ 8.4 min；加 NPP 五次冷启（30–60s/次，录制外）与 take 间布景，
单次全推约 20–30 min；留 NG 缓冲按 2–3h 占机。

## 五、录前检查（按序）

1. `python oneoffs/check_anchors.py`——退出码 0 才开拍（锚点/编辑序列磁盘镜像）。
2. 便携 NPP 目验：暗色主题、zoom=0、Wrap=no、Alt+Up/Down 行移动映射仍在
   （doLocalConf.xml 持久；launch 后程序还会双保险关 wrap）。
3. `python oneoffs/record_segments.py warmup`——吞冷启＋终端各命令输出目验；
   确认 `rec-shots/onion.png` 生成（无 --selector 默认拍 #sub，#title 淡入只
   呈粉框 marker；概念卡若要用真 ghost，后期 `--selector #title` 重出）。
4. 沙盒工程在 `F:\_hftest\hf05-check\proj`，backup 七态齐；关闭用户日常 NPP
   里任何同名 index.html（避免 find_window 复用误撞；reset 后均为新进程）。
5. 录屏机黑屏/休眠关闭，微信等通知静音；录中人离机（guard 一碰用户窗即中止）。

## 六、录后流程

1. 每 take 已自动抽 2s/帧到 `F:\_hftest\hf05-rec\frames\`，立即 contact 目验＋
   尾帧彻查（warning/error 文案逐字对第三节基准；NG 当晚重录，s3/s6 备份是
   快速起点：叙事虽走现场改色/贴块，NG 补镜头可直接从对应态起）。
2. 母带归位（gitignored）：
   `copy F:\_hftest\hf05-rec\takes\*.mp4 videos\projects\hf-05\media\`
3. `python oneoffs/cut_shorts.py frames`→目验 sheet→回填 CUTS→`cut`。
4. CFR 硬闸：
   `python -m videopipe probe-fps videos/projects/hf-05/media/t-*.mp4` 必须 **exit 2**（原始 VFR）；
   `python -m videopipe probe-fps videos/projects/hf-05/media/shorts` 必须 **exit 0**。
   精切四参数 `-vf fps=30 -g 30 -keyint_min 30 -movflags +faststart` 已在 cut 模板。
5. 后续：TTS（蝉镜 24k mono）→whisper/align/cues→measure_offset 逐片→
   make_video（12 幕，终端缩左 58%＋右卡，freeze＝尾帧 PNG）→check→render（非沙箱）→F2→PR。

## 七、坑（录中回填）

- 【待回填】t1 真机 check 录制态墙钟（gdigrab 负载）；超 28s 尾帧缺 Check passed
  则 t1 及各 check take 统一加秒重录（常量一处改）。
- 【待回填】%ERRORLEVEL% 入镜形态（t4d）：必须 check 回提示符后再敲；若拍成
  同行或数值非 0，t4d 单独重录。
- 【待回填】cmd 输入排队兜底：固定 sleep 内 check 未完时命令进 conin 缓冲，
  退出码语义仍正确（交互行执行前展开），但画面会穿帮——以母带为准。
- 已知：NPP 外部覆盖文件前必须先关实例（reset 流程已保），否则「重新加载」框
  由 _dismiss_modal 处理（Alt+Y）；close_any_npp 三轮关不掉且 exe 非 npp-local
  会拒绝强杀。
- 管道坑（非本片）：`check | tail` 后 `$?` 是 tail 的码；量退出码别接管道。
