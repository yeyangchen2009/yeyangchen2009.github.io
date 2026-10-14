# 真人录屏代录 SOP（gdigrab · 素材先行）

触发条件：要录**真人操作演示**（编辑器敲码、终端命令、浏览器点击、DevTools）作为
b-roll 进 HyperFrames 片时，开拍前先读本文件。纯 HTML/SVG 动画不需要本文件——
那条路走 snapshot/render 的确定性逐帧路径，见 `hyperframes-agent.md`。

- 首个全量实战范本：`projects/hf-04/oneoffs/RECORD-NOTES.md`（12 take 台账、七坑
  全部带定量证据）；彩排期机制实测见同目录 `REHEARSAL-NOTES.md`。
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
- **批量循环加 `-nostdin`**，否则第二个迭代起 ffmpeg 吞掉循环的标准输入导致挂死/异常。
- **`signalstats` 的 `metadata=print` 是 info 级日志**：配 `-loglevel error` 会被一起
  压光，取证时保持默认日志级别。ROI 量化模板：
  `crop=1000:130:280:185,signalstats,metadata=print -f null -`，读 YAVG 序列。
- drawtext 滤镜的 `text=` 里冒号是过滤链分隔符，时间戳文本必须 `.replace(":", "\\:")`
  （范本 `f2_contact_sheet.py`）。

## 9. 运行环境与台账

- render / ffmpeg 正式编码须在**非沙箱**跑（沙箱内存上限编码会挂）；短探针可在沙箱。
- 素材母带与全部抽帧放仓库外沙盒目录；只有入选成片素材归位 `media/rec-*.mp4`
  （`media/` 命中 .gitignore，二进制不入库，沿 hf-03/hf-04 惯例）。
- 每片维护 `oneoffs/RECORD-NOTES.md`：每 take 一行（镜号/文件/ffprobe 时长/大小/
  录成时刻/内容/重录备注）、新坑小节（现象/误判风险/根因/固化在哪个函数/跨集价值）、
  几何速查表、定量证据。复盘文与后续集直接从台账取材，不靠事后回忆。
