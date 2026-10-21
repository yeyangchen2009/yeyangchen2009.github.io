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
| PowerShell | **不另开 tab**：cmd 内敲 `powershell -NoProfile -NoLogo` 进子进程，跑完 `exit` 回 cmd（本机无 pwsh7，只有 Windows PowerShell 5.1） | 窗口标题恒锁 hf08-rec，guard 零风险 | Get-FileHash 六连（t2） |
| 便携 NPP | `F:\_hftest\npp-local\notepad++.exe -multiInst -nosession <chunk.js>` | 类名 Notepad++ 且标题含 `chunk-3WG63KFW.js` | 仅 src-blackbar 一张 freeze |

- 录区：gdigrab 物理 **(0,0,1600,920)@30**；系统 DPI 150%，坐标全是物理像素。
- 右边 12px 透明带、BlackMat 垫窗、鼠标 park (12,884)——同 hf-06。
- 无浏览器/CDP/dev server（render 自己开无头 Chrome，不算身份；guard 只认
  wt 与 NPP，用户回机切窗下一注入立即 `UnsafeForeground` 中止）。
- 终端三环境变量（同 hf-06）：`HYPERFRAMES_FONT_CACHE_DIR=F:\_hftest\.cache\fonts`、
  `HYPERFRAMES_NO_UPDATE_CHECK=1`、`HYPERFRAMES_SKIP_SKILLS=1`。
- `--suppressApplicationTitle` 必须有：npx 会 SetConsoleTitle。
- 终端 1600×920 录区在分镜里缩到 **1120×644（.term，object-fit:fill）**，
  右 620px 让给概念卡；字号别缩：wt 配置沿用 hf-06 录制档（22px 左右）。

## 二、布景（setup_scenes.py，目标工作区 `F:\_hftest\hf08-media`）

探针期资产已存在，setup 只搬运/重跑，不重新做实验。2026-10-21 脚本已落
（oneoffs/setup_scenes.py，子命令 init/refresh-debug/verify/list）：

| 布景项 | 来源（探针期实物） | setup 动作 |
|---|---|---|
| 沙盒工程 | 仓库内 `videos/projects/av-sync-calib`（13s/390 帧/黑底五白闪） | 不 copy，录屏终端 cwd 直接用仓库真名路径（render 自报路径入镜，路径无用户名） |
| 六权威 mp4 | `hf08-probe\body-a/body-b/w1/hw-a/hw-b/dbg.mp4`（全 61145B、sha256 六连同） | copy 到 `hashes\` 并改名 **soft-a/soft-b/1015-old/w1/hw-a/hw-b.mp4`，逐件 sha 闸；copy 不改字节 |
| 1015-old 底档 | probe-seeds 未留独立文件；六跑字节同 hash＝内容寻址证据，**用 dbg 那份改名顶替**，manifest 记来源 | 同上，改名 1015-old.mp4 |
| 坏工程 | `hf08-probe\bad-lint\`（6s 红块 rAF，无 timeline 注册；含 f01/f02 备用帧＋默认产物 24527B） | 整目录 copy 到 `bad-lint\` |
| 缺音轨工程 | `hf08-probe\missing-media\`（audio src=media/nope.wav） | 整目录 copy 到 `missing-media\` |
| --debug 实物 | `.debug/<jobId>/` 在 **npx 缓存目录内、jobId 随机且可能被清** | init 现跑一次 `render . --no-browser-gpu --debug -o debug-output\dbg.mp4`（约 70s），跑前跑后取 .debug 差集定位新 job，**立即整目录搬**到 `debug\`，断言 compiled/index.html、render.log、perf-summary.json、video-only.mp4、output.mp4、390 JPG（frame_000000–000389）、输出 mp4 sha 全同 |
| png-sequence | `hf08-probe\seq\`（390 PNG frame_000001 起＋audio.m4a） | copy 到 `seq\` |
| 11 份日志 | `hf08-probe\*.log`：run-a/run-b/w1/hw-a/hw-b/bad-lint-default/bad-lint-strict/mm-be/mm-strict/dbg/seq.log | copy 到 `logs\`，录屏尾报数字的「二遍对拍」底本 |

幂等动作＝再跑一次 `init`（脚本先删整棵布景重建）；六 mp4 严禁任何工具
触碰（缩略图生成不改字节，但别过编辑器）。布景台账 stage-manifest.json。

## 三、命令与等待常量（2026-10-21 run_rehearsal 真机回填）

| 命令（av-sync-calib） | 真机墙钟 | 尾报关键数字 | take |
|---|---|---|---|
| `render . --no-browser-gpu -o …` **冷态首跑** | **68.1s**（探针冷态；录制日 t0 必须冷态） | `rendered in 1m 8.1s`，setup 16.4s，capture 33.6s，encode 14.2s | t0 |
| 同上热态复跑 | 彩排 flaky 三连 51.8/51.3/59.9s，hash 全同、零 UNSAFE_PORT | 热态 setup 5.2–5.5s（**不录**，对拍用） | — |
| `render . --browser-gpu -o …` | **52.4s**（探针热态） | capture 40.5s 与 `encode (during capture) 40.5s` 完全重叠 | t1 |
| bad-lint 默认 render（6s 工程） | **141.2s**（两轮 45000ms 等待都发生，poll45 命中 2 次） | `2 error(s), 1 warning(s)` → Continuing，exit 0，产物 24527B | t3 |
| bad-lint `--strict` | **12.6s**（lint 编译期拦，无等待） | `Aborting render due to lint issues`，exit 1，无产物 | t4 |
| missing-media 默认 render | **15.6s**（缺音轨 mix 期即拦，**无 45s 等待**——早先两轮等待预估作废） | `Render blocked by 1 correctness warning: audio_processing_failed`，exit 1 | t5 |
| `Get-FileHash` 六连 | 秒回（Format-Table 单行不折，彩排已验） | 六行 Hash 全同 | t2 |

警告逐字（日志行 47/74，334 字符）：`[FrameCapture] Sub-composition
timelines not registered after 45000ms: main.` 后接 data-no-timeline
skip 提示；另有行 49/76 `sub_timeline_readiness_timeout` 长变体（含
`timeoutMs: 45000`）。注意是 **45000ms** 不是「45 seconds」（findstr
锚点已按真机串）。

**冷态纪律（本集头号坑）**：t0 要的尾报是 **68.1s**，差的 12s 在
capture-calibration（16.4 vs 热 5.5）。当天录屏**第一条就是 t0**，
之前不许跑任何 render 做 warmup（与 hf-06「先 warmup 吞冷启」正好相反）；
t1 紧接 t0 跑正好是热态。NG 重录 t0 若浏览器已热，setup reset 后
另起全新 wt 再录；尾报 NG 阈值：sw 必须报 **1m0x s**（口播钉「68 秒」），
hw 52±3s。

## 四、take 表（6 母带；录制顺序＝ALL_TAKES，不可调换）

母带时长＝record_segments.record(...) 实参（垫幕 2＋打字 WAIT＋尾帧 3；
WAIT 已按 2026-10-21 run_rehearsal 真机回填）：

| take | 目录/shell | 命令 | record 时长 | 成片取用（VIDEOS 已预填） |
|---|---|---|---|---|
| t0-sw | av-sync-calib／cmd | `npx hyperframes@0.8.107 render . --no-browser-gpu -o F:\_hftest\hf08-rec\sw.mp4` | 75.0（WAIT 70，覆盖冷态 68.1） | sw1 源内 1.0–6.2（5.2s 启动行）；sw2 源内 60.5–65.3（4.8s Timing） |
| t1-hw | 同窗接跑／cmd | `npx hyperframes@0.8.107 render . --browser-gpu -o F:\_hftest\hf08-rec\hw.mp4` | 64.0（打字 4.5＋WAIT 54.5） | hw1 源内 5.0–9.8（4.8s probe 行）；hw2 源内 44.5–51.3（6.8s Timing＋streaming） |
| t2-hash | hashes／**powershell 子进程** | `Get-FileHash soft-a.mp4,soft-b.mp4,1015-old.mp4,w1.mp4,hw-a.mp4,hw-b.mp4 -Algorithm SHA256 \| Format-Table Path,Hash -AutoSize` | 22.0（垫4＋进 PS 3＋打字6＋等6＋尾3） | hash6 源内 0.8–8.7（7.9s）＋尾帧 freeze hash6-run.png（at 14.0） |
| t3-badlint | bad-lint／cmd | `npx hyperframes@0.8.107 render . -o out.mp4` | **149.5**（打字 4.5＋WAIT 140；真机 render 141.2） | badlint 源内 0.5–8.8（8.3s：lint 2 error＋Continuing）；两轮 45000ms 等待整段弃 |
| t4-strict | bad-lint／cmd | `npx hyperframes@0.8.107 render . --strict` | 22.5（打字 4.5＋WAIT 13；真机 12.6） | 全程弃视频，只取尾帧 strict-abort.png（at 19.0） |
| t5-missing | missing-media／cmd | `npx hyperframes@0.8.107 render . -o out.mp4` | **26.5**（打字 4.5＋WAIT 17；真机 15.6，无等待） | 全程弃视频，只取尾帧 missing-audio.png（at 22.0） |

净母带 ≈ 359.5s（彩排回填值）；freeze 回放帧另拍（见第五节）；加布景/NPP/NG 缓冲按
**2–3h 占机**（真人离机，开始前与用户确认时段）。
注意 t0/t1 输出路径写到录制目录而非工程内（工程目录是仓库，不污染）。

## 五、freeze 表（14 张；除 contact 外全是真终端回放帧，禁伪造）

**2026-10-21 全量彩排 10/10 目验通过**，hf-06 的「滚轮上滚 3 格」工艺
本集基本不用：长输出（tree 411 行／perf-summary 575 行）一律 **more 分页
定点**，滚轮要回几百行不可靠。三个彩排教训已固化进 record_segments.py：

1. **more 退出竞争**：`q` 退 more 后 conPTY 重建提示符有窗口期，立刻敲
   下一张 `cd` 整行丢键（彩排三例三验：debug-tree/worker-sizing 后的 cd
   全丢，perf-ledger/no-timeline 因此 cwd 错误）。统一走 `quit_pager()`：
   q → 0.8s → 空 ENTER 同步（more 已自动退出时 q 残留被 ENTER 当命令吞，
   报错由下张 cls 清）。
2. **chcp 65001**：控制台默认 GBK(936)，hf-07 尾报的 `◇`/`·` 乱码成
   「鉫？」「路」。`open_rec_term` 每次幂等发 `chcp 65001 >nul`
   （`_ensure_utf8`，随后 cls 清回显）；对 render/findstr/dir 无副作用。
3. **浅色窗鼠标穿帮**：NPP 水平滚动条上箭头显形；src-blackbar 单独
   park 到录区物理区外 `(1650,950)`（grab crop 0,0,1600,920 必然不含）。

| 文件 | 出处 | 拍摄命令（工作区相对） | 彩排目验结果 |
|---|---|---|---|
| freezes/hash6-run.png | t2 尾帧 tail-freeze@14.0 | — | 六行 Hash 全 `2057D037…C6C5A83`（大写），六个 Path；at 录后按 contact 微调 |
| freezes/frames-dir.png | debug/captured-frames | `dir captured-frames`，零滚动 | ✓ 尾屏＝frame_000375–389＋**390 个文件 5,069,220 字节**＋2 个目录 |
| freezes/debug-tree.png | STAGE 根 | `tree /F debug \| more`，截完 q | ✓ 首屏：6 个根文件＋capture-attempt-0/worker-0…2＋capture-calibration＋captured-frames/frame_000000–001（More 贴底） |
| freezes/perf-ledger.png | debug/ | `more +24 perf-summary.json`，q | ✓ resolution 1920×1080/videoCount 0/audioCount 1＋**stages 十键全在**：compileOnly 218/probe 126/compile 361/audio 547/capture 32851/captureFrame 28045/setup 4806/encode 12245/assemble 1817（行 31–43，+24 定点） |
| freezes/pngseq-dir.png | STAGE 根 | `dir seq`，零滚动 | ✓ frame_000376–390＋**391 个文件 3,335,581 字节**（390 PNG＋audio.m4a） |
| freezes/gate-multi.png | logs/run-a.log | `findstr /C:"streaming-encode gate" logs\run-a.log` | ✓ 254 字符软折 4 物理行：enabled:false/multi_worker/configFlag:true/workerCount:3/durationSeconds:13/maxDurationSeconds:240 全可读 |
| freezes/gate-stream.png | logs/hw-a.log（**备料**，分镜未消费，docstring 挂 m09） | 彩排改双 findstr `&&`：`findstr /C:"streaming-encode gate" logs\hw-a.log && findstr /C:"drawelement capture" logs\hw-a.log`，q 不用 | ✓ 一屏齐＝gate（enabled:true/single_worker/workerCount:1）＋尾报 `drawelement capture · hardware gpu … capture 40.5s · encode (during capture) 40.5s · assemble 1.6s`。原三串 OR 实测连 checkpoint 心跳共 5+ 条超一屏、gate 滚出顶，弃 |
| freezes/hf07-timing.png | **仓库** projects/hf-07/build/render.log（行号硬闸：41m43.3 在 7313–7316） | `more +7312 "<绝对路径>"`，quit_pager 收尾（仅 3 行 more 自动退出） | ✓ UTF-8 后 `◇` 路径行＋`53.1 MB · 9m 19.2s video · rendered in 41m 43.3s`＋capture/encode 39m 9.4s、assemble 1m 6.4s |
| freezes/worker-sizing.png | debug/perf-summary.json | `more perf-summary.json`（首屏），q | ✓ 11/12 字段可见：workers 3/boundBy contention/effectiveMax 6/cpu 6/mem 5/frame 13/heap 5/heapLimitMb 4288/totalMemoryMb 16278/cpuCount 8/multiplier 1；第 12 个 exceedsHeapAdvisory 被 More 行翻到次页（非教学点，接受） |
| freezes/src-blackbar.png | **chunk-3WG63KFW.js**（黑条注释＋24576 同文件；computeWorkerSizing 在 chunk-D5EJCP26.js） | NPP `-multiInst -nosession`（CHUNK_3W 钉死 npx hash 目录），Ctrl+F 搜 `vertical black slabs`，Esc 关栏，鼠标 park (1650,950) 再截 | ✓ 10933–10937 注释七行全、命中高亮、标题栏路径、状态栏 17,152 行/Ln 10933；鼠标已出框 |
| freezes/strict-abort.png | t4 尾帧 tail-freeze@19.0（或 logs/bad-lint-strict.log 回放兜底） | — | `Aborting render due to lint issues`，rc=1；at 录后微调 |
| freezes/missing-audio.png | t5 尾帧 tail-freeze@22.0（或 logs/mm-be.log 回放兜底） | — | `Render blocked by 1 correctness warning … audio_processing_failed: Audio mix failed; output would be video-only`，rc=1；at 录后微调 |
| freezes/no-timeline-warn.png | logs/bad-lint-default.log | `findstr /C:"not registered after 45000ms" logs\bad-lint-default.log` | ✓ 行47/74 两条 334 字符全文同屏（含 data-no-timeline skip 建议），各折 4 行 |
| artifacts/redblock-30-150.png | **非终端**：bad-lint/f01.png（第30帧）＋f02.png（第150帧） | `python oneoffs/make_redblock_contact.py`（PIL 横拼） | ✓ 已出图目验：左「第 30 帧 · 1.0s · 红块中心 x=246」右「第 150 帧 · 5.0s · x=966」，蓝标线压入卡顶 |

尾报里的钉版行 `This project pins hyperframes@0.8.107 (latest 0.8.181).`
若入镜别遮（第二季悬念＋钉版纪律）。freeze 全程零 Chrome，t0 前后任意
时点拍都不烤冷态；NPP 与 wt 互不干扰，freeze-all 约 2 分钟。

## 六、录前检查（按序）

1. `python oneoffs/setup_scenes.py init`（在 videos/ 下、非沙箱；含一次
   --debug 现跑约 70s），**再 init 一次**验幂等（脚本先删整棵布景重建）。
   init/refresh-debug 会烤热无头 Chrome，布景与彩排必须早于录制日完成。
2. `python oneoffs/run_rehearsal.py`——全部 case PASS：
   六 mp4 sha256 全等且＝`2057…c6c5a83`、captured-frames 390 JPG、
   seq 390 PNG＋m4a、三日志尾报逐字匹配（68.1/52.4/41m43.3）、
   bad-lint/missing 工程 6s 且无 timeline 脚本、perf-summary workerSizing 字段存在。
   **实测 t3/t5 墙钟并回填本表第三、四节**（45s 等待是否真发生）。
3. `python oneoffs/check_anchors.py`——退出码 0 才开拍（目录镜像、
   文件名 soft-a…hw-b、日志锚点、chunk 源码锚点）。
4. wt 目验：暗色、22px、`hf08-rec` 标题；cmd 内 `powershell -NoProfile
   -NoLogo` 子进程秒进、`exit` 回 cmd 标题不变；NPP 暗色 zoom=0
   Wrap=no（src-blackbar 一行长代码别折）。
5. **不跑 warmup**；但可在 t0 录完之后、t1 之前目验 t0 尾报数字
   （t1 本身就是热态第二跑）。freeze 10 张彩排已全过（第五节），录制日
   `freeze-all` 重拍即可——全程零 Chrome，安排在 t0 前拍也不破坏冷态，
   但注意 freezes/ 覆盖写，若想保留彩排片先手工拷走。
6. 黑屏/休眠关闭、通知静音；录制前对 ALT/CTRL/SHIFT/WIN 发 keyup
   （hf-05 Alt+Tab 事故预防）。
7. 管道坑：量退出码别接管道（`$?` 是 tail 的码）。

## 七、录后流程

1. 每 take 自动抽 2s/帧到 `F:\_hftest\hf08-rec\frames\`，立即 contact
   目验＋尾帧彻查（尾报数字逐字对第三节；sw 不是 1m0x 整段 NG）。
2. 母带归位（gitignored）：`copy F:\_hftest\hf08-rec\takes\*.mp4 media\`；
   freeze 14 张按 VIDEOS 路径归位 `media/freezes|artifacts`。
3. **粗切**：`cut_shorts.py frames`→目验→回填 CUTS→`cut`：
   **4 short**（不是 6）——sw/hw 各切一条从母带 0 点起的长段，
   rec-sw1/sw2、rec-hw1/hw2 靠 data-media-start（1.0/60.5、5.0/44.5）
   在同一文件内各取区间：hash6-run 9.2／sw-render 66.0／hw-render 52.0／
   badlint-run 9.5，宁长勿短；freeze 不在 cut 阶段抽（尾帧走 tail-freeze）。
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

1. **t0 冷态恢复手法已定稿（2026-10-21 源码核实）**：Chrome profile 是
   mkdtemp 临时目录、进程退出即弃；冷态差只来自 OS 文件缓存
   （chrome-headless-shell 二进制在 standby list）＋字体缓存（已重定向
   F:\_hftest\.cache\fonts）。**唯一可靠冷态＝重启电脑后第一条 render**；
   删 `~/.cache/hyperframes/chrome` 会触发重新下载、反而污染首跑墙钟，
   **禁止删**。录制日纪律：重启→不跑 setup init/verify、不跑 rehearsal、
   平时不手痒 npx render（这些都启 Chrome 烤热）；布景/彩排必须提前一天
   完成（已完成）。彩排日的 flaky 三连等 render 已把机器烤热，录制日
   务必重启。若 t0 因 flake 失败，重启电脑重新制造冷态后再录。
2. **尾报数字漂移（设计已规避）**：68.1/16.4/55.7/52.4 是口播钉死值，
   证据永久在布景 logs/（gate/perf/hf07 freeze 从日志回放拍，不依赖录制
   日墙钟）。分镜 rec-sw2（源内 60.5–65.3）/rec-hw2（44.5–51.3）拍的是
   **尾报前的 Timing 进行段而非结论行**，尾报本就不入动态录屏——唯一约束
   是录制区间内 render 仍在跑。二切按真机尾报秒 T 反推 data-media-start：
   sw 取 [T−7.6, T−2.8]（探针 T=68.1 对到现切点 60.5–65.3）、hw 取
   [T−7.9, T−1.1]（T=52.4 对 44.5–51.3），区间内须是滚动计时行无提示符；
   t0 母带 WAIT 70 即使盖不住尾报也无损失（成片只取尾报前两段）。hw2 含
   `encode (during capture) 40.5s` 是「边抓边编」教学点，该串来自
   hw-a.log 回放/真机滚动，真机若换措辞以母带为准、口播不添字。
3. **45000ms 等待（彩排已实测）**：只 t3 有——真机 141.2s、poll45 命中
   2 次（行47/49 与 74/76，等待 46161/45777ms），录制不可中断，成片只
   取头 8.8s；**t5 无等待**（缺音轨 15.6s 在 mix 期即拦）。若录制日 t3
   墙钟显著偏离 141s，以母带 contact sheet 实测为准，no-timeline-warn
   freeze 永远从日志回放拍（不依赖等待当场发生）。
4. **--debug 目录易失**：jobId 随机、在 npx 缓存深处；setup 跑完立即
   copy 到固定路径，freeze 只拍拷贝。
5. **src-blackbar 缓存路径硬编码**：record_segments.CHUNK_3W 钉死
   `F:\npm-cache\_npx\82df529928acbd64\…`（0.8.107 实例 hash）。npx 缓存
   若被清/重装，hash 目录改名即 NG——check_anchors 已动态按 package.json
   version 定位 dist 并验锚点；freeze 开拍前若 check 报缺件，按其打印的
   实际 dist 路径回填 CHUNK_3W（注释原文已逐字取证，不允许后期补字）。
6. **Get-FileHash 输出宽度**：Format-Table 在 1600 宽窗口可能把 64 位
   Hash 折行；彩排确认单行（必要时 `Format-Table -Wrap:$false` 或
   `Format-List`，但 list 太长——优先调 wt 窗口/字号让 table 单行）。
7. **六个文件名是 setup 改名的**（body-a→soft-a 等）：录屏目录/命令/
   指纹表必须三处一致；check_anchors 校验。
8. **ERR_UNSAFE_PORT flake**（hf-06 教训）：headless Chrome 偶发拒连
   抽中 unsafe 端口，非录制复跑即恢复，不改等待常量；render 若因 flake
   失败，t0 冷态作废需重新制造冷态。2026-10-21 彩排三连 flaky 全过、零
   UNSAFE_PORT（51.8/51.3/59.9s、hash 全同），本次风险低但不消除。
