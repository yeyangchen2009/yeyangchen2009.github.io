# -*- coding: utf-8 -*-
"""hf-05 成片音频外科补丁（两条，从原始母带一次重建）。

沿 hf-02/03 patch_hang_yin 工艺：蝉镜克隆音色个别字音/缩写念错，字幕烧的是
正确书面字、画面无错误，重 render 要 69 分钟且改视频流，故只在母带音轨 PCM
上做句级替换——同音色整句重合成，窗界沿 20ms RMS 包络在句外停顿谷底定界，
补丁 atempo 到窗长，两端 12ms 余弦 crossfade，窗外采样逐样本不动（断言）。

补丁 1 · WCAG（230.26–236.92 句）
  蝉镜把 WCAG 当可发音整词读成双音节 wàigé（词段仅 0.34s 客观坐实）。
  空格/点号/顿号/逗号/全角/逐句六种写法均被文本归一化词典锁死；孤立单字母
  合成电平异常。用户人耳终审：逐句版「W。C。A。G。」（q-wcag6）连听可逐字母
  分辨，采用。atempo 0.9949。

补丁 2 · 得到 dé→děi（157.68–159.78 半句「它得到第十三秒才走」）
  「得到」是高频词，蝉镜按 dédào 整词读，而此处 děi dào＝必须到。
  三版候选（逗号破词「它得，到」/得等到/得要到）用户人耳确认均念 děi；
  采用 q-dei1「它得，到第十三秒才走」——与原句同字数（逗号只造停顿），
  字幕逐字高亮零错位。

重封（视频流 -c:v copy；终片音频轴＝正片时间轴，finalize 音频未平移）::

  ffmpeg -i media/hf-05-yeyang-cover.mp4 -i media/hf-05-yeyang-patched.wav \\
      -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart \\
      media/hf-05-yeyang-cover-patched.mp4
"""
import io
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 24000
XFADE = 0.012

# (标签, 补丁 wav, 句起, 句止, 谷搜索半窗)
PATCHES = [
    ("wcag", "build/verify/patch/q-wcag6.wav", 230.26, 236.92, 0.12),
    ("dei1", "build/verify/patch/q-dei1.wav", 157.68, 159.78, 0.12),
]


def read_wav(path):
    w = wave.open(str(path), "rb")
    assert w.getframerate() == SR and w.getnchannels() == 1 \
        and w.getsampwidth() == 2
    pcm = np.frombuffer(w.readframes(w.getnframes()),
                        dtype=np.int16).astype(np.float64)
    w.close()
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
        stdout=subprocess.PIPE, check=True)
    w = wave.open(io.BytesIO(proc.stdout), "rb")
    p = np.frombuffer(w.readframes(w.getnframes()),
                      dtype=np.int16).astype(np.float64)
    if len(p) < target_n:
        p = np.concatenate([p, np.zeros(target_n - len(p))])
    return p[:target_n], tempo


def main():
    out = read_wav(ROOT / "media/hf-05-yeyang.wav")
    master0 = out.copy()
    for tag, rel, s, e, half in PATCHES:
        patch = read_wav(ROOT / rel)
        win_s = valley(out, s, half, "left")
        win_e = valley(out, e, half, "right")
        a, b = int(round(win_s * SR)), int(round(win_e * SR))
        p2, tempo = atempo_to(patch, b - a)
        nf = int(XFADE * SR)
        ramp = 0.5 * (1 - np.cos(np.pi * np.arange(nf) / nf))
        p2 = p2.copy()
        p2[:nf] *= ramp
        p2[-nf:] *= ramp[::-1]
        hole = out[a:b].copy()
        hole[:nf] *= ramp[::-1]
        hole[-nf:] *= ramp
        out[a:b] = hole + p2
        print("%-5s 窗 %.3f–%.3f（%.3fs）补丁 %.3fs atempo %.4f"
              % (tag, win_s, win_e, win_e - win_s, len(patch) / SR, tempo))

    wav_out = ROOT / "media/hf-05-yeyang-patched.wav"
    with wave.open(str(wav_out), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(np.clip(out, -32768, 32767).astype(np.int16).tobytes())
    print("→", wav_out.relative_to(ROOT))


if __name__ == "__main__":
    main()
