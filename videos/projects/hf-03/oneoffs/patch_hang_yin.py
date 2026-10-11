# -*- coding: utf-8 -*-
"""hf-03 成片音频外科补丁：3 处「一行」被 TTS 误读 yìxíng → 借音「航」补读 háng。

背景
----
蝉镜克隆音色把「一行副标题 / 后一行 / 一行脚本」里的量词「行」读成 xíng
（应为 háng）。字幕烧的是正确书面字、画面无任何错误，重 render 要 22 分钟且
会改动视频流，故只在**终片音轨 PCM** 上做句级替换：同音色借同音字「航」
（háng，无歧读）合成整小句，atempo 微调到原句等长后，在停顿谷底换片。

补丁音频复现（蝉镜试听通道，0 蝉豆；绝不点「立即生成」）::

    node ../../../tools/cj-web-tts.js qN.txt build/verify/patch/qN.wav \\
        C-df5d6f1a95904a91a8e086b6f2fd8a53 \\
        --profile /f/Data/gmeek-site/Temp/cj-profile

三个 qN.txt 内容（行→航）::

    q1 = 一航副标题，灰色小字
    q2 = 标题标签的后一航
    q3 = 从头到尾没写过一航脚本

替换窗（成片时间轴＝母带时间轴；由 build/16k.wav 20ms 能量包络在停顿谷底
人工定界，48k/24k 下均为整数采样）与补丁有效语音段（-26dB 门限）::

    q1  窗 141.33–143.51 (2.18s)  补丁声 0.00–2.26 (2.26s)  atempo 1.037
    q2  窗 155.89–157.62 (1.73s)  补丁声 0.00–1.68 (1.68s)  atempo 0.971
    q3  窗 211.22–213.42 (2.20s)  补丁声 0.06–2.37 (2.31s)  atempo 1.050

|Δtempo| 全部 < 5%，听感无变速。窗两端各 12ms 余弦 crossfade，窗外采样逐样本
不动（脚本自带断言）。

输出
----
- build/verify/final-patched.wav      48k stereo，拿去与终片视频流 -c:v copy 重封
- media/hf-03-yeyang-patched.wav      24k mono，补丁母带留档（供日后重 render）

重封命令::

    ffmpeg -i media/hf-03-yeyang-cover.mp4 -i build/verify/final-patched.wav \\
        -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart \\
        media/hf-03-yeyang-cover-patched.mp4
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent  # 项目根（oneoffs/ 的上一级）
SR_MASTER, SR_FINAL = 24000, 48000
XFADE = 0.012  # 两端余弦交叉淡变 12ms

# (补丁wav, 补丁头裁秒, 补丁有效声长, 窗起, 窗止)
PATCHES = [
    ("q1.wav", 0.00, 2.26, 141.33, 143.51),
    ("q2.wav", 0.00, 1.68, 155.89, 157.62),
    ("q3.wav", 0.06, 2.31, 211.22, 213.42),
]


def read_wav(path):
    import wave
    w = wave.open(str(path), "rb")
    assert w.getsampwidth() == 2, "只支持 s16le"
    sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
    if ch > 1:
        pcm = pcm.reshape(-1, ch)
    return pcm, sr, ch


def write_wav(path, pcm, sr, ch):
    import wave
    if pcm.ndim == 1:
        data = pcm
    else:
        data = pcm.reshape(-1)
    data = np.clip(np.round(data), -32768, 32767).astype(np.int16)
    w = wave.open(str(path), "wb")
    w.setnchannels(ch)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(data.tobytes())
    w.close()


def synth_patch(name, head, voiced, win_s, win_e, sr_out, ch_out, tmpdir):
    """蝉镜补丁 wav → 去头 → atempo → 目标规格 → 精确窗长 numpy 数组。"""
    src = ROOT / "build" / "verify" / "patch" / name
    tempo = voiced / (win_e - win_s)
    out = tmpdir / ("%s-%d.wav" % (src.stem, sr_out))
    # -ss/-t 输入定位（24k 整数采样边界）；atempo 保调变速；重采样/转声道
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-ss", "%.3f" % head, "-t", "%.3f" % voiced, "-i", str(src),
         "-af", "atempo=%.6f" % tempo,
         "-ar", str(sr_out), "-ac", str(ch_out), "-c:a", "pcm_s16le",
         str(out)],
        check=True)
    pcm, sr, ch = read_wav(out)
    target = round((win_e - win_s) * sr_out)
    n = pcm.shape[0]
    # atempo 滤波器有毫秒级尾延迟，残差一律线性精修到逐采样等长；
    # 残差 >2% 说明粗调异常，叫停人工看。
    if abs(n - target) / target > 0.02:
        sys.exit("%s atempo 后 %d 样本，离目标 %d 超 2%%，需人工检查"
                 % (name, n, target))
    if n != target:
        x_old = np.linspace(0.0, 1.0, n)
        x_new = np.linspace(0.0, 1.0, target)
        if pcm.ndim == 1:
            pcm = np.interp(x_new, x_old, pcm)
        else:
            pcm = np.stack([np.interp(x_new, x_old, pcm[:, c])
                            for c in range(ch)], axis=1)
    total_ratio = (target / (round(voiced * sr_out)))  # 窗长/原有效声长＝总拉伸
    print("  %s atempo=%.4f 精修 %d→%d，总变速 %.1f%% → %d 样本（窗 %.2fs）"
          % (name, tempo, n, target, (total_ratio - 1) * 100, target, win_e - win_s))
    return pcm


def splice(base, patch, start, sr, ch):
    """在 start 样点处用 patch 覆写，两端 XFADE 秒余弦交叉。返回新数组。"""
    out = base.copy()
    n = patch.shape[0]
    k = int(XFADE * sr)
    g = (1.0 - np.cos(np.linspace(0.0, np.pi / 2, k)))  # 0→1
    fade_in, fade_out = g, g[::-1]

    # 入端交叉
    if ch == 1:
        out[start:start + k] = base[start:start + k] * (1 - fade_in) + patch[:k] * fade_in
    else:
        out[start:start + k, :] = (base[start:start + k, :] * (1 - fade_in)[:, None]
                                   + patch[:k, :] * fade_in[:, None])
    # 中段直盖
    out[start + k:start + n - k] = patch[k:n - k]
    # 出端交叉
    end = start + n
    if ch == 1:
        out[end - k:end] = (base[end - k:end] * fade_out
                            + patch[n - k:n] * (1 - fade_out))
    else:
        out[end - k:end, :] = (base[end - k:end, :] * fade_out[:, None]
                               + patch[n - k:n, :] * (1 - fade_out)[:, None])
    return out


def run():
    tmpdir = ROOT / "build" / "verify" / "patch" / "work"
    tmpdir.mkdir(parents=True, exist_ok=True)

    jobs = [
        ("build/verify/final.wav", SR_FINAL, 2,
         "build/verify/final-patched.wav"),
        ("media/hf-03-yeyang.wav", SR_MASTER, 1,
         "media/hf-03-yeyang-patched.wav"),
    ]
    for src_rel, sr, ch, dst_rel in jobs:
        print("手术 %s（%dHz %dch）" % (src_rel, sr, ch))
        base, sr_got, ch_got = read_wav(ROOT / src_rel)
        assert (sr_got, ch_got) == (sr, ch)
        total0 = base.shape[0]
        out = base
        windows = []
        for name, head, voiced, ws, we in PATCHES:
            patch = synth_patch(name, head, voiced, ws, we, sr, ch, tmpdir)
            start = round(ws * sr)
            n = patch.shape[0]
            # 蝉镜单句合成电平与整篇母带不一致：按窗内原音 RMS 匹配响度
            old_seg = base[start:start + n]
            g = float(np.sqrt(np.mean(old_seg.astype(np.float64) ** 2))
                      / np.sqrt(np.mean(patch ** 2)))
            if not 0.5 <= g <= 2.0:
                sys.exit("%s 响度增益 %.3f 超出 0.5–2.0，人工检查" % (name, g))
            peak = np.max(np.abs(patch * g))
            assert peak < 32760, "%s 增益后削波（峰 %.0f）" % (name, peak)
            patch = patch * g
            print("    响度匹配 ×%.3f（%+.1f dB），增益后峰 %.0f"
                  % (g, 20 * np.log10(g), peak))
            out = splice(out, patch, start, sr, ch)
            windows.append((start, start + n, name))
        # 断言：总长不变；且改动只发生在三个窗内
        assert out.shape[0] == total0, "总长被改变！"
        changed = np.any(out != base, axis=1) if ch > 1 else (out != base)
        assert changed.any(), "没有任何改动"
        # 严格区间检查：所有改动样点必须落在三窗并集内
        union = np.zeros_like(changed)
        for a, b, _ in windows:
            union[a:b] = True
        outside = changed & ~union
        assert not outside.any(), "窗外有 %d 个样点被改动" % outside.sum()
        write_wav(ROOT / dst_rel, out, sr, ch)
        print("  → %s（总长不变 %d 样本，改动仅 %d 窗）\n"
              % (dst_rel, total0, len(windows)))


if __name__ == "__main__":
    run()
