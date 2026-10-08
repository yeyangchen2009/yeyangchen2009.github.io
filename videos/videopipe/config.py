# -*- coding: utf-8 -*-
"""videopipe 全局常量与项目路径约定。

所有帧率 / 时长 / 编码 / 魔法数字的单一来源；各模块与项目 make_video
都通过这里寻址，不再散落硬编码。
"""
from dataclasses import dataclass
from pathlib import Path

# ---- 画布与依赖（五片实测统一） ----
WIDTH, HEIGHT, FPS = 1920, 1080, 30
GSAP_URL = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"
HYPERFRAMES_PIN = "0.8.107"

# ---- 轨道编号 ----
TRACK_SCENE, TRACK_AUDIO, TRACK_BG = 1, 2, 3

# ---- 字幕时间常数（四片实测） ----
SUB_FADE = 0.26          # 标准片整句淡入淡出
SUB_LEAD, SUB_TAIL = 0.35, 0.30     # fade_out = max(s+.35, e-.30)
# 逐字高亮补偿：faster-whisper 对克隆 TTS 的词时间戳系统偏晚（实测约
# 80ms：声音已念到、高亮还没跳），把逐字变色整体提前。0＝不补偿。
WHISPER_WORD_LEAD = 0.08

# ---- 心经整片专用：底部整句 .28s 淡变，fade_out = max(s+.35, e-.28) ----
XJ_TAIL = 0.28

# ---- 编码规格（concat / render 对齐正片） ----
X264 = dict(profile="high", pix_fmt="yuv420p", crf=18)
AAC = dict(ar=48000, ac=2)
COVER_HOLD = 2.0

# ---- 组句标点 ----
SPLIT_FULL = "，。：？！"
SPLIT_XJ = "，。："


@dataclass
class ProjectPaths:
    """单个视频项目的标准目录布局。"""

    root: Path

    @classmethod
    def at(cls, root) -> "ProjectPaths":
        return cls(Path(root))

    @property
    def index_html(self) -> Path:
        return self.root / "index.html"

    @property
    def src_dir(self) -> Path:
        return self.root / "src"

    @property
    def cues_json(self) -> Path:
        return self.root / "cues" / "cues.json"

    @property
    def build_dir(self) -> Path:
        return self.root / "build"

    @property
    def media_dir(self) -> Path:
        return self.root / "media"

    @property
    def renders_dir(self) -> Path:
        return self.root / "renders"

    @property
    def snapshots_dir(self) -> Path:
        return self.root / "snapshots"

    @property
    def oneoffs_dir(self) -> Path:
        return self.root / "oneoffs"

    def ensure(self) -> None:
        """仅创建输出目录，不动已有内容。"""
        for p in (self.src_dir, self.root / "cues", self.build_dir,
                  self.media_dir, self.renders_dir, self.snapshots_dir,
                  self.oneoffs_dir):
            p.mkdir(parents=True, exist_ok=True)
