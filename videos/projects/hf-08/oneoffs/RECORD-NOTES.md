# hf-08《render：无头 Chrome 怎样把网页烤成 MP4》正式录屏台账

> 上游：`src/hf-08-zhengyin.md`（2438 汉字／母带 611.51s）、20 幕分镜
> `make_video.py`（293 句）、`PROBE-NOTES.md`（2026-10-21 真机探针，
> 全部数字/报文的逐字出处）。本篇只记**正式录屏**的机位、take 表、
> freeze 表、录前录后流程与坑。
>
> 与 hf-06 的根本不同：本集主角是 `render`（烤一次 52–68s），不是秒回的
> `check`；母带少而长（6 条），freeze 多（14 张，大半是日志/目录回放帧）。

## 一、机位（沿用 hf-06，三身份）

| 身份 | 窗口 | 标题针 | 用途 |
|---|---|---|---|
| 终端 cmd | `wt.exe -w new --title hf08-rec --suppressApplicationTitle -d <proj> cmd /k <env>` | startswith `hf08-rec` | render 全跑、日志/目录回放 |
| 终端 pwsh | 同一 wt 的第二个 tab：`pwsh -NoProfile` | 窗口标题不变（仍 hf08-rec） | Get-FileHash 六连（t2） |
| 便携 NPP | `F:\_hftest\npp-local\notepad++.exe -multiInst -nosession <chunk.js>` | 含 `_hftest\hf08-media` | 仅 src-blackbar 一张 freeze |

- 录区：gdigrab 物理 **(0,0,1600,920)@30**；系统 DPI 150%，坐标全是物理像素。
- 右边 12px 透明带、BlackMat 垫窗、鼠标 park (12,884)——同 hf-06。
- 无浏览器/CDP/dev server（render 自己开无头 Chrome，不算身份；guard 只认
  wt 与 NPP，用户回机切窗下一注入立即 `UnsafeForeground` 中止）。
- 终端三环境变量（同 hf-06）：`HYPERFRAMES_FONT_CACHE_DIR=F:\_hftest\.cache\fonts`、
  `HYPERFRAMES_NO_UPDATE_CHECK=1`、`HYPERFRAMES_SKIP_SKILLS=1`。
- `--suppressApplicationTitle` 必须有：npx 会 SetConsoleTitle。
- 终端 1600×920 录区在分镜里缩到 **1120×644（.term，object-fit:fill）**，
  右 620px 让给概念卡；字号别缩：wt 配置沿用 hf-06 录制档（22px 左右）。

## 二、布景（setup_scenes.py 待写，目标工作区 `F:\_hftest\hf08-media`）

探针期资产已存在，setup 只搬运/重跑，不重新做实验：

| 布景项 | 来源（探针期实物） | setup 动作 |
|---|---|---|
| 沙盒工程 | 仓库内 `videos/projects/av-sync-calib`（13s/390 帧/黑底五白闪） | 录屏就用仓库路径跑（render 自报路径会入镜，工程名是真名） |
| 六权威 mp4 | `F:\_hftest\hf08-probe\body-a/body-b/w1/hw-a/hw-b/dbg.mp4`（全 61145B 同 hash） | copy 到 `hf08-media\hashes\` 并改名 **soft-a/soft-b/1015-old/w1/hw-a/hw-b.mp4**（与分镜指纹表逐字一致；copy 不改字节） |
| 1015-old 底档 | 2026-10-15 历史产物（探针时比对过，先找 `probe-seeds/`，没有从 hf-08 oneoffs 探针脚本登记处取） | 同上，改名 1015-old.mp4 |
| 坏工程 | `hf08-probe\bad-lint\index.html`（6s 红块 rAF，无 timeline 注册） | copy 到 `hf08-media\bad-lint\`（含 f01/f02 备用） |
| 缺音轨工程 | `hf08-probe\missing-media\index.html`（audio src=media/nope.wav） | copy 到 `hf08-media\missing-media\` |
| --debug 实物 | `.debug/<jobId>/` 在 **npx 缓存目录内、jobId 随机且可能被清** | setup 现跑一次 `render . --debug -o dbg.mp4`，跑完**立即 copy** 到 `hf08-media\debug\`（compiled/、captured-frames 390 JPG、perf-summary.json、render.log） |
| png-sequence | `hf08-probe\seq\`（390 PNG＋audio.m4a，3.2MB） | copy 到 `hf08-media\seq\` |
| 七份日志 | `hf08-probe\run-a/run-b/w1/hw-a/hw-b/bad-lint-default/bad-lint-strict/mm-be/mm-strict/dbg/seq.log` | copy 到 `hf08-media\logs\`，录屏尾报数字的「二遍对拍」底本 |

restore 动作＝删工作区重 copy（debug 重跑）；六 mp4 严禁任何工具触碰
（缩略图生成不改字节，但别过编辑器）。

## 三、命令与等待常量（2026-10-21 探针热态实测；录制态彩排回填）

| 命令（av-sync-calib） | 探针墙钟 | 尾报关键数字 | take |
|---|---|---|---|
| `render . --no-browser-gpu -o …` **冷态首跑** | **68.1s** | `rendered in 1m 8.1s`，setup 16.4s，capture 33.6s，encode 14.2s | t0 |
| 同上第二跑（热） | 55.7s | setup 5.5s（**不录**，只做对拍） | — |
| `render . --browser-gpu -o …` | **52.4s** | capture 40.5s 与 `encode (during capture) 40.5s` 完全重叠 | t1 |
| bad-lint 默认 render（6s 工程） | 约 60s（含 45s 轮询，彩排实测） | `2 error(s), 1 warning(s)` → Continuing，exit 0，产物 24527B | t3 |
| bad-lint `--strict` | 约 10–12s | `Aborting render due to lint issues`，exit 1，无产物 | t4 |
| missing-media 默认 render | 约 60s（同含 45s，彩排实测） | `Render blocked by 1 correctness warning: audio_processing_failed`，exit 1 | t5 |
| `Get-FileHash` 六连 | 秒回 | 六行 Hash 全同 | t2 |

**冷态纪律（本集头号坑）**：t0 要的尾报是 **68.1s**，差的 12s 在
capture-calibration（16.4 vs 热 5.5）。当天录屏**第一条就是 t0**，
之前不许跑任何 render 做 warmup（与 hf-06「先 warmup 吞冷启」正好相反）；
t1 紧接 t0 跑正好是热态。NG 重录 t0 若浏览器已热，setup reset 后
另起全新 wt 再录；尾报 NG 阈值：sw 必须报 **1m0x s**（口播钉「68 秒」），
hw 52±3s。

## 四、take 表（6 母带；录制顺序＝ALL_TAKES，不可调换）

| take | 目录/tab | 命令 | 母带时长 | 成片取用（VIDEOS 已预填） |
|---|---|---|---|---|
| t0-sw | av-sync-calib／cmd | `npx hyperframes@0.8.107 render . --no-browser-gpu -o F:\_hftest\hf08-rec\sw.mp4` | ~72 | sw1 源内 1.0–6.2（5.2s 启动行）；sw2 源内 60.5–65.3（4.8s Timing） |
| t1-hw | 同窗接跑／cmd | `npx hyperframes@0.8.107 render . --browser-gpu -o F:\_hftest\hf08-rec\hw.mp4` | ~56 | hw1 源内 5.0–9.8（4.8s probe 行）；hw2 源内 44.5–51.3（6.8s Timing＋streaming） |
| t2-hash | hashes／**pwsh tab** | `Get-FileHash soft-a.mp4,soft-b.mp4,1015-old.mp4,w1.mp4,hw-a.mp4,hw-b.mp4 -Algorithm SHA256 \| Format-Table Path,Hash -AutoSize` | ~16 | hash6 源内 0.8–8.7（7.9s）＋尾帧 freeze hash6-run.png（18.5–24.0） |
| t3-badlint | bad-lint／cmd | `npx hyperframes@0.8.107 render . -o out.mp4` | ~62 | badlint 源内 0.5–8.8（8.3s：lint 2 error＋Continuing）；中段 45s 等待整段弃 |
| t4-strict | bad-lint／cmd | `npx hyperframes@0.8.107 render . --strict` | ~14 | 全程弃视频，只取尾帧 strict-abort.png |
| t5-missing | missing-media／cmd | `npx hyperframes@0.8.107 render . -o out.mp4` | ~62 | 全程弃视频，只取尾帧 missing-audio.png |

净母带 ≈ 282s；freeze 回放帧另拍（见第五节）；加布景/NPP/NG 缓冲按
**2–3h 占机**（真人离机，开始前与用户确认时段）。
注意 t0/t1 输出路径写到录制目录而非工程内（工程目录是仓库，不污染）。

## 五、freeze 表（14 张；除 contact 外全是真终端回放帧，禁伪造）

瞬刷/超长输出一律 hf-06 工艺：报文稳定后**鼠标滚轮上滚 3 格**取静态帧，
**Shift+PgUp 禁用**（wt 无此绑定，PgUp 被 doskey 吃）。

| 文件 | 出处 | 拍摄命令（工作区相对） | 入镜要点（逐字对拍 PROBE-NOTES） |
|---|---|---|---|
| freezes/hash6-run.png | t2 尾帧 | — | 六行 Hash 全 `2057D037…C6C5A83`（大写），六个 Path |
| freezes/frames-dir.png | debug/captured-frames | `dir captured-frames \| more` 滚到编号段＋尾行 | `frame_000000.jpg` 六位编号；尾行 **390 个文件** |
| freezes/debug-tree.png | debug/ | `tree /F debug`（若太长先 `tree debug` 不带 /F） | compiled/、capture-attempt-0/worker-0…2/、captured-frames/、audio*.m4a、video-only.mp4、output.mp4、perf-summary.json、render.log |
| freezes/perf-ledger.png | debug/perf-summary.json | `type perf-summary.json` 滚轮 | stages 各段毫秒、workerSizing、captureCalibration(p95Ms)、tmpPeakBytes |
| freezes/pngseq-dir.png | seq/ | `dir seq` | frame_000001.png（**png 从 1 起**）390 张＋audio.m4a＋尾行约 3.2MB |
| freezes/gate-multi.png | logs/run-a.log | `findstr /C:"streaming-encode gate" logs\run-a.log` | `"enabled":false,"reason":"multi_worker" … "workerCount":3 … "maxDurationSeconds":240` |
| freezes/gate-stream.png | logs/hw-a.log | `findstr /C:"streaming-encode gate" /C:"capture_streaming" /C:"captureMode" logs\hw-a.log` | gate `enabled:true,reason:"single_worker",workerCount:1`；phase `capture_streaming`；`captureMode":"drawelement"` |
| freezes/hf07-timing.png | **仓库** projects/hf-07/build/render.log 第 7313–7314 行 | `more +7312 ..\..\hf-07\build\render.log`（彩排微调行号） | `drawelement capture · hardware gpu …` ＋ `53.1 MB · 9m 19.2s video · rendered in 41m 43.3s` |
| freezes/worker-sizing.png | debug/perf-summary.json 的 workerSizing 对象＋run-a.log:58 | 先 type JSON 滚轮，不够再补 `findstr /C:"worker_resolution" logs\run-a.log` | cpu/mem/frame/heap 四账 6/5/13/5 与 resolved workerCount:3；**JSON 字段名彩排先 dump 目验**（探针未逐字登记） |
| freezes/src-blackbar.png | npx 缓存 dist chunk（sizing＝chunk-D5EJCP26.js；parallel router＝chunk-3WG63KFW.js） | NPP 打开，`HF_DE_PARALLEL_MIN_MEM_MB`/24576 与 0.7.52 注释同屏 | **注释原文探针期是转述非逐字**：彩排先 grep 定位（vertical/black/tile/0.7.52 关键词），拍真原文；若原文无「黑条」字样，改拍 24576 常量＋router 判定，口播/卡不添字 |
| freezes/strict-abort.png | t4 尾帧（或 logs/bad-lint-strict.log） | — | `Aborting render due to lint issues`，rc=1 |
| freezes/missing-audio.png | t5 尾帧（或 logs/mm-be.log） | — | `Render blocked by 1 correctness warning: audio_processing_failed: Audio mix failed; output would be video-only`，rc=1 |
| freezes/no-timeline-warn.png | logs/bad-lint-default.log | `findstr /C:"45 seconds" logs\bad-lint-default.log` | `producer polls for timeline registration for up to 45 seconds … Add data-no-timeline` |
| artifacts/redblock-30-150.png | **非终端**：bad-lint/f01.png（第30帧）＋f02.png（第150帧） | `python oneoffs/make_redblock_contact.py`（PIL 横拼＋暗色标注） | 左「第 30 帧 · 1.0s · x=246」右「第 150 帧 · 5.0s · x=966」；容器 .shot 1120×644 contain，出图 1120 宽整倍数 |

尾报里的钉版行 `This project pins hyperframes@0.8.107 (latest 0.8.181).`
正好入镜，别遮（第二季悬念＋钉版纪律）。

## 六、录前检查（按序）

1. `python oneoffs/setup_scenes.py init`（非沙箱；含一次 --debug 重跑约 70s），
   再 restore 一次验幂等。
2. `python oneoffs/run_rehearsal.py`——全部 case PASS：
   六 mp4 sha256 全等且＝`2057…c6c5a83`、captured-frames 390 JPG、
   seq 390 PNG＋m4a、三日志尾报逐字匹配（68.1/52.4/41m43.3）、
   bad-lint/missing 工程 6s 且无 timeline 脚本、perf-summary workerSizing 字段存在。
   **实测 t3/t5 墙钟并回填本表第三、四节**（45s 等待是否真发生）。
3. `python oneoffs/check_anchors.py`——退出码 0 才开拍（目录镜像、
   文件名 soft-a…hw-b、日志锚点、chunk 源码锚点）。
4. wt 目验：暗色、22px、`hf08-rec` 标题；pwsh tab 能无 profile 秒开；
   NPP 暗色 zoom=0 Wrap=no（src-blackbar 一行长代码别折）。
5. **不跑 warmup**；但可在 t0 录完之后、t1 之前目验 t0 尾报数字
   （t1 本身就是热态第二跑）。
6. 黑屏/休眠关闭、通知静音；录制前对 ALT/CTRL/SHIFT/WIN 发 keyup
   （hf-05 Alt+Tab 事故预防）。
7. 管道坑：量退出码别接管道（`$?` 是 tail 的码）。

## 七、录后流程

1. 每 take 自动抽 2s/帧到 `F:\_hftest\hf08-rec\frames\`，立即 contact
   目验＋尾帧彻查（尾报数字逐字对第三节；sw 不是 1m0x 整段 NG）。
2. 母带归位（gitignored）：`copy F:\_hftest\hf08-rec\takes\*.mp4 media\`；
   freeze 14 张按 VIDEOS 路径归位 `media/freezes|artifacts`。
3. **粗切**：`cut_shorts.py frames`→目验→回填 CUTS→`cut`：
   6 short（hash 7.9／sw1 5.2／sw2 4.8／hw1 4.8／hw2 6.8／badlint 8.3）
   宁长勿短＋同名尾帧 freeze。
4. CFR 双闸（`videos/` 下）：
   `python -m videopipe probe-fps projects/hf-08/media/t*.mp4` 必须 exit 2；
   `python -m videopipe probe-fps projects/hf-08/media/shorts` 必须 exit 0。
   精切四参数 `-vf fps=30 -g 30 -keyint_min 30 -movflags +faststart`。
5. **二切**（需要时）：sw/hw 两段同源切点（1.0/60.5、5.0/44.5）已在
   VIDEOS 注释钉死，data-media-start 按精切实测回填，偏差 ≤0.1s。
6. **对齐 make_video**：去 `--cards-only`，按 CUTS 实测改 data-duration；
   媒体缺失占位分支删掉（VIDEOS 块已写全 19 引用）。
7. `python make_video.py`→check 0 error（基线 22 warning）→snapshot
   录屏与右卡同屏目验（重点 216.8/244.8/278.3/365.4/406.2 五录屏位＋
   全部 freeze 位）→render（非沙箱，UHD620 约 40min）→finalize 拼封面
   2s→F2（见 #611）。

## 八、已知风险点

1. **t0 冷态不可复现性最高**：68.1 靠校准浏览器首启；开机/重置后第一条
   录它，不预演。若探针后机器又跑过 render，重启 wt 不够，需重启电脑或
   等 Chrome 缓存自然冷——彩排先验冷态恢复手法（删哪个缓存目录）。
2. **尾报数字漂移**：sw 1m0x、hw 52±3、setup 16.4 是口播/卡片钉死值；
   setup 16.4 若在启动段 cut 里出现（sw1 源内 1–6.2s 太早，不含），
   Timing 行必须逐字对。hw2 含 `encode (during capture) 40.5s` 是
   「边抓边编」教学点，尾报若换措辞以真机为准、口播不添字。
3. **45s 等待**：t3/t5 母带中段各有一段 producer 轮询死等，录制不可中断；
   成片只取头/尾。若彩排实测两工程被识别为 no-timeline 不足 45s
   （例如 static-frame dedup 快返回），以实测回填，no-timeline-warn
   freeze 仍从日志回放拍（warning 是 lint 期输出，不依赖等待发生）。
4. **--debug 目录易失**：jobId 随机、在 npx 缓存深处；setup 跑完立即
   copy 到固定路径，freeze 只拍拷贝。
5. **src-blackbar 逐字未取证**（见 freeze 表）：唯一允许「拍不到预想文案」
   的位，以 chunk 源码实文为准，不允许后期补字。
6. **Get-FileHash 输出宽度**：Format-Table 在 1600 宽窗口可能把 64 位
   Hash 折行；彩排确认单行（必要时 `Format-Table -Wrap:$false` 或
   `Format-List`，但 list 太长——优先调 wt 窗口/字号让 table 单行）。
7. **六个文件名是 setup 改名的**（body-a→soft-a 等）：录屏目录/命令/
   指纹表必须三处一致；check_anchors 校验。
8. **ERR_UNSAFE_PORT flake**（hf-06 教训）：headless Chrome 偶发拒连
   抽中 unsafe 端口，非录制复跑即恢复，不改等待常量；render 若因 flake
   失败，t0 冷态作废需重新制造冷态——所以彩排连跑 3 次 render 估 flake 率。
