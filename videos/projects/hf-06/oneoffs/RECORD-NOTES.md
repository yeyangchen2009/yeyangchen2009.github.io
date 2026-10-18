# hf-06《给片子配上声音》正式录屏台账

> 上游：`src/hf-06-src.txt`（1851 字／v3 母带 491.835s）、`STORYBOARD-FRAMEWORK.md`
> （17 幕/16 take）、`MEDIA-FACTS.md`（0.8.107 真机报错文案台账）。本篇只记
> **正式录屏**的机位、命令、take 表、实测耗时与坑。布景＝`setup_scenes.py`
> 在 `F:\_hftest\hf06-media` 生成五权威态，响度由 `calibrate_media.py` 锚定。

## 一、机位（沿用 hf-05，两身份）

| 身份 | 窗口 | 标题针 | 外框几何 |
|---|---|---|---|
| 便携 NPP | `F:\_hftest\npp-local\notepad++.exe -multiInst -nosession F:\_hftest\hf06-media\proj\index.html` | 含 `_hftest\hf06-media` | (-12,0,1624,928) |
| 终端 | `wt.exe -w new --title hf06-rec --suppressApplicationTitle -d <proj> cmd /k <env>` | startswith `hf06-rec` | (-12,0,1632,1000) |

- 录区：gdigrab 物理 **(0,0,1600,920)@30**；系统 DPI 150%，坐标全是物理像素。
- 右边 12px 圆角透明带：实体右缘到 1600 才零穿帮。BlackMat 垫窗遮底缘缝；鼠标 park (12,884)。
- 无浏览器/CDP/dev server：check/beats/normalize/treatment 直接读磁盘文件。
  guard 白名单只两身份，用户回机切窗，下一注入立即 `UnsafeForeground` 中止。
- 终端三环境变量：`HYPERFRAMES_FONT_CACHE_DIR=F:\_hftest\.cache\fonts`、
  `HYPERFRAMES_NO_UPDATE_CHECK=1`、`HYPERFRAMES_SKIP_SKILLS=1`。
- `--suppressApplicationTitle` 必须有：npx 会 SetConsoleTitle，没它标题针失配。

## 二、命令与等待常量（2026-10-18 沙盒彩排真机标定，热态，UHD620）

| 命令 | 非录制态墙钟（热） | 常量/片长 |
|---|---|---|
| `check .` s0 全绿（五段） | 22.6s（冷态首跑含 GPU probe 35.7s，warmup 吞） | **CHECK_WAIT=28**，run 片 34 |
| `check .` 错误态（Lint 短路） | 10–12s | 同上，尾帧充裕 |
| `check .` s5 仅 warning 全段 | 26s，exit 0 | 同上 |
| `lint .` | 9.1s | （仅 warmup） |
| `beats .`（真出 23 拍 bpm 243.9） | 10.6–16s | **BEATS_WAIT=20**，片 24 |
| `normalize-audio … --json`（dry/write/幂等） | 8.1–8.5s | **NORM_WAIT=14**，片 24 |
| normalize target 写错（exit1） | 8.5s（冷轮曾 22s） | t10 给 14s |
| `media-treatment --analyze --json` | 11.5s | **TREAT_WAIT=16**，片 24 |
| treatment selector 写错（exit1） | 8.8s | t10 给 16s |
| s9 天花板（exit1） | 同 normalize ~9s | 片 24 |

全新 cmd 首轮 npx 冷启另算，正式录前必须跑 `warmup` 吞掉（warmup 连跑
check×2/beats/norm/treatment，约 3 min）。

## 三、五态＋三编辑的入镜基准（逐字以 MEDIA-FACTS.md 为准）

- **s0-good**：五段全绿 Lint/Runtime/Layout(9 samples)/Motion/Contrast(10/10
  WCAG AA)，尾行 `◇ Check passed`，rc=0。
- **删 id（现场编辑）**：同屏 `⚠ studio_missing_editable_id` ＋
  `✗ media_missing_id: … this video will be FROZEN in renders.`，rc=1。
- **删 muted（现场编辑）**：`✗ video_missing_muted: … declares neither muted
  nor data-has-audio …`（带 Fix 行：有声加 data-has-audio、无声加 muted）。
- **voice.wav→voise.wav（现场编辑）**：`✗ audio_src_not_found: … not found in
  the project: media/voise.wav. The rendered video will be silent.`
- **s4-missing**：两条 `✗ missing_local_asset: … silently skip these and
  produce a video with missing visuals.`
- **s5-sametrack**：`⚠ duplicate_audio_track: Multiple audible
  <audio>/<video> elements on track 3 overlap (media/voice.wav at 0-6.0s,
  media/music.wav at 0-6.0s). This causes layered audio playback.`
  ——1 warning 但 **Check passed，rc=0**（warning 不拦）。
- **s8-placeholder**：先 `[StaticGuard] Invalid HyperFrame contract:` 行，再
  `✗ placeholder_media_url: … will 404 at render time:
  https://example.com/voice.wav`。
- **s9-ceiling**：normalize exit1，`"ok": false, "error": "Matching #bgm
  needs 16.0 dB, beyond the +12 dB authoring ceiling. … mixer gain raises the
  noise floor … ffmpeg loudnorm … or lower #voice instead."`
- **normalize dry（s0 校准后）**：`referenceLufs -21.8 / targetLufs
  -37.2588 / gainDb 7.5 / volume 2.371373705661655 / wrote:false`；
  `--write` 当次 JSON 给全精度，**写盘 data-volume="2.371374"**（6 位），
  再 dry 给 `withinTolerance:true`＋`"previousVolume": 2.371374`。
- **id 写错**：`{"ok": false, "error": "Target audio #bgn was not found"}`
  rc=1；**selector 写错**：`{"ok":false,"error":"Selector did not match:
  #dem",…}` rc=1。两条都只喊疼不干活（文件不变、渲染没开始）。
- **beats**：`✓ Wrote 23 beats → beats/media/music.wav.json (bpm 243.9, low)`。

## 四、take 表（16 母带，录制顺序＝ALL_TAKES）

| take | 起点态 | 内容 | duration | 产 shorts |
|---|---|---|---|---|
| t0-good | reset s0 | 首跑 check 五段全绿（别敲第二遍） | 34 | good-run |
| t1a-del-id | reset s0＋NPP | L24 删 ` id="demo"`、存盘 | 12 | del-id-edit |
| t1b-noid-run | 接态 | check 红 FROZEN（同屏 studio⚠） | 34 | noid-run |
| t2a-del-muted | reset s0＋NPP | L25 删 ` muted`、存盘 | 10 | del-muted-edit |
| t2b-nomuted-run | 接态 | check 红 video_missing_muted | 34 | nomuted-run |
| t3a-bad-src | reset s0＋NPP | L29 选区 voice.wav 打字覆盖 voise.wav、存盘 | 12 | bad-src-edit |
| t3b-badaudio-run | 接态 | check 红 audio_src_not_found silent | 34 | badaudio-run |
| t4-missing | reset s4 | missing_local_asset×2 silently skip | 34 | missing-run |
| t5-sametrack | reset s5 | duplicate_audio_track⚠ 但 passed（rc=0） | 34 | sametrack-run |
| t6-beats | reset s0 | beats 出 23 拍写 beats/ | 24 | beats-run |
| t7-norm-dry | reset s0 | normalize --json：-21.8/-37.26/7.5，wrote:false | 24 | norm-dry |
| t8-norm-write | **接 t7 态** | --write 写盘 2.371374；再 dry：withinTolerance | 43 | norm-write |
| t9-ceiling | reset s9 | exit1 needs 16.0 dB＋+12 ceiling 长句 | 24 | ceiling |
| t10-badid | reset s0 | --target bgn exit1；treatment --selector #dem exit1 | 49 | badid |
| t11-treatment | reset s0 | treatment --selector "#demo" --analyze --json | 24 | treatment |
| t12-placeholder | reset s8 | StaticGuard＋placeholder_media_url will 404 | 34 | placeholder-run |

净素材 460s ≈ 7.7 min；加三次 NPP 冷启与 take 间布景，单次全推约 20–30 min；
留 NG 缓冲按 **2–3h 占机**（真人离机，开始前必须与用户确认时段）。
注意 **t8 依赖 t7 刚跑完的 s0 态**（dry 不写文件）；单独重录 t8 前先
`python oneoffs/setup_scenes.py restore s0-good`（或先重录 t7）。

## 五、录前检查（按序）

1. **布景与响度**（母带重合成后也走这套）：
   `python oneoffs/setup_scenes.py init`
   `python oneoffs/calibrate_media.py`（非沙箱；锚 voice -21.8／music15 needs 16.0，
   台账落 build/media-calibration.json）
2. `python oneoffs/run_rehearsal.py`——16 case 全 PASS（非沙箱，约 4 min）。
3. `python oneoffs/check_anchors.py`——退出码 0 才开拍（五态 LF 闸、锚点唯一性、
   行号 L24/L25/L29、三编辑磁盘镜像、校准台账）。
4. 便携 NPP 目验：暗色主题、zoom=0、Wrap=no；行号槽暗色由 record_segments
   开窗后补发 Scintilla 2052/2051（同 hf-05 工艺）。
5. `python oneoffs/record_segments.py warmup`——吞冷启＋五条命令输出目验。
6. 关闭用户日常 NPP 里任何同名 index.html；录屏机黑屏/休眠关闭，通知静音。
7. 录制前对 ALT/CTRL/SHIFT/WIN 发 keyup 清异步键态（hf-05 Alt+Tab 事故预防）。

## 六、录后流程

1. 每 take 自动抽 2s/帧到 `F:\_hftest\hf06-rec\frames\`，立即 contact 目验＋
   尾帧彻查（报错文案逐字对第三节；NG 当晚重录——a/b 成对设计使重录成本
   最小：编辑废只重 a，跑废只重 b）。
2. 母带归位（gitignored）：
   `copy F:\_hftest\hf06-rec\takes\*.mp4 videos\projects\hf-06\media\`
3. **粗切**：`python oneoffs/cut_shorts.py frames`→目验 sheet→回填 CUTS→`cut`
   （16 short 宁长勿短＋同名尾帧 freeze）。
4. CFR 双闸（在 `videos/` 下，glob 是 `t*.mp4`）：
   `python -m videopipe probe-fps projects/hf-06/media/t*.mp4` 必须 exit 2（原始 VFR）；
   `python -m videopipe probe-fps projects/hf-06/media/shorts` 必须 exit 0。
   精切四参数 `-vf fps=30 -g 30 -keyint_min 30 -movflags +faststart` 已在 cut 模板。
5. **二切**：`python oneoffs/cut_final.py frames`→目验 build/final-frames/sheet-*
   →回填 CUTS2→`cut`，产出片首打字段（*-type/-cmd/-act）＋过程 freeze
   （dry-json/write-json/idem-json/bgn-err/dem-err/treat-result 等，命名见
   cut_final.py 头部长表；bgn/dem 两段都出自 t10-badid，勿混 t11-treatment）。
6. **对齐 make_video**：去掉 `--cards-only`，按 CUTS2 实际产物改 VIDEOS 段
   src 名与 data-start/duration（当前为粗切同名＋预估时长占位；S2/S11/S12/
   S14/S15 要换成「短打字段＋长 freeze」多段式）。
7. `python make_video.py`→check 0 error→snapshot 录屏与右卡同屏目验→
   render（非沙箱）→finalize 拼封面 2s→轻量 F2→PR。

## 七、录前已知风险点（坑段待代录回填）

1. **t8/t10 是唯二的双命令 take**：第二条命令必须在第一条回提示符后敲
   （等待常量已按非录态×1.2 留量：14/16s）。若录制态 normalize 冷到 20s+，
   第二条会排队进 conin——发现尾帧异常优先查这两条。
2. **t1a/t2a/t3a 都是单跨区小编辑**：删/覆盖后 save 谓词严格（见
   check_anchors 镜像），禁做整块移动（hf-05 Scintilla 选区坑不重复）。
3. **布景 CRLF 坑已由 setup newline="\n"＋check_anchors bytes 闸双保险**；
   权威文件若被外部编辑器动过（存成 CRLF），闸会红——重跑 setup init。
4. **校准值不要手抄进任何脚本**：彩排断言读 build/media-calibration.json；
   母带重合成后 init→calibrate 一条龙，数值自动跟随。
5. **NPP「重新加载」框**：reset 覆盖文件前必须先关实例（reset 已保）；
   close_any_npp 三轮关不掉且 exe 非 npp-local 会拒绝强杀。
6. 管道坑：量退出码别接管道（`check | tail` 后 `$?` 是 tail 的码）。
