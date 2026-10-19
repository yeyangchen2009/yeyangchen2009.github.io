# hf-07《把每一帧看清楚》分镜框架（录前定稿 v1，勘误后第二版）

> 上游：`src/hf-07-src.txt`（1772 字／母带 440.170s／cues 215 句已落地，
> time_offset 双峰裁决取 0.29；★母带为勘误前旧叙事，**局部重录进行中**：
> CSS 主角改自掐表黑户，约 12–14 句重录后 cues 局部重对齐，幕表时点届时
> 回填）、`oneoffs/PROBE-NOTES.md`（文首有 2026-10-19 翻转勘误＋五级真机
> 矩阵，E2–E6 旧文留档勿再引）、`oneoffs/probe-seeds/`（三工程种子）。
> 机位/安全/精切工艺沿用 hf-04（浏览器段）＋hf-06（终端 take 体例），
> 见 `../../docs/screen-rec.md`。本篇只定幕表、take 表、概念卡、布景。

## 一、机位（两身份，无 NPP）

| 身份 | 窗口 | 标题针 | 外框几何 |
|---|---|---|---|
| 隔离 Edge | `msedge.exe --remote-debugging-port=9222 --user-data-dir=F:\_hftest\edge-cdp`（裸 player tab，端口 **3021** 后台 preview server） | CDP 9222 pid（netstat 权威，不看标题） | (-12,0,1624,928) |
| 终端 | `wt.exe -w new --title hf07-rec --suppressApplicationTitle -d <proj> cmd /k <env>` | startswith `hf07-rec` | (-12,0,1632,1000) |

- 录区 gdigrab (0,0,1600,920)@30；系统 DPI 150%／页面 zoom 50%／dpr 0.75，
  几何与 hf-04 完全同机同值（Edge 实体右缘 1612 盖死录区）。
- 本集**没有 NPP 现场编辑段**：三个演示工程全部静态冻结，snapshot/keyframes/
  compare 只读工程、不改工程，布景状态机比 hf-06 简单（无五态、无锚点）。
- 终端三环境变量同 hf-05/06（FONT_CACHE_DIR／NO_UPDATE_CHECK／SKIP_SKILLS）。
- guard 白名单两身份：CDP 9222 Edge、hf07-rec 终端。Studio 不入镜
  （hf-04 坑④：Studio Preview 实时画布四轮坏画面；录播放结果走裸 player）。

## 二、布景（setup_scenes.py 生成，LF 换行）

沙盒 `F:\_hftest\hf07-frames\`（公开画面无用户名）：

```
proj/
  hyperframes.json        paths.compositions=.
  package.json
  grades.json             grade-compare 的两档候选（暖色/高亮），E7 实测 filter 串
  v1/index.html           主工程：蓝 GSAP seekable 0→800 ＋ 绿点合法 CSS
                          （legalPulse 2s，WAAPI 接管）＋ 红块 setInterval
                          自掐表 4s 一圈（黑户，check 0 error、seek 管不着）
  v1/gsap.min.js          本地 gsap（铁律：CDN 在无头环境 ERR_CONNECTION_RESET，E1）
  v2/index.html           compare 变体：蓝块换绿 #238636、距离缩到 500；
                          合法绿点与自掐表红块同 v1
  v2/gsap.min.js
  v3/index.html           边界实验：红块换 60s 一圈自掐表慢表（第十秒补刀）
  v3/gsap.min.js
  build/                  keyframes/compare/grade 产物输出位（snapshot 只清自己目录）
backup/v1|v2|v3/          视觉权威态冻结拷贝（index.html＋gsap.min.js，restore 一键回冻）

> 文件名铁律（2026-10-19 彩排真机）：CLI 目录参数（check/preview/
> snapshot/keyframes `v1`）只认 **index.html**，叫 frame.html 报
> `No composition found`；compare/grade 帮文档位直接收目录。唯 preview
> server 首次访问会规范化 index.html（注入 data-hf-id），故 setup init 先
> prenormalize 三工程再冻结。init 纯净重建 proj/（连 snapshots/build 一起
> 清），9 个冻结文件入 backup/，verify 哈希闸（第七次彩排 c12 OK）。
```

- 种子＝入库的 `oneoffs/probe-seeds/01|02|03`，setup 原样复制。
- v1 画面文字即教学文字：
  - 左上绿点旁：「合法 CSS 动画（登记在册，seek 也管得住）」；
  - 蓝标签「GSAP seekable（snapshot 该走到哪走到哪）」，蓝块 `OK`；
  - 红标签「自掐表动画（setInterval，墙钟驱动，seek 管不着）」，红块 `墙钟`；
  - v3 红块字 `慢表`，标签「自掐表动画，慢表一分钟一圈（seek 照样管不着）」；
  - 右上 `t=<tl.time()>` 角标（dummy tween onUpdate，挂真实元素 #clock，
    规避 dwell/hold 空 target 的 querySelector 崩溃，E5 坑）。
- 自掐表实现（唯一既过 check 又不可 seek 的形态，五级矩阵见 PROBE-NOTES
  文首）：闭包内 `let __wall=0; setInterval(()=>{__wall=(__wall+.016)%4;
  el.style.transform='translateX('+__wall/4*800+'px)';},16)`——不读
  Date.now/performance.now（否则 non_deterministic_code 硬 error）、
  不用 requestAnimationFrame（StaticGuard 墙钟契约硬 error）、不注册
  `__timelines`、不走 WAAPI。
- snapshot 产物默认进各自 `vN/snapshots/`，每次跑只清自己的 frame-*.png、
  重写 contact-sheet.jpg（E8）；故每个 take 录完**立即**把产物归位
  `F:\_hftest\hf07-rec\artifacts\<take>\`，下一 take 不连坐。
- 视觉权威态冻结（hf-04 坑②硬闸）：init 后跑彩排产出全套真机图，已目验
  通过并冻结（2026-10-19，第七次彩排 12/12）：
  - **contact4（★高潮）**：四格角标 t=2.00s；蓝块四帧质心全 0.2391、
    合法绿点全 0.0373（登记在册者钉死），红块四帧 .31/.33/.36/.39 单调异位；
  - **v3 frame10**：t=10.00s 蓝在终点（blue≈.552）、慢表红贴起点（red≈.147）；
  - **contact5**：t=0/3/6/9/11.64s 五均分帧，蓝随 seek 均匀推进、红相位乱；
  - **zoom 裁图**：真机 504×504，红块「墙钟」大特写；
  - **onion-good**：front·zoom-fit·9 frames，蓝块 0→10.5s 轨迹＋时间标，
    红/绿无残影（--selector 只画登记在册的 #good）；
  - **compare.png**：1212×372 两格（方案A·x800 蓝／方案B·x500 绿）；
    两格红块格内质心差≈0.002（近似同相，旧「暗线」说法已作废）；
  - **grade.png**：original/暖色/高亮三格，filter 可辨；
  - 断言全部落进 `run_rehearsal.py`（蓝/绿同位容差 .006、红 distinct≥3、
    cssKeyframes 在册 legalPulse/#legal、#bad 报告隐身＋--shot exit 1）。

## 三、take 表（9 母带，录制顺序＝ALL_TAKES）

等待常量已按第七次彩排热态墙钟×1.3 回填 `record_segments.py`（snapshot
开销主要是 headless 拉起＋管线固定 ~14s，帧数几乎不影响墙钟）。

| take | 起点 | 内容 | 片长 | 关键产物/归位 |
|---|---|---|---:|---|
| t00-prev-bg | server 已 stop | 终端敲 `npx hyperframes preview v1 --background --no-open --port 3021`，尾帧停后台 URL/PID 状态行（真机 11.7–12.7s，WAIT 17） | 24 | —（命令真实起 server） |
| t01-preview | t00 接态 | 切隔离 Edge 裸 player：reload→就绪→双轨自检→`__player.play()`，蓝块随播放头 0→800、绿点随时间轴 pulse、红块 4s 墙钟循环，拍满 12s | 16 | 红块「顺滑」观感（黑户预览无痕） |
| t02-snap4 | reset 文件态 | `snapshot v1 --at 2,2,2,2 --no-end --no-browser-gpu`：四帧＋接触表，尾帧停 Saved/contact 行 | 30 | **artifacts/t02：contact-sheet.jpg＋4 frame（★高潮）** |
| t03-forwards | 静态 | `snapshot v3 --at 10 --no-end --no-browser-gpu`：第十秒慢表红才走 1/6 贴起点、蓝早在终点（take id 沿用旧名） | 29 | artifacts/t03：frame-10 |
| t04-frames5 | 静态 | `snapshot v1 --frames 5 --no-browser-gpu`：五帧均分（首尾自动带 0/11.64s）＋接触表 | 30 | artifacts/t04：contact-sheet.jpg＋5 frame |
| t05-zoom | 静态 | 两条连敲：`snapshot v1 --at 4 --zoom "#bad" --no-end …`（504×504 局部裁图）；`… --zoom "#nope" …`（选择器不命中硬 error，文案 `✗ Snapshot failed: --zoom selector matched no element: #nope`）。真机报文仅 7 行一屏装得下，**纯 freeze 不上滚** | 53 | artifacts/t05：录后非录态补跑成功轮产 zoom 裁图归位；error 尾帧在录屏里 |
| t06-keyframes | 静态 | 三条连敲：①`keyframes v1`（无参报告 **3 items**：#good/#clock/legalPulse #legal，#bad 隐身）；②`keyframes v1 --shot build/onion-good.png --selector #good`（★目录形态为彩排 SHOT_WINNER，Saved 行 freeze）；③`keyframes v1/index.html --shot build/onion-bad.png --selector #bad`（exit 1 无图：`--shot: nothing animates under '#bad'. Nearest animated elements: #good, #clock, #legal.`，2 行一屏装得下，纯 freeze） | 72 | artifacts/t06：只归位 onion-good.png；报告帧/error 帧在录屏里 |
| t07-compare | 静态 | `compare v1 v2 --at 4 --labels 方案A·x800,方案B·x500 --out build/compare.png`（真机 19.7s 成 1212×372；标签内禁逗号，数量不符真机 **exit 1** 文案 `--labels count (1) must match path count (2)`；中文标签段走 paste） | 36 | artifacts/t07：compare.png |
| t08-grade | 备帧在 | 录制外先 `snapshot v1 --at 4 --no-end` 备帧；`grade-compare --for v1/snapshots/<帧>.png --grades grades.json --out build/grade.png`（彩排 GRADE_WINNER＝**无 --project**；original 基线自动 prepend，三格） | 31 | artifacts/t08：grade.png |

净素材 321s ≈ 5.4 min；无 NPP 冷启、无多态 restore，take 间隔只有
终端/Edge 切换与产物归位，单次全推估 15–25 min；按 **1–1.5h 占机**留 NG
缓冲（真人离机，开始前必须与用户确认时段）。

present 不录（src 一句话带过，幕内给小卡）。DevTools seek 矩阵不录
（hf-04 seg8 已深录；本集老契约用概念卡＋t02 接触表自证）。

## 四、幕表（make_video 20 幕，时点待局部重录后 cues 回填）

| 幕 | 口播段（新叙事口径） | 画面 | 素材 |
|---|---|---|---|
| m01 | 先做一个实验 | C0 实验台卡：蓝/绿守规矩、红自己掐表，同一秒同一路线 | 卡 |
| m02 | 三个元素／我开 preview，红的又顺又稳 | t00 打字段＋t01 player 红蓝绿同屏（红 4s 循环顺滑无痕） | t00/t01 |
| m03 | 不拖进度条，连拍四个第二秒 | t02 打字段（命令入镜） | t02 |
| m04 | 四张照片：蓝和绿纹丝不动，红四个位置；上万帧白等；最怕不确定 | **contact4 freeze 全屏＋放大格**（指给观众看绿点也钉死）；C1 烤片成本卡（一帧零点几秒×上万帧） | t02 freeze＋卡 |
| m05 | 墙钟与时间轴，两种时间 | C2 双钟卡（页面打开起走 vs 进度条） | 卡 |
| m06 | 拖到第十秒不搭理；把它的表调慢到一分钟一圈，第十秒才走六分之一 | t03 打字段＋frame10 freeze（红贴起点、蓝在终点） | t03 |
| m07 | CSS 不是被告：绿点这种 CSS 动画浏览器登记在 WAAPI 上，seek 照样管；loading/hover/弹窗是网页天经地义。真正的黑户是不登记、自己掐表的脚本 | C3 卡（合法三家 GSAP/CSS/Anime 都登记在时间轴 vs 黑户 setInterval 计数器；rAF/读墙钟更惨，check 直接拦） | 卡＋t02 绿点短回切 |
| m08 | 老契约：paused／登记 __timelines／seek；薛定谔的猫 | C4 契约三件卡；t01 蓝块短回切 | 卡＋t01 |
| m09 | preview 还要，但「这一帧对不对」永远问 snapshot | C5 感受/事实分工卡 | 卡 |
| m10 | 跟 check 分工：机器体检 vs 你的眼睛（check 0 error 也能骗眼睛——红块就过了 check） | C6 两道闸卡（规则没破≠画面对） | 卡 |
| m11 | at 列秒数／frames 均分／接触表＝体检总览 | t04 打字段＋contact5 freeze | t04 |
| m12 | zoom 选择器/像素区，写错直接报错不糊弄 | t05 打字段＋zoom 裁图 freeze＋#nope 报错 freeze（不上滚） | t05 |
| m13 | 拍哪些秒：接缝/半途/心虚句；只清自己的帧 | C7 三处必拍卡；E8 清扫语义小卡（MARKER.txt 不碰） | 卡 |
| m14 | keyframes 体检：在册的三家逐户登记，报告 3 items | t06 报告段 freeze（#good/#clock/legalPulse #legal） | t06 |
| m15 | 红得扎眼的 #bad 报告里没有户口；--shot 点它直接硬 error「nothing animates」；洋葱皮只画得出登记过的运动 | onion-good freeze（蓝轨迹、红绿无残影）＋#bad 报错 freeze＋C8「在册才被时间轴管」卡 | t06 freeze＋卡 |
| m16 | compare：两变体一排，编号标签，最多四个；标签逗号小脾气 | t07 打字段＋compare.png freeze | t07 |
| m17 | grade-compare 调色选片；present 演讲模式，都不是查帧 | t08 短打字段＋grade.png freeze；present 一句小卡 | t08＋卡 |
| m18 | 三句话：管感受/管事实；能被 seek 管住的才配进烤片；拿不准拍照片 | C9 金句 recap | 卡 |
| m19 | 行动件：frames 拍五张＋--shot 洋葱皮；自己掐表跑的墙钟元素趁早换 seekable（CSS 放心用） | C10 行动卡 | 卡 |
| m20 | 下集 render 预告＋道别 | C11 render 预告（无头浏览器烤 MP4）＋片尾 | 卡 |

概念卡 C0–C11 全暗色 GitHub Dark（#0d1117/#161b22），本集主色蓝
（snapshot 事实集，区别于 hf-06 声音集的金）：蓝 #58a6ff、红 #f85149
（黑户/墙钟＝危险色）、**绿 #3fb950（合法登记/seekable/通过，绿点同色）**、
金 #e3b341 仅金句 recap 与标题沿用封面系。freeze 一律真机产物 PNG
（接触表/洋葱皮/对照图不给观众读运动帧；终端报错本集报文 ≤7 行一屏内，
纯 freeze，不走 hf-06 的上滚回滚）。

## 五、录前决策（已定，不再问）

1. 演示沙盒与正片工程分离（沙盒 F:\_hftest\hf07-frames，正片人声是
   hf-07 真母带）；gsap 全部本地。
2. 所有命令真实跑、报错文案逐字以彩排/实拍真机为准，终端不许造文案；
   contact-sheet/onion/compare/grade 全部真机产出物，不后期伪造。
3. snapshot 一律 `--no-browser-gpu`（SwiftShader 保确定性）；
   compare/grade-compare/keyframes --shot 默认硬 GPU（无开关），照实录、
   不强求像素逐帧可复现（教学点是几何/时间标，不是像素同）。
4. keyframes 体检报告口播念「GSAP／CSS／Anime 都查得出来」是能力陈述：
   v1 真布 GSAP（#good/#clock）＋合法 CSS（#legal）两类，真机报告
   3 items 即支撑「在册的都查得到」，不引第三库 anime（免 vendor 与未探
   报告格式风险）；#bad 隐身与 --shot 硬 error 支撑「黑户查不到」。
5. preview 用 `--background --no-open` 真起 server，Edge 只开裸 player
   （URL 形态彩排 curl 验证后回填 cdp_ctrl）；播放由 CDP
   `window.__player.play()` 触发（合成 Space 不触发，hf-04 已证）。
6. 浏览器段全套 hf-04 SOP：guard CDP 身份、swapchain 双轨自检＋
   minimize/restore 自愈、扩展隐藏 reload 重注、页面 zoom 只认真键、
   外壳瞬抢按空闲时长恢复。
7. 标题用《把每一帧看清楚》（封面已定），发布前可换。
