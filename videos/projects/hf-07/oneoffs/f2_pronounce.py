# -*- coding: utf-8 -*-
"""hf-07 F2 人耳正音抽检：高危点切句拼成一个 mp3（2026-10-20）。

客观层（build/transcript.txt＋build/align-check.txt，whisper 复转 v2 母带）
已核完字面与 15 个 GAP；同音错写（帧→针、墙钟→强中、滑→划）属 whisper
识别常态，不进清单。TTS 同音念错 whisper 分不出来（lěi/lèi、tiáo/diào、
xuē、轻声 nong），疑似轻读漏念的 GAP 也必须人耳——本脚本按 raw.json 的
segment 时间戳切句，另有 11 个新旧段衔接点按 cues 段首时间切窗。

产出：
  build/f2/pronounce-check.mp3   每点前后留 0.6s，点间 0.8s 静音
  build/f2/pronounce-index.txt  抽检清单（顺序/时间/原转录句）

用法：python oneoffs/f2_pronounce.py
"""
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WAV = ROOT / "media" / "hf-07-yeyang.wav"
RAW = ROOT / "build" / "raw.json"
CUES = ROOT / "cues" / "cues.json"
SRC = ROOT / "src" / "hf-07-src.txt"
OUT = ROOT / "build" / "f2"

PAD = 0.6
GAP = 0.8

# (标签, 转录中命中子串)；同串多处命中全部收，标签加序号
NEEDLES = [
    ("01 setInterval 念法（P2/P7 两处）", "set interval"),
    ("03 requestAnimationFrame 念法", "requestanimation"),
    ("04 items 念法（报告三个 items，两处）", "items"),
    ("05 CSS filter 念法", "css filter"),
    ("06 累加 lěi（防 lèi）", "累加"),
    ("07 调慢 tiáo", "条慢"),
    ("08 samples 调 tiáo", "sanpost"),
    ("09 调色 tiáo（grade 段，多处）", "调色"),
    ("10 逐帧回调 diào", "回条"),
    ("11 听调度 diào", "调度"),
    ("12 相位 xiàng（两处）", "向位"),
    ("13 闭包 bì bāo（多处）", "闭包"),
    ("14 掐表 qiā biǎo（多处）", "掐"),
    ("15 薛定谔 xuē dìng è", "缺定饿"),
    ("16 window 点 __timelines（双下划线吞读，hf-04 基线可接受）", "内张表"),
    ("17 横杠横杠 shot（多处）", "横杠横杠"),
    ("18 grade compare 拆词", "gridcompare"),
    ("19 loading 念法", "楼顶"),
    ("20 Anime 不是 animate", "animate"),
    ("21 at 念法（whisper 听成 Edge）", "edge"),
    ("22 分个工（whisper 听成风格弓）", "风格弓"),
    ("23 今天一集（whisper 听成议题）", "议题"),
    ("24 转圈 zhuàn（loading 段）", "赚圈"),
    ("25 弹窗 tán（两处）", "弹"),
    ("26 幻灯片 huàn（whisper 写换）", "换灯片"),
    ("27 暂停 zàn", "暂停"),
    ("28 洋葱 yáng cōng", "洋葱"),
    ("29 糊弄 hù nong（whisper 听成互动）", "互动"),
    ("30 喘气 chuǎn（whisper 写传气）", "传气"),
    ("31 行动件 xíng（全篇唯一行）", "行动键"),
    ("32 道别 我们下期见（whisper 听成佛门，必听）", "佛门"),
    ("33 我是叶扬 yáng（系列固定句）", "叶阳"),
]

# 直接按时间窗切（GAP/节拍点），(标签, 起, 止)
WINDOWS = [
    ("34 开篇四个第二秒（节拍感，whisper 漏对齐前三）", 38.0, 43.6),
    ("35 掐头去尾（GAP 352.93/353.39，疑似轻读）", 352.3, 354.8),
    ("36 八百像素（GAP 427.02/427.18）", 426.2, 427.9),
    ("37 五百（GAP 428.88/429.18）", 428.3, 429.9),
    ("38 慢表三数字：一分钟一圈", 140.6, 142.3),
    ("39 慢表三数字：第十秒", 143.4, 144.6),
    ("40 慢表三数字：六分之一", 149.7, 151.3),
    ("41 MP4＝M P 四", 511.0, 513.2),
]

# 11 个新旧段衔接界点：段号（src 1..22），界点在该段开头之前
BOUNDARIES = [2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 15, 16, 18, 19, 20, 21]
# 新段（蝉镜重合成）号：02/04/07/08/09/12/15/16/18/19/20
NEW_SEGS = {2, 4, 7, 8, 9, 12, 15, 16, 18, 19, 20}


def run(cmd):
    subprocess.run(cmd, check=True, cwd=str(ROOT),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def norm(s):
    out = []
    for ch in s:
        if "一" <= ch <= "鿿" or ch.isalnum():
            out.append(ch.lower())
    return "".join(out)


def segment_starts():
    """从 src 22 段首句在 cues 流中顺序定位，返回 {段号: 首句 s}。"""
    paras = [p.strip() for p in SRC.read_text(encoding="utf-8").split("\n\n")
             if p.strip()]
    cues = json.loads(CUES.read_text(encoding="utf-8"))["cues"]
    starts = {}
    pos = 0
    search_pos = 0
    stream = ""
    spans = []
    for c in cues:
        t = norm(c["t"])
        spans.append((pos, pos + len(t), c["s"]))
        stream += t
        pos += len(t)
    for i, p in enumerate(paras, start=1):
        head = norm(p)[:7]
        j = stream.find(head, search_pos)
        assert j >= 0, "段 %d 首句定位失败：%s" % (i, head)
        search_pos = j + len(head)
        for a, b, s in spans:
            if a <= j < b:
                starts[i] = s
                break
    return starts


def main():
    segs = json.load(open(RAW, encoding="utf-8"))["segments"]
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- needle 命中（词级定位切小窗，同串全收）----
    hits = []

    def locate(seg, needle):
        """在 seg 词级流里定位 needle，返回 (t0,t1)；失败回退整段。"""
        toks, stream = [], ""
        for w in seg.get("words", []):
            n = norm(w["w"])
            if n:
                toks.append((len(stream), len(stream) + len(n),
                             w["s"], w["e"]))
                stream += n
        key = norm(needle)
        i = stream.find(key)
        if i < 0:
            return seg["s"], seg["e"]
        j = i + len(key) - 1
        t0 = next(s for a, b, s, e in toks if a <= i < b)
        t1 = next(e for a, b, s, e in toks if a <= j < b)
        return t0, t1

    for label, needle in NEEDLES:
        matched = [s for s in segs if needle in s["t"].lower()]
        if not matched:
            print("MISS", label)
            continue
        for k, s in enumerate(matched):
            w0, w1 = locate(s, needle)
            tag = label if len(matched) == 1 else "%s（%d/%d）" % (
                label, k + 1, len(matched))
            hits.append((tag, max(0.0, w0 - PAD), w1 + PAD,
                         s["t"].strip()))
    print("needle 命中 %d 窗" % len(hits))

    # ---- 时间窗 ----
    for label, t0, t1 in WINDOWS:
        hits.append((label, t0, t1, "（按对齐时间窗切）"))

    # ---- 11 衔接界点（实为 16 个相邻段界，其中新旧跨界 11 个全收）----
    starts = segment_starts()
    for n in BOUNDARIES:
        t = starts[n] - 0.34  # 段间 0.34s 停顿中点近似
        a_new, b_new = n - 1 in NEW_SEGS, n in NEW_SEGS
        kind = ("旧→新" if not a_new and b_new else
                "新→旧" if a_new and not b_new else
                "新→新" if b_new else "旧→旧")
        hits.append(("42 段界 P%02d/P%02d（%s）电平/音色衔接"
                     % (n - 1, n, kind), max(0.0, t - 2.0), t + 2.0,
                     "界点约 %.2fs" % t))

    # 重叠/相邻窗合并（间隔 < GAP）
    hits.sort(key=lambda x: x[1])
    merged = []
    for tag, t0, t1, note in hits:
        if merged and t0 - merged[-1][2] < GAP:
            ptag, p0, p1, pnote = merged[-1]
            merged[-1] = (ptag + " ＋ " + tag, p0, max(p1, t1),
                          pnote + " ｜ " + note)
        else:
            merged.append((tag, t0, t1, note))

    parts, index = [], []
    cursor = 0.0
    for k, (tag, t0, t1, note) in enumerate(merged):
        clip = OUT / ("pc-%02d.wav" % k)
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t0),
             "-i", str(WAV), "-t", str(t1 - t0),
             "-c:a", "pcm_s16le", "-ar", "24000", "-ac", "1", str(clip)])
        parts.append(clip)
        index.append("%05.1fs  %s\n         原转录：%s（%.2f–%.2f）"
                     % (cursor, tag, note, t0, t1))
        cursor += (t1 - t0) + GAP

    gap = OUT / "_gap.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
         "-i", "anullsrc=r=24000:cl=mono", "-t", str(GAP),
         "-c:a", "pcm_s16le", str(gap)])
    lines = []
    for p in parts:
        lines.append("file '%s'" % p.as_posix())
        lines.append("file '%s'" % gap.as_posix())
    listfile = OUT / "_pronounce-list.txt"
    listfile.write_text("\n".join(lines), encoding="utf-8")
    mp3 = OUT / "pronounce-check.mp3"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
         "-safe", "0", "-i", str(listfile),
         "-c:a", "libmp3lame", "-q:a", "4", str(mp3)])
    head = [
        "hf-07 F2 人耳正音抽检清单（v2 母带 559.22s，2026-10-20）",
        "音频：build/f2/pronounce-check.mp3（每点前后 0.6s，点间 0.8s 静音）",
        "客观层：15 个对齐 GAP（四个第二秒 40s／掐头去尾 353s／八百五百 427-429s",
        "已在 34-37；轻声语气词 GAP：儿 45/423/465、呢 54、的 361、时 261）",
        "重点：双音 tiáo/diào 各读各音；累加 lěi；薛 xuē；佛门疑云（道别）；",
        "11 新旧段衔接电平；Anime≠animate；at≠Edge；__timelines 吞读（基线可过）",
        "",
    ]
    (OUT / "pronounce-index.txt").write_text(
        "\n".join(head + index), encoding="utf-8")
    print("→ %s（%d 段，%.1f 分钟）" %
          (mp3.relative_to(ROOT), len(parts), cursor / 60))


if __name__ == "__main__":
    main()
