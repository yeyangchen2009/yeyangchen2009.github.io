# -*- coding: utf-8 -*-
r"""hf-04 录屏前静态自检：npp_ops 取景/编辑锚点 vs 沙盒 backup 五权威态。

纯文件校验，不碰桌面、不启 NPP/Edge，秒级跑完。npp_ops 的
line_of/reveal_in_line 只在「磁盘当前内容」上工作，而 reveal_in_line 的
start/end 锚必须落在同一物理行（跨行直接 AssertionError，实拍即翻车）；
多行块只能靠 scroll_anchor 垂直取景。本脚本把 record_segments 各 take 在
对应布景态上的每一处 line_of/reveal/insert/replace 锚点全量验一遍：

  python check_anchors.py

布景态来源：F:\_hftest\hf04-seek\backup\s0..s4（LF）；
seg2a 的实拍产物文本＝s0 经 _css_edits（已验证与 s1 备份逐字一致）；
seg6 的实拍产物文本＝s3 经 _gsap_edits（s4 备份已收敛为同一单行款）。

另有 NppDiskModel 双态（磁盘/缓冲区）编辑序列步进模拟：replace_all/
insert 只改缓冲区、save 才落磁盘、line_of 只读磁盘——实拍漏 save 必崩，
模拟器在同一拍复现；三序列终态须与 s1/s4 备份逐字相等。

新增/改动任何 npp 锚点或编辑/save 序列后必须先跑本脚本；退出码非 0 不许开拍。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import record_segments as rs  # noqa: E402

BK = os.path.join(rs.PROJ, "backup")


def read_state(name):
    p = os.path.join(BK, rs.STATES[name])
    if not os.path.exists(p):
        raise SystemExit("权威备份缺失: " + p)
    return io.open(p, encoding="utf-8").read()


def find_lines(text, sub):
    """substring 命中的全部行号（1 起）＋行文本。"""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if sub in line:
            out.append((i, line))
    return out


def css_edited(s0):
    """s0 --(seg2a 入镜编辑)--> s1 实拍文本（复刻 npp 行级操作）。"""
    lines = s0.split("\n")
    card = next(i for i, ln in enumerate(lines, 1) if "#card {" in ln)
    # 实拍调 insert_after_line(card-1)：第 card-1 行之后＝0 起索引 card-1 处
    lines.insert(card - 1, rs.KEYFRAMES_CSS)
    t = "\n".join(lines)
    ls = next(i for i, ln in enumerate(t.split("\n"), 1)
              if "letter-spacing: -0.03em;" in ln)
    lines = t.split("\n")
    lines.insert(ls, rs.ANIM_LINE)
    return "\n".join(lines)


def gsap_edited(s3):
    """s3 --(seg6 入镜编辑)--> s4 实拍文本（replace 注释行＋两次插行）。"""
    assert s3.count(rs.SKEL_COMMENT) == 1
    t = s3.replace(rs.SKEL_COMMENT, rs.TT_TITLE, 1)
    lines = t.split("\n")
    i = next(k for k, ln in enumerate(lines) if '"power2.out" }, 2);' in ln)
    lines.insert(i + 1, rs.TT_CARD)
    i = next(k for k, ln in enumerate(lines) if '"back.out(1.7)" }, 3);' in ln)
    lines.insert(i + 1, rs.TT_SUB)
    return "\n".join(lines)


S0 = read_state("s0")
S1 = read_state("s1")
S2 = read_state("s2")
S3 = read_state("s3")
S4 = read_state("s4")
S1P = css_edited(S0)
S4P = gsap_edited(S3)

fails = []


def check_reveal(desc, text, line_sub, start_sub, end_sub=None,
                 scroll_sub=None):
    """对应 n.reveal_in_line(n.line_of(line_sub), start, end, scroll_anchor=)。"""
    hits = find_lines(text, line_sub)
    if len(hits) != 1:
        fails.append("%s: line_of(%r) 命中 %d 次 %s（须恰好 1 次）"
                     % (desc, line_sub, len(hits), [h[0] for h in hits]))
        return
    no, line = hits[0]
    if start_sub not in line:
        fails.append('%s: 第 %d 行找不到起点锚 %r' % (desc, no, start_sub))
    if end_sub is not None and end_sub not in line:
        fails.append('%s: 终点锚 %r 不在第 %d 行（跨行取景必须改用 scroll_anchor）'
                     % (desc, end_sub, no))
    if scroll_sub is not None:
        sh = find_lines(text, scroll_sub)
        if not sh:
            fails.append('%s: scroll_anchor %r 文件中不存在' % (desc, scroll_sub))
    print("PASS %-28s L%d  %s" % (desc, no, line.strip()[:72]))


def check_insert(desc, text_before, anchor, block, expected_sub=None):
    """insert_after_anchor/replace_all 的锚点唯一性与落盘校验。"""
    hits = find_lines(text_before, anchor)
    if len(hits) != 1:
        fails.append("%s: 插入锚 %r 命中 %d 次（须唯一）"
                     % (desc, anchor, len(hits)))
    if expected_sub is not None and expected_sub not in text_before:
        fails.append("%s: 前置内容缺 %r" % (desc, expected_sub))
    print("PASS %-28s 锚 %r 唯一（L%s）"
          % (desc, anchor[:36], hits[0][0] if hits else "?"))


print("== seg2a（s0 → s1，@keyframes 入镜） ==")
check_reveal("seg2a 开场 #title 块", S0, "#title {", "#title {",
             scroll_sub="letter-spacing")
check_insert("seg2a 插 keyframes", S0, "#card {", rs.KEYFRAMES_CSS)
check_insert("seg2a 插 animation 行", S1P, "letter-spacing: -0.03em;", rs.ANIM_LINE)
check_reveal("seg2a keyframes 全块", S1P, "@keyframes flyin", "@keyframes",
             scroll_sub="translateY(0);")
check_reveal("seg2a animation 行", S1P, "animation: flyin",
             "animation: flyin", "ease-out;")

print("== seg4a（s2，setInterval 块取景） ==")
check_reveal("seg4a 开场 setInterval", S2, "setInterval", "setInterval",
             scroll_sub="}, 500);")
check_reveal("seg4a tick 元素 h2", S2, 'id="subtitle"', 'id="subtitle"', "</h2>")
check_reveal("seg4a 回块顶 let tick", S2, "let tick = 0;", "let tick = 0;",
             scroll_sub="}, 500);")

print("== seg6（s3 → s4，三件套入镜） ==")
check_reveal("seg6 第一件 paused", S3, "gsap.timeline", "gsap.timeline",
             "paused: true")
check_reveal("seg6 注释骨架行", S3, "// tl.fromTo", "// tl.fromTo", "0);")
check_insert("seg6 注释换 title", S3, rs.SKEL_COMMENT, rs.TT_TITLE)
check_insert("seg6 挂 card", S4P.split(rs.TT_CARD)[0] + rs.TT_CARD,
             '"power2.out" }, 2);', rs.TT_CARD)
check_insert("seg6 挂 subtitle",
             S4P.split(rs.TT_SUB)[0] + rs.TT_SUB,
             '"back.out(1.7)" }, 3);', rs.TT_SUB)
check_reveal("seg6 title 挂第 2 秒", S4P, 'tl.fromTo("#title"', "tl.fromTo",
             '"power2.out" }, 2);')
check_reveal("seg6 card 挂第 3 秒", S4P, 'tl.fromTo("#card"',
             'tl.fromTo("#card"', '"back.out(1.7)" }, 3);')
check_reveal("seg6 subtitle 挂第 6 秒", S4P, 'tl.fromTo("#subtitle"',
             'tl.fromTo("#subtitle"', '"power2.out" }, 6);')
check_reveal("seg6 注册行＋seek0", S4P, 'window.__timelines["main"]',
             'window.__timelines["main"]', "= tl;", scroll_sub="tl.seek(0);")

class NppDiskModel:
    """镜像 npp_ops 的命门语义：replace_all/insert_after_* 只改 NPP 缓冲区，
    save 才同步磁盘；而 line_of/reveal_in_line/insert_after_anchor 的锚点
    解析全部读磁盘。实拍里「编辑后忘 save 就锚定新内容」必抛 AssertionError，
    本模型在同一时序点复现该崩溃（2026-10-12 seg6 曾中此招）。
    """

    def __init__(self, text):
        self.disk = text
        self.buf = text

    def replace_all(self, find, repl):
        cnt = self.buf.count(find)
        if cnt != 1:
            raise AssertionError("replace_all 锚命中 %d 次（须 1）：%r"
                                 % (cnt, find[:48]))
        self.buf = self.buf.replace(find, repl, 1)

    def _line_of_disk(self, sub):
        hits = find_lines(self.disk, sub)
        if len(hits) != 1:
            raise AssertionError("line_of(%r) 在磁盘命中 %d 次 %s——实拍此时"
                                 "必崩（前面的编辑是不是忘了 save？）"
                                 % (sub[:48], len(hits), [h[0] for h in hits]))
        return hits[0][0]

    def insert_after_line(self, no, block):
        lines = self.buf.split("\n")          # 行号按磁盘解析，插入作用于缓冲区
        if not 1 <= no <= len(lines):
            raise AssertionError("insert_after_line 行号 %d 越界" % no)
        lines.insert(no, block)
        self.buf = "\n".join(lines)

    def insert_after_anchor(self, anchor, block):
        self.insert_after_line(self._line_of_disk(anchor), block)

    def save(self, check=None):
        self.disk = self.buf
        if check is not None and not check(self.disk):
            raise AssertionError("save 后磁盘未达 check 预期")

    def reveal(self, desc, line_sub, start_sub, end_sub=None, scroll_sub=None):
        hits = find_lines(self.disk, line_sub)
        if len(hits) != 1:
            raise AssertionError("%s: line_of 磁盘命中 %d 次" % (desc, len(hits)))
        no, line = hits[0]
        if start_sub not in line or (end_sub is not None and end_sub not in line):
            raise AssertionError("%s: 磁盘第 %d 行 start/end 锚不全" % (desc, no))
        if scroll_sub is not None and not find_lines(self.disk, scroll_sub):
            raise AssertionError("%s: scroll_anchor 磁盘不存在" % desc)
        print("PASS %-28s 磁盘态 L%d" % (desc, no))


def simulate_sequences():
    """严格按 record_segments.take_seg6/_gsap_edits/take_seg2a 的实拍调用序。"""
    # ---- seg6（s3 → s4），序列与 take_seg6 act 严格镜像 ----
    m = NppDiskModel(S3)
    m.reveal("seg6 paused", "gsap.timeline", "gsap.timeline", "paused: true")
    m.reveal("seg6 注释行", "// tl.fromTo", "// tl.fromTo", "0);")
    m.replace_all(rs.SKEL_COMMENT, rs.TT_TITLE)        # 只改缓冲区
    m.save(lambda t: '"power2.out" }, 2);' in t and "// tl.fromTo" not in t)
    m.reveal("seg6 title 行", 'tl.fromTo("#title"', "tl.fromTo",
             '"power2.out" }, 2);')
    m.insert_after_anchor('"power2.out" }, 2);', rs.TT_CARD)
    m.save(lambda t: '"back.out(1.7)" }, 3);' in t)
    m.insert_after_anchor('"back.out(1.7)" }, 3);', rs.TT_SUB)
    m.save(lambda t: ('"back.out(1.7)" }, 3);' in t
                      and '"power2.out" }, 6);' in t))
    m.reveal("seg6 card 行", 'tl.fromTo("#card"', 'tl.fromTo("#card"',
             '"back.out(1.7)" }, 3);')
    m.reveal("seg6 subtitle 行", 'tl.fromTo("#subtitle"', 'tl.fromTo("#subtitle"',
             '"power2.out" }, 6);')
    m.reveal("seg6 注册行", 'window.__timelines["main"]',
             'window.__timelines["main"]', "= tl;", scroll_sub="tl.seek(0);")
    if m.disk != S4:
        raise AssertionError("seg6 序列终态 != s4-final.html 备份（实拍产物会分叉）")
    print("PASS seg6 序列终态 == s4 备份")

    # ---- _gsap_edits（布景快进，s3 → s4），同构 save 时序 ----
    m2 = NppDiskModel(S3)
    m2.replace_all(rs.SKEL_COMMENT, rs.TT_TITLE)
    m2.save(lambda t: '"power2.out" }, 2);' in t and "// tl.fromTo" not in t)
    m2.insert_after_anchor('"power2.out" }, 2);', rs.TT_CARD)
    m2.save(lambda t: '"back.out(1.7)" }, 3);' in t)
    m2.insert_after_anchor('"back.out(1.7)" }, 3);', rs.TT_SUB)
    m2.save(lambda t: "back.out(1.7)" in t and '"power2.out" }, 6);' in t)
    if m2.disk != S4:
        raise AssertionError("_gsap_edits 终态 != s4 备份")
    print("PASS _gsap_edits 布景序列 == s4 备份")

    # ---- seg2a（s0 → s1），两次编辑后均有 save ----
    m3 = NppDiskModel(S0)
    card = next(i for i, ln in enumerate(S0.split("\n"), 1) if "#card {" in ln)
    m3.insert_after_line(card - 1, rs.KEYFRAMES_CSS)
    m3.save(lambda t: "@keyframes flyin" in t)
    m3.reveal("seg2a keyframes", "@keyframes flyin", "@keyframes",
              scroll_sub="translateY(0);")
    m3.insert_after_anchor("letter-spacing: -0.03em;", rs.ANIM_LINE)
    m3.save(lambda t: "animation: flyin 0.8s ease-out;" in t)
    m3.reveal("seg2a animation", "animation: flyin", "animation: flyin", "ease-out;")
    if m3.disk != S1:
        raise AssertionError("seg2a 序列终态 != s1-css.html 备份")
    print("PASS seg2a 序列终态 == s1 备份")


print("== 编辑序列磁盘态模拟（缓冲区 vs 磁盘，save 时序） ==")
try:
    simulate_sequences()
except AssertionError as exc:
    fails.append("编辑序列磁盘态模拟失败: " + str(exc))

print("== 备份一致性 ==")
if S1P == S1:
    print("PASS s1 备份 == seg2a 实拍文本")
else:
    fails.append("s1 备份与 seg2a 实拍文本不一致（布景/备份分叉）")
if S4P == S4:
    print("PASS s4 备份 == seg6 实拍文本")
else:
    fails.append("s4 备份与 seg6 实拍文本不一致（布景/备份分叉）")
for name, text, needles in (
        ("s0", S0, ("我的第一个片段",)),
        ("s2", S2, ("data-no-timeline", "setInterval", "}, 500);")),
):
    for nd in needles:
        if nd in text:
            print("PASS %s 含 %r" % (name, nd))
        else:
            fails.append("%s 缺 %r" % (name, nd))

print()
if fails:
    print("锚点自检失败 %d 项：" % len(fails))
    for f in fails:
        print("  FAIL", f)
    sys.exit(1)
print("全部锚点自检通过，可以开拍。")
