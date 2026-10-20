# -*- coding: utf-8 -*-
"""hf-07 母带段级重建（换主角：CSS 黑户 → setInterval 自掐表，2026-10-20）。

新稿 22 段中 11 段叙事翻转，蝉镜试听 0 豆逐段重合成（build/resynth/segNN.wav，
NN＝新段号 02/04/07/08/09/12/15/16/18/19/20）；其余 11 段逐字未改，从旧母带
（CSS 版，先备份为 media/hf-07-yeyang-old-css.wav）按旧 cues 段界切出复用。

与 hf-05 patch_audio 的区别：那次是窗内同长替换（总时长不变、视频流 copy）；
本集新增整段（慢表段）、11 段重录，总时长变，故整母带重建，随后整体重跑
transcribe→align→cues（旧 cues 不沿用）。

前置冻结件（build/ gitignored；2026-10-20 从 v2 提交前主干导出，重跑必备）：
  git show HEAD:videos/projects/hf-07/src/hf-07-src.txt  > build/old-src.txt
  git show HEAD:videos/projects/hf-07/cues/cues.json     > build/old-cues.json
v2 合入后 HEAD 即新版，需要重跑得从合入前的 commit（本 PR）取这两个文件。

旧段窗＝旧 cues 中该段首句 s 与末句 e，再向相邻段 gap 中点外扩（共享边界处
中点即边界本身）；新段＝蝉镜整段 wav。两者统一过 trim_edges：20ms 帧 RMS
门限找能量边界（连续 3 帧过门限才认，防呼吸噪声），段内停顿一律不碰。

拼接节奏：每段内容前 HEAD、后 TAIL 静音（段间 = HEAD+TAIL = 0.34s，取旧母带
20 个段界 gap 实测均值 0.32 与句间 p90 0.41 之间）；全片头 0.20s、片尾 0.50s。

用法：
  python oneoffs/rebuild_audio.py dry     # 只打印每段裁边/时长/语速，不写文件
  python oneoffs/rebuild_audio.py go      # 备份旧母带后写 media/hf-07-yeyang.wav
"""
import json
import re
import shutil
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"
BUILD = ROOT / "build"
OLD_CUES = BUILD / "old-cues.json"
OLD_SRC = BUILD / "old-src.txt"
RESYNTH = BUILD / "resynth"
OLD_MASTER = MEDIA / "hf-07-yeyang.wav"
BACKUP = MEDIA / "hf-07-yeyang-old-css.wav"

SR = 24000
FRAME = int(0.02 * SR)          # 20ms RMS 帧
HEAD, TAIL = 0.14, 0.20         # 每段内容前/后静音（段间合计 0.34s）
HEAD_FIRST, TAIL_LAST = 0.20, 0.50
RMS_ABS = 350.0                 # int16 绝对门限（蝉镜底噪近 0）
RMS_REL = 0.06                  # 相对全段 RMS 的比例门限
HIT_RUN = 3                     # 连续 3 帧超门限才认能量边界
MARGIN = 0.03                   # 能量边界外留 30ms
RATE_MIN, RATE_MAX = 0.12, 0.38  # 每归一化字符秒数合理区间

# (新段号 1..22, 来源)；old:N＝旧稿第 N 段；new＝build/resynth/segNN.wav
PLAN = [
    (1, "old:1"), (2, "new"), (3, "old:3"), (4, "new"), (5, "old:5"),
    (6, "old:6"), (7, "new"), (8, "new"), (9, "new"), (10, "old:9"),
    (11, "old:10"), (12, "new"), (13, "old:12"), (14, "old:13"),
    (15, "new"), (16, "new"), (17, "old:16"), (18, "new"), (19, "new"),
    (20, "new"), (21, "old:20"), (22, "old:21"),
]


def read_wav(path):
    w = wave.open(str(path), "rb")
    assert w.getframerate() == SR and w.getnchannels() == 1 \
        and w.getsampwidth() == 2, "格式不符 %s" % path
    pcm = np.frombuffer(w.readframes(w.getnframes()),
                        dtype=np.int16).astype(np.float64)
    w.close()
    return pcm


def write_wav(path, pcm):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(np.round(np.clip(pcm, -32768, 32767))
                      .astype(np.int16).tobytes())


def rms_profile(pcm):
    n = len(pcm) // FRAME
    if n == 0:
        return np.zeros(0)
    fr = pcm[:n * FRAME].reshape(n, FRAME)
    return np.sqrt(np.mean(fr ** 2, axis=1))


def trim_edges(pcm):
    """返回（内容 PCM, 头裁秒, 尾裁秒）。连续 HIT_RUN 帧超门限为能量界。"""
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


def find_valley(pcm, t_center, half=0.25, floor=600.0, min_run=3):
    """在 t_center±half 内找最深段间静音谷：连续 ≥min_run 帧 RMS<floor 的
    区间，取离 center 最近者的中点（秒）。找不到则退回 center。

    为什么不用 cue gap 中点：相邻 cue 共享同一时间戳时（如旧 5/6、9/10 段
    界 e==s），中点压在尾音上——实测尾音越过界点 0.12s、真正的谷在界点
    后 0.14–0.46s。谷中落刀保证尾音与首字都完整。"""
    c = int(t_center * SR)
    lo = max(0, c - int(half * SR))
    hi = min(len(pcm), c + int(half * SR))
    n = (hi - lo) // FRAME
    fr = pcm[lo:lo + n * FRAME].reshape(n, FRAME)
    prof = np.sqrt(np.mean(fr ** 2, axis=1))
    quiet = prof < floor
    runs, k = [], 0
    while k < n:
        if quiet[k]:
            j = k
            while j < n and quiet[j]:
                j += 1
            if j - k >= min_run:
                runs.append((k, j))
            k = j
        else:
            k += 1
    if not runs:
        return t_center
    # 区间中点离 center 最近者；并列取 RMS 更低者
    def score(r):
        mid = (r[0] + r[1]) / 2 * FRAME + lo
        d = abs(mid / SR - t_center)
        v = float(np.mean(prof[r[0]:r[1]]))
        return (round(d, 3), v)
    a, b = min(runs, key=score)
    return ((a + b) / 2 * FRAME + lo) / SR


def old_segment_windows(master):
    """旧稿 21 段 → 母带采样窗 {段号: (起样本, 止样本)}。

    段文本归一化后在旧 cues 拼接流中顺序定位；内部窗界不按 cue gap 中点，
    而在 ±0.25s 内找静音谷中心（共享时间戳处中点会压在尾音上）。"""
    old = OLD_SRC.read_text(encoding="utf-8")
    oparas = [p.strip() for p in old.split("\n\n") if p.strip()]
    assert len(oparas) == 21
    cues = json.loads(OLD_CUES.read_text(encoding="utf-8"))["cues"]
    norm = lambda s: re.sub(r"[^一-鿿A-Za-z0-9]", "", s)
    parts = [norm(c["t"]) for c in cues]
    stream = "".join(parts)
    offs, acc = [], 0
    for t in parts:
        offs.append((acc, acc + len(t)))
        acc += len(t)

    def cue_at(pos):
        for k, (a, b) in enumerate(offs):
            if a <= pos < b:
                return k
        return len(cues) - 1

    segs = []
    pos = 0
    for i, p in enumerate(oparas, start=1):
        key = norm(p)
        j = stream.find(key, pos)
        assert j >= 0, "旧段 %d 定位失败" % i
        pos = j + len(key)
        segs.append((cue_at(j), cue_at(pos - 1)))

    # 内部边界时刻＝相邻 cue 的 gap 中点；再找谷微调
    bounds = [0.0]
    for i in range(20):
        _, ke = segs[i]
        ks2, _ = segs[i + 1]
        center = (cues[ke]["e"] + cues[ks2]["s"]) / 2
        bounds.append(find_valley(master, center))
    bounds.append(len(master) / SR)

    return {i + 1: (max(0, int(round(bounds[i] * SR))),
                    min(len(master), int(round(bounds[i + 1] * SR))))
            for i in range(21)}


def n_chars_for(new_seg):
    """新段归一化字符数（语速校验用）。"""
    txt = (RESYNTH / ("seg%02d.txt" % new_seg)).read_text(encoding="utf-8")
    return len(re.sub(r"[^一-鿿A-Za-z0-9]", "", txt))


def main():
    go = len(sys.argv) > 1 and sys.argv[1] == "go"
    # 旧段切割源永远是 CSS 版备份：首次 go 之后 OLD_MASTER 已被 v2 覆盖，
    # 再读它会把新母带当旧母带切。
    src_master = BACKUP if BACKUP.exists() else OLD_MASTER
    master = read_wav(src_master)
    windows = old_segment_windows(master)

    pieces = []
    content_n = 0
    print("段  来源     内容秒   原首静  原尾静   字  秒/字")
    for k, (seg, src) in enumerate(PLAN):
        if src == "new":
            raw = read_wav(RESYNTH / ("seg%02d.wav" % seg))
            chars = n_chars_for(seg)
            tag = "new%02d" % seg
        else:
            n = int(src.split(":")[1])
            a, b = windows[n]
            raw = master[a:b]
            chars = None
            tag = "old%02d" % n
        body, lt, rt = trim_edges(raw)
        dur = len(body) / SR
        rate = dur / chars if chars else float("nan")
        if chars and not (RATE_MIN <= rate <= RATE_MAX):
            print("  ⚠ %s 语速越界 %.3f 秒/字（%d 字 %.2fs）"
                  % (tag, rate, chars, dur))
        print("%2d  %-6s  %6.2f  %6.2f %6.2f  %4s  %.3f"
              % (seg, tag, dur, lt, rt,
                 chars if chars else "-", rate))
        hp = HEAD_FIRST if k == 0 else HEAD
        tp = TAIL_LAST if k == len(PLAN) - 1 else TAIL
        content_n += len(body)
        pieces.append(np.concatenate([
            np.zeros(int(hp * SR)), body, np.zeros(int(tp * SR))]))

    out = np.concatenate(pieces)
    total = len(out) / SR
    print("母带总时长 %.2fs（内容 %.2fs，22 段，源旧母带 %.2fs）"
          % (total, content_n / SR, len(master) / SR))

    if not go:
        print("dry-run 完成（源：%s）；确认后 go 写盘（旧母带先备份）"
              % src_master.name)
        return
    if not BACKUP.exists():
        shutil.copyfile(OLD_MASTER, BACKUP)
        print("旧母带备份 → %s" % BACKUP.name)
    write_wav(OLD_MASTER, out)
    print("→ %s（%.2fs）" % (OLD_MASTER.relative_to(ROOT), total))


if __name__ == "__main__":
    main()
