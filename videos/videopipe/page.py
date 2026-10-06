# -*- coding: utf-8 -*-
"""HyperFrames HTML 文件外壳。

封装每个成片逐字相同的部分：doctype / head / meta / GSAP CDN /
`#root[data-composition-id="main"]` / GSAP paused timeline 与注册。
内容（css / body / js）由 scene、subtitle 等轨道模块产出后注入。
"""
from . import config


def jsnum(x) -> str:
    """JS 秒数字面量：0.0 -> '0.0'，11.15 -> '11.15'，68.2 -> '68.2'。"""
    return str(float(x))


def attr_num(x) -> str:
    """HTML data 属性数字：整数值不带小数（0 -> '0'，1 -> '1'）。"""
    f = float(x)
    return str(int(f)) if f == int(f) else str(f)


def audio_tag(src: str, duration, *, track=config.TRACK_AUDIO, volume=1.0) -> str:
    """标准口播音频元素（固定 id，轨道 2）。"""
    return (
        '      <audio id="a-roll-audio" src="%s" data-start="0" data-duration="%s"\n'
        '             data-track-index="%d" data-volume="%s"></audio>'
        % (src, jsnum(duration), track, attr_num(volume)))


def render_page(*, total, css: str, body: str, js: str,
                body_lead_blank: bool = True) -> str:
    """组装完整 index.html 文本（不写盘，便于测试与对比）。

    body_lead_blank: 标准片 root 开标签后有一空行；心经老版 root 后
    直接接 <video>，传 False 保持零差异。
    """
    lead = "\n" if body_lead_blank else ""
    return (
        '<!doctype html>\n'
        '<html lang="zh" data-resolution="landscape">\n'
        '  <head>\n'
        '    <meta charset="UTF-8" />\n'
        '    <meta name="viewport" content="width=1920, height=1080" />\n'
        '    <script src="%s"></script>\n'
        '    <style>\n%s\n    </style>\n'
        '  </head>\n'
        '  <body>\n'
        '    <div id="root" data-composition-id="main" data-start="0" '
        'data-duration="%s" data-width="1920" data-height="1080">\n'
        '%s%s\n'
        '    </div>\n'
        '\n'
        '    <script>\n'
        '      const tl = gsap.timeline({ paused: true });\n'
        '\n%s\n'
        '\n'
        '      window.__timelines = window.__timelines || {};\n'
        '      window.__timelines[\'main\'] = tl;\n'
        '    </script>\n'
        '  </body>\n'
        '</html>\n'
    ) % (config.GSAP_URL, css, jsnum(total), lead, body, js)
