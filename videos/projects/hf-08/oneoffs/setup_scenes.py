# -*- coding: utf-8 -*-
r"""hf-08 录屏布景生成器：在公开沙盒（默认 F:\_hftest\hf08-media）落地

  hashes/        六权威 mp4（soft-a/soft-b/1015-old/w1/hw-a/hw-b，全 61145B、
                 sha256 六连同）——探针六跑 copy 改名，字节不动
  bad-lint/      6s 红块 rAF 工程（无 timeline 注册）＋f01/f02 备用帧＋默认产物
  missing-media/ 6s 工程，audio src=media/nope.wav
  seq/           png-sequence 实物：390 PNG（frame_000001 起）＋audio.m4a
  logs/          探针期 11 份日志（尾报/gate/45000ms 警告的二遍对拍底本）
  debug/         现跑一次 --debug 后从 npx 包目录 .debug/<jobId>/ 整目录搬来
                 （compiled/、capture-attempt-0/、captured-frames 390 JPG、
                 perf-summary.json、render.log；jobId 随机且可能被清，必须现搬）
  debug-output/  上述 --debug 跑的输出 mp4（-o 指这里，不碰仓库工程）
  stage-manifest.json  布景台账

av-sync-calib 工程**不 copy**：录屏终端 cwd 直接在仓库真名路径
F:\Data\Code\gmeek-site\videos\projects\av-sync-calib（render 自报路径入镜，工程名
是真名；该路径无用户名。成片录制于 2026-10-23 仓库迁移前，片里入镜的旧路径为
F:\Data\gmeek-site\videos\projects\av-sync-calib）。渲染输出一律 -o 到 F:\_hftest\hf08-rec，不污染仓库。

用法（在 videos/ 下）：
    python projects/hf-08/oneoffs/setup_scenes.py init            # 全建＋现跑 --debug（约 70s，非沙箱）
    python projects/hf-08/oneoffs/setup_scenes.py init --no-debug # 跳 debug 现跑（只搬静态件）
    python projects/hf-08/oneoffs/setup_scenes.py refresh-debug   # 只重跑/重搬 debug
    python projects/hf-08/oneoffs/setup_scenes.py verify          # hash/计数快验
    python projects/hf-08/oneoffs/setup_scenes.py list

冷态纪律（RECORD-NOTES 风险点 1）：init/refresh-debug 会真跑 render、把无头
Chrome 烤热。布景必须在录制日之前完成；录制当天第一条就是 t0，之前本目录
不许再跑任何 render（与 hf-06「先 warmup」相反）。
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = r"F:\_hftest\hf08-media"
PROBE_DIR = r"F:\_hftest\hf08-probe"
NPX_ROOT = r"F:\npm-cache\_npx"
HF_VERSION = "0.8.107"

P = Path(__file__).resolve().parents[1]              # projects/hf-08
PROJECTS = P.parent
CALIB = PROJECTS / "av-sync-calib"                   # 录屏真跑工程（仓库真名）

# 六权威 mp4：探针六跑 sha256 全等（PROBE-NOTES 第 2 节）。1015-old 代表
# 2026-10-15 历史档（probe-seeds 未留独立文件，六跑字节同 hash＝内容寻址证据，
# 用 dbg 跑的那份改名顶替，manifest 记来源）。
HASH_SHA256 = "2057d0377a07fbfd32e01c42c5ddf1c269b9b44cd1548f26324377f9ac6c5a83"
COPY_VIDEOS = [
    ("body-a", "soft-a"),
    ("body-b", "soft-b"),
    ("w1", "w1"),
    ("hw-a", "hw-a"),
    ("hw-b", "hw-b"),
    ("dbg", "1015-old"),
]
LOG_GLOBS = ["*.log"]


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def copydir_clean(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


# ---------- 静态件 ----------

def stage_static(root: Path, probe: Path) -> dict:
    counts = {}

    # 六权威 mp4：copy 改名＋逐件 sha 校验
    hd = root / "hashes"
    hd.mkdir(parents=True, exist_ok=True)
    for src_name, dst_name in COPY_VIDEOS:
        src = probe / (src_name + ".mp4")
        if not src.is_file():
            sys.exit("探针源缺失：%s" % src)
        got = sha256_of(src)
        if got != HASH_SHA256:
            sys.exit("探针源 hash 不符 %s：%s" % (src.name, got))
        shutil.copy2(src, hd / (dst_name + ".mp4"))
    counts["hashes"] = len(list(hd.glob("*.mp4")))

    # 坏工程／缺音轨工程
    copydir_clean(probe / "bad-lint", root / "bad-lint")
    copydir_clean(probe / "missing-media", root / "missing-media")
    counts["bad-lint"] = len(list((root / "bad-lint").iterdir()))
    counts["missing-media"] = len(list((root / "missing-media").iterdir()))

    # png-sequence 实物（390 PNG＋audio.m4a）
    copydir_clean(probe / "seq", root / "seq")
    counts["seq_files"] = len(list((root / "seq").iterdir()))

    # 日志：探针目录全部 *.log
    ld = root / "logs"
    ld.mkdir(parents=True, exist_ok=True)
    logs = sorted(probe.glob("*.log"))
    for lg in logs:
        shutil.copy2(lg, ld / lg.name)
    counts["logs"] = len(logs)
    return counts


# ---------- --debug 现跑＋整目录搬运 ----------

def _existing_debug_jobs() -> dict:
    jobs = {}
    npx = Path(NPX_ROOT)
    if not npx.is_dir():
        return jobs
    # 真机布局（2026-10-21）：.debug 在 node_modules 正下方、与 hyperframes 包
    # 平级（<hash>/node_modules/.debug/<jobId>/），不在包目录内；两种都扫兼容。
    patterns = ("*/node_modules/.debug", "*/node_modules/hyperframes/.debug")
    seen = set()
    for pat in patterns:
        for d in npx.glob(pat):
            if not d.is_dir() or d in seen:
                continue
            seen.add(d)
            for j in d.iterdir():
                if j.is_dir():
                    jobs[j.resolve()] = j.stat().st_mtime
    return jobs


def stage_debug(root: Path) -> dict:
    """在 av-sync-calib 真跑一次 --no-browser-gpu --debug，搬 .debug/<jobId>/。

    必须非沙箱（render 编码，沙箱限内存）。约 70s。
    """
    if not (CALIB / "index.html").is_file():
        sys.exit("录屏工程不存在：%s" % CALIB)
    out_dir = root / "debug-output"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / "dbg.mp4"
    if out_mp4.exists():
        out_mp4.unlink()

    before = _existing_debug_jobs()
    env_extra = {
        "HYPERFRAMES_FONT_CACHE_DIR": r"F:\_hftest\.cache\fonts",
        "HYPERFRAMES_NO_UPDATE_CHECK": "1",
        "HYPERFRAMES_SKIP_SKILLS": "1",
    }
    import os
    env = dict(os.environ)
    env.update(env_extra)
    argv = ["npx.cmd", "--yes", "hyperframes@" + HF_VERSION,
            "render", ".", "--no-browser-gpu", "--debug",
            "-o", str(out_mp4)]
    print("现跑 --debug（约 70s）：%s" % " ".join(argv))
    t0 = time.time()
    p = subprocess.run(argv, cwd=str(CALIB), env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    log_text = p.stdout.decode("utf-8", errors="replace")
    (root / "debug-output" / "setup-render.log").write_text(
        log_text, encoding="utf-8", newline="\n")
    if p.returncode != 0:
        sys.exit("--debug 渲染失败 exit=%s（见 debug-output/setup-render.log）"
                 % p.returncode)

    after = _existing_debug_jobs()
    new = [j for j in after if j not in before]
    if not new:
        # 容差：没抓到差集就取全包内最新 job（极端情况下 .debug 是跑前刚清的）
        sys.exit("没发现新增 .debug/<jobId>/（npx 根=%s）——手动定位后重跑"
                 % NPX_ROOT)
    job = max(new, key=lambda j: after[j])
    print("命中 debug job：%s" % job)

    dst = root / "debug"
    copydir_clean(job, dst)

    # 结构断言（PROBE-NOTES 第 3 节目录实物）
    frames = sorted((dst / "captured-frames").glob("frame_*.jpg"))
    perf = dst / "perf-summary.json"
    must = [dst / "compiled" / "index.html", dst / "render.log", perf,
            dst / "video-only.mp4", dst / "output.mp4"]
    missing = [str(m) for m in must if not m.exists()]
    if missing:
        sys.exit("debug 目录缺件：%s" % missing)
    if len(frames) != 390:
        sys.exit("captured-frames 应为 390 JPG，实测 %d" % len(frames))
    if frames[0].name != "frame_000000.jpg" or frames[-1].name != "frame_000389.jpg":
        sys.exit("JPG 编号首尾异常：%s … %s" % (frames[0].name, frames[-1].name))
    if not out_mp4.is_file() or sha256_of(out_mp4) != HASH_SHA256:
        sys.exit("debug 输出 mp4 缺失或 hash 不符（内容寻址证据失效）")

    perf_data = json.loads(perf.read_text(encoding="utf-8"))
    ws = perf_data.get("workerSizing")
    if not isinstance(ws, dict):
        sys.exit("perf-summary.json 无 workerSizing 对象")
    info = {
        "jobDir": str(job),
        "wallSeconds": round(dt, 1),
        "frames": len(frames),
        "totalElapsedMs": perf_data.get("totalElapsedMs"),
        "workerSizing": ws,
    }
    print("workerSizing 字段：%s" % ", ".join(sorted(ws.keys())))
    print("workers=%s boundBy=%s 四账 cpu=%s mem=%s frame=%s heap=%s"
          % (ws.get("workers"), ws.get("boundBy"),
             ws.get("cpuBasedWorkers"), ws.get("memoryBasedWorkers"),
             ws.get("frameBasedWorkers"), ws.get("heapBasedWorkers")))
    return info


# ---------- 子命令 ----------

def init(root: Path, probe: Path, run_debug: bool) -> None:
    if not Path(PROBE_DIR).is_dir():
        sys.exit("探针资产目录不存在：%s" % PROBE_DIR)
    if root.exists():
        print("清空旧布景：%s" % root)
        shutil.rmtree(root)
    root.mkdir(parents=True)
    counts = stage_static(root, probe)
    debug_info = stage_debug(root) if run_debug else None
    manifest = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "probeDir": str(probe),
        "calibProject": str(CALIB),
        "hyperframes": HF_VERSION,
        "sha256": HASH_SHA256,
        "copyVideos": [{"from": a, "to": b} for a, b in COPY_VIDEOS],
        "counts": counts,
        "debug": debug_info,
    }
    (root / "stage-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print("布景完成：%s（%s）" % (root, counts))
    if not run_debug:
        print("已跳 --debug 现跑；录前必须补跑 refresh-debug")


def refresh_debug(root: Path) -> None:
    if not root.is_dir():
        sys.exit("布景不存在，先 init：%s" % root)
    info = stage_debug(root)
    mf = root / "stage-manifest.json"
    manifest = json.loads(mf.read_text(encoding="utf-8"))
    manifest["debug"] = info
    manifest["debugRefreshedAt"] = datetime.now(timezone.utc).isoformat()
    mf.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8", newline="\n")
    print("debug 已刷新")


def verify(root: Path) -> None:
    hd = root / "hashes"
    bad = []
    for _, name in COPY_VIDEOS:
        f = hd / (name + ".mp4")
        if not f.is_file() or sha256_of(f) != HASH_SHA256:
            bad.append(name)
    n_jpg = len(list((root / "debug" / "captured-frames").glob("*.jpg")))
    n_png = len(list((root / "seq").glob("frame_*.png")))
    print("六 mp4：%s" % ("全中" if not bad else "失败 %s" % bad))
    print("captured-frames JPG：%d（390）" % n_jpg)
    print("seq PNG：%d（390）" % n_png)
    if bad or n_jpg != 390 or n_png != 390:
        sys.exit(1)


def list_states(root: Path) -> None:
    for d in ("hashes", "bad-lint", "missing-media", "seq", "logs",
              "debug", "debug-output"):
        p = root / d
        n = len(list(p.rglob("*"))) if p.exists() else 0
        print("%-14s %s（%d 项）" % (d, "在" if p.exists() else "缺", n))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "refresh-debug", "verify", "list"])
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--probe", default=PROBE_DIR)
    ap.add_argument("--no-debug", action="store_true",
                    help="init 时跳 --debug 现跑")
    args = ap.parse_args()
    root = Path(args.root)
    if args.cmd == "init":
        init(root, Path(args.probe), run_debug=not args.no_debug)
    elif args.cmd == "refresh-debug":
        refresh_debug(root)
    elif args.cmd == "verify":
        verify(root)
    else:
        list_states(root)


if __name__ == "__main__":
    main()
