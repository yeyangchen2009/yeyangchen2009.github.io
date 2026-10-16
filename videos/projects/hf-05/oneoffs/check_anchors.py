# -*- coding: utf-8 -*-
r"""hf-05 录屏前静态自检：record_segments 的取景锚点/入镜编辑序列 vs backup 七态。

纯文件校验，不碰桌面、不启 NPP，秒级跑完。reveal_in_line 的 start/end 锚
必须落在同一物理行（跨行直接 AssertionError，实拍即翻车）；入镜编辑全是
「选区→DELETE/打字覆盖选区→save」，本脚本在磁盘文本上镜像每一处替换与
dom_swap 的整行剪切粘贴，并回放 save 谓词：

  python check_anchors.py

布景态来源：F:\_hftest\hf05-check\backup\<state>\index.html（setup_scenes
生成）。关键终态交叉断言：t2a 的实拍产物必须与 s1-no-duration 备份逐字
一致（删的就是那个属性，一个字节都不能差）。

新增/改动任何锚点或编辑序列后必须先跑本脚本；退出码非 0 不许开拍。
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import record_segments as rs  # noqa: E402

BK = r"F:\_hftest\hf05-check\backup"


def read_state(name):
    p = os.path.join(BK, rs.STATES[name], "index.html")
    if not os.path.exists(p):
        raise SystemExit("权威备份缺失: " + p)
    return io.open(p, encoding="utf-8").read()


def lines_of(text):
    return text.splitlines()


def line_no(text, sub, occurrence=1):
    """镜像 n.line_of（磁盘，1 起）。"""
    n = 0
    for i, line in enumerate(lines_of(text), 1):
        if sub in line:
            n += 1
            if n == occurrence:
                return i
    raise AssertionError("line_of(%r) 未命中" % sub)


def select_span(line, start, end=None):
    """镜像 reveal_in_line 行内选区间，返回 (c1, c2)；锚缺失即翻车。"""
    c1 = line.find(start)
    if c1 < 0:
        raise AssertionError("行内找不到起点锚 %r" % start)
    if end is None:
        return c1, c1 + len(start)
    hit = line.find(end, c1)
    if hit < 0:
        raise AssertionError("行内找不到终点锚 %r（跨行取景必须改 scroll_anchor）" % end)
    return c1, hit + len(end)


def replace_selection(text, line_no_, start, typed, end=None):
    """镜像「reveal 选区→打字（DELETE＝typed=''）覆盖」后的磁盘文本。"""
    ls = lines_of(text)
    line = ls[line_no_ - 1]
    c1, c2 = select_span(line, start, end)
    ls[line_no_ - 1] = line[:c1] + typed + line[c2:]
    return "\n".join(ls) + ("\n" if text.endswith("\n") else "")


fails = []


def must(cond, msg):
    if cond:
        print("PASS", msg)
    else:
        fails.append(msg)
        print("FAIL", msg)


S0 = read_state("s0")
S1 = read_state("s1")
S2 = read_state("s2")
S3 = read_state("s3")
S4 = read_state("s4")
S5 = read_state("s5")
S6 = read_state("s6")

# ---------- t2a：s0 删 title data-duration，终态须逐字等于 s1 ----------

print("== t2a 删 data-duration（s0 → s1） ==")
n_title = line_no(S0, 'id="title"')
must(n_title == 18, "s0 title 开标签在 L18（实测 L%d）" % n_title)
title0 = lines_of(S0)[n_title - 1]
c1, c2 = select_span(title0, ' data-duration="10"', '"10"')
must(c2 - c1 == len(' data-duration="10"'),
     "t2a 选区恰好是 ' data-duration=\"10\"'（%d 字符）" % (c2 - c1))
s1_shot = replace_selection(S0, n_title, ' data-duration="10"', "", '"10"')
must(rs._title_line(s1_shot) == lines_of(S1)[line_no(S1, 'id="title"') - 1],
     "t2a 删除后 title 行逐字等于 s1 备份")
must(s1_shot == S1, "t2a 实拍终态与 s1-no-duration 备份全文逐字一致")
must('data-start="0"' in rs._title_line(s1_shot),
     "t2a 保存后二拍锚 data-start=\"0\" 仍在 title 行")

# ---------- t3b：s2 给 tail 行镜头＋root 10→13 ----------

print("== t3b 越界 root 修复（s2） ==")
must(line_no(S2, 'id="tail"') == 22, "s2 tail 开标签在 L22")
tail = lines_of(S2)[21]
select_span(tail, 'data-start="8"', 'data-duration="5"')
print("PASS t3b tail 行双锚同行")
must(line_no(S2, 'data-composition-id="main"') == 16, "s2 root 开标签在 L16")
root = lines_of(S2)[16]
rc1, rc2 = select_span(root, "10", "10")
must(root[rc1:rc2] == "10" and 'data-duration="10"' in root[:rc1 + 20],
     "t3b root 行首个 '10' 命中 data-duration（不是 1080）")
s2_fix = replace_selection(S2, 17, "10", "13", "10")
must('data-duration="13"' in s2_fix and 'data-height="1080"' in s2_fix,
     "t3b 保存谓词：root 变 13、1080 完好")

# ---------- t4a/c：色值两连改（CSS L11，跨态不变） ----------

print("== t4 对比度色值链（CSS L11） ==")
for name, t in (("s2+root13", s2_fix), ("s0", S0), ("s4", S4), ("s6", S6)):
    must('#e6edf3' in lines_of(t)[10], "%s 态 L11 含初始色 #e6edf3" % name)
css_line = lines_of(s2_fix)[10]
select_span(css_line, "#e6edf3")
bad = replace_selection(s2_fix, 11, "#e6edf3", "#1a1f26")
must("#1a1f26" in bad and rs._title_line  # save 谓词只查色值
     and "#1a1f26" in lines_of(bad)[10], "t4a 保存谓词：L11 变 #1a1f26")
select_span(lines_of(bad)[10], "#1a1f26")
fixed = replace_selection(bad, 11, "#1a1f26", "rgb(93,97,102)")
must("rgb(93,97,102)" in lines_of(fixed)[10], "t4c 保存谓词：L11 变 rgb(93,97,102)")
# s3 备份是同色的另一布景（GOOD clips＋root10），验锚点同源
must("#1a1f26" in lines_of(S3)[10], "s3 备份 L11 同为 #1a1f26（NG 快速起点可用）")

# ---------- t5b：s4 DOM 两行块整移 ----------

print("== t5b DOM 对调（s4） ==")
must(line_no(S4, 'id="title"') == 18 and line_no(S4, 'id="sub"') == 20,
     "s4 title L18 / sub L20")
ls = S4.splitlines(keepends=True)
# 实拍：goto L20 行首 → SHIFT+DOWN×2（选区 = L20+L21 含各自换行）→ Ctrl+X
# → goto L18 行首 → Ctrl+V
cut = ls[19] + ls[20]
rest = ls[:19] + ls[21:]
swapped = "".join(rest[:17]) + cut + "".join(rest[17:])
must(rs._dom_swapped(swapped), "t5b 保存谓词：sub 物理行移到 title 之前")
must(sorted(swapped.splitlines()) == sorted(S4.splitlines()),
     "t5b 只移动行、不改字（行集合逐字不变）")
sub_after = lines_of(swapped)[line_no(swapped, 'id="sub"') - 1]
must('data-start="3"' in sub_after, "t5b 保存后二拍锚 data-start=\"3\" 在 sub 行")

# ---------- t5d0：s6 蓝块取景 ----------

print("== t5d0 遮挡块（s6） ==")
must(line_no(S6, 'id="block"') == 22, "s6 block 开标签在 L22")
block = lines_of(S6)[21]
select_span(block, 'id="block"', 'data-duration="10"')
print("PASS t5d0 block 行双锚同行")
must("background:#1f6feb;" in lines_of(S6)[24],
     "t5d0 scroll_anchor L25 含 background:#1f6feb;（style 跨行）")

# ---------- t6a：s5 #sut 行在 L26 ----------

print("== t6a 拼错选择器（s5） ==")
must(line_no(S5, "tl.fromTo('#sut'") == 26, "s5 #sut tween 在 L26")
sut = lines_of(S5)[25]
select_span(sut, "tl.fromTo('#sut'", "duration: 1")
print("PASS t6a #sut 行双锚同行")

# ---------- 七态终端断言（与六命令真机标定一致，2026-10-16） ----------

print("== 七态备份健康度（布景源文件） ==")
for name, needle in (
        ("s0", "Check 基线由 setup_scenes 保证"),):
    pass
for name, t in (("s0", S0), ("s1", S1), ("s2", S2), ("s3", S3),
                ("s4", S4), ("s5", S5), ("s6", S6)):
    must('gsap.min.js"></script>' in t or 'src="gsap.min.js"' in t,
         "%s 引本地 gsap.min.js" % name)

print()
if fails:
    print("锚点自检失败 %d 项：" % len(fails))
    for f in fails:
        print("  FAIL", f)
    sys.exit(1)
print("全部锚点自检通过，可以开拍。")
