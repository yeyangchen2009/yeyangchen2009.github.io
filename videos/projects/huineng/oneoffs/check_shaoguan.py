# -*- coding: utf-8 -*-
"""用 small 模型重转「韶关」句，裁决 TTS 是否把 sháo 读成别的音。

base 模型把「韶关」听成「勞官」，但同句「曹溪」也被误听成「潮西」，
故单靠 base 不足为凭。用法: python oneoffs/check_shaoguan.py
"""
import wave

import numpy as np
from faster_whisper import WhisperModel

WAV = "build/shaoguan.wav"

# 直接喂 PCM 数组：本机 PyAV 版本旧，av.open 不兼容 metadata_errors
wf = wave.open(WAV, "rb")
pcm = np.frombuffer(wf.readframes(wf.getnframes()),
                    dtype=np.int16).astype(np.float32) / 32768.0

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(pcm, beam_size=5, language="zh")
for seg in segments:
    print("[%.2f-%.2f] %s" % (seg.start, seg.end, seg.text))
