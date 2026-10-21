# -*- coding: utf-8 -*-
"""hf-08 蝉镜段级取音＋母带拼接（首录全 22 段新音，2026-10-21）。

借音稿 src/hf-08-tts.txt 按空行切段（与正字稿段一一对应），逐段走蝉镜
网页「试听」通道 0 蝉豆取音（全局 skill chanjing-tts 的 cj-web-tts.js，
绝不点「立即生成」），项目独立 profile Temp/cj-profile（SETUP.md 复制）。

裁边/拼接常量沿 hf-07 rebuild_audio.py 实测值：20ms 帧 RMS 双门限找能量
界、连续 3 帧命中；每段内容前 0.14s 后 0.20s 静音（段间合计 0.34s），
片头 0.20s、片尾 0.50s。

用法（fetch 必须非沙箱：要起浏览器联网；split/build 纯本地）：
  python oneoffs/fetch_segments.py split            # 切 segNN.txt，打印段长
  python oneoffs/fetch_segments.py fetch [NN ...]   # 逐段取音，已存在跳过
  python oneoffs/fetch_segments.py fetch --force 03 # 强制重取某段
  python oneoffs/fetch_segments.py build            # 裁边拼接 → media 母带
"""
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC_TTS = ROOT / "src" / "hf-08-tts.txt"
SEG_DIR = ROOT / "build" / "tts-seg"
MEDIA = ROOT / "media"
MASTER = MEDIA / "hf-08-yeyang.wav"

CJ_JS = r"C:\Users\yyb44\.claude\skills\chanjing-tts\scripts\cj-web-tts.js"
PROFILE = str(ROOT / "Temp" / "cj-profile")
AUDIO_MAN = "C-df5d6f1a95904a91a8e086b6f2fd8a53"

SR = 24000
FRAME = int(0.02 * SR)
HEAD, TAIL = 0.14, 0.20
HEAD_FIRST, TAIL_LAST = 0.20, 0.50
RMS_ABS = 350.0
RMS_REL = 0.06
HIT_RUN = 3
MARGIN = 0.03
RATE_MIN, RATE_MAX = 0.12, 0.38


def segments():
    paras = [p.strip() for p in SRC_TTS.read_text(encoding="utf-8").split("\n\n")
             if p.strip()]
    return paras


def split():
    SEG_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for i, p in enumerate(segments(), 1):
        (SEG_DIR / ("seg%02d.txt" % i)).write_text(p, encoding="utf-8")
        n = len(p)
        total += n
        print("seg%02d  %4d 字  %.1f–%.1fs  %s"
              % (i, n, n * RATE_MIN, n * RATE_MAX, p[:22]))
    print("共 %d 段，%d 字（含英文标识符）" % (len(segments()), total))


def fetch_one(i, force):
    txt = SEG_DIR / ("seg%02d.txt" % i)
    wav = SEG_DIR / ("seg%02d.wav" % i)
    if wav.exists() and not force:
        print("seg%02d 已存在，跳过" % i)
        return
    cmd = ["node", CJ_JS, str(txt), str(wav), AUDIO_MAN,
           "--profile", PROFILE, "--wait-login", "300"]
    print("[seg%02d] 取音中 ..." % i, flush=True)
    r = subprocess.run(cmd, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, text=True, timeout=300)
    tail = " | ".join(r.stdout.strip().splitlines()[-2:])[:240]
    if r.returncode != 0 or not wav.exists():
        sys.exit("seg%02d 取音失败 exit=%s：%s\n业务 code 非 0 不重复提交，"
                 "先按 skill 排障（10201＝登录态过期）。" % (i, r.returncode, tail))
    with wave.open(str(wav), "rb") as w:
        dur = w.getnframes() / w.getframerate()
    print("seg%02d OK %.2fs  %s" % (i, dur, tail))


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 \
            and w.getsampwidth() == 2, "格式不符 %s" % path
        pcm = np.frombuffer(w.readframes(w.getnframes()),
                            dtype=np.int16).astype(np.float64)
    return pcm


def rms_profile(pcm):
    n = len(pcm) // FRAME
    fr = pcm[:n * FRAME].reshape(n, FRAME)
    return np.sqrt(np.mean(fr ** 2, axis=1))


def trim_edges(pcm):
    prof = rms_profile(pcm)
    thr = max(RMS_ABS, RMS_REL * float(np.sqrt(np.mean(pcm ** 2))))
    hit = prof > thr
    runs = np.convolve(hit.astype(int), np.ones(HIT_RUN, dtype=int),
                       mode="same") >= HIT_RUN
    idx = np.nonzero(runs)[0]
    if len(idx) == 0:
        raise ValueError("整段无能量超门限")
    a = max(0, idx[0] * FRAME - int(MARGIN * SR))
    b = min(len(pcm), (idx[-1] + 1) * FRAME + int(MARGIN * SR))
    return pcm[a:b], a / SR, (len(pcm) - b) / SR


def write_wav(path, pcm):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.round(np.clip(pcm, -32768, 32767))
                      .astype(np.int16).tobytes())


def build():
    paras = segments()
    n = len(paras)
    pieces = []
    report = []
    for i, p in enumerate(paras, 1):
        wav = SEG_DIR / ("seg%02d.wav" % i)
        if not wav.exists():
            sys.exit("缺 seg%02d.wav，先 fetch" % i)
        pcm, head_cut, tail_cut = trim_edges(read_wav(wav))
        pre = HEAD_FIRST if i == 1 else HEAD
        post = TAIL_LAST if i == n else TAIL
        pieces.append(np.zeros(int(pre * SR)))
        pieces.append(pcm)
        pieces.append(np.zeros(int(post * SR)))
        dur = len(pcm) / SR
        rate = dur / len(p)
        flag = "" if RATE_MIN <= rate <= RATE_MAX else "  ★语速出区间"
        report.append((i, dur, len(p), rate, head_cut, tail_cut, flag))
    master = np.concatenate(pieces)
    MEDIA.mkdir(exist_ok=True)
    write_wav(MASTER, master)
    for i, dur, chars, rate, hc, tc, flag in report:
        print("seg%02d 内容 %5.2fs  %3d 字  %.3fs/字  裁头%.2f 裁尾%.2f%s"
              % (i, dur, chars, rate, hc, tc, flag))
    total = len(master) / SR
    print("母带 %s：%.2fs（%.1f 分钟），%d 段" % (MASTER.name, total, total / 60, n))


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd = args[0]
    if cmd == "split":
        split()
    elif cmd == "fetch":
        rest = args[1:]
        force = False
        if rest and rest[0] == "--force":
            force = True
            rest = rest[1:]
        SEG_DIR.mkdir(parents=True, exist_ok=True)
        if not rest:
            rest = ["%02d" % i for i in range(1, len(segments()) + 1)]
        for s in rest:
            fetch_one(int(s), force)
    elif cmd == "build":
        build()
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
