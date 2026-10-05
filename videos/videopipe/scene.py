# -*- coding: utf-8 -*-
"""场景四元组与 clip / scene-inner 渲染。

HyperFrames StaticGuard 规避固化在此：动画元素（class 含 "clip"）内必须
再包一层 `.scene-inner`，静态守卫盯 clip、切换只对 inner 做 opacity。
"""
from dataclasses import dataclass

from . import config
from .page import jsnum


@dataclass
class Scene:
    id: str
    s: float
    e: float
    body: str


def render_scenes(scenes, *, track=config.TRACK_SCENE) -> str:
    """把 Scene 列表渲染成标准 clip 序列。"""
    out = []
    for sc in scenes:
        dur = round(sc.e - sc.s, 3)
        out.append(
            '      <div id="%s" class="scene clip" data-start="%.2f" '
            'data-duration="%.3f" data-track-index="%d">\n'
            '        <div class="scene-inner">%s\n'
            '        </div>\n'
            '      </div>'
            % (sc.id, sc.s, dur, track, sc.body))
    return "\n".join(out)


def jdur(x) -> str:
    """JS 时长简写：0.5 -> '.5'，0.45 -> '.45'（GSAP 习惯）。"""
    s = repr(float(x))
    return s[1:] if s.startswith("0.") else s


def scene_fade_js(scene_id, *, in_at, out_at,
                  in_dur=0.5, out_dur=0.45) -> str:
    """针对 `#id > .scene-inner` 的入场/出场两行（时间显式给，不隐式推导）。"""
    return (
        "      tl.fromTo('#%s > .scene-inner', {opacity:0}, "
        "{opacity:1,duration:%s,ease:'power1.out'}, %s);\n"
        "      tl.to('#%s > .scene-inner', {opacity:0,duration:%s,"
        "ease:'power1.in'}, %s);"
        % (scene_id, jdur(in_dur), jsnum(in_at),
           scene_id, jdur(out_dur), jsnum(out_at)))
