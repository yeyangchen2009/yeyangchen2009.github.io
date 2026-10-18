# hf-06 媒体功能真机事实台账（HyperFrames 0.8.107，2026-10-18 实测）

> 探针工程：`hf-05/build/hf06-probe/`（gitignored）；沙盒彩排：`F:\_hftest\hf06-media`
> （run_rehearsal.py 16 case 全绿，日志 build/rehearsal-log.txt）。所有报错文案均为
> 本机实跑原文，录屏照此复现，不许凭记忆造。**沙盒彩排数据覆盖早期探针估计值。**

## 元素契约

- 三兄弟：`<img>` / `<video>` / `<audio class="clip">` ＋老三件 `data-start / data-duration / data-track-index`。
- **id 是 media 的命门**：`<video>`/`<audio>` 不写 id＝error `media_missing_id`：
  「The renderer requires id to discover media elements — this video will be **FROZEN** in renders / this audio will be **SILENT** in renders.」
  `<img>` 无 id 仅 warning `studio_missing_editable_id`（Studio 编辑目标），渲染不拦。
  原理：渲染器不是浏览器自动播放，它按 id 把媒体登记进时间轴。
- `<video>` 必须二选一声明声音立场，否则 error `video_missing_muted`：
  无声素材（录屏）写 `muted`；保留原声写 `data-has-audio="true"`。实测原文：「If the file has sound, add data-has-audio="true" … If it is silent, add muted.」
- 缺文件＝硬错误：
  - audio：`audio_src_not_found`「references file(s) not found in the project: …. The rendered video will be **silent**.」
  - video/img：`missing_local_asset`「The renderer will silently skip these and produce a video with **missing visuals**.」
- 占位 URL（example.com 等）＝error `placeholder_media_url`「will 404 at render time」。
- 真实 http(s) URL：lint 0/0 放行——默认 **autoProxy**：本地资源服务器代理远程媒体；`data-autoproxy="false"` 关。
- **退出码**：`lint` 子命令即使有 error 也退 0；`check` 三合一总闸退 1（沿 hf-05 认知）。

## 音量与裁切（docs data-attributes 原文）

- `data-volume`：增益，1＝0dB，0＝静音，顶 3.98（+12dB）。
- `data-fade-in / data-fade-out`：clip 边缘线性增益斜坡（秒），乘在 data-volume 与音量车道之上。
- `data-media-start="2"`：从素材第 2 秒起用（trim）。clip 短于素材合法（0/0）；clip 越过 root duration＝warning `clip_ends_past_root_duration`（hf-04 老相识）。
- 同轨多音频时间重叠＝warning `duplicate_audio_track`「This causes layered audio playback.」BGM 分轨放 track 3。
- music 轨识别（beats 认）：`data-timeline-role="music"` 或 id 起 `music/bgm/soundtrack`。hf-05 beats「没找到音乐轨」的反面。
- 实测：audio 不写 data-volume，0.8.107 不报错（文档 rules 表与实现有出入，口播不说「会警告」）。

## normalize-audio（真机 JSON，沙盒切片 2026-10-18）

`hyperframes normalize-audio --reference voice --target bgm [--write] [--tolerance=0.5] [--json]`
（`--reference=voice` 等号形式同效；终端录屏用空格形式）

- 量 integrated LUFS，算 target 该补的增益，dry-run 给建议，`--write` 才写回 data-volume。
- **沙盒实测数据点（校准终值，2026-10-18 v3 母带）**：voice **-21.8 LUFS**；
  music **-37.2588 LUFS**（显示 -37.3）；gainDb **+7.5**；volume 0.4→**2.371374**
  （--write 写回 6 位小数）；projectedLufs -21.8；projectedTruePeak **-8.8 dBTP**；
  changeDb 15.4588。容差 0.5 LU：写后再跑 `withinTolerance:true, wrote:false,
  changeDb≈-1e-6`（幂等，previousVolume 2.371374）。
- **为什么有 calibrate_media.py**：蝉镜每次整段重渲染，同一切片 LUFS 微漂——
  voice 头 6s 自然值三版母带实测 -21.5/-21.8/-21.4，music15 需增益 16.2/16.0。
  口播念的是一位小数定值，改稿→重合成→数值漂→再改稿是死循环。校准器在
  `setup_scenes init`（直切）之后跑：三件 wav 同乘 10^(k/20) 整体平移（LUFS 差
  不变、建议 volume 不变），把真机显示值锚到 voice **-21.8**；music15 系数
  0.15 时真机即报 **needs 16.0 dB**（一轮命中，无需微调）。台账落
  build/media-calibration.json，彩排断言读台账不钉数值。
  （更早的 hf-05 探针 -37.56/+8.1/2.540973 是另一切片，已作废。）
- **+12dB 天花板**（music15＝同段压 0.15 再叠 data-volume 0.15，校准后需 16.0dB），
  exit **1**：
  `"ok": false, "error": "Matching #bgm needs 16.0 dB, beyond the +12 dB authoring ceiling. A gap this large belongs in the source file, not the mixer — mixer gain raises the noise floor with the signal. Normalize bgm's asset offline (e.g. ffmpeg loudnorm), or lower #voice instead."`
- **id/selector 写错＝exit 1 的明确报错，但什么都不改**（2026-10-18 沙盒彩排，
  **覆盖早期探针"matched:false/exit 0 静默"记录**——以本次真机为准）：
  - normalize target 不存在：exit 1，`{"ok": false, "error": "Target audio #bgn was not found"}`
  - media-treatment 选择器不匹配：exit 1，`{"ok":false,"error":"Selector did not match: #dem",...}`
  - 叙事落点（口播已按此重写）：元素**不写 id** 是 check 硬错误（冻帧/哑巴）；命令里 id
    **写错**是命令自己 exit 1 喊疼，但**文件一个字节没动、渲染没开始**——红句滚屏/脚本
    不查退出码就等于没喊。主题＝命令跑完≠活干完，呼应 sut 鬼故事。

## beats

有 music 轨即产出 `beats/<audio路径>.json`（{version,audio,beats}）。沙盒 music.wav
（6s）实测 **23 拍**。人声切片也硬出拍（探针 21 拍 bpm 262）——检测不挑素材，
但拍子只有真音乐才有意义。非录态 beats 约 16s。

## check 输出形态与真机耗时（热态包缓存，非录态秒表）

- s0 全绿五段：Lint / Runtime / Layout（9 sample）/ Motion / Contrast（10/10 WCAG AA），
  尾行 `◇ Check passed`，exit 0。冷态首跑含 browserGpuMode probe 约 35.7s；
  错误态在 Lint 即短路，约 10–12s；s5（仅 warning 全段跑完）26s，exit **0**。
- s5 同轨重叠 warning 原文：`⚠ duplicate_audio_track: Multiple audible <audio>/<video>
  elements on track 3 overlap (media/voice.wav at 0-6.0s, media/music.wav at 0-6.0s).
  This causes layered audio playback.` —— 1 warning 但 Check passed（warning 不拦）。
- 删 video id 时同屏两条：⚠ studio_missing_editable_id（Studio 目标）＋
  ✗ media_missing_id（FROZEN）。
- 占位 URL 时先出 `[StaticGuard] Invalid HyperFrame contract:` 行再出 ✗ placeholder_media_url。
- normalize 约 9s/条（loudnorm 两遍）；media-treatment analyze 约 11–13s。
- 录制态 gdigrab 同机负载按 hf-05 经验 +20% 留量，等待常量在 record_segments 顶部分档。

## media-treatment（画面素材，一句带过即可）

- `--selector "#id" --analyze --json`：video 抽 5 帧（img 1 帧）量 YUV（yMin/yAvg/yMax、satAvg、削波风险），出 diagnosis＋`suggestedPatch.adjust`（exposure/contrast/blacks/whites/temperature/tint）。
- `--apply` 把调色 patch 写进 index.html（确定性）；四族：correction / grading / presets / finishing；`--capabilities --all` 查目录。
- 实测 hf-05 录屏帧 yAvg 29.5、诊断 no obvious imbalance、建议 exposure +0.245/contrast +0.14（暗色录屏普遍偏暗，analyze 确实看得出来）。

## 粗稿取舍

- 主线：三元素进场 → id 命门（硬错误）→ 文件缺失（扣子1）→ 音乐第二轨 → 音量三属性 → LUFS 归一化 → +12dB 天花板 → id 写错静默（扣子2反转）。
- 一句带过：autoProxy、media-treatment；beats 只做回收 hf-05 钩子。
- 不讲：volume lane/automation（skill 文档级）、grading 深水区、presets 细节。
