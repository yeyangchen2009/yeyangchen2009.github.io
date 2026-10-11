# hf-03 录屏素材笔记（粗稿开路·素材先行第③步产物）

2026-10-11 正式录屏，7 个 take 全部目验通过，已归位 `media/`
（1600×920@30 gdigrab，共 220.9s / 4.8MB，gitignore 不入库）。
口播定稿（#516）对着本笔记＋成片帧对时间窗；最终分镜（#518）
从此长 take 里 ffmpeg 切短片段（hf-02 模式：短片＋freeze 帧）。

时间为脚本时序推算（record 起抓后 1.0s 才进 act，操作耗时按实测估），
精确切点以 `-ss T -frames:v 1` 抽帧复核为准。

| take | 时长 | 内容 | 关键时间窗（录制内秒） |
|---|---|---|---|
| rec-attrs-cdn | 28.0 | S0 首屏 → 四属性两拍 → CDN 换本地 | 0–3.2 首屏；~4–7 拍A `class/data-start/data-duration=10`；~8–10.8 拍B `data-track-index/Title`；~12–14 旧 CDN 地址（jsdelivr@3.14.2）；~16–20 换好本地 `gsap.min.js`，尾镜停到 28 |
| rec-title-time | 26.0 | 旧 Title → 「我的第一个片段」＋2/4 | 0–3 开场旧属性；~4–5.8 旧 Title 全貌；~8.7–11.7 `data-start=2/duration=4`；~12.7–15.9 新标题文字；~17–19.3 回到 2/4 |
| rec-play | 11.93 | Edge 点 Play，2 秒进、6 秒走（实测帧） | 0–2.3 空场 00:00 三角；2.3 手型正中 Play；点击 ≈2.4；标题进 ≈4.4（5.7 帧 00:02 在屏）；标题走 ≈8.4（10.8 帧 00:07 已走） |
| rec-stack | 50.0 | root relative → #card/#subtitle 样式 → 层叠 Alt+Up | 1–3.6 旧 #root；~5.6–8.6 ④a `position:relative`；~9.6–11.8 旧 #title 样式；~17–20.8 ④b #card/#subtitle 样式块；~21.8–23.6 body 旧序；~27.5–30.1 card 插在 title 后（属性拍）；~31–33.9 文案「HTML 里后写的，盖在上面」；~36.4–39.4 ④d Alt+Up 提到 title 前；~43–46.2 ④e subtitle「零行 JavaScript，先出片子」；尾镜到 50 |
| rec-check-fail | 45.5 | npm run check 报 content_overlap | 命令 ≈3.5 发出；~4–8 Checking；红 ✗ 结论约 34–36 出现，停到 45.5（≥9s 尾镜）。文案：`t=3-4.88s (17 samples) content_overlap #card inside #title ... Fix: ... data-layout-allow-overlap`＋`1 error(s)`＋红 `Check failed` |
| rec-allow-overlap | 14.0 | card 行加 data-layout-allow-overlap | 0–3.2 S3 card 行；~6–9.4 行尾 `allow-overlap="" data-track-index="0">HTML 里后写的…`；尾镜到 14 |
| rec-check-pass | 45.5 | 再跑 check 全绿 | 节奏同 fail；绿 `Check passed` 约 34–36 出现停到尾；Layout `0 issues across 9 samples`、Contrast 4/4 WCAG AA |

备忘：
- check 无头稳态耗时 20.7s（pass）/22.4s（fail）；TTY＋录屏并发约 33–36s，
  等待给 42s（首版 24s 没拍到结论，已重录）。
- seg5a 运行中 WT tab 标题会变 `C:\WINDOWS\system32\cmd`（npm 子进程占标题），
  pass 段空提示符时是 `hf03-rec`；均无用户名穿帮。
- 底缝防穿帮＝BlackMat 黑垫窗（blackmat.py）；进程收尾 Tcl_AsyncDelete
  abort（exit 3）无害：产物完整、窗口随进程销毁，无残留。
