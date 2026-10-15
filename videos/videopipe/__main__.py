# -*- coding: utf-8 -*-
"""videopipe 命令行：把管线里逐片重复的三个步骤收成一条命令。

在 videos/ 目录下运行（project 传项目目录）：

    # ③ TTS 音频 → 16k → whisper 词级转录
    python -m videopipe transcribe projects/liangwudi
    # ④ 正字稿对齐转录、组句（产物只进 build/，评审后加 --install 落地）
    python -m videopipe cues projects/liangwudi
    python -m videopipe cues projects/liangwudi --install
    # ⑧ 封面静帧头 + 正片无损 concat → 终片（时长自动 probe、自动断言）
    python -m videopipe finalize projects/liangwudi
    # 录屏素材帧率门禁（gdigrab VFR 体检，精切前必跑；退出码 2＝检出 VFR）
    python -m videopipe probe-fps projects/hf-05/media

所有路径默认按 ProjectPaths 与「<项目目录名>」约定推导，可用对应
--wav/--src/--body/--cover/--out 覆盖；不再需要每片手抄 oneoff。
"""
import argparse
import io
import sys
from pathlib import Path

from . import config
from .align import align, check_report
from .audioio import probe_duration, read_pcm16, to_16k_mono
from .concat import finalize_concat, finalize_intro, make_cover_head
from .config import ProjectPaths
from .cues import build_cues_json, enforce_monotonic, group_cues, save_cues, to_srt
from .whisper_asr import load_raw, save_raw, transcribe


def _paths(project: str) -> ProjectPaths:
    P = ProjectPaths.at(Path(project).resolve())
    if not P.root.is_dir():
        sys.exit("项目目录不存在：%s" % P.root)
    P.build_dir.mkdir(parents=True, exist_ok=True)
    return P


# --- ③ 转录 ---

def cmd_transcribe(P: ProjectPaths, a) -> None:
    name = P.root.name
    wav = Path(a.wav) if a.wav else P.media_dir / ("%s-yeyang.wav" % name)
    if not wav.exists():
        sys.exit("TTS 音频不存在：%s（可用 --wav 指定）" % wav)

    wav16 = P.build_dir / "16k.wav"
    raw = P.build_dir / "raw.json"
    txt = P.build_dir / "transcript.txt"

    to_16k_mono(wav, wav16)
    dur = probe_duration(wav)
    pcm = read_pcm16(wav16)
    print("时长 %.2f 秒" % dur)

    tr = transcribe(pcm, dur, model_size=a.model, beam_size=a.beam,
                    vad_filter=a.vad_filter,
                    condition_on_previous_text=a.keep_context)
    save_raw(tr, raw)

    lines = []
    for seg in tr.segments:
        print("SEG %.2f-%.2f %s" % (seg.s, seg.e, seg.t))
        lines.append(seg.t)
    io.open(txt, "w", encoding="utf-8").write("\n".join(lines))
    print("词数 %d" % sum(len(g.words) for g in tr.segments))
    print("产物：%s、%s、%s" % (wav16, raw, txt))


# --- ④ 对齐组句 ---

def cmd_cues(P: ProjectPaths, a) -> None:
    name = P.root.name
    src = Path(a.src) if a.src else P.src_dir / ("%s-src.txt" % name)
    raw = Path(a.raw) if a.raw else P.build_dir / "raw.json"
    if not src.exists():
        sys.exit("正字稿不存在：%s（可用 --src 指定）" % src)
    if not raw.exists():
        sys.exit("词级转录不存在：%s（先跑 transcribe）" % raw)

    out_json = P.build_dir / "cues.json"
    out_srt = P.build_dir / "cues.srt"
    out_chk = P.build_dir / "align-check.txt"

    src_text = io.open(src, encoding="utf-8").read()
    tr = load_raw(raw)

    al = align(src_text, tr)
    report = check_report(al)
    print(report)

    cues = enforce_monotonic(group_cues(src_text, al, a.split))
    data = build_cues_json(tr.duration, al, cues)
    save_cues(data, out_json)
    io.open(out_srt, "w", encoding="utf-8").write(to_srt(cues))

    buf = [report, "", "句数 %d，字數 %d" % (len(cues), len(al.chars)), ""]
    for q in cues:
        buf.append("%.2f-%.2f  %s" % (q["s"], q["e"], q["t"]))
    io.open(out_chk, "w", encoding="utf-8").write("\n".join(buf))

    print("句数 %d" % len(cues))
    print("产物：%s、%s、%s" % (out_json, out_srt, out_chk))
    if a.install:
        P.cues_json.parent.mkdir(parents=True, exist_ok=True)
        save_cues(data, P.cues_json)
        print("已落地评审版：%s" % P.cues_json)
    else:
        print("评审 align-check/srt 无误后，加 --install 落地为 %s"
              % P.cues_json)


# --- ⑧ 终片拼接 ---

def cmd_finalize(P: ProjectPaths, a) -> None:
    name = P.root.name
    cover = Path(a.cover) if a.cover else P.snapshots_dir / "cover-final.png"
    body = Path(a.body) if a.body else P.renders_dir / ("%s-body.mp4" % name)
    out = Path(a.out) if a.out else P.media_dir / ("%s-yeyang-cover.mp4" % name)
    if not cover.exists():
        sys.exit("封面不存在：%s（可用 --cover 指定）" % cover)
    if not body.exists():
        sys.exit("正片不存在：%s（可用 --body 指定）" % body)

    head = P.build_dir / "cover-head.mp4"
    make_cover_head(cover, head, seconds=a.hold)
    head_dur = probe_duration(head)
    body_dur = probe_duration(body)
    print("封面头 %.3fs" % head_dur)
    print("正片   %.3fs" % body_dur)

    out.parent.mkdir(parents=True, exist_ok=True)
    if a.intro:
        # 封面段吃正片开头 N 秒声音（报名响在封面），画面 -ss N 裁起；
        # 音频整段不动，终片与正片等长。
        finalize_intro(head, body, out, seconds=a.hold, workdir=P.build_dir)
        expect = body_dur
        print("模式   intro（封面带正片头 %s 秒声音，画面 -ss %s 裁起）"
              % (a.hold, a.hold))
    else:
        finalize_concat(head, body, out, seconds=a.hold, workdir=P.build_dir)
        expect = a.hold + body_dur
    total = probe_duration(out)
    print("终片   %.3fs → %s" % (total, out))
    assert abs(total - expect) < 0.1, "终片 %f != 预期 %f" % (total, expect)
    print("RESULT PASS")


# --- 录屏素材帧率门禁（gdigrab VFR 体检，不按项目布局，路径任意）---

def cmd_probe_fps(a) -> int:
    from .mediaprobe import scan
    healthy, vfr, unreadable = scan(a.paths, threshold=a.threshold)
    print("CFR %d 段" % len(healthy))
    for info in vfr:
        r = "%.3f" % info["r_fps"] if info["r_fps"] else "?"
        avg = "%.3f" % info["avg_fps"] if info["avg_fps"] else "?"
        print("VFR  %s  r=%s avg=%s 偏差 %.1f%%"
              % (info["path"], r, avg, info["ratio"] * 100))
    for info in unreadable:
        print("???? %s  帧率字段缺失或不可读" % info["path"])
    if unreadable:
        return 1
    if vfr:
        print("%d 段 VFR：精切必须加 -vf fps=30 重建 PTS" % len(vfr),
              file=sys.stderr)
        return 2
    print("帧率门禁通过（阈值 %.0f%%）" % (a.threshold * 100))
    return 0


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    p = argparse.ArgumentParser(
        prog="python -m videopipe",
        description="视频管线命令行：transcribe（转录）/ cues（对齐组句）/ "
                    "finalize（终片拼接）/ probe-fps（录屏帧率门禁）",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("transcribe", help="③ TTS wav → 16k → whisper 词级转录")
    t.add_argument("project", help="项目目录，如 projects/liangwudi")
    t.add_argument("--wav", help="TTS 音频（默认 media/<项目名>-yeyang.wav）")
    t.add_argument("--model", default="base", help="whisper 模型，默认 base")
    t.add_argument("--beam", type=int, default=5, help="beam size，默认 5")
    t.add_argument("--vad", dest="vad_filter", action="store_true",
                   help="开 VAD（TTS 干净连续，默认不开）")
    t.add_argument("--keep-context", dest="keep_context", action="store_true",
                   default=True, help="保留上文条件（默认开）")
    t.add_argument("--no-keep-context", dest="keep_context",
                   action="store_false", help="关闭上文条件")

    c = sub.add_parser("cues", help="④ 正字稿对齐转录、组句")
    c.add_argument("project", help="项目目录")
    c.add_argument("--src", help="正字稿（默认 src/<项目名>-src.txt）")
    c.add_argument("--raw", help="词级转录（默认 build/raw.json）")
    c.add_argument("--split", default=config.SPLIT_FULL,
                   help="组句标点，默认 config.SPLIT_FULL")
    c.add_argument("--install", action="store_true",
                   help="评审后直接落地 cues/cues.json（默认只写 build/）")

    f = sub.add_parser("finalize", help="⑧ 封面静帧头 + 正片 → 终片")
    f.add_argument("project", help="项目目录")
    f.add_argument("--cover", help="封面 PNG（默认 snapshots/cover-final.png）")
    f.add_argument("--body", help="正片（默认 renders/<项目名>-body.mp4）")
    f.add_argument("--out", help="终片（默认 media/<项目名>-yeyang-cover.mp4）")
    f.add_argument("--hold", type=float, default=config.COVER_HOLD,
                   help="封面静帧秒数，默认 2.0")
    f.add_argument("--intro", action="store_true",
                   help="封面段吃正片头 N 秒声音（报名响在封面），正片画面 "
                        "-ss N 裁起，音频整段不动，终片与正片等长")

    pf = sub.add_parser("probe-fps",
                        help="录屏素材 VFR 帧率门禁（文件或目录，退出码 2＝检出 VFR）")
    pf.add_argument("paths", nargs="+", help="视频文件或含视频的目录")
    pf.add_argument("--threshold", type=float, default=0.1,
                    help="|rFps-avgFps|/max 判 VFR 阈值，默认 0.1（10%%）")

    args = p.parse_args()
    if args.cmd == "probe-fps":
        raise SystemExit(cmd_probe_fps(args))
    P = _paths(args.project)
    {"transcribe": cmd_transcribe,
     "cues": cmd_cues,
     "finalize": cmd_finalize}[args.cmd](P, args)


if __name__ == "__main__":
    main()
