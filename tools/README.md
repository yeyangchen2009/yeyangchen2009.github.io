# tools — 工具箱

博客、视频、审稿、分发各流水线共用的脚本。Python 脚本尽量只用标准库；
需要第三方包的依赖会惰性导入，不影响其它命令。

## 凭证与安全约定

- 所有登录态/cookie/token **只在进程内部使用，不打印、不进日志、不入 git**。
- B 站：biliup 格式 `cookies.json`，路径优先级 `--cookie > 环境变量 BILIUP_COOKIE > 内置默认路径`；失效后在 cookie 所在目录 `python -m biliup login`（用户本人操作）。
- 蝉镜：`tools/.chanjing.env`（不入库）配置 `CHANJING_APP_ID` / `CHANJING_SECRET_KEY`。
- 浏览器自动化使用独立 profile 目录（如 `Temp/cj-profile`），不进 git。

## 工具索引

### B 站视频

| 工具 | 用途 |
|---|---|
| `bili-pub.py` | **投稿 + 合集管理**：upload / seasons / season / season-add / season-edit / season-sort |
| `bili-edit.py` | 已有稿件编辑：查看分 P、改分 P 名、换稿件整体封面（默认 dry-run，`--commit` 提交） |

```bash
# 投稿（--desc 可换 --desc-file；默认公开、自制、人文历史分区）
# --cover 超 B 站约 5MB 上限时自动等比缩到宽 1920（需 ffmpeg）
python tools/bili-pub.py upload --video xx-cover.mp4 \
    --title "标题" --desc-file desc.txt --cover cover.png

# 合集：列出 → 归集多稿 → 改简介（简介写泛，别写死具体视频名）
python tools/bili-pub.py seasons
python tools/bili-pub.py season-add 10349359 --vid BV1xx --vid BV1yy
python tools/bili-pub.py season-edit 9255943 --desc-file intro.txt
# 按 BV 顺序重排
python tools/bili-pub.py season-sort 10349359 --order BV1xx,BV1yy
```

合集**创建**没有可用接口（旧逆向接口维权后已 404），在官方网页操作：
<https://member.bilibili.com/platform/upload-manager/series>，建好后用
`season-add` 归集。

### 声模块：蝉镜 TTS 与数字人

见下方 [声模块详解](#声模块详解chanjing-tts)。

| 工具 | 通道 | 蝉豆 |
|---|---|---|
| `chanjing.py` | 开放平台 API（标准库客户端） | 合成任务计费；token 本地缓存 |
| `cj-web-tts.js` | 网页「试听」自动化，UI 点击 / `--api` XHR 两种模式 | **0 豆** |
| `cj-auto-tts.js` | 网页「试听」一键版（连接已开浏览器的调试端口） | **0 豆** |

### 博客发布

| 工具 | 用途 |
|---|---|
| `publish-post.py` | 一键发文章：pre-flight → 建 issue → 门户打勾 → 限时轮询双绿 → 验证。严格串行 |
| `fetch-drafts.py` | 从 GitHub issue 拉正文落地 `drafts/`，站内图片路径同步换成云端绝对 URL |
| `portal_hooks/` | 门户（系列合集）钩子，`zhong.py` 为中系；`--series` 传 hook 名 |
| `build-readme.py` | 把 `README.custom.md` 幂等拼接到 Gmeek 重写的 README 统计区下 |

### 审稿与分发

| 工具 | 用途 |
|---|---|
| `feishu-sync.py` | Markdown 同步飞书知识库（手机审稿）：占位图换本地图、mermaid 换飞书画板，支持 `--parent` |
| `zhihu-draft.js` | 文章入知乎草稿箱（**只存草稿，绝不发布**） |

### 截图、录屏与 Mermaid

| 工具 | 用途 |
|---|---|
| `cdp-shot.js` | 零依赖无头截图器（CDP），`--scale 1` 出 1x，默认 2x |
| `screen-rec.js` | 零依赖屏幕录制器（FFmpeg gdigrab）：录终端/编辑器操作演示，支持区域裁剪、定时、Ctrl+C 收尾、dshow 麦克风 |
| `ui-shot.ps1` / `shot-window.ps1` | Windows 窗口/UI 截图 |
| `mermaid-shot.js` | Mermaid 代码块渲染截图 |
| `mermaid-to-png.js` | Mermaid 转 `mermaid.ink` PNG（飞书白板兜底用） |

其它：`primer-21.0.7.css`（GitHub Primer 样式，截图复刻用）。

视频制作的深模块管线在 [`../videos/`](../videos/README.md)（TTS 之后的
whisper 转录、对齐、分镜、渲染、封面拼接均在其中）。

---

## 声模块详解（chanjing TTS）

视频配音统一走蝉镜。核心诉求：**稳定拿到与目标音色一致的 wav，尽量 0 成本**。

### 音色

- 公共音色：`chanjing.list_common_audio(page, size)` 翻页查看（91 个）。
  命令行快速查看：
  `python -c "import sys; sys.path.insert(0,'tools'); import chanjing; print(chanjing.list_common_audio())"`
- 克隆音色：在网页端录制/上传样本克隆，得到 `C-xxxx` 形式的 `audio_man` id。
  克隆音色同样可用于试听通道。

### 三条取音路线

**① 网页试听（推荐日常使用，0 蝉豆）**

试听本就是平台给用户的免费功能，自动化只点「试听」、不点「立即生成」：

```bash
# UI 模式：独立 profile，自动开页/贴稿/点试听/抓 wav
node tools/cj-web-tts.js text.txt out.wav C-xxxxxxxx \
     --profile Temp/cj-profile
# 首次需手动登录，加 --wait-login 60 留登录时间

# 已开着带调试端口的浏览器时，用一键版
node tools/cj-auto-tts.js --port 10127 \
    --url 'https://www.chanjing.cc/creation-audio?id=C-xxxx&type=custom' \
    --text text.txt --out out.wav
```

抓到的 wav 在 `res.chanjing.cc`，轮询 `<audio>.src` 或网络请求即可获得。

**② 开放平台 API（`chanjing.py`，正式/批量场景）**

```python
import tools.chanjing as cj
task = cj.create_audio_task('C-xxxxxxxx', text)   # → task_id
state, _ = cj.wait_audio(task)                    # 退避轮询
wav_url = state['full']['url']
```

- access_token 自动获取并缓存于 `tools/.chanjing-state.json`（提前 60 秒刷新）。
- 业务成功以响应 **`code === 0`** 为准（HTTP 200 不算数）。
- TTS 轮询节奏：首间隔 3s、指数退避上限 10s、总超时 5 分钟。

**③ 开源克隆 + 免费 GPU（合规 ¥0 路线，备选）**

不依赖平台额度的本地方案，无独显时用 Kaggle 免费 GPU 跑开源 TTS 克隆。
适合平台额度/账号受限时兜底。

### 铁律

- **绝不点「立即生成」**（扣豆、走计费合成），只点「试听」。
- secret、access_token、JWT 一律不输出；`cj-*.js` 连 localStorage.token
  都只在页面上下文内使用，不读取打印。
- 网页通道关键坑：页面真实请求除 cookie 外还带 `Authorization` 头
  （JWT 存 `localStorage.token`），裸 fetch 会报 `10201 用户不存在`。
