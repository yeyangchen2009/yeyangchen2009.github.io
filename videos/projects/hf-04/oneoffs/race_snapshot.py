# -*- coding: utf-8 -*-
"""排队三同 vs 一窝蜂分叉：snapshot 串行/并发实证（hf-04 段⑤a 入镜脚本）。

背景：s2-timer 页用 setInterval 每 500ms 把 tick 加一，这个动画不在 GSAP
时间轴上，seek 管不着它。实测：
  · 串行连问同一 t——三帧逐字节相同（机器闲、调度稳，截帧前墙钟流逝一致）；
  · N 路 Chrome 同时问同一 t——帧里的 tick 分叉（render workers=auto
    并行抢 CPU 的真实工况，各进程被调度得快慢不一，截帧前计数器多跳少跳）。

脚本分两轮，终端里一镜到底演完：

    python race-snapshot.py
      第一轮：排队，连问 3 次第二秒         -> rec-shots/ser-1..3
      第二轮：6 个渲染器同时问第二秒        -> rec-shots/tk-1..6
      收口：排队 1 种内容，一窝蜂 N 种内容

    python race-snapshot.py -n 8 --serial 0   # 不演串行、直接 8 路并发

用 --no-browser-gpu（SwiftShader）刻意制造 CPU 争抢——这正是无独显机器
上 render 的真实工况。脚本只调 npx snapshot，不碰任何窗口。
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PIN = "0.8.107"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_one(tag, out_rel, args, env):
    """一路 snapshot。tag 是日志/分组显示名（ser-1/tk-1）；帧落到 out_rel。"""
    out_abs = os.path.abspath(out_rel)
    if os.path.isdir(out_abs):
        shutil.rmtree(out_abs)
    cmd = ("npx --yes hyperframes@%s snapshot . --at %s --no-end -o %s"
           % (PIN, args.at, out_rel))
    if not args.gpu:
        cmd += " --no-browser-gpu"
    t0 = time.time()
    # npx 在 Windows 是 npx.cmd，必须 shell=True（直接 Popen 会 WinError 2）。
    # 180s 兜底：实拍最慢一轮实测 95s；超时 shell 被杀，极端情况下 chrome
    # 孙进程可能残留，超时时人工任务管理器核对。
    try:
        p = subprocess.run(cmd, shell=True, cwd=args.proj, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=180)
        dt = time.time() - t0
        frame = os.path.join(out_abs, "frame-00-at-%ss.png" % args.at)
        ok = p.returncode == 0 and os.path.exists(frame)
        return tag, ok, dt, frame, (None if ok else p.stdout[:400])
    except subprocess.TimeoutExpired:
        return tag, False, time.time() - t0, "", "超过 180s"


def report(label, tags, results, wall):
    """按 MD5 分组打印一轮结论。results: {tag: (ok, frame, err)}。"""
    groups = {}
    for tag in tags:
        ok, frame, _ = results[tag]
        if ok:
            groups.setdefault(md5(frame), []).append(tag)
    print("-" * 44)
    print("%s：墙钟 %.1fs，%d 张帧，%d 种内容"
          % (label, wall, len(tags), len(groups)))
    for ids in sorted(groups.values(), key=lambda v: -len(v)):
        line = "  " + "  ".join(ids)
        if len(ids) == 1:
            line += "  （独一份）"
        print(line)
    return groups


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--at", default="2", help="统一询问的时间点（默认 2 秒）")
    ap.add_argument("-n", "--count", type=int, default=6,
                    help="并发轮渲染器数量（默认 6）")
    ap.add_argument("-o", "--out-prefix", default="rec-shots/tk",
                    dest="out_prefix", help="并发轮输出前缀")
    ap.add_argument("--serial", type=int, default=3,
                    help="先串行连问几次做对照（默认 3，0 跳过）")
    ap.add_argument("--serial-prefix", default="rec-shots/ser",
                    dest="serial_prefix", help="串行轮输出前缀")
    ap.add_argument("--proj", default=os.getcwd(),
                    help="hyperframes 项目目录（默认当前目录）")
    ap.add_argument("--gpu", action="store_true",
                    help="不关 GPU（默认 --no-browser-gpu，用 SwiftShader 抢 CPU）")
    args = ap.parse_args()

    env = dict(os.environ)
    # 与 hf04-rec 终端 init 同口径；已在该终端内时变量继承、这里是兜底
    env.setdefault("HYPERFRAMES_FONT_CACHE_DIR", r"F:\_hftest\.cache\fonts")
    env.setdefault("HYPERFRAMES_NO_UPDATE_CHECK", "1")
    env.setdefault("HYPERFRAMES_SKIP_SKILLS", "1")

    # ---- 第一轮：排队，一个一个问 ----
    ser_groups = None
    if args.serial > 0:
        ser_tags = ["ser-%d" % i for i in range(1, args.serial + 1)]
        print("第一轮：排队，一个一个问第 %s 秒……" % args.at, flush=True)
        ser_results = {}
        t0 = time.time()
        for n, tag in enumerate(ser_tags, 1):
            print("  [排队] 第 %d 个出发" % n, flush=True)
            tg, ok, dt, frame, err = run_one(
                tag, "%s-%d" % (args.serial_prefix, n), args, env)
            ser_results[tg] = (ok, frame, err)
            print("  [归位] %s  %.1fs%s"
                  % (tg, dt, "" if ok else "  ✗ " + repr(err)), flush=True)
        ser_wall = time.time() - t0
        if any(not ok for ok, _, _ in ser_results.values()):
            print("串行轮有渲染器没出帧")
            return 1
        ser_groups = report("排 队 问", ser_tags, ser_results, ser_wall)
        print()

    # ---- 第二轮：一窝蜂，N 路同时问 ----
    par_tags = ["tk-%d" % i for i in range(1, args.count + 1)]
    print("第二轮：%d 个渲染器，同时问第 %s 秒……"
          % (args.count, args.at), flush=True)
    for tag in par_tags:
        print("  [出发] %s" % tag, flush=True)

    par_results = {}
    done = set()
    lock = threading.Lock()
    wall0 = time.time()

    def heartbeat(stop):
        # 无界面 Chrome 闷头跑可能 90s+，终端不能是死画面：
        # 每 5s 刷一行心跳，录屏加速段才有动感
        while not stop.wait(5):
            with lock:
                left = args.count - len(done)
            if left <= 0:
                break
            print("  ……已用 %ds，%d 路在跑"
                  % (int(time.time() - wall0), left), flush=True)

    stop_beat = threading.Event()
    beat = threading.Thread(target=heartbeat, args=(stop_beat,), daemon=True)
    beat.start()
    try:
        with ThreadPoolExecutor(max_workers=args.count) as ex:
            futs = [ex.submit(run_one, tag,
                              "%s-%d" % (args.out_prefix, n), args, env)
                    for n, tag in enumerate(par_tags, 1)]
            for fut in as_completed(futs):
                tag, ok, dt, frame, err = fut.result()
                with lock:
                    done.add(tag)
                par_results[tag] = (ok, frame, err)
                print("  [完成] %s  %.1fs%s"
                      % (tag, dt, "" if ok else "  ✗ " + repr(err)),
                      flush=True)
    finally:
        stop_beat.set()
    par_wall = time.time() - wall0

    if any(not ok for ok, _, _ in par_results.values()):
        print("并发轮有渲染器没出帧: %s"
              % [t for t, (ok, _, _) in par_results.items() if not ok])
        return 1
    par_groups = report("一 窝 蜂", par_tags, par_results, par_wall)

    # ---- 收口对比 ----
    print("=" * 44)
    if ser_groups is not None:
        print(">>> 排队问：%d 种；一窝蜂：%d 种。同一个第 %s 秒，答案唯不唯一，"
              "取决于问法" % (len(ser_groups), len(par_groups), args.at))
    else:
        print(">>> 同一个第 %s 秒，%d 个渲染器给出 %d 种画面"
              % (args.at, args.count, len(par_groups)))
    if len(par_groups) == 1:
        print("！并发轮全同——调度器没抢起来，重跑一次（或 -n 8）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
