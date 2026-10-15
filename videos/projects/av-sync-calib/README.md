# av-sync-calib · 音画偏移标定片

HyperFrames 工程链路的「音画同步基线」工程片（非播出内容）。回答一个问题：
**从 HTML 工程到终片 MP4，渲染与 finalize 拼接这两道工序本身会不会引入音画偏移？**
hf-05 路径 C 第一步，2026-10-15 实测。

## 结论先行

| 版本 | 五事件配对 | 每事件 offset | spread | 门限 |
|---|---|---|---|---|
| body（`render` 直出） | 5/5 | **−0.1ms** | **0.0ms** | PASS |
| 终片（`finalize --intro`） | 5/5 | **−0.1ms** | **0.0ms** | PASS |

- −0.1ms 即测量精度内的**零**（一帧 33.3ms，0.1ms 不可闻见），两版帧位完全一致。
- **渲染管线音画零偏移，finalize --intro 的封面拼接/整段重编码也不引入额外偏移。**
- 因此历史四片 time_offset（hf-01 **0.28**／hf-02 **0.37**／hf-03 **0.29**／hf-04 **0.30**）
  全部来自 **faster-whisper 转 TTS 母带时把句间停顿吞进后段**这一对齐误差，与渲染/拼接无关。
- **time_offset 不能从本片取一个固定值复用**：它补偿的是逐片 TTS 节奏下的 whisper 对齐误差，
  仍须每片用 `oneoffs/measure_offset.py`（silencedetect 法）实测；本片的价值是**排除管线嫌疑、
  建立零偏移基线**——将来升级 HyperFrames/FFmpeg 或怀疑拼接串位时，重跑本片即可定位是哪一环。

## 标定设计

13s、1920×1080@30fps、黑底；5 个事件在 body 时间轴 **t = 3 / 5 / 7 / 9 / 11s**：

- **声音**：`media/beeps.wav`，24kHz mono pcm_s16le（与蝉镜 TTS 母带同规格），
  每事件一个 1kHz／60ms 窄脉冲（peak 0.5），onset 精确落在整秒；
- **画面**：track 0 全程纯黑，track 1 在每事件显示 **0.1s（3 帧）全屏纯白 clip**，
  用 clip 原生 display 切换（不用 GSAP 渐变），取得最锐利的单帧亮度跳变；
- **测量**：音频解出 PCM 做幅值 onset；视频走 ffmpeg `signalstats` 取逐帧 YAVG，
  黑→白上升沿即白闪首帧。`offset = t_visual − t_audio`（正＝画面晚，视觉需提前）。
- 事件从 3s 起，给 finalize `--hold 2.0` 封面段留余量；intro 模式封面静帧占 0–2s，
  裁后 body 画面接在 2s 处放 body t=2、音频整段不动，所以**五事件在终片里仍是 3/5/7/9/11s**，两版同口径直接比。

门限：配对比 ≥ 3/5、spread ≤ 1 帧（33.4ms）、事件帧落在期望时刻 ±0.1s。实测 5/5、spread 0、全中。

## 绑定参数（结论的生效条件）

- HyperFrames **0.8.107**（全季钉死）；Node v24.6.0；FFmpeg 7.1.1；Chrome headless-shell 152；
  软件渲染（`--no-browser-gpu`，SwiftShader）；1920×1080／30fps；CRF looks 默认。
- 脉冲不经 TTS，故本结论与音色/蝉镜版本无关——管线层对任何音轨都零偏移。
- 逐片 time_offset 的绑定对象是 **faster-whisper 模型版本＋TTS 母带规格（24k mono）＋cues 组句参数**，
  不随渲染参数变。

## 复现步骤

```bash
cd videos
python new_project.py av-sync-calib
cp projects/hf-04/gsap.min.js projects/av-sync-calib/   # gsap 不入库，本地复制
cd projects/av-sync-calib

# ① 合成 media/beeps.wav（24k mono，5 脉冲 @3/5/7/9/11s，peak≈0.5）
ffmpeg -y \
 -f lavfi -i "sine=frequency=1000:duration=0.06" \
 -f lavfi -i "sine=frequency=1000:duration=0.06" \
 -f lavfi -i "sine=frequency=1000:duration=0.06" \
 -f lavfi -i "sine=frequency=1000:duration=0.06" \
 -f lavfi -i "sine=frequency=1000:duration=0.06" \
 -filter_complex "[0]adelay=3000[b0];[1]adelay=5000[b1];[2]adelay=7000[b2];\
[3]adelay=9000[b3];[4]adelay=11000[b4];\
[b0][b1][b2][b3][b4]amix=inputs=5:normalize=0,volume=4.0,\
apad=whole_dur=13,atrim=0:13,aresample=24000,asetpts=PTS-STARTPTS[out]" \
 -map "[out]" -ac 1 -c:a pcm_s16le media/beeps.wav

# ② 生成工程并过门控
python make_video.py
npx hyperframes@0.8.107 check

# ③ 渲染 body（须非沙箱：沙箱限内存 4K，libx264 会 malloc failed）
npx hyperframes@0.8.107 render . -o renders/body.mp4 --no-browser-gpu

# ④ 极简封面（snapshots/cover-final.png；内部工程片，Arial 黑底技术卡）
#    再 finalize --intro 出终片
python -m videopipe finalize projects/av-sync-calib \
    --body projects/av-sync-calib/renders/body.mp4 --intro \
    --out projects/av-sync-calib/renders/final-intro.mp4   # 在 videos/ 下执行

# ⑤ 两版测量（脚本同时校验配对/spread/期望时刻，全绿 exit 0）
python oneoffs/measure_av_sync.py renders/body.mp4
python oneoffs/measure_av_sync.py renders/final-intro.mp4
```

## 原始数据（2026-10-15）

```
body：render 51.4s（capture 29.1s / encode 12.9s / 3 workers），13.0s · 390 帧 · 59.7KB
事件  audio onset   白闪帧   visual     offset
 1    3.0001s        90     3.0000s     −0.1ms
 2    5.0001s       150     5.0000s     −0.1ms
 3    7.0001s       210     7.0000s     −0.1ms
 4    9.0001s       270     9.0000s     −0.1ms
 5   11.0001s       330    11.0000s     −0.1ms
配对 5/5 · 中位 −0.1ms · spread 0.0ms（0.00 帧）

final-intro：13.0s；五事件帧位 90/150/210/270/330 与 body 逐帧相同，offset 全 −0.1ms
```

注：白闪帧 n 覆盖时间区间 [n/30, (n+1)/30)，visual 取帧起始；audio 3.0001s 的 0.1ms
是 AAC 重编码后首个越阈采样相对整秒的量化差，远低于感知与单帧量级，两版完全稳定。

## 入库边界

- 入库：`make_video.py`、`oneoffs/measure_av_sync.py`、`hyperframes.json`、`package.json`、`meta.json`。
- 不入库（可重建，已 gitignore）：`media/beeps.wav`（上面 ① 一条命令重建）、`index.html`、
  `gsap.min.js`（从 hf-04 复制）、`renders/`、`snapshots/`、`build/`。
