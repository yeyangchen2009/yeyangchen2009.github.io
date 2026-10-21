# -*- coding: utf-8 -*-
"""hf-08 · 封面生成器（暗色工作室金/蓝，与 hf-05/06/07 同视觉系）。

本集主题是「render 的确定性」：右窗＝sha256 校验终端——同一份 13 秒
工程烤六次（软件 GPU ×2、硬件 GPU ×2、单 worker、六天前旧档），六个
文件同为 61,145 B、同一个指纹。hash 用缩写口径（前 8 … 后 7），与
oneoffs/PROBE-NOTES.md 台账完全一致（2057d037…c6c5a83），不杜撰全长。
窗底一行 render 命令。圆徽章＝烤炉（炉身＋胶片条＋三簇火苗）：
render＝把网页烤成 MP4。封面是设计资产（概念插画，同 hf-06 波形柱、
hf-07 胶片条），真机 sha256 六连在正片与台账。

截图：
  chrome-headless-shell --screenshot=snapshots/cover-final.png \\
      --window-size=1920,1080 --hide-scrollbars \\
      --virtual-time-budget=5000 file:///<绝对路径>/cover.html
用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

HASH = "2057d037…c6c5a83"
SIZE = "61,145 B"

ROWS = [
    ("soft-a.mp4",   "软件 GPU"),
    ("soft-b.mp4",   "软件 GPU"),
    ("hw-a.mp4",     "硬件 GPU"),
    ("hw-b.mp4",     "硬件 GPU"),
    ("w1.mp4",       "单 worker"),
    ("1015-old.mp4", "六天前旧档"),
]


def row(name, note):
    return f"""      <div class="row">
        <span class="name">{name}</span>
        <span class="size">{SIZE}</span>
        <span class="hash">{HASH}</span>
        <span class="tick">✓</span>
      </div>
      <!-- {note} -->
"""


rows = "".join(row(n, t) for n, t in ROWS)

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>hf-08 封面</title>
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
  #tag { position:absolute; top:208px; font-size:28px; color:#58a6ff;
    letter-spacing:.3em; font-family:'Consolas',monospace; white-space:nowrap; }
  #title { position:absolute; top:286px; font-size:100px; line-height:1.18;
    color:#e3b341; letter-spacing:.06em; white-space:nowrap; }
  #title .mono { font-family:'Consolas',monospace; font-size:.92em; }
  #sub { position:absolute; top:540px; font-size:44px; color:#e6edf3;
    letter-spacing:.05em; white-space:nowrap; }
  #sub .en { color:#58a6ff; font-family:'Consolas',monospace; font-size:.9em; }
  #sub .dim { color:#8b949e; }
  #motto { position:absolute; top:648px; font-size:40px; color:#8b949e;
    line-height:1.7; }
  #motto b { color:#e3b341; font-weight:normal; }
  #rule { position:absolute; top:820px; width:120px; height:6px;
    background:#e3b341; border-radius:3px; }

  /* ===== 右侧 sha256 终端窗 ===== */
  #term { position:absolute; left:990px; top:190px; width:820px;
    background:#161b22; border:2px solid #30363d; border-radius:18px;
    box-shadow:0 30px 90px rgba(0,0,0,.6); overflow:hidden; }
  #term-bar { height:64px; background:#0d1521; border-bottom:2px solid #30363d;
    display:flex; align-items:center; padding:0 26px; }
  .dot { width:15px; height:15px; border-radius:50%; margin-right:12px; }
  .d1 { background:#f85149; } .d2 { background:#d29922; } .d3 { background:#3fb950; }
  #term-title { margin-left:16px; font-family:'Consolas',monospace;
    font-size:22px; color:#8b949e; }
  #term-body { padding:30px 32px 26px;
    font-family:'Consolas','Courier New',monospace; }

  #table { font-size:21px; }
  .hrow, .row { display:grid;
    grid-template-columns:182px 118px 1fr 44px; align-items:center; }
  .hrow { height:34px; font-size:15px; color:#484f58; letter-spacing:.18em; }
  .row { height:42px; }
  .row .name { color:#7ee787; }
  .row .size { color:#8b949e; }
  .row .hash { color:#e3b341; letter-spacing:.02em;
    text-shadow:0 0 14px rgba(227,179,65,.25); }
  .row .tick { color:#3fb950; font-size:24px; }
  .row:nth-child(odd) { background:rgba(255,255,255,.018); border-radius:6px; }

  #legend { margin-top:20px; font-size:17px; color:#8b949e; line-height:1.7; }
  #legend .cond { color:#c9d1d9; }
  #legend .verdict { color:#7ee787; font-family:'Consolas',monospace;
    font-size:18px; }

  #cmdline { margin-top:18px; padding-top:18px; border-top:2px solid #30363d;
    font-size:21px; color:#8b949e; line-height:1.6; }
  #cmdline .cmd { color:#7ee787; }
  #cmdline .opt { color:#58a6ff; }

  /* 烤炉徽章：终端窗右上外缘 */
  #badge { position:absolute; left:1638px; top:142px; width:146px; height:146px;
    border-radius:50%; background:#0d1117; border:5px solid #e3b341;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 10px 40px rgba(227,179,65,.35); z-index:2; }
  #badge svg { width:86px; height:86px; }

  /* ===== 底部 ===== */
  #dateline { position:absolute; left:120px; bottom:56px;
    font-family:'Consolas',monospace; font-size:24px; color:#8b949e;
    letter-spacing:.24em; }
  #epblock { position:absolute; right:120px; bottom:44px; text-align:right; }
  #epno { font-family:'Consolas',monospace; font-size:30px; color:#e3b341;
    letter-spacing:.2em; }
  #finale { margin-top:4px; font-family:'Consolas',monospace; font-size:15px;
    color:#8b949e; letter-spacing:.34em; }
</style>
</head>
<body>
  <div id="bg-grid"></div>
  <div id="bg-glow"></div>

  <div id="left">
    <div id="tag">HYPERFRAMES 教程 · 第 8 集 · 第一季终</div>
    <div id="title">把网页烤成 <span class="mono">MP4</span></div>
    <div id="sub"><span class="en">render</span> 不是录屏 <span class="dim">·</span> 三百九十格独立求解</div>
    <div id="motto">同一份工程烤六次 ——<br><b>六个指纹，同一个文件</b></div>
    <div id="rule"></div>
  </div>

  <div id="badge">
    <svg viewBox="0 0 24 24" fill="none">
      <!-- 炉顶胶片条 -->
      <rect x="5" y="3.6" width="14" height="2.6" rx="0.8"
            stroke="#e3b341" stroke-width="1.4"/>
      <rect x="7.2" y="4.35" width="1.1" height="1.1" fill="#e3b341"/>
      <rect x="10.9" y="4.35" width="1.1" height="1.1" fill="#e3b341"/>
      <rect x="14.6" y="4.35" width="1.1" height="1.1" fill="#e3b341"/>
      <!-- 炉身 -->
      <rect x="3.5" y="8" width="17" height="12.6" rx="2.2"
            stroke="#e3b341" stroke-width="1.7"/>
      <!-- 火箱口 -->
      <rect x="7" y="12.4" width="10" height="6.2" rx="1"
            stroke="#e3b341" stroke-width="1.3"/>
      <!-- 三簇火苗 -->
      <path d="M12 18.1 C10.5 16.9 10.7 14.9 12 13.4 C13.3 14.9 13.5 16.9 12 18.1 Z"
            fill="#e3b341"/>
      <path d="M8.9 18.1 C8 17.4 8.1 16 8.9 14.9 C9.7 16 9.8 17.4 8.9 18.1 Z"
            fill="#e3b341"/>
      <path d="M15.1 18.1 C14.2 17.4 14.3 16 15.1 14.9 C15.9 16 16 17.4 15.1 18.1 Z"
            fill="#e3b341"/>
      <!-- 炉脚 -->
      <path d="M6.6 20.6 v1.5 M17.4 20.6 v1.5" stroke="#e3b341"
            stroke-width="1.4" stroke-linecap="round"/>
    </svg>
  </div>

  <div id="term">
    <div id="term-bar">
      <span class="dot d1"></span><span class="dot d2"></span><span class="dot d3"></span>
      <span id="term-title">sha256-identical &mdash; hf08-probe</span>
    </div>
    <div id="term-body">
      <div id="table">
        <div class="hrow">
          <span>NAME</span><span>SIZE</span><span>SHA-256</span><span></span>
        </div>
__ROWS__
      </div>
      <div id="legend">
        <div class="cond">软件 GPU ×2　·　硬件 GPU ×2　·　单 worker　·　六天前旧档</div>
        <div class="verdict">6 runs &middot; same input &middot; byte-identical output</div>
      </div>
      <div id="cmdline">F:\\_hftest\\hf08-probe&gt; <span class="cmd">hyperframes render</span> . <span class="opt">--browser-gpu</span></div>
    </div>
  </div>

  <div id="dateline">SEEK &middot; CAPTURE &middot; ENCODE &middot; BYTE-IDENTICAL RENDER</div>
  <div id="epblock">
    <div id="epno">No.08</div>
    <div id="finale">SEASON 1 FINALE</div>
  </div>
</body>
</html>
"""

html = html.replace("__ROWS__", rows)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
