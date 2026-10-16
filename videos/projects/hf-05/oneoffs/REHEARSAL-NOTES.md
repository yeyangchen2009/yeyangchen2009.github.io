# hf-05《check 门控》彩排真机台账（2026-10-15 深夜，0.8.107）

> 全部结论以本机实测为准（Node v24.6.0／FFmpeg 7.1.1／headless-shell 152／UHD620），
> 不照选题库大纲想当然。探针页在 `build/probe/`（gitignored，不入库；
> 正式录屏布景由 `oneoffs/setup_scenes.py` 在 `F:\_hftest\hf05-check` 重新生成）。

## 1. 命令面（`npx hyperframes@0.8.107 --help` 实测）

| 命令 | 实测职责 | 0.8.107 状态 |
|---|---|---|
| `lint` | 纯静态读 HTML：时间属性、media id/src、结构。**不起 Chrome，秒级** | 正式 |
| `validate` | 只跑运行时段（headless Chrome：console 错、缺资源、对比度） | **deprecated，提示改用 check** |
| `inspect` | 只跑 9 采样点布局巡检 | **deprecated，提示改用 check** |
| `check` | 一道总闸，六段：Lint／Runtime／Layout／Motion／Contrast／Snapshots | 正式，本片主角 |
| `keyframes` | 列全部动画（fromTo/flat、起止、0%/100% 值），`--shot out.png` 出洋葱皮 | 体检工具，非门 |
| `beats` | 检测音乐轨节拍；无音乐轨报 `Add data-timeline-role="music"`（或 id 含 music/bgm/soundtrack） | 体检工具，非门 |

退出码实测：**lint/check 都是有 error → exit 1；纯 warning 或全绿 → exit 0**（CI 可直接挂）。

## 2. check 六段机制（好页基线：0 error 全绿、exit 0）

1. **Lint**：不起浏览器读文件。缺文件这种事静态就能查（会 stat src）。
2. **Runtime**：开 headless Chrome 真跑页面，收 console。GPU 探测走硬件（UHD620 D3D11），录屏首行会刷 `browserGpuMode probe → hardware`。
3. **Layout**：在时间轴上抽 **9 个采样点**逐帧量布局。关键错误 `sweep_static`——seek 下时间轴没前进（假 timeline 桩必触发），且明示「every green verdict on this run is unreliable」（错会连坐，后面全绿不算数）。
4. **Motion**：动画合法性（见 infinite repeat）。
5. **Contrast**：逐采样点量文字与底色对比，**大字门限 3:1**（WCAG AA 大字口径），报错直接递修复建议色 `Try rgb(93,97,102)`。
6. **Snapshots**：未配置即 disabled。

## 3. 探针矩阵（e1–e9，全部真机跑过）

| 探针 | 构造 | lint 单跑 | check 全闸 | 段 / 规则名 |
|---|---|---|---|---|
| good | 黑底白字卡＋真 GSAP paused timeline | 0/0 | **passed, 0** | 基线 |
| e1 缺 duration | clip 无 data-duration | 1 warning, exit 0 | **passed, 0** | Lint `timeline_element_missing_timing`⚠ |
| e2 越界 | start 8＋dur 5（root 10） | 1 warning, exit 0 | **passed, 0** | Lint `clip_ends_past_root_duration`⚠，给双修复（延长 root／缩短 clip） |
| e3 **同轨重叠** | 两 clip 同 track-index=1、时间重叠 | 0/0 | **passed, 0** | **全绿——合法！** |
| e4 对比度 | #1a1f26 字 on #0d1117 | 0/0 | **failed, exit 1** | Contrast 5 采样点全 ✗ `1.14:1 (need 3:1)`＋建议色 |
| e5 缺资源 | `<audio src="media/nope.wav">` | **2 errors, exit 1** | failed, 1 | Lint `audio_src_not_found`✗＋`media_missing_id`✗（无 id 会静音）＋无 id 的 Studio warning |
| e6a JS 硬错 | 脚本里 `boom()` | 0/0 | failed, 1 | Runtime `page_error: boom is not defined`✗；Layout 连坐 sweep_static✗ |
| e6b GSAP 空目标 | `tl.to('#ghost',…)` 选择器拼错 | 0/0 | **passed, 0** | Runtime `console_warning: GSAP target #ghost not found`⚠——动画静默没了 |
| e7 缺 start | clip 无 data-start | 0/0 | passed, 0 | 默认 0，合法 |
| e8 无限循环 | `repeat:-1,yoyo` | — | passed, 0 | Motion `gsap_infinite_repeat`⚠（五片既有基线 warning） |
| e9 跨轨遮挡 | 不透明色块盖过文字 | — | failed, 1 | Layout `text_occluded … Text is hidden beneath an opaque element`（3 samples），放行属性 **`data-layout-allow-occlusion`**（hf-03 时旧名 content_overlap/allow-overlap 已改名） |

## 4. 教学结构：三个认知反转（真机给的，比大纲四类错更有戏）

1. **你以为会拦的，它只警告**：缺 duration、越界都是 warning，`Check passed` 照亮、exit 0——
   但后果是真的（timeline 画不出终点；海报/预览/渲染被切）。warning 是给人读的，绿灯不是免死金牌。
2. **你以为是错的，它判合法**：同 track-index 重叠零报错。track-index 只是 Studio 轨道元数据，
   渲染层叠只看 DOM 顺序（呼应 hf-03）；反过来，**跨轨**不透明元素真盖住文字，Layout 采样点抓到 text_occluded。
3. **人眼难发现的，它铁面抓**：对比度 1.14:1，9 个采样点逐一量，exit 1 硬阻断，还递上修好的颜色。
   为什么 lint 抓不到？颜色是 Chrome 算出来的——静态读文本算不出渲染后的像素。

机制主线：**静态能查的（结构/文件）→ lint；真跑才暴露的（JS 错/警告）→ Runtime；渲染后才量得出的
（遮挡/对比）→ Layout/Contrast**。check ＝ 三层流水线一道闸。

## 5. 录屏段设计 v0（正式录屏待布景脚本定型，需用户离机 2–3h）

| seg | 内容 | 敲键/画面 | 时长估 |
|---|---|---|---|
| A | 好工程跑 check，六段全绿走一遍（建立基线形态） | `npx hyperframes@0.8.107 check` | ~40s |
| B | 删掉 data-duration → check：warning 但 passed（反转1上） | NPP 删行→存盘→check | ~50s |
| C | 加越界 clip → warning＋双修复建议 → 选「延长 root」修好复绿 | NPP 编辑两回合 | ~70s |
| D | **主线「写错→报错→修好」**：字色调近底色 → 5 点 ✗ exit 1 → 按建议色改好 → 复跑全绿（反转3） | NPP＋终端两回合 | ~90s |
| E | 同 track 重叠 → 零报错（反转2）；DOM 顺序挪一下，盖的关系变了 | NPP＋check 两回合 | ~70s |
| F | 给副标题加动画，选择器 `#sub` 拼成 `#sut` → console_warning 但 passed（warning 学院第二案例，副标题动画静默失踪） | NPP＋check | ~50s |
| G | 体检三连快剪：keyframes（列动画＋洋葱皮）、inspect（deprecated 提示）、beats（无音乐轨提示） | 三条命令 | ~45s |
| H | 收尾：check 管机器能判的，审美/节奏归人；`echo $?`/CI 退出码；预告 hf-06 加媒体 | 终端 | ~30s |

录屏净操作估 7–8min 素材，剪到 6–6.5min（论述段上概念卡，参照 hf-04 30s 缺口工艺）。
取舍待定：e6a JS 硬错（page_error＋sweep_static 连坐很有戏剧性）可能替换或并入 F；
e5 缺资源留给 hf-06 加媒体正合适，本片只在概念卡里点名。

## 6. setup_scenes 七权威态真机复验（2026-10-16 凌晨，0.8.107）

布景生成器重跑 init 后，对 `backup/` 七态逐一 `npx hyperframes@0.8.107 check .`：

| 状态 | 实测输出 | exit | 录屏 take 锚点 |
|---|---|---|---|
| s0-good | 六段全绿，10/10 对比通过 | 0 | seg A 基线 |
| s1-no-duration | Lint 1⚠ `timeline_element_missing_timing`，Check passed | 0 | seg B |
| s2-overflow | Lint 1⚠ `clip_ends_past_root_duration`（8s→13s），双修复建议 | 0 | seg C：按建议把 root duration 10→13 复绿 |
| s3-contrast | Contrast 5✗ 全采样点 `1.14:1 (need 3:1)`，Try **rgb(93,97,102)** | **1** | seg D：按建议色改 #title 复绿（建议色已实测） |
| s4-same-track | 六段全绿 | 0 | seg E：track-index 相同且重叠，零报错 |
| s5-null-target | Runtime 3⚠（`#sut not found` 一条＋空 target 两条），Layout 0 issues，Check passed | 0 | seg F：#sub 拼成 #sut，副标题动画静默失踪 |
| s6-occluded | Layout 1✗ `text_occluded #title inside #block`（**9/9 采样点**），Contrast 不连坐 10/10 | 1 | seg E 收尾：蓝块压标题；Fix 文案含三种修法 |

s5 踩坑修正：唯一 tween 指向拼错目标时真实元素不动画，会连坐 Layout `sweep_static` 变 ✗ exit 1
（假时间轴同罚）。布景定型为 title 合法 tween 在前、`#sut` 拼错 tween 追加在后——
时间轴仍前进，只剩 warning，才是 e6b「warning 但 passed」的真机形态。

s6 几何坑：遮挡块首版 350–610 越界连坐盖到 540 的 #sub，多背一条 text_occluded 还把
Contrast 染红蓝底灰字（#sub 1.51:1）；收成 340/370/760×120 只盖标题区后干净 1✗。
**放行属性实测：`data-layout-allow-occlusion` 必须贴在被盖的文字元素（#title）上才 passed；
贴遮挡块（#block）无效。**（临时变体目录测完即删，不进权威态。）

> 退出码测量注意：`check . | tail` 后 `$?` 取到的是 tail 的码；复核退出码必须不接管道
> （`check . > log 2>&1; echo $?`）。正式录屏演示 `echo %ERRORLEVEL%`（cmd）不受此影响。

## 4 类大纲错的最终归属（防止粗稿写串）

- 缺 duration → Lint **warning** 不阻断（不是 error！）
- 时间轴越界 → Lint **warning** 不阻断
- track 冲突 → **不存在**：同轨合法；跨轨遮挡归 Layout `text_occluded` error
- 对比度 → Contrast **error** 硬阻断（唯一在样例里 exit 1 的画面错）
