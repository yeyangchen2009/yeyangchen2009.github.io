# -*- coding: utf-8 -*-
"""hf-05 F2 人耳正音抽检：把 18 个高危点切成短句拼成一个 mp3。

whisper 转录（build/transcript.txt）已客观核对过大多数点（蛇形规则名
按词念、npx/at/横杠横杠/error level、9 处「行」改写、量→测等），
但 TTS 同音念错 whisper 分不出来——几百「行/航」、3 处 děi、色值
逐字符、WCAG 逐字母、糊弄轻声——必须人耳。本脚本按 raw.json 的
segment 时间戳定位，每段前后留 0.5s，段间插 0.8s 静音拼成
build/f2/pronounce-check.mp3，清单同目录 pronounce-index.txt。
s-u-t vs sub 已有专用探针 build/probe-sut.wav（转录已证分字母），
清单里单列、不进合集。

用法：python oneoffs/f2_pronounce.py
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WAV = ROOT / "media" / "hf-05-yeyang.wav"
RAW = ROOT / "build" / "raw.json"
OUT = ROOT / "build" / "f2"

# (标签, whisper 转录中可命中的子串——按 transcript.txt 实际转写取)
TARGETS = [
    ("01 几百行 HTML 的行 háng", "几百行"),
    ("02 děi 它得到第十三秒才走", "得到第"),
    ("03 děi 都得 Chrome 画出像素", "都得"),
    ("04 děi 黄字得逐条读完", "条读完"),
    ("05 重叠 chóng", "时间还重"),
    ("06 挑 tiāo 深蓝灰", "挑了个"),
    ("07 色值 井号一a一f二六", "EF26"),
    ("08 rgb 九三 九七 一零二", "9397102"),
    ("09 WCAG 逐字母", "外格"),
    ("10 糊弄 hù nong", "互努"),
    ("11 帧 zhēn 帧帧可复现", "真真可"),
    ("12 暂 zàn 暂停的时间轴", "暂停的时间轴"),
    ("13 碍 ài 无障碍标准", "无障碍"),
    ("14 蛇形名 timeline element missing timing", "Mission Timing"),
    ("15 蛇形名 clip ends past root duration", "RudeDuration"),
    ("16 蛇形名 text occluded", "Acluded"),
    ("17 n-p-x 与 at 0.8.107", "NPX"),
    ("18 一点一四比一（四检查点全红）", "全红"),
    ("19 测布局（量→测改写）", "测布局"),
    ("20 测得出（量→测改写）", "测得出"),
    ("21 算节拍（数→算改写）", "算结拍"),
    ("22 停五秒（待→停改写）", "停五秒"),
    ("23 横杠横杠 shot", "横杠横杠"),
    ("24 error level（ERRORLEVEL 拆词）", "Area level"),
]

PAD = 0.5
GAP = 0.8


def run(cmd):
    subprocess.run(cmd, check=True, cwd=str(ROOT),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    segs = json.load(open(RAW, encoding="utf-8"))["segments"]
    OUT.mkdir(parents=True, exist_ok=True)
    parts, index = [], []
    cursor = 0.0
    for label, needle in TARGETS:
        hit = next((s for s in segs if needle in s["t"]), None)
        if hit is None:
            index.append("[未命中] %s（关键词 %s）" % (label, needle))
            print("MISS", label)
            continue
        s0, s1 = max(0.0, hit["s"] - PAD), hit["e"] + PAD
        clip = OUT / ("pc-%02d.wav" % len(parts))
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(s0),
             "-i", str(WAV), "-t", str(s1 - s0),
             "-c:a", "pcm_s16le", "-ar", "24000", "-ac", "1", str(clip)])
        parts.append(clip)
        index.append("%05.1fs  %s   （wav %.2f–%.2f：%s）"
                     % (cursor, label, s0, s1, hit["t"].strip()))
        cursor += (s1 - s0) + GAP
        print("OK  %s  %.2f–%.2f" % (label, s0, s1))
    # 段间静音：统一重切为 wav pcm 后 concat 带静音间隔
    gap = OUT / "_gap.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", "anullsrc=r=24000:cl=mono", "-t", str(GAP),
         "-c:a", "pcm_s16le", str(gap)])
    lines, seq = [], []
    for p in parts:
        lines.append("file '%s'" % p.as_posix())
        lines.append("file '%s'" % gap.as_posix())
    listfile = OUT / "_pronounce-list.txt"
    listfile.write_text("\n".join(lines), encoding="utf-8")
    mp3 = OUT / "pronounce-check.mp3"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", str(listfile),
         "-c:a", "libmp3lame", "-q:a", "4", str(mp3)])
    head = [
        "hf-05 F2 人耳正音抽检清单",
        "音频：build/f2/pronounce-check.mp3（每句前后留 0.5s，句间 0.8s 静音）",
        "另听：build/probe-sut.wav —— 井号 sub（本音）对比井号 s-u-t（分字母×2）",
        "",
    ]
    (OUT / "pronounce-index.txt").write_text(
        "\n".join(head + index), encoding="utf-8")
    print("→ %s（%d 段）" % (mp3.relative_to(ROOT), len(parts)))


if __name__ == "__main__":
    main()
