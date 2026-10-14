# hf-04《seek》实拍代录笔记（2026-10-14，#535）

> 本文件记录「正式代录 12 take」一夜的台账、坑位与定量证据，是后续复盘文的原始素材。
> 彩排期（10-12）的机制实测见同目录 `REHEARSAL-NOTES.md`（__proxied 代理、定时器分叉、
> Studio 同域 iframe 等）；静态加固期（10-12 至 10-13）见计时日志与已发审稿站的复盘文。
> 本文只写实拍当晚新发生的事。

## 〇、环境与现场

- 沙盒 `F:\_hftest\hf04-seek`（公开画面无 C:\Users 用户名）；dev server 端口 3002，
  cwd 必须是项目目录（hf-03 老坑，继续有效）。
- 隔离 Edge：`--remote-debugging-port=9222 --user-data-dir=F:\_hftest\edge-cdp`，
  两 tab——裸 player（前台）＋Studio；CDP 全部走 `http://127.0.0.1:9222`（localhost 走
  IPv6 ::1 每次多等 2s，cdp_ctrl.py 注释在案）。
- 隔离便携 NPP：`F:\_hftest\npp-local\`，标题含 `_hftest\hf04-seek`；
  录制终端：`--suppressApplicationTitle` 锁标题 startswith `hf04-rec`。
- 录屏：node tools/screen-rec.js，gdigrab 物理区 **1600×920@(0,0)，30fps**；
  Edge 窗口外框固定 (-12,0,1624,928)，实体右缘 1612 盖死录区 → 右缘零穿帮
  （hf-03 的 27px 右缘穿帮本集根治）。
- HyperFrames 钉版 0.8.107；系统 DPI 150%，页面 zoom 50%（几何见第四节）。
- guard 三身份闸：只认 9222 隔离 Edge／隔离 NPP／hf04-rec 终端。用户 WT(pid 9776)、
  主 Edge(pid 4764)、日常 NPP(pid 11308) 全程不碰。杀进程只按具体 PID/HWND。

## 一、12 take 台账（ffprobe 实测时长）

成片素材时间戳 **06:48 → 11:47**；12 take 全部通过抽帧目验，无一废片入库
（废片均在当晚被重录覆盖，未归位 media/）。

| 镜 | 文件（media/rec-*.mp4） | 时长 | 大小 | 录成时刻 | 内容 | 备注 |
|---|---|---:|---:|---|---|---|
| seg1 | rec-play-static | 12.93s | 157KB | 08:22 | 静态 s0 页点 Play 三角 | **重录**：首录撞 Edge 灰屏（坑①） |
| seg2a | rec-css-keyframes | 25.97s | 442KB | 06:48 | NPP 写 CSS @keyframes 并保存 | 一次过 |
| seg2b | rec-play-css | 13.00s | 128KB | 06:48 | 播放 CSS 动画版 | 一次过 |
| seg3 | rec-snap-css | 85.90s | 1.76MB | 09:12 | 对 CSS 动画 snapshot 三帧逐字同 | 一次过 |
| seg4a | rec-timer-code | 17.93s | 245KB | 09:19 | NPP 写 setInterval 定时器版 | 一次过 |
| seg4b | rec-play-timer | 12.83s | 112KB | 09:24 | 播放定时器版（tick 走墙钟） | 一次过 |
| seg5a | rec-snap-timer | 165.87s | 771KB | 09:41 | race-snapshot.py 串行/并发两轮 | 一次过；粗稿 L27 数字待回填（见下） |
| seg5b | rec-check-pass | 30.73s | 257KB | 09:49 | check 四项全绿（Runtime/Layout/Motion/Contrast） | 实拍等待 42s 预算沿用 hf-03 |
| seg6 | rec-gsap-three | 45.97s | 728KB | 11:21 | NPP 改 GSAP 三件套（paused/fromTo 位置参/注册 main） | **重录**：s3/s4 布局 10:57 定稿后旧片作废 |
| seg7 | rec-play-final | 12.83s | 52KB | 11:23 | 播放 GSAP 最终版 | **方案改道**：Studio Preview 四轮废片→裸 player（坑④） |
| seg8 | rec-console-seek | 69.87s | 403KB | 11:26 | DevTools 十拍 seek 矩阵 a–j | 一次过；片尾需掐尾（坑⑤） |
| seg9 | rec-render | 82.97s | 8.14MB | 11:47 | 终端 `npm run render -- -o rec-render/hf04-seek.mp4` 全流程 | 一次过；worker headless 不弹窗 |

**净长合计 576.8s（9 分 37 秒）**。媒体在 `videos/projects/hf-04/media/`（.gitignore 命中
`videos/projects/**/media/`，二进制不入库，沿 hf-03 惯例），母带与全部抽帧在仓库外
`F:\_hftest\hf04-rec\`（takes/ 与 frames/）。

## 二、总耗时

- 成片素材墙钟 **06:48–11:47 ≈ 5 小时**，其中含：布景 s3/s4 布局重排与五点目验、
  seg7 Studio Preview 四轮废片排查、沉浸式翻译红钮排查＋全素材回溯、seg1/seg6 两次重录、
  每 take 抽帧目验与尾帧彻查。
- 此前 A 节 7 项真机标定（#534，10-13 深夜）与三轮静态加固另计。
- 纯素材净长 9.6 分钟，录制/墙钟比约 1:31——「素材先行」流程的真实成本主要在
  布景确定性与穿帮排查，不在敲键盘本身。

## 三、实拍期新坑（复盘主料）

### 坑① Edge 上屏合成挂起：页面活着、屏幕整块灰（seg1 首录作废）

- **现象**：seg1 开录后播放器窗口在屏幕上整块均匀灰，无任何画面；同刻 CDP
  `captureScreenshot` 返回完全正常的页面，DOM/player ready 标志齐全。
- **误判风险**：CDP 探针全绿会让人以为一切正常——**截图对≠上屏对**。这是本集最值得
  复盘的一条：自动化「看页面」有两个通道（合成器上屏 vs CDP 位图），挂的恰是前者。
- **根因**：Windows 上 Edge 窗口的 GPU swapchain/合成挂起（锁屏/休眠/桌面会话切换后
  偶发，本集现场经历过整夜无人值守），DOM 与渲染管线没死，所以 CDP 截图照常。
- **解法**（record_segments.py 已固化）：`wait_studio_ready` 改双轨——屏幕 Play 三角
  白像素探测（gdigrab 同源截屏）＋CDP 截图复核；判定「页面活而屏幕灰」即
  `heal_edge_compositing()`：minimize→restore 强制重建 swapchain，自愈后再录。
  rec_automate.py 补 SW_MINIMIZE 标志（hf-03 共享脚本，PR 正文须说明向后兼容）。
- **跨集价值**：后续一切「隔夜/锁屏后代录」默认带灰屏自检，不能只信 CDP。

### 坑② 布景布局定稿：s3/s4 重排，seg6 旧片连带作废

- 10-14 10:57 把 card 改为 **780×266 定高底板**、title/card/subtitle 三元素 abspos、
  top 统一钉画面中心，清掉占位句；seek 0/2.4/3/6.3/9 五点目验＋getComputedStyle
  （visibility/opacity/rect）双证后入 backup 为 s3/s4 权威态。
- 教训：**布景在第一批 take 已录完后才定稿，seg6 被迫重录**。素材先行流程里
  「全部布景权威态先于任一 take 冻结」应当成为硬闸（本次靠 check_anchors 保了磁盘态，
  没保住视觉态——视觉定稿没有闸）。

### 坑③ 沉浸式翻译扩展红钮：Shadow DOM 注入物贴 player 右缘入镜

- **现象**：抽帧发现 player 视口右缘约物理 x=1847 处有一个红色圆钮（沉浸式翻译扩展的
  `#immersive-translate-popup`），被切 1/3，像穿帮按钮。
- **排查难点**：宿主元素 0×0，红钮在其 **Shadow DOM** 内，`document.elementsFromPoint`
  只能摸到宿主、摸不到钮；且它由扩展在页面加载后异步注入，reload 即复发。
- **区分证据图与视频帧**（重要几何结论）：seg5-shots 的证据图是 CDP 全屏 1920×1080，
  拍到隔离 Edge 右后方还露着第二个 Edge 窗（Studio 白编辑器）与红钮；而 gdigrab 只录
  物理 (0,0,1600,920)，Edge 外框实体右缘 1612 盖死录区。对视频帧做 PIL 亮度量化：
  y=20 右缘 0/0/0、y=200 max 60、y=600 恒 51（面板灰）——**录区内零污染**，
  污染只存在于 1920 宽的证据图。右缘条带拼图回溯确认此前全部素材无红钮入镜。
- **解法**（cdp_ctrl.py 已固化）：`hide_page_extensions()` 注入
  `#__rec-hide-ext`（`display:none!important`）＋MutationObserver 兜底延迟注入；
  **reload 后样式失效，每次 reload 必须重注**（take_seg8 已按此编排）。
- **跨集价值**：任何带扩展的隔离 profile 都可能在页面里留注入物；「录区几何量化」
  是比肉眼更可靠的穿帮裁判。

### 坑④ seg7 四轮废片：Studio Preview 实时画布不可录，改道裸 player

- **原计划**：seg7 录 Studio 里点 Preview 三角播放最终版（与 seg1/seg2b 同样的点击叙事）。
- **实战**：Studio Preview 实时画布连续四轮给出四种坏画面（时间码叠字／轨道层残留等），
  而裸 player 引擎路径探针全部正确。Studio 的实时预览与渲染/抓帧不是同一条确定性路径。
- **探针二证**：裸 player 页面无任何可见控件（不会拍到假按钮）；CDP 合成 Space 键
  **不触发**裸 player 播放（合成键不进页面输入管线）。
- **定稿**：seg7 改为终端外的 CDP 调用 `window.__player.play()`（cdp_ctrl.player_play，
  与点 Studio 三角同一条实时引擎路径，画面就是播放本身），一次成片。点击播放的叙事
  seg1/seg2b 已两次入镜，不重复，教学无损。
- **跨集价值**：要录「播放结果」但不要 Studio 壳时，裸 player ＋ `__player.play()`
  是干净机位；但它必须由 CDP 求值触发，不能靠合成键。

### 坑⑤ seg8 尾帧：DevTools 关闭动作在录区外（设计内，剪辑掐尾）

- 十拍 seek（a=2.4/b=3/c=6.3/d=9/e=0＋f–j 五回 2.4）每拍含 type＋enter＋等 1.2s＋
  getTime 断言＋截图，**实测每拍约 4.8s**（open 4.8＋split 4.5＋zoom 3.6＋seek 43.3
  ＋close 3.5≈59.8s 动作预算），record 取 70s；真机 close 落在约 71s，超出录区。
- 66–69.8s 精抽五帧：DevTools 全程仍开，停在 seek(2.4) 历史＋空提示符。
- **非事故的证据链**：record 正常退出（step_close 内 `devtools_open()` 复查失败会
  SystemExit，没触发）；当前 /json 无 devtools:// target；34-closed.png 记录关闭态。
- record_segments.py 预先接受此形态：「尾帧是 DevTools 关闭画面，片尾静场剪辑直接掐尾，
  拍不全 close 才是事故」。**成片剪辑点＝最后一拍断言之后，掐掉空提示符静场。**
- **附带发现（待修）**：关闭 DevTools 后 Edge 窗口跳回旧矩形 1310×790。因发生在停录后
  不入素材，但 step_close 应补「关闭后重摆 WND」，否则下一 take 布景全歪。

### 坑⑥ 页面 zoom 与 DevTools zoom 的输入通道相反（标定回填）

- 系统 150% DPI × 页面 50% zoom ⇒ **devicePixelRatio 0.75，CSS 像素 ×0.75＝物理像素**；
  1920×1080 固定 body 在 1056 高 CSS 视口里居中、上下各溢出 -24px。
- **页面 zoom 只认真实键盘**：CDP `Input.dispatchKeyEvent` 合成的 Ctrl+- 对 Edge 浏览器
  快捷键无效；必须 PostMessage/SendInput 走真实键路（ensure_page_zoom_half：Ctrl+0 复位
  ＋五击 OEM_MINUS，edge 档位 100→90→80→75→67→50）。
- **DevTools 自身 zoom 相反**：只收 dt_ws（DevTools target 会话）上的合成键，
  Ctrl+0＋两击 Ctrl+=，定档 z2、dpr 1.875。真实键路反而打不进 DevTools。
- 控制台开台即 `DEVTOOLS-TEXT-EDITOR` active；十拍期间 focus 断言全程挂在它上面。

### 坑⑦ guard 期间的后台窗口瞬抢

- 整夜两次出现前台瞬时变成 `Shell_TrayWnd`／`ThumbnailDeviceHelperWnd`（系统外壳，
  非用户操作）。处置：不立即判用户回机，先读 LASTINPUTINFO 空闲时长＋枚举窗口，
  确认空闲连续（seg9 录前 17.9 分钟）后把隔离窗抬回继续。
- 判据：**身份失败＋真实输入新近发生**才中止；身份失败但无输入＝系统瞬抢，可恢复。

## 四、几何速查（后续集直接复用）

| 量 | 值 |
|---|---|
| 系统 DPI / 页面 zoom / dpr | 150% / 50% / 0.75（CSS×0.75＝物理） |
| body 固定尺寸 / CSS 视口 | 1920×1080；视口 1056 高，body rect [0,-24,1920,1080] |
| gdigrab 录区 | 物理 (0,0) 起 1600×920 @30fps |
| Edge 外框 / 实体右缘 | (-12,0,1624,928) / x=1612（盖死录区右缘） |
| DevTools 停靠 / dpr | 底停靠 z2 档 / 1.875 |
| DevTools 面板顶 / 命令行 / 分割拖拽 | PANEL_TOP=555 / ROW_OFFSET=30 / SPLIT_X=760（seg5_rehearse.py） |
| CDP 证据图宽 | 1920（含录区外的后台窗，不能当穿帮证据，穿帮只看视频帧） |

## 五、定量证据（验收口径）

### seg8 seek 矩阵（33-seek-a..j.png ＋ getTime 断言双证）

| 拍 | 命令 | 画面断言（证据图目验） |
|---|---|---|
| a | seek(2.4) | title 半透明浮在半路（opacity≈0.6「我的第一个片段」灰字） |
| b | seek(3) | title 纯白就位（back.out 起点 card opacity 0，属正确） |
| c | seek(6.3) | 深色卡片在场，副标题「时间轴一挂，画面就活了」半路进场 |
| d | seek(9) | title/card/subtitle 三件套全就位 |
| e | seek(0) | 空台 |
| f–j | seek(2.4) ×5 | 五回逐字节同画面＋getTime 全 OK（确定性收口） |

控制台历史命令文本/参数与证据图逐张一致；十拍断言 a–j 全 OK。

### seg9 render 自报（尾帧停绿色输出路径行）

- `npm run render -- -o rec-render/hf04-seek.mp4`，HF 自报 **rendered in 39.0s**
  （compile 1.5s · setup 13.9s · capture 22.9s · assemble 0.2s；墙钟 47.5s）。
- 产物 **253.9 KB · 10.0s · 300 帧**；模式 **drawElement**（captureMode），hardware gpu。
- static-frame dedup **209/209 reused**（runs=3/3、screenshots=27、seeks=28），
  drawElement self-verify 4 帧 @[75,150,225,285]。
- worker 为 **headless，不弹可见窗**（capture 期窗口枚举零 Chrome 弹窗）；
  视频尾帧 16/21 均稳定停 `rec-render\hf04-seek.mp4` 输出路径行。

### seg5a race 正式 take 读数（2026-10-14 已回填定稿候选 src/hf-04-src.candidate.txt）

- 排队轮（终端「排队问：墙钟 45.4s，3 张帧，2 种内容」）：ser-1 tick3、ser-2 tick3
  （MD5 fb93…相同）、ser-3 tick4（9ffb…，独一份）；单帧耗时 14.5/14.5/15.9s。
- 并发轮（终端「一窝蜂：墙钟 44.4s，6 张帧，3 种内容」）：tk-1/2/5 tick6（3e67…）、
  tk-3/6 tick7（150c…）、tk-4 tick4（9ffb…＝与 ser-3 同哈希，独一份）；
  完成时刻 42.3/42.7/43.1/44.3/44.3/44.4s。
- 旧粗稿「三张全 tick 3、逐字节一模一样」已证伪并改写（连排队都 2 种，故事反而更强）；
  彩排轮基线（闲机）串行 46s／并发 47s、tick 4/6/7 分布与正式 take 不同，以正式 take 为准。
- CSS 三时刻两轮逐字节相同（s1-a vs s1-b，MD5 三对全等：2.1s 4944…／2.5s b395…／2.9s 2c63…）。

## 六、guard 安全闸运行记录

- 整夜键鼠动作全部经过「前台身份＋落点」双校验，零误触用户窗口。
- 录前四查每批必做：三身份／用户空闲时长／沙盒权威态（磁盘锚点）／dev server 健康。
- 两次外壳瞬抢按坑⑦规则恢复，未中止。
- 收尾：未强杀任何用户进程；隔离现场（Edge 两 tab、hf04-rec 终端、server 3002、
  沙盒 s4）保留为热场，等用户审素材。

## 七、给后续复盘的选题线索

1. **「截图对≠上屏对」：自动化代录的两个视觉通道与灰屏自愈**（坑①，跨集通用，首选）。
2. **证据图 1920 vs 视频帧 1600：穿帮裁判必须用录区几何量化，肉眼会冤枉素材**（坑③）。
3. **浏览器扩展是画面里的第三者：Shadow DOM 注入物的发现、回溯与隐藏**（坑③）。
4. **Studio Preview 不是渲染器：实时画布四轮坏画面与裸 player 机位**（坑④，
   可与 REHEARSAL-NOTES 的 __proxied 代理合成一篇「运行时到底有几条画面路径」）。
5. **素材先行的成本账：9.6 分钟素材为什么录了 5 小时**（第二节；布景视觉定稿无闸、
   每 take 目验、尾帧彻查；对照 hf-03《五分半视频的十小时》）。
6. **合成键的两条边界：浏览器快捷键只认真键、DevTools 只收 dt_ws**（坑⑥）。
7. DPI 150%×zoom 50% 的坐标算术（第四节，适合做复盘文里的小卡片）。

## 八、待办（走分支 PR，一分支一 PR，串行）

1. `hf-03/oneoffs/rec_automate.py`：SW_MINIMIZE＋灰屏判定原语（跨集共享，
   PR 正文说明向后兼容；blackmat.py 的 Event 关闭一并带上）。
2. `hf-04/oneoffs/record_segments.py`：wait_studio_ready 双轨自愈、
   ensure_page_zoom_half、seg7 player 化、seg8 编排、hide_page_extensions 重注点
   （当前工作区 M 对主干版本）。
3. `hf-04/oneoffs/cdp_ctrl.py`：player_play／hide_page_extensions（当前 M）。
4. seg5_rehearse.py：step_close 关闭 DevTools 后重摆窗口 WND（坑⑤附带项）。
5. 本文件随 RECORD-NOTES 与计时日志条目同批走 PR。

## 九、现场留存（用户审片期间不清理）

- 沙盒五权威态：`F:\_hftest\hf04-seek\backup\s0-static/s1-css/s2-timer/s3-gsap-skel/s4-final`
  （s3/s4 mtime 10-14 10:57；当前 index.html＝s4，三锚点位置参已验）。
- 母带 `F:\_hftest\hf04-rec\takes\rec-*.mp4`；抽帧 `F:\_hftest\hf04-rec\frames\`
  （正式抽帧 rec-*-NN.png＋尾帧/右缘/裁剪探针）。
- 运行时证据：`oneoffs/seg5-shots/33-seek-a..j.png`、`34-closed.png`（整目录 gitignore）。
- 一次性探针 9 个（_probe_*／_tune_subtop／_hide_ext）已删，不入库。
