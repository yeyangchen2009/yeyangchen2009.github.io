# -*- coding: utf-8 -*-
"""hf-07 · 封面生成器（暗色工作室金/蓝，与 hf-05/06 同视觉系）。

本集主题是「逐帧验收」：右窗＝本集灵魂镜头的概念化复刻——同一秒连拍
四张（snapshot --at 2,2,2,2）的胶片条：蓝块（GSAP seekable）四帧纹丝
不动，红块（CSS 墙钟动画）四帧四个位置，每帧角标 t=2.00s。位置比例取
探针真机 E3（蓝在 25%，红 ≈ 6%/21%/27%/13%，见 oneoffs/PROBE-NOTES）。
窗底一行 snapshot 命令。圆徽章＝相机快门（snapshot＝拍照）。
封面是设计资产（概念插画，同 hf-06 波形柱），真机取证在正片。

截图：
  chrome-headless-shell --screenshot=snapshots/cover-final.png \
      --window-size=1920,1080 --hide-scrollbars \
      --virtual-time-budget=5000 file:///<绝对路径>/cover.html
用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# E3 真机比例（0–1）：蓝＝t=2s 时 200/800=0.25，四帧一致；
# 红＝translateX 50/170/215/105 相对 800 轨迹。
BLUE_X = 0.25
RED_X = (50, 170, 215, 105)

FW, FH = 168, 100          # 迷你帧尺寸
BOX = 15                   # 方块边长
BLUE_Y, RED_Y = 18, 60


def frame(i):
    rx = round(RED_X[i] / 800 * (FW - BOX), 1)
    bx = round(BLUE_X * (FW - BOX), 1)
    return f"""
    <div class="frame">
      <span class="tcode">t=2.00s</span>
      <span class="box blue" style="left:{bx}px;top:{BLUE_Y}px"></span>
      <span class="box red" style="left:{rx}px;top:{RED_Y}px"></span>
      <span class="fno">#{i+1}</span>
    </div>"""


frames = "".join(frame(i) for i in range(4))

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>hf-07 封面</title>
<link rel="stylesheet" href="../../assets/wenkai/lxgwwenkai-bold.css">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:1920px; height:1080px; overflow:hidden; }
  body { background:#0d1117; color:#e6edf3;
    font-family:'LXGW WenKai Bold','LXGW WenKai','Microsoft YaHei',sans-serif;
    position:relative; }
  #bg-grid { position:absolute; inset:0;
    background-image:
      linear-gradient(rgba(88,166,255,.055) 1px, transparent 1px),
      linear-gradient(90deg, rgba(88,166,255,.055) 1px, transparent 1px);
    background-size:80px 80px; }
  #bg-glow { position:absolute; inset:0;
    background:
      radial-gradient(720px 500px at 12% 18%, rgba(227,179,65,.12), transparent 70%),
      radial-gradient(880px 600px at 88% 86%, rgba(31,111,235,.13), transparent 70%); }

  /* ===== 左侧主张 ===== */
  #left { position:absolute; left:120px; top:0; width:920px; height:1080px; }
  #tag { position:absolute; top:208px; font-size:30px; color:#58a6ff;
    letter-spacing:.32em; font-family:'Consolas',monospace; }
  #title { position:absolute; top:280px; font-size:104px; line-height:1.18;
    color:#e3b341; letter-spacing:.06em; white-space:nowrap; }
  #sub { position:absolute; top:540px; font-size:46px; color:#e6edf3;
    letter-spacing:.05em; }
  #sub .en { color:#58a6ff; font-family:'Consolas',monospace; font-size:.86em; }
  #sub .en2 { color:#7ee787; font-family:'Consolas',monospace; font-size:.86em; }
  #motto { position:absolute; top:648px; font-size:40px; color:#8b949e;
    line-height:1.7; }
  #motto b { color:#e3b341; font-weight:normal; }
  #rule { position:absolute; top:812px; width:120px; height:6px;
    background:#e3b341; border-radius:3px; }

  /* ===== 右侧接触表窗 ===== */
  #term { position:absolute; left:990px; top:190px; width:820px;
    background:#161b22; border:2px solid #30363d; border-radius:18px;
    box-shadow:0 30px 90px rgba(0,0,0,.6); overflow:hidden; }
  #term-bar { height:64px; background:#0d1521; border-bottom:2px solid #30363d;
    display:flex; align-items:center; padding:0 26px; }
  .dot { width:15px; height:15px; border-radius:50%; margin-right:12px; }
  .d1 { background:#f85149; } .d2 { background:#d29922; } .d3 { background:#3fb950; }
  #term-title { margin-left:16px; font-family:'Consolas',monospace;
    font-size:22px; color:#8b949e; }
  #term-body { padding:34px 30px 28px;
    font-family:'Consolas','Courier New',monospace; }

  #filmstrip { display:flex; gap:14px; }
  .frame { position:relative; width:__FW__px; height:__FH__px;
    background:#0d1117; border:2px solid #30363d; border-radius:8px;
    flex:0 0 auto; }
  .tcode { position:absolute; left:8px; top:6px; font-size:13px; color:#8b949e; }
  .fno { position:absolute; right:8px; bottom:4px; font-size:13px; color:#484f58; }
  .box { position:absolute; width:__BOX__px; height:__BOX__px;
    border-radius:3px; }
  .box.blue { background:#1f6feb; box-shadow:0 0 12px rgba(31,111,235,.55); }
  .box.red { background:#da3633; box-shadow:0 0 12px rgba(218,54,51,.55); }

  #legend { display:flex; gap:34px; margin-top:22px; font-size:19px;
    color:#8b949e; }
  #legend .sw { display:inline-block; width:14px; height:14px; border-radius:3px;
    margin-right:9px; vertical-align:-1px; }
  #legend .same { color:#58a6ff; } #legend .drift { color:#f85149; }

  #cmdline { margin-top:20px; padding-top:20px; border-top:2px solid #30363d;
    font-size:21px; color:#8b949e; line-height:1.6; }
  #cmdline .cmd { color:#7ee787; }
  #cmdline .opt { color:#58a6ff; }

  /* 相机徽章：接触表窗右上外缘 */
  #badge { position:absolute; left:1638px; top:142px; width:146px; height:146px;
    border-radius:50%; background:#0d1117; border:5px solid #e3b341;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 10px 40px rgba(227,179,65,.35); z-index:2; }
  #badge svg { width:84px; height:84px; }

  /* ===== 底部 ===== */
  #dateline { position:absolute; left:120px; bottom:56px;
    font-family:'Consolas',monospace; font-size:24px; color:#8b949e;
    letter-spacing:.24em; }
  #epno { position:absolute; right:120px; bottom:48px;
    font-family:'Consolas',monospace; font-size:30px; color:#e3b341;
    letter-spacing:.2em; }
</style>
</head>
<body>
  <div id="bg-grid"></div>
  <div id="bg-glow"></div>

  <div id="left">
    <div id="tag">HYPERFRAMES 教程 · 第 7 集</div>
    <div id="title">把每一帧看清楚</div>
    <div id="sub"><span class="en">preview</span> 管感受 · <span class="en2">snapshot</span> 管事实</div>
    <div id="motto">同一秒连拍四张 ——<br><b>眼睛会骗人，帧不会</b></div>
    <div id="rule"></div>
  </div>

  <div id="badge">
    <svg viewBox="0 0 24 24" fill="none">
      <rect x="2.5" y="7" width="19" height="13" rx="2.4" stroke="#e3b341" stroke-width="2"/>
      <circle cx="12" cy="13.5" r="4" stroke="#e3b341" stroke-width="2"/>
      <path d="M8 7l1.3-2.4h5.4L16 7" stroke="#e3b341" stroke-width="2"
            stroke-linejoin="round" fill="none"/>
      <circle cx="12" cy="13.5" r="1.1" fill="#e3b341"/>
    </svg>
  </div>

  <div id="term">
    <div id="term-bar">
      <span class="dot d1"></span><span class="dot d2"></span><span class="dot d3"></span>
      <span id="term-title">contact-sheet.jpg &mdash; hf07</span>
    </div>
    <div id="term-body">
      <div id="filmstrip">__FRAMES__</div>
      <div id="legend">
        <span class="same"><span class="sw" style="background:#1f6feb"></span>GSAP seekable · 四帧同位</span>
        <span class="drift"><span class="sw" style="background:#da3633"></span>CSS 墙钟 · 四帧四位置</span>
      </div>
      <div id="cmdline">F:\\_hftest\\hf07-probe&gt; <span class="cmd">hyperframes snapshot</span> v1 <span class="opt">--at 2,2,2,2</span></div>
    </div>
  </div>

  <div id="dateline">PREVIEW FOR FEELING &middot; SNAPSHOT FOR FACT &middot; SEEKABLE ONLY</div>
  <div id="epno">No.07</div>
</body>
</html>
"""

html = (html.replace("__FRAMES__", frames)
            .replace("__FW__", str(FW)).replace("__FH__", str(FH))
            .replace("__BOX__", str(BOX)))

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
