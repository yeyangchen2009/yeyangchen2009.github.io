# hf-06《给片子配上声音》分镜框架（录前定稿 v0）

> 上游：`src/hf-06-src.txt`（1851 字／v3 母带 491.835s／cues 288 句 v3 已落地，time_offset 实测 0.31）、
> `MEDIA-FACTS.md`（0.8.107 真机报错文案台账）。
> 机位/安全/精切工艺全部沿用 hf-05（见 ../../hf-05/oneoffs/RECORD-NOTES.md），
> 本篇只定幕表、take 表、概念卡、布景状态机。

## 一、机位（同 hf-05）

| 身份 | 窗口 | 标题针 | 外框几何 |
|---|---|---|---|
| 便携 NPP | `F:\_hftest\npp-local\notepad++.exe -multiInst -nosession F:\_hftest\hf06-media\proj\index.html` | 含 `_hftest\hf06-media` | (-12,0,1624,928) |
| 终端 | `wt.exe -w new --title hf06-rec --suppressApplicationTitle -d <proj> cmd /k <env>` | startswith `hf06-rec` | (-12,0,1632,1000) |

- 录区 gdigrab (0,0,1600,920)@30；沙盒 `F:\_hftest\hf06-media`，素材在 `proj/media/`。
- 终端三环境变量同 hf-05（FONT_CACHE_DIR／NO_UPDATE_CHECK／SKIP_SKILLS）。
- guard 白名单两身份：`_hftest\hf06-media` NPP、`hf06-rec` 终端。

## 二、布景状态机（setup_scenes.py 生成，LF 换行）

好基线 s0 工程 `proj/index.html`（root 12s）：

- `<div id="title">` 暗色文字卡（contrast 过）；
- `<video id="demo" class="clip" data-start="0" data-duration="4" data-track-index="0" src="media/demo.mp4" muted playsinline>`；
- `<img id="pic" class="clip" data-start="4" data-duration="4" data-track-index="0" src="media/pic.png">`；
- `<audio id="voice" … data-track-index="2" src="media/voice.wav" data-volume="1">`；
- `<audio id="bgm" … data-track-index="3" src="media/music.wav" data-volume="0.4" data-timeline-role="music">`。
- check 实测 0 error 0 warning（彩排复核，真机为准）。

素材（setup init 直切→**calibrate_media.py 校准**，不入 git；2026-10-18 v3 母带真机）：
- `voice.wav`＝hf-06 母带 `-t 6` 再整体平移（校准锚 **-21.8 LUFS**，自然值 -21.4、偏移 -0.4dB）；
  `music.wav`＝母带 `-ss 60 -t 6 -af volume=0.4` 同平移（**-37.26 LUFS**，normalize 建议 +7.5dB／
  volume **2.371374**，truePeak -8.8）；
  `music15.wav`＝同段 `-af volume=0.15`（needs **16.0dB**，撞 +12dB 天花板 exit1）；
  校准台账 build/media-calibration.json；蝉镜重合成后重跑 init→calibrate 即可重新锁定。
- `demo.mp4`＝hf-05 一条 shorts（beats.mp4）；`pic.png`＝hf-05 一张 freeze。

| 态 | 与 s0 的差别 | 用途 |
|---|---|---|
| s0-good | 如上 | t0/t6/t7/t8/t10/t11 |
| s4-missing | demo.mp4→gone.mp4、pic.png→gone.png（引用名改，文件不在） | t4 missing_local_asset |
| s5-sametrack | bgm `data-track-index="2"`、起止与 voice 重叠 | t5 duplicate_audio_track |
| s8-placeholder | voice src 改 `https://example.com/voice.wav` | t12 placeholder_media_url |
| s9-ceiling | bgm src 换 music15.wav、data-volume="0.15" | t9 16.0dB 拒绝（exit1） |

现场编辑态（不预制备份，reset s0 后 NPP 现场敲）：
- 删 video 的 ` id="demo"` → media_missing_id（FROZEN）；
- 删 video 的 ` muted` → video_missing_muted；
- voice.wav 改 voise.wav → audio_src_not_found。

## 三、take 表（15 母带，录制顺序＝ALL_TAKES）

| take | 起点态 | 内容 | 估片长 | 产 shorts/freeze |
|---|---|---|---|---|
| t0-good | reset s0 | 首跑 check 全绿（别敲第二遍） | 34 | good-run |
| t1a-del-id | reset s0＋NPP | 双击选中 `id="demo"` 删除、存盘 | 12 | del-id（edit） |
| t1b-noid-run | 接态 | check 红 media_missing_id「will be FROZEN」 | 34 | noid-run |
| t2a-del-muted | reset s0＋NPP | 删 ` muted`、存盘 | 10 | del-muted（edit） |
| t2b-nomuted-run | 接态 | check 红 video_missing_muted | 34 | nomuted-run |
| t3a-bad-src | reset s0＋NPP | voice.wav→voise.wav（退格 c 敲 s）、存盘 | 12 | bad-src（edit） |
| t3b-badaudio-run | 接态 | check 红 audio_src_not_found「will be silent」 | 34 | badaudio-run |
| t4-missing | reset s4 | check 红 missing_local_asset×2「silently skip」 | 34 | missing-run |
| t5-sametrack | reset s5 | check ⚠ duplicate_audio_track（layered playback），passed | 34 | sametrack-run |
| t6-beats | reset s0 | beats 出拍子（music.wav 23 拍，写 beats/media/music.wav.json） | 24 | beats-run |
| t7-norm-dry | reset s0 | normalize-audio voice→bgm --json：-21.8/-37.26/gain 7.5，wrote:false | 24 | norm-dry |
| t8-norm-write | 接态 | --write 写回 volume 2.371374；再跑 withinTolerance:true | 43 | norm-write |
| t9-ceiling | reset s9 | normalize exit1「needs 16.0 dB … +12 dB authoring ceiling」 | 24 | ceiling |
| t10-badid | reset s0 | normalize --target bgn exit1「Target audio #bgn was not found」；treatment --selector #dem exit1「Selector did not match」 | 49 | badid |
| t11-treatment | reset s0 | media-treatment --selector "#demo" --analyze --json（measured/suggestedPatch） | 24 | treatment |
| t12-placeholder | reset s8 | check 红 placeholder_media_url「will 404」（StaticGuard 行同屏） | 34 | placeholder-run |

净素材 460s ≈ 7.7 min；加 3 次 NPP 冷启与 take 间布景，单次全推 25–35 min，按 2–3h 占机留缓冲。
等待常量（run_rehearsal.py 非录态实测 2026-10-18，录制态 +20%）：check 冷态 35.7s（含 GPU
probe，warmup 吞）／错误短路 10–12s／warning 全段 26s；beats 16s；normalize 9s/条；
treatment 11–13s。录制态取 CHECK_WAIT=28（全段）、BEATS_WAIT=20、NORM_WAIT=14、TREAT_WAIT=16。

## 四、幕表（make_video 17 幕，时点待 cues 细化后回填）

| 幕 | 口播段 | 画面 |
|---|---|---|
| m01 | 默片钩子（每个 video 都 muted） | C0 标题＋概念卡：一排 video 标签全盖 muted 灰章 |
| m02 | 三兄弟＋老契约 | C1 img/video/audio 三标签＋clip/start/duration 三件套 |
| m03 | 删 id＝身份证 | shorts del-id＋noid-run（终端缩左＋右卡 C2 FROZEN/SILENT；img 仅 warning 对比） |
| m04 | muted 声音立场 | shorts del-muted＋nomuted-run（右卡 C3 岔路 muted↔data-has-audio） |
| m05 | 扣子1：文件找不到 | shorts bad-src＋badaudio-run（audio_src_not_found 行定格） |
| m06 | silently skip＋exit 1 | shorts missing＋placeholder（C4 三连报错谱） |
| m07 | audio 进场：a-roll-audio 第二轨 | C5 工程卡：人声就是一个 audio 标签 |
| m08 | 同轨层叠＋BGM 第三轨 | shorts sametrack（warning 行定格） |
| m09 | music 轨＋beats | shorts beats（C6 两轨示意＋beats 地图） |
| m10 | 音量三件套 | C7 data-volume 0–3.98 尺／fade in-out／media-start |
| m11 | LUFS 客观尺 | shorts norm-dry（C8 −21.8 vs −37.3 双表） |
| m12 | --write 与幂等 | shorts norm-write（2.371374 写回＋withinTolerance） |
| m13 | +12dB 天花板 | shorts ceiling（C9 噪声底示意＋loudnorm/调小两正路） |
| m14 | 扣子2：id 写错 exit1 但不动文件 | shorts badid（C10「命令跑完≠活干完」：红报错＋文件没变，呼应 sut 鬼故事） |
| m15 | autoProxy＋media-treatment | shorts treatment（analyze JSON 一句带过；远程代理小卡） |
| m16 | 收尾三件事 | C11 金句 recap |
| m17 | 行动件＋hf-07 预告 | 行动件卡＋片尾 |

概念卡 C0–C11 全暗色 GitHub Dark（#0d1117/#161b22），金色主调（声音集），
报错卡红 #f85149、警告 #d29922、绿 #3fb950、蓝 #58a6ff，沿 hf-05 卡片语法。
freeze 一律尾帧 PNG（warning/JSON 运动帧不给观众读）。

## 五、录前决策（已定，不再问）

1. 演示沙盒与正片工程分离（沙盒 F:\_hftest，正片口播人声是 hf-06 真母带）。
2. 规则名/报错文案逐字以 MEDIA-FACTS.md 真机台账为准，NPP/终端不许造文案。
3. 三现场编辑只做「删除/改字母」简单操作，不做整块移动（避开 hf-05 Scintilla 选区坑）。
4. t8 --write 会改沙盒 index.html，下一个 reset s0 的 take 自动恢复，幂等。
5. 标题暂用 B「给片子配上声音：媒体进场与一把响度尺」，发布前可换。
