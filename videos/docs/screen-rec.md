# 真人录屏代录 SOP（gdigrab · 素材先行）

触发条件：要录**真人操作演示**（编辑器敲码、终端命令、浏览器点击、DevTools）作为
b-roll 进 HyperFrames 片时，开拍前先读本文件。纯 HTML/SVG 动画不需要本文件——
那条路走 snapshot/render 的确定性逐帧路径，见 `hyperframes-agent.md`。

- 首个全量实战范本：`projects/hf-04/oneoffs/RECORD-NOTES.md`（12 take 台账、七坑
  全部带定量证据）；彩排期机制实测见同目录 `REHEARSAL-NOTES.md`；终端命令类 take
  范本见 hf-05/hf-06 同目录 RECORD-NOTES.md（第 10 节出处）。
- 配套：仓库根 `tools/screen-rec.js`（零依赖 gdigrab 录制器）；项目 `oneoffs/` 放
  本片编排脚本——从 hf-04 复制改造：`guard.py`（身份闸）、`cdp_ctrl.py`（CDP 原语）、
  `record_segments.py`（take 编排）、`cut_shorts.py`（抽帧＋精切）。
- 录屏素材是 **VFR 重灾区**，录完进 render 前有硬门禁（第 7 节），跳过必崩。

## 1. 录前硬闸（四条全过才开录）

1. **guard 三身份**：只认指定调试端口的隔离浏览器、便携编辑器（窗口标题含沙盒路径）、
   带锁标题的录制终端；用户日常窗口全程不碰，杀进程只按具体 PID/HWND。
2. **布景视觉定稿先于任一 take**：check_anchors 只保磁盘态、保不住视觉态。所有幕的
   布景权威态先冻结（seek 若干关键点目验 ＋ `getComputedStyle` 的 visibility/opacity/rect
   双证），备份为 backup 权威态后再录第一批 take。hf-04 的 seg6 因布景在 take 之后
   改定稿而整段作废，是本闸存在的原因。
3. **沙盒脱敏**：所有公开画面走仓库外沙盒目录（公开画面允许出现沙盒路径），
   不得出现用户目录名、邮箱等身份信息；dev server 的 cwd 必须是项目目录。
4. **录前四查**：三身份 ／ 用户空闲时长 ／ 沙盒磁盘锚点 ／ dev server 健康。

完成判据：四查记录在案；任 take 布景相对权威态有改动时，先重定权威态、再评估旧 take 作废。

## 2. 几何与两种 zoom（hf-04 标定值，换机重标）

| 量 | hf-04 值 |
|---|---|
| gdigrab 录区 | 物理 `(0,0)` 起 **1600×920 @30fps**（`--width/--height/--x/--y`） |
| 系统 DPI / 页面 zoom / dpr | 150% / 50% / 0.75（CSS 像素 ×0.75＝物理像素） |
| 窗口外框 | 右缘实体必须盖死录区边缘（hf-04 外框右缘 1612＞录区 1600，根治 hf-03 的 27px 穿帮） |

- **页面 zoom 只认真实键盘**：CDP `Input.dispatchKeyEvent` 合成的 Ctrl+- 打不进浏览器
  快捷键，必须 SendInput 真实键路（Ctrl+0 复位 ＋ 五击 OEM_MINUS，100→50%）。
- **DevTools zoom 相反**：只收 DevTools target 会话（dt_ws）上的合成键，真实键路打不进。
- **证据图 ≠ 视频帧**：CDP 截图是整屏 1920 宽，会带进录区外的后台窗口，**不能当穿帮
  证据**；穿帮裁判只认 gdigrab 视频帧，用 PIL 对录区边缘条带做像素亮度量化。

## 3. 双轨自检：截图对 ≠ 上屏对

CDP `captureScreenshot` 与屏幕上屏是两个通道。Edge 的 GPU swapchain 在锁屏/休眠/
隔夜无人值守后可能挂起：**页面活着、CDP 截图全绿，屏幕整块均匀灰**。

- 录制就绪判定必须双轨：gdigrab 同源截屏做特征像素探测 ＋ CDP 截图复核。
- 判出「页面活而屏幕灰」时跑合成自愈（最小化→还原强制重建 swapchain），
  自愈后重检再录；不要只信 CDP 就开录。
- 隔夜/锁屏后的第一批 take 默认带灰屏自检。

## 4. 清场：浏览器扩展是画面里的第三者

隔离 profile 里的扩展仍会在页面注入元素（hf-04 抓到沉浸式翻译的红色圆钮贴 player 右缘）：

- 注入物常在 **Shadow DOM** 内：宿主 0×0，`document.elementsFromPoint` 只能摸到宿主；
  由扩展异步注入，**reload 即复发**。
- 处置：CDP 注入 `#__rec-hide-ext`（`display:none!important`）＋ MutationObserver
  兜底延迟注入；**每次 reload 后必须重注**，编排脚本要把重注点排进每个 take。
- 回溯旧素材用录区几何量化（第 2 节），不靠肉眼一张张看。

## 5. 录「播放结果」走裸 player，不录 Studio Preview

Studio 的实时 Preview 画布与渲染/抓帧**不是同一条确定性路径**，同一时间线可连续给出
不同坏画面。要录播放结果、又不要 Studio 壳时：

- 用无任何可见控件的裸 player 页（不会拍到假按钮）；
- 播放由 CDP 求值 `window.__player.play()` 触发（与点三角同一条实时引擎路径，画面就是
  播放本身）；**CDP 合成 Space 键不触发**页面输入管线，不能靠合成键开播。

## 6. 录中与录后

- 每个 take 录完立即抽帧目验 ＋ **尾帧彻查**；废片当晚重录覆盖，不带废片进入剪辑。
- guard 期间前台被系统外壳瞬抢（`Shell_TrayWnd` 等）时：身份失败**且**真实输入新近
  发生才中止；身份失败但无输入＝系统瞬抢，确认连续空闲后把隔离窗抬回继续。
- 尾帧允许「设计内拍不全」：在编排里预先声明关闭动作落在录区外、成片直接掐尾
  （剪辑点＝最后一个有效断言之后）；拍不全才是事故，拍全了反而要查是否超预算。
  注意关闭 DevTools 会让浏览器窗口跳回旧矩形，停录后下一 take 前要重摆窗口。

## 7. ★ 帧率门禁（硬闸）：录完 → 精切前必跑

gdigrab 文件的 `r_frame_rate` 恒报 `30/1`，但桌面合成打嗝时 `avg_frame_rate` 会掉到
5–24fps（hf-04 原始 12 段实测 avg 5.2–10.7）。hyperframes render 的 preflight 用
同源判据 `|rFps−avgFps|/max > 10%` 打回 VFR；带病素材进精切后，抽帧会回退
rawvideo NUT 双管道，多路并发一帧未写即崩（hf-04 首轮 33 路崩 16 路；hf-03 仅 13 路
侥幸过——「上次能跑」不证明素材健康）。

```bash
cd videos
python -m videopipe probe-fps projects/<片>/media/rec-*.mp4   # 原始段：必须看见退出码 2
python -m videopipe probe-fps projects/<片>/media/shorts      # 精切件：必须退出码 0
```

退出码：**0** 全 CFR 放行；**2** 检出 VFR（逐文件列出 r/avg/偏差）；**1** 有文件
帧率字段缺失或 ffprobe 不可读，先人工看，不放行。

精切模板＝`cut_shorts.py` 的 `phase_cut()`，四个参数缺一不可：

```
-vf fps=30                     # 过滤链重建 PTS，强制 CFR（根治，不是重命名帧率）
-g 30 -keyint_min 30           # 每秒一个 IDR，消 compile 期 sparse-keyframe warning
-movflags +faststart           # 便回放
```

精切后必须复跑门禁到退出码 0，才允许进 render。

## 8. 终片/深位置取证的三条 ffmpeg 规矩

- **sparse-keyframe 文件用 output seeking**：`-ss` 写在 `-i` **之后**才逐帧解码到点；
  写在 `-i` 前（input seeking）会退回前一个关键帧（hf-04 在 296s 抽帧退回 22.5s）。
- **长片多点抽帧用混合 seeking（hf-05/hf-06 各踩一次纯 output 超时）**：纯 output
  seeking 对 490s+ 终片每点从头解码，20–40 点必超时；改「输入侧 `-ss t-1.5` 落就近
  关键帧 ＋ 输出侧 `-ss 1.5` 精确定位」，每点秒出、精度仍由 output seek 保。
  公共件 `videos/tools/frames_at.py` 已固化此工艺，别再到各项目 oneoffs 里抄。
- **批量循环加 `-nostdin`**，否则第二个迭代起 ffmpeg 吞掉循环的标准输入导致挂死/异常。
- **`signalstats` 的 `metadata=print` 是 info 级日志**：配 `-loglevel error` 会被一起
  压光，取证时保持默认日志级别。ROI 量化模板：
  `crop=1000:130:280:185,signalstats,metadata=print -f null -`，读 YAVG 序列。
- drawtext 滤镜的 `text=` 里冒号是过滤链分隔符，时间戳文本必须 `.replace(":", "\\:")`
  （范本 `f2_contact_sheet.py`）；fontfile 不能带盘符冒号，字体复制到输出目录用纯
  文件名相对路径。
- 小坑三则：git-bash 无 `bc`，整数/浮点算术用 bash 自带 `$(( ))`；封面截图用的
  chrome-headless-shell 不在 PATH，走 playwright 缓存目录全路径；后台长跑任务命令
  尾巴别加 `| tail`，进度会被缓冲住不可见。

## 10. 终端命令类 take 专项（hf-05/hf-06 实录）

录「终端里敲命令、等结果」的 take 与录编辑器/浏览器不同，坑集中在**报文怎么入镜**：

- **瞬刷输出要用滚轮 freeze 法（hf-06 首录 6 take 同病 NG 的修法）**：check 这类命令
  的约 30 行输出是整屏**瞬时**刷出的，没有滚动中间态，可视区约 20 行装不下——排在前
  面的报错段（恰是核心教学画面）从始至终不入镜。修法：报文稳定后**鼠标滚轮上滚
  3 格**让前段入镜，freeze 取这一帧；下滚会过量自动停底，不影响后续。**Shift+PgUp
  勿用**：wt 1.17+ 默认键绑定无 scrollUpPage，PgUp 被 cmd 的 doskey 吃成「历史上溯」，
  录出来的是上一条命令。
- **报文瞬刷窗仅约 0.5s**（hf-05 实测 t2b 25.9–26.4s）：3s 稀疏探针必漏，目验定位
  用 0.3s 加密帧；成片里这类报文一律用 freeze PNG 定格呈现，不靠活动录屏去「赶」。
- **片长必须按打字速率反推**（hf-05 t4d 废片教训）：term_cmd 逐字实测约 **0.07s/字**
  （delay=.035 外加 keyup 开销），`sleep 33` 才开敲的 18 字命令打完约 38.8s，被 40s
  片长整段切掉、零字入镜。编排时：打字开始时刻 ＋ 命令字数 ×0.07 ＋ 回显稳定余量
  ≤ 片长。
- **cmd 读退出码必须分两行敲**：`check & echo %ERRORLEVEL%` 同句执行时 echo 读的是
  上一条命令的旧值，录出假 `0`。
- **整块改行禁用系统剪贴板**（hf-05 t5b 废片）：录制期剪贴板会被后台程序抢占，整块
  移动改用纯 Scintilla 消息（2142/2144 按 UTF-8 **字节位置**定选区、2620 整块上移）；
  消息号查 Scintilla 头文件实数，勿凭记忆（2050 是 STYLECLEARALL 不是 SETFORE）。
- **布景文件写盘钉死 LF**：Windows `Path.write_text` 默认把 `\n` 译成 CRLF，权威备份
  多出的 `\r` 让字节位置全偏、Scintilla 选区立即错位——生成布景一律
  `newline="\n"`，录前闸对备份做 CRLF bytes 检查。
- **打字带出编辑器自动补全框要补 Esc**（hf-06 t3a）：补全框会遮挡定格帧，save 前先
  Esc 关框。行号槽等外观设置做完**读回校验**（写入≠生效），不过则重试。
- **同构 take 是设计出来的，切点才能批量复用**（hf-06 红利）：六条 check 系 run 在
  编排时刻意做成同节奏（0.5–2s 提示符、3–5.5s 打字、15s 出 Checking、21s 起报文），
  精切目验一条定切点 (1.5, 6.0)，全组六次复用。编排同构化省的是后期每一刀。
- **目验对 MEDIA-FACTS 清单、不对感觉**：每 take 录前先写下「这条必须拍到什么」
  （哪个报错原文、哪行 JSON、哪个状态字），录后逐条核。hf-06 首录 16 take 目验
  10 过 6 NG，全靠这道闸拦住六个「画面里没有教学内容」的废镜头。

## 9. 运行环境与台账

- render / ffmpeg 正式编码须在**非沙箱**跑（沙箱内存上限编码会挂）；短探针可在沙箱。
- 素材母带与全部抽帧放仓库外沙盒目录；只有入选成片素材归位 `media/rec-*.mp4`
  （`media/` 命中 .gitignore，二进制不入库，沿 hf-03/hf-04 惯例）。
- 每片维护 `oneoffs/RECORD-NOTES.md`：每 take 一行（镜号/文件/ffprobe 时长/大小/
  录成时刻/内容/重录备注）、新坑小节（现象/误判风险/根因/固化在哪个函数/跨集价值）、
  几何速查表、定量证据。复盘文与后续集直接从台账取材，不靠事后回忆。
