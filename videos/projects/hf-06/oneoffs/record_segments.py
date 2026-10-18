# -*- coding: utf-8 -*-
r"""hf-06《给片子配上声音》正式录屏编排：16 take，1600×920@30 gdigrab。

素材先行（源文件只入 git，成片/母带不入）。布景状态机＝沙盒
F:\_hftest\hf06-media\backup\ 五权威态（setup_scenes.py 生成）＋三处
NPP 现场编辑（删 id / 删 muted / voice→voise），每 take 冷推、可单独重录。
机位同 hf-05：带锁标题终端（cmd 跑 check/normalize/beats/treatment）＋
便携 NPP 两身份，无浏览器/CDP/dev server（全部直接读磁盘文件）。

takes（对 STORYBOARD-FRAMEWORK.md 第三节；文案逐字以 MEDIA-FACTS.md 真机台账为准）：
  t0-good              s0 首跑 check，五段全绿 Check passed（别敲第二遍）
  t1a-del-id           NPP 删 video 的 ' id="demo"'、存盘
  t1b-noid-run         check 红 media_missing_id「will be FROZEN」（同屏 studio⚠）
  t2a-del-muted        reset s0：删 ' muted'、存盘
  t2b-nomuted-run      check 红 video_missing_muted（二选一声明声音立场）
  t3a-bad-src          reset s0：voice.wav→voise.wav、存盘
  t3b-badaudio-run     check 红 audio_src_not_found「will be silent」
  t4-missing           reset s4：missing_local_asset ×2 silently skip
  t5-sametrack         reset s5：duplicate_audio_track⚠ 但 Check passed（exit 0）
  t6-beats             reset s0：beats 出 music.wav 23 拍
  t7-norm-dry          reset s0：normalize dry-run（-21.8/-37.26/+7.5，wrote:false）
  t8-norm-write        接态：--write 写回 2.371374；再 dry：withinTolerance:true
  t9-ceiling           reset s9：exit1「needs 16.0 dB … +12 dB authoring ceiling」
  t10-badid            reset s0：--target bgn exit1「Target audio #bgn was not found」
                        ＋treatment --selector #dem exit1「Selector did not match」
  t11-treatment        reset s0：treatment --selector "#demo" --analyze --json
  t12-placeholder      reset s8：StaticGuard＋placeholder_media_url「will 404」

安全铁律（guard.py）：每个键鼠动作前过闸（前台＋落点双校验），只认标题含
_hftest\hf06-media 的隔离 NPP 与 hf06-rec 终端两个身份。用户一回机切自己的窗，
下一注入立即 UnsafeForeground 中止。不按进程名批量杀窗，不碰用户 WT/日常 NPP。

用法：
  python record_segments.py warmup        # 录制外：吞 npx 冷启＋目验输出形态
  python record_segments.py t0-good
  python record_segments.py t1a-del-id t1b-noid-run
  python record_segments.py all
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HF03_ONEOFFS = os.path.join(HERE, "..", "..", "hf-03", "oneoffs")
sys.path.insert(0, HF03_ONEOFFS)
sys.path.insert(0, HERE)

import guard  # noqa: E402
import npp_ops as n  # noqa: E402
import rec_automate as r  # noqa: E402
from blackmat import BlackMat  # noqa: E402

guard.install_input_guards(r)

# ---------- 常量 ----------

PROJ = r"F:\_hftest\hf06-media\proj"
HTML = os.path.join(PROJ, "index.html")
BACKUP = r"F:\_hftest\hf06-media\backup"
STATES = {
    "s0": "s0-good",
    "s4": "s4-missing",
    "s5": "s5-sametrack",
    "s8": "s8-placeholder",
    "s9": "s9-ceiling",
}

REC_DIR = r"F:\_hftest\hf06-rec\takes"
FRAME_DIR = r"F:\_hftest\hf06-rec\frames"
SCREEN_REC = r"F:\Data\gmeek-site\tools\screen-rec.js"

# 录区物理 (0,0,1600,920)（gdigrab，1920×1080@150%）。外框几何沿用 hf-05：
# Win11 右边 12px 圆角透明带，窗口摆 (-12,0,1624,928) 实体右缘正好 1600。
WND_X, WND_Y, WND_W, WND_H = -12, 0, 1624, 928
TERM_X, TERM_Y = -12, 0
TERM_W, TERM_H = 1632, 1000
REC_TERM_TITLE = "hf06-rec"

NPX = "npx --yes hyperframes@0.8.107"
CHECK = NPX + " check ."
BEATS = NPX + " beats ."
NORM_PREFIX = NPX + " normalize-audio --reference voice --target"
NORM_DRY = NORM_PREFIX + " bgm --json"
NORM_WRITE = NORM_PREFIX + " bgm --write --json"
NORM_BADID = NORM_PREFIX + " bgn --json"
TREAT = NPX + ' media-treatment --selector "#demo" --analyze --json'
TREAT_BAD = NPX + ' media-treatment --selector "#dem" --analyze --json'

# 等待时长（run_rehearsal.py 非录态真机 2026-10-18＋hf-05 gdigrab +20% 经验）：
# check 冷态 35.7s（GPU probe，warmup 吞）／错误短路 10–12s／warning 全段 26s；
# beats 16s（真出 23 拍）；normalize 9s/条（loudnorm 两遍）；treatment 11–13s。
CHECK_WAIT = 28
BEATS_WAIT = 20
NORM_WAIT = 14
TREAT_WAIT = 16
TYPE_NORM = 5.5     # normalize 命令 70+ 字符实测打字约 5s
TYPE_TREAT = 5.5

os.makedirs(REC_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

_mat = None
_term_hwnd = None


# ---------- 隔离 NPP 关窗（只认 _hftest\hf06-media 标题） ----------

def _enum_hf06_npp():
    """所有可见、标题含 _hftest\\hf06-media 的 Notepad++ 顶层窗。"""
    found = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        c = r.ctypes.create_unicode_buffer(64)
        r.u.GetClassNameW(wnd, c, 64)
        if c.value == "Notepad++" and r.u.IsWindowVisible(wnd):
            ln = r.u.GetWindowTextLengthW(wnd)
            b = r.ctypes.create_unicode_buffer(ln + 1)
            r.u.GetWindowTextW(wnd, b, ln + 1)
            if r"_hftest\hf06-media" in b.value:
                found.append((wnd, b.value))
        return True

    r.u.EnumWindows(cb, 0)
    return found


def _wnd_pid(wnd):
    pid = r.wintypes.DWORD()
    r.ctypes.windll.user32.GetWindowThreadProcessId(wnd, r.ctypes.byref(pid))
    return pid.value


def _pid_exe(pid):
    k = r.ctypes.windll.kernel32
    h = k.OpenProcess(0x1000, False, pid)
    if not h:
        return ""
    try:
        buf = r.ctypes.create_unicode_buffer(260)
        size = r.wintypes.DWORD(260)
        if k.QueryFullProcessImageNameW(h, 0, buf, r.ctypes.byref(size)):
            return buf.value
    finally:
        k.CloseHandle(h)
    return ""


def _dismiss_modal(owner):
    """外部修改「重新加载」框→Alt+Y 重载磁盘；其余保存确认→Alt+N。"""
    GetWindow = r.ctypes.windll.user32.GetWindow
    GetWindow.restype = r.wintypes.HWND
    GetWindow.argtypes = [r.wintypes.HWND, r.wintypes.UINT]
    dialogs = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        c = r.ctypes.create_unicode_buffer(32)
        r.u.GetClassNameW(wnd, c, 32)
        if (c.value == "#32770" and r.u.IsWindowVisible(wnd)
                and GetWindow(wnd, 4) == owner):
            dialogs.append(wnd)
        return True

    r.u.EnumWindows(cb, 0)
    acted = False
    for dlg in dialogs:
        ln = r.u.GetWindowTextLengthW(dlg)
        b = r.ctypes.create_unicode_buffer(ln + 1)
        r.u.GetWindowTextW(dlg, b, ln + 1)
        r.activate(dlg)
        guard.assert_fg_safe()
        if "重新加载" in b.value:
            r.hotkey("ALT", "Y")
        else:
            r.hotkey("ALT", "N")
        acted = True
        time.sleep(.6)
    return acted


def close_any_npp():
    """三轮 WM_CLOSE＋模态分类；仍存活按 PID 验明 npp-local 后 taskkill。"""
    for _round in range(3):
        found = _enum_hf06_npp()
        if not found:
            return
        for wnd, _ in found:
            r.u.PostMessageW(wnd, 0x0010, 0, 0)
        t0 = time.time()
        while time.time() - t0 < 3:
            time.sleep(.3)
            if not _enum_hf06_npp():
                return
        for wnd, _ in _enum_hf06_npp():
            _dismiss_modal(wnd)
        time.sleep(.5)
    for wnd, title in _enum_hf06_npp():
        pid = _wnd_pid(wnd)
        exe = _pid_exe(pid)
        if exe.lower().startswith(r"f:\_hftest\npp-local\\"):
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            time.sleep(.5)
        else:
            raise RuntimeError(
                "隔离 NPP 窗关不掉且 exe 不属于 npp-local，拒绝强杀："
                "pid=%s exe=%s title=%s" % (pid, exe, title))
    if _enum_hf06_npp():
        raise RuntimeError("三轮关闭＋兜底后仍有 _hftest\\hf06-media NPP 窗")


# ---------- 布景状态机 ----------

def reset(state, open_npp=False):
    """冷推权威态：关 NPP→backup/<state>/index.html 覆盖→可选开 NPP。

    终端 cwd 恒在 PROJ，覆盖文件后下一条命令立即读到新态，无需 cd。
    """
    assert state in STATES, state
    close_any_npp()
    n.hwnd = None
    time.sleep(.4)
    src = os.path.join(BACKUP, STATES[state], "index.html")
    if not os.path.exists(src):
        raise RuntimeError("权威备份缺失: " + src)
    shutil.copyfile(src, HTML)
    time.sleep(.4)
    if open_npp:
        npp_open()


def npp_open():
    """便携 NPP 开 HTML 摆入镜位（close_any_npp 之后调用，保新进程）。

    行号槽暗色两道关（hf-05 实测，NPP 7.8.8 便携）：①config.xml 的
    stylerTheme 必须指便携自身 stylers.xml；②词法样式落定后手工补发
    SETBACK/SETFORE。消息号以 Scintilla.h 实数为准：SETBACK=2052、
    SETFORE=2051；2050 是 STYLECLEARALL，误发会清空全部样式。
    COLORREF 为 BGR 序：#161b22→0x221B16、#8b949e→0x9E948B。
    补发后读回校验（本机 SciLexer 实测 GETBACK=2482：发 2052 纯红后
    2482 读回红；最小化/恢复/前后台切换均不回退）。hf-06 录前目验抓到
    一次开窗早期 flake（补发后仍白槽），故不盲信一次补发，读不回暗底
    就重发，三轮不中直接报错——白槽穿帮只能 NG 重录，必须开拍前拦住。
    """
    n.launch(HTML, x=WND_X, y=WND_Y, w=WND_W, h=WND_H)
    n.set_zoom(0)
    time.sleep(.3)
    s = n.active_scintilla()
    n._senda(s, n.SCI_SETSEL, 0, 0)
    time.sleep(2.0)  # 等词法样式应用完再补发，开窗即发会被样式刷新覆盖
    for attempt in range(3):
        s = n.active_scintilla()
        n._senda(s, 2052, 33, 0x221B16)  # SCI_STYLESETBACK 行号槽 #161b22
        n._senda(s, 2051, 33, 0x9E948B)  # SCI_STYLESETFORE 行号字 #8b949e
        time.sleep(.3)
        if (n._senda(s, 2482, 33, 0) & 0xFFFFFF) == 0x221B16:
            return
    raise RuntimeError("行号槽暗色补发三次未生效（读回 0x%06X），停止开拍"
                       % (n._senda(s, 2482, 33, 0) & 0xFFFFFF))


# ---------- 录制基元 ----------

def record(name, duration, action):
    out = os.path.join(REC_DIR, name + ".mp4")
    t0 = time.time()
    proc = subprocess.Popen(
        ["node", SCREEN_REC, out,
         "--width", "1600", "--height", "920", "--x", "0", "--y", "0",
         "-t", str(duration)],
        cwd=r"F:\Data\gmeek-site",
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(1.0)
    action()
    rest = duration - (time.time() - t0) - 1.2
    if rest > 0:
        time.sleep(rest)
    proc.wait(timeout=duration + 30)
    print(proc.stdout.read().strip()[-300:])
    extract_frames(name)
    return out


def extract_frames(name, every=2):
    src = os.path.join(REC_DIR, name + ".mp4")
    pat = os.path.join(FRAME_DIR, name + "-%02d.png")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", src, "-vf", "fps=1/%d,scale=800:-1" % every, pat],
                   check=True)
    print("frames:", name)


def park_mouse():
    r.mouse_move(12, 884)


# ---------- 终端 ----------

def open_rec_term():
    """独立 WT 窗（cmd，cwd/三变量就位），外框盖满录区。绝不动用户 WT。"""
    global _term_hwnd
    existing = r.find_window(REC_TERM_TITLE)
    if existing:
        _term_hwnd = existing
        r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
        r.move(_term_hwnd, TERM_X, TERM_Y, TERM_W, TERM_H)
        time.sleep(.4)
        r.activate(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(.4)
        return existing
    init = ('set "HYPERFRAMES_FONT_CACHE_DIR=F:\\_hftest\\.cache\\fonts" '
            '&& set "HYPERFRAMES_NO_UPDATE_CHECK=1" '
            '&& set "HYPERFRAMES_SKIP_SKILLS=1" && cls')
    # --suppressApplicationTitle 必须有：npx 运行时 SetConsoleTitle 会把 tab
    # 标题改成 npm 命令，白名单 startswith("hf06-rec") 立刻失配。
    subprocess.Popen(["wt.exe", "-w", "new", "--title", REC_TERM_TITLE,
                      "--suppressApplicationTitle",
                      "-d", PROJ, "cmd.exe", "/k", init])
    t0 = time.time()
    while time.time() - t0 < 20:
        h = r.find_window(REC_TERM_TITLE)
        if h:
            _term_hwnd = h
            break
        time.sleep(.5)
    if not _term_hwnd:
        raise RuntimeError("等不到 hf06-rec 终端窗口")
    time.sleep(1.2)
    r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
    r.move(_term_hwnd, TERM_X, TERM_Y, TERM_W, TERM_H)
    time.sleep(.5)
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.5)
    return _term_hwnd


def term_cmd(line, post=0.0):
    """在 hf06-rec 敲一条命令并回车。前台必须仍是隔离终端。"""
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.25)
    r.type_text(line, delay=.035)
    time.sleep(.2)
    guard.assert_fg_safe()
    r.tap("ENTER")
    if post:
        time.sleep(post)


def term_cls():
    term_cmd("cls")
    time.sleep(.7)


def _run_check(duration):
    """check 系通用 act：垫幕→敲 check→等报文→尾帧。"""
    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()
    return record(duration, 6 + CHECK_WAIT, act)


def take_warmup():
    """录制外吞 npx/headless 冷启（冷启曾实测 60s+）。check 跑两遍（一冷一热），
    再 beats/normalize/treatment 各一；目验终端输出形态后即可开拍。"""
    reset("s0")
    open_rec_term()
    for cmd, wait in [(CHECK, 90), (CHECK, 40),
                      (BEATS, BEATS_WAIT + 15),
                      (NORM_DRY, NORM_WAIT + 15),
                      (TREAT, TREAT_WAIT + 15)]:
        term_cmd(cmd, post=wait)
    term_cls()
    print("warmup 完成：冷启已吞；目验各命令输出形态后开拍")


# ---------- t0：s0 首跑 check，五段全绿 ----------

def take_t0_good():
    reset("s0")
    open_rec_term()
    term_cls()
    park_mouse()
    return _run_check("t0-good")


# ---------- t1：删 id → media_missing_id FROZEN ----------

def take_t1a_del_id():
    reset("s0", open_npp=True)
    # s0：<video id="demo" …> 行；' id="demo"' 全文唯一（check_anchors 闸）
    n.reveal_in_line(n.line_of('id="demo"'), ' id="demo"')
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.5)                # 开场：要删的身份证高亮
        r.tap("DELETE")
        time.sleep(.5)
        n.save(lambda t: 'id="demo"' not in t)
        time.sleep(.4)
        n.reveal_in_line(n.line_of("media/demo.mp4"), "playsinline")
        time.sleep(3.0)                # 删完：video 标签光秃秃
        park_mouse()

    return record("t1a-del-id", 12, act)


def take_t1b_noid_run():
    open_rec_term()
    term_cls()
    park_mouse()
    return _run_check("t1b-noid-run")


# ---------- t2：删 muted → video_missing_muted ----------

def take_t2a_del_muted():
    reset("s0", open_npp=True)
    n.reveal_in_line(n.line_of(" muted"), " muted")
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.5)                # 开场：muted 声音立场高亮
        r.tap("DELETE")
        time.sleep(.5)
        n.save(lambda t: " muted" not in t)
        time.sleep(.4)
        n.reveal_in_line(n.line_of("media/demo.mp4"), "playsinline")
        time.sleep(2.5)
        park_mouse()

    return record("t2a-del-muted", 10, act)


def take_t2b_nomuted_run():
    open_rec_term()
    term_cls()
    park_mouse()
    return _run_check("t2b-nomuted-run")


# ---------- t3：voice.wav→voise.wav → audio_src_not_found silent ----------

def take_t3a_bad_src():
    reset("s0", open_npp=True)
    # voice audio 续行 L29 src="media/voice.wav"；选文件名 9 字符整词覆盖
    n.reveal_in_line(n.line_of("media/voice.wav"), "voice.wav")
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.5)                # 开场：正确文件名高亮
        # Scintilla 有选区时打字＝覆盖选区：首字符替换选中串
        r.type_text("voise.wav", delay=.05)
        time.sleep(.4)
        n.save(lambda t: "media/voise.wav" in t and "media/voice.wav" not in t)
        time.sleep(.4)
        n.reveal_in_line(n.line_of("voise.wav"), "voise.wav")
        time.sleep(3.0)                # 错一个字母的文件名定格
        park_mouse()

    return record("t3a-bad-src", 12, act)


def take_t3b_badaudio_run():
    open_rec_term()
    term_cls()
    park_mouse()
    return _run_check("t3b-badaudio-run")


# ---------- t4：s4 视觉文件缺失 ----------

def take_t4_missing():
    reset("s4")
    open_rec_term()
    term_cls()
    park_mouse()
    return _run_check("t4-missing")


# ---------- t5：s5 同轨层叠（warning 但 passed，exit 0） ----------

def take_t5_sametrack():
    reset("s5")
    open_rec_term()
    term_cls()
    park_mouse()
    return _run_check("t5-sametrack")


# ---------- t6：beats 音乐轨出 23 拍 ----------

def take_t6_beats():
    reset("s0")
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(BEATS)
        time.sleep(BEATS_WAIT)          # 尾帧停 beats/media/music.wav.json
        park_mouse()

    return record("t6-beats", 4 + BEATS_WAIT, act)


# ---------- t7/t8：normalize dry-run / --write＋幂等 ----------

def take_t7_norm_dry():
    reset("s0")
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(NORM_DRY)
        time.sleep(NORM_WAIT)          # JSON 尾帧：wrote:false gainDb 7.5
        park_mouse()

    return record("t7-norm-dry", 8 + NORM_WAIT + 2, act)


def take_t8_norm_write():
    # 接 t7 态（dry-run 不写文件，index 仍 s0）；本 take 真改 volume
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(NORM_WRITE)
        time.sleep(NORM_WAIT)          # wrote:true，data-volume→2.371374
        term_cmd(NORM_DRY)
        time.sleep(NORM_WAIT - 2)      # withinTolerance:true 幂等尾帧
        park_mouse()

    return record("t8-norm-write",
                  4 + TYPE_NORM + NORM_WAIT + TYPE_NORM + NORM_WAIT, act)


# ---------- t9：s9 +12dB 天花板 ----------

def take_t9_ceiling():
    reset("s9")
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(NORM_DRY)
        time.sleep(NORM_WAIT)          # ok:false needs 16.0 dB
        park_mouse()

    return record("t9-ceiling", 8 + NORM_WAIT + 2, act)


# ---------- t10：id/selector 写错，exit1 但不动文件 ----------

def take_t10_badid():
    reset("s0")
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(NORM_BADID)
        time.sleep(NORM_WAIT)          # Target audio #bgn was not found（8.5s 非录态）
        term_cmd(TREAT_BAD)
        time.sleep(TREAT_WAIT)         # Selector did not match: #dem（8.8s 非录态）
        park_mouse()

    return record("t10-badid",
                  4 + TYPE_NORM + NORM_WAIT + TYPE_TREAT + TREAT_WAIT + 4, act)


# ---------- t11：treatment analyze 真选择器 ----------

def take_t11_treatment():
    reset("s0")
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(TREAT)
        time.sleep(TREAT_WAIT)         # suggestedPatch JSON 尾帧
        park_mouse()

    return record("t11-treatment", 8 + TREAT_WAIT, act)


# ---------- t12：s8 占位 URL ----------

def take_t12_placeholder():
    reset("s8")
    open_rec_term()
    term_cls()
    park_mouse()
    return _run_check("t12-placeholder")


TAKES = {
    "warmup": take_warmup,
    "t0-good": take_t0_good,
    "t1a-del-id": take_t1a_del_id,
    "t1b-noid-run": take_t1b_noid_run,
    "t2a-del-muted": take_t2a_del_muted,
    "t2b-nomuted-run": take_t2b_nomuted_run,
    "t3a-bad-src": take_t3a_bad_src,
    "t3b-badaudio-run": take_t3b_badaudio_run,
    "t4-missing": take_t4_missing,
    "t5-sametrack": take_t5_sametrack,
    "t6-beats": take_t6_beats,
    "t7-norm-dry": take_t7_norm_dry,
    "t8-norm-write": take_t8_norm_write,
    "t9-ceiling": take_t9_ceiling,
    "t10-badid": take_t10_badid,
    "t11-treatment": take_t11_treatment,
    "t12-placeholder": take_t12_placeholder,
}

ALL_TAKES = [k for k in TAKES if k != "warmup"]


def main():
    global _mat
    args = sys.argv[1:] or ["all"]
    if args == ["all"]:
        args = ALL_TAKES
    _mat = BlackMat()
    failed = False
    try:
        for name in args:
            print("\n===== take %s =====" % name, flush=True)
            TAKES[name]()
    except BaseException:
        failed = True
        raise
    finally:
        _mat.close()
        if not failed:
            # daemon Tcl 线程终结期 Tcl_AsyncDelete 是 tkinter/Windows 已知顽疾
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)


if __name__ == "__main__":
    main()
