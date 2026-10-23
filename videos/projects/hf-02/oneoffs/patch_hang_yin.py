# -*- coding: utf-8 -*-
"""hf-02 成片音频外科补丁：「中间一行标题」的量词「行」被 TTS 误读 xíng →
借音「航」补读 háng。

背景
----
蝉镜克隆音色把「深色底，中间一行标题，安安静静待在那儿」里的「行」读成
xíng（应为 háng；whisper 误识为「中间疫情标题」）。hf-03 已用整小句替换
修过同类三处；本处按同法先合成整句，却发现语速对不上：

- 整句「深色底，中间一航标题，安安静静待在那儿」补丁声 3.665s，原句窗
  4.045s，atempo 0.906（−9.4%）——原片这里是教学强调慢读，蝉镜整句偏快；
- 独立短语「中间一航标题」六字更糟：短句 TTS 念得更快，voiced 1.26s 对
  1.66s 最小物理窗，要放慢 24%。

两种整段方案都破「|Δtempo| ≤ 5%」红线。改用**双字切片**：补丁仍是整句
合成（保句法语调，非孤立短语），但只从整句音里切「一航」两字，替换原片
里同样黏成一段的「一行」（物理上本就是一个声学段，两端是字间谷底）：

    原片窗 278.20–278.57 (0.37s)  ←  切片 q1.wav 1.44–1.81 (0.37s)
    atempo 1.000，两端 12ms 余弦 crossfade

判音证据（20ms Hann 窗＋预加重 rfft 测 F1/F2）：切片「航」韵腹
F1≈715–779/F2≈750–830 接 ŋ 尾（F1 落 217、F2 保持 770），是 háng；
原片对应段无 a 韵腹、仅 45ms 近静音 F2≈2500，是弱读 xíng。

补丁音频复现（蝉镜试听通道，0 蝉豆；绝不点「立即生成」）::

    node ../../../tools/cj-web-tts.js q1.txt build/verify/patch/q1.wav \\
        C-df5d6f1a95904a91a8e086b6f2fd8a53 \\
        --profile /f/Data/Code/gmeek-site/Temp/cj-profile

q1.txt 内容（行→航，整句合成以保自然语调，脚本只切其中两字）::

    深色底，中间一航标题，安安静静待在那儿。

两域时间轴不同：24k 母带 media/audio.wav 是 body 原声；终片是旧版
「封面 2s 静音＋body」，故 48k 终片轨窗坐标整体 +2.0s（280.20–280.57）。
终片轨先抽出::

    ffmpeg -y -i media/hf-02-yeyang-cover.mp4 -vn -ac 2 -ar 48000 \\
        -c:a pcm_s16le build/verify/final.wav

输出
----
- build/verify/final-patched.wav      48k stereo，拿去与终片视频流 -c:v copy 重封
- media/audio-patched.wav             24k mono，补丁母带留档（供日后重 render）

重封命令::

    ffmpeg -i media/hf-02-yeyang-cover.mp4 -i build/verify/final-patched.wav \\
        -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -movflags +faststart \\
        media/hf-02-yeyang-cover-patched.mp4
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent  # 项目根（oneoffs/ 的上一级）
SR_MASTER, SR_FINAL = 24000, 48000
XFADE = 0.012  # 两端余弦交叉淡变 12ms

# (补丁wav, 补丁内切片起秒, 切片有效长, 母带轴窗起, 母带轴窗止)
# 补丁是整句合成，1.44–1.81 即整句中的「一航」两字（跳过 TTS 自加的
# schwa 起势；中文「间一」本就是 n→i 直连，不要那个过渡）。
PATCHES = [
    ("q1.wav", 1.44, 0.37, 278.20, 278.57),
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
    """蝉镜补丁 wav → 切片 → atempo → 目标规格 → 精确窗长 numpy 数组。"""
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
    print("  %s atempo=%.4f 精修 %d→%d → %d 样本（窗 %.2fs）"
          % (name, tempo, n, target, target, win_e - win_s))
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

    # (源, 采样率, 声道, 目标, 相对母带轴的秒偏移——旧版终片前有 2s 封面静音)
    jobs = [
        ("build/verify/final.wav", SR_FINAL, 2,
         "build/verify/final-patched.wav", 2.0),
        ("media/audio.wav", SR_MASTER, 1,
         "media/audio-patched.wav", 0.0),
    ]
    for src_rel, sr, ch, dst_rel, off in jobs:
        print("手术 %s（%dHz %dch，轴偏移 %+.1fs）" % (src_rel, sr, ch, off))
        base, sr_got, ch_got = read_wav(ROOT / src_rel)
        assert (sr_got, ch_got) == (sr, ch)
        total0 = base.shape[0]
        out = base
        windows = []
        for name, head, voiced, ws, we in PATCHES:
            patch = synth_patch(name, head, voiced, ws, we, sr, ch, tmpdir)
            start = round((ws + off) * sr)
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
        # 断言：总长不变；且改动只发生在补丁窗内
        assert out.shape[0] == total0, "总长被改变！"
        changed = np.any(out != base, axis=1) if ch > 1 else (out != base)
        assert changed.any(), "没有任何改动"
        # 严格区间检查：所有改动样点必须落在补丁窗并集内
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
