# -*- coding: utf-8 -*-
"""hf-08 F2 人耳正音抽检：38 个高危点切成短句拼一个 mp3（render 前预扫）。

whisper 转录（build/raw.json，旧母带；patched 仅 267.24–271.12 四句秒
替换，raw 段时间戳窗外全部仍有效）客观核对不了的同音念错，必须人耳：
帧→针、烤→考、墙钟→墙中（whisper 同音），16777 是否念全「一万六千七百
七十七」，段188「check 零 error」是否被念成 check lint error（意思关天），
段82「390 张 PNG」转录只剩「390张N」疑似漏字母，SwiftShader/lambda/
benchmark/cloudrun/requestAnimationFrame/data-no-timeline 蛇形英文，
处 chù、重叠 chóng、兆、瓷砖，补丁新句「五十四秒」。

TARGETS：("seg", 子串) 按 raw segment 文本定位；("@", 起, 止) 显式窗。
每点前后留 0.5s（与前后句相连的长段不裁），段间 0.8s 静音，源统一为
patched 母带（补丁窗两点只有 patched 是新音）。

用法：python oneoffs/f2_pronounce.py
产物：build/f2/pronounce-check.mp3 ＋ pronounce-index.txt
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WAV = ROOT / "media" / "hf-08-yeyang-patched.wav"
RAW = ROOT / "build" / "raw.json"
OUT = ROOT / "build" / "f2"

# (标签, 定位)  定位：("seg", 子串) 或 ("@", 起, 止)
TARGETS = [
    ("01 无头 Chrome 整词", ("seg", "无头Chrome")),
    ("02 GPU 逐字母＋worker（软件/硬件 GPU 长段）", ("seg", "软件GPU")),
    ("03 每秒三十格/十三秒/三百九十格", ("seg", "30格")),
    ("04 --debug 横杠横杠", ("seg", "debug开关")),
    ("05 三百九十张 PNG（转录只剩 N，疑漏字母）★", ("seg", "390张N")),
    ("06 三点二兆＋烤炉（烤 kǎo/兆 zhào）", ("seg", "3.2兆")),
    ("07 SwiftShader 整词首听", ("seg", "SwiftShader")),
    ("08 好处 chù（不读 chǔ）", ("seg", "好处")),
    ("09 软件路首跑六十八秒", ("seg", "68秒")),
    ("10 试截几帧就花掉十六秒（帧 zhēn）", ("seg", "16秒")),
    ("11 五十六秒以内", ("seg", "56秒以内")),
    ("12 硬件路五十四秒★（补丁新音）", ("@", 267.26, 268.78)),
    ("13 编码和抓帧重叠在一起★（重叠 chóng／补丁新音）", ("@", 268.78, 271.02)),
    ("14 一万六千七百七十七帧★（16777 是否念全）", ("seg", "16777")),
    ("15 抓帧本体三十九分钟", ("seg", "39分钟")),
    ("16 全程四十一分四十三秒", ("seg", "41分43")),
    ("17 折下来每秒七帧左右（帧 zhēn）", ("seg", "每秒7针")),
    ("18 每个 worker 一千五百三十六兆", ("seg", "1536")),
    ("19 八核十六 G（核 hé）", ("seg", "八盒")),
    ("20 门槛二十四 G 内存", ("seg", "24G")),
    ("21 画面瓷砖（cí zhuān）", ("seg", "瓷砖")),
    ("22 iframe（i frame 两词）", ("seg", "iFrame")),
    ("23 lint 有 error 它并不拦", ("seg", "Lint有Error")),
    ("24 requestAnimationFrame 蛇形长名★", ("seg", "RequestAnimation")),
    ("25 墙钟黑户（qiáng zhōng）", ("seg", "墙中")),
    ("26 lint 报了两个 error", ("seg", "两个Error")),
    ("27 --strict", ("seg", "Strict")),
    ("28 check 零 error★★（勿念成 check lint error）", ("seg", "CheckLintError")),
    ("29 data-no-timeline 蛇形标记", ("seg", "NoTimeLine")),
    ("30 worker 静默退出", ("seg", "静默退出")),
    ("31 用 -w 降到一个 worker（横杠 w）", ("seg", "降到")),
    ("32 六十秒/三百秒/四十五秒 三道超时", ("@", 522.7, 528.4)),
    ("33 画质分三等、格式六种", ("@", 532.5, 536.0)),
    ("34 第四集 seek", ("seg", "交给Seek")),
    ("35 HTML 到 MP4", ("seg", "一份HTML")),
    ("36 cloud、lambda 两词首听", ("seg", "Cloud Lambda")),
    ("37 cloud run（cloudrun 是否念两词）", ("seg", "Cloud Run")),
    ("38 benchmark 整词首听", ("seg", "Benchmark")),
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
    for label, loc in TARGETS:
        if loc[0] == "seg":
            needle = loc[1]
            hit = next((s for s in segs if needle in s["t"]), None)
            if hit is None:
                index.append("[未命中] %s（关键词 %s）" % (label, needle))
                print("MISS", label)
                continue
            s0, s1, ctx = max(0.0, hit["s"] - PAD), hit["e"] + PAD, \
                hit["t"].strip()
        else:
            _, s0, s1 = loc
            ctx = "（显式窗）"
        clip = OUT / ("pc-%02d.wav" % len(parts))
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(s0),
             "-i", str(WAV), "-t", str(s1 - s0),
             "-c:a", "pcm_s16le", "-ar", "24000", "-ac", "1", str(clip)])
        parts.append(clip)
        index.append("%05.1fs  %s   （wav %.2f–%.2f：%s）"
                     % (cursor, label, s0, s1, ctx))
        cursor += (s1 - s0) + GAP
        print("OK  %s  %.2f–%.2f" % (label, s0, s1))

    gap = OUT / "_gap.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", "anullsrc=r=24000:cl=mono", "-t", str(GAP),
         "-c:a", "pcm_s16le", str(gap)])
    lines = []
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
        "hf-08 F2 人耳正音抽检清单（render 前预扫，源＝patched 母带）",
        "音频：build/f2/pronounce-check.mp3（每点前后 0.5s，点间 0.8s 静音）",
        "",
    ]
    (OUT / "pronounce-index.txt").write_text(
        "\n".join(head + index), encoding="utf-8")
    print("→ %s（%d 段）" % (mp3.relative_to(ROOT), len(parts)))


if __name__ == "__main__":
    main()
