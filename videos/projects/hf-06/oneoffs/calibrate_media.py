# -*- coding: utf-8 -*-
r"""hf-06 素材响度校准器：把真机 normalize 显示值锚到口播念的数字。

为什么需要它：voice/music/music15 三件 wav 从蝉镜母带 ffmpeg 直切，而蝉镜
每次整段重渲染都有 ±0.2 dB 波形微漂（v1→v2 实测 voice −21.5→−21.8、
music15 需增益 16.2→16.0）。口播念的是一位小数定值，改口播就得重合成、
重合成又会漂——死循环。斩断法：合成后用 ffmpeg volume 对素材做确定性
微调，让 0.8.107 normalize 真机实测值精确等于口播数字，之后母带再重合成
只需重跑本脚本。

锁定目标（与 src/hf-06-src.txt 一致）：
  voice referenceLufs 一位小数 = -21.8
  s9 music15 报错            = needs 16.0 dB（+12 dB 天花板演示）
  副产物（封面/彩排断言用，落 build/media-calibration.json）：
    music targetLufs、gainDb、--write 写回的 6 位 volume、truePeak

算法：
  1. k_dB 整体平移：voice/music/music15 同乘 10^(k/20)，三件一起响/轻，
     LUFS 差不变（normalize 建议 volume 比值只取决于差），voice 绝对值
     精确落到 -21.8（真机一位小数显示即 -21.8，落区间 [-21.85,-21.75)）；
  2. music15 追差微调 a15（只重切 music15）：needs 值对系数的斜率
     20 dB/十倍程，按实测 dB 差反推系数，最多两轮；
  3. 终检：s0 normalize dry 全套字段＋s9 报错串逐字断言，restore s0。

顺序：setup_scenes.py init（从母带直切原始件）→ 本脚本 → run_rehearsal.py。
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import setup_scenes as S  # noqa: E402

ROOT = S.DEFAULT_ROOT
PROJ = os.path.join(ROOT, "proj")
MEDIA = os.path.join(PROJ, "media")
BACKUP = os.path.join(ROOT, "backup")
CALIB = os.path.join(S.P, "build", "media-calibration.json")

HF = ["npx.cmd", "--yes", "hyperframes@0.8.107"]
VOICE_TARGET = -21.8      # 口播：「负二十一点八 LUFS」
CEIL_TARGET = 16.0        # 口播：「差了十六点零分贝」
TOL_HALF = 0.049          # 一位小数四舍五入到目标的半格减余量

ENV = dict(os.environ,
           HYPERFRAMES_FONT_CACHE_DIR=r"F:\_hftest\.cache\fonts",
           HYPERFRAMES_NO_UPDATE_CHECK="1",
           HYPERFRAMES_SKIP_SKILLS="1")


def cut(voice_k=1.0, music_v=0.4, m15_v=0.15):
    """从母带切三件：voice 头 6s；music/music15 取 60s 处 6s。

    系数均含整体校准偏移 voice_k（三件同源平移）。
    """
    jobs = [
        ("voice.wav",
         ["ffmpeg", "-y", "-loglevel", "error", "-i", str(S.WAV_MASTER),
          "-t", "6", "-af", "volume=%.8f" % voice_k,
          os.path.join(MEDIA, "voice.wav")]),
        ("music.wav",
         ["ffmpeg", "-y", "-loglevel", "error", "-ss", "60",
          "-i", str(S.WAV_MASTER), "-t", "6",
          "-af", "volume=%.8f" % (music_v * voice_k),
          os.path.join(MEDIA, "music.wav")]),
        ("music15.wav",
         ["ffmpeg", "-y", "-loglevel", "error", "-ss", "60",
          "-i", str(S.WAV_MASTER), "-t", "6",
          "-af", "volume=%.8f" % (m15_v * voice_k),
          os.path.join(MEDIA, "music15.wav")]),
    ]
    for name, cmd in jobs:
        subprocess.run(cmd, check=True)
        print("切", name, "系数", cmd[cmd.index("-af") + 1])


def norm_dry():
    """s0 态跑 normalize --json，返回解析后的 dict。"""
    p = subprocess.run(HF + ["normalize-audio", "--reference", "voice",
                             "--target", "bgm", "--json"],
                       cwd=PROJ, env=ENV, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    m = re.search(r"\{.*\}", p.stdout, re.S)
    if not m:
        sys.exit("normalize 无 JSON 输出：\n" + p.stdout[-800:] + p.stderr[-400:])
    return json.loads(m.group(0))


def ceiling_need():
    """临时覆 s9 态跑 normalize，解析 needs X.X dB；结束 restore s0。"""
    shutil.copyfile(os.path.join(BACKUP, "s9-ceiling", "index.html"),
                    os.path.join(PROJ, "index.html"))
    try:
        p = subprocess.run(HF + ["normalize-audio", "--reference", "voice",
                                 "--target", "bgm", "--json"],
                           cwd=PROJ, env=ENV, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=120)
    finally:
        shutil.copyfile(os.path.join(BACKUP, "s0-good", "index.html"),
                        os.path.join(PROJ, "index.html"))
    text = p.stdout + p.stderr
    m = re.search(r"needs (\d+\.?\d*) dB", text)
    if p.returncode == 0 or not m:
        sys.exit("s9 未撞天花板（exit=%d）：\n%s" % (p.returncode, text[-800:]))
    return float(m.group(1))


def r1_close(x, target):
    """真机一位小数显示等于 target（x 落其四舍五入区间，留安全余量）。"""
    shown = round(x + 1e-9, 1)
    return abs(shown - target) < 1e-9


def main():
    if not os.path.exists(S.WAV_MASTER):
        sys.exit("缺母带：%s" % S.WAV_MASTER)
    os.makedirs(os.path.dirname(CALIB), exist_ok=True)

    # ---- 第 0 轮：原始切片测自然值 ----
    print("== 第 0 轮：原始切片（k=0, a15=0.15）==")
    cut(1.0, 0.4, 0.15)
    d0 = norm_dry()
    v0 = d0["referenceLufs"]
    k = VOICE_TARGET - v0          # dB，精确平移到 -21.8
    klin = 10.0 ** (k / 20.0)
    print("voice 自然值 %.3f → 整体偏移 %+.3f dB（系数 %.8f）" % (v0, k, klin))
    if abs(k) > 2.5:
        sys.exit("偏移 %.2f dB 异常大，先查母带/切片" % k)

    # ---- 第 1 轮：三件一起平移 ----
    print("== 第 1 轮：整体平移 ==")
    cut(klin, 0.4, 0.15)
    a15 = 0.15
    g15 = ceiling_need()
    print("music15 needs %.2f dB（目标 %.1f）" % (g15, CEIL_TARGET))

    # ---- 第 2 轮：按 dB 差反推 music15 系数 ----
    for rnd in range(3):
        if r1_close(g15, CEIL_TARGET):
            break
        # needs 随 a15 增大而减小（文件越响，需要补的越少），20 dB/十倍程
        a15 = a15 * (10.0 ** ((g15 - CEIL_TARGET) / 20.0))
        if a15 <= 0 or a15 > 1:
            sys.exit("music15 系数越界：%.6f" % a15)
        print("== 第 %d 轮微调：a15=%.6f ==" % (rnd + 2, a15))
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-ss", "60",
             "-i", str(S.WAV_MASTER), "-t", "6",
             "-af", "volume=%.8f" % (a15 * klin),
             os.path.join(MEDIA, "music15.wav")], check=True)
        g15 = ceiling_need()
        print("music15 needs %.2f dB" % g15)
    else:
        sys.exit("music15 三轮仍未锚到 %.1f（末值 %.2f）" % (CEIL_TARGET, g15))

    # ---- 终检：s0 全套字段 ----
    print("== 终检 ==")
    d = norm_dry()
    checks = {
        "referenceLufs": r1_close(d["referenceLufs"], VOICE_TARGET),
        "projectedLufs": r1_close(d["projectedLufs"], VOICE_TARGET),
        "wrote:false": d["wrote"] is False,
        "ceiling 16.0": r1_close(g15, CEIL_TARGET),
    }
    # 写回值预测：--write 以 6 位小数落 data-volume，幂等跑读 previousVolume
    vol6 = round(d["volume"], 6)

    out = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "master": os.path.basename(str(S.WAV_MASTER)),
        "voice_k_db": round(k, 4),
        "voice_k_lin": round(klin, 8),
        "music15_coef": round(a15, 6),
        "referenceLufs": d["referenceLufs"],
        "targetLufs": d["targetLufs"],
        "projectedLufs": d["projectedLufs"],
        "gainDb": d["gainDb"],
        "volume_exact": d["volume"],
        "volume_written": vol6,
        "truePeakDbfs": d["projectedTruePeakDbfs"],
        "ceiling_needs_db": g15,
        "display": {
            "voice_lufs": round(d["referenceLufs"] + 1e-9, 1),
            "music_lufs": round(d["targetLufs"] + 1e-9, 1),
            "ceiling_db": round(g15 + 1e-9, 1),
        },
    }
    with open(CALIB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    bad = [k_ for k_, ok in checks.items() if not ok]
    if bad:
        sys.exit("校准终检失败：%s" % bad)
    print("\n✓ 校准完成：voice %.1f LUFS／music15 needs %.1f dB／写回 %s"
          % (out["display"]["voice_lufs"], out["display"]["ceiling_db"], vol6))
    print("台账：", CALIB)


if __name__ == "__main__":
    main()
