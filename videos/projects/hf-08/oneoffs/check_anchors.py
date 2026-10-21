# -*- coding: utf-8 -*-
r"""hf-08 录前静态自检：布景镜像/逐字锚点/拍摄对象，秒级、不渲染不联网。

正式开拍前最后一道闸，退出码非 0 不许开录。覆盖：

- 沙盒 F:\_hftest\hf08-media 六 mp4（sha256 全等 2057…c6c5a83）、
  captured-frames 390 JPG、seq 390 PNG＋m4a、11 份日志、stage-manifest；
- 日志逐字锚点（gate 两行／尾报 1m8.1/52.4/41m43.3／45000ms 警告／
  Aborting／audio_processing_failed）；
- npx 缓存 0.8.107 两 chunk 的源码锚点（黑条注释、24576 地板、
  computeWorkerSizing 四笔账）——src-blackbar freeze 拍的就是它；
- 坏工程静态属性（rAF／无 __timelines／nope.wav）；
- 录屏依赖可执行（wt/npx/ffmpeg/powershell）＋工程真名路径在位。

  python oneoffs/check_anchors.py
"""
import hashlib
import io
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import setup_scenes as S  # noqa: E402

ROOT = Path(S.DEFAULT_ROOT)
fails = []


def must(cond, msg):
    if cond:
        print("PASS", msg)
    else:
        fails.append(msg)
        print("FAIL", msg)


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


# ---------- 1. 布景总览 ----------
print("== 布景目录 ==")
must((ROOT / "stage-manifest.json").is_file(), "stage-manifest.json 在")
for d in ("hashes", "bad-lint", "missing-media", "seq", "logs",
          "debug", "debug-output"):
    must((ROOT / d).is_dir(), "%s/ 在" % d)

print("== 六权威 mp4 ==")
for _, name in S.COPY_VIDEOS:
    f = ROOT / "hashes" / (name + ".mp4")
    must(f.is_file() and f.stat().st_size == 61145 and sha(f) == S.HASH_SHA256,
         "%s.mp4 61145B sha 全同" % name)

print("== 帧序列计数/编号 ==")
jpgs = sorted((ROOT / "debug" / "captured-frames").glob("frame_*.jpg"))
must(len(jpgs) == 390 and jpgs[0].name == "frame_000000.jpg"
     and jpgs[-1].name == "frame_000389.jpg",
     "captured-frames 390 JPG 000000–000389（实测 %d）" % len(jpgs))
pngs = sorted((ROOT / "seq").glob("frame_*.png"))
must(len(pngs) == 390 and pngs[0].name == "frame_000001.png"
     and pngs[-1].name == "frame_000390.png"
     and (ROOT / "seq" / "audio.m4a").is_file(),
     "seq 390 PNG 000001–000390＋audio.m4a（实测 %d）" % len(pngs))
debug_mp4 = ROOT / "debug" / "output.mp4"
must(debug_mp4.is_file() and sha(debug_mp4) == S.HASH_SHA256,
     "debug/output.mp4 同 hash（内容寻址证据）")

print("== 11 份日志 ==")
expect_logs = ["run-a.log", "run-b.log", "w1.log", "hw-a.log", "hw-b.log",
               "bad-lint-default.log", "bad-lint-strict.log",
               "mm-be.log", "mm-strict.log", "dbg.log", "seq.log"]
for lg in expect_logs:
    must((ROOT / "logs" / lg).is_file(), "logs/%s" % lg)

# ---------- 2. 逐字锚点 ----------
print("== 日志逐字锚点 ==")
ra = read(ROOT / "logs" / "run-a.log")
hw = read(ROOT / "logs" / "hw-a.log")
bd = read(ROOT / "logs" / "bad-lint-default.log")
bs = read(ROOT / "logs" / "bad-lint-strict.log")
mb = read(ROOT / "logs" / "mm-be.log")

must('"enabled":false,"reason":"multi_worker"' in ra
     and '"workerCount":3' in ra and '"maxDurationSeconds":240' in ra,
     "run-a：gate multi_worker/workerCount3/240s 单行")
must("rendered in 1m 8.1s" in ra and "setup 16.4s" in ra
     and "capture 33.6s" in ra and "encode 14.2s" in ra,
     "run-a：冷态尾报 1m8.1＋setup16.4＋capture33.6＋encode14.2")
must('"enabled":true,"reason":"single_worker"' in hw
     and '"workerCount":1' in hw,
     "hw-a：gate single_worker/workerCount1")
must('"captureMode":"drawelement"' in hw and "capture_streaming" in hw,
     "hw-a：drawelement＋capture_streaming")
must("rendered in 52.4s" in hw and "encode (during capture) 40.5s" in hw,
     "hw-a：尾报 52.4＋encode during capture 40.5")
must("2 error(s), 1 warning(s)" in bd
     and "Continuing render despite lint issues" in bd,
     "bad-lint 默认：2 error 1 warning＋Continuing")
must("not registered after 45000ms" in bd and "data-no-timeline" in bd,
     "bad-lint 默认：45000ms 等待警告＋data-no-timeline 提示")
must("Aborting render due to lint issues" in bs,
     "bad-lint --strict：Aborting 逐字")
must("Render blocked by 1 correctness warning" in mb
   and "audio_processing_failed: Audio mix failed; output would be video-only"
   in mb, "mm-be：blocked＋audio_processing_failed 逐字")

hf07 = S.PROJECTS / "hf-07" / "build" / "render.log"
if hf07.is_file():
    lines = read(hf07).splitlines()
    hit = [i + 1 for i, ln in enumerate(lines) if "41m 43.3s" in ln]
    must(bool(hit), "hf-07 render.log 41m 43.3s 尾报（行 %s）" % hit[:3])
    # more +7312 表示从第 7313 行开始显示，目标行须在其下一两行内
    near = [n for n in hit if 7313 <= n <= 7316]
    must(bool(near), "more +7312 起屏即见（7313–7316；实测 %s）" % hit[:5])
else:
    must(False, "hf-07 render.log 存在：%s" % hf07)

# ---------- 3. chunk 源码（src-blackbar 拍摄对象） ----------
print("== chunk 源码锚点 ==")
dists = []
for pj in Path(r"F:\npm-cache\_npx").glob("*/node_modules/hyperframes"):
    pkg = pj / "package.json"
    if pkg.is_file() and json.loads(read(pkg)).get("version") == S.HF_VERSION:
        dists.append(pj / "dist")
must(len(dists) >= 1, "npx 缓存存在 0.8.107 dist（候选 %d）" % len(dists))
if dists:
    dist = dists[0]
    c3w_p = dist / "chunk-3WG63KFW.js"
    c5_p = dist / "chunk-D5EJCP26.js"
    must(c3w_p.is_file() and c5_p.is_file(),
         "两 chunk 在（%s）" % dist)
    c3w, c5 = read(c3w_p), read(c5_p)
    must("RAM floor: routed parallel DE runs 3 concurrent hardware-GPU Chrome"
         in c3w and "produced vertical black slabs in the" in c3w
         and "final MP4 (wild report, CLI 0.7.52)" in c3w,
         "3WG63KFW：黑条注释三句逐字（16GB/3 实例/0.7.52）")
    must("HF_DE_PARALLEL_MIN_MEM_MB" in c3w and c3w.count("24576") >= 2,
         "3WG63KFW：HF_DE_PARALLEL_MIN_MEM_MB＋24576 地板")
    must("function computeWorkerSizing" in c5
         and "MEMORY_PER_WORKER_MB = 1536" in c5
         and "cpuCount - 2" in c5 and "totalMemoryMb * 0.5" in c5
         and "totalFrames / MIN_FRAMES_PER_WORKER" in c5,
         "D5EJCP26：computeWorkerSizing＋1536＋四笔账")

# ---------- 4. 坏工程静态属性 ----------
print("== 坏工程属性 ==")
bl = read(ROOT / "bad-lint" / "index.html")
must("requestAnimationFrame" in bl and "__timelines" not in bl
     and "data-no-timeline" not in bl,
     "bad-lint：rAF 驱动、无 timeline 注册（45000ms 等待必现）")
for f01 in ("f01.png", "f02.png", "out-default.mp4"):
    must((ROOT / "bad-lint" / f01).is_file(), "bad-lint/%s" % f01)
mm = read(ROOT / "missing-media" / "index.html")
must("media/nope.wav" in mm, "missing-media：audio src=media/nope.wav")

# ---------- 5. 真机工程与可执行依赖 ----------
print("== 工程/依赖 ==")
must((S.CALIB / "index.html").is_file() and (S.CALIB / "hyperframes.json").is_file(),
     "av-sync-calib 工程在仓库真名路径：%s" % S.CALIB)
for exe in ("wt.exe", "ffmpeg.exe", "powershell.exe"):
    must(shutil.which(exe) is not None, "%s 在 PATH" % exe)
must(shutil.which("npx.cmd") or shutil.which("npx"), "npx 在 PATH")
npp = Path(r"F:\_hftest\npp-local\notepad++.exe")
must(npp.is_file(), "便携 NPP 在 %s" % npp)
rec_dir = Path(r"F:\_hftest\hf08-rec")
try:
    rec_dir.mkdir(parents=True, exist_ok=True)
    must(rec_dir.is_dir(), "录制输出目录可写：%s" % rec_dir)
except OSError as e:
    must(False, "录制输出目录不可写：%s" % e)

print()
if fails:
    print("锚点自检失败 %d 项：" % len(fails))
    for f in fails:
        print("  FAIL", f)
    sys.exit(1)
print("全部锚点自检通过，可以开拍（记住：t0 必须是冷态第一条）。")
