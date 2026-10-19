# -*- coding: utf-8 -*-
r"""hf-07 录前彩排（不注入键鼠，只跑 CLI＋像素断言）。

把 take 表涉及的全部真机行为先演一遍：check 三工程、preview 生命周期与
裸 player 路由探测、snapshot 四连/慢表 at10/frames5/清扫/zoom、keyframes
报告与 --shot、compare、grade-compare，最后 verify 布景零污染。断言本集
灵魂事故的像素证据（蓝块四帧同位、红块四帧异位；t=10 红在左蓝在右）。
等待墙钟逐命令记录，末尾打印常量表供回填 record_segments.py。

用法（必须非沙箱：npx＋硬 GPU）：
  python projects/hf-07/oneoffs/setup_scenes.py init
  python projects/hf-07/oneoffs/run_rehearsal.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import setup_scenes as S  # noqa: E402

HF = ["npx.cmd", "--yes", "hyperframes@0.8.107"]
PROJ_REL = Path("proj")
LOG = HERE.parent / "build" / "rehearsal-log.txt"

results = []
_timings = []


# ---------- 基础 ----------

def run(proj: Path, argv: list, timeout: int = 240, env: dict | None = None):
    t0 = time.time()
    p = subprocess.run(HF + argv, cwd=str(proj),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=timeout, env=env)
    out = p.stdout.decode("utf-8", errors="replace")
    dt = time.time() - t0
    _timings.append((" ".join(argv[:2]), dt, p.returncode))
    return p.returncode, out, dt


def case(name):
    def deco(fn):
        fn._case = name
        return fn
    return deco


def _centroid(path: Path, y0r: float, y1r: float, pred):
    """在相对横条 [y0r,y1r)（比例）内找满足 pred(r,g,b) 的像素质心 x（比例）。"""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    W, H = im.size
    px = im.load()
    xs = []
    for y in range(int(H * y0r), int(H * y1r)):
        for x in range(0, W, 2):  # 横条采样够密，隔列省时间
            r, g, b = px[x, y]
            if pred(r, g, b):
                xs.append(x)
    if not xs:
        return None, (W, H)
    return sum(xs) / len(xs) / W, (W, H)


BLUE = lambda r, g, b: b > 120 and r < 90 and g < 140          # #1f6feb
BLUE_GREEN = lambda r, g, b: g > 110 and r < 90 and b < 110   # #238636
RED = lambda r, g, b: r > 150 and g < 100 and b < 100         # #da3633
LEGAL_GREEN = lambda r, g, b: g > 130 and r < 110 and b < 110  # #3fb950 合法 CSS 点


def snap_frames(d: Path):
    return sorted((d / "snapshots").glob("frame-*.png"))


# ---------- 各 case（返回 errs 列表；空＝PASS） ----------

@case("01 三工程 check exit 0")
def c01(proj, log):
    errs = []
    for d in ("v1", "v2", "v3"):
        code, out, dt = run(proj, ["check", d])
        log.write("--- check %s exit=%s %.1fs ---\n%s\n" % (d, code, dt, out[-2000:]))
        if code != 0:
            errs.append("%s check exit %s" % (d, code))
    return errs


@case("02 preview 生命周期＋player 路由探测")
def c02(proj, log):
    errs = []
    code, out, dt = run(proj, ["preview", "v1", "--background", "--no-open",
                               "--port", "3021"], timeout=90)
    log.write("--- preview start exit=%s %.1fs ---\n%s\n" % (code, dt, out))
    if code != 0:
        return ["preview --background exit %s" % code]
    time.sleep(2.0)

    def http_get(url):
        try:
            with urllib.request.urlopen(url, timeout=8) as r:
                body = r.read(300)
                return r.status, body[:120]
        except Exception as e:
            return None, repr(e).encode()

    for label, url in (("studio-root", "http://127.0.0.1:3021/"),
                       ("player", "http://127.0.0.1:3021/api/projects/v1/preview"
                                  "?__hf_shader_loading=player")):
        st, body = http_get(url)
        log.write("HTTP %s -> %s %r\n" % (label, st, body[:120]))
        if st != 200:
            errs.append("%s HTTP %s（PLAYER_URL 待改）" % (label, st))

    code, out, _ = run(proj, ["preview", "--list"])
    log.write("--- preview --list ---\n%s\n" % out)
    if "3021" not in out:
        errs.append("--list 无 3021")

    code, out, _ = run(proj, ["preview", "v1", "--stop"])
    log.write("--- preview --stop ---\n%s\n" % out)
    code, out, _ = run(proj, ["preview", "--list"])
    log.write("--- preview --list(after stop) ---\n%s\n" % out)
    if "No active" not in out:
        errs.append("--stop 后 list 仍有 server")
    return errs


@case("03 snapshot 四连：蓝同位/红异位（★灵魂事故）")
def c03(proj, log):
    code, out, dt = run(proj, ["snapshot", "v1", "--at", "2,2,2,2",
                               "--no-end", "--no-browser-gpu"])
    log.write("--- snap4 exit=%s %.1fs ---\n%s\n" % (code, dt, out[-2500:]))
    errs = []
    if code != 0:
        return ["snap4 exit %s" % code]
    # --no-end：只留四个 at-2s 帧（默认会追加 11.64s 尾帧，接触表也跟着多一格）
    frames = sorted((proj / "v1" / "snapshots").glob("frame-*-at-2s.png"))
    if len(frames) != 4:
        return ["at-2s 帧 %d≠4（是否漏 --no-end？）" % len(frames)]
    if not (proj / "v1" / "snapshots" / "contact-sheet.jpg").is_file():
        errs.append("缺 contact-sheet.jpg")
    blues, reds, greens = [], [], []
    for f in frames:
        bx, size = _centroid(f, .26, .37, BLUE)   # 蓝条带 top280/1080≈.26
        rx, _ = _centroid(f, .59, .70, RED)       # 红条带 top640≈.59
        # 合法 CSS 绿点 top48px（scale 外扩到 ~90px）：WAAPI 接管须四帧同位
        gx, _ = _centroid(f, .035, .095, LEGAL_GREEN)
        blues.append(bx)
        reds.append(rx)
        greens.append(gx)
        log.write("%s size=%s blue=%s green=%s red=%s\n"
                  % (f.name, size, bx, gx, rx))
    if any(b is None for b in blues):
        errs.append("有帧找不到蓝块")
    elif max(blues) - min(blues) > 0.006:
        errs.append("蓝块四帧异位（max-min=%.4f）" % (max(blues) - min(blues)))
    if any(g is None for g in greens):
        errs.append("有帧找不到合法 CSS 绿点")
    elif max(greens) - min(greens) > 0.006:
        errs.append("绿点四帧异位（CSS 未被 WAAPI 接管？max-min=%.4f）"
                    % (max(greens) - min(greens)))
    real = [x for x in reds if x is not None]
    if len(real) < 4:
        errs.append("有帧找不到红块")
    else:
        distinct = sum(1 for i, x in enumerate(sorted(reds))
                       if i == 0 or x - sorted(reds)[i - 1] > 0.008)
        if distinct < 3:
            errs.append("红块四帧位置不足 3 种（distinct=%d, %s）"
                        % (distinct, ["%.4f" % x for x in reds]))
    return errs


@case("04 snapshot v3 --at 10：慢表红贴起点、蓝在终点")
def c04(proj, log):
    code, out, dt = run(proj, ["snapshot", "v3", "--at", "10",
                               "--no-end", "--no-browser-gpu"])
    log.write("--- snap10 exit=%s %.1fs ---\n%s\n" % (code, dt, out[-1500:]))
    if code != 0:
        return ["snap v3 exit %s" % code]
    frames = sorted((proj / "v3" / "snapshots").glob("frame-*-at-10s.png"))
    if not frames:
        return ["v3 无 at-10s 帧"]
    bx, _ = _centroid(frames[0], .26, .37, BLUE)
    rx, _ = _centroid(frames[0], .59, .70, RED)
    log.write("t=10 blue=%s red=%s\n" % (bx, rx))
    errs = []
    if bx is None or bx < 0.50:        # 蓝在 x=800 终位：left200+800，中心/1920≈.55
        errs.append("蓝块未在终点（blue=%s）" % bx)
    # v3 红块是 60s 一圈的自掐表（真机三跑 red≈.146 稳定）：
    # 截图墙钟 ~8–15s ⇒ translateX≤200px，红中心 ≤(200+200+60)/1920≈.24
    if rx is None or rx > 0.35:
        errs.append("红块未在起点附近（red=%s，慢钟未生效？）" % rx)
    return errs


@case("05 snapshot --frames 5：五帧＋接触表")
def c05(proj, log):
    code, out, dt = run(proj, ["snapshot", "v1", "--frames", "5",
                               "--no-browser-gpu"])
    log.write("--- frames5 exit=%s %.1fs ---\n%s\n" % (code, dt, out[-1500:]))
    errs = []
    if code != 0:
        return ["frames5 exit %s" % code]
    frames = snap_frames(proj / "v1")
    if len(frames) != 5:
        errs.append("frame 数 %d≠5" % len(frames))
    if not (proj / "v1" / "snapshots" / "contact-sheet.jpg").is_file():
        errs.append("缺 contact-sheet.jpg")
    log.write("5 帧文件名：%s\n" % [f.name for f in frames])
    return errs


@case("06 只清自己的帧：MARKER.txt 保留、frame 换批")
def c06(proj, log):
    sd = proj / "v1" / "snapshots"
    marker = sd / "MARKER.txt"
    marker.write_text("keep me\n", encoding="utf-8")
    code, out, _ = run(proj, ["snapshot", "v1", "--frames", "3",
                              "--no-browser-gpu"])
    log.write("--- frames3 exit=%s ---\n%s\n" % (code, out[-800:]))
    errs = []
    if not marker.is_file():
        errs.append("MARKER.txt 被误删")
    if len(snap_frames(proj / "v1")) != 3:
        errs.append("frame 数≠3")
    return errs


@case("07 zoom：#bad 成功出图、#nope 硬 error（真机文案回填）")
def c07(proj, log):
    errs = []
    code, out, dt = run(proj, ["snapshot", "v1", "--at", "4",
                               "--zoom", "#bad", "--no-end",
                               "--no-browser-gpu"])
    log.write("--- zoom #bad exit=%s %.1fs ---\n%s\n" % (code, dt, out[-1500:]))
    if code != 0:
        errs.append("zoom #bad exit %s" % code)
    # zoom 不另起名：裁图就是 frame-00-at-4s.png（--no-end 后唯一帧），
    # 尺寸按 #bad bbox 裁剪，必小于全幅 1920
    zf = proj / "v1" / "snapshots" / "frame-00-at-4s.png"
    if zf.is_file():
        from PIL import Image
        with Image.open(zf) as im:
            zw, zh = im.size
        log.write("zoom 裁图：%s %dx%d\n" % (zf.name, zw, zh))
        if zw >= 1920:
            errs.append("zoom 裁图宽 %d 未裁剪" % zw)
    else:
        errs.append("缺 frame-00-at-4s.png 裁图")
    code2, out2, _ = run(proj, ["snapshot", "v1", "--at", "4",
                                "--zoom", "#nope", "--no-end",
                                "--no-browser-gpu"])
    log.write("--- zoom #nope exit=%s ---\n%s\n" % (code2, out2[-1500:]))
    if code2 == 0:
        errs.append("zoom #nope 居然 exit 0")
    # 真机文案（2026-10-19）：✗ Snapshot failed: --zoom selector matched
    # no element: #nope。注意失败轮也会先清扫 frame-*.png（t05 录后补跑产图）
    first_err = next((ln for ln in out2.splitlines()
                      if ln.strip() and "failed" in ln.lower()),
                     out2.strip().splitlines()[-1:])
    log.write("ZOOM_ERROR_TEXT>>> %s\n" % first_err)
    return errs


@case("08 keyframes 无参报告＋--json：#bad 隐身（机器看不见它在动）")
def c08(proj, log):
    errs = []
    code, out, dt = run(proj, ["keyframes", "v1"])
    log.write("--- keyframes v1 exit=%s %.1fs ---\n%s\n" % (code, dt, out[-2500:]))
    if code != 0:
        return ["keyframes exit %s" % code]
    # 真机 3 items：#good/#clock（GSAP）＋@keyframes legalPulse #legal（合法 CSS
    # 在册）；自掐表 #bad 没有任何声明可静态检出，报告里不得出现。
    if "#bad" in out:
        errs.append("无参报告里竟出现 #bad（它不是不可见吗？）")
    if "#good" not in out:
        errs.append("报告缺 #good")
    if "legalPulse" not in out or "#legal" not in out:
        errs.append("报告缺合法 CSS 项 legalPulse/#legal（口播『CSS 也查得到』无支撑）")
    code, out, _ = run(proj, ["keyframes", "v1", "--json"])
    log.write("--- keyframes --json (tail) ---\n%s\n" % out[-1500:])
    try:
        data = json.loads(out[out.index("{"):])
    except (ValueError, json.JSONDecodeError):
        return errs + ["--json 输出不是纯 JSON（可能有前导行，录制命令注意）"]
    # 真机结构：cssKeyframes/tweens 检出都挂在 compositions[0] 下
    comps = data.get("compositions") or []
    if not comps:
        return errs + ["--json 无 compositions"]
    c0 = comps[0]
    css = c0.get("cssKeyframes") or []
    css_names = [k.get("name") for k in css]
    css_sels = [s for k in css for s in (k.get("selectors") or [])]
    if "legalPulse" not in css_names or "#legal" not in css_sels:
        errs.append("cssKeyframes 未在册登记 legalPulse/#legal：%r %r"
                    % (css_names, css_sels))
    if "#bad" in css_sels:
        errs.append("cssKeyframes 里竟有 #bad")
    tweens = c0.get("tweens") or []
    targets = {t.get("target") for t in tweens}
    if "#good" not in targets:
        errs.append("tweens 里没有 #good（targets=%s）" % targets)
    if "#bad" in targets:
        errs.append("tweens 里竟有 #bad")
    log.write("comp0 keys=%s css=%s/%s tween_targets=%s\n"
              % (list(c0.keys()), css_names, css_sels, targets))
    return errs


@case("09 keyframes --shot：#good 洋葱皮成图；#bad 硬报错 nothing animates")
def c09(proj, log):
    errs = []
    forms = [
        ["keyframes", "v1", "--shot", "build/onion-good.png",
         "--selector", "#good"],
        ["keyframes", "v1/index.html", "--shot", "build/onion-good.png",
         "--selector", "#good"],
    ]
    from PIL import Image
    winner = None
    for argv in forms:
        code, out, dt = run(proj, argv)
        log.write("--- shot #good form=%s exit=%s %.1fs ---\n%s\n"
                  % (argv[1], code, dt, out[-1200:]))
        png = proj / "build" / "onion-good.png"
        if code == 0 and png.is_file() and png.stat().st_size > 10_000:
            winner = argv
            with Image.open(png) as im:
                log.write("onion-good.png %s\n" % (im.size,))
            break
    log.write("SHOT_WINNER>>> %s\n" % (" ".join(winner) if winner else None))
    if not winner:
        errs.append("onion-good 两种命令形态都失败")
    # #bad：真机 exit 1 且不出图——「机器根本不知道它在动」。
    # 2026-10-19 文案（加合法绿点后）：--shot: nothing animates under '#bad'.
    # Nearest animated elements: #good, #clock, #legal.（只断言 nothing animates，
    # Nearest 名单随布景演进，全文留日志）
    png_bad = proj / "build" / "onion-bad.png"
    if png_bad.is_file():
        png_bad.unlink()   # 防旧档串味
    code, out, dt = run(proj, ["keyframes", "v1/index.html", "--shot",
                               "build/onion-bad.png", "--selector", "#bad"])
    log.write("--- shot #bad exit=%s %.1fs ---\n%s\n" % (code, dt, out[-1200:]))
    if code == 0 or png_bad.is_file():
        errs.append("#bad 竟 exit 0 或出了洋葱皮（真机应硬 error 无图）")
    if "nothing animates" not in out:
        errs.append("#bad 报错不含 nothing animates（文案变了？）")
    return errs


@case("10 compare：两变体成图；labels 数量不符 exit 1")
def c10(proj, log):
    errs = []
    argv = ["compare", "v1", "v2", "--at", "4",
            "--labels", "方案A·x800,方案B·x500", "--out", "build/compare.png"]
    code, out, dt = run(proj, argv)
    log.write("--- compare exit=%s %.1fs ---\n%s\n" % (code, dt, out[-1500:]))
    if code != 0:
        errs.append("compare exit %s" % code)
    png = proj / "build" / "compare.png"
    if png.is_file():
        from PIL import Image
        with Image.open(png).convert("RGB") as im:
            W, H = im.size
            log.write("compare.png %s %dB\n" % (im.size, png.stat().st_size))
            # 事实记录（2026-10-19 真机）：两格红块格内质心几乎同位（差≈0.01）
            # ——compare 在同一浏览器实例内近乎同时导航/截图，两个自掐表
            # 相位被启动时差锁死，「各停各墙钟」暗线在 compare 里不成立
            # （单次 snapshot 四连帧红异位才是事故证据，见 c03）。只 log。
            px = im.load()

            def red_cx(x0r, x1r, cell_left):
                xs = []
                for y in range(int(H * .55), int(H * .80)):
                    for x in range(int(W * x0r), int(W * x1r), 2):
                        r, g, b = px[x, y]
                        if r > 150 and g < 100 and b < 100:
                            xs.append(x)
                if not xs:
                    return None
                return (sum(xs) / len(xs) / W - cell_left) / .5
            cl, cr = red_cx(.02, .48, 0.0), red_cx(.52, .98, .5)
            log.write("compare 红块格内质心 left=%s right=%s 差=%s\n"
                      % (cl, cr, None if cl is None or cr is None
                         else "%.4f" % abs(cl - cr)))
    else:
        errs.append("无 build/compare.png")
    code2, out2, _ = run(proj, ["compare", "v1", "v2",
                                "--at", "4", "--labels", "只有一个"])
    log.write("--- compare bad labels exit=%s ---\n%s\n" % (code2, out2[-600:]))
    # 真机：数量不符 exit 1（非 2），文案 "--labels count (1) must match path count (2)"
    if code2 != 1:
        errs.append("labels 数量不符预期 exit 1，实得 %s" % code2)
    return errs


# active grading 在本机 headless hardware 模式必撞导航 10s 超时（UHD 620），
# 必须 software 渲染（真机 ~29.5s/次），另给浏览器 render-ready 超时 30s。
SW_ENV = {**os.environ, "PRODUCER_BROWSER_GPU_MODE": "software"}

# 像素闸（0–255 口径，2×2 格位、跳过 46px 标签条）：no-op 三格全等＝全 0；
# 教学可视档真机暖色 MAD=(11.8,1.8,10.2)/显著 94.3%，
# 高亮 (13.7,10.9,8.3)/93.5%（显著＝任一通道差 >GRADE_DIFF_T）。
# 阈值取半空档，留足余量。
GRADE_MAD_MIN = 6.0       # 任一通道平均差须超过
GRADE_FRAC_MIN = 0.25     # 显著像素占比须超过（实测 94%/94%）
GRADE_DIFF_T = 6


def grade_metrics(png: Path):
    """2×2 grade 图：左上 original／右上暖色／左下高亮／右下留空。
    暖色、高亮各对 original 算 (三通道 MAD, 显著像素占比)；跳过顶部
    46px 标签条（三格标签文字不同，免得白字进差分）。"""
    im = Image.open(png).convert("RGB")
    W, H = im.size
    hw, hh = W // 2, H // 2
    boxes = {
        "orig": (0, 46, hw, hh),
        "warm": (hw, 46, W, hh),
        "bright": (0, hh + 46, hw, H),
    }
    g = {k: list(im.crop(b).getdata()) for k, b in boxes.items()}
    base = g["orig"]
    out = []
    for key in ("warm", "bright"):
        px = g[key]
        n = len(px)
        s = [0, 0, 0]
        hot = 0
        for (r0, g0, b0), (r1, g1, b1) in zip(base, px):
            d = (abs(r1 - r0), abs(g1 - g0), abs(b1 - b0))
            s[0] += d[0]
            s[1] += d[1]
            s[2] += d[2]
            if max(d) > GRADE_DIFF_T:
                hot += 1
        out.append((tuple(v / n for v in s), hot / n))
    return out


@case("11 grade-compare：三格成图＋active grading 像素闸（software 渲染）")
def c11(proj, log):
    # c07 的 #nope 失败轮会清空 snapshots，先自备一张实拍帧（与录制 t08 同构）
    code, out, _ = run(proj, ["snapshot", "v1", "--at", "4",
                             "--no-end", "--no-browser-gpu"])
    if code != 0:
        return ["备帧 snapshot exit %s" % code]
    frame = next((proj / "v1" / "snapshots").glob("frame-*.png"))
    rel = "v1/snapshots/" + frame.name
    forms = [
        ["grade-compare", "--for", rel, "--grades", "grades.json",
         "--out", "build/grade.png", "--timeout", "30000"],
        ["grade-compare", "--for", rel, "--grades", "grades.json",
         "--project", "v1", "--out", "build/grade.png",
         "--timeout", "30000"],
    ]
    errs = []
    winner = None
    for argv in forms:
        code, out, dt = run(proj, argv, env=SW_ENV)
        log.write("--- grade form tail=%s exit=%s %.1fs ---\n%s\n"
                  % (argv[-4:], code, dt, out[-1500:]))
        png = proj / "build" / "grade.png"
        if not (code == 0 and png.is_file() and png.stat().st_size > 10_000):
            continue
        # 闸①：grading schema 不认时工具自报 inactive/no-op，三格全等
        if "inactive/no-op" in out:
            log.write("grade form 命中 inactive/no-op 警告，判失败\n")
            continue
        # 闸②：两档候选必须真的改了像素（CSS filter 串事故＝三格全等漏网根源）
        metrics = grade_metrics(png)
        log.write("grade metrics 暖色 MAD=(%.1f,%.1f,%.1f) hot=%.1f%% | "
                  "高亮 MAD=(%.1f,%.1f,%.1f) hot=%.1f%%\n"
                  % (metrics[0][0][0], metrics[0][0][1], metrics[0][0][2],
                     metrics[0][1] * 100,
                     metrics[1][0][0], metrics[1][0][1], metrics[1][0][2],
                     metrics[1][1] * 100))
        ok = all(max(m[0]) > GRADE_MAD_MIN and m[1] > GRADE_FRAC_MIN
                 for m in metrics)
        if ok:
            winner = argv
            break
    log.write("GRADE_WINNER>>> %s\n" % (" ".join(winner) if winner else None))
    if not winner:
        errs.append("grade-compare 无形态过闸（exit/inactive/像素差异）")
    return errs


@case("12 布景零污染：verify 与 backup 逐字节一致")
def c12(proj, log):
    return ["verify FAIL"] if S.verify(S_ROOT, quiet=True) else []


S_ROOT = Path(S.DEFAULT_ROOT)

CASES = [c01, c02, c03, c04, c05, c06, c07, c08, c09, c10, c11, c12]


def main():
    root = Path(S.DEFAULT_ROOT)
    proj = root / PROJ_REL
    if not (root / "backup").is_dir():
        sys.exit("布景未 init：python projects/hf-07/oneoffs/setup_scenes.py init")
    if not shutil.which("npx.cmd") and not shutil.which("npx"):
        sys.exit("PATH 中找不到 npx")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    logf = LOG.open("w", encoding="utf-8", newline="\n")
    nfail = 0
    try:
        for fn in CASES:
            name = fn._case
            logf.write("\n===== %s =====\n" % name)
            logf.flush()
            print("→ %s ... " % name, end="", flush=True)
            try:
                errs = fn(proj, logf)
            except Exception as e:
                errs = ["EXC %r" % e]
            logf.flush()
            if errs:
                nfail += 1
                print("FAIL\n    " + "\n    ".join(errs))
            else:
                print("PASS")
            results.append((name, errs))
    finally:
        logf.write("\n===== 等待常量（热态墙钟，秒）=====\n")
        for cmd, dt, code in _timings:
            logf.write("%-46s %6.1f  exit=%s\n" % (cmd, dt, code))
        logf.close()

    print("\n" + "=" * 60)
    for name, errs in results:
        if errs:
            print("✗ %s\n    %s" % (name, "\n    ".join(errs)))
    print("=" * 60)
    print("PASS %d/%d  日志：%s" % (len(CASES) - nfail, len(CASES), LOG))
    print("等待常量表见日志末尾（回填 record_segments 的 *_WAIT）")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
