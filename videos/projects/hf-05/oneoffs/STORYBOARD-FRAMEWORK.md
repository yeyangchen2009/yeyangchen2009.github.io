# hf-05《check 门控》分镜框架 v0（2026-10-16）

> 上游：`src/hf-05-draft.txt`（粗稿 1914 念字／6.0–6.4min）＋ `oneoffs/REHEARSAL-NOTES.md`（真机台账）。
> 本文档是**框架不是最终分镜**：录屏 take 精切、口播 TTS 出 cues 后，时间码在 make_video.py
> 以 S幕注释落定（惯例同 hf-04：`# S1 …（录屏 xxx＋freeze）0.00–14.42`）。
> 视觉语言沿用 hf-04：GitHub Dark 暗色卡（#0d1117 底／#161b22 卡／#1f6feb 蓝／
> warning #d29922／error #f85149／pass #3fb950／正文 #e6edf3）。

## 1. 成片骨架

封面静帧 2s（finalize --intro，事件时刻不折回，av-sync-calib 已证零偏移）
→ 口播铺满全片，录屏段与概念卡交替；char_track 底部逐字字幕。
录屏作**顶层 video clip、置 scenes 下层**（StaticGuard：video 必须顶层）；
概念卡是上层 Scene，终端段用 freeze（录屏尾帧静帧）缩左让右给卡。

## 2. 幕切分与素材映射（时间预算 v0，TTS 后重排）

| 幕 | 粗稿段 | 画面构成 | shorts 素材名（media/shorts/） | 预算 |
|---|---|---|---|---|
| S1 | seg A 开场～守门员 | 封面后概念卡 C1 六关＋录屏 check-good 全滚 | `check-good.mp4` | ~55s |
| S2 | seg B 删 duration | 录屏 NPP 删除＋check 黄字 passed；freeze 让 C2 头 | `dur-del.mp4` `dur-run.mp4` | ~35s |
| S3 | seg C 越界 | restore s2 跳切（镜头给 tail 行）→ check 双修复 → 现场改 root 13 复绿 | `overflow-run.mp4` `root-fix.mp4` | ~45s |
| S4 | 论述卡① | 全屏概念卡 C2（warning/error/退出码/CI） | —（原生 Scene） | ~30s |
| S5 | seg D 对比度主线 | 现场改色 #1a1f26 → check 红 5 点 exit 1（全片唯一红灯，戏剧高点）→ 改 rgb(93,97,102) → 10/10 | `color-bad.mp4` `color-fix.mp4` | ~60s |
| S6 | seg D 机制段 | 概念卡 C3 三层流水线（读文本/真跑/量像素） | — | ~35s |
| S7 | seg E 同轨 | restore s4 → check 全绿；DOM 对调仍绿；加遮挡色块 → text_occluded 红 | `same-track-run.mp4` `dom-swap.mp4` `occlude-run.mp4` | ~60s |
| S8 | seg E 小结 | 概念卡 C4（track-index 元数据 vs DOM 顺序；查结果不查命名） | — | ~20s |
| S9 | seg F 拼目标 | restore s5（镜头先给 #sut 行）→ check 3 warning passed | `nulltarget-run.mp4` | ~40s |
| S10 | seg F 连坐 | 概念卡 C5（绿灯≠没事；page_error→sweep_static「本次绿不可信」） | — | ~25s |
| S11 | seg G 体检三连 | restore s0：keyframes（--shot 洋葱皮）、inspect deprecated、beats 提示 | `kf.mp4` `inspect-dep.mp4` `beats.mp4` | ~40s |
| S12 | seg H 收尾 | 录屏 echo %ERRORLEVEL% 定格 0 → 概念卡 C6 行动三条 → 预告卡 C7 hf-06 | `errlvl-zero.mp4` | ~35s |

合计约 480s 素材位 → 剪到 **380–400s（6.3–6.7min）**：论述卡段口播不占满的用录屏
尾帧 freeze＋底注消化（hf-04「freeze 底注轮替」工艺）；若超 6.5min，先砍 S8 并入 S10
同侧卡片、再压 S11 inspect（deprecated 一句带过）。

## 3. 概念卡清单（原生 Scene，GitHub Dark）

| 卡 | 标题 | 要点 | 出现 |
|---|---|---|---|
| C1 | check 六道关 | Lint（不起浏览器读文件）／Runtime（无头 Chrome 收 console）／Layout（9 采样点 seek 量布局）／Motion（动画写法，repeat:-1 黄）／Contrast（逐点 3:1）／Snapshots；下三层标注「静态→真跑→渲染后量」 | S1 |
| C2 | 警告 vs 错误 | 黄⚠：页面成立但有后果，exit 0；红✗：页面不成立，exit 1；CI：零才放行，黄字人读；「绿灯不是免死金牌」 | S4（S2/S3 freeze 时先露头） |
| C3 | 对比度为什么归 Chrome 算 | 文本里只有色值；叠底/透明/动画中间态要真画像素才知道；9 采样点不眨眼；WCAG 大字 3:1 | S6 |
| C4 | 没有「轨」，只有结果 | track-index＝Studio 元数据；层叠看 DOM 顺序（呼应 hf-03）；遮挡 text_occluded 查的是画面；放行属性 data-layout-allow-occlusion **贴被盖文字元素才生效**（贴遮挡块无效，真机实测） | S8 |
| C5 | 绿灯≠没事 | #sut not found×3 → 动画静默失踪；真函数不存在 → page_error✗ 连坐 sweep_static「every green verdict unreliable」 | S10 |
| C6 | 行动三件 | 红错照修法改；黄警逐条读；exit 0 再渲染 | S12 |
| C7 | 下集预告 | hf-06 加声音与素材；audio_src_not_found＋media_missing_id 是硬 error | S12 尾 |

卡片动效统一：标题蓝色左边条滑入（0.25s power2.out），要点逐条 fade，时长由 cues 锁。
不引入无限循环（Motion gsap_infinite_repeat 自己讲过就别犯）。

## 4. 录屏 take 计划（布景 restore 顺序＝最少跳转）

| take | 起点态 | 现场操作 | 产 shorts |
|---|---|---|---|
| t1 | s0-good | 首跑 check（别敲第二遍，首滚最完整） | check-good |
| t2 | s0-good | 删 title 的 data-duration、存盘、check | dur-del/dur-run |
| t3 | s2-overflow（restore） | check；改 root duration 10→13；check | overflow-run/root-fix |
| t4 | 接 t3 末态 | title color 改 #1a1f26、check（红）；改 rgb(93,97,102)、check（绿）；分两行 echo %ERRORLEVEL% | color-bad/color-fix/errlvl-zero |
| t5 | s4-same-track（restore） | check；DOM 两段对调、check；贴入预置蓝块、check（text_occluded 9/9） | same-track-run/dom-swap/occlude-run |
| t6 | s5-null-target（restore） | 镜头给 #sut 拼写行，check | nulltarget-run |
| t7 | s0-good（restore） | keyframes --shot；inspect；beats | kf/inspect-dep/beats |

- s3-contrast 备份态只作 NG 重录快速起点，叙事走 t4 现场改色（犯错手感）。
- s6-occluded 同理：叙事在 t5 从 s4 现场贴入蓝块，s6 备份供 NG 重录/补镜头直接起点。
- 整块新增（tail、#sut、遮挡块）走预置＋跳切，不现场敲长代码。
- 录前读 videos/docs/screen-rec.md；gdigrab 素材精切必须 `-vf fps=30` 强制 CFR＋`-g 30`
  （hf-04 VFR 16 崩教训）；录屏同宽，避 hf-03 右缘 27px 穿帮。
- cmd 退出码分两行敲（`check` 回车，再 `echo %ERRORLEVEL%`），同行 & 读旧值录假结果。
- 窗口/字体/缩放几何沿用 hf-04 RECORD-NOTES「四、几何速查」；F:\_hftest 路径公开无脱敏问题。

## 5. make_video 实现备忘（录屏＋cues 齐了再写）

- track 分配：bg(track0) ／ 录屏 video clips（顶层、下层）／ 概念卡 scenes（track 2+）／ 字幕 char_track（最上）。
- root total 以 TTS wav 时长为准；音频 media 24kHz mono 蝉镜母带规格。
- 每个 freeze＝录屏尾帧 PNG（ffmpeg -ss output seeking -frames:v 1，sparse-keyframe 坑见 hf-04）。
- measure_offset 逐片重跑，不取历史固定值（av-sync-calib 结论：偏差归 whisper 句间停顿）。
- check 六段长输出用「终端缩左 58%＋右侧要点卡」，不全屏堆满终端。
- 0.8.107 钉死；本机 UHD620 硬件 D3D11 行首刷可保留可剪。

## 6. 待决策（录前定）

1. 正片标题三选一（粗稿文首候选）。
2. shell：倾向 cmd（%ERRORLEVEL% 传统画面）；若用 PowerShell 全部口播改 $LASTEXITCODE。
3. 遮挡段是否演示 data-layout-allow-occlusion 放行（＋30s，默认不演示，只在 C4 卡上列属性名）。
4. 封面：check 绿勾＋终端意象，亮色宣纸系还是 hf-04 暗色系——与前四封摆一排拍板。
