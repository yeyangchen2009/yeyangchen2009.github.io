# -*- coding: utf-8 -*-
"""hf-08 母带音频外科补丁（从原始母带一次重建）。

录屏母带入镜尾报是 rendered in 54.2s（录制与抓帧并行口径，RECORD-NOTES
第十一节），而蝉镜首录音频念「五十二秒」（探针日无录屏口径 52.4s）。
重 render 改视频流代价大且此处只差一个数字，故只在母带音轨 PCM 上做句级
替换——同音色整句重合成，窗界沿 20ms RMS 包络在句外停顿谷底定界，补丁
atempo 到窗长，两端 12ms 余弦 crossfade，窗外采样逐样本不动（断言）。

工艺勘误（对 hf-05 patch_audio.py）：hf-05 写法 hole 只淡化两端 12ms、
中段保留原音 100% 再与补丁相加，即窗中段两路念白全程叠加；其 atempo
0.9949 近同步、同文叠加近似加倍响度才蒙混过耳。本集 atempo 1.0425 失步
更快，同窗 whisper base 转写整段糊成乱码（「抓抓珍珠」）实证此患。本脚本
改为真正的交叉淡化：窗中段＝纯补丁，两端 12ms 线性（余弦）互补混合。

补丁 · 硬件路五十四秒（cues 窗 267.26–271.02）
  新音 build/patch/q-54a.wav：蝉镜网页「试听」通道 0 蝉豆重取整句
  「硬件路五十四秒，编码和抓帧重叠在一起。」（cj-web-tts.js，叶扬音色
  audio_man C-df5d6f1a…，绝不点「立即生成」），18 字内容 3.760s。
  母带谷底实窗 267.240–271.120＝3.880s，atempo 1.0425（≤5% 无感区）。
  注意双口径并存：布景日志 logs/hw-a.log 尾报 52.4s 是探针日历史锚点
  （check_anchors/run_rehearsal 校验，不改），本补丁只对齐入镜母带 54.2s。

输出 media/hf-08-yeyang-patched.wav；make_video 音频引用指向 patched，
cues.json 该句字幕 t 改「硬件路五十四秒」，时间戳不动（等窗替换不挪轴）。

sw「软件路首跑六十八秒」暂不补：等冷态 t0 母带真机尾报，若不是 68s 再
追加一条同工艺补丁（PATCHES 加一行即可）。
"""
import io
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 24000
XFADE = 0.012

# (标签, 补丁 wav, 句起, 句止, 谷搜索半窗)
PATCHES = [
    ("q54", "build/patch/q-54a.wav", 267.26, 271.02, 0.12),
]


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1 \
            and w.getsampwidth() == 2, "格式不符 %s" % path
        pcm = np.frombuffer(w.readframes(w.getnframes()),
                            dtype=np.int16).astype(np.float64)
    return pcm


def valley(x, center, half, side):
    """句外停顿谷：side=left 搜 [center-half, center]，right 搜
    [center, center+half]。谷在句外，窗要包住整句。"""
    n = int(0.02 * SR)
    c = int(center * SR)
    if side == "left":
        lo, hi = max(0, c - int(half * SR)), c
    else:
        lo, hi = c, min(len(x), c + int(half * SR))
    best, best_v = c, 1e9
    i = lo
    while i + n <= hi:
        v = np.sqrt(np.mean(x[i:i+n]**2))
        if v < best_v:
            best, best_v = i, v
        i += n // 2
    return best / SR


def atempo_to(patch, target_n):
    tempo = len(patch) / target_n
    proc = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR),
         "-ac", "1", "-i", "pipe:0", "-af", "atempo=%.5f" % tempo,
         "-f", "wav", "-c:a", "pcm_s16le", "-"],
        input=patch.astype(np.int16).tobytes(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    w = wave.open(io.BytesIO(proc.stdout), "rb")
    p = np.frombuffer(w.readframes(w.getnframes()),
                      dtype=np.int16).astype(np.float64)
    if len(p) < target_n:
        p = np.concatenate([p, np.zeros(target_n - len(p))])
    return p[:target_n], tempo


def main():
    src = ROOT / "media" / "hf-08-yeyang.wav"
    out = ROOT / "media" / "hf-08-yeyang-patched.wav"
    audio = read_wav(src)
    original = audio.copy()
    for tag, rel, s, e, half in PATCHES:
        patch = read_wav(ROOT / rel)
        win_s = valley(audio, s, half, "left")
        win_e = valley(audio, e, half, "right")
        a, b = int(round(win_s * SR)), int(round(win_e * SR))
        p2, tempo = atempo_to(patch, b - a)
        nf = int(XFADE * SR)
        ramp = 0.5 * (1 - np.cos(np.pi * np.arange(nf) / nf))
        # 真交叉淡化：中段纯补丁；左端原音 1→0、补丁 0→1，右端反之。
        # （hf-05 旧写法中段两路相加＝叠加念白，atempo 偏差大时糊。）
        orig_win = audio[a:b].copy()
        p2 = p2.copy()
        orig_win[:nf] *= ramp[::-1]
        orig_win[nf:-nf] = 0.0
        orig_win[-nf:] *= ramp
        p2[:nf] *= ramp
        p2[-nf:] *= ramp[::-1]
        audio[a:b] = orig_win + p2
        print("%-5s 窗 %.3f–%.3f（%.3fs）补丁 %.3fs atempo %.4f"
              % (tag, win_s, win_e, win_e - win_s, len(patch) / SR, tempo))

    # 窗外逐样本不动：除所有补丁窗并集外，PCM 必须与原母带完全一致
    mask = np.ones(len(audio), dtype=bool)
    for _, _, s, e, half in PATCHES:
        a = int(round(valley(original, s, half, "left") * SR))
        b = int(round(valley(original, e, half, "right") * SR))
        mask[a:b] = False
    if not np.array_equal(audio[mask], original[mask]):
        sys.exit("断言失败：窗外采样发生变化")
    print("窗外逐样本不动：OK（%d 样本受保护）" % int(mask.sum()))

    with wave.open(str(out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.clip(audio, -32768, 32767).astype(np.int16).tobytes())
    print("→", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
