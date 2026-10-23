# -*- coding: utf-8 -*-
r"""hf-03 正式录屏编排：五个教程段落 × 7 个 take，1600×920@30 gdigrab。

素材先行流程的第③步产物。操作链与 smoke_npp 同款（已 10 断言验证），
这里额外负责：窗口摆位、段前「布景」（不录制地把文件推进到该 take
起点状态）、镜头取景（reveal_in_line 七镜清单）、操作节奏、录制与抽帧。

takes：
  seg1 rec-attrs-cdn     NPP 指认四属性（两拍）＋CDN 换本地
  seg2 rec-title-time    NPP 标题改「我的第一个片段」＋data-start=2/duration=4
  seg3 rec-play          Edge 点 Play，2 秒进、6 秒走
  seg4 rec-stack         NPP root relative＋#card/#subtitle 样式＋层叠调序
  seg5a rec-check-fail   终端 npm run check 报 content_overlap
  seg5b rec-allow        NPP 加 data-layout-allow-overlap
  seg5c rec-check-pass   终端再跑 check 通过

文件状态机（正式文件 F:\_hftest\hf03-clip\index.html）：
  S0 干净 init 样板 → S1 CDN 本地 → S2 标题/时间 → S3 段④全部
  → S4 放行属性。每个 take 布景都从 S0 冷推，状态确定、可单独重录。

用法：
  python record_segments.py seg1     # 录单个 take
  python record_segments.py seg1 seg2 seg3
  python record_segments.py all
注意：跑前确保 npp-local 隔离实例未开着正式文件（脚本会自行关开），
Edge Studio(0x111d0)/dev server(3002) 在位；不碰用户任何窗口。
"""
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rec_automate as r
import npp_ops as n
from blackmat import BlackMat

# ---------- 常量 ----------

CLIP_DIR = r"F:\_hftest\hf03-clip"
HTML = os.path.join(CLIP_DIR, "index.html")
CLEAN_BAK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "backup", "hf03-index.clean.bak")
REC_DIR = r"F:\_hftest\hf03-rec\takes"
FRAME_DIR = r"F:\_hftest\hf03-rec\frames"
# 仓库根＝HERE（videos/projects/<片>/oneoffs）上溯四级，随仓库位置自适应
REPO_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SCREEN_REC = os.path.join(REPO_ROOT, "tools", "screen-rec.js")

EDGE_HWND = 0x111d0
PLAY_X, PLAY_Y = 775, 487

# NPP/Edge 用 920 高（probe 七镜按此定型）。底缝防穿帮：920 高窗底缘
# y≈915–920 有 Win11 圆角透明缝，后方用户最大化 WT（绝不能动）的红字会
# 透入录制区——由 BlackMat 在入镜窗紧后垫无边框纯黑窗遮住（见 blackmat.py），
# 不靠加高窗口；park_stray_terms() 把 hf03-check 移屏外是双保险。
# hf03-rec 终端用 1000 高：cmd 输出顶对齐行位不变，920 线稳落黑底区
# （content_overlap/Check failed 完整在线内）；WT 右缘约 17px 透明边框，
# 宽给 1620 让不透明黑底盖过 1600。
WND_X, WND_Y, WND_W, WND_H = 0, 0, 1600, 920
TERM_W, TERM_H = 1620, 1000
STRAY_TERM_TITLE = "hf03-check"
STRAY_PARK_X = 2000

CDN_URL = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
OLD_TITLE = ('class="clip" data-start="0" data-duration="10" '
             'data-track-index="0">Title</h1>')
NEW_TITLE = ('class="clip" data-start="2" data-duration="4" '
             'data-track-index="0">我的第一个片段</h1>')
ALLOW_FIND = 'id="card" class="clip" data-start="3" data-duration="2"'
ALLOW_ATTR = ' data-layout-allow-overlap=""'

CARD_CSS = """      #card {
        position: absolute;
        width: 780px;
        padding: 52px 60px;
        background: #18181b;
        border: 1px solid #3f3f46;
        border-radius: 24px;
        color: #fbbf24;
        font-size: 44px;
        font-weight: 500;
        text-align: center;
      }
      #subtitle {
        color: #a1a1aa;
        font-size: 40px;
        font-weight: 400;
        margin-top: 28px;
      }"""
CARD_EL = ('      <div data-hf-id="hf-hj9x" id="card" class="clip" '
           'data-start="3" data-duration="2" data-track-index="0">'
           'HTML 里后写的，盖在上面</div>')
SUB_EL = ('      <h2 data-hf-id="hf-n4nz" id="subtitle" class="clip" '
          'data-start="6" data-duration="4" data-track-index="0">'
          '零行 JavaScript，先出片子</h2>')

os.makedirs(REC_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

# main() 启动、全程存活的黑垫窗；每个 act 开头 behind(入镜窗)。
_mat = None


# ---------- 布景（不录入镜） ----------

def _enum_hf03_npp():
    """所有可见、标题含 _hftest\\hf03 的 Notepad++ 顶层窗 [(hwnd, title)]。
    用户日常 NPP（D:\\Program Files，标题不含该串）永不命中。"""
    found = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        c = r.ctypes.create_unicode_buffer(64)
        r.u.GetClassNameW(wnd, c, 64)
        if c.value == "Notepad++" and r.u.IsWindowVisible(wnd):
            ln = r.u.GetWindowTextLengthW(wnd)
            b = r.ctypes.create_unicode_buffer(ln + 1)
            r.u.GetWindowTextW(wnd, b, ln + 1)
            if r"_hftest\hf03" in b.value:
                found.append((wnd, b.value))
        return True

    r.u.EnumWindows(cb, 0)
    return found


def _wnd_pid(wnd):
    pid = r.wintypes.DWORD()
    r.ctypes.windll.user32.GetWindowThreadProcessId(
        wnd, r.ctypes.byref(pid))
    return pid.value


def _pid_exe(pid):
    """进程 exe 全路径（QueryFullProcessImageName），失败返回 ''。"""
    k = r.ctypes.windll.kernel32
    h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
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
    """处理挡在 owner（NPP 主窗）前的 #32770 模态框。

    外部修改「重新加载」框：点是(Y) 让缓冲区重载磁盘，之后 WM_CLOSE 无脏
    标记可干净退出（点否会保留脏缓冲区，下一轮又弹保存框，死循环）；
    其余（保存确认等）：Alt+N 不保存。返回是否处理过弹框。"""
    GetWindow = r.ctypes.windll.user32.GetWindow
    GetWindow.restype = r.wintypes.HWND
    GetWindow.argtypes = [r.wintypes.HWND, r.wintypes.UINT]
    dialogs = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        c = r.ctypes.create_unicode_buffer(32)
        r.u.GetClassNameW(wnd, c, 32)
        if (c.value == "#32770" and r.u.IsWindowVisible(wnd)
                and GetWindow(wnd, 4) == owner):  # GW_OWNER
            dialogs.append(wnd)
        return True

    r.u.EnumWindows(cb, 0)
    acted = False
    for dlg in dialogs:
        ln = r.u.GetWindowTextLengthW(dlg)
        b = r.ctypes.create_unicode_buffer(ln + 1)
        r.u.GetWindowTextW(dlg, b, ln + 1)
        r.activate(dlg)
        if "重新加载" in b.value:
            r.hotkey("ALT", "Y")  # 是：重载磁盘内容
        else:
            r.hotkey("ALT", "N")  # 否：不保存
        acted = True
        time.sleep(.6)
    return acted


def close_any_npp():
    """关所有标题含 _hftest\\hf03 的隔离 NPP 窗（跨进程，n.close 只管本进程
    launch 的）。绝不能按进程名批量关——用户日常 NPP 是另一个实例。

    三轮「WM_CLOSE→等 3s→模态框分类处理」；仍存活的按 PID 验明 exe 属于
    F:\\_hftest\\npp-local 后 taskkill 兜底，exe 不符直接报错，绝不强杀。"""
    for _round in range(3):
        found = _enum_hf03_npp()
        if not found:
            return
        for wnd, _ in found:
            r.u.PostMessageW(wnd, 0x0010, 0, 0)  # WM_CLOSE
        t0 = time.time()
        while time.time() - t0 < 3:
            time.sleep(.3)
            if not _enum_hf03_npp():
                return
        for wnd, _ in _enum_hf03_npp():  # 模态框拦着 WM_CLOSE：处理掉再循环
            _dismiss_modal(wnd)
        time.sleep(.5)
    for wnd, title in _enum_hf03_npp():
        pid = _wnd_pid(wnd)
        exe = _pid_exe(pid)
        if exe.lower().startswith(r"f:\_hftest\npp-local\\"):
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            time.sleep(.5)
        else:
            raise RuntimeError(
                f"隔离 NPP 窗关不掉且 exe 不属于 npp-local，拒绝强杀："
                f"pid={pid} exe={exe} title={title}")
    if _enum_hf03_npp():
        raise RuntimeError("三轮关闭＋兜底后仍有 _hftest\\hf03 NPP 窗")


def park_stray_terms():
    """把叠放在录制位的 hf03-check 旧终端移到屏外 (2000,0)。

    实测该终端客户区底行（hyperframes auto-update failed 红字）会从入镜
    窗口底缘几 px 透明缝透入录制区（NPP/Edge 920 高时 y≈915 可见）。
    只移动窗口——绝不输入/关闭（窗内有其他工作 pane）；找不到就算了。"""
    h = r.find_window(STRAY_TERM_TITLE)
    if h:
        r.move(h, STRAY_PARK_X, 0, 1600, 920)
        time.sleep(.3)


def restore_stray_terms():
    """录完把仍停在屏外停车点的 hf03-check 移回原位。"""
    h = r.find_window(STRAY_TERM_TITLE)
    if h:
        rc = r.wintypes.RECT()
        r.u.GetWindowRect(h, r.ctypes.byref(rc))
        if rc.left >= STRAY_PARK_X:
            r.move(h, 0, 0, 1600, 920)


def reset_s0():
    """关全部隔离 NPP→恢复 S0 干净样板→开实例 zoom=0→caret 回首屏。"""
    close_any_npp()
    n.close()
    time.sleep(1.0)
    # 干净备份是唯一权威，任何状态（S1..S4）一律无条件覆盖回 S0；
    # 只校验备份自身完好（含 CDN 行），防止拿错/损坏的备份清了现场。
    bak = open(CLEAN_BAK, "rb").read()
    if b"cdn.jsdelivr" not in bak:
        raise RuntimeError("干净备份自身不含 CDN 行，备份可能损坏: " + CLEAN_BAK)
    shutil.copyfile(CLEAN_BAK, HTML)
    n.launch(HTML)
    n.set_zoom(0)
    r.move(n.hwnd, WND_X, WND_Y, WND_W, WND_H)
    time.sleep(.3)
    s = n.active_scintilla()
    n._senda(s, n.SCI_SETSEL, 0, 0)


def build_s1():
    reset_s0()
    n.replace_all(CDN_URL, "gsap.min.js")
    n.save(lambda t: 'src="gsap.min.js"' in t and "cdn.jsdelivr" not in t)


def build_s2():
    build_s1()
    n.replace_all(OLD_TITLE, NEW_TITLE)
    n.save(lambda t: "我的第一个片段" in t
                    and 'data-start="2" data-duration="4"' in t)


def build_s3():
    build_s2()
    n.insert_after_anchor("#root {", "        position: relative;")
    n.save(lambda t: "position: relative;" in t)
    n.insert_after_line(n.line_of("</style>") - 1, CARD_CSS)
    n.save(lambda t: "#card {" in t and "#subtitle {" in t)
    n.insert_after_anchor("我的第一个片段", CARD_EL)
    n.save(lambda t: 'id="card"' in t)
    n.move_line_up(n.line_of('id="card"'))
    n.save(lambda t: t.index('id="card"') < t.index("我的第一个片段"))
    n.insert_after_anchor("我的第一个片段", SUB_EL)
    n.save(lambda t: 'id="subtitle"' in t)


def build_s4():
    build_s3()
    n.replace_all(ALLOW_FIND, ALLOW_FIND + ALLOW_ATTR)
    n.save(lambda t: "data-layout-allow-overlap" in t)


# ---------- 录制基元 ----------

def park_mouse():
    r.mouse_move(12, 884)  # 行号列空白：不挡代码，920 线内深色底


def end_anchor():
    """reveal_in_line 的垂直取景锚：文件最后内容行（splitlines 口径）。

    属性长行（L39）裸 SETSEL 会被最小滚动压到屏底、上半屏全空；先把 caret
    送文件尾把视图下压，再建选区，目标行稳落屏上 1/3（见 framing-anchor-a）。
    seg4 录制中文件边录边涨行，故每次现算、不写死行号。"""
    return (len(n.read_file().splitlines()), None)


def record(name, duration, action):
    """启动 gdigrab 录屏→跑 action(已过秒数回调)→等收尾→抽帧。"""
    out = os.path.join(REC_DIR, name + ".mp4")
    t0 = time.time()
    proc = subprocess.Popen(
        ["node", SCREEN_REC, out,
         "--width", "1600", "--height", "920", "--x", "0", "--y", "0",
         "-t", str(duration)],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    time.sleep(1.0)  # 等 ffmpeg 起抓
    action()
    rest = duration - (time.time() - t0) - 1.2
    if rest > 0:
        time.sleep(rest)
    proc.wait(timeout=duration + 30)
    log = proc.stdout.read()
    print(log.strip()[-300:])
    extract_frames(name)
    return out


def extract_frames(name, every=4):
    src = os.path.join(REC_DIR, name + ".mp4")
    pat = os.path.join(FRAME_DIR, name + "-%02d.png")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", src, "-vf", f"fps=1/{every},scale=800:-1", pat],
                   check=True)
    print("frames:", name)


def ss():  # 节奏辅助
    pass


# ---------- 段① 四属性＋CDN ----------

def take_seg1():
    reset_s0()  # 布景到 S0（CDN 替换要在镜头里做）
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        time.sleep(2.2)                 # 首屏停留
        tl = n.line_of('class="clip"')
        cdn = n.line_of("cdn.jsdelivr")
        n.reveal_in_line(tl, 'class="clip"', 'data-duration="10"',
                         scroll_anchor=end_anchor())
        time.sleep(2.8)                 # 拍 A：三属性
        n.reveal_in_line(tl, "data-track-index", "</h1>",
                         scroll_anchor=end_anchor())
        time.sleep(2.8)                 # 拍 B：track-index＋Title
        n.reveal_in_line(cdn, "<script", "gsap@3.14.2")
        time.sleep(2.4)                 # CDN 旧地址
        n.replace_all(CDN_URL, "gsap.min.js")
        n.save(lambda t: 'src="gsap.min.js"' in t)
        time.sleep(.4)
        n.reveal_in_line(n.line_of("<script"), "<script", "gsap.min.js")
        time.sleep(3.2)                 # 换好本地文件
        park_mouse()

    return record("rec-attrs-cdn", 28, act)


# ---------- 段② 标题＋时间 ----------

def take_seg2():
    build_s1()  # 布景到 S1，段②开场镜头＝旧属性行
    tl = n.line_of('class="clip"')
    n.reveal_in_line(tl, 'class="clip"', 'data-duration="10"',
                     scroll_anchor=end_anchor())
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        time.sleep(2.0)
        n.reveal_in_line(n.line_of('class="clip"'), "data-track-index", "</h1>",
                         scroll_anchor=end_anchor())
        time.sleep(1.8)                 # 旧 Title 全貌一拍
        n.replace_all(OLD_TITLE, NEW_TITLE)
        n.save(lambda t: "我的第一个片段" in t)
        time.sleep(.4)
        n.reveal_in_line(n.line_of("我的第一个片段"),
                         'data-start="2"', 'data-duration="4"',
                         scroll_anchor=end_anchor())
        time.sleep(3.0)                 # 2 / 4 时间属性
        n.reveal_in_line(n.line_of("我的第一个片段"),
                         "data-track-index", "</h1>",
                         scroll_anchor=end_anchor())
        time.sleep(3.2)                 # 新标题文字
        n.reveal_in_line(n.line_of("我的第一个片段"),
                         'data-start="2"', 'data-duration="4"',
                         scroll_anchor=end_anchor())
        time.sleep(2.4)
        park_mouse()

    return record("rec-title-time", 26, act)


# ---------- 段③ Edge 播放 ----------

def take_seg3():
    build_s2()                     # 文件推进到 S2（dev server 热更）
    n.close()                      # 让开录制区
    time.sleep(.8)
    subprocess.run([sys.executable,
                    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "cdp_reload.py")], check=True)
    time.sleep(6.0)                # SPA 项目渲染
    if not r.u.IsWindow(EDGE_HWND):
        raise RuntimeError(
            f"CDP Edge 窗 {hex(EDGE_HWND)} 已不存在，需重启 --remote-debugging-port=9222 实例")
    r.u.ShowWindow(EDGE_HWND, r.SW_RESTORE)
    r.move(EDGE_HWND, WND_X, WND_Y, WND_W, WND_H)
    r.activate(EDGE_HWND)
    time.sleep(.8)
    r.mouse_move(120, 840)         # 光标左下角候场

    def act():
        _mat.behind(EDGE_HWND)
        time.sleep(1.4)            # t=0 空场（标题未到点）
        r.mouse_move(PLAY_X, PLAY_Y)
        time.sleep(.5)
        r.mouse_click(PLAY_X, PLAY_Y)
        time.sleep(.15)
        r.mouse_move(120, 840)     # 立刻让开
        time.sleep(8.6)            # 2s 进、6s 走，留尾

    return record("rec-play", 12, act)


# ---------- 段④ 层叠 ----------

def take_seg4():
    build_s2()
    n.reveal_in_line(n.line_of("#root {"), "#root {",
                     scroll_anchor=(n.line_of("font-family: Inter"),
                                    "font-family: Inter"))
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        time.sleep(2.6)
        # ④a #root 加定位上下文
        n.insert_after_anchor("#root {", "        position: relative;")
        n.save(lambda t: "position: relative;" in t)
        time.sleep(.3)
        n.reveal_in_line(n.line_of("#root {"), "#root {",
                         scroll_anchor=(n.line_of("font-family: Inter"),
                                        "font-family: Inter"))
        time.sleep(3.0)
        # ④b #card/#subtitle 样式
        n.reveal_in_line(n.line_of("#title {"), "#title {",
                         scroll_anchor=(n.line_of("letter-spacing"),
                                        "letter-spacing"))
        time.sleep(2.2)
        n.insert_after_line(n.line_of("</style>") - 1, CARD_CSS)
        n.save(lambda t: "#card {" in t and "#subtitle {" in t)
        time.sleep(.3)
        n.reveal_in_line(n.line_of("#card {"), "#card {",
                         scroll_anchor=(n.line_of("margin-top: 28px;"),
                                        "margin-top: 28px;"))
        time.sleep(3.8)
        # ④c card 元素先插 title 后（后写者盖上）
        n.reveal_in_line(n.line_of("我的第一个片段"), "<h1", 'class="clip"',
                         scroll_anchor=end_anchor())
        time.sleep(1.8)
        n.insert_after_anchor("我的第一个片段", CARD_EL)
        n.save(lambda t: 'id="card"' in t)
        time.sleep(.3)
        card = n.line_of('id="card"')
        n.reveal_in_line(card, 'id="card"', 'data-duration="2"',
                         scroll_anchor=end_anchor())
        time.sleep(2.6)
        n.reveal_in_line(card, ">HTML", "</div>",
                         scroll_anchor=end_anchor())
        time.sleep(2.8)            # 「HTML 里后写的，盖在上面」
        # ④d Alt+Up 提到 title 前
        n.move_line_up(card)
        n.save(lambda t: t.index('id="card"') < t.index("我的第一个片段"))
        time.sleep(.3)
        n.reveal_in_line(n.line_of('id="card"'), 'id="card"',
                         'data-duration="2"', scroll_anchor=end_anchor())
        time.sleep(3.0)            # card 已在 title 上方相邻
        # ④e subtitle 插 title 后
        n.insert_after_anchor("我的第一个片段", SUB_EL)
        n.save(lambda t: 'id="subtitle"' in t)
        time.sleep(.3)
        n.reveal_in_line(n.line_of('id="subtitle"'), 'id="subtitle"',
                         "</h2>", scroll_anchor=end_anchor())
        time.sleep(3.2)
        park_mouse()

    return record("rec-stack", 50, act)


# ---------- 段⑤ 终端 check ----------

REC_TERM_TITLE = "hf03-rec"
_term_hwnd = None


def open_rec_term():
    """新开独立 WT 窗口（cmd，cwd/三变量就位），摆 1600×920。绝不动用户 WT。"""
    global _term_hwnd
    existing = r.find_window(REC_TERM_TITLE)
    if existing:
        # 复用既有窗也要重新摆位归位（诊断时可能被移到屏外停车点）
        _term_hwnd = existing
        time.sleep(.3)
        r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
        r.move(_term_hwnd, WND_X, WND_Y, TERM_W, TERM_H)
        time.sleep(.4)
        r.activate(_term_hwnd)
        time.sleep(.4)
        return existing
    init = ('set "HYPERFRAMES_FONT_CACHE_DIR=F:\\_hftest\\.cache\\fonts" '
            '&& set "HYPERFRAMES_NO_UPDATE_CHECK=1" '
            '&& set "HYPERFRAMES_SKIP_SKILLS=1" && cls')
    subprocess.Popen(["wt.exe", "-w", "new", "--title", REC_TERM_TITLE,
                      "-d", CLIP_DIR, "cmd.exe", "/k", init])
    t0 = time.time()
    while time.time() - t0 < 20:
        h = r.find_window(REC_TERM_TITLE)
        if h:
            _term_hwnd = h
            break
        time.sleep(.5)
    if not _term_hwnd:
        raise RuntimeError("等不到 hf03-rec 终端窗口")
    time.sleep(1.2)
    r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
    r.move(_term_hwnd, WND_X, WND_Y, TERM_W, TERM_H)
    time.sleep(.5)
    r.activate(_term_hwnd)
    time.sleep(.5)
    return _term_hwnd


def term_run_check():
    r.activate(_term_hwnd)
    time.sleep(.3)
    r.type_text("npm run check", delay=.05)
    time.sleep(.3)
    r.tap("ENTER")


def term_cls():
    r.activate(_term_hwnd)
    time.sleep(.2)
    r.type_text("cls", delay=.04)
    r.tap("ENTER")
    time.sleep(.7)


def take_seg5a(check_wait=42):
    # 无头实测 check 22.4s（exit 1）；TTY＋gdigrab 编码＋Edge dev 驻留时
    # probe 后编译/布局检查明显变慢，24s 实拍曾停在 probe 行没拍到结论，
    # 42s ≈ 无头耗时 1.9 倍留足余量（剪辑只取结论段）。
    build_s3()
    n.close()
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        time.sleep(1.2)
        term_run_check()
        time.sleep(check_wait)     # 输出滚完，尾帧停在 content_overlap
        park_mouse()

    return record("rec-check-fail", 1.5 + 2.0 + check_wait, act)


def take_seg5b():
    # 需要 NPP 开着 S3 态；文件不是 S3（未到/已是 S4）就冷推重建
    t = open(HTML, encoding="utf-8").read()
    if 'id="card"' not in t or "data-layout-allow-overlap" in t:
        build_s3()
    elif r.find_window(r"hf03-clip\index.html") is None:
        n.launch(HTML)  # 5a 收尾关了 NPP，重开（文件仍 S3）
        n.set_zoom(0)
        r.move(n.hwnd, WND_X, WND_Y, WND_W, WND_H)
    n.reveal_in_line(n.line_of('id="card"'), 'id="card"', 'data-duration="2"',
                     scroll_anchor=end_anchor())
    park_mouse()

    def act():
        _mat.behind(n.hwnd)
        time.sleep(2.2)
        n.replace_all(ALLOW_FIND, ALLOW_FIND + ALLOW_ATTR)
        n.save(lambda t: "data-layout-allow-overlap" in t)
        time.sleep(.3)
        n.reveal_in_line(n.line_of("data-layout-allow-overlap"),
                         "data-track-index", ">", scroll_anchor=end_anchor())
        time.sleep(3.4)
        park_mouse()

    return record("rec-allow-overlap", 14, act)


def take_seg5c(check_wait=42):
    # 同 seg5a：无头 20.7s Check passed，实拍留 42s。
    # 连续录制时文件已是 S4；单独跑 build_s4
    if "data-layout-allow-overlap" not in open(HTML, encoding="utf-8").read():
        build_s4()
    n.close()
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        time.sleep(1.0)
        term_run_check()
        time.sleep(check_wait)     # 尾帧 Check passed
        park_mouse()

    return record("rec-check-pass", 1.5 + 2.0 + check_wait, act)


TAKES = {
    "seg1": take_seg1,
    "seg2": take_seg2,
    "seg3": take_seg3,
    "seg4": take_seg4,
    "seg5a": take_seg5a,
    "seg5b": take_seg5b,
    "seg5c": take_seg5c,
}


def main():
    global _mat
    args = sys.argv[1:] or ["all"]
    if args == ["all"]:
        args = ["seg1", "seg2", "seg3", "seg4", "seg5a", "seg5b", "seg5c"]
    _mat = BlackMat()
    try:
        for name in args:
            park_stray_terms()  # 每个 take 前确保旧终端在屏外（黑垫之外的双保险）
            print(f"\n===== take {name} =====")
            TAKES[name]()
    finally:
        _mat.close()
        restore_stray_terms()


if __name__ == "__main__":
    main()
