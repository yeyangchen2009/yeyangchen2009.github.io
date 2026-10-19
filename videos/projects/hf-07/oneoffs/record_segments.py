# -*- coding: utf-8 -*-
r"""hf-07《把每一帧看清楚》正式录屏编排：9 take，1600×920@30 gdigrab。

素材先行（源文件只入 git，成片/母带不入）。布景＝沙盒
F:\_hftest\hf07-frames\proj 三个静态冻结工程（setup_scenes.py 生成，
backup/ 哈希闸），本集无 NPP 现场编辑、无布景状态机：snapshot/
keyframes/compare/grade-compare 全部只读工程，每 take 独立可重录。

两机位（对 STORYBOARD-FRAMEWORK.md 第一节）：
  终端 hf07-rec   cmd 跑 snapshot/keyframes/compare/grade/preview
  隔离 Edge       CDP 9222 裸 player tab 接 3021 后台 preview server（仅 t01）

takes（对框架第三节；★高潮＝t02 接触表四帧蓝同位红异位）：
  t00-prev-bg     终端真起 preview --background --no-open --port 3021
  t01-preview     Edge 裸 player reload→双轨自检→__player.play() 拍 12s
  t02-snap4       snapshot v1 --at 2,2,2,2：四帧＋接触表（灵魂事故）
  t03-forwards    snapshot v3 --at 10：红在起点、蓝在终点
  t04-frames5     snapshot v1 --frames 5：五均分帧＋接触表
  t05-zoom        --zoom "#bad" 裁图＋--zoom "#nope" 硬 error（回滚取原文）
  t06-keyframes   无参报告（#bad 隐身）＋--shot #good 洋葱皮
                  ＋--shot #bad 硬 error（nothing animates，回滚取原文）
  t07-compare     compare v1 v2 --labels 中文标签（paste 注入）
  t08-grade       grade-compare --for 实拍帧 --grades grades.json

每个终端 take 录制外先 prerun 同命令（吞 npx/headless 冷启＋真机定文案/
产物名），再 cls 入镜；take 录完产物立即归位 F:\_hftest\hf07-rec\
artifacts\<take>\（snapshot 下轮自清扫，不立即归位就连坐）。

安全铁律（guard.py）：每个键鼠动作前过闸（前台＋落点双校验），只认
CDP 9222 隔离 Edge 与 hf07-rec 终端两个身份。用户一回机切自己的窗，
下一注入立即 UnsafeForeground 中止。不按进程名批量杀窗，不碰用户
WT/主 Edge。

用法（必须非沙箱；开录前先跑完 run_rehearsal.py 并目验全套真机图）：
  python record_segments.py warmup
  python record_segments.py t02-snap4
  python record_segments.py all
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
HF03_ONEOFFS = os.path.join(HERE, "..", "..", "hf-03", "oneoffs")
sys.path.insert(0, HF03_ONEOFFS)
sys.path.insert(0, HERE)

import rec_automate as r  # noqa: E402
from blackmat import BlackMat  # noqa: E402
import guard  # noqa: E402
import cdp_ctrl  # noqa: E402

guard.install_input_guards(r)

# ---------- 常量 ----------

PROJ = r"F:\_hftest\hf07-frames\proj"
REC_ROOT = r"F:\_hftest\hf07-rec"
REC_DIR = os.path.join(REC_ROOT, "takes")
FRAME_DIR = os.path.join(REC_ROOT, "frames")
ARTIFACT_DIR = os.path.join(REC_ROOT, "artifacts")
SCREEN_REC = r"F:\Data\gmeek-site\tools\screen-rec.js"

# 录区物理 (0,0,1600,920)（gdigrab，1920×1080@150%）。外框几何同 hf-04/05/06：
# Win11 右缘 12px 圆角透明带，窗口摆 (-12,0,1624,928) 实体右缘正好 1600。
WND_X, WND_Y, WND_W, WND_H = -12, 0, 1624, 928
TERM_X, TERM_Y = -12, 0
TERM_W, TERM_H = 1632, 1000
REC_TERM_TITLE = "hf07-rec"

PORT = 3021
NPX = "npx --yes hyperframes@0.8.107"
PREV_BG = NPX + " preview v1 --background --no-open --port %d" % PORT
PREV_STOP = NPX + " preview v1 --stop"
# --at 系一律 --no-end：默认追加的 11.64s 尾帧会让接触表多一格、帧名错位
# （真机 2026-10-19）。--frames 系不加：尾帧本就是均分五帧之一。
SNAP4 = NPX + " snapshot v1 --at 2,2,2,2 --no-end --no-browser-gpu"
SNAP10 = NPX + " snapshot v3 --at 10 --no-end --no-browser-gpu"
FRAMES5 = NPX + " snapshot v1 --frames 5 --no-browser-gpu"
ZOOM_BAD = NPX + ' snapshot v1 --at 4 --zoom "#bad" --no-end --no-browser-gpu'
ZOOM_NOPE = NPX + ' snapshot v1 --at 4 --zoom "#nope" --no-end --no-browser-gpu'
# 真机形态（2026-10-19 第五次彩排 SHOT_WINNER）：--shot #good 收目录 exit 0
# 出洋葱皮；#bad 两种形态都 exit 1，录制固定走文件形态以锁定文案
# 「--shot: nothing animates under '#bad'. Nearest: #good, #clock.」。
KF = NPX + " keyframes v1"
SHOT_GOOD = NPX + " keyframes v1 --shot build/onion-good.png --selector #good"
SHOT_BAD = NPX + " keyframes v1/index.html --shot build/onion-bad.png --selector #bad"
# 中文标签段不能走逐字符键路（cmd 控制台收 Unicode 不稳），拆开 paste：
COMPARE_HEAD = NPX + " compare v1 v2 --at 4 --labels "
COMPARE_LABELS = "方案A·x800,方案B·x500"
COMPARE_TAIL = " --out build/compare.png"

# 等待时长（2026-10-19 第五次彩排热态墙钟×1.3 取整回填）：
# snapshot 开销主要是 headless 拉起＋管线固定 ~14s，帧数几乎不影响墙钟。
PREV_BG_WAIT = 17       # 真机 12.7s：background server 起＋状态行落定
SNAP4_WAIT = 20         # 真机 14.6s：四帧 SwiftShader
SNAP1_WAIT = 19         # 真机 14.4s：单帧（v3）
FRAMES5_WAIT = 20       # 真机 15.4s：五均分帧（首尾自动带）
ZOOM_WAIT = 18          # 真机 13.7s：裁图成功轮
ERROR_WAIT = 17         # 真机 13.2s：选择器不命中硬 error（短路但要过 headless 拉起）
KF_WAIT = 11            # 真机 7.7s：无参文本报告（3 items：#good/#clock/#legal，#bad 隐身）
SHOT_WAIT = 18          # 真机 13.4s：--shot #good 洋葱皮（默认硬 GPU，目录形态）
SHOT_BAD_WAIT = 17      # 真机 13.0s：--shot #bad 硬 error（nothing animates）
COMPARE_WAIT = 25       # 真机 19.2s：两 composition 各 seek 截图拼版
GRADE_WAIT = 20         # 真机 15.2s
FREEZE = 3.0            # 关键尾帧静场

os.makedirs(REC_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

_mat = None
_term_hwnd = None
_player_tid = None


# ---------- 非录态 CLI（prerun 吞冷启／server 生命周期） ----------

def cli_argv(argv):
    return ["npx.cmd", "--yes", "hyperframes@0.8.107"] + argv


def cli_run(argv, timeout=240):
    t0 = time.time()
    p = subprocess.run(cli_argv(argv), cwd=PROJ,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=timeout)
    out = p.stdout.decode("utf-8", errors="replace")
    return p.returncode, out, time.time() - t0


def server_up():
    try:
        with urllib.request.urlopen(
                "http://127.0.0.1:%d/" % PORT, timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_server():
    """非录态保证 3021 在跑（t01 前置；单 take 重录时兜底）。"""
    if server_up():
        return
    code, out, dt = cli_run(["preview", "v1", "--background", "--no-open",
                             "--port", str(PORT)], timeout=90)
    print("[server] start exit=%s %.1fs %s" % (code, dt, out.strip().splitlines()[-1:]))
    t0 = time.time()
    while time.time() - t0 < 20:
        if server_up():
            return
        time.sleep(.5)
    raise RuntimeError("preview server 起不来：\n" + out[-800:])


def stop_server():
    if not server_up():
        return
    cli_run(["preview", "v1", "--stop"], timeout=60)
    time.sleep(1.0)


def prerun(argv, label, timeout=240):
    """录制外同命令试跑：吞冷启＋真机确认 exit/文案/产物，打印墙钟供回填。"""
    code, out, dt = cli_run(argv, timeout=timeout)
    tail = " | ".join(out.strip().splitlines()[-2:])[:220]
    print("[prerun %s] exit=%s %.1fs  %s" % (label, code, dt, tail), flush=True)
    return code, out, dt


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


def wheel(amount, n=1, gap=.18):
    """鼠标滚轮：amount 正＝上滚（回看 scrollback）。调用方负责指针位置。"""
    for _ in range(n):
        r.u.mouse_event(0x0800, 0, 0, amount, 0)
        time.sleep(gap)


def rollback_freeze(up=0, freeze=FREEZE):
    """硬 error 尾帧冻结。up>0 时上滚 up 格取报错原文、再过量下滚回底
    （hf-06 的 30 行瞬刷才需要）。本集真机报文 #nope 仅 7 行、#bad 仅 2 行，
    一屏约 50 行装得下，默认 up=0 纯 freeze——滚动反而会把错误行带离下缘。
    Shift+PgUp 禁用（doskey 吃）。"""
    r.mouse_move(700, 500)
    time.sleep(.25)
    if up:
        wheel(120, up, gap=.22)
        time.sleep(freeze)
        wheel(-120, up + 5, gap=.12)
        time.sleep(.8)
    else:
        time.sleep(freeze)
    park_mouse()


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
    # 标题改成 npm 命令，白名单 startswith("hf07-rec") 立刻失配。
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
        raise RuntimeError("等不到 hf07-rec 终端窗口")
    time.sleep(1.2)
    r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
    r.move(_term_hwnd, TERM_X, TERM_Y, TERM_W, TERM_H)
    time.sleep(.5)
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.5)
    return _term_hwnd


def term_to_front():
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.3)


def term_run(parts, wait=0.0):
    """在 hf07-rec 敲一条命令并回车。parts：ASCII 片段 str 与 ("paste", 中文)
    混排（中文标签走剪贴板，逐字符 Unicode 键路在 cmd 控制台不稳）。"""
    term_to_front()
    time.sleep(.2)
    for p in parts:
        if isinstance(p, tuple) and p[0] == "paste":
            r.paste(p[1])
        else:
            r.type_text(p, delay=.035)
    time.sleep(.2)
    guard.assert_fg_safe()
    r.tap("ENTER")
    if wait:
        time.sleep(wait)


def term_cmd(line, wait=0.0):
    term_run([line], wait=wait)


def term_cls():
    term_cmd("cls")
    time.sleep(.7)


# ---------- Edge（裸 player，仅 t01） ----------

def edge_to_front(tid):
    """激活 player tab→按 pid 强前置主窗（关扩展小窗）→摆位过闸。"""
    cdp_ctrl.browser_activate(tid)
    time.sleep(.5)
    hwnd = guard.force_isolated_edge_foreground()
    r.u.ShowWindow(hwnd, r.SW_RESTORE)
    r.move(hwnd, WND_X, WND_Y, WND_W, WND_H)
    time.sleep(.3)
    r.activate(hwnd)
    time.sleep(.3)
    guard.assert_fg_isolated()
    guard.assert_point_isolated(800, 300)
    return hwnd


VK_CTRL = 0x11
VK_0 = 0x30
VK_OEM_MINUS = 0xBD


def _real_ctrl_combo(vk, hold=.03, gap=.18):
    """真实键盘 Ctrl+组合键（CDP 合成键对浏览器快捷键无效，hf-04 已证）。"""
    r.u.keybd_event(VK_CTRL, 0, 0, 0)
    time.sleep(hold)
    r.u.keybd_event(vk, 0, 0, 0)
    time.sleep(hold)
    r.u.keybd_event(vk, 0, r.KEYEVENTF_KEYUP, 0)
    r.u.keybd_event(VK_CTRL, 0, r.KEYEVENTF_KEYUP, 0)
    time.sleep(gap)


def ensure_page_zoom_half(tid):
    """player 页 zoom 幂等收敛 50%（系统 150% DPI×50% ⇒ dpr 0.75）。"""
    dpr = float(cdp_ctrl.eval_tab(tid, "window.devicePixelRatio"))
    if abs(dpr - 0.75) < .03:
        print("page zoom 已是 50%% (dpr=%.3f)" % dpr, flush=True)
        return
    guard.assert_fg_isolated()
    print("page zoom dpr=%.3f，复位后重缩 ..." % dpr, flush=True)
    _real_ctrl_combo(VK_0, gap=.35)
    for _ in range(5):
        _real_ctrl_combo(VK_OEM_MINUS)
    time.sleep(.4)
    dpr = float(cdp_ctrl.eval_tab(tid, "window.devicePixelRatio"))
    if abs(dpr - 0.75) >= .03:
        raise RuntimeError("页面 zoom 未收敛到 50%%（dpr=%s）" % dpr)
    print("page zoom 收敛 50%% (dpr=%.3f)" % dpr, flush=True)


def _cdp_shot(tid):
    """CDP 截 player tab 全页，返回 PIL.Image（绕过屏幕合成链路）。"""
    import base64
    import io
    import websocket
    t = next(x for x in cdp_ctrl.pages() if x["id"] == tid)
    ws = websocket.create_connection(
        t["webSocketDebuggerUrl"], suppress_origin=True)
    ws.settimeout(10)
    try:
        ws.send(json.dumps({"id": 1, "method": "Page.captureScreenshot",
                            "params": {"format": "png"}}))
        end = time.time() + 10
        while time.time() < end:
            msg = json.loads(ws.recv())
            if msg.get("id") == 1:
                from PIL import Image
                return Image.open(io.BytesIO(
                    base64.b64decode(msg["result"]["data"]))).convert("RGB")
        raise RuntimeError("CDP 截图超时")
    finally:
        ws.close()


def _count_blocks(im, x0r=.0, x1r=1.0, y0r=.0, y1r=1.0):
    """统计蓝/红运动块像素（隔点采样）。蓝 #1f6feb、红 #da3633。"""
    W, H = im.size
    nb = nr = 0
    for y in range(int(H * y0r), int(H * y1r), 2):
        for x in range(int(W * x0r), int(W * x1r), 2):
            rr, gg, bb = im.getpixel((x, y))
            if bb > 120 and rr < 90 and gg < 140:
                nb += 1
            elif rr > 150 and gg < 100 and bb < 100:
                nr += 1
    return nb, nr


def _screen_blocks():
    """屏幕物理截图里页面内容宽松大框的蓝/红像素。
    页面 dpr 0.75：1920×1080 CSS 缩成 1440×810 物理；浏览器栏约 80px。
    框取物理 x∈[100,700] y∈[220,780]（seek(0) 蓝在左、红轨迹也在左半），
    ★彩排目验 t01 前置帧后收紧。"""
    probe = os.path.join(FRAME_DIR, "_player-probe.png")
    r.screenshot(probe, 1920, 1080)
    from PIL import Image
    with Image.open(probe) as im:
        return _count_blocks(im, 100 / 1920, 700 / 1920, 220 / 1080, 780 / 1080)


def heal_edge_compositing(hwnd):
    """最小化→还原强制重建 swapchain（屏幕灰而 CDP 页面活，hf-04 坑①）。"""
    guard.assert_fg_isolated()
    print("heal: 最小化→还原重建上屏链路 ...", flush=True)
    r.u.ShowWindow(hwnd, r.SW_MINIMIZE)
    time.sleep(1.2)
    r.u.ShowWindow(hwnd, r.SW_RESTORE)
    time.sleep(1.0)
    r.move(hwnd, WND_X, WND_Y, WND_W, WND_H)
    r.activate(hwnd)
    time.sleep(1.5)
    guard.assert_fg_isolated()


def wait_player_visible(tid, hwnd, timeout=40.0):
    """seek(0) 后轮询屏幕出画面；屏幕灰而 CDP 活＝swapchain 挂起，自愈≤2 次。"""
    t0 = time.time()
    last_cdp = 0.0
    last_heal = -99.0
    heal_count = 0
    page_ever_alive = False
    while True:
        sb, sr = _screen_blocks()
        if sb + sr >= 80:
            print("player visible %.1fs (blue=%d red=%d, heal=%d)"
                  % (time.time() - t0, sb, sr, heal_count), flush=True)
            return
        now = time.time()
        if now - t0 > 6.0 and now - last_cdp > 2.5:
            last_cdp = now
            try:
                cb, cr = _count_blocks(_cdp_shot(tid), .05, .55, .20, .75)
            except Exception as e:
                print("cdp probe failed: %r" % e, flush=True)
                cb = cr = 0
            if cb + cr >= 150:
                page_ever_alive = True
                if heal_count < 2 and now - last_heal > 8.0:
                    heal_count += 1
                    last_heal = now
                    heal_edge_compositing(hwnd)
        if now - t0 > timeout:
            why = ("页面侧已渲染但屏幕持续灰，heal %d 次未恢复" % heal_count
                   if page_ever_alive else "页面侧也未见红蓝块")
            raise RuntimeError("player 画面 %.0fs 内未上屏（%s），放弃 take"
                               % (timeout, why))
        time.sleep(.8)


def setup_player():
    """t01 录制外全套布景：server→Edge/player tab→reload 就绪→藏扩展→
    seek0→前置→zoom50%→双轨自检。返回 (tid, hwnd)。"""
    global _player_tid
    ensure_server()
    cdp_ctrl.start_edge()
    tid = cdp_ctrl.prep_player_tab()
    _player_tid = tid
    hwnd = edge_to_front(tid)
    ensure_page_zoom_half(tid)
    r.move(hwnd, WND_X, WND_Y, WND_W, WND_H)
    time.sleep(.3)
    wait_player_visible(tid, hwnd)
    guard.assert_fg_isolated()
    park_mouse()
    # 证据帧落 artifacts/_preflight（彩排/开录前目验页面几何）
    probe = os.path.join(ARTIFACT_DIR, "_preflight-player.png")
    os.makedirs(os.path.dirname(probe), exist_ok=True)
    _cdp_shot(tid).save(probe)
    return tid, hwnd


# ---------- 产物归位（snapshot 下轮自清扫，录完立即拷） ----------

def harvest(take, patterns):
    dst = os.path.join(ARTIFACT_DIR, take)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    n = 0
    for pat in patterns:
        for f in sorted(glob.glob(os.path.join(PROJ, pat))):
            if os.path.isfile(f):
                shutil.copy2(f, os.path.join(dst, os.path.basename(f)))
                n += 1
    print("[harvest %s] %d 个产物 → %s" % (take, n, dst), flush=True)
    if n == 0:
        raise RuntimeError("归位为空（命令没产产物？）: " + take)


# ---------- warmup（录制外，吞全部冷启） ----------

def take_warmup():
    """冷启曾实测 60s+，任何固定时长预算都会被打穿（hf-04 教训）。顺序：
    终端 snapshot 一冷一热→preview server 冷启→Edge/player 冷启＋双轨＋
    播放短走一遍→stop server。目验终端输出与 _preflight-player.png 后开拍。"""
    open_rec_term()
    term_cls()
    term_cmd(SNAP4.replace("--at 2,2,2,2", "--at 1,1"), wait=90)   # 冷
    term_cls()
    term_cmd(NPX + " snapshot v1 --at 1 --no-end --no-browser-gpu", wait=30)  # 热
    term_cls()
    term_cmd(PREV_BG, wait=40)                                      # server 冷启
    if not server_up():
        raise RuntimeError("warmup：preview server 冷启后仍不可见")
    setup_player()
    tid = _player_tid
    # 播放冷路径也走一遍（2s 后拉回 0），t01 只剩热态
    cdp_ctrl.player_play(tid)
    time.sleep(2.5)
    cdp_ctrl.player_pause(tid)
    cdp_ctrl.player_seek(tid, 0)
    time.sleep(.8)
    term_to_front()
    stop_server_term()
    term_cls()
    print("warmup 完成：冷启已吞；目验 _preflight-player.png 与各输出形态后开拍")


def stop_server_term():
    """warmup 用：在终端里敲 stop（同时让终端态停在 stop 输出，t00 前会 cls）。"""
    term_cmd(PREV_STOP, wait=8)


# ---------- t00：真起后台 preview server ----------

def take_t00_prev_bg():
    stop_server()                  # 幂等：server 在跑先停（warmup 已停，双保险）
    open_rec_term()
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(PREV_BG, wait=PREV_BG_WAIT)   # 尾帧停后台 URL/PID 状态行
        park_mouse()

    duration = 3 + 4 + PREV_BG_WAIT
    out = record("t00-prev-bg", duration, act)
    if not server_up():
        raise RuntimeError("t00 录完 server 不在 3021——尾帧白录，检查命令")
    return out


# ---------- t01：裸 player 播放，红蓝同滑 12s ----------

def take_t01_preview():
    tid, hwnd = setup_player()     # reload→双轨自检（录制外），server 由 t00 在跑
    park_mouse()

    def act():
        _mat.behind(hwnd)
        guard.assert_fg_isolated()
        time.sleep(1.4)            # t=0 空台：seek(0) 蓝在起点，红按墙钟在位
        cdp_ctrl.player_play(tid)  # 合成键不触发播放（hf-04 证），走 CDP
        time.sleep(12.6)           # 蓝 8s 滑到终点停住、红 4s 循环三圈

    return record("t01-preview", 16, act)


# ---------- t02：★四帧同秒，蓝同位红异位 ----------

def take_t02_snap4():
    open_rec_term()
    prerun(["snapshot", "v1", "--at", "2,2,2,2", "--no-end",
            "--no-browser-gpu"], "t02", timeout=120)
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(SNAP4, wait=SNAP4_WAIT)   # 尾帧停 Saved 4 frames/contact 行
        time.sleep(FREEZE)
        park_mouse()

    out = record("t02-snap4", 4 + 4 + SNAP4_WAIT + FREEZE, act)
    harvest("t02-snap4",
            os.path.join("v1", "snapshots", "frame-*-at-2s.png"),
            os.path.join("v1", "snapshots", "contact-sheet.jpg"))
    return out


# ---------- t03：v3 第十秒，慢表一分钟一圈（take id 沿用 t03-forwards） ----------

def take_t03_forwards():
    open_rec_term()
    prerun(["snapshot", "v3", "--at", "10", "--no-end", "--no-browser-gpu"],
           "t03", timeout=120)
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(SNAP10, wait=SNAP1_WAIT)
        time.sleep(FREEZE)
        park_mouse()

    out = record("t03-forwards", 3 + 4 + SNAP1_WAIT + FREEZE, act)
    harvest("t03-forwards", os.path.join("v3", "snapshots", "frame-*-at-10s.png"))
    return out


# ---------- t04：--frames 5 均分 ----------

def take_t04_frames5():
    open_rec_term()
    prerun(["snapshot", "v1", "--frames", "5", "--no-browser-gpu"], "t04", timeout=120)
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(FRAMES5, wait=FRAMES5_WAIT)
        time.sleep(FREEZE)
        park_mouse()

    out = record("t04-frames5", 3 + 4 + FRAMES5_WAIT + FREEZE, act)
    harvest("t04-frames5",
            os.path.join("v1", "snapshots", "frame-*.png"),
            os.path.join("v1", "snapshots", "contact-sheet.jpg"))
    return out


# ---------- t05：zoom 成功裁图＋不命中硬 error ----------

def take_t05_zoom():
    open_rec_term()
    prerun(["snapshot", "v1", "--at", "4", "--zoom", "#bad", "--no-end",
            "--no-browser-gpu"], "t05a", timeout=120)
    code, out, _ = prerun(["snapshot", "v1", "--at", "4", "--zoom", "#nope",
                           "--no-end", "--no-browser-gpu"], "t05b", timeout=120)
    print("[t05] #nope exit=%s（真机硬 error 文案见上，回滚格数据此定）" % code)
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(ZOOM_BAD, wait=ZOOM_WAIT)     # 局部裁图成
        term_cmd(ZOOM_NOPE, wait=ERROR_WAIT)  # 选择器不命中硬 error（7 行一屏内）
        rollback_freeze()                     # 纯 freeze，无需上滚

    duration = 3 + 4 + ZOOM_WAIT + 4 + ERROR_WAIT + 7
    out = record("t05-zoom", duration, act)
    # #nope 失败轮启动时先清扫 frame-*.png（真机），裁图同归于尽；录后非录态
    # 补跑一次成功轮产图归位（真机工具产出，不伪造，画面帧以录屏为准）
    prerun(["snapshot", "v1", "--at", "4", "--zoom", "#bad", "--no-end",
            "--no-browser-gpu"], "t05-harvest", timeout=120)
    harvest("t05-zoom", os.path.join("v1", "snapshots", "frame-*-at-4s.png"))
    return out


# ---------- t06：keyframes 报告＋#good 洋葱皮＋#bad 硬 error ----------

def take_t06_keyframes():
    open_rec_term()
    prerun(["keyframes", "v1"], "t06a", timeout=90)
    prerun(["keyframes", "v1", "--shot", "build/onion-good.png",
            "--selector", "#good"], "t06b", timeout=120)
    # #bad 真机 exit 1「nothing animates under '#bad'. Nearest: #good, #clock」
    code, out, _ = prerun(["keyframes", "v1/index.html", "--shot",
                           "build/onion-bad.png", "--selector", "#bad"],
                          "t06c", timeout=120)
    print("[t06] #bad exit=%s（真机硬 error；不产图，录屏靠回滚帧展示）" % code)
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(KF, wait=KF_WAIT)            # 报告 3 items（含 CSS #legal），#bad 不在册
        time.sleep(1.0)
        term_cmd(SHOT_GOOD, wait=SHOT_WAIT)   # 洋葱皮成，Saved 行 freeze
        time.sleep(FREEZE)
        term_cmd(SHOT_BAD, wait=SHOT_BAD_WAIT)  # 硬 error（2 行一屏内）
        rollback_freeze()                     # 纯 freeze，无需上滚
        park_mouse()

    duration = (3 + 3 + KF_WAIT + 1 + 5 + SHOT_WAIT + FREEZE
                + 4 + SHOT_BAD_WAIT + 7)
    out = record("t06-keyframes", duration, act)
    # #bad 轮无图（真机 exit 1），只归位 #good 洋葱皮
    harvest("t06-keyframes", os.path.join("build", "onion-good.png"))
    return out


# ---------- t07：compare 两变体一排 ----------

def take_t07_compare():
    open_rec_term()
    prerun(["compare", "v1", "v2", "--at", "4",
            "--labels", COMPARE_LABELS, "--out", "build/compare.png"],
           "t07", timeout=150)
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        # 中文标签走剪贴板；ASCII 命令体逐字敲（命令本身入镜）
        term_run([COMPARE_HEAD, ("paste", COMPARE_LABELS), COMPARE_TAIL],
                 wait=COMPARE_WAIT)
        time.sleep(FREEZE)
        park_mouse()

    duration = 3 + 5 + COMPARE_WAIT + FREEZE
    out = record("t07-compare", duration, act)
    harvest("t07-compare", os.path.join("build", "compare.png"))
    return out


# ---------- t08：grade-compare 调色三格 ----------

def take_t08_grade():
    open_rec_term()
    # grade --for 需要一张实拍帧：录制外备帧（顺带热机）。命令形态以彩排
    # winner 为准（是否要 --project v1），先按无 --project。
    prerun(["snapshot", "v1", "--at", "4", "--no-end", "--no-browser-gpu"],
           "t08-seed", timeout=120)
    frames = sorted(glob.glob(os.path.join(
        PROJ, "v1", "snapshots", "frame-*-at-4s.png")))
    if not frames:
        raise RuntimeError("t08：备帧不存在")
    frame_rel = "v1/snapshots/" + os.path.basename(frames[0])
    grade_argv = ["grade-compare", "--for", frame_rel, "--grades", "grades.json",
                  "--out", "build/grade.png"]
    prerun(grade_argv, "t08", timeout=120)
    grade_cmd = NPX + " " + " ".join(grade_argv)
    term_cls()
    park_mouse()

    def act():
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        time.sleep(1.2)
        term_cmd(grade_cmd, wait=GRADE_WAIT)
        time.sleep(FREEZE)
        park_mouse()

    duration = 3 + 5 + GRADE_WAIT + FREEZE
    out = record("t08-grade", duration, act)
    harvest("t08-grade", os.path.join("build", "grade.png"))
    return out


TAKES = {
    "warmup": take_warmup,
    "t00-prev-bg": take_t00_prev_bg,
    "t01-preview": take_t01_preview,
    "t02-snap4": take_t02_snap4,
    "t03-forwards": take_t03_forwards,
    "t04-frames5": take_t04_frames5,
    "t05-zoom": take_t05_zoom,
    "t06-keyframes": take_t06_keyframes,
    "t07-compare": take_t07_compare,
    "t08-grade": take_t08_grade,
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
