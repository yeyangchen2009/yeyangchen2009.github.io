# -*- coding: utf-8 -*-
"""音频读写：ffmpeg 转 16k 单声道、PCM 读取、ffprobe 时长。

用标准库 wave 读 16kHz PCM 再转 np.float32，绕开 PyAV 0.19 与
faster-whisper 的二进制不兼容（五片实测可行路径）。
"""
import json
import subprocess

import numpy as np

SR16 = 16000


def to_16k_mono(src, dst) -> None:
    """任意输入 → 16kHz / mono / pcm_s16le wav。"""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-ar", str(SR16), "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
        check=True)


def read_pcm16(path) -> np.ndarray:
    """读 16kHz mono PCM wav，返回 np.float32（/32768）。"""
    import wave
    with wave.open(str(path), "rb") as wf:
        pcm = np.frombuffer(wf.readframes(wf.getnframes()),
                            np.int16).astype(np.float32) / 32768.0
    return pcm


def probe_duration(path) -> float:
    """ffprobe 取时长（秒）。"""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True).stdout
    return float(json.loads(out)["format"]["duration"])
