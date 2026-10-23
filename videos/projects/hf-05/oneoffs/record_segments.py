# -*- coding: utf-8 -*-
r"""hf-05《check 门控》正式录屏编排：7 组 20 take，1600×920@30 gdigrab。

素材先行（源文件只入 git，成片/母带不入）。布景状态机＝沙盒
F:\_hftest\hf05-check\backup\ 七权威态（setup_scenes.py 生成），每 take
冷推、可单独重录。本片比 hf-04 简单：只有带锁标题终端（cmd 跑 check）＋
便携 NPP 两个身份，无浏览器/CDP/dev server（check 直接读磁盘文件）。

takes（对 STORYBOARD-FRAMEWORK.md 第 4 节 t1–t7）：
  t1-check-good        s0 首跑 check，六段全滚（首滚最完整，别敲第二遍）
  t2a-dur-del          NPP 删 title 的 data-duration、存盘
  t2b-dur-run          check：timeline_element_missing_timing⚠ 但 passed
  t3a-overflow-run     restore s2：clip_ends_past_root_duration⚠ 双修复
  t3b-root-fix-npp     镜头给 tail 行，root duration 10→13 现场敲、存盘
  t3c-root-fix-run     check 复绿
  t4a-color-bad-npp    title color #e6edf3→#1a1f26（接 t3 末态，不 restore）
  t4b-color-bad-run    check 红：Contrast 5✗ exit 1（全片唯一红灯高点）
  t4c-color-fix-npp    #1a1f26→rgb(93,97,102)（建议色，真机实测）
  t4d-color-fix-run    check 复绿 10/10；分两行 echo %ERRORLEVEL% 定格 0
  t5a-same-track-run   restore s4：同 track-index 重叠，全绿合法
  t5b-dom-swap         NPP 两块 DOM 顺序对调（Scintilla 消息整块上移，无剪贴板）
  t5c-dom-swap-run     check 仍全绿
  t5d0-occlude-code    restore s6：NPP 静场给预置蓝块代码（整块新增跳切）
  t5d-occlude-run      check 红：text_occluded #title inside #block 9/9
  t6a-nulltarget-code  restore s5：NPP 静场给 #sut 拼写行
  t6b-nulltarget-run   check：Runtime 3⚠ 但 passed（动画静默失踪）
  t7a-kf               restore s0：keyframes 列表＋--shot 洋葱皮
  t7b-inspect          inspect（deprecated 提示改用 check）
  t7c-beats            beats（无音乐轨提示）

安全铁律（2026-10-12 误触事故后固化，guard.py）：每个键鼠动作前过闸
（前台＋落点双校验），只认标题含 _hftest\hf05-check 的隔离 NPP 与
hf05-rec 终端两个身份。用户一回机切自己的窗，下一注入立即
UnsafeForeground 中止。不按进程名批量杀窗，不碰用户 WT/日常 NPP。

用法：
  python record_segments.py warmup        # 录制外：吞 npx 冷启＋标定等待
  python record_segments.py t1-check-good
  python record_segments.py t2a-dur-del t2b-dur-run
  python record_segments.py all
"""
import io
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

PROJ = r"F:\_hftest\hf05-check\proj"
HTML = os.path.join(PROJ, "index.html")
BACKUP = r"F:\_hftest\hf05-check\backup"
STATES = {
    "s0": "s0-good",
    "s1": "s1-no-duration",
    "s2": "s2-overflow",
    "s3": "s3-contrast",
    "s4": "s4-same-track",
    "s5": "s5-null-target",
    "s6": "s6-occluded",
}

REC_DIR = r"F:\_hftest\hf05-rec\takes"
FRAME_DIR = r"F:\_hftest\hf05-rec\frames"
# 仓库根＝HERE（videos/projects/<片>/oneoffs）上溯四级，随仓库位置自适应
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SCREEN_REC = os.path.join(REPO_ROOT, "tools", "screen-rec.js")

# 录区物理 (0,0,1600,920)（gdigrab，1920×1080@150%）。外框几何沿用 hf-04：
# Win11 右边 12px 圆角透明带，窗口摆 (-12,0,1624,928) 实体右缘正好 1600。
WND_X, WND_Y, WND_W, WND_H = -12, 0, 1624, 928
TERM_X, TERM_Y = -12, 0
TERM_W, TERM_H = 1632, 1000
REC_TERM_TITLE = "hf05-rec"

NPX = "npx --yes hyperframes@0.8.107"
CHECK = NPX + " check ."
KEYFRAMES = NPX + " keyframes"
SHOT_CMD = KEYFRAMES + " --shot rec-shots/onion.png"
INSPECT = NPX + " inspect ."
BEATS = NPX + " beats ."

# 等待时长（2026-10-16 无注入 subprocess 真机标定，包缓存热态）：
# check 六态全部 20.0–21.2s（冷启另算，warmup 吞）；keyframes 7.9s；
# keyframes --shot 14.1s；inspect 15.8s；beats 8.3s。录制态 gdigrab 负载
# 下留余量（hf-04 经验 +20%）：check 取 28，其余各 +4~5。
# 2026-10-16 正式代录实测：gdigrab 同机负载比 hf-04 经验更重——keyframes
# 列表 ~9.5s 才刷出（KF_WAIT=12 只留 ~2.5s 稳定窗）；--shot 20s 仍停在
# GPU probe、洋葱皮路径未出（同机非录态实测 16.4s）；beats 10s+ 未出
# （非录态 8.6s）。故 KF 16／SHOT 28／BEATS 18，t7a 片长 52s、t7c 22s。
CHECK_WAIT = 28
KF_WAIT = 16
SHOT_WAIT = 28
INSP_WAIT = 21
BEATS_WAIT = 18

os.makedirs(REC_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

_mat = None
_term_hwnd = None


# ---------- 隔离 NPP 关窗（只认 _hftest\hf05-check 标题） ----------

def _enum_hf05_npp():
    """所有可见、标题含 _hftest\\hf05-check 的 Notepad++ 顶层窗。"""
    found = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        c = r.ctypes.create_unicode_buffer(64)
        r.u.GetClassNameW(wnd, c, 64)
        if c.value == "Notepad++" and r.u.IsWindowVisible(wnd):
            ln = r.u.GetWindowTextLengthW(wnd)
            b = r.ctypes.create_unicode_buffer(ln + 1)
            r.u.GetWindowTextW(wnd, b, ln + 1)
            if r"_hftest\hf05-check" in b.value:
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
        found = _enum_hf05_npp()
        if not found:
            return
        for wnd, _ in found:
            r.u.PostMessageW(wnd, 0x0010, 0, 0)
        t0 = time.time()
        while time.time() - t0 < 3:
            time.sleep(.3)
            if not _enum_hf05_npp():
                return
        for wnd, _ in _enum_hf05_npp():
            _dismiss_modal(wnd)
        time.sleep(.5)
    for wnd, title in _enum_hf05_npp():
        pid = _wnd_pid(wnd)
        exe = _pid_exe(pid)
        if exe.lower().startswith(r"f:\_hftest\npp-local\\"):
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            time.sleep(.5)
        else:
            raise RuntimeError(
                "隔离 NPP 窗关不掉且 exe 不属于 npp-local，拒绝强杀："
                "pid=%s exe=%s title=%s" % (pid, exe, title))
    if _enum_hf05_npp():
        raise RuntimeError("三轮关闭＋兜底后仍有 _hftest\\hf05-check NPP 窗")


# ---------- 布景状态机 ----------

def reset(state, open_npp=False):
    """冷推权威态：关 NPP→backup/<state>/index.html 覆盖→可选开 NPP。

    终端 cwd 恒在 PROJ，覆盖文件后下一次 check 立即读到新态，无需 cd。
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

    行号槽暗色（真机排查 2026-10-16，NPP 7.8.8 便携）两道关：
    1. config.xml 的 stylerTheme 必须指便携自身 stylers.xml；被绝对路径钉到
       %%APPDATA%% 的浅色 stylers.xml 时整个编辑区都是白底（换机重建便携 NPP
       必查，仓库外配置不入 git）。
    2. 即便暗色 stylers.xml 生效，STYLE_LINENUMBER(33) 的前景/背景在这版启动
       流程里没被应用（真机 raw：fg=0、margin 留系统色 F0F0F0），控件可见、
       词法样式落定后手工补发一次。
    消息号以 Scintilla.h 实数为准，别凭记忆：SETBACK=2052、SETFORE=2051；
    2050 是 SCI_STYLECLEARALL——误当 SETFORE 发出会清空全部样式（行号槽回白、
    fg 读回归零），本次排查在这条上耗了最久。COLORREF 为 BGR 序：
    #161b22→0x221B16、#8b949e→0x9E948B。同实例不切语言不会被重刷。
    """
    n.launch(HTML, x=WND_X, y=WND_Y, w=WND_W, h=WND_H)
    n.set_zoom(0)
    time.sleep(.3)
    s = n.active_scintilla()
    n._senda(s, n.SCI_SETSEL, 0, 0)
    # 等词法样式应用完再补发（开窗即发会被随后的样式刷新覆盖）
    time.sleep(2.0)
    s = n.active_scintilla()
    n._senda(s, 2052, 33, 0x221B16)  # SCI_STYLESETBACK 行号槽 #161b22
    n._senda(s, 2051, 33, 0x9E948B)  # SCI_STYLESETFORE 行号字 #8b949e


def _title_line(text):
    return next(line for line in text.splitlines() if 'id="title"' in line)


def _backup_line(state, needle):
    """权威备份中含 needle 的物理行（无行尾），save 谓词收紧到行逐字比对。"""
    with io.open(os.path.join(BACKUP, STATES[state], "index.html"),
                 encoding="utf-8") as f:
        return next(line.rstrip("\n") for line in f if needle in line)


# ---------- NPP 入镜编辑原语 ----------

def goto_line_start(line_no):
    """Ctrl+G 跳行，双 HOME 到物理行首（虚缩进防第一拍落到缩进位）。"""
    n._activate()
    r.hotkey("CTRL", "G")
    time.sleep(.5)
    r.type_text(str(line_no), delay=.03)
    time.sleep(.15)
    r.tap("ENTER")
    time.sleep(.4)
    r.tap("HOME")
    time.sleep(.06)
    r.tap("HOME")
    time.sleep(.12)


def type_replacing_selection(text, delay=.05):
    """有选区时逐字输入：首字符替换选区，余追加（中英通用 Unicode 注入）。"""
    r.type_text(text, delay=delay)
    time.sleep(.25)


def dom_swap_edits():
    """s4 专用入镜序列：把 #sub 两行（L20-21）整块移到 #title（L18-19）前。

    纯 Scintilla 消息、不碰系统剪贴板：t5b 首录走 Ctrl+X/V，录制期间剪贴板
    被后台程序抢占、title 行被注入无关本地路径，整片作废（2026-10-16）。
    正解＝按 UTF-8 字节位置发 SETSELECTIONSTART/END 选 L20 行首..L22 行首
    （含两行各自尾换行，移动后 </div> 不会挤行），再连发两次
    SCI_MOVESELECTEDLINESUP 整块上移两格。键盘 SHIFT+DOWN 在 Ctrl+G 之后
    建选区锚点不稳（彩排实测选区错位、块反向下移），消息建选区才确定
    （彩排 swapped=True、行集合逐字不变、长度 1204）。
    消息号以 Scintilla-788.h 实数为准：SETSELECTIONSTART=2142、
    SETSELECTIONEND=2144、MOVESELECTEDLINESUP=2620（别凭记忆）。
    """
    s = n.active_scintilla()
    n._senda(s, 2142, n._byte_position(20), 0)
    time.sleep(.5)
    n._senda(s, 2144, n._byte_position(22), 0)   # L22 行首＝含 L20/L21 尾换行
    time.sleep(1.0)                               # 拍 sub 两行整选
    n._senda(s, 2620, 0, 0)
    time.sleep(.6)
    n._senda(s, 2620, 0, 0)
    time.sleep(.6)


def _dom_swapped(text):
    lines = text.splitlines()
    i_sub = next(i for i, line in enumerate(lines) if 'id="sub"' in line)
    i_title = next(i for i, line in enumerate(lines) if 'id="title"' in line)
    return i_sub < i_title


# ---------- 录制基元 ----------

def record(name, duration, action):
    out = os.path.join(REC_DIR, name + ".mp4")
    t0 = time.time()
    proc = subprocess.Popen(
        ["node", SCREEN_REC, out,
         "--width", "1600", "--height", "920", "--x", "0", "--y", "0",
         "-t", str(duration)],
        cwd=REPO_ROOT,
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
    # 标题改成 npm 命令，白名单 startswith("hf05-rec") 立刻失配。
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
        raise RuntimeError("等不到 hf05-rec 终端窗口")
    time.sleep(1.2)
    r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
    r.move(_term_hwnd, TERM_X, TERM_Y, TERM_W, TERM_H)
    time.sleep(.5)
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.5)
    return _term_hwnd


def term_cmd(line, post=0.0):
    """在 hf05-rec 敲一条命令并回车。前台必须仍是隔离终端。"""
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


def take_warmup():
    """录制外吞 npx/headless 冷启（全新 cmd 首轮冷启曾实测 68s），并让
    rec-shots/ 就位。跑两遍 check：第一遍冷、第二遍热，墙钟看终端自感；
    精确计时另用无注入 subprocess 标定回填 CHECK_WAIT。"""
    reset("s0")
    os.makedirs(os.path.join(PROJ, "rec-shots"), exist_ok=True)
    open_rec_term()
    for cmd, wait in [(CHECK, 90), (CHECK, 40),
                      (KEYFRAMES, KF_WAIT + 15),
                      (SHOT_CMD, SHOT_WAIT + 15),
                      (INSPECT, INSP_WAIT + 15),
                      (BEATS, BEATS_WAIT + 15)]:
        term_cmd(cmd, post=wait)
    term_cls()
    print("warmup 完成：冷启已吞；目验终端各命令输出形态后回填等待常量")


# ---------- t1：s0 首跑 check，六段全滚 ----------

def take_t1_check_good():
    reset("s0")
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)     # Check passed＋六段完整尾帧
        park_mouse()

    return record("t1-check-good", 6 + CHECK_WAIT, act)


# ---------- t2：删 data-duration → warning 但 passed ----------

def take_t2a_dur_del():
    reset("s0", open_npp=True)
    # s0 L18 是 title 开标签；选区先落在 data-duration="10"
    n.reveal_in_line(n.line_of('id="title"'), ' data-duration="10"', '"10"')
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.5)                # 开场：要删的属性高亮
        r.tap("DELETE")                # 删选区（含前导空格，行尾收在 data-start）
        time.sleep(.5)
        # 谓词收紧到整行逐字等于 s1 备份（旧谓词只查 data-duration 缺席，
        # 多删/少删空格也会过）：删选区含前导空格，行尾收在 data-start。
        n.save(lambda t: _title_line(t) == _backup_line("s1", 'id="title"'))
        time.sleep(.4)
        n.reveal_in_line(n.line_of('id="title"'), 'data-start="0"', 'data-start="0"')
        time.sleep(3.0)                # 删完的行尾
        park_mouse()

    return record("t2a-dur-del", 12, act)


def take_t2b_dur_run():
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()

    return record("t2b-dur-run", 6 + CHECK_WAIT, act)


# ---------- t3：越界双修复 → 现场改 root 13 复绿 ----------

def take_t3a_overflow_run():
    reset("s2")                        # 关 NPP，覆盖 s2
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()

    return record("t3a-overflow-run", 6 + CHECK_WAIT, act)


def take_t3b_root_fix_npp():
    npp_open()                         # t3a 已覆盖 s2，这里只开编辑器
    # s2：tail 在 L22（data-start="8" data-duration="5"）
    n.reveal_in_line(22, 'data-start="8"', 'data-duration="5"')
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(3.0)                # 「第八秒进来待五秒」先给彩蛋行
        # root L17：data-duration="10"（行内第一个 "10"，1080 在其后不抢）
        n.reveal_in_line(17, "10", "10")
        time.sleep(1.0)
        type_replacing_selection("13")
        time.sleep(.8)
        n.save(lambda t: 'data-duration="13"' in t)
        time.sleep(1.8)
        park_mouse()

    return record("t3b-root-fix-npp", 14, act)


def take_t3c_root_fix_run():
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()

    return record("t3c-root-fix-run", 6 + CHECK_WAIT, act)


# ---------- t4：对比度主线（接 t3 末态：s2＋root13） ----------

def take_t4a_color_bad_npp():
    r.activate(n.hwnd)                 # t3c 把终端留在前台
    time.sleep(.3)
    # CSS L11：#title { ... color: #e6edf3; }
    n.reveal_in_line(11, "#e6edf3")
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.2)
        type_replacing_selection("#1a1f26")
        time.sleep(.8)
        n.save(lambda t: "#1a1f26" in t)
        time.sleep(2.2)
        park_mouse()

    return record("t4a-color-bad-npp", 11, act)


def take_t4b_color_bad_run():
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)     # Check failed＋5✗ 尾帧
        park_mouse()

    return record("t4b-color-bad-run", 6 + CHECK_WAIT, act)


def take_t4c_color_fix_npp():
    r.activate(n.hwnd)
    time.sleep(.3)
    n.reveal_in_line(11, "#1a1f26")
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.2)
        type_replacing_selection("rgb(93,97,102)")
        time.sleep(.8)
        n.save(lambda t: "rgb(93,97,102)" in t)
        time.sleep(2.2)
        park_mouse()

    return record("t4c-color-fix-npp", 12, act)


def take_t4d_color_fix_run():
    """复绿＋分两行敲 echo %ERRORLEVEL%（同行 & 会读旧值录假结果）。

    时长坑（2026-10-16 首版实证）：term_cmd 逐字实测约 0.07s/字（delay=.035
    外加 keyup 开销），CHECK 回车约在片内 5.8s；check 录制态 ~27s 回提示符。
    首版 sleep(CHECK_WAIT+5)=33s 才敲 echo，18 字打完约 35.5s——但片长只有
    40s，echo 整句被片长切掉（抽帧彻查 33.5–39.3s 全是无提示符的静态终态，
    零字符入镜）。改 sleep 28s（echo 开打 ~34s，落在提示符回来 7s 后），
    片长 44s，尾帧 0 定格留 8s 稳定窗。
    """
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT)         # ~34s 敲 echo，提示符 27s 已回，不进 npx stdin
        term_cmd("echo %ERRORLEVEL%")
        time.sleep(6.0)                # 尾帧 0 定格
        park_mouse()

    return record("t4d-color-fix-run", 12 + CHECK_WAIT + 4, act)


# ---------- t5：同轨合法＋DOM 对调仍绿＋遮挡红 ----------

def take_t5a_same_track_run():
    reset("s4")
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()

    return record("t5a-same-track-run", 6 + CHECK_WAIT, act)


def take_t5b_dom_swap():
    npp_open()
    # s4：title L18-19、sub L20-21；开场选区给 title 轨道属性，scroll_anchor
    # 压到 L21 让四块同框（否则 L20-21 在屏外，观众看不到被选中的 sub）
    n.reveal_in_line(18, 'id="title"', 'data-start="0"',
                     scroll_anchor=(21, "color:#7ee787;"))
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.5)                # 两块现状同框
        dom_swap_edits()
        time.sleep(.4)
        n.save(_dom_swapped)
        time.sleep(.4)
        # 对调后两块同框：sub 已在 title 之上（L21 此刻是 title 续行）
        n.reveal_in_line(n.line_of('id="sub"'), 'id="sub"', 'data-start="3"',
                         scroll_anchor=(21, "data-track-index"))
        time.sleep(2.6)
        park_mouse()

    return record("t5b-dom-swap", 17, act)


def take_t5c_dom_swap_run():
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()

    return record("t5c-dom-swap-run", 6 + CHECK_WAIT, act)


def take_t5d0_occlude_code():
    reset("s6", open_npp=True)
    # s6：block L22-25（style 跨行，background 在 L25）；开场选区给块声明，
    # scroll_anchor 保蓝底样式行同框
    n.reveal_in_line(22, 'id="block"', 'data-duration="10"',
                     scroll_anchor=(25, "background:#1f6feb;"))
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(5.0)                # 整块新增，镜头先给代码（跳切）
        park_mouse()

    return record("t5d0-occlude-code", 6, act)


def take_t5d_occlude_run():
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()

    return record("t5d-occlude-run", 6 + CHECK_WAIT, act)


# ---------- t6：GSAP 拼目标，3 warning 但 passed ----------

def take_t6a_nulltarget_code():
    reset("s5", open_npp=True)
    # s5：GOOD clips 占 L18-21、</div>L22、<script>L23，TIMELINE_NULL
    # 起 L24——拼错 tween 是第 3 行，在 L26
    n.reveal_in_line(26, "tl.fromTo('#sut'", "duration: 1")
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(5.0)
        park_mouse()

    return record("t6a-nulltarget-code", 6, act)


def take_t6b_nulltarget_run():
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(CHECK)
        time.sleep(CHECK_WAIT + 4)
        park_mouse()

    return record("t6b-nulltarget-run", 6 + CHECK_WAIT, act)


# ---------- t7：体检三连 ----------

def take_t7a_kf():
    reset("s0")                        # 关 NPP
    os.makedirs(os.path.join(PROJ, "rec-shots"), exist_ok=True)
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(KEYFRAMES)
        time.sleep(KF_WAIT)
        term_cls()
        term_cmd(SHOT_CMD)
        time.sleep(SHOT_WAIT)          # 尾帧停洋葱皮输出路径
        park_mouse()

    return record("t7a-kf", 8 + KF_WAIT + SHOT_WAIT, act)


def take_t7b_inspect():
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(INSPECT)
        time.sleep(INSP_WAIT)          # deprecated, use check 尾帧
        park_mouse()

    return record("t7b-inspect", 4 + INSP_WAIT, act)


def take_t7c_beats():
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(BEATS)
        time.sleep(BEATS_WAIT)         # 无音乐轨提示尾帧
        park_mouse()

    return record("t7c-beats", 4 + BEATS_WAIT, act)


TAKES = {
    "warmup": take_warmup,
    "t1-check-good": take_t1_check_good,
    "t2a-dur-del": take_t2a_dur_del,
    "t2b-dur-run": take_t2b_dur_run,
    "t3a-overflow-run": take_t3a_overflow_run,
    "t3b-root-fix-npp": take_t3b_root_fix_npp,
    "t3c-root-fix-run": take_t3c_root_fix_run,
    "t4a-color-bad-npp": take_t4a_color_bad_npp,
    "t4b-color-bad-run": take_t4b_color_bad_run,
    "t4c-color-fix-npp": take_t4c_color_fix_npp,
    "t4d-color-fix-run": take_t4d_color_fix_run,
    "t5a-same-track-run": take_t5a_same_track_run,
    "t5b-dom-swap": take_t5b_dom_swap,
    "t5c-dom-swap-run": take_t5c_dom_swap_run,
    "t5d0-occlude-code": take_t5d0_occlude_code,
    "t5d-occlude-run": take_t5d_occlude_run,
    "t6a-nulltarget-code": take_t6a_nulltarget_code,
    "t6b-nulltarget-run": take_t6b_nulltarget_run,
    "t7a-kf": take_t7a_kf,
    "t7b-inspect": take_t7b_inspect,
    "t7c-beats": take_t7c_beats,
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
            # 成功路径直退：daemon Tcl 线程终结期 Tcl_AsyncDelete 是
            # tkinter/Windows 已知顽疾，与素材无关；子进程均已 wait。
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(0)


if __name__ == "__main__":
    main()
