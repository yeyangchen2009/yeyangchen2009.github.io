# -*- coding: utf-8 -*-
r"""hf-07 录屏布景生成器：在公开沙盒（默认 F:\_hftest\hf07-frames）生成

- proj/v1/index.html   主工程：GSAP 蓝块 seekable 0→800 ＋ 合法 CSS 绿点
                       （legalPulse，WAAPI 接管、体检在册）＋ 红块 setInterval
                       自掐表墙钟动画（4s 周期，不登记 timeline/WAAPI）
- proj/v2/index.html   compare 变体：蓝块换绿、距离缩到 500，绿点/红块同 v1
- proj/v3/index.html   边界实验：红块慢表 60s 一圈（第十秒补刀用）
- proj/grades.json     grade-compare 两档候选（暖色/高亮，adjust 对象档；
                       active grading 须 software 渲染，见 GRADES_JSON 注释）
- proj/hyperframes.json / package.json
- backup/              视觉权威态冻结（v1/v2/v3＋根配置），restore 一键回冻、
                        verify 哈希闸（hf-04 坑②：视觉定稿必须先于任一 take 冻结）

与 hf-06 不同：本集无 NPP 现场编辑、无多态切换、无媒体派生——三工程静态，
snapshot/keyframes/compare 全部只读工程。产物落 vN/snapshots/ 与 build/，
不污染冻结文件（snapshot 只清自己的 frame-*.png，PROBE E8）。

用法（在 videos/ 下）：
    python projects/hf-07/oneoffs/setup_scenes.py init
    python projects/hf-07/oneoffs/setup_scenes.py verify
    python projects/hf-07/oneoffs/setup_scenes.py restore v1
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

DEFAULT_ROOT = r"F:\_hftest\hf07-frames"
P = Path(__file__).resolve().parents[1]          # projects/hf-07
P05 = P.parent / "hf-05"
SEEDS = P / "oneoffs" / "probe-seeds"
GSAP = P / "gsap.min.js"

# (子目录, 种子文件)
COMPOSITIONS = [
    ("v1", "01-css-vs-gsap.html"),
    ("v2", "02-variant-x500.html"),
    ("v3", "03-wallclock-slow.html"),
]

HYPERFRAMES_JSON = """{
  "registry": [],
  "paths": { "compositions": "." },
  "media": { "autoProxy": true }
}
"""

PACKAGE_JSON = """{
  "name": "hf07-frames-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "check": "npx --yes hyperframes@0.8.107 check"
  }
}
"""

# PROBE E7（2026-10-20 勘误）：grading **不认 CSS filter 串**——"sepia(0.6)"
# 被当不存在的 preset id，adjust 全零，工具发
# 「Warning: grading for "暖色" is inactive/no-op」三格全等（首录 t08 即此态，
# c11 只断言成图大小未拦像素差异，溜过 12 次彩排）。正确 schema＝preset id
# （warm-daylight 等）或 {adjust:{...}} 对象，键 exposure/contrast/
# temperature/saturation 等，限值 ±1（exposure ±2）。力度取教学可视档
# （2×2 格位/跳标签条，MAD 暖色 (11.8,1.8,10.2)、高亮 (13.7,10.9,8.3)，
# 显著像素均 94%）。
# 另：active grading 在本机 headless hardware 模式必撞
# 「Navigation timeout of 10000ms exceeded」（UHD 620），必须
# PRODUCER_BROWSER_GPU_MODE=software ＋ --timeout 30000（真机 ~29.5s）。
# original 基线由工具自动 prepend。
GRADES_JSON = json.dumps([
    {"label": "暖色", "grading": {"adjust": {
        "temperature": 0.45, "saturation": 0.25, "exposure": 0.05}}},
    {"label": "高亮", "grading": {"adjust": {
        "exposure": 0.45, "contrast": 0.15}}},
], ensure_ascii=False, indent=2) + "\n"

# 文件名必须是 index.html：CLI 目录参数（check/preview/snapshot v1）只认
# index.html（真机：frame.html 报 No composition found）；compare 帮文档
# 位也可直接传目录。冻结清单只认这些，snapshots/ 与 build/ 不属布景。
FROZEN_FILES = ["hyperframes.json", "package.json", "grades.json"] + [
    "%s/index.html" % d for d, _ in COMPOSITIONS
] + ["%s/gsap.min.js" % d for d, _ in COMPOSITIONS]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _preview_up(port: int = 3021, timeout: float = 20.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with urllib.request.urlopen(
                    "http://127.0.0.1:%d/" % port, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(.5)
    return False


def prenormalize(proj: Path, port: int = 3021) -> None:
    """三工程各起停一次 background preview，触发 server 对 index.html 的
    规范化（注入 data-hf-id、属性压行、去自闭合斜杠），之后再冻结。

    2026-10-19 真机：check/snapshot 不写工程文件，唯 preview server 首次
    访问会改写；已带 data-hf-id 的文件原样保留（ID 不跨重启重生）。不预
    规范化则 verify 在 t00 起 server 后必挂。"""
    hf = ["npx.cmd", "--yes", "hyperframes@0.8.107"]
    for sub, _ in COMPOSITIONS:
        p = subprocess.run(hf + ["preview", sub, "--background", "--no-open",
                                 "--port", str(port)],
                           cwd=str(proj), capture_output=True,
                           timeout=90)
        if not _preview_up(port):
            sys.exit("预规范化：%s 的 preview server 起不来\n%s"
                     % (sub, p.stdout.decode("utf-8", "replace")[-800:]))
        time.sleep(2.0)   # 等 server 写盘
        subprocess.run(hf + ["preview", sub, "--stop"], cwd=str(proj),
                       capture_output=True, timeout=60)
        t0 = time.time()
        while time.time() - t0 < 10 and _preview_up(port, timeout=2):
            time.sleep(.5)
        print("  prenormalize %s ok" % sub)


def init(root: Path) -> None:
    if not (SEEDS / "01-css-vs-gsap.html").is_file():
        sys.exit("缺种子目录：%s" % SEEDS)
    if not GSAP.is_file():
        if not (P05 / "gsap.min.js").is_file():
            sys.exit("缺 gsap.min.js（hf-05 也没有）")
        shutil.copy(P05 / "gsap.min.js", GSAP)
    proj = root / "proj"
    backup = root / "backup"
    # 纯净重建：清掉上轮 frame.html 残留与 build 产物（snapshots 不入库但
    # 同盘，连坐清掉保证 init 幂等）。
    if proj.exists():
        shutil.rmtree(proj)
    (proj / "build").mkdir(parents=True, exist_ok=True)

    # newline="\n"：布景铁律，CRLF 会偏字节锚点（虽然本集无 NPP，hash 闸同样要求）。
    (proj / "hyperframes.json").write_text(
        HYPERFRAMES_JSON, encoding="utf-8", newline="\n")
    (proj / "package.json").write_text(
        PACKAGE_JSON, encoding="utf-8", newline="\n")
    (proj / "grades.json").write_text(
        GRADES_JSON, encoding="utf-8", newline="\n")
    for sub, seed in COMPOSITIONS:
        d = proj / sub
        d.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SEEDS / seed, d / "index.html")
        shutil.copyfile(GSAP, d / "gsap.min.js")

    # 先让 preview server 规范化一次（data-hf-id 注入），冻结的才是稳态
    prenormalize(proj)

    # 视觉权威态冻结
    if backup.exists():
        shutil.rmtree(backup)
    for rel in FROZEN_FILES:
        dst = backup / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(proj / rel, dst)
    rc = verify(root, quiet=True)
    print("布景完成：%s（三工程＋grades；权威态已冻结 backup/，verify=%s）"
          % (root, "OK" if rc == 0 else "FAIL"))


def restore(root: Path, name: str) -> None:
    """整目录回冻（v1/v2/v3）或根配置（root）。"""
    backup = root / "backup"
    proj = root / "proj"
    if not backup.is_dir():
        sys.exit("无 backup/，先 init")
    targets = [n for n, _ in COMPOSITIONS] + ["root"]
    if name not in targets:
        sys.exit("未知恢复目标 %s（可选 %s）" % (name, targets))
    if name == "root":
        rels = ["hyperframes.json", "package.json", "grades.json"]
    else:
        rels = ["%s/index.html" % name, "%s/gsap.min.js" % name]
    for rel in rels:
        src = backup / rel
        if not src.is_file():
            sys.exit("权威备份缺失: " + str(src))
        shutil.copyfile(src, proj / rel)
    print("已恢复 %s → proj/" % name)


def verify(root: Path, quiet: bool = False) -> int:
    """哈希闸：proj 冻结清单必须与 backup 逐字节一致（返回退出码，不 sys.exit）。"""
    proj = root / "proj"
    backup = root / "backup"
    bad = []
    for rel in FROZEN_FILES:
        a, b = proj / rel, backup / rel
        if not a.is_file() or not b.is_file():
            bad.append("%s（文件缺失）" % rel)
        elif _sha(a) != _sha(b):
            bad.append("%s（与 backup 不一致）" % rel)
    if bad:
        print("verify FAIL：\n  " + "\n  ".join(bad))
        return 1
    if not quiet:
        print("verify OK：%d 个冻结文件与 backup/ 逐字节一致" % len(FROZEN_FILES))
    return 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["init", "verify", "restore"])
    ap.add_argument("target", nargs="?", help="restore 用：v1/v2/v3/root")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    args = ap.parse_args()
    root = Path(args.root)

    if args.cmd == "init":
        init(root)
    elif args.cmd == "verify":
        sys.exit(verify(root))
    else:
        if not args.target:
            sys.exit("restore 需要目标名（v1/v2/v3/root）")
        restore(root, args.target)


if __name__ == "__main__":
    main()
