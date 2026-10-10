# -*- coding: utf-8 -*-
"""videopipe —— 视频工作流公共包（深模块：接口小、内部厚）。

按管线阶段组织再导出：
  config   常量 / 路径
  page     HTML 外壳
  theme    主题 / CSS 装配
  scene    场景 clip
  subtitle 字幕轨道
  audioio / whisper_asr / align / cues  音频→对齐后端
  concat   封面头 / 拼接
  verify   结构 / 零差异对比
"""
from . import config
from .config import ProjectPaths
from .page import render_page, audio_tag, stage_gsap
from .theme import (Theme, assemble_css, DARK_GOLD_GH, DUNHUANG_WARM,
                    XUANZHI, SILK_PRO, DARK_GOLD_XJ, THEMES)
from .scene import Scene, render_scenes, scene_fade_js
from .subtitle import (Fragments, char_track, CenterTrack, SentenceTrack,
                       center_char_clips, sentence_track)
from .audioio import to_16k_mono, read_pcm16, probe_duration
from .whisper_asr import (Word, Segment, Transcript, transcribe,
                          save_raw, load_raw)
from .align import Scores, Alignment, align, check_report, HAN_RE
from .cues import (group_cues, enforce_monotonic, build_cues_json,
                   save_cues, load_cues, to_srt, write_srt)
from .concat import make_cover_head, concat_copy, finalize_concat
from .verify import structure, compare
from .cover import (CoverLayout, render_cover, RULER_LEFT, BOX_RIGHT)

__all__ = [
    "config", "ProjectPaths",
    "render_page", "audio_tag", "stage_gsap",
    "Theme", "assemble_css", "DARK_GOLD_GH", "DUNHUANG_WARM", "XUANZHI",
    "SILK_PRO", "DARK_GOLD_XJ", "THEMES",
    "Scene", "render_scenes", "scene_fade_js",
    "Fragments", "char_track", "CenterTrack", "SentenceTrack",
    "center_char_clips", "sentence_track",
    "to_16k_mono", "read_pcm16", "probe_duration",
    "Word", "Segment", "Transcript", "transcribe", "save_raw", "load_raw",
    "Scores", "Alignment", "align", "check_report", "HAN_RE",
    "group_cues", "enforce_monotonic", "build_cues_json",
    "save_cues", "load_cues", "to_srt", "write_srt",
    "make_cover_head", "concat_copy", "finalize_concat",
    "structure", "compare",
    "CoverLayout", "render_cover", "RULER_LEFT", "BOX_RIGHT",
]
