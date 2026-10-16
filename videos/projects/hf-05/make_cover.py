# -*- coding: utf-8 -*-
"""hf-05 · 封面生成器（暗色终端绿，录前决策定稿）。

与 hf-01/02/03/04 的宣纸毛笔封面不同：本集主题是终端里的 check 门控，
封面直接用片内 GitHub Dark 视觉——#0d1117 底＋金色细网格，右侧终端窗
六行关全绿＋◇ Check passed 与大绿勾徽章，左側金/白主张。截图：
  chrome-headless-shell --screenshot=snapshots/cover-final.png \
      --window-size=1920,1080 --hide-scrollbars \
      --virtual-time-budget=5000 file:///<绝对路径>/cover.html
用法：python make_cover.py [输出html路径]
"""
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# 终端窗六行（文案与片内右卡/真机一致）
GATES = [
    ("Lint", "0 errors"),
    ("Runtime", "0 errors, 0 warnings"),
    ("Layout", "0 issues across 9 sample(s)"),
    ("Motion", "0 errors, 0 warnings"),
    ("Contrast", "64/64 text checks pass WCAG AA"),
    ("Snapshots", "disabled"),
]
gate_rows = "\n".join(
    '      <div class="gate-row"><span class="g-name">%s</span>'
    '<span class="g-state">&#9671; %s</span></div>' % (n, s)
    for n, s in GATES)

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>hf-05 封面</title>
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
      radial-gradient(720px 500px at 12% 18%, rgba(31,111,235,.16), transparent 70%),
      radial-gradient(840px 580px at 88% 88%, rgba(63,185,80,.10), transparent 70%); }

  /* ===== 左侧主张 ===== */
  #left { position:absolute; left:120px; top:0; width:880px; height:1080px; }
  #tag { position:absolute; top:208px; font-size:30px; color:#58a6ff;
    letter-spacing:.32em; font-family:'Consolas',monospace; }
  #title { position:absolute; top:268px; font-size:148px; line-height:1.18;
    color:#e3b341; letter-spacing:.06em; }
  #title .check { color:#7ee787; font-family:'Consolas',monospace;
    font-size:.62em; letter-spacing:0; vertical-align:.12em; }
  #sub { position:absolute; top:548px; font-size:50px; color:#e6edf3;
    letter-spacing:.06em; }
  #sub .en { color:#7ee787; font-family:'Consolas',monospace; }
  #motto { position:absolute; top:660px; font-size:38px; color:#8b949e;
    line-height:1.7; }
  #motto b { color:#e3b341; font-weight:normal; }
  #rule { position:absolute; top:800px; width:120px; height:6px;
    background:#3fb950; border-radius:3px; }

  /* ===== 右侧终端窗 ===== */
  #term { position:absolute; left:1030px; top:210px; width:770px;
    background:#161b22; border:2px solid #30363d; border-radius:18px;
    box-shadow:0 30px 90px rgba(0,0,0,.6); overflow:hidden; }
  #term-bar { height:64px; background:#0d1521; border-bottom:2px solid #30363d;
    display:flex; align-items:center; padding:0 26px; }
  .dot { width:15px; height:15px; border-radius:50%; margin-right:12px; }
  .d1 { background:#f85149; } .d2 { background:#d29922; } .d3 { background:#3fb950; }
  #term-title { margin-left:16px; font-family:'Consolas',monospace;
    font-size:22px; color:#8b949e; }
  #term-body { padding:30px 34px 34px;
    font-family:'Consolas','Courier New',monospace; }
  #cmdline { font-size:23px; color:#8b949e; line-height:1.6; margin-bottom:18px; }
  #cmdline .cmd { color:#7ee787; }
  #checking { font-size:25px; color:#e6edf3; margin-bottom:14px; }
  #checking .diamond { color:#58a6ff; }
  .gate-row { display:flex; align-items:baseline; font-size:24px;
    line-height:1.92; }
  .g-name { width:150px; color:#e6edf3; }
  .g-state { color:#7ee787; font-size:22px; }
  #pass { margin-top:22px; padding-top:20px; border-top:2px solid #30363d;
    font-size:36px; color:#3fb950; font-weight:bold; letter-spacing:.04em; }

  /* 大绿勾徽章：终端窗右上外缘（认证戳，不遮标题栏圆点） */
  #badge { position:absolute; left:1616px; top:160px; width:150px; height:150px;
    border-radius:50%; background:#0d1117; border:5px solid #3fb950;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 10px 40px rgba(63,185,80,.35); z-index:2; }
  #badge svg { width:84px; height:84px; }

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
    <div id="tag">HYPERFRAMES 教程 · 第 5 集</div>
    <div id="title">别用眼睛看</div>
    <div id="sub"><span class="en">check</span> 门控实操</div>
    <div id="motto">让机器先看 ——<br><b>错留在本地，别留到发出去以后</b></div>
    <div id="rule"></div>
  </div>

  <div id="badge">
    <svg viewBox="0 0 52 52" fill="none">
      <path d="M10 27 L22 39 L43 15" stroke="#3fb950" stroke-width="7"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </div>

  <div id="term">
    <div id="term-bar">
      <span class="dot d1"></span><span class="dot d2"></span><span class="dot d3"></span>
      <span id="term-title">cmd &mdash; hf05-check</span>
    </div>
    <div id="term-body">
      <div id="cmdline">F:\\_hftest\\hf05-check\\proj&gt;</div>
      <div id="cmdline" style="margin-top:-6px"><span class="cmd">npx hyperframes@0.8.107 check</span></div>
      <div id="checking"><span class="diamond">&#9670;</span>&nbsp; Checking hf-05</div>
__GATES__
      <div id="pass">&#9671;&nbsp; Check passed</div>
    </div>
  </div>

  <div id="dateline">MACHINE-FIRST REVIEW &middot; exit 0 ONLY</div>
  <div id="epno">No.05</div>
</body>
</html>
"""

html = html.replace("__GATES__", gate_rows)

out = Path(sys.argv[1]) if len(sys.argv) > 1 else (HERE / "cover.html")
io.open(out, "w", encoding="utf-8").write(html)
print("已生成封面：%s（%d 字符）" % (out, len(html)))
