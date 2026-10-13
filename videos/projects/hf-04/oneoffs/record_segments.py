# -*- coding: utf-8 -*-
r"""hf-04《seek》正式录屏编排：11 个 take，1600×920@30 gdigrab。

素材先行（源文件只入 git，成片不入）。布景状态机＝沙盒 backup 五权威态，
每个 take 冷推、可单独重录：

  s0-static     静态 clips：title 2-6「砰」地出现（上一集成果）
  s1-css        title 加 @keyframes flyin（CSS 时钟被运行时接管，三帧全对）
  s2-timer      setInterval 计数器页（data-no-timeline，seek 不了、check 全绿）
  s3-gsap-skel  骨架：paused 空轴＋注册行，fromTo 是一条注释
  s4-final      注释换成三条 fromTo 挂 2/3/6（GSAP 正解）

takes（对粗稿行号）：
  seg1  rec-play-static    Edge/Studio 播放 s0：2s 砰出现、3s 卡片、6s 副标题
  seg2a rec-css-keyframes  NPP 写 @keyframes＋animation 行（s0→s1，入镜）
  seg2b rec-play-css       Studio 播放 s1：标题飞入
  seg3  rec-snap-css       终端 snapshot 2.1/2.5/2.9 两轮＋fc /b 逐字节复验
  seg4a rec-timer-code     NPP 展示 s2：tick 元素＋setInterval
  seg4b rec-play-timer     Studio 播放 s2：数字半秒一跳
  seg5a rec-snap-timer     终端 snapshot --at 2 连截三张（同一秒三个样）
  seg5b rec-check-pass     终端 npm run check 全绿（留 42s）
  seg6  rec-gsap-three     NPP 三件套：指认 paused/注册行，注释换三条 fromTo
  seg7  rec-play-final     Studio 播放 s4：浮、弹、进场各就各位
  seg8  rec-console-seek   裸 player 窗＋DevTools 亲手 __player.seek 矩阵
  seg9  rec-render         （可选，不入 all）终端 npm run render 出片日志

安全铁律（2026-10-12 误触用户 WT 事故后固化）：
  每个键鼠动作前过 guard（前台＋落点双校验）；只认隔离 Edge（9222）、
  标题含 _hftest\hf04-seek 的隔离 NPP、hf04-rec 终端三个身份。用户一回机
  把自己的窗口切前台，下一个动作立即 UnsafeForeground 中止。不按进程名
  批量杀窗，不碰用户 WT/主 Edge/日常 NPP。

用法：
  python record_segments.py seg1
  python record_segments.py seg3 seg5b
  python record_segments.py all
跑前：dev server 3002 在跑（F:\_hftest\hf04-seek，npm run dev）；
隔离 Edge 没开也行（ensure_edge 会按隔离 profile 启动）。
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

import rec_automate as r  # noqa: E402
import npp_ops as n      # noqa: E402
from blackmat import BlackMat  # noqa: E402
import guard             # noqa: E402
import cdp_ctrl          # noqa: E402
import seg5_rehearse     # noqa: E402  # 段⑧直接复用其五步（已带 Edge 专闸）


def _install_input_guards():
    """给 rec_automate 的注入类原语统一套前台白名单闸（实现收在
    guard.install_input_guards；seg5_rehearse 独立分步运行时也装同一套，
    幂等）。

    npp_ops 是 10-12 事故前写的老模块（内部 hotkey/type/paste 不带闸），
    它和 seg5_rehearse import 的都是同一个 rec_automate 模块对象，装闸后
    所有击键/点击/移动在「注入的那一瞬」复查前台：序列中途用户回机把
    自己的窗口切前台，下一个注入立即 UnsafeForeground 中止，封死 14:25
    的盲打事故。只包注入原语；activate、move(hwnd)、截图、定向 SendMessage
    （force_wrap_off/disable_ime）不包。
    """
    guard.install_input_guards(r)


_install_input_guards()

# ---------- 常量 ----------

PROJ = r"F:\_hftest\hf04-seek"
HTML = os.path.join(PROJ, "index.html")
START_SNAP = os.path.join(PROJ, "index.start.html")  # watcher 产物，会致 lint 报错
BACKUP = os.path.join(PROJ, "backup")
STATES = {
    "s0": "s0-static.html",
    "s1": "s1-css.html",
    "s2": "s2-timer.html",
    "s3": "s3-gsap-skel.html",
    "s4": "s4-final.html",
}

REC_DIR = r"F:\_hftest\hf04-rec\takes"
FRAME_DIR = r"F:\_hftest\hf04-rec\frames"
SCREEN_REC = r"F:\Data\gmeek-site\tools\screen-rec.js"

# 段⑤a 入镜脚本：git 源在 oneoffs，布景时复制到沙盒根（敲短命令）
RACE_SRC = os.path.join(HERE, "race_snapshot.py")
RACE_DST = os.path.join(PROJ, "race-snapshot.py")

# 录区是屏幕物理 (0,0,1600,920)（gdigrab，屏幕 1920×1080@150%）。Win11 DWM：
# 窗口右边 12px 是圆角/阴影透明带（实测实体到 rect-12），左边 11px 不透明边框。
# 故窗口外框摆 (-12, 0, 1624, 928)：实体右缘到 1600、左客户区仅切 1px，
# 底部实体到 ~936，录区四周零穿帮（hf-03 右缘 27px 穿帮的根治）。
WND_X, WND_Y, WND_W, WND_H = -12, 0, 1624, 928
TERM_X, TERM_Y = -12, 0
TERM_W, TERM_H = 1632, 1000  # 高向下超出录区无妨（穿帮只在窗口盖不住录区的方向）
REC_TERM_TITLE = "hf04-rec"

# Studio Preview Play 三角中心：2026-10-13 实拍标定（新摆位 gdigrab 录区内，
# bbox 770..782×422..436，质心 775.4,428.8）
PLAY_X, PLAY_Y = 775, 428

NPX = "npx --yes hyperframes@0.8.107"

# ---- 段② @keyframes（s0→s1）----
KEYFRAMES_CSS = """      @keyframes flyin {
        from {
          opacity: 0;
          transform: translateY(60px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }"""
ANIM_LINE = "        animation: flyin 0.8s ease-out;"

# ---- 段⑥ 三条 fromTo（s3 注释行→正解；单行写法给 NPP 替换工艺兜底）----
SKEL_COMMENT = ('      // tl.fromTo("#title", { opacity: 0, y: 24 }, '
                '{ opacity: 1, y: 0, duration: 0.6 }, 0);')
# 入场时长按 seg5 seek 演示点反推：title 1.4s → seek(2.4) 落 power2.out
# 约 49% 进度（半透明浮半路）、seek(3) 约 92%（标题就位）；subtitle 1.2s
# → seek(6.3) 落约 44%（副标题半路）、seek(9) 全就位。尾锚 2/3/6 不变。
TT_TITLE = ('      tl.fromTo("#title", { opacity: 0, y: 60 }, '
            '{ opacity: 1, y: 0, duration: 1.4, ease: "power2.out" }, 2);')
TT_CARD = ('      tl.fromTo("#card", { opacity: 0, scale: 0.8 }, '
           '{ opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.7)" }, 3);')
TT_SUB = ('      tl.fromTo("#subtitle", { opacity: 0, y: 30 }, '
          '{ opacity: 1, y: 0, duration: 1.2, ease: "power2.out" }, 6);')

os.makedirs(REC_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

_mat = None
_term_hwnd = None


# ---------- 隔离 NPP 关窗（只认 _hftest\hf04-seek 标题） ----------

def _enum_hf04_npp():
    """所有可见、标题含 _hftest\\hf04 的 Notepad++ 顶层窗 [(hwnd, title)]。"""
    found = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        c = r.ctypes.create_unicode_buffer(64)
        r.u.GetClassNameW(wnd, c, 64)
        if c.value == "Notepad++" and r.u.IsWindowVisible(wnd):
            ln = r.u.GetWindowTextLengthW(wnd)
            b = r.ctypes.create_unicode_buffer(ln + 1)
            r.u.GetWindowTextW(wnd, b, ln + 1)
            if r"_hftest\hf04" in b.value:
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
        found = _enum_hf04_npp()
        if not found:
            return
        for wnd, _ in found:
            r.u.PostMessageW(wnd, 0x0010, 0, 0)
        t0 = time.time()
        while time.time() - t0 < 3:
            time.sleep(.3)
            if not _enum_hf04_npp():
                return
        for wnd, _ in _enum_hf04_npp():
            _dismiss_modal(wnd)
        time.sleep(.5)
    for wnd, title in _enum_hf04_npp():
        pid = _wnd_pid(wnd)
        exe = _pid_exe(pid)
        if exe.lower().startswith(r"f:\_hftest\npp-local\\"):
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            time.sleep(.5)
        else:
            raise RuntimeError(
                "隔离 NPP 窗关不掉且 exe 不属于 npp-local，拒绝强杀："
                "pid=%s exe=%s title=%s" % (pid, exe, title))
    if _enum_hf04_npp():
        raise RuntimeError("三轮关闭＋兜底后仍有 _hftest\\hf04 NPP 窗")


# ---------- 布景状态机 ----------

def _remove_start_snap():
    """watcher 会把旧 composition 另存 index.start.html，导致
    multiple_root_compositions；确认存在再删（它不是任何备份）。"""
    t0 = time.time()
    while time.time() - t0 < 3:
        if os.path.exists(START_SNAP):
            os.remove(START_SNAP)
            time.sleep(.3)
            return
        time.sleep(.25)


def reset(state, open_npp=False):
    """冷推权威态：关 NPP→备份无条件覆盖→（删 start 快照）→可选开 NPP。"""
    assert state in STATES, state
    close_any_npp()
    n.close()
    time.sleep(.6)
    src = os.path.join(BACKUP, STATES[state])
    if not os.path.exists(src):
        raise RuntimeError("权威备份缺失: " + src)
    shutil.copyfile(src, HTML)
    time.sleep(.6)  # 等 watcher 落 index.start.html
    _remove_start_snap()
    if open_npp:
        n.launch(HTML)
        n.set_zoom(0)
        r.move(n.hwnd, WND_X, WND_Y, WND_W, WND_H)
        time.sleep(.3)
        s = n.active_scintilla()
        n._senda(s, n.SCI_SETSEL, 0, 0)


def build_s1():
    reset("s1")  # 权威态直接覆盖（s1 已是 s0+keyframes 的结果）


def build_s4():
    """文件已是 s4 内容则不动；否则从 s3 走替换工艺（与 seg6 入镜动作一致）。"""
    t = open(HTML, encoding="utf-8").read()
    if '"power2.out" }, 2);' in t and '"back.out(1.7)" }, 3);' in t:
        _remove_start_snap()
        return
    reset("s3", open_npp=True)
    _gsap_edits()
    n.close()
    time.sleep(.6)
    _remove_start_snap()


def _css_edits():
    """s0→s1 的 NPP 编辑（布景快进用；seg2a 入镜版另写节奏）。"""
    n.insert_after_line(n.line_of("#card {") - 1, KEYFRAMES_CSS)
    n.save(lambda t: "@keyframes flyin" in t)
    n.insert_after_anchor("letter-spacing: -0.03em;", ANIM_LINE)
    n.save(lambda t: "animation: flyin 0.8s ease-out;" in t)


def _gsap_edits():
    """s3→s4 的 NPP 编辑：注释行换 title 单条，再依次插 card/sub。

    line_of/read_file 只认磁盘，而 replace_all/insert 只改缓冲区，每步
    之间必须 save 同步，否则下一个锚点在磁盘上不存在（seg6 入镜版同构）。
    """
    n.replace_all(SKEL_COMMENT, TT_TITLE)
    n.save(lambda t: '"power2.out" }, 2);' in t and "// tl.fromTo" not in t)
    n.insert_after_anchor('"power2.out" }, 2);', TT_CARD)
    n.save(lambda t: '"back.out(1.7)" }, 3);' in t)
    n.insert_after_anchor('"back.out(1.7)" }, 3);', TT_SUB)
    n.save(lambda t: ("back.out(1.7)" in t and '"power2.out" }, 6);' in t
                      and "tl.fromTo" in t))


# ---------- Edge / Studio ----------

def ensure_edge():
    """9222 在线就复用；否则隔离 profile 启动。保证 Studio＋裸 player 两 tab。"""
    cdp_ctrl.start_edge()
    studio, player = cdp_ctrl.ensure_tabs()
    return studio, player


def edge_foreground_hwnd(tab_id):
    """激活 tab→按 pid 强前置窗（顺带关扩展广告小窗）→摆位过闸，返回主窗 hwnd。"""
    cdp_ctrl.browser_activate(tab_id)
    time.sleep(.5)
    hwnd = guard.force_isolated_edge_foreground()
    r.u.ShowWindow(hwnd, r.SW_RESTORE)
    r.move(hwnd, WND_X, WND_Y, WND_W, WND_H)
    time.sleep(.3)
    r.activate(hwnd)
    time.sleep(.3)
    guard.assert_fg_isolated()
    guard.assert_point_isolated(PLAY_X, PLAY_Y)
    return hwnd


def safe_click(x, y):
    guard.assert_fg_isolated()
    guard.assert_point_isolated(x, y)
    r.mouse_click(x, y)


def park_mouse():
    r.mouse_move(12, 884)


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


def extract_frames(name, every=4):
    src = os.path.join(REC_DIR, name + ".mp4")
    pat = os.path.join(FRAME_DIR, name + "-%02d.png")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", src, "-vf", "fps=1/%d,scale=800:-1" % every, pat],
                   check=True)
    print("frames:", name)


# ---------- 段① s0 播放：砰地出现 ----------

def take_seg1():
    reset("s0")
    studio, _ = ensure_edge()
    cdp_ctrl.reload_tab(studio)
    time.sleep(6.0)
    hwnd = edge_foreground_hwnd(studio)
    park_mouse()

    def act():
        _mat.behind(hwnd)
        guard.assert_fg_isolated()
        time.sleep(1.4)            # t=0 空场
        r.mouse_move(PLAY_X, PLAY_Y)
        time.sleep(.5)
        safe_click(PLAY_X, PLAY_Y)
        time.sleep(.15)
        park_mouse()
        time.sleep(9.8)            # 2 进、3 卡片、6 副标题，拍满 10s

    return record("rec-play-static", 13, act)


# ---------- 段②a NPP 写 @keyframes ----------

def take_seg2a():
    reset("s0", open_npp=True)
    n.reveal_in_line(n.line_of("#title {"), "#title {",
                     scroll_anchor=(n.line_of("letter-spacing"), "letter-spacing"))
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.4)            # 开场：#title 现状
        n.insert_after_line(n.line_of("#card {") - 1, KEYFRAMES_CSS)
        n.save(lambda t: "@keyframes flyin" in t)
        time.sleep(.3)
        # keyframes 是 10 行块：scroll_anchor 先送 caret 到块底 translateY(0)
        # 逼视图下压，再回开口行建选区（reveal_in_line 只建单行选区，尾锚禁跨行）
        n.reveal_in_line(n.line_of("@keyframes flyin"), "@keyframes",
                         scroll_anchor=(n.line_of("translateY(0);"), "translateY(0);"))
        time.sleep(4.2)            # 拍 keyframes 全块（0.8s/60px）
        n.insert_after_anchor("letter-spacing: -0.03em;", ANIM_LINE)
        n.save(lambda t: "animation: flyin 0.8s ease-out;" in t)
        time.sleep(.3)
        n.reveal_in_line(n.line_of("animation: flyin"), "animation: flyin", "ease-out;")
        time.sleep(3.6)            # 拍 animation 行
        park_mouse()

    return record("rec-css-keyframes", 26, act)


# ---------- 段②b 播放 s1：飞入 ----------

def take_seg2b():
    build_s1()
    studio, _ = ensure_edge()
    cdp_ctrl.reload_tab(studio)
    time.sleep(6.0)
    hwnd = edge_foreground_hwnd(studio)
    park_mouse()

    def act():
        _mat.behind(hwnd)
        guard.assert_fg_isolated()
        time.sleep(1.4)
        r.mouse_move(PLAY_X, PLAY_Y)
        time.sleep(.5)
        safe_click(PLAY_X, PLAY_Y)
        time.sleep(.15)
        park_mouse()
        time.sleep(9.8)

    return record("rec-play-css", 13, act)


# ---------- 段③ 终端 snapshot 三帧＋逐字节复验 ----------

_term_hwnd = None


def open_rec_term():
    """独立 WT 窗（cmd，cwd/三变量就位），1632×1000 外框盖住录区。绝不动用户 WT。"""
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
    # --suppressApplicationTitle 必须有：npm/npx 运行时会 SetConsoleTitle，
    # WT 默认跟随应用把 tab 标题改成 npm 命令，guard 白名单 startswith
    # ("hf04-rec") 立刻失配，下一条注入/ park_mouse 撞自己的闸。抑制后
    # tab 标题恒为 hf04-rec。开录前若有旧参数启动的残留窗，先手动关掉。
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
        raise RuntimeError("等不到 hf04-rec 终端窗口")
    time.sleep(1.2)
    r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
    r.move(_term_hwnd, TERM_X, TERM_Y, TERM_W, TERM_H)
    time.sleep(.5)
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.5)
    return _term_hwnd


def term_cmd(line, post=0.0):
    """在 hf04-rec 敲一条命令并回车。前台必须仍是隔离终端。"""
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


def take_seg3(snap_wait=20.0):
    # snap_wait 真机标定 2026-10-13（A③）：单轮 headless 三帧在本机闲机
    # 约 14–17s，取 20 保住「命令回显停稳再拍下一条」；两轮逐字节复验不变
    # 两轮三帧 snapshot（每轮一个 headless 会话）＋for/fc 逐字节复验
    build_s1()
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd("%s snapshot --at 2.1,2.5,2.9 --no-end -o rec-shots/s1-a" % NPX)
        time.sleep(snap_wait)
        term_cmd("%s snapshot --at 2.1,2.5,2.9 --no-end -o rec-shots/s1-b" % NPX)
        time.sleep(snap_wait)
        # 敲进交互式 cmd（非批处理文件），for 变量必须单 %f；
        # 本串不做 Python % 格式化，% 在普通字符串里就是普通字符
        # （最初版本错在尾部挂了 % (...) 元组，%f 才被当浮点转换符崩掉）。
        term_cmd('for %f in (2.1 2.5 2.9) do @fc /b '
                 '"rec-shots\\s1-a\\frame-00-at-%fs.png" '
                 '"rec-shots\\s1-b\\frame-00-at-%fs.png"')
        time.sleep(4.0)            # 三行「FC: 找不到差异」
        park_mouse()

    # 两条 snapshot 命令各约 80 字符（打字 ~3.3s）＋fc 行 ~95 字符（~3.8s）
    return record("rec-snap-css", 6 + 2 * snap_wait + 12, act)


# ---------- 段④a NPP 展示 s2 计数器 ----------

def take_seg4a():
    reset("s2", open_npp=True)
    # setInterval 块跨 54-59 六行：reveal_in_line 只建单行选区，块底用
    # scroll_anchor 先送 caret 逼视图下压，开口行选区与整块同框
    n.reveal_in_line(n.line_of("setInterval"), "setInterval",
                     scroll_anchor=(n.line_of("}, 500);"), "}, 500);"))
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(2.4)
        n.reveal_in_line(n.line_of('id="subtitle"'), 'id="subtitle"', "</h2>")
        time.sleep(3.4)            # tick 0 元素
        # 回代码块顶（let tick 行）；块底 500 行由 scroll_anchor 保入镜
        n.reveal_in_line(n.line_of("let tick = 0;"), "let tick = 0;",
                         scroll_anchor=(n.line_of("}, 500);"), "}, 500);"))
        time.sleep(5.0)            # setInterval 全貌
        park_mouse()

    return record("rec-timer-code", 18, act)


# ---------- 段④b 播放 s2：数字跳得欢 ----------

def take_seg4b():
    reset("s2")
    studio, _ = ensure_edge()
    cdp_ctrl.reload_tab(studio)
    time.sleep(6.0)
    hwnd = edge_foreground_hwnd(studio)
    park_mouse()

    def act():
        _mat.behind(hwnd)
        guard.assert_fg_isolated()
        time.sleep(1.4)
        r.mouse_move(PLAY_X, PLAY_Y)
        time.sleep(.5)
        safe_click(PLAY_X, PLAY_Y)
        time.sleep(.15)
        park_mouse()
        time.sleep(9.8)

    return record("rec-play-timer", 13, act)


# ---------- 段⑤a 串行三同 vs 六帧并发分叉 ----------

def take_seg5a(race_wait=150.0):
    # 串行三连拍已被实测证伪（同 t 逐字节相同）；入镜脚本 race-snapshot.py
    # 一镜演两轮：先排队连问 3 次（ser-1..3，实测全 tick 3、1 种内容），
    # 再 6 路 headless 同时问同一秒（tk-1..6，重演 render workers 并行抢
    # CPU；彩排轮出 tick 4/6/7 三种），收口打印「排队 1 种；一窝蜂 N 种」。
    # 5s 心跳行防长等待死画面。等待段剪辑加速。
    reset("s2")
    shutil.copyfile(RACE_SRC, RACE_DST)
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd("python race-snapshot.py")
        time.sleep(race_wait)
        park_mouse()

    # 两轮墙钟实测（机器闲）：串行 46s＋并发 47s ≈ 94s，留余量取 150；
    # 忙工况（用户在机）单路能到 90s，若深夜仍偏忙导致结论行被截，重拍
    return record("rec-snap-timer", 6 + race_wait + 10, act)


# ---------- 段⑤b check 全绿 ----------

def take_seg5b(check_wait=26):
    # check_wait 真机标定 2026-10-13（A④）：npm run check 全绿在本机闲机
    # 约 22–24s，取 26 保住 Check passed 尾帧；原估 42 回收 16s
    reset("s2")  # 幂等：保证 index 是 s2、无 start 快照
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.0)
        term_cmd("npm run check")
        time.sleep(check_wait)     # Check passed 尾帧
        park_mouse()

    return record("rec-check-pass", 3.0 + check_wait + 2, act)


# ---------- 段⑥ NPP 三件套 ----------

def take_seg6():
    reset("s3", open_npp=True)
    # 开场一次拍下骨架四行（timeline／注释样例／注册／seek 0）：锚点送
    # tl.seek(0) 贴客户区底缘（s3 仅 45 行，无锚点时 L38 会被最小滚动压到
    # 屏底、注释行出屏，第二拍 reveal 还要再滚一行）。2026-10-14 真机探针
    # 截图 npp-seg6-39 验证四行同框、选区 y≈800 余量充足。
    n.reveal_in_line(n.line_of("gsap.timeline"), "gsap.timeline", "paused: true",
                     scroll_anchor=(n.line_of("tl.seek(0);"), "tl.seek(0);"))
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        guard.assert_fg_safe()
        time.sleep(3.0)            # 第一件：paused: true
        # 第二件：注释行 → title fromTo，再挂 card/sub。
        # ★编辑序列与 check_anchors.py 的 seg6 磁盘态模拟严格镜像
        # （replace/insert 只改缓冲区、line_of 只认磁盘，每步必 save），
        # 改此序列必须同步改校验器，否则 python check_anchors.py 拦下
        n.reveal_in_line(n.line_of("// tl.fromTo"), "// tl.fromTo", "0);")
        time.sleep(2.4)            # 骨架留好的位置
        n.replace_all(SKEL_COMMENT, TT_TITLE)
        # line_of 只认磁盘：replace 只改了缓冲区，不 save 下一个锚点必崩
        n.save(lambda t: '"power2.out" }, 2);' in t and "// tl.fromTo" not in t)
        time.sleep(.5)
        n.reveal_in_line(n.line_of("tl.fromTo(\"#title\""), "tl.fromTo", '"power2.out" }, 2);')
        time.sleep(3.0)            # title 挂第 2 秒
        n.insert_after_anchor('"power2.out" }, 2);', TT_CARD)
        n.save(lambda t: '"back.out(1.7)" }, 3);' in t)   # 同步磁盘，下个锚才找得到
        time.sleep(.4)
        n.insert_after_anchor('"back.out(1.7)" }, 3);', TT_SUB)
        n.save(lambda t: "back.out(1.7)" in t and '"power2.out" }, 6);' in t)
        time.sleep(.4)
        n.reveal_in_line(n.line_of("tl.fromTo(\"#card\""), "tl.fromTo(\"#card\"",
                         '"back.out(1.7)" }, 3);')
        time.sleep(2.6)            # card 挂第 3 秒
        n.reveal_in_line(n.line_of("tl.fromTo(\"#subtitle\""), "tl.fromTo(\"#subtitle\"",
                         '"power2.out" }, 6);')
        time.sleep(3.0)            # subtitle 挂第 6 秒
        # 第三件：注册行＋紧接其下的 tl.seek(0)；选区只在注册行（= tl;），
        # scroll_anchor 送下一行保两行同框（尾锚必须在同一物理行内）
        n.reveal_in_line(n.line_of('window.__timelines["main"]'),
                         'window.__timelines["main"]', "= tl;",
                         scroll_anchor=(n.line_of("tl.seek(0);"), "tl.seek(0);"))
        time.sleep(4.2)
        park_mouse()

    return record("rec-gsap-three", 46, act)


# ---------- 段⑦ 播放 s4 正解 ----------

def take_seg7():
    build_s4()
    close_any_npp()  # seg6 结束时 NPP 可能仍开着（build_s4 幂等不 reset）
    n.close()
    studio, _ = ensure_edge()
    cdp_ctrl.reload_tab(studio)
    time.sleep(6.0)
    hwnd = edge_foreground_hwnd(studio)
    park_mouse()

    def act():
        _mat.behind(hwnd)
        guard.assert_fg_isolated()
        time.sleep(1.4)
        r.mouse_move(PLAY_X, PLAY_Y)
        time.sleep(.5)
        safe_click(PLAY_X, PLAY_Y)
        time.sleep(.15)
        park_mouse()
        time.sleep(9.8)

    return record("rec-play-final", 13, act)


# ---------- 段⑧ 裸 player＋DevTools 亲手 seek ----------

def take_seg8():
    build_s4()
    _, player = ensure_edge()
    # 布景：裸 tab reload→就绪→seek(0)，激活前置；DevTools 须为关态
    cdp_ctrl.reload_tab(player, cdp_ctrl.PLAYER_READY, ready_timeout=18)
    time.sleep(.6)
    cdp_ctrl.player_seek(player, 0)
    time.sleep(.4)
    hwnd = edge_foreground_hwnd(player)
    # DevTools 若上次残留开着，Ctrl+Shift+J 会把它关掉而非打开：按 target 检测
    if cdp_ctrl.devtools_open():
        guard.assert_point_safe(760, 200)
        r.hotkey("ctrl", "shift", "j")
        time.sleep(1.2)
        if cdp_ctrl.devtools_open():
            raise RuntimeError("DevTools 无法关到初始态，seg8 放弃，避免录反")
    park_mouse()

    def act():
        _mat.behind(hwnd)
        time.sleep(1.2)
        # 复用 seg5_rehearse 五步（每步自带 Edge 专闸＋证据截图）
        seg5_rehearse.step_open()
        seg5_rehearse.step_split()
        seg5_rehearse.step_zoom()
        seg5_rehearse.step_seek()
        seg5_rehearse.step_close()
        park_mouse()

    # 真机实测（2026-10-13，分步计时）：open 4.8＋split 4.5（edge 已在 555
    # 一轮收敛；若需拖拽每轮 +2–3s）＋zoom 3.6＋seek 43.3（10 条×约 4.2：
    # 打字 25 字符×0.07≈1.8＋等 1.2＋证据截图 1.05）＋close 3.5 ≈ 59.8；
    # 加 act 开头静场 1.2 与拖拽余量，record 取 70（原精算 58 漏算 /json
    # localhost IPv6 每次 2s 与截图 1s/张，已随 127.0.0.1＋长连回收）。
    # 尾帧是 DevTools 关闭画面，片尾静场剪辑直接掐尾，拍不全 close 才是事故
    return record("rec-console-seek", 70, act)


# ---------- 段⑨（可选）终端 render：一帧帧 seek 截图烤成 MP4 ----------

def take_seg9(render_wait=80):
    """粗稿行 53-55「捅破窗户纸」配的终端镜头。2026-10-14 真机定量：
    墙钟 47.5s（HF 自报 35.4s），worker headless 不弹可见窗，render_wait=80
    预留并发余量；尾帧停输出路径，长了剪辑掐尾，剪不剪用户定。"""
    build_s4()
    close_any_npp()
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.0)
        term_cmd("npm run render -- -o rec-render/hf04-seek.mp4")
        time.sleep(render_wait)   # 帧进度滚完＋FFmpeg，尾帧停输出路径
        park_mouse()

    return record("rec-render", 3.0 + render_wait, act)


TAKES = {
    "seg1": take_seg1,
    "seg2a": take_seg2a,
    "seg2b": take_seg2b,
    "seg3": take_seg3,
    "seg4a": take_seg4a,
    "seg4b": take_seg4b,
    "seg5a": take_seg5a,
    "seg5b": take_seg5b,
    "seg6": take_seg6,
    "seg7": take_seg7,
    "seg8": take_seg8,
    "seg9": take_seg9,  # 2026-10-14 实测墙钟 47.5s、worker headless 不弹窗，纳入录序
}

# seg9 第三批压轴：2026-10-14 真机定量（墙钟 47.5s，render_wait 80 够），
# capture 期枚举可见窗口确认无 Chrome 弹窗盖终端；剪不剪由用户定，素材先录备着
ALL_TAKES = ["seg1", "seg2a", "seg2b", "seg3", "seg4a", "seg4b",
             "seg5a", "seg5b", "seg6", "seg7", "seg8", "seg9"]


def main():
    global _mat
    args = sys.argv[1:] or ["all"]
    if args == ["all"]:
        args = ALL_TAKES
    _mat = BlackMat()
    try:
        for name in args:
            print("\n===== take %s =====" % name, flush=True)
            TAKES[name]()
    finally:
        _mat.close()


if __name__ == "__main__":
    main()
