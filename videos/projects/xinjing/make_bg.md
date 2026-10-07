# 背景视频 bg.mp4 制作记录

71.5s／1920×1080／30fps 动态云雾实景背景。素材来自 coverr.co（免费可商用；
2026-10 本机网络下 Pexels/Pixabay 均 403，仅 coverr 可直连）。完整踩坑
经过见教程《动态视频背景：多彩实景、彩色化纠正与成片压缩》，这里只留
可复现命令。

## 素材（四段，颜色层层递进：翠绿 → 金秋 → 粉橙晚霞）

| 段 | base_filename | 画面 |
|---|---|---|
| p1 | coverr-a-green-mountain-4652 | 翠绿群山航拍＋蓝天裸岩 |
| p2 | coverr-lush-green-mountain-pathway | 翠绿山谷土路（清晨） |
| p3 | coverr-beautiful-scenery-of-an-autumn-forest-4217 | 金黄秋叶＋蓝天 |
| p4 | coverr-sunrise-in-queenstown-new-zealand-9001 | 粉橙火烧云映紫红湖面 |

搜索 API 参数名是 `query`（不是 `q`）；下载不用 Mux playback_id（403），
走 coverr CDN：

```bash
curl -L "https://cdn.coverr.co/videos/{base_filename}/1080p.mp4" -o pN.mp4
```

## 裁切＋统一帧率（保色，★不压 saturation）

```bash
ffmpeg -i p1.mp4 -ss 1.0 -t 13.0 -vf "fps=30,eq=saturation=1.06:contrast=1.03,format=yuv420p" -preset veryfast cseg-p1.mp4
ffmpeg -i p2.mp4 -ss 0.8 -t 12.4 -vf "fps=30,eq=saturation=1.06:contrast=1.03,format=yuv420p" -preset veryfast cseg-p2.mp4
ffmpeg -i p3.mp4 -ss 1.2 -t 21.9 -vf "fps=30,eq=saturation=1.06:contrast=1.03,format=yuv420p" -preset veryfast cseg-p3.mp4
ffmpeg -i p4.mp4 -ss 1.0 -t 26.3 -vf "fps=30,eq=saturation=1.10:contrast=1.03,format=yuv420p" -preset veryfast cseg-p4.mp4
```

★铁律：要彩色就别压饱和度。第一版 `saturation=0.45`＋压亮把整片调成了
黑白。暗角也不在 ffmpeg 做（vignette 慢），由 make_video.py 里 #bgveil
四层渐变在 HTML 中布光。

## xfade 三段接缝（duration .7，净时长 71.5s）

offset 在累积输出时间轴上，每接一段要减去已用过渡时长（.7×接缝数）：

```bash
ffmpeg -i cseg-p1.mp4 -i cseg-p2.mp4 -i cseg-p3.mp4 -i cseg-p4.mp4 \
 -filter_complex "\
[0][1]xfade=transition=fade:duration=0.7:offset=12.3[x1];\
[x1][2]xfade=transition=fade:duration=0.7:offset=24.0[x2];\
[x2][3]xfade=transition=fade:duration=0.7:offset=45.2,format=yuv420p[v]" \
 -map "[v]" -preset veryfast -c:v libx264 bg.mp4
```

产出约 40MB，放到 `media/bg.mp4`（大文件不入库，gitignore）。
