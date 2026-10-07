# -*- coding: utf-8 -*-
"""脚手架：新建一个标准布局视频项目到 projects/<name>。

用法：  python new_project.py <name>
复制 templates/project 全部文件，替换 __NAME__ / __CREATEDAT__，
并创建本地输出目录（media/build/renders/snapshots，均 gitignored）。
"""
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "templates" / "project"
PROJECTS = ROOT / "projects"


def main(name: str) -> None:
    dst = PROJECTS / name
    if dst.exists():
        sys.exit("目标已存在：%s" % dst)

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") \
        + "%03dZ" % (datetime.now(timezone.utc).microsecond // 1000)

    for src in TEMPLATE.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(TEMPLATE)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in (".gitkeep",):
            shutil.copyfile(src, out)
            continue
        text = src.read_text(encoding="utf-8")
        text = text.replace("__NAME__", name).replace("__CREATEDAT__", created)
        out.write_text(text, encoding="utf-8")

    for d in ("media", "build", "renders", "snapshots"):
        (dst / d).mkdir(parents=True, exist_ok=True)

    print("已创建项目：%s" % dst)
    print("下一步：① 做封面 make_cover.py  ② 放口播到 media/  "
          "③ cues/ 放对齐结果  ④ 改 make_video.py 分镜")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("用法：python new_project.py <name>")
    main(sys.argv[1])
