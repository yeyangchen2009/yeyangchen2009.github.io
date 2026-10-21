# -*- coding: utf-8 -*-
r"""hf-08 录前彩排：布景静态闸＋t3/t4/t5 真机 render＋Get-FileHash＋flake 率。

不注入键鼠、不录屏；全部断言逐字出自 PROBE-NOTES.md 与 chunk 源码
（2026-10-21 取证）。全量日志落 build/rehearsal-log.txt，实测墙钟落
build/rehearsal-timings.json——录屏等待常量与 RECORD-NOTES 第三、四节
按本文件回填。

用法（在 videos/ 下，必须非沙箱）：
    python projects/hf-08/oneoffs/setup_scenes.py init
    python projects/hf-08/oneoffs/run_rehearsal.py              # 全量（含三连 flaky，约 10 分钟）
    python projects/hf-08/oneoffs/run_rehearsal.py --skip-flaky # 跳三连 render
"""
import argparse
import hashlib
import io
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import setup_scenes as S  # noqa: E402

BUILD = HERE.parent / "build"
LOG = BUILD / "rehearsal-log.txt"
TIMINGS = BUILD / "rehearsal-timings.json"
HF = ["npx.cmd", "--yes", "hyperframes@" + S.HF_VERSION]

results = []
timings = {}


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("%s  %s  %s" % ("PASS" if cond else "FAIL", name, detail)).rstrip())


def section(t):
    print("\n== %s ==" % t)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def run_render(cwd: Path, argv_extra, out_name=None, timeout=600):
    """真机 render，计时；返回 (code, out, dt)。产物 -o 指 build/rehearsal/。"""
    out_dir = BUILD / "rehearsal"
    out_dir.mkdir(parents=True, exist_ok=True)
    argv = HF + ["render", "."] + argv_extra
    if out_name:
        argv += ["-o", str(out_dir / out_name)]
    t0 = time.time()
    p = subprocess.run(argv, cwd=str(cwd),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=timeout)
    dt = time.time() - t0
    return p.returncode, p.stdout.decode("utf-8", errors="replace"), dt


# ---------- 静态闸 ----------

def static_layout(root: Path):
    section("布景目录与六 hash")
    for _, name in S.COPY_VIDEOS:
        f = root / "hashes" / (name + ".mp4")
        ok = f.is_file() and sha(f) == S.HASH_SHA256
        check("hash %s.mp4 61145B 同 sha" % name, ok,
              "" if ok else "缺或 hash 不符")

    jpgs = sorted((root / "debug" / "captured-frames").glob("frame_*.jpg"))
    check("debug captured-frames 390 JPG（000000–000389）",
          len(jpgs) == 390 and jpgs[0].name == "frame_000000.jpg"
          and jpgs[-1].name == "frame_000389.jpg",
          "实测 %d" % len(jpgs))
    pngs = sorted((root / "seq").glob("frame_*.png"))
    check("seq 390 PNG（000001–000390）＋audio.m4a",
          len(pngs) == 390 and pngs[0].name == "frame_000001.png"
          and pngs[-1].name == "frame_000390.png"
          and (root / "seq" / "audio.m4a").is_file(),
          "实测 %d" % len(pngs))
    check("debug output.mp4 同 hash（内容寻址）",
          sha(root / "debug" / "output.mp4") == S.HASH_SHA256)

    section("perf-summary workerSizing 字段")
    perf = json.loads(read(root / "debug" / "perf-summary.json"))
    ws = perf.get("workerSizing", {})
    fields = {"workers", "boundBy", "cpuBasedWorkers", "memoryBasedWorkers",
              "frameBasedWorkers", "heapBasedWorkers", "heapLimitMb",
              "totalMemoryMb", "cpuCount"}
    miss = fields - set(ws)
    check("workerSizing 含四账＋决议字段", not miss,
          "缺 %s；实测字段 %s" % (sorted(miss), sorted(ws)))
    check("本机决议 workerCount=3（cpu6/mem5/frame13/heap5 取小 contention）",
          ws.get("workers") == 3, "实测 workers=%s boundBy=%s"
          % (ws.get("workers"), ws.get("boundBy")))
    check("cpu 账＝核数−2＝6", ws.get("cpuBasedWorkers") == 6,
          "cpuCount=%s → %s" % (ws.get("cpuCount"), ws.get("cpuBasedWorkers")))
    check("frame 账＝390/30＝13", ws.get("frameBasedWorkers") == 13,
          "实测 %s" % ws.get("frameBasedWorkers"))

    section("坏工程静态属性")
    bl = read(root / "bad-lint" / "index.html")
    check("bad-lint 是 rAF 红块、无 timeline 注册",
          "requestAnimationFrame" in bl and "__timelines" not in bl
          and "data-no-timeline" not in bl)
    check("bad-lint 时长 data-duration=\"6\"", 'data-duration="6"' in bl)
    mm = read(root / "missing-media" / "index.html")
    check("missing-media audio src=nope.wav", "media/nope.wav" in mm)


def static_logs(root: Path):
    section("日志逐字锚点（二遍对拍底本）")
    ra = read(root / "logs" / "run-a.log")
    hw = read(root / "logs" / "hw-a.log")
    bd = read(root / "logs" / "bad-lint-default.log")
    bs = read(root / "logs" / "bad-lint-strict.log")
    mb = read(root / "logs" / "mm-be.log")

    check("run-a gate 多 worker 关 streaming",
          '"enabled":false' in ra and '"reason":"multi_worker"' in ra
          and '"workerCount":3' in ra and '"maxDurationSeconds":240' in ra)
    check("run-a 尾报 1m 8.1s＋setup 16.4s＋capture 33.6s",
          "rendered in 1m 8.1s" in ra and "setup 16.4s" in ra
          and "capture 33.6s" in ra and "encode 14.2s" in ra)
    check("hw-a gate 单 worker 开 streaming",
          '"enabled":true' in hw and '"reason":"single_worker"' in hw
          and '"workerCount":1' in hw)
    check("hw-a drawelement＋capture_streaming",
          '"captureMode":"drawelement"' in hw and "capture_streaming" in hw)
    check("hw-a 尾报 52.4s＋encode (during capture) 40.5s",
          "rendered in 52.4s" in hw
          and "encode (during capture) 40.5s" in hw)
    check("bad-lint 默认：2 error 1 warning＋Continuing",
          "2 error(s), 1 warning(s)" in bd
          and "Continuing render despite lint issues" in bd)
    check("bad-lint 默认：45000ms 等待警告＋data-no-timeline 提示",
          "not registered after 45000ms" in bd and "data-no-timeline" in bd)
    check("bad-lint --strict：Aborting",
          "Aborting render due to lint issues" in bs)
    check("missing-media：audio_processing_failed blocked",
          "Render blocked by 1 correctness warning" in mb
          and "audio_processing_failed: Audio mix failed; output would be video-only"
          in mb)

    hf07 = S.PROJECTS / "hf-07" / "build" / "render.log"
    if hf07.is_file():
        lines = read(hf07).splitlines()
        hit = [i + 1 for i, ln in enumerate(lines) if "41m 43.3s" in ln]
        check("hf-07 render.log 含 41m 43.3s 尾报", bool(hit),
              "行号 %s（RECORD-NOTES 估 7314）" % hit[:3])
    else:
        check("hf-07 render.log 存在", False, str(hf07))


def static_chunks():
    section("npx 缓存 chunk 源码逐字（freeze 拍摄对象）")
    # npx 缓存 hash 目录随安装变，按 package.json 版本解析 0.8.107 实例
    base = Path(r"F:\npm-cache\_npx")
    dists = []
    for pj in base.glob("*/node_modules/hyperframes"):
        try:
            ver = json.loads(read(pj / "package.json")).get("version")
        except OSError:
            continue
        if ver == S.HF_VERSION:
            dists.append(pj / "dist")
    if not dists:
        check("找到 0.8.107 dist 目录", False)
        return
    dist = dists[0]
    check("0.8.107 dist 唯一定位（%s）" % dist, len(dists) >= 1,
          "候选 %d 个，取 %s" % (len(dists), dist))
    c3w = read(dist / "chunk-3WG63KFW.js")
    c5 = read(dist / "chunk-D5EJCP26.js")
    check("黑条注释逐字（16GB/3 实例/vertical black slabs/0.7.52）",
          "RAM floor: routed parallel DE runs 3 concurrent hardware-GPU Chrome"
          in c3w and "produced vertical black slabs in the" in c3w
          and "final MP4 (wild report, CLI 0.7.52)" in c3w)
    check("并行内存地板 HF_DE_PARALLEL_MIN_MEM_MB=24576＋700 帧闸",
          "HF_DE_PARALLEL_MIN_MEM_MB" in c3w and c3w.count("24576") >= 2
          and "700" in c3w)
    check("computeWorkerSizing 四笔账逐字（−2／0.5／1536／30）",
          "function computeWorkerSizing" in c5
          and "MEMORY_PER_WORKER_MB = 1536" in c5
          and "cpuCount - 2" in c5 and "totalMemoryMb * 0.5" in c5
          and "totalFrames / MIN_FRAMES_PER_WORKER" in c5)


# ---------- 真机 render ----------

def live_badlint(root: Path):
    section("t3 真机：bad-lint 默认 render（含 45000ms×N 等待，计时）")
    code, out, dt = run_render(root / "bad-lint", [], "t3.mp4")
    timings["t3_badlint_seconds"] = round(dt, 1)
    ok = code == 0 and "Continuing render despite lint issues" in out \
        and "2 error(s), 1 warning(s)" in out
    check("t3 exit0＋2 error 1 warning＋Continuing", ok,
          "exit=%s %.1fs" % (code, dt))
    mp4 = BUILD / "rehearsal" / "t3.mp4"
    check("t3 产物落盘（探针档 24527B）", mp4.is_file()
          and 20000 < mp4.stat().st_size < 30000,
          "%d B" % (mp4.stat().st_size if mp4.is_file() else -1))
    n45 = out.count("not registered after 45000ms")
    timings["t3_poll45_hits"] = n45
    check("t3 45000ms 等待命中次数（录制中段弃段依据）", n45 >= 1,
          "实测 %d 次" % n45)


def live_strict(root: Path):
    section("t4 真机：bad-lint --strict（计时）")
    code, out, dt = run_render(root / "bad-lint", ["--strict"], None)
    timings["t4_strict_seconds"] = round(dt, 1)
    check("t4 exit1＋Aborting due to lint issues",
          code == 1 and "Aborting render due to lint issues" in out,
          "exit=%s %.1fs" % (code, dt))


def live_missing(root: Path):
    section("t5 真机：missing-media 默认 render（计时）")
    code, out, dt = run_render(root / "missing-media", [], "t5.mp4")
    timings["t5_missing_seconds"] = round(dt, 1)
    check("t5 exit1＋audio_processing_failed blocked",
          code == 1 and "Render blocked by 1 correctness warning" in out
          and "audio_processing_failed" in out,
          "exit=%s %.1fs" % (code, dt))


def live_hash(root: Path):
    section("t2 真机：PowerShell Get-FileHash 六连")
    ps = ("Get-FileHash soft-a.mp4,soft-b.mp4,1015-old.mp4,w1.mp4,hw-a.mp4,"
          "hw-b.mp4 -Algorithm SHA256 | Format-Table Path,Hash -AutoSize "
          "| Out-String -Width 220")
    p = subprocess.run(["powershell.exe", "-NoProfile", "-Command", ps],
                       cwd=str(root / "hashes"),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.stdout.decode("utf-8", errors="replace")
    # Format-Table 行形态：<name>.mp4  <64hex>；取所有 64 十六进制串
    import re
    hx = re.findall(r"\b[0-9A-F]{64}\b", out.upper())
    check("六行 Hash 全＝2057…c6c5a83", len(hx) == 6
          and all(h == S.HASH_SHA256.upper() for h in hx),
          "解析到 %d 个 hash" % len(hx))
    check("Format-Table 单行不折（含 Path 六个文件名）",
          all(n in out for n in ("soft-a.mp4", "soft-b.mp4", "1015-old.mp4",
                                 "w1.mp4", "hw-a.mp4", "hw-b.mp4")))


def live_flaky(root: Path):
    section("flake 率：av-sync-calib 软件路连跑 3 次（约 3 分钟）")
    cwd = S.CALIB
    rows = []
    for i in (1, 2, 3):
        code, out, dt = run_render(cwd, ["--no-browser-gpu"],
                                   "flaky-%d.mp4" % i)
        mp4 = BUILD / "rehearsal" / ("flaky-%d.mp4" % i)
        same = mp4.is_file() and sha(mp4) == S.HASH_SHA256
        tail = ""
        for ln in out.splitlines()[::-1]:
            if "rendered in" in ln:
                tail = ln.strip()
                break
        rows.append((i, code, round(dt, 1), same, tail))
        check("flaky #%d exit0＋产物同 hash" % i, code == 0 and same,
              "exit=%s %.1fs %s" % (code, dt, tail))
        time.sleep(2)
    timings["flaky_runs"] = [
        {"i": i, "exit": c, "seconds": d, "hashSame": s, "tail": t}
        for i, c, d, s, t in rows]
    check("三连无 ERR_UNSAFE_PORT",
          all(c == 0 for _, c, _, _, _ in rows))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=S.DEFAULT_ROOT)
    ap.add_argument("--skip-flaky", action="store_true")
    ap.add_argument("--only", default="",
                    help="只跑一组：static/log/chunks/t3/t4/t5/hash/flaky")
    args = ap.parse_args()
    root = Path(args.root)
    if not (root / "stage-manifest.json").is_file():
        sys.exit("布景不存在：先 python oneoffs/setup_scenes.py init")
    if not shutil.which("npx.cmd") and not shutil.which("npx"):
        sys.exit("PATH 中找不到 npx")

    BUILD.mkdir(parents=True, exist_ok=True)
    groups = {
        "static": lambda: static_layout(root),
        "logs": lambda: static_logs(root),
        "chunks": static_chunks,
        "t3": lambda: live_badlint(root),
        "t4": lambda: live_strict(root),
        "t5": lambda: live_missing(root),
        "hash": lambda: live_hash(root),
        "flaky": lambda: live_flaky(root) if not args.skip_flaky else None,
    }
    order = ["static", "logs", "chunks", "t3", "t4", "t5", "hash", "flaky"]
    if args.only:
        order = [args.only]

    saved = sys.stdout
    logf = LOG.open("w", encoding="utf-8", newline="\n")

    class Tee:
        def write(self, s):
            saved.write(s)
            logf.write(s)
        def flush(self):
            saved.flush()
            logf.flush()

    sys.stdout = Tee()
    try:
        for g in order:
            fn = groups[g]
            if fn is None:
                continue
            fn()
    except subprocess.TimeoutExpired as e:
        check("render 超时", False, str(e))
    finally:
        sys.stdout = saved
        logf.close()
        TIMINGS.write_text(json.dumps(timings, ensure_ascii=False, indent=2)
                          + "\n", encoding="utf-8", newline="\n")

    nfail = sum(1 for _, ok, _ in results if not ok)
    print("\n" + "=" * 60)
    print("FAIL %d / %d；日志 %s；墙钟 %s"
          % (nfail, len(results), LOG, TIMINGS))
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
