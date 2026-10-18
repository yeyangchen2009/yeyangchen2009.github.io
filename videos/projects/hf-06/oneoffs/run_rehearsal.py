# -*- coding: utf-8 -*-
r"""hf-06 录前彩排（不注入键鼠，只驱动布景＋CLI）。

把 take 表的 16 条命令全部真机跑一遍，断言 MEDIA-FACTS.md 里的规则名/退出码，
全量日志落 build/rehearsal-log.txt。录屏当天可重跑核对，避免现场翻车。

用法：python projects/hf-06/oneoffs/run_rehearsal.py [--root F:\_hftest\hf06-media]
必须非沙箱（npx ＋ ffmpeg loudnorm）。
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import setup_scenes as S  # noqa: E402

HF = ["npx.cmd", "--yes", "hyperframes@0.8.107"]
PROJ_REL = Path("proj")
LOG = HERE.parent / "build" / "rehearsal-log.txt"


def edit_index(proj: Path, old: str, new: str, expect: int = 1) -> None:
    """模拟录屏时 NPP 的现场编辑：唯一锚点替换（LF 写回）。"""
    f = proj / "index.html"
    html = f.read_text(encoding="utf-8")
    n = html.count(old)
    assert n == expect, "锚点 %r 出现 %d 次，预期 %d" % (old, n, expect)
    f.write_text(html.replace(old, new), encoding="utf-8", newline="\n")


def restore(root: Path, name: str) -> None:
    S.restore(root, name)


def run(proj: Path, argv: list, timeout: int = 240) -> tuple:
    t0 = time.time()
    p = subprocess.run(HF + argv, cwd=str(proj),
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=timeout)
    out = p.stdout.decode("utf-8", errors="replace")
    return p.returncode, out, time.time() - t0


# (case, setup 函数, argv, 预期退出码, 必含串[], 必不含串[])
def cases(root: Path):
    proj = root / PROJ_REL

    def s0(*_): restore(root, "s0-good")
    def s4(*_): restore(root, "s4-missing")
    def s5(*_): restore(root, "s5-sametrack")
    def s8(*_): restore(root, "s8-placeholder")
    def s9(*_): restore(root, "s9-ceiling")

    def e_noid(*_):
        s0()
        edit_index(proj, ' id="demo"', "")
    def e_nomuted(*_):
        s0()
        edit_index(proj, " muted", "")
    def e_badsrc(*_):
        s0()
        edit_index(proj, "media/voice.wav", "media/voise.wav")

    norm = ["normalize-audio", "--reference=voice", "--target=bgm", "--json"]
    # 响度数值以 calibrate_media.py 校准台账为准（蝉镜母带每次重合成有
    # ±0.4dB 微漂，校准器把真机显示值锚到口播数字；断言不钉死数值）
    calib_p = HERE.parent / "build" / "media-calibration.json"
    calib = json.loads(calib_p.read_text(encoding="utf-8"))
    vol6 = str(calib["volume_written"])          # 写盘值，case06 previousVolume 验
    vol_exact = repr(calib["volume_exact"])      # --write 当次 JSON 给全精度
    need = "needs %.1f dB" % calib["display"]["ceiling_db"]
    return [
        ("01 s0 check 全绿", s0, ["check"], 0,
         [], ["media_missing_id", "video_missing_muted", "audio_src_not_found",
              "missing_local_asset", "placeholder_media_url"]),
        ("02 s0 lint 退 0", s0, ["lint"], 0, [], []),
        ("03 s0 beats 出拍子", s0, ["beats"], 0, [], []),
        ("04 normalize dry-run", s0, norm, 0,
         ['"wrote": false'], []),
        ("05 normalize --write 写回", s0,
         ["normalize-audio", "--reference=voice", "--target=bgm",
          "--write", "--json"], 0,
         # 当次 JSON 给全精度 volume；6 位写回值在 case06 previousVolume 验
         ['"wrote": true', vol_exact], []),
        ("06 normalize 幂等 withinTolerance", lambda *_: None, norm, 0,
         ["withinTolerance", '"previousVolume": %s' % vol6], []),
        ("07 target id 写错 exit1 但不动文件", s0,
         ["normalize-audio", "--reference=voice", "--target=bgn", "--json"], 1,
         ['"ok": false', "Target audio #bgn was not found"], []),
        ("08 media-treatment analyze #demo", s0,
         ["media-treatment", "--selector=#demo", "--analyze", "--json"], 0,
         ["suggestedPatch"], []),
        ("09 treatment selector 写错", s0,
         ["media-treatment", "--selector=#dem", "--analyze", "--json"], 1,
         ["Selector did not match"], []),
        ("10 删 id → FROZEN", e_noid, ["check"], 1,
         ["media_missing_id", "FROZEN"], []),
        ("11 删 muted → 声音立场", e_nomuted, ["check"], 1,
         ["video_missing_muted"], []),
        ("12 voice→voise → silent", e_badsrc, ["check"], 1,
         ["audio_src_not_found", "silent"], []),
        ("13 s4 缺视觉文件", s4, ["check"], 1,
         ["missing_local_asset"], []),
        ("14 s5 同轨层叠 warning", s5, ["check"], None,
         ["duplicate_audio_track"], []),  # 退出码彩排见真章
        ("15 s8 占位 URL", s8, ["check"], 1,
         ["placeholder_media_url"], []),
        ("16 s9 +12dB 天花板", s9,
         ["normalize-audio", "--reference=voice", "--target=bgm", "--json"], 1,
         ['"ok": false', need, "+12 dB"], []),
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=S.DEFAULT_ROOT)
    args = ap.parse_args()
    root = Path(args.root)
    proj = root / PROJ_REL
    if not shutil.which("npx.cmd") and not shutil.which("npx"):
        sys.exit("PATH 中找不到 npx")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    logf = LOG.open("w", encoding="utf-8", newline="\n")
    results = []
    try:
        for name, setup, argv, exp_code, must, must_not in cases(root):
            setup()
            try:
                code, out, dt = run(proj, argv)
            except subprocess.TimeoutExpired:
                results.append((name, "TIMEOUT", ""))
                logf.write("===== %s TIMEOUT =====\n" % name)
                continue
            logf.write("===== %s | exit=%s %.1fs | %s =====\n%s\n\n"
                       % (name, code, dt, " ".join(argv), out))
            logf.flush()
            errs = []
            if exp_code is not None and code != exp_code:
                errs.append("exit 预期 %s 实得 %s" % (exp_code, code))
            for s in must:
                if s not in out:
                    errs.append("缺串 %r" % s)
            for s in must_not:
                if s in out:
                    errs.append("不应出现 %r" % s)
            # beats 产物落盘核查
            if name.startswith("03"):
                bj = list((proj / "beats").rglob("*.json")) if (proj / "beats").exists() else []
                if not bj:
                    errs.append("beats/ 无 json 产物")
                else:
                    data = json.loads(bj[0].read_text(encoding="utf-8"))
                    logf.write("beats 产物：%s（%d 拍）\n\n"
                               % (bj[0].relative_to(proj), len(data.get("beats", []))))
            results.append((name, "PASS" if not errs else "FAIL",
                            "; ".join(errs)))
    finally:
        restore(root, "s0-good")
        logf.close()

    print("=" * 64)
    nfail = 0
    for name, status, err in results:
        mark = "✓" if status == "PASS" else ("✗" if status == "FAIL" else "⏱")
        if status == "FAIL":
            nfail += 1
        print("%s %-34s %s %s" % (mark, name, status, err))
    print("=" * 64)
    print("日志：%s" % LOG)
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
