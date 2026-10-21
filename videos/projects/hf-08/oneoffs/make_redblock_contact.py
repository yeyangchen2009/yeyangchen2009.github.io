# -*- coding: utf-8 -*-
r"""hf-08 redblock contact：bad-lint 第 30/150 帧横拼＋暗色标注（PIL 离线）。

分镜 m15 用：6s rAF 红块工程（无 GSAP timeline），第 30 帧（1.0s）红块左缘
x=246、第 150 帧（5.0s）x=966——红方块 requestAnimationFrame 自己掐表跑、
不注册时间轴，正是 lint error 与 45000ms 等待的主角。探针期已像素验证
（PROBE-NOTES 失败案例节，f01/f02 均 1920×1080）。

出图对准成片容器 .shot（1120×644、object-fit:contain、底 #0a0d12）：
画布 1120×630，两帧各缩 544×306 横排，帧内底部暗色标注条＋红块 x 位细标线。

用法：
    python oneoffs/make_redblock_contact.py            # 读布景 bad-lint
    python oneoffs/make_redblock_contact.py --probe    # 布景未建时读探针源
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT_P = HERE.parent
MEDIA_OUT = ROOT_P / "media" / "artifacts" / "redblock-30-150.png"

STAGE = Path(r"F:\_hftest\hf08-media\bad-lint")
PROBE = Path(r"F:\_hftest\hf08-probe\bad-lint")

W, H = 1120, 630
BG = (10, 13, 18)          # #0a0d12，同 .shot 底
INK = (230, 237, 243)      # #e6edf3
ACCENT = (88, 166, 255)    # #58a6ff
RED = (255, 100, 90)
CARD_W, CARD_H = 544, 306
CARD_Y = 46
GAP = W - 2 * CARD_W       # 32：左右各 16
SCALE = CARD_W / 1920.0

# x 为红块中心像素（块宽 120、left:0、translateX 为左缘，中心＝左缘+60；
# PIL 实测 f01 左缘 186／f02 左缘 906，中心 246/966）。
FRAMES = [
    ("f01.png", 16, "第 30 帧 · 1.0s · 红块中心 x=246", 246),
    ("f02.png", 16 + CARD_W + GAP, "第 150 帧 · 5.0s · 红块中心 x=966", 966),
]

FONT = r"C:\Windows\Fonts\msyh.ttc"


def load_font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true",
                    help="从探针目录取 f01/f02")
    args = ap.parse_args()
    src_dir = PROBE if args.probe or not STAGE.is_dir() else STAGE

    canvas = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(canvas)
    f_title = load_font(25)
    f_tag = load_font(19)

    d.text((16, 10), "同一个工程，烤两次：红方块只信 requestAnimationFrame",
           fill=INK, font=f_title)

    for fname, x0, tag, red_x in FRAMES:
        src = src_dir / fname
        if not src.is_file():
            sys.exit("缺帧：%s（先跑 setup_scenes.py init）" % src)
        im = Image.open(src).convert("RGB")
        if im.size != (1920, 1080):
            sys.exit("%s 尺寸 %s，预期 1920×1080" % (fname, im.size))
        im = im.resize((CARD_W, CARD_H), Image.LANCZOS)
        canvas.paste(im, (x0, CARD_Y))
        # 卡片描边
        d.rectangle([x0, CARD_Y, x0 + CARD_W - 1, CARD_Y + CARD_H - 1],
                    outline=(48, 54, 61), width=1)
        # 红块中心 x 位细标线（卡顶内 6–28px，accent 蓝，不挨标题）
        lx = x0 + round(red_x * SCALE)
        d.line([(lx, CARD_Y + 6), (lx, CARD_Y + 28)], fill=ACCENT, width=2)
        d.line([(lx - 5, CARD_Y + 12), (lx + 5, CARD_Y + 12)],
               fill=ACCENT, width=2)
        d.ellipse([lx - 3, CARD_Y + 2, lx + 3, CARD_Y + 8], fill=ACCENT)
        # 帧内底部标注条
        bar_h = 34
        bar = Image.new("RGBA", (CARD_W, bar_h), (13, 17, 23, 215))
        canvas.paste(bar, (x0, CARD_Y + CARD_H - bar_h), bar)
        d.text((x0 + 12, CARD_Y + CARD_H - bar_h + 6), tag,
               fill=INK, font=f_tag)

    # 底部两行小字
    f_note = load_font(18)
    d.text((16, CARD_Y + CARD_H + 16),
           "不注册 window.__timelines，producer 死等 45000ms；默认 lint error",
           fill=(139, 148, 158), font=f_note)
    d.text((16, CARD_Y + CARD_H + 42),
           "best-effort 仍 Continuing 出片，--strict 直接 Aborting",
           fill=(139, 148, 158), font=f_note)

    MEDIA_OUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(MEDIA_OUT)
    print("出图：%s（%d×%d，源 %s）" % (MEDIA_OUT, W, H, src_dir))


if __name__ == "__main__":
    main()
