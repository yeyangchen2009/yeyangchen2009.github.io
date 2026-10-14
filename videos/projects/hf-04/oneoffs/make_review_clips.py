# -*- coding: utf-8 -*-
"""把 hf-04 母带的人耳验收疑点切成一个合集 wav（段间 0.5s 静音）。

声学已判（见 check_pron.py 输出）：行 háng×3 过、tick×6 过、得 děi 4 中 3
明过＋1 搭配锁定。本合集只收 whisper 判不了、必须人耳的点：英文术语念法、
涨/Chrome/薛定谔、瘾/闲零星疑字。编号即播放顺序。
"""
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC_WAV = ROOT / "media" / "hf-04-yeyang.wav"
OUT_WAV = ROOT / "build" / "review-clips.wav"
GAP = 0.5

# (起, 止, 编号, 听点, 期望)
CLIPS = [
    (87.5, 90.2, 1, "seekable 首现（命根子术语）", "英文 seekable [ˈsiːkəbl]，不是 cable"),
    (77.0, 78.9, 2, "「都得回答」的得", "děi（上声，需要义）"),
    (62.4, 64.2, 3, "「你长什么样」①", "涨 zhǎng（生长），不是 cháng"),
    (239.1, 241.0, 4, "「你长什么样」②", "涨 zhǎng"),
    (174.3, 177.8, 5, "排队段 tick 三 / tick 四", "tick [tɪk]，不是 check"),
    (190.1, 195.7, 6, "这一趟 tick 三 / 成了 tick 四", "tick"),
    (195.9, 197.7, 7, "「机器闲，也只差这一下」", "闲 xián（不读 xié 鞋）"),
    (206.4, 214.9, 8, "tick 四、六、七；跳到 tick 七", "四处 tick"),
    (221.0, 222.9, 9, "多个无头 Chrome 并行", "Chrome [kroʊm]，不是 cron/窗户"),
    (274.7, 277.3, 10, "薛定谔的画面", "薛 xuē（不是 què）"),
    (281.8, 283.2, 11, "是 GSAP 的时间轴（首现）", "GSAP 念法统一可辨"),
    (291.8, 294.1, 12, "paused 等于 true", "paused / true 清楚（true 不念「处」）"),
    (310.7, 312.1, 13, "我写 fromTo", "fromTo 可辨"),
    (317.0, 319.3, 14, "power2 点 out", "out [aʊt]，不念零"),
    (344.3, 345.8, 15, "这航（行）是报到", "háng（声学已过，抽听）"),
    (360.1, 363.1, 16, "全局 GSAP 动画", "GSAP 与 11 一致"),
    (389.2, 390.6, 17, "三航（行）凑齐", "háng（抽听）"),
    (401.7, 404.3, 18, "还不过瘾", "瘾 yǐn（前鼻，不读 yǐng 影）"),
    (491.8, 494.6, 19, "无头 Chrome 干的事", "Chrome，与 9 一致"),
    (509.8, 512.4, 20, "这十秒的片子，三百帧", "片子 piān（平声）"),
    (524.1, 525.6, 21, "GSAP 不是唯一选择", "GSAP，与 11 一致"),
    (530.4, 532.3, 22, "原生的 WAAPI", "WAAPI 念法可辨（哇皮/逐字母均可接受）"),
    (533.4, 537.6, 23, "Lottie、Three 点 js、Anime 点 js", "三个库名可辨，点字在"),
    (565.7, 569.0, 24, "GSAP 时间轴是不是 paused 等于 true", "GSAP/paused/true"),
    (590.2, 592.4, 25, "灵魂在 seek（片尾口号）", "seek [siːk] 长元音"),
]

w = wave.open(str(SRC_WAV), "rb")
SR, CH, SW = w.getframerate(), w.getnchannels(), w.getsampwidth()
assert (SR, CH, SW) == (24000, 1, 2)
full = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
w.close()

gap = np.zeros(int(GAP * SR), dtype=np.int16)
parts = []
for t0, t1, num, _name, _want in CLIPS:
    seg = full[int(t0 * SR):int(t1 * SR)]
    parts += [gap, seg]
out = np.concatenate(parts[1:])
OUT_WAV.parent.mkdir(exist_ok=True)
with wave.open(str(OUT_WAV), "wb") as o:
    o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes(out.tobytes())

mp3 = OUT_WAV.with_suffix(".mp3")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(OUT_WAV),
                "-codec:a", "libmp3lame", "-qscale:a", "4", str(mp3)], check=True)
print("合集：%s（%.1fs）＋ %s（%.0f KB）"
      % (OUT_WAV.relative_to(ROOT), len(out) / SR, mp3.name, mp3.stat().st_size / 1024))
for t0, t1, num, name, want in CLIPS:
    print("%2d. %7.2f–%7.2f  %-26s 期望：%s" % (num, t0, t1, name, want))
