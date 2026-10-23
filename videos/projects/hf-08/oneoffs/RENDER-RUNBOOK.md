# hf-08 正式 render → finalize 一条龙

所有 render/ffmpeg/npx 命令必须**非沙箱**（沙箱限内存 4K，libx264
malloc failed）。cwd 均为 `videos/projects/hf-08`，除标注 `cd videos` 外。

## 阶段 0–2 · 已完成（2026-10-23，热态演录口径）

用户拍板不重启：t0-sw 在连续开机 26h 后热态演录（冷态 68.1s 尾报口径以
探针彩排台账为准，见 PROBE-NOTES 第 3 节「hf-08 入镜口径」注记）。

- 阶段 0：`python oneoffs/record_segments.py t0-sw`——母带 161.4s
  （F:\_hftest\hf08-rec\takes\t0-sw.mp4，6226779B），已归位 media/t0-sw.mp4。
  实测：打字 6.5–11s／ENTER≈11s／banner≈30s／calibration 134–152s／
  worker 配置 153–158s；160s 停录时正式 capture 未开始，尾报天然不入镜。
- 阶段 1：`probe-fps media/t0-sw.mp4` exit 2（VFR avg 19.02，双闸第一闸过）；
  `cut_shorts frames` 接触表读数（sheet-t0-sw-0.png＋sheet-t0-sw-tail.png）。
  真机秒与暂定偏差 >0.3s，已回填：sw1 8.0→**6.8**、sw2 144.0→**153.8**。
  尾报不是 68.x 是预期（热态），**不打第二条音频补丁**——68 秒口径锚定
  冷态探针日志，热态母带不取尾报。
- 阶段 2：`cut_shorts cut` 出 media/shorts/sw-render.mp4（0–159.8s）；
  `probe-fps media/shorts` exit 0（四条全 CFR，双闸第二闸过）；
  make_video.py 两 clip 已定稿 6.8／153.8（文件存在性降级机制已移除——
  缺资产应由 check 直接报错）；`check` **0 error / 22 warning**；
  snapshot 219.4/228.6 目验通过（打字段命令可读；sw2 一屏集齐
  workerCount:3／gate enabled:false multi_worker／forceScreenshot／
  useStreamingEncode:false／0/3 ready／swiftshader，尾报秒数不在屏）。

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

finalize 内部断言封面头恰 2.000000s。封面用 `build/cover-final.png`
（2026-10-22 已截，533524B，1920×1080 六指纹表），勿依赖 snapshots/ 那份
——每次 snapshot 会清空整个 snapshots/。

## 阶段 5 · 终片 F2

- 视觉：阶段 4 接触表全尺寸补帧，五录屏位/sw 双位/三 freeze/字幕轨在位；
- 声音：`build/f2/pronounce-check.mp3` 38 点已过人耳（2026-10-22/23）；
  热态演录不触发 68 秒第二补丁，无新增补听窗；
- patched 母带窗外逐样本不动已断言；终片音频轴＝正片时间轴。

过了之后进 #612：终片/素材 PR、计时账、速读＋深读复盘、审稿站配图同步。
**B 站发布等用户原话明确指令。**
