# hf-08 冷态 t0 → 正式 render → finalize 一条龙

唯一硬前置：**t0-sw 必须是开机后第一个 render**。冷态＝npx 包解析＋Chrome/
系统冷缓存全在这一条上（实测跳过 t0 时，会话首 render 前置长尾 118s）。
录之前机器不得跑任何 node/npx/Chrome。

所有 render/ffmpeg/npx/录屏命令必须**非沙箱**（沙箱限内存 4K，libx264
malloc failed）。cwd 均为 `videos/projects/hf-08`。

## 阶段 0 · 冷态录 t0（用户重启后第一件事，约 4 分钟）

用户重启进系统后，不打开任何 node/npx/Chrome/浏览器，直接通知开工：

```bash
python oneoffs/record_segments.py t0-sw
```

WAIT sw=155s（含冷态前置），gdigrab 母带落 `F:\_hftest\hf08-rec\takes\t0-sw.mp4`，
覆盖首录事故废片（552238B）。具名跑自带 prepare_term 置前过 HWND 闸。

## 阶段 1 · 母带归位＋真机读数

```bash
cp /f/_hftest/hf08-rec/takes/t0-sw.mp4 media/t0-sw.mp4
cd /f/Data/gmeek-site/videos
PYTHONPATH=. python -m videopipe probe-fps projects/hf-08/media/t0-sw.mp4
# 期望 exit 2（gdigrab 原始 VFR）
cd projects/hf-08
python oneoffs/cut_shorts.py frames     # t0 布点已在 PROBE，自动补抽
```

看 `build/frames/sheet-t0-sw-0.png`（stamped 接触表带黄字时间戳），读三件事：

1. **尾报 rendered in ??s**——口播「软件路首跑**六十八**秒」。若真机不是
   68.x：追加第二条音频补丁（`patch_audio_54.py` 的 PATCHES 加一行，同工艺
   重取整句），并回填 src/tts/draft/cues 数字；若 68.x 则不动。
2. **sw1 打字段真机秒**（暂定 data-media-start 8.0：cd→cls→命令打字）。
3. **sw2 尾报前进行段真机秒**（暂定 144.0：Streaming/尾报前）。
   读数与暂定偏差 >0.3s 则回填 make_video.py 两处 data-media-start。

## 阶段 2 · 切 short＋重生成＋门控

```bash
python oneoffs/cut_shorts.py cut        # 产出 media/shorts/sw-render.mp4
cd /f/Data/gmeek-site/videos
PYTHONPATH=. python -m videopipe probe-fps projects/hf-08/media/shorts
# 期望 exit 0（四条 short 全 CFR）
cd projects/hf-08
python make_video.py                    # sw 两 clip 自动从注释降级切回真机
npx hyperframes@0.8.107 check           # 期望 0 error / 22 warning
```

snapshot 目验两 sw 位（216.8–222 中点 219.4、226.2–231 中点 228.6）：

```bash
npx hyperframes@0.8.107 snapshot --at 219.4,228.6 --no-browser-gpu
```

**注意 snapshot 会清空 snapshots/**——封面图有备份 `build/cover-final.png`
（2026-10-22 已截，533524B，1920×1080 六指纹表），finalize 用 `--cover
build/cover-final.png` 即可，勿依赖 snapshots/ 那份。

## 阶段 3 · 正式 render（非沙箱，预计 45–50 分钟）

composition 611.51s × 30fps ≈ **18346 帧**；本机 UHD620 集显，长片
自动 drawelement 单 worker（hf-07 16777 帧 41m43s，本片约 46–48min）。

```bash
npx hyperframes@0.8.107 render
# 默认 cwd=. 、GPU auto-detect（本机即 browser GPU/硬件路）、
# 30fps standard；产物 renders/hf-08_<日期>_<时间>.mp4
```

跑起来后确认横幅 `auto workers` 实际收成 1、`GPU: browser GPU`。
中途 worker 静默退出＝内存，按提示 -w 1 重烤（本片本来就该 1）。

## 阶段 4 · 抽帧验收＋finalize

抽帧必须 output seeking＋`-nostdin`（sparse-keyframe 终片 input seeking
会从头解）；用公共件 `videos/tools/frames_at.py`。关键位：封面后首帧、
五录屏 clip 中点（14.5/219.4/228.6/240.6/248.2/410.4）、m09 时间账卡、
strict-abort 436.9、missing-audio 455、片尾 609。

```bash
cd /f/Data/gmeek-site/videos
python tools/frames_at.py projects/hf-08/renders/hf-08_<时间>.mp4 \
    2=cover 14.5=hash6 219.4=sw1 228.6=sw2 240.6=hw1 248.2=hw2 \
    410.4=badlint 436.9=strict 455=missing 609=bye \
    -o projects/hf-08/build/final-frames --sheet 5x2
# 全尺寸补帧：对关键位加 --scale ""（默认抽 480x270 缩略＋接触表）
PYTHONPATH=. python -m videopipe finalize projects/hf-08 \
    --cover projects/hf-08/build/cover-final.png \
    --body  projects/hf-08/renders/hf-08_<时间>.mp4
# → projects/hf-08/media/hf-08-yeyang-cover.mp4（封面 2s 静帧头，无 --intro：
#   报名「我是叶扬」在片尾；终片 ffprobe 应 ≈613.51s）
```

finalize 内部断言封面头恰 2.000000s。

## 阶段 5 · 终片 F2

- 视觉：阶段 4 接触表全尺寸补帧，五录屏位/sw 双位/三 freeze/字幕轨在位；
- 声音：`build/f2/pronounce-check.mp3` 38 点已过人耳（2026-10-22）；
  若阶段 1 触发 68 秒第二补丁，补切该窗 ±0.6s 人耳复听；
- patched 母带窗外逐样本不动已断言；终片音频轴＝正片时间轴。

过了之后进 #612：终片/素材 PR、计时账、速读＋深读复盘、审稿站配图同步。
**B 站发布等用户原话明确指令。**
