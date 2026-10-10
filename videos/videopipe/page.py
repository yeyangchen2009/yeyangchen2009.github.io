# -*- coding: utf-8 -*-
"""HyperFrames HTML 文件外壳。

封装每个成片逐字相同的部分：doctype / head / meta / GSAP（项目内本地副本）/
`#root[data-composition-id="main"]` / GSAP paused timeline 与注册。
内容（css / body / js）由 scene、subtitle 等轨道模块产出后注入。
"""
import shutil
from pathlib import Path

from . import config


def stage_gsap(P) -> Path:
    """把唯一源 assets/gsap/gsap.min.js 复制进项目根（内容不变才写盘）。

    index.html 用 <script src="gsap.min.js"> 引用：不能用 CDN（实测约 11s，
    卡 check 浏览器 10s 导航超时），不能用 ../../ 穿越项目根（静态检查拒绝），
    也不能内联（库源码含 Math.random/Date.now 字样，被非确定性检查命中）。
    项目根的副本是构建产物（gitignored），仓库里只保留 assets 下一份源。
    """
    dst = P.root / "gsap.min.js"
    if not dst.exists() or dst.read_bytes() != config.GSAP_LOCAL.read_bytes():
        shutil.copyfile(config.GSAP_LOCAL, dst)
    return dst


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
                gsap_src: str = "gsap.min.js",
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
    ) % (gsap_src, css, jsnum(total), lead, body, js)
