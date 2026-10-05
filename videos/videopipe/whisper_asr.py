# -*- coding: utf-8 -*-
"""faster-whisper 转录封装：词级时间戳，CPU/int8 单例。

raw JSON 格式与历史 transcribe-*.py 输出逐键兼容，便于复用既有
raw 文件与对齐脚本。
"""
import json
from dataclasses import dataclass, field

_MODEL = None


@dataclass
class Word:
    w: str
    s: float
    e: float


@dataclass
class Segment:
    s: float
    e: float
    t: str
    words: list = field(default_factory=list)


@dataclass
class Transcript:
    duration: float
    segments: list = field(default_factory=list)   # list[Segment]

    def to_raw(self) -> dict:
        return {
            "duration": self.duration,
            "segments": [
                {"s": round(g.s, 3), "e": round(g.e, 3), "t": g.t,
                 "words": [{"w": w.w, "s": round(w.s, 3),
                            "e": round(w.e, 3)} for w in g.words]}
                for g in self.segments],
        }


def _get_model(model_size):
    global _MODEL
    if _MODEL is None or _MODEL[0] != model_size:
        from faster_whisper import WhisperModel
        _MODEL = (model_size,
                  WhisperModel(model_size, device="cpu", compute_type="int8"))
    return _MODEL[1]


def transcribe(pcm, duration, *, model_size="base", beam_size=5,
                vad_filter=False, condition_on_previous_text=True,
                time_offset=0.0, language="zh") -> Transcript:
    """对 np.float32 PCM（16kHz）转录，返回 Transcript。

    time_offset: 对所有词/段时间整体平移（切片转录复用）。
    duration: 源音频总时长（写入 raw，不由 PCM 推断）。
    """
    model = _get_model(model_size)
    segments, info = model.transcribe(
        pcm, language=language, beam_size=beam_size,
        word_timestamps=True, vad_filter=vad_filter,
        condition_on_previous_text=condition_on_previous_text)

    out = []
    for seg in segments:
        words = []
        if seg.words:
            for w in seg.words:
                words.append(Word(w.word,
                                  round(w.start + time_offset, 3),
                                  round(w.end + time_offset, 3)))
        out.append(Segment(round(seg.start + time_offset, 3),
                           round(seg.end + time_offset, 3),
                           seg.text.strip(), words))
    tr = Transcript(duration=duration, segments=out)
    tr.info = info        # 语言/概率等诊断信息，供 oneoff 打印
    return tr


def save_raw(tr: Transcript, path) -> None:
    with open(str(path), "w", encoding="utf-8") as f:
        json.dump(tr.to_raw(), f, ensure_ascii=False, indent=1)


def load_raw(path) -> Transcript:
    """读历史 raw 文件（dict）→ Transcript。"""
    raw = json.load(open(str(path), encoding="utf-8"))
    segs = []
    for g in raw["segments"]:
        segs.append(Segment(
            g["s"], g["e"], g["t"],
            [Word(w["w"], w["s"], w["e"]) for w in g.get("words", [])]))
    return Transcript(duration=raw.get("duration", 0.0), segments=segs)
