# -*- coding: utf-8 -*-
"""hf-06 · 封面生成器（暗色工作室金/绿，与 hf-05 同视觉系）。

本集主题是「媒体进场＋响度归一化」：右窗两条音轨——VOICE 波形满幅、
右侧 −21.8 LUFS；MUSIC 波形原本矮一截（−37.3），一道绿箭头拉到
−21.8；窗底一行 normalize-audio 命令。圆徽章＝金喇叭出声波（片子开口）。
数值取自 build/media-calibration.json（calibrate_media.py 真机校准）。
截图：
  chrome-headless-shell --screenshot=snapshots/cover-final.png \
      --window-size=1920,1080 --hide-scrollbars \
      --virtual-time-budget=5000 file:///<绝对路径>/cover.html
用法：python make_cover.py [输出html路径]
"""
import io
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def wavebars(seed, n, lo, hi, color, width=440, base=72, bw=4, gap=2):
    """确定性波形柱（多频正弦叠加，禁用随机）。返回 SVG rect 串。"""
    out = []
    for i in range(n):
        t = i / n
        v = (lo + (hi - lo) * (
            0.5 + 0.5 * math.sin(seed + t * 26.0) * 0.55
            + 0.28 * math.sin(seed * 2.3 + t * 61.0)
            + 0.16 * math.sin(seed * 4.1 + t * 113.0)))
        v = max(lo, min(hi, v))
        h = max(3, round(v * base))
        x = i * (bw + gap)
        y = (base - h) / 2
        out.append('<rect x="%.1f" y="%.1f" width="%d" height="%d" rx="1" '
                   'fill="%s"/>' % (x, y, bw, h, color))
    return '<svg width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>' % (
        width, base, n * (bw + gap), base, "".join(out))


voice_wave = wavebars(1.7, 70, 0.42, 0.98, "#e3b341")
music_wave = wavebars(4.2, 70, 0.08, 0.26, "#8b949e")

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>hf-06 封面</title>
<link rel="stylesheet" href="../../assets/wenkai/lxgwwenkai-bold.css">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:1920px; height:1080px; overflow:hidden; }
  body { background:#0d1117; color:#e6edf3;
    font-family:'LXGW WenKai Bold','LXGW WenKai','Microsoft YaHei',sans-serif;
    position:relative; }
  #bg-grid { position:absolute; inset:0;
    background-image:
      linear-gradient(rgba(227,179,65,.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(227,179,65,.05) 1px, transparent 1px);
    background-size:80px 80px; }
  #bg-glow { position:absolute; inset:0;
    background:
      radial-gradient(720px 500px at 12% 18%, rgba(227,179,65,.13), transparent 70%),
      radial-gradient(840px 580px at 88% 88%, rgba(63,185,80,.10), transparent 70%); }

  /* ===== 左侧主张 ===== */
  #left { position:absolute; left:120px; top:0; width:900px; height:1080px; }
  #tag { position:absolute; top:208px; font-size:30px; color:#58a6ff;
    letter-spacing:.32em; font-family:'Consolas',monospace; }
  #title { position:absolute; top:276px; font-size:118px; line-height:1.18;
    color:#e3b341; letter-spacing:.06em; white-space:nowrap; }
  #sub { position:absolute; top:560px; font-size:50px; color:#e6edf3;
    letter-spacing:.06em; }
  #sub .en { color:#7ee787; font-family:'Consolas',monospace; font-size:.82em; }
  #motto { position:absolute; top:668px; font-size:38px; color:#8b949e;
    line-height:1.7; }
  #motto b { color:#e3b341; font-weight:normal; }
  #rule { position:absolute; top:812px; width:120px; height:6px;
    background:#e3b341; border-radius:3px; }

  /* ===== 右侧多轨窗 ===== */
  #term { position:absolute; left:1010px; top:190px; width:800px;
    background:#161b22; border:2px solid #30363d; border-radius:18px;
    box-shadow:0 30px 90px rgba(0,0,0,.6); overflow:hidden; }
  #term-bar { height:64px; background:#0d1521; border-bottom:2px solid #30363d;
    display:flex; align-items:center; padding:0 26px; }
  .dot { width:15px; height:15px; border-radius:50%; margin-right:12px; }
  .d1 { background:#f85149; } .d2 { background:#d29922; } .d3 { background:#3fb950; }
  #term-title { margin-left:16px; font-family:'Consolas',monospace;
    font-size:22px; color:#8b949e; }
  #term-body { padding:34px 36px 30px;
    font-family:'Consolas','Courier New',monospace; }

  .track { display:flex; align-items:center; margin-bottom:26px; }
  .t-name { width:96px; font-size:24px; letter-spacing:.08em; }
  .t-name.voice { color:#58a6ff; }
  .t-name.music { color:#3fb950; }
  .t-wave { flex:1; padding:0 18px 0 8px; }
  .t-lufs { width:236px; text-align:right; font-size:26px; color:#e6edf3;
    white-space:nowrap; }
  .t-lufs .from { color:#8b949e; font-size:22px; }
  .t-lufs .arrow { color:#3fb950; margin:0 8px; }
  .t-lufs .to { color:#7ee787; }
  .t-lufs .unit { color:#8b949e; font-size:18px; margin-left:4px; }
  .t-lufs.voice .to { color:#e3b341; }

  #cmdline { margin-top:10px; padding-top:22px; border-top:2px solid #30363d;
    font-size:21px; color:#8b949e; line-height:1.6; }
  #cmdline .cmd { color:#7ee787; }
  #cmdline .opt { color:#58a6ff; }

  /* 金喇叭徽章：多轨窗右上外缘 */
  #badge { position:absolute; left:1628px; top:142px; width:146px; height:146px;
    border-radius:50%; background:#0d1117; border:5px solid #e3b341;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 10px 40px rgba(227,179,65,.35); z-index:2; }
  #badge svg { width:82px; height:82px; }

  /* ===== 底部 ===== */
  #dateline { position:absolute; left:120px; bottom:56px;
    font-family:'Consolas',monospace; font-size:24px; color:#8b949e;
    letter-spacing:.28em; }
  #epno { position:absolute; right:120px; bottom:48px;
    font-family:'Consolas',monospace; font-size:30px; color:#e3b341;
    letter-spacing:.2em; }
</style>
</head>
<body>
  <div id="bg-grid"></div>
  <div id="bg-glow"></div>

  <div id="left">
    <div id="tag">HYPERFRAMES 教程 · 第 6 集</div>
    <div id="title">给片子配上声音</div>
    <div id="sub">媒体进场 · 一把<span class="en">LUFS</span>响度尺</div>
    <div id="motto">响度不靠耳朵猜 ——<br><b>让机器量，不让耳朵扛</b></div>
    <div id="rule"></div>
  </div>

  <div id="badge">
    <svg viewBox="0 0 24 24" fill="none">
      <path d="M4 9.2v5.6h3.6L13 19.4V4.6L7.6 9.2H4z" fill="#e3b341"/>
      <path d="M16 8.8a4.6 4.6 0 0 1 0 6.4" stroke="#e3b341" stroke-width="2"
            stroke-linecap="round" fill="none"/>
      <path d="M18.4 6.2a8 8 0 0 1 0 11.6" stroke="#e3b341" stroke-width="2"
            stroke-linecap="round" fill="none" opacity=".75"/>
    </svg>
  </div>

  <div id="term">
    <div id="term-bar">
      <span class="dot d1"></span><span class="dot d2"></span><span class="dot d3"></span>
      <span id="term-title">media &mdash; hf06</span>
    </div>
    <div id="term-body">
      <div class="track">
        <span class="t-name voice">VOICE</span>
        <span class="t-wave">__VOICE__</span>
        <span class="t-lufs voice"><span class="to">&minus;21.8</span><span class="unit">LUFS</span></span>
      </div>
      <div class="track">
        <span class="t-name music">MUSIC</span>
        <span class="t-wave">__MUSIC__</span>
        <span class="t-lufs"><span class="from">&minus;37.3</span><span class="arrow">&#10142;</span><span class="to">&minus;21.8</span><span class="unit">LUFS</span></span>
      </div>
      <div id="cmdline">F:\\_hftest\\hf06-media&gt; <span class="cmd">hyperframes normalize-audio</span> <span class="opt">--reference voice --target bgm --write</span></div>
    </div>
  </div>

  <div id="dateline">MEDIA IN &middot; LUFS NORMALIZED &middot; exit 0 ONLY</div>
  <div id="epno">No.06</div>
</body>
</html>
"""

html = html.replace("__VOICE__", voice_wave).replace("__MUSIC__", music_wave)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
