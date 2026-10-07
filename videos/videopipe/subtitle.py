# -*- coding: utf-8 -*-
"""底部字幕轨道：整句淡变 + 句内逐字到点高亮。

四片标准结构（zsx / wang / zbj / pro 同源）。逐字 span 跨 cue 连续编号，
与对齐产出的 chars 一一对应（带断言）。时间全部显式给秒，不依赖调用
顺序推导，保证逐帧 seek 确定性。
"""
from dataclasses import dataclass

from . import config
from .page import jsnum


@dataclass
class Fragments:
    html: str       # .sub 序列（置于 #subbar 内）
    js: str         # 整句 autoAlpha 淡入/淡出
    word_js: str    # 逐字 tl.set 变色


def char_track(cues, chars, accent, *, time_offset=0.0,
               sub_ids=None) -> Fragments:
    """底部「整句 + 逐字高亮」轨道。

    cues: [{"t","s","e"}]；chars: [{"c","s",...}]，两者逐字对齐。
    time_offset: pro 切片复用同一份 cues 时整体平移。
    sub_ids: 自定义每句编号序列；默认 0,1,2…。
    """
    if sub_ids is None:
        sub_ids = range(len(cues))
    off = float(time_offset)

    char_idx = 0
    sub_html, sub_js, word_js = [], [], []
    for ci, cue in zip(sub_ids, cues):
        spans = []
        for ch in cue["t"]:
            c = chars[char_idx]
            assert c["c"] == ch, (c["c"], ch)
            spans.append('<span class="ch" id="w%d">%s</span>'
                         % (char_idx, ch))
            word_js.append(
                "      tl.set('#w%d', { color: '%s' }, %.3f);"
                % (char_idx, accent, c["s"] + off))
            char_idx += 1
        sub_html.append(
            '      <span class="sub" id="sub%02d">%s</span>'
            % (ci, "".join(spans)))
        s = cue["s"] + off
        e = cue["e"] + off
        fade_out = max(s + config.SUB_LEAD, e - config.SUB_TAIL)
        sub_js.append(
            "      tl.fromTo('#sub%02d', { autoAlpha: 0 }, "
            "{ autoAlpha: 1, duration: .26, ease: 'power1.out' }, %.2f);"
            % (ci, s))
        sub_js.append(
            "      tl.to('#sub%02d', { autoAlpha: 0, duration: .26, "
            "ease: 'power1.in' }, %.2f);" % (ci, fade_out))
    assert char_idx == len(chars), (char_idx, len(chars))
    return Fragments("\n".join(sub_html),
                     "\n".join(sub_js),
                     "\n".join(word_js))


@dataclass
class CenterTrack:
    html: str       # .cue clip 序列（置于 #caption-wrap 内）
    word_js: str    # 逐字到点变金（带光晕 textShadow）


@dataclass
class SentenceTrack:
    html: str       # .sub 序列（整句文字，置于 #subbar 内）
    js: str         # 整句 autoAlpha 淡入/淡出


def center_char_clips(cues, chars, accent, *,
                      glow_rgba="rgba(232,184,75,.55)") -> CenterTrack:
    """中央「逐字 cue clip」轨道（心经专用）。

    每句一个 `.cue.clip`（data-duration 下限 .3s），句内逐字 span 全局
    连续编号，到点 set 金色＋金色光晕。
    """
    char_idx = 0
    cue_html, word_js = [], []
    for ci, cue in enumerate(cues):
        spans = []
        for ch in cue["t"]:
            c = chars[char_idx]
            assert c["c"] == ch, (c["c"], ch)
            spans.append('<span class="ch" id="w%d">%s</span>'
                         % (char_idx, ch))
            word_js.append(
                "      tl.set('#w%d', { color: '%s', textShadow: "
                "'0 0 26px %s' }, %.3f);"
                % (char_idx, accent, glow_rgba, c["s"]))
            char_idx += 1
        dur = round(max(0.3, cue["e"] - cue["s"]), 3)
        cue_html.append(
            '      <div class="cue clip" id="cue%02d" data-start="%.2f" '
            'data-duration="%.2f">%s</div>'
            % (ci, cue["s"], dur, "".join(spans)))
    assert char_idx == len(chars), (char_idx, len(chars))
    return CenterTrack("\n".join(cue_html), "\n".join(word_js))


def sentence_track(cues) -> SentenceTrack:
    """底部「整句」轨道（心经：.sub 内直接放整句，.28s 淡变）。

    fade_out = max(s + .35, e - .28)。
    """
    sub_html, sub_js = [], []
    for ci, cue in enumerate(cues):
        sub_html.append('      <span class="sub" id="sub%02d">%s</span>'
                        % (ci, cue["t"]))
        s, e = cue["s"], cue["e"]
        fade_out = max(s + config.SUB_LEAD, e - config.XJ_TAIL)
        sub_js.append(
            "      tl.fromTo('#sub%02d', { autoAlpha: 0 }, "
            "{ autoAlpha: 1, duration: .28, ease: 'power1.out' }, %.2f);"
            % (ci, s))
        sub_js.append(
            "      tl.to('#sub%02d', { autoAlpha: 0, duration: .28, "
            "ease: 'power1.in' }, %.2f);" % (ci, fade_out))
    return SentenceTrack("\n".join(sub_html), "\n".join(sub_js))
