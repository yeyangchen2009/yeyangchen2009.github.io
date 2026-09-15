#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 README.custom.md 幂等拼接到 Gmeek 自动生成的 README.md 统计区下方。

背景：Gmeek.py 在非 schedule 构建时会整体重写 README.md（六行统计信息），
直接往 README.md 里写的自定义内容下次发文章就会被抹掉。因此自定义内容放在
README.custom.md，由本脚本用标记块拼接；workflow 在 Gmeek 生成之后、
自动提交之前运行本脚本。

幂等：每次先砍掉旧标记块（schedule 构建时 Gmeek 不重写 README，旧块还在），
再追加当前的 README.custom.md，重复执行结果稳定，无内容变化时 git 无 diff。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
CUSTOM = os.path.join(ROOT, "README.custom.md")
BEGIN = "<!-- BEGIN CUSTOM README -->"
END = "<!-- END CUSTOM README -->"


def main():
    with io.open(README, encoding="utf-8") as f:
        base = f.read()
    cut = base.find(BEGIN)
    if cut != -1:
        base = base[:cut]
    base = base.rstrip() + "\n"

    with io.open(CUSTOM, encoding="utf-8") as f:
        custom = f.read().strip()

    out = base + "\n\n" + BEGIN + "\n" + custom + "\n" + END + "\n"
    with io.open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(out)
    print("====== rebuild README.md: custom section %d chars ======" % len(custom))


if __name__ == "__main__":
    sys.exit(main())
