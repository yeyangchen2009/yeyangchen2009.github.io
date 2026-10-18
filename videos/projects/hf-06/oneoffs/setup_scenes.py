# -*- coding: utf-8 -*-
r"""hf-06 录屏布景生成器：在公开沙盒（默认 F:\_hftest\hf06-media）生成

- proj/                 录屏主工程（portable NPP 编辑这里的 index.html）
- proj/media/           五件素材（setup 用 ffmpeg 从仓库内母带/素材派生）
- backup/s0-good …      各 take 的权威起点，restore 一键恢复（只换 index.html，
                        media 五态共用一套：s4 只改引用名、s9 引用真实文件）

用法（在 videos/ 下）：
    python projects/hf-06/oneoffs/setup_scenes.py init      # 生成工程＋素材＋权威态
    python projects/hf-06/oneoffs/setup_scenes.py list
    python projects/hf-06/oneoffs/setup_scenes.py restore s5-sametrack

所有报错文案均在 build/hf06-probe 真机验证过（0.8.107，详见 MEDIA-FACTS.md）。
沙盒路径短且无用户名，满足公开画面脱敏要求。换行一律 LF（见下 newline 注）。
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = r"F:\_hftest\hf06-media"
P = Path(__file__).resolve().parents[1]          # projects/hf-06
P05 = P.parent / "hf-05"
GSAP = P / "gsap.min.js"
WAV_MASTER = P / "media" / "hf-06-yeyang.wav"
DEMO_SRC = P05 / "media" / "shorts" / "beats.mp4"
PIC_SRC = P05 / "media" / "freezes" / "check-good.png"

HYPERFRAMES_JSON = """{
  "registry": [],
  "paths": { "compositions": "." },
  "media": { "autoProxy": true }
}
"""

PACKAGE_JSON = """{
  "name": "hf06-media-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "check": "npx --yes hyperframes@0.8.107 check",
    "lint": "npx --yes hyperframes@0.8.107 lint"
  }
}
"""

HEAD = """<!doctype html>
<html lang="zh">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="gsap.min.js"></script>
    <style>
      html, body { margin: 0; background: #0d1117; }
      #title { position: absolute; left: 120px; top: 70px; width: 1680px;
               font-size: 76px; font-weight: 700; color: #e6edf3;
               font-family: sans-serif; }
      #sub { position: absolute; left: 120px; top: 900px; width: 1680px;
             font-size: 40px; color: #8b949e; font-family: sans-serif; }
      #demo, #pic { position: absolute; left: 360px; top: 280px;
                    width: 1200px; height: 560px; object-fit: contain;
                    background: #161b22; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0"
         data-duration="12" data-width="1920" data-height="1080">
%CLIPS%
    </div>
    <script>
      const tl = gsap.timeline({ paused: true });
      tl.fromTo('#title', { opacity: 0 }, { opacity: 1, duration: 1 });
      window.__timelines = window.__timelines || {};
      window.__timelines['main'] = tl;
    </script>
  </body>
</html>
"""

# s0 好基线：video 有 id＋muted；img 有 id；voice track3、bgm track4 不重叠音轨。
# 三个现场编辑锚点（NPP 操作目标，check_anchors 校验唯一）：
#   ' id="demo"' 删 → media_missing_id (FROZEN)
#   ' muted'      删 → video_missing_muted
#   'media/voice.wav' → voise.wav → audio_src_not_found
CLIPS_GOOD = """      <div id="title" class="clip" data-start="0" data-duration="12"
           data-track-index="2">hf-06 媒体进场演示</div>
      <video id="demo" class="clip" data-start="0" data-duration="4"
           data-track-index="0" src="media/demo.mp4" muted playsinline></video>
      <img id="pic" class="clip" data-start="4" data-duration="4"
           data-track-index="0" src="media/pic.png" alt="">
      <audio id="voice" class="clip" data-start="0" data-duration="6"
           data-track-index="3" src="media/voice.wav" data-volume="1"></audio>
      <audio id="bgm" class="clip" data-start="0" data-duration="6"
           data-track-index="4" src="media/music.wav" data-volume="0.4"
           data-timeline-role="music"></audio>
      <div id="sub" class="clip" data-start="0" data-duration="12"
           data-track-index="2">voice 轨 3 &middot; bgm 轨 4 &middot; demo 已静音</div>"""

# s4：引用名指向不存在文件（missing_local_asset ×2，silently skip）
CLIPS_MISSING = CLIPS_GOOD.replace('media/demo.mp4', 'media/gone.mp4') \
                          .replace('media/pic.png', 'media/gone.png')

# s5：bgm 挪到 track 3 且与 voice 同段重叠（duplicate_audio_track warning）
CLIPS_SAMETRACK = CLIPS_GOOD.replace(
    '<audio id="bgm" class="clip" data-start="0" data-duration="6"\n'
    '           data-track-index="4"',
    '<audio id="bgm" class="clip" data-start="0" data-duration="6"\n'
    '           data-track-index="3"')

# s8：voice src 占位 URL（placeholder_media_url，will 404）
CLIPS_PLACEHOLDER = CLIPS_GOOD.replace(
    'src="media/voice.wav"',
    'src="https://example.com/voice.wav"')

# s9：bgm 换 0.15 倍压音乐＋增益 0.15（校准后 normalize 需 16.0dB，撞天花板）
CLIPS_CEILING = CLIPS_GOOD.replace(
    'src="media/music.wav" data-volume="0.4"',
    'src="media/music15.wav" data-volume="0.15"')

STATES = {
    "s0-good": ("好工程基线：check 0 error 0 warning", CLIPS_GOOD),
    "s4-missing": ("video/img 文件缺失：missing_local_asset silently skip",
                   CLIPS_MISSING),
    "s5-sametrack": ("voice/bgm 同 track 3 重叠：duplicate_audio_track warning",
                     CLIPS_SAMETRACK),
    "s8-placeholder": ("占位 URL：placeholder_media_url will 404",
                       CLIPS_PLACEHOLDER),
    "s9-ceiling": ("bgm 差 16.0dB：normalize 拒超 +12dB 天花板",
                   CLIPS_CEILING),
}

# NPP 现场编辑锚点（必须在 s0 中唯一）
EDIT_ANCHORS = [' id="demo"', " muted", "media/voice.wav"]


def make_media(media: Path) -> None:
    media.mkdir(parents=True, exist_ok=True)
    # 注意：这里只做「直切」，LUFS 自然值随蝉镜母带重合成微漂（voice 头 6s
    # 三版母带实测 -21.5/-21.8/-21.4）。口播念的定值由 calibrate_media.py 在
    # init 之后整体平移锚定：voice -21.8 LUFS、music15 needs 16.0 dB（校准台账
    # build/media-calibration.json；music -37.26／gain 7.5／写回 2.371374 是
    # v3 母带校准后实测，LUFS 差不随整体平移变化）。
    jobs = [
        # voice：母带头 6s
        (["ffmpeg", "-y", "-loglevel", "error", "-i", str(WAV_MASTER),
          "-t", "6", str(media / "voice.wav")]),
        # music：母带 60s 处取 6s 压到 0.4（校准后 -37.26 LUFS，差 voice 7.5dB）
        (["ffmpeg", "-y", "-loglevel", "error", "-ss", "60", "-i",
          str(WAV_MASTER), "-t", "6", "-af", "volume=0.4",
          str(media / "music.wav")]),
        # music15：同段压 0.15（校准后 needs 16.0dB，撞 +12dB 天花板 exit1）
        (["ffmpeg", "-y", "-loglevel", "error", "-ss", "60", "-i",
          str(WAV_MASTER), "-t", "6", "-af", "volume=0.15",
          str(media / "music15.wav")]),
    ]
    for cmd in jobs:
        subprocess.run(cmd, check=True)
    shutil.copy(DEMO_SRC, media / "demo.mp4")
    shutil.copy(PIC_SRC, media / "pic.png")
    print("素材 5 件 → %s" % media)


def page(clips: str) -> str:
    return HEAD.replace("%CLIPS%", clips)


def init(root: Path) -> None:
    if not WAV_MASTER.is_file():
        sys.exit("缺母带：%s（先跑 TTS）" % WAV_MASTER)
    if not GSAP.is_file():
        shutil.copy(P05 / "gsap.min.js", GSAP)
    proj = root / "proj"
    backup = root / "backup"
    (proj / "media").mkdir(parents=True, exist_ok=True)
    make_media(proj / "media")
    shutil.copy(GSAP, proj / "gsap.min.js")
    # newline="\n" 必须显式：CRLF 会让 NPP 字节锚点全偏（hf-05 坑 6）。
    (proj / "hyperframes.json").write_text(
        HYPERFRAMES_JSON, encoding="utf-8", newline="\n")
    (proj / "package.json").write_text(
        PACKAGE_JSON, encoding="utf-8", newline="\n")
    for name, (desc, clips) in STATES.items():
        d = backup / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(
            page(clips), encoding="utf-8", newline="\n")
        shutil.copy(GSAP, d / "gsap.min.js")
        (d / "hyperframes.json").write_text(
            HYPERFRAMES_JSON, encoding="utf-8", newline="\n")
        (d / "desc.txt").write_text(desc, encoding="utf-8", newline="\n")
    restore(root, "s0-good")
    print("布景完成：%s（权威态 %d 个在 backup/）" % (root, len(STATES)))


def restore(root: Path, name: str) -> None:
    src = root / "backup" / name / "index.html"
    if not src.is_file():
        sys.exit("未知状态：%s（先 list）" % name)
    shutil.copy(src, root / "proj" / "index.html")
    print("已恢复 %s → proj/index.html" % name)


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
            print("%-16s %s" % (name, desc))
        print("现场编辑态（不备份）：删 id / 删 muted / voice→voise")
    else:
        if not args.state:
            sys.exit("restore 需要状态名（见 list）")
        restore(root, args.state)


if __name__ == "__main__":
    main()
