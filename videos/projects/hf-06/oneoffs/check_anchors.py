# -*- coding: utf-8 -*-
r"""hf-06 录前静态自检：record_segments 的取景锚点/三现场编辑 vs backup 五态。

纯文件校验，不碰桌面、不启 NPP，秒级跑完。reveal_in_line 的 start/end 锚
必须落在同一物理行（跨行直接 AssertionError，实拍即翻车）；入镜编辑全是
「选区→DELETE/打字覆盖选区→save」，本脚本在磁盘文本上镜像每一处替换，
并回放 record_segments 里的 save 谓词：

  python check_anchors.py

布景态来源：F:\_hftest\hf06-media\backup\<state>\index.html（setup_scenes
生成，calibrate_media 校准响度）。改任何锚点/编辑序列后必须先跑本脚本；
退出码非 0 不许开拍。
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_scenes as S  # noqa: E402

ROOT = S.DEFAULT_ROOT
BK = os.path.join(ROOT, "backup")
STATES = {"s0": "s0-good", "s4": "s4-missing", "s5": "s5-sametrack",
          "s8": "s8-placeholder", "s9": "s9-ceiling"}
MEDIA = os.path.join(ROOT, "proj", "media")
CALIB = os.path.join(S.P, "build", "media-calibration.json")

fails = []


def must(cond, msg):
    if cond:
        print("PASS", msg)
    else:
        fails.append(msg)
        print("FAIL", msg)


def read_state(name):
    p = os.path.join(BK, STATES[name], "index.html")
    if not os.path.exists(p):
        raise SystemExit("权威备份缺失: " + p)
    return io.open(p, encoding="utf-8").read()


def line_no(text, sub, occurrence=1):
    """镜像 n.line_of（磁盘，1 起）。"""
    n = 0
    for i, line in enumerate(text.splitlines(), 1):
        if sub in line:
            n += 1
            if n == occurrence:
                return i
    raise AssertionError("line_of(%r) 未命中" % sub)


def select_span(line, start):
    """镜像 reveal_in_line 单行锚点，返回 (c1, c2)；锚缺失即翻车。"""
    c1 = line.find(start)
    if c1 < 0:
        raise AssertionError("行内找不到锚 %r" % start)
    return c1, c1 + len(start)


def replace_selection(text, line_no_, start, typed):
    """镜像「reveal 选区→打字（DELETE＝typed=''）覆盖」后的磁盘文本。"""
    ls = text.splitlines()
    line = ls[line_no_ - 1]
    c1, c2 = select_span(line, start)
    ls[line_no_ - 1] = line[:c1] + typed + line[c2:]
    return "\n".join(ls) + ("\n" if text.endswith("\n") else "")


S0 = read_state("s0")
S4 = read_state("s4")
S5 = read_state("s5")
S8 = read_state("s8")
S9 = read_state("s9")

# ---------- 硬闸：权威备份必须纯 LF（Scintilla 字节锚点按 LF 标） ----------
print("== 五态备份行结束符（bytes 闸） ==")
for st, txt in (("s0", S0), ("s4", S4), ("s5", S5), ("s8", S8), ("s9", S9)):
    raw = io.open(os.path.join(BK, STATES[st], "index.html"), "rb").read()
    must(b"\r\n" not in raw, "%s/index.html 纯 LF、无 CRLF（%d 字节）" % (st, len(raw)))

# ---------- 三现场编辑锚点：s0 全文唯一 ----------
print("== 三 NPP 编辑锚点唯一性 ==")
for anchor in (' id="demo"', " muted", "media/voice.wav"):
    must(S0.count(anchor) == 1,
         "s0 中 %r 恰好 1 次（实测 %d）" % (anchor, S0.count(anchor)))

# ---------- 行号闸（setup_scenes HEAD+CLIPS_GOOD 物理布局，2026-10-18 实测） ----------
print("== 取景行号（NPP 跳转/行内选区） ==")
n_demo = line_no(S0, 'id="demo"')
n_muted = line_no(S0, " muted")
n_voice = line_no(S0, "media/voice.wav")
must(n_demo == 24, "video#demo 开标签在 L24（实测 L%d）" % n_demo)
must(n_muted == 25, "muted/playsinline 续行在 L25（实测 L%d）" % n_muted)
must(n_voice == 29, "audio#voice src 续行在 L29（实测 L%d）" % n_voice)

# ---------- t1a：L24 删 ' id="demo"' → media_missing_id FROZEN ----------
print("== t1a 删 id（s0 → 现场态） ==")
row24 = S0.splitlines()[23]
c1, c2 = select_span(row24, ' id="demo"')
must(row24[c1:c2] == ' id="demo"', "t1a 选区恰好是 ' id=\"demo\"'（10 字符）")
t1 = replace_selection(S0, 24, ' id="demo"', "")
must('id="demo"' not in t1, "t1a save 谓词：id=\"demo\" 消失")
must('<video class="clip"' in t1.splitlines()[23],
     "t1a 删除后 L24 秃开标签 <video class=\"clip\"")
must("playsinline" in t1.splitlines()[24], "t1a 二拍：L25 仍含 playsinline")

# ---------- t2a：L25 删 ' muted' → video_missing_muted ----------
print("== t2a 删 muted（s0 → 现场态） ==")
row25 = S0.splitlines()[24]
c1, c2 = select_span(row25, " muted")
must(row25[c1:c2] == " muted", "t2a 选区恰好是 ' muted'（6 字符）")
t2 = replace_selection(S0, 25, " muted", "")
must(" muted" not in t2, "t2a save 谓词：muted 消失")
must('src="media/demo.mp4" playsinline>' in t2.splitlines()[24],
     "t2a 删除后 L25＝src 直接接 playsinline")
must(line_no(t2, "media/demo.mp4") == line_no(t2, "playsinline") == 25,
     "t2a 二拍：media/demo.mp4 与 playsinline 同在 L25")

# ---------- t3a：L29 voice.wav 选区打字覆盖 voise.wav → audio_src_not_found ----------
print("== t3a voice.wav→voise.wav（s0 → 现场态） ==")
row29 = S0.splitlines()[28]
c1, c2 = select_span(row29, "voice.wav")
must(row29[c1:c2] == "voice.wav", "t3a 选区恰好是 voice.wav（9 字符）")
t3 = replace_selection(S0, 29, "voice.wav", "voise.wav")
must("media/voise.wav" in t3 and "media/voice.wav" not in t3,
     "t3a save 谓词：media/voise.wav 在、media/voice.wav 消失")
must('id="voice"' in t3.splitlines()[27], "t3a 只改文件名，L28 id=\"voice\" 完好")
must(line_no(t3, "voise.wav") == 29, "t3a 二拍：voise.wav 在 L29")

# ---------- 其余四态差异点（take 起点闸） ----------
print("== s4/s5/s8/s9 差异点 ==")
must('src="media/gone.mp4"' in S4 and 'src="media/gone.png"' in S4
     and "media/demo.mp4" not in S4, "s4：demo/pic 引用改 gone.*、文件不在")
s5_idx3 = [ln for ln in S5.splitlines() if 'data-track-index="3"' in ln]
must(len(s5_idx3) == 2, "s5：voice＋bgm 同在 track 3（实测 %d 行）" % len(s5_idx3))
must('src="https://example.com/voice.wav"' in S8
     and "media/voice.wav" not in S8, "s8：voice src 是占位 https URL")
must('src="media/music15.wav" data-volume="0.15"' in S9,
     "s9：bgm 换 music15.wav＋data-volume 0.15")

# ---------- 公共健康度 ----------
print("== 五态公共健康度 ==")
for st, txt in (("s0", S0), ("s4", S4), ("s5", S5), ("s8", S8), ("s9", S9)):
    must('src="gsap.min.js"' in txt, "%s 引本地 gsap.min.js" % st)
    must("data-timeline-role=\"music\"" in txt, "%s bgm 带 music 角色（beats 轨）" % st)

# ---------- 素材与校准台账（calibrate_media.py 产物） ----------
print("== 校准素材/台账 ==")
for f in ("voice.wav", "music.wav", "music15.wav", "demo.mp4", "pic.png"):
    must(os.path.exists(os.path.join(MEDIA, f)), "proj/media/%s 存在" % f)
if not os.path.exists(CALIB):
    must(False, "校准台账存在（先跑 calibrate_media.py）")
else:
    calib = json.loads(io.open(CALIB, encoding="utf-8").read())
    d = calib["display"]
    must(d["voice_lufs"] == -21.8, "台账 voice 显示 -21.8（实测 %s）" % d["voice_lufs"])
    must(d["ceiling_db"] == 16.0, "台账 ceiling 显示 16.0（实测 %s）" % d["ceiling_db"])
    print("    music %s LUFS／gainDb %s／写回 %s／music15 系数 %s"
          % (d["music_lufs"], calib["gainDb"], calib["volume_written"],
             calib["music15_coef"]))

print()
if fails:
    print("锚点自检失败 %d 项：" % len(fails))
    for f in fails:
        print("  FAIL", f)
    sys.exit(1)
print("全部锚点自检通过，可以开拍。")
