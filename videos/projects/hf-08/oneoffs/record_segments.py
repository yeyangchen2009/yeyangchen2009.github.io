# -*- coding: utf-8 -*-
r"""hf-08《render》正式录屏编排：6 take，1600×920@30 gdigrab。

主角是 render（冷态首跑全链真机约 141s，热态 60s 上下，坏工程还各带
两轮 45000ms 死等），母带少而长；另拍 9 张终端回放 freeze＋1 张 NPP
chunk 源码 freeze，3 张尾帧直接从母带抽，redblock contact 走 PIL
（make_redblock_contact.py）。take 间不靠固定 sleep 衔接，一律
wait_render_idle() 完成门控（命令行含 hyperframes 的 node 与
chrome-headless-shell 双判空），防命令在前台 render 运行时进输入缓冲。

机位（RECORD-NOTES 第一节）：一个锁标题 wt（hf08-rec，--suppressApplication
Title）；t2 不另开 tab——cmd 内敲 `powershell -NoProfile -NoLogo` 进子进程
跑完 exit 回 cmd（标题恒锁，guard 零风险）。NPP 仅 src-blackbar 一张。
open_rec_term 幂等发 chcp 65001（UTF-8，否则日志的 ◇/· 在 GBK 下乱码）；
more 分页镜头统一 quit_pager() 收尾（q 后空 ENTER 同步，防 cd 丢键）。

takes（ALL_TAKES 顺序不可换；t0 必须是冷态第一条，之前禁跑任何 render；
每个 take 开录前先过 wait_render_idle 完成门控，再 prepare_term 把
hf08-rec 窗显式置前过 HWND 闸——具名单跑任意 take 也安全，不隐式依赖
t0；2026-10-22 None 句柄事故见 RECORD-NOTES 第十节）：
  t0-sw        av-sync-calib 软件路冷跑（全链约 141s；母带 160s）
  t1-hw        同窗接跑硬件路（job 52.4s，热态；母带 77.5s）
  t2-hash      hashes/ 内 PowerShell Get-FileHash 六连，exit 回 cmd
  t3-badlint   bad-lint 默认 render（真机 141.2s；2 error＋Continuing，
               中段两轮 45000ms 等待整段弃，poll45 命中 2 次）
  t4-strict    bad-lint --strict（真机 12.6s；Aborting，exit1）
  t5-missing   missing-media 默认 render（真机 15.6s；缺音轨 mix 期即拦、
               无 45s 等待；audio_processing_failed，exit1）

用法：
  python record_segments.py t0-sw
  python record_segments.py t0-sw t1-hw t2-hash
  python record_segments.py all
  python record_segments.py freeze frames-dir gate-multi   # 单张回放
  python record_segments.py freeze-all                     # 10 张全拍
  python record_segments.py tail-freeze                    # 3 张母带尾帧

等待/时长常量彩排回填（run_rehearsal.py 的 build/rehearsal-timings.json）。
必须非沙箱（render 编码＋gdigrab）。
"""
import os
import shutil
import subprocess
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
HF03_ONEOFFS = os.path.join(HERE, "..", "..", "hf-03", "oneoffs")
sys.path.insert(0, HF03_ONEOFFS)
sys.path.insert(0, HERE)

import guard  # noqa: E402
import rec_automate as r  # noqa: E402
from blackmat import BlackMat  # noqa: E402

guard.install_input_guards(r)

import setup_scenes as S  # noqa: E402

# ---------- 路径 ----------
STAGE = S.DEFAULT_ROOT
CALIB = str(S.CALIB)
DIR_HASHES = os.path.join(STAGE, "hashes")
DIR_BADLINT = os.path.join(STAGE, "bad-lint")
DIR_MISSING = os.path.join(STAGE, "missing-media")
DIR_DEBUG = os.path.join(STAGE, "debug")
HF07_LOG = os.path.join(str(S.PROJECTS), "hf-07", "build", "render.log")

REC_DIR = r"F:\_hftest\hf08-rec\takes"
FREEZE_DIR = r"F:\_hftest\hf08-rec\freezes"
FRAME_DIR = r"F:\_hftest\hf08-rec\frames"
SCREEN_REC = r"F:\Data\gmeek-site\tools\screen-rec.js"
NPP_EXE = r"F:\_hftest\npp-local\notepad++.exe"
CHUNK_3W = (r"F:\npm-cache\_npx\82df529928acbd64\node_modules\hyperframes"
            r"\dist\chunk-3WG63KFW.js")

# ---------- 窗口几何（同 hf-06） ----------
WND_X, WND_Y, WND_W, WND_H = -12, 0, 1624, 928
TERM_X, TERM_Y = -12, 0
TERM_W, TERM_H = 1632, 1000
REC_TERM_TITLE = "hf08-rec"

NPX = "npx --yes hyperframes@0.8.107"
OUT_SW = r"F:\_hftest\hf08-rec\sw.mp4"
OUT_HW = r"F:\_hftest\hf08-rec\hw.mp4"
CMD_SW = NPX + " render . --no-browser-gpu -o " + OUT_SW
CMD_HW = NPX + " render . --browser-gpu -o " + OUT_HW
CMD_T3 = NPX + " render . -o out.mp4"
CMD_T4 = NPX + " render . --strict"
CMD_T5 = NPX + " render . -o out.mp4"
CMD_HASH = ("Get-FileHash soft-a.mp4,soft-b.mp4,1015-old.mp4,w1.mp4,hw-a.mp4,"
            "hw-b.mp4 -Algorithm SHA256 | Format-Table Path,Hash -AutoSize")

# ---------- 等待/时长（2026-10-21 正式录制日首录事故后重定） ----------
# 首录实证：探针 68.1s 是 render 内部 Timing 口径（尾报 rendered in），漏了
# CLI 层——重启后首跑 npx/node 冷启＋Checking browser 冷启 chrome 实测
# ENTER 后约 66s job 才开跑（job trace：calibration 187ms/frame p95、
# capture_disk 41.2s、encode start elapsedMs 60.6），全链约 141s。旧值
# WAIT=70 母带没盖住，后一条命令在 render 占前台时进控制台输入缓冲，六
# take 边界全错位作废（详见 RECORD-NOTES「首录时序事故」）。
# 新模型：母带盖住全链＋take 间 wait_render_idle() 完成门控双保险。
# sw 155：ENTER 约在录制 9s，母带 160s 盖到 ENTER+151（全链 141＋余 10）；
# hw 68：热态 CLI 约 8s＋job 52.4，母带 77.5s 余 7.5；
# t3 150：墙钟 141.2（rehearsal 口径已含 npx 启动），尾报入镜方便尾帧抽点；
# t4 14（strict 12.6）／t5 19（missing 15.6）；hash 9（六连秒回）。
WAIT = {"sw": 155.0, "hw": 68.0, "hash": 9.0, "t3": 150.0,
        "t4": 14.0, "t5": 19.0}
TYPE_RENDER = 4.5      # render 命令约 80 字符
TYPE_HASH = 6.0       # 130 字符
REC_EXTRA = 7.0       # 垫幕 1.2＋打字＋尾帧余量

os.makedirs(REC_DIR, exist_ok=True)
os.makedirs(FREEZE_DIR, exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)

_mat = None
_term_hwnd = None


# ---------- 终端 ----------

def _ensure_utf8():
    """控制台切 UTF-8 代码页：hf-07 render.log 的 ◇/│ 在 GBK(936) 下乱码。

    每次 open 幂等发一次（chcp 重设无副作用，>nul 吞回显），随后各镜头的
    cls 会清掉命令行本身。
    """
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.2)
    r.type_text("chcp 65001 >nul", delay=.03)
    time.sleep(.1)
    guard.assert_fg_safe()
    r.tap("ENTER")
    time.sleep(.5)


def open_rec_term(cwd=CALIB):
    """独立 WT 窗（cmd，cwd/三变量就位），外框盖满录区。绝不动用户 WT。"""
    global _term_hwnd
    existing = r.find_window(REC_TERM_TITLE)
    if existing:
        _term_hwnd = existing
        r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
        r.move(_term_hwnd, TERM_X, TERM_Y, TERM_W, TERM_H)
        time.sleep(.4)
        _ensure_utf8()
        return existing
    init = ('set "HYPERFRAMES_FONT_CACHE_DIR=F:\\_hftest\\.cache\\fonts" '
            '&& set "HYPERFRAMES_NO_UPDATE_CHECK=1" '
            '&& set "HYPERFRAMES_SKIP_SKILLS=1" && cls')
    # --suppressApplicationTitle 必须有：npx/powershell 都会 SetConsoleTitle。
    subprocess.Popen(["wt.exe", "-w", "new", "--title", REC_TERM_TITLE,
                      "--suppressApplicationTitle",
                      "-d", cwd, "cmd.exe", "/k", init])
    t0 = time.time()
    while time.time() - t0 < 20:
        h = r.find_window(REC_TERM_TITLE)
        if h:
            _term_hwnd = h
            break
        time.sleep(.5)
    if not _term_hwnd:
        raise RuntimeError("等不到 hf08-rec 终端窗口")
    time.sleep(1.2)
    r.u.ShowWindow(_term_hwnd, r.SW_RESTORE)
    r.move(_term_hwnd, TERM_X, TERM_Y, TERM_W, TERM_H)
    time.sleep(.5)
    _ensure_utf8()
    return _term_hwnd


def prepare_term(cwd=CALIB):
    """每个 take 开录前的就位闸：终端窗存在、几何就位、在前台、过 HWND 闸。

    2026-10-22 热录事故根因：具名 `... t1-hw ...` 起跑不经过 take_t0_sw，
    全局 _term_hwnd 保持 None，activate(None) 静默失败（前台仍是跑
    Claude Code 的 WT 窗）；guard 当年按 PID 认窗又被「同 WT 进程多窗口」
    洞穿，打字静直流向错误窗口。open_rec_term 对已存在窗口是幂等复用
    （不重开 wt、不动 Chrome 热态），chcp 在开录前敲入不入镜，故每个
    take 必调；返回时前台必须就是 hf08-rec 那个具体顶层窗。
    """
    open_rec_term(cwd)
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    return _term_hwnd


def quit_pager():
    """q 退 more 后空回车同步提示符。

    more.com 退出到 cmd 重建提示符有个窗口期，立刻敲下一张 cd 会整行丢键
    （2026-10-21 彩排三例三验：debug-tree/worker-sizing 后的 cd 全丢）。
    若内容不足一屏 more 已自动退出，q 会残留进输入行，ENTER 把它当 `q`
    命令执行掉，报错回显由下一张 cls 清——两种状态都收敛到干净提示符。
    """
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    r.tap("q")
    time.sleep(.8)
    guard.assert_fg_safe()
    r.tap("ENTER")
    time.sleep(.4)


def term_cmd(line, post=0.0):
    r.activate(_term_hwnd)
    guard.assert_fg_safe()
    time.sleep(.2)
    r.type_text(line, delay=.035)
    time.sleep(.15)
    guard.assert_fg_safe()
    r.tap("ENTER")
    if post:
        time.sleep(post)


def term_cd(path):
    term_cmd('cd /d "%s"' % path, post=.8)


def term_cls():
    term_cmd("cls", post=.7)


def park_mouse():
    r.mouse_move(12, 884)


def wheel(up_notches, down_notches=0):
    """鼠标滚轮（指针须在终端区内；Shift+PgUp 在 wt 无绑定，勿用）。"""
    r.mouse_move(700, 500)
    time.sleep(.2)
    total = up_notches - down_notches
    steps = abs(total)
    for _ in range(steps):
        r.u.mouse_event(0x0800, 0, 0, 120 if total > 0 else -120, 0)
        time.sleep(.12)
    time.sleep(.6)


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
    try:
        time.sleep(1.0)
        action()
        rest = duration - (time.time() - t0) - 1.2
        if rest > 0:
            time.sleep(rest)
        proc.wait(timeout=duration + 30)
    except BaseException:
        # action/等待异常时 node 与 ffmpeg 不会自退（ffmpeg 要跑满 -t 定时），
        # 不杀树就成孤儿继续写废片（2026-10-22 事故：77.5s 孤儿废片实证）。
        # /T 连 node 拉起的 ffmpeg 一起杀。
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True)
        raise
    print((proc.stdout.read() or "").strip()[-300:])
    extract_frames(name)
    return out


def extract_frames(name, every=2):
    src = os.path.join(REC_DIR, name + ".mp4")
    pat = os.path.join(FRAME_DIR, name + "-%02d.png")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", src, "-vf", "fps=1/%d,scale=800:-1" % every, pat],
                   check=True)
    print("frames:", name)


# ---------- take 间完成门控（首录事故后新增） ----------

def render_busy():
    """系统里是否还有 hyperframes render 链路进程（True＝前台仍被占）。

    判忙两条，命中任一即忙：
      1. 命令行含 hyperframes 的 node.exe——npx 父进程与 CLI 子进程命令行
         都含该字样；录屏器 screen-rec.js 自身虽是 node，命令行不含
         hyperframes，不会误伤；
      2. chrome-headless-shell.exe 仍存活（render 退出即随之退出）。
    """
    ps = ("(Get-CimInstance Win32_Process | Where-Object { "
          "($_.Name -eq 'node.exe' -and $_.CommandLine -like '*hyperframes*') "
          "-or $_.Name -eq 'chrome-headless-shell.exe' }).Count")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                         capture_output=True, text=True, timeout=20)
    return int((out.stdout or "").strip() or "0") > 0


def wait_render_idle(timeout=300.0):
    """下一 take 打字前，等上一条 render 链路彻底退出、cmd 提示符可用。

    固定 sleep 模型在冷态首跑被证伪（CLI 层 66s 未计入）：母带停录时
    render 可能仍在前台，后续命令进控制台输入缓冲排队、字符在 spinner
    刷新间隙碎行回显，take 边界整体错位。门控连续两轮（4s）判空才放行，
    避开进程退出间隙的误判；超时直接 raise——render 挂死时绝不能再敲
    命令重演缓冲事故。t0 之前也调一次，兼作开机零残留核验。
    """
    t0 = time.time()
    quiet = 0
    while time.time() - t0 < timeout:
        quiet = 0 if render_busy() else quiet + 1
        if quiet >= 2:
            return
        time.sleep(2.0)
    raise RuntimeError("等 render 链路退出超时（%ss），手动排查后再续"
                       % timeout)


def tail_freeze(take, at, freeze_name):
    """从母带指定秒抽单帧到 freezes/（hash6/strict-abort/missing-audio）。"""
    src = os.path.join(REC_DIR, take + ".mp4")
    out = os.path.join(FREEZE_DIR, freeze_name + ".png")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", str(at), "-i", src, "-frames:v", "1", out],
                   check=True)
    print("tail-freeze:", freeze_name)


def grab_freeze(freeze_name):
    """gdigrab 单帧 crop 到录区（与录屏同物理区、同几何）。"""
    out = os.path.join(FREEZE_DIR, freeze_name + ".png")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "gdigrab", "-i", "desktop",
                    "-vframes", "1", "-vf", "crop=1600:920:0:0", out],
                   check=True)
    print("freeze:", freeze_name)


# ---------- 6 take ----------

def _render_take(name, cwd, cmd, wait, dur_type):
    def act():
        # behind 是 NOACTIVATE，必须先显式把终端拉到前台再垫黑幕，
        # 否则黑幕垫了、终端没来（2026-10-22 None 事故的顺序根因）
        r.activate(_term_hwnd)
        guard.assert_fg_safe()
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        term_cd(cwd)
        term_cls()
        time.sleep(.6)
        term_cmd(cmd)
        time.sleep(wait + dur_type)     # 渲染全程＋尾报稳定
        park_mouse()
    duration = 2.0 + dur_type + wait + 3.0
    return record(name, duration, act)


def take_t0_sw():
    prepare_term(CALIB)
    park_mouse()
    # ★ 冷态第一条：本 take 之前整个会话不许跑过 render
    return _render_take("t0-sw", CALIB, CMD_SW, WAIT["sw"], 0.0)


def take_t1_hw():
    # 同窗接跑＝热态；prepare_term 对已存在终端是幂等复用（不重开 wt、
    # 不动 Chrome 热态），只把它重新置前并过 HWND 闸
    prepare_term(CALIB)
    return _render_take("t1-hw", CALIB, CMD_HW, WAIT["hw"], TYPE_RENDER)


def take_t2_hash():
    prepare_term(CALIB)

    def act():
        r.activate(_term_hwnd)
        guard.assert_fg_safe()
        _mat.behind(_term_hwnd)
        guard.assert_fg_safe()
        term_cd(DIR_HASHES)
        term_cls()
        time.sleep(.5)
        term_cmd("powershell -NoProfile -NoLogo", post=2.0)
        term_cmd(CMD_HASH, post=WAIT["hash"])
        # 必须显式 exit 回 cmd：否则 t3 起的 cd/cls/render 全落进 PowerShell
        # 子进程（cd /d 在 PS 报错、目录切不成，render 跑错工程）
        term_cmd("exit", post=1.0)
        park_mouse()
    return record("t2-hash", 4.0 + 3.0 + TYPE_HASH + WAIT["hash"] + 3.0, act)


def take_t3_badlint():
    prepare_term(CALIB)
    return _render_take("t3-badlint", DIR_BADLINT, CMD_T3,
                        WAIT["t3"], TYPE_RENDER)


def take_t4_strict():
    prepare_term(CALIB)
    return _render_take("t4-strict", DIR_BADLINT, CMD_T4,
                        WAIT["t4"], TYPE_RENDER)


def take_t5_missing():
    prepare_term(CALIB)
    return _render_take("t5-missing", DIR_MISSING, CMD_T5,
                        WAIT["t5"], TYPE_RENDER)


# ---------- 终端回放 freeze ----------
# (name, cwd, 命令, 出命令后等, 上滚轮格, 下滚轮格, 截后按键)
# 长输出一律 more 分页定点，不靠滚轮回几百行（2026-10-21 离线行数侦察后定）：
# tree /F debug 共 411 行，worker-0/1/2 在行 11–14、captured-frames 在 16，
# 首屏即齐；perf-summary.json 575 行，workerSizing 行 7–20、stages 行 31–43，
# worker-sizing 取首屏（more 头），perf-ledger 取 more +24（stages 落屏上沿）。
FREEZE_PLAYS = [
    # dir 尾屏：末段帧号＋「390 个文件」统计行，零滚动即含计数
    ("frames-dir", DIR_DEBUG, "dir captured-frames", 1.5, 0, 0, ""),
    # tree 经管道给 more 时固定按系统 OEM(GBK) 出制表字节，65001 解成
    # ◊◊、chcp 437 解成 └┬ñ┌ñ（2026-10-21 录制日两案皆验挂）；/A 用纯
    # ASCII（+--、|、\）画树，任何代码页都不乱
    ("debug-tree", STAGE, "tree /F /A debug | more", 2.0, 0, 0, "q"),
    ("perf-ledger", DIR_DEBUG, "more +24 perf-summary.json", 1.2, 0, 0, "q"),
    ("pngseq-dir", STAGE, "dir seq", 1.5, 0, 0, ""),
    ("gate-multi", STAGE,
     'findstr /C:"streaming-encode gate" logs\\run-a.log', 1.0, 0, 0, ""),
    # 备料（当前分镜未消费，docstring 挂 m09）：三串 OR 实测连 checkpoint
    # 心跳共 5+ 条长 JSON（每条折 3–4 物理行），总高超一屏、gate 滚出屏顶。
    # 改双 findstr && 只取首尾＝行63 开闸（enabled:true/single_worker）
    # ＋行151 尾报 drawelement capture·encode during capture 40.5s，一屏齐。
    ("gate-stream", STAGE,
     'findstr /C:"streaming-encode gate" logs\\hw-a.log && '
     'findstr /C:"drawelement capture" logs\\hw-a.log', 1.2, 0, 0, ""),
    ("worker-sizing", DIR_DEBUG, "more perf-summary.json", 1.2, 0, 0, "q"),
    ("no-timeline-warn", STAGE,
     'findstr /C:"not registered after 45000ms" logs\\bad-lint-default.log',
     1.2, 0, 0, ""),
]


def play_freeze(name, cwd, cmd, wait, up, down, quit_key):
    open_rec_term(CALIB)
    _mat.behind(_term_hwnd)
    guard.assert_fg_safe()
    term_cd(cwd)
    term_cls()
    time.sleep(.4)
    term_cmd(cmd, post=wait)
    if up or down:
        wheel(up, down)
    else:
        time.sleep(.5)
    park_mouse()
    time.sleep(.8)
    grab_freeze(name)
    if quit_key:
        quit_pager()


def freeze_hf07_timing():
    """more 分页器：7313 行起屏，目标 41m43.3s 在屏顶第二行，截完 q 退出。"""
    open_rec_term(CALIB)
    _mat.behind(_term_hwnd)
    guard.assert_fg_safe()
    term_cd(STAGE)
    term_cls()
    term_cmd('more +7312 "%s"' % HF07_LOG, post=1.5)
    park_mouse()
    time.sleep(.8)
    grab_freeze("hf07-timing")
    # 尾报仅 3 行，more 显示完已自动退出；quit_pager 两种状态都收敛
    quit_pager()


# ---------- NPP：chunk 黑条注释 ----------

def _enum_hf08_npp():
    found = []

    @r.ctypes.WINFUNCTYPE(r.ctypes.c_bool, r.wintypes.HWND, r.wintypes.LPARAM)
    def cb(wnd, _):
        c = r.ctypes.create_unicode_buffer(64)
        r.u.GetClassNameW(wnd, c, 64)
        if c.value == "Notepad++" and r.u.IsWindowVisible(wnd):
            ln = r.u.GetWindowTextLengthW(wnd)
            b = r.ctypes.create_unicode_buffer(ln + 1)
            r.u.GetWindowTextW(wnd, b, ln + 1)
            if guard.NPP_TITLE_NEEDLE in b.value:
                found.append((wnd, b.value))
        return True

    r.u.EnumWindows(cb, 0)
    return found


def close_any_npp():
    for _ in range(3):
        found = _enum_hf08_npp()
        if not found:
            return
        for wnd, _ in found:
            r.u.PostMessageW(wnd, 0x0010, 0, 0)
        t0 = time.time()
        while time.time() - t0 < 3:
            time.sleep(.3)
            if not _enum_hf08_npp():
                return
        time.sleep(.5)
    if _enum_hf08_npp():
        raise RuntimeError("三轮 WM_CLOSE 后仍有 chunk NPP 窗，手动确认后再续")


def freeze_src_blackbar():
    """NPP 开 chunk-3WG63KFW.js 直跳 10933 行拍黑条注释段。

    首版用 Ctrl+F 搜 vertical black slabs：2026-10-21 正式录制日实证非模态
    Find 对话框吃键不稳（ENTER/ESC 落到编辑器，查找未执行、框不关，还改脏
    文件）。文件实为 17,152 物理行（注释七行自带真实换行），check_anchors
    钉死注释在 10933–10937，直接命令行 -n10933 跳行：零对话框零键入。
    Wrap 须 off（便携默认）。
    """
    close_any_npp()
    subprocess.Popen([NPP_EXE, "-multiInst", "-nosession", "-n10933", CHUNK_3W])
    t0 = time.time()
    npp_hwnd = None
    while time.time() - t0 < 20:
        wins = _enum_hf08_npp()
        if wins:
            npp_hwnd = wins[0][0]
            break
        time.sleep(.5)
    if not npp_hwnd:
        raise RuntimeError("等不到 chunk NPP 窗")
    r.move(npp_hwnd, WND_X, WND_Y, WND_W, WND_H)
    time.sleep(2.5)  # 大文件加载＋词法着色＋跳行
    r.activate(npp_hwnd)
    guard.assert_fg_safe()
    time.sleep(.3)
    # NPP 是浅色窗，(12,884) 的箭头会落在水平滚动条上显形（彩排实证）；
    # park 到录区物理区 (0,0,1600,920) 外右下，grab crop 必然不含指针
    r.mouse_move(1650, 950)
    time.sleep(.8)
    grab_freeze("src-blackbar")
    close_any_npp()


# ---------- 母带尾帧 3 张（take 录完即抽；时长彩排回填后校 at） ----------

def do_tail_freeze():
    # ENTER 实测在录制 ~8.8s（垫幕后 cd/cls/打字串行），报文落屏＝8.8＋真机
    # 墙钟（t4 12.6→约21.4／t5 15.6→约24.4），at 取落屏后 1s 稳定帧；
    # t2 hash 命令 ENTER≈13.8s、表在 15–23s 在屏取 17.0。cut_shorts 目验后
    # 如需微调直接重跑本命令改 at。
    tail_freeze("t2-hash", 17.0, "hash6-run")
    tail_freeze("t4-strict", 22.0, "strict-abort")
    tail_freeze("t5-missing", 26.0, "missing-audio")


TAKES = {
    "t0-sw": take_t0_sw,
    "t1-hw": take_t1_hw,
    "t2-hash": take_t2_hash,
    "t3-badlint": take_t3_badlint,
    "t4-strict": take_t4_strict,
    "t5-missing": take_t5_missing,
}
ALL_TAKES = ["t0-sw", "t1-hw", "t2-hash", "t3-badlint", "t4-strict",
             "t5-missing"]

FREEZE_FNS = {name: (lambda n=name, c=cwd, cmd=cmd, w=w, u=u2, d=d2, q=qk:
                     play_freeze(n, c, cmd, w, u, d, q))
              for name, cwd, cmd, w, u2, d2, qk in FREEZE_PLAYS}
FREEZE_FNS["hf07-timing"] = freeze_hf07_timing
FREEZE_FNS["src-blackbar"] = freeze_src_blackbar


def main():
    global _mat
    args = sys.argv[1:] or ["all"]
    _mat = BlackMat()
    failed = False
    try:
        if args == ["all"]:
            for name in ALL_TAKES:
                print("\n===== take %s =====" % name, flush=True)
                wait_render_idle()
                TAKES[name]()
        elif args[0] == "freeze":
            for name in args[1:]:
                print("\n===== freeze %s =====" % name, flush=True)
                FREEZE_FNS[name]()
        elif args[0] == "freeze-all":
            for name in list(FREEZE_FNS):
                print("\n===== freeze %s =====" % name, flush=True)
                FREEZE_FNS[name]()
        elif args[0] == "tail-freeze":
            do_tail_freeze()
        else:
            for name in args:
                print("\n===== take %s =====" % name, flush=True)
                wait_render_idle()
                TAKES[name]()
    except BaseException as exc:
        # 2026-10-22 事故：except: raise 后 finally 里的 os._exit(0) 抢在
        # 解释器打印 traceback 之前终止进程，异常现场彻底消失、只留下孤儿
        # 录屏，排查走了一整轮弯路。这里显式把完整栈打出来再走 os._exit。
        failed = True
        print("\n[record_segments] 中止于 %s: %s"
              % (type(exc).__name__, exc), file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.stderr.flush()
    finally:
        _mat.close()
        sys.stdout.flush()
        sys.stderr.flush()
        # 仍须 os._exit：解释器自然退出会在非 Tk 线程销毁 Tcl 解释器，
        # tcl86t.dll 抛 0x80000003 硬崩溃（2026-10-22 WER 实证，退出码 3）
        os._exit(1 if failed else 0)


if __name__ == "__main__":
    main()
