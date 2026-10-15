# -*- coding: utf-8 -*-
r"""hf-05 录屏布景生成器：在公开沙盒（默认 F:\_hftest\hf05-check）生成

- proj/                 录屏主工程（portable NPP 编辑这里的 index.html）
- backup/s0-good …      各 take 的权威起点，restore 一键恢复

用法（在 videos/ 下）：
    python projects/hf-05/oneoffs/setup_scenes.py init      # 生成工程＋全部权威态
    python projects/hf-05/oneoffs/setup_scenes.py list      # 列状态
    python projects/hf-05/oneoffs/setup_scenes.py restore s3-contrast

所有 HTML 均在 build/probe 真机验证过（0.8.107，详见 REHEARSAL-NOTES.md）。
沙盒路径短且无用户名，满足公开画面脱敏要求。
"""
import argparse
import shutil
import sys
from pathlib import Path

DEFAULT_ROOT = r"F:\_hftest\hf05-check"

GSAP = Path(__file__).resolve().parents[1] / "gsap.min.js"

HYPERFRAMES_JSON = """{
  "registry": [],
  "paths": { "compositions": "." },
  "media": { "autoProxy": true }
}
"""

PACKAGE_JSON = """{
  "name": "hf05-check-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "check": "npx --yes hyperframes@0.8.107 check",
    "lint": "npx --yes hyperframes@0.8.107 lint",
    "render": "npx --yes hyperframes@0.8.107 render"
  }
}
"""

# 各权威态共用的片段。页面 1920x1080，主卡即教学样例本身。
HEAD = """<!doctype html>
<html lang="zh">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="gsap.min.js"></script>
    <style>
      html, body { margin: 0; background: #0d1117; }
      .card { position: absolute; width: 1200px; font-family: sans-serif; }
      #title { left: 360px; top: 380px; font-size: 88px; font-weight: 700;
               color: %TITLECOLOR%; }
      #sub { left: 360px; top: 540px; font-size: 44px; color: #8b949e; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0"
         data-duration="%ROOTDUR%" data-width="1920" data-height="1080">
%CLIPS%
    </div>
    <script>
%TIMELINE%
    </script>
  </body>
</html>
"""

CLIP_TITLE_GOOD = """      <div id="title" class="card clip" data-start="0" data-duration="10"
           data-track-index="1">check 门控：让机器先帮你挑错</div>
      <div id="sub" class="card clip" data-start="0.5" data-duration="9.5"
           data-track-index="1">写完先 check，再按渲染</div>"""

TIMELINE_GOOD = """      const tl = gsap.timeline({ paused: true });
      tl.fromTo('#title', { opacity: 0 }, { opacity: 1, duration: 1 });
      window.__timelines = window.__timelines || {};
      window.__timelines['main'] = tl;"""

# s5 选择器拼错：给副标题加动画时 #sub 拼成 #sut——该动画静默失踪
# （console_warning，不阻断）；title 动画照常，时间轴仍前进，sweep 不连坐
TIMELINE_NULL = """      const tl = gsap.timeline({ paused: true });
      tl.fromTo('#title', { opacity: 0 }, { opacity: 1, duration: 1 });
      tl.fromTo('#sut', { opacity: 0 }, { opacity: 1, duration: 1 });
      window.__timelines = window.__timelines || {};
      window.__timelines['main'] = tl;"""

# s1 删 title 的 data-duration（warning 不阻断）
CLIP_NO_DURATION = """      <div id="title" class="card clip" data-start="0"
           data-track-index="1">check 门控：让机器先帮你挑错</div>
      <div id="sub" class="card clip" data-start="0.5" data-duration="9.5"
           data-track-index="1">写完先 check，再按渲染</div>"""

# s2 越界：副卡 8s 起、5s 长，结束 13s > root 10s（warning＋双修复建议）
CLIP_OVERFLOW = CLIP_TITLE_GOOD + """
      <div id="tail" class="card clip" data-start="8" data-duration="5"
           data-track-index="2"
           style="color:#7ee787;font-size:40px;">片尾彩蛋，其实被切掉了</div>"""

# s4 同轨重叠：两 clip 同 track-index=1、时间重叠——全绿合法
CLIP_SAME_TRACK = """      <div id="title" class="card clip" data-start="0" data-duration="10"
           data-track-index="1">check 门控：让机器先帮你挑错</div>
      <div id="sub" class="card clip" data-start="3" data-duration="4"
           data-track-index="1" style="color:#7ee787;">同一根轨道，时间还重叠，报错吗？</div>"""

TIMELINE_STUB = """      window.__timelines = window.__timelines || {};
      window.__timelines['main'] = { seek: function (t) {} };"""


def page(clips, timeline, root_dur=10, title_color="#e6edf3"):
    return (HEAD.replace("%CLIPS%", clips)
                .replace("%TIMELINE%", timeline)
                .replace("%ROOTDUR%", str(root_dur))
                .replace("%TITLECOLOR%", title_color))


STATES = {
    # name: (说明, html)
    "s0-good": ("好工程基线：check 六段全绿",
                page(CLIP_TITLE_GOOD, TIMELINE_GOOD)),
    "s1-no-duration": ("缺 data-duration：Lint warning 但 Check passed",
                       page(CLIP_NO_DURATION, TIMELINE_GOOD)),
    "s2-overflow": ("clip 越界（8+5>10）：Lint warning＋双修复建议",
                    page(CLIP_OVERFLOW, TIMELINE_GOOD)),
    # 近底色：#1a1f26 on #0d1117，实测 1.14:1，5 采样点全 ✗ exit 1
    "s3-contrast": ("标题色近底色 1.14:1：Contrast error exit 1",
                    page(CLIP_TITLE_GOOD, TIMELINE_GOOD, title_color="#1a1f26")),
    "s4-same-track": ("同 track-index 重叠：全绿合法（层叠只看 DOM 顺序）",
                      page(CLIP_SAME_TRACK, TIMELINE_GOOD)),
    "s5-null-target": ("GSAP 选择器拼错 #titel：console_warning 不阻断",
                       page(CLIP_TITLE_GOOD, TIMELINE_NULL)),
}


def init(root: Path) -> None:
    proj = root / "proj"
    backup = root / "backup"
    proj.mkdir(parents=True, exist_ok=True)
    shutil.copy(GSAP, proj / "gsap.min.js")
    (proj / "hyperframes.json").write_text(HYPERFRAMES_JSON, encoding="utf-8")
    (proj / "package.json").write_text(PACKAGE_JSON, encoding="utf-8")
    for name, (desc, html) in STATES.items():
        d = backup / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(html, encoding="utf-8")
        shutil.copy(GSAP, d / "gsap.min.js")
        (d / "hyperframes.json").write_text(HYPERFRAMES_JSON, encoding="utf-8")
        (d / "desc.txt").write_text(desc, encoding="utf-8")
    restore(root, "s0-good")
    print("布景完成：%s" % root)
    print("录屏工程 %s；权威态 %d 个在 backup/" % (proj, len(STATES)))


def restore(root: Path, name: str) -> None:
    src = root / "backup" / name / "index.html"
    if not src.is_file():
        sys.exit("未知状态：%s（先 list）" % name)
    dst = root / "proj" / "index.html"
    shutil.copy(src, dst)
    print("已恢复 %s → %s" % (name, dst))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "list", "restore"])
    ap.add_argument("state", nargs="?", help="restore 用的状态名")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    args = ap.parse_args()
    root = Path(args.root)

    if args.cmd == "init":
        init(root)
    elif args.cmd == "list":
        for name, (desc, _) in STATES.items():
            print("%-18s %s" % (name, desc))
    else:
        if not args.state:
            sys.exit("restore 需要状态名（见 list）")
        restore(root, args.state)


if __name__ == "__main__":
    main()
