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

无注入 subprocess 标定（非录制态）：

| 命令 | 非录制态墙钟 | 录制态实测（gdigrab 同机负载） | 常量/片长 |
|---|---|---|---|
| `check .`（冷/热） | 24.1s / 20.1s（六态 20.0–21.2s） | 报文 26–27s 刷、`Check passed/failed` ~27s | **CHECK_WAIT=28**，run 片 34 |
| `… keyframes` | 7.9s | 列表 ~9.5s 才刷出 | **KF_WAIT=16** |
| `… keyframes --shot rec-shots/onion.png` | 14.1s（曾测 16.4s） | GPU probe 后 saved 路径在第二段 **44s+**（20s 仍停在 probe） | **SHOT_WAIT=28**，t7a 片长 **52** |
| `… inspect .` | 15.8s，rc=0 | deprecated 三行 ~15s | INSP_WAIT=21，片 25 |
| `… beats .` | 8.3s，**rc=1** | 红字 ~12s（10s 未出） | **BEATS_WAIT=18**，片长 **22** |

`No music track found. Add data-timeline-role="music" to the <audio>…` 逐字以第三节为准。
全新 cmd 首轮 npx 冷启另算（hf-04 实测 68s），正式录前必须跑 `warmup` 吞掉。
录制态 gdigrab 同机争用比 hf-04 经验更重，keyframes/shot/beats 首轮常量全偏小、
均按母带实证加大（见第七节）；check 尾帧必须拍到 `Check passed/failed`。

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
| t2b-dur-run | 接态 | check 黄⚠ passed（warning 瞬刷，完整窗 25.9–26.4s，freeze 26.05） | 34 | dur-run |
| t3a-overflow-run | reset s2 | check 越界双修复（warning 完整帧 ~26.4s，freeze 26.45） | 34 | overflow-run |
| t3b-root-fix-npp | 开 NPP | tail 行静场→root L17 `10`→`13`、存盘 | 14 | root-fix（上） |
| t3c-root-fix-run | 接态 | check 复绿 11/11 | 34 | root-fix（下） |
| t4a-color-bad-npp | 接 t3 末态 | L11 `#e6edf3`→`#1a1f26`、存盘 | 11 | color-bad（上） |
| t4b-color-bad-run | 接态 | check 红 5✗ rc=1（全片高点） | 34 | color-bad（下） |
| t4c-color-fix-npp | 接态 | →`rgb(93,97,102)`、存盘 | 12 | color-fix（上） |
| t4d-color-fix-run | 接态 | check 复绿；**分两行** echo %ERRORLEVEL%→0 | 44（重录） | color-fix／errlvl-zero |
| t5a-same-track-run | reset s4 | check 全绿 6/6 | 34 | same-track-run |
| t5b-dom-swap | 开 NPP | Scintilla 消息选 L20行首–L22行首＋MOVESELECTEDLINESUP×2 整块上移、存盘（无剪贴板） | 17 | dom-swap |
| t5c-dom-swap-run | 接态 | 对调后 check 仍绿 | 34 | （备尾帧） |
| t5d0-occlude-code | reset s6＋NPP | block L22-25 静场（整块新增跳切） | 6 | occlude-run（上） |
| t5d-occlude-run | 接态 | check text_occluded 9/9 红 | 34 | occlude-run（下） |
| t6a-nulltarget-code | reset s5＋NPP | L26 `#sut` 拼写行静场 | 6 | nulltarget-run（上） |
| t6b-nulltarget-run | 接态 | check 3⚠ passed | 34 | nulltarget-run（下） |
| t7a-kf | reset s0，关 NPP | keyframes 列表→cls→--shot 洋葱皮（saved 路径 44s+） | 52（重录） | kf |
| t7b-inspect | 接态 | inspect deprecated | 25 | inspect-dep |
| t7c-beats | 接态 | beats 无音乐轨（rc=1） | 22（重录） | beats |

净素材 ≈ 8.4 min；加 NPP 五次冷启（30–60s/次，录制外）与 take 间布景，
单次全推约 20–30 min；留 NG 缓冲按 2–3h 占机。

## 五、录前检查（按序）

1. `python oneoffs/check_anchors.py`——退出码 0 才开拍（锚点/编辑序列磁盘镜像）。
2. 便携 NPP 目验：暗色主题、zoom=0、Wrap=no。**不要指望 Alt+Up/Down 行移动**：
   便携 NPP 7.8.8 默认无此快捷键映射（彩排实测无效），整块行移动走 Scintilla
   消息 2620/2621（见第七节 t5b 工艺）。
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
4. CFR 硬闸（在 `videos/` 下跑；glob 是 `t*.mp4` 不是 `t-*.mp4`——本片母带
   命名 t1-/t2a-，t 后直接数字，写错模式空集会 vacuous pass 报「CFR 0 段」）：
   `python -m videopipe probe-fps projects/hf-05/media/t*.mp4` 必须 **exit 2**（原始 VFR）；
   `python -m videopipe probe-fps projects/hf-05/media/shorts` 必须 **exit 0**。
   精切四参数 `-vf fps=30 -g 30 -keyint_min 30 -movflags +faststart` 已在 cut 模板。
5. 后续：TTS（蝉镜 24k mono）→whisper/align/cues→measure_offset 逐片→
   make_video（12 幕，终端缩左 58%＋右卡，freeze＝尾帧 PNG）→check→render（非沙箱）→F2→PR。

## 七、坑（2026-10-16 正式代录回填，已全部落锤）

**1. check 录制态墙钟＝26–27s，CHECK_WAIT=28 够但不宽裕。**
无注入标定时热态 20.1s，gdigrab 同机负载下各 check take 均在 26.0–26.9s
刷完报文、~27s 回提示符；30s 探针帧尾态已稳定。六态一致，常量一处控全局。

**2. t4d 首版 echo %ERRORLEVEL% 被片长切掉（漏网 NG，切前 contact sheet 才抓到）。**
term_cmd 逐字实测约 0.07s/字（`delay=.035` 外加 keyup 开销），CHECK 回车约在
片内 5.8s。首版 `sleep(CHECK_WAIT+5)=33s` 后才敲 echo（18 字），打完约 35.5s
动作结束——但片长只有 40s，33.5–39.3s 逐帧全是无提示符的静态终态，echo
零字符入镜。改 `sleep(28)`（echo 开打 ~34s，落在 27s 回提示符 7s 后，不进
npx stdin）、片长 44s、尾帧 0 定格留 8s，单独重录。教训：**带第二条命令的
take，切点要按打字实测速率反推，不能只数 sleep**。首版废片留证在
`F:\_hftest\hf05-rec\quarantine\`。
入镜形态落锤：check 回提示符后另起一行敲 `echo %ERRORLEVEL%`，回显 `0`；
严禁同行 `check . & echo …`（cmd 同行在解析时展开，读到旧值＝假结果）。

**3. t5b 系统剪贴板被抢占，整块行移动改纯 Scintilla 消息。**
首版走 Ctrl+X/Ctrl+V，录制期间后台程序抢占剪贴板，title 行被注入无关本地
路径（且含真实用户名），整片作废。正解＝按 UTF-8 **字节位置**发
SCI_SETSELECTIONSTART(2142)=L20行首 / SCI_SETSELECTIONEND(2144)=L22行首
（含 L20/L21 各自尾换行，移动后不挤行），再 SCI_MOVESELECTEDLINESUP(2620)
连发两次。键盘 SHIFT+DOWN 在 Ctrl+G 之后建选区锚点不稳（彩排实测选区错位、
块反向下落）；消息建选区彩排 swapped=True、行集合逐字不变。
**消息号必须查本地 Scintilla 头文件**（F:\_hftest\Scintilla-788.h），凭记忆
错位两轮：2187/2188 实为 SETSELECTIONSTART/END 的错误猜测；另 2050＝
SCI_STYLECLEARALL（误当 SETFORE 发出会清空全部样式，行号槽排查在此耗最久），
2051/2052 才是 SETFORE/SETBACK。

**4. 外部焦点 Alt+Tab 事故（guard 正确拦截）。**
一批次中 guard 报 `前台 ThumbnailDeviceHelperWnd 不属于隔离录制环境`，断在
Ctrl+S 前的闸上；废片前 7s 录到 Claude Code TUI、随后弹 Alt+Tab 切换器。
取证结论：activate 走 AttachThreadInput＋SetForegroundWindow（不发 Alt）、
BlackMat.behind 用 NOACTIVATE，脚本链不产生 Alt+Tab，只可能外部物理输入或
早前探针热键残留 ALT 按下态叠加 SetForegroundWindow。处置＝9 分钟只读轮询
确认无人在机、验明僵尸便携 NPP 的 exe 路径属 F:\_hftest\npp-local 后才杀、
不碰日常安装版 NPP。**预防固化：每批次/重录前 keybd_event 对
ALT(0x12)/CTRL(0x11)/SHIFT(0x10)/WIN(0x5b,0x5c) 发 KEYUP(0x2) 清异步键态。**

**5. warning 瞬刷（t2b/t3a）：完整可读窗 <0.5s。**
timeline_element_missing_timing 完整四行只在 25.9–26.4s；
clip_ends_past_root_duration 完整帧 ~26.4–26.8s。3s 稀疏探针必然漏，
切 shorts 的 freeze 必须用加密帧定位（CUTS 已填 26.05/26.45）；make_video
概念卡若需定格读全文，用 freezes PNG 而非指望观众读运动画面。

**6. 布景 CRLF 坑（setup_scenes）。**
Windows 上 Path.write_text 默认把 \n 翻成 CRLF：权威备份带 \r 后行号不变、
UTF-8 字节位置全偏，t5b 的 2142/2144 字节选区立即错位。已给全部 write_text
加 `newline="\n"`，check_anchors 新增七态 bytes 闸（b"\\r\\n" 即 FAIL）。

**7. 便携 NPP 暗色主题绝对路径坑（换机重建必查）。**
config.xml 的 stylerTheme 被钉到 `%APPDATA%` 下浅色 stylers.xml 时整个编辑区
白底；必须指便携自身 stylers.xml。该配置在仓库外（F:\_hftest\npp-local）、
不入 git，换机/重建便携 NPP 后先查此项。即便暗色生效，行号槽 STYLE_LINENUMBER
(33) 在这版启动流程不被应用，npp_open 词法样式落定后手工补发 2052/2051。

**8. gdigrab 录制态墙钟全面上调（见第二节表）。**
KF_WAIT 12→16、SHOT_WAIT 19→28（--shot 在 GPU probe 后还要等 saved 路径，
首录 19s 尾帧停在 probe）、BEATS_WAIT 13→18；t7a 片长 39→52、t7c 17→22。

- cmd 输入排队兜底落锤：固定 sleep 内命令确会进 conin 缓冲、退出码语义仍正确
  （交互行执行前展开），但画面穿帮——t4d 已把 echo 排到提示符回来 7s 后，未复现。
- 已知：NPP 外部覆盖文件前必须先关实例（reset 流程已保），否则「重新加载」框
  由 _dismiss_modal 处理（Alt+Y）；close_any_npp 三轮关不掉且 exe 非 npp-local
  会拒绝强杀。
- 管道坑（非本片）：`check | tail` 后 `$?` 是 tail 的码；量退出码别接管道。

## 八、精切台账（2026-10-16，#567）

20 母带 → **21 条 shorts＋21 张 freeze**（t4d 重录版拆 color-fix-run／
errlvl-zero 两条；edit/run 成对拆开给后期跳切）。切点见 cut_shorts.py 的 CUTS，
目验依据＝20 张稀疏 sheet＋`build/frames/extra` 加密帧（t2b 25.9–26.9、
t3a 24.8–27.5、t7a 40–51.8、t4d 重录 26.5–43）。

双闸实测：

- 原始 20 母带全 VFR，r=30.000、**avg 5.15–5.63fps、偏差 81–83%**（本片 gdigrab
  打嗝比 hf-04 重；终端静态画面多，fps=30 重建后可用），probe-fps **exit 2**。
- 21 shorts 全 CFR（avg 30/1），probe-fps **exit 0**。
- 关键 freeze 已逐张目验：dur-run 26.05（missing_timing 全文）、
  overflow-run 26.45（past_root_duration＋双 Fix）、errlvl-zero 40.0
  （echo 行＋0＋复提示符）、kf 50.0（onion saved 绿路径＋proj-1 item 列表）。
